#!/usr/bin/env python3
"""
Command-line interface for EHR Chatbot
Can be called from Java using ProcessBuilder

Usage:
    python cli.py <json_input>
    
Example JSON input:
    {
        "action": "start_session",
        "user_id": 1234567890123,
        "condition_name": "دیابت نوع 2",
        "patient_data": {...},
        "generate_initial_content": true
    }
    
    {
        "action": "send_message",
        "session_id": 1,
        "message": "سوال من چیست؟"
    }
    
    {
        "action": "generate_education",
        "session_id": 1
    }
"""

import sys
import json
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from core.chatbot import MedicalChatbot
from db import init_db, get_db, get_or_create_user, create_condition, get_user_conditions
from db import create_chat_session, get_session_by_id, add_message, get_session_messages
from db import get_condition_by_id


def load_json_input(input_str: str) -> Dict[str, Any]:
    """Load JSON from string"""
    try:
        data = json.loads(input_str)
        if not isinstance(data, dict):
            return {"error": "Input must be a JSON object"}
        return data
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {str(e)}"}


def start_session(payload: Dict[str, Any], db) -> Dict[str, Any]:
    """Start a new chat session"""
    try:
        user_id = payload.get("user_id")
        condition_name = payload.get("condition_name")
        patient_data = payload.get("patient_data", {})
        generate_initial = payload.get("generate_initial_content", False)
        
        if not user_id or not condition_name:
            return {"error": "user_id and condition_name are required"}
        
        # Ensure user exists
        user = get_or_create_user(db, user_id)
        
        # Find or create condition
        existing_conditions = get_user_conditions(db, user_id)
        condition = next((c for c in existing_conditions if c.name == condition_name), None)
        if not condition:
            condition = create_condition(
                db=db,
                user_id=user_id,
                name=condition_name,
                name_en=condition_name,
                data_file="",  # No file persistence for CLI
            )
        
        # Create chat session
        session = create_chat_session(db, user_id=user_id, condition_id=condition.id)
        
        # Store patient context as system message
        add_message(
            db,
            session_id=session.id,
            role="system",
            content=f"patient_context:{json.dumps(patient_data, ensure_ascii=False)}"
        )
        
        result = {
            "success": True,
            "session_id": session.id,
            "user_id": user_id,
            "condition_id": condition.id,
            "condition_name": condition_name,
        }
        
        # Generate initial educational content if requested
        if generate_initial:
            chatbot = MedicalChatbot()
            content = chatbot.generate_educational_content(
                condition_name=condition_name,
                session_id=session.id,
                condition_data=patient_data,
            )
            add_message(db, session_id=session.id, role="assistant", content=content)
            result["initial_message"] = {
                "type": "education_note",
                "content": content,
            }
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to start session: {str(e)}"}


def send_message(payload: Dict[str, Any], db) -> Dict[str, Any]:
    """Send a message to an existing session"""
    try:
        session_id = payload.get("session_id")
        message = payload.get("message")
        
        if not session_id or not message:
            return {"error": "session_id and message are required"}
        
        # Get session
        session = get_session_by_id(db, session_id)
        if not session:
            return {"error": f"Session {session_id} not found"}
        
        # Get conversation history
        history_rows = get_session_messages(db, session_id=session_id)
        
        # Extract patient context
        patient_context: Dict[str, Any] = {}
        for r in history_rows:
            if r.role == "system" and isinstance(r.content, str) and r.content.startswith("patient_context:"):
                try:
                    payload_str = r.content[len("patient_context:"):]
                    patient_context = json.loads(payload_str)
                except Exception:
                    patient_context = {}
                break
        
        # Convert history to format expected by chatbot
        history = []
        for m in history_rows:
            if m.role in ("user", "assistant", "system"):
                history.append({"role": m.role, "content": m.content})
        
        # Get chatbot response
        chatbot = MedicalChatbot()
        reply_text = chatbot.chat(
            question=message,
            session_id=session_id,
            conversation_history=history if history else None,
            condition_data=patient_context if patient_context else None,
        )
        
        # Persist messages
        add_message(db, session_id=session_id, role="user", content=message)
        msg = add_message(db, session_id=session_id, role="assistant", content=reply_text)
        
        return {
            "success": True,
            "session_id": session_id,
            "reply": {
                "role": "assistant",
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            },
        }
        
    except Exception as e:
        return {"error": f"Failed to send message: {str(e)}"}


def generate_education(payload: Dict[str, Any], db) -> Dict[str, Any]:
    """
    Generate educational content for a session.
    
    This can be used:
    - For initial educational content (if not generated during start_session)
    - Mid-chat to regenerate or retrieve educational content
    - Anytime during the session lifecycle
    """
    try:
        session_id = payload.get("session_id")
        
        if not session_id:
            return {"error": "session_id is required"}
        
        # Get session
        session = get_session_by_id(db, session_id)
        if not session:
            return {"error": f"Session {session_id} not found"}
        
        condition = get_condition_by_id(db, session.condition_id)
        if not condition:
            return {"error": f"Condition for session {session_id} not found"}
        
        # Extract patient context
        history_rows = get_session_messages(db, session_id=session_id)
        patient_context: Dict[str, Any] = {}
        for r in history_rows:
            if r.role == "system" and isinstance(r.content, str) and r.content.startswith("patient_context:"):
                try:
                    payload_str = r.content[len("patient_context:"):]
                    patient_context = json.loads(payload_str)
                except Exception:
                    patient_context = {}
                break
        
        # Generate educational content
        chatbot = MedicalChatbot()
        content = chatbot.generate_educational_content(
            condition_name=condition.name,
            session_id=session_id,
            condition_data=patient_context,
        )
        
        # Persist message
        add_message(db, session_id=session_id, role="assistant", content=content)
        
        return {
            "success": True,
            "session_id": session_id,
            "content": content,
        }
        
    except Exception as e:
        return {"error": f"Failed to generate education: {str(e)}"}


def get_session_messages_list(payload: Dict[str, Any], db) -> Dict[str, Any]:
    """Get all messages for a session"""
    try:
        session_id = payload.get("session_id")
        
        if not session_id:
            return {"error": "session_id is required"}
        
        session = get_session_by_id(db, session_id)
        if not session:
            return {"error": f"Session {session_id} not found"}
        
        messages = get_session_messages(db, session_id=session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in messages
            ],
        }
        
    except Exception as e:
        return {"error": f"Failed to get messages: {str(e)}"}


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="EHR Chatbot CLI")
    parser.add_argument(
        "input",
        nargs="?",
        help="JSON input string (or read from stdin if not provided)",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read input from stdin instead of argument",
    )
    
    args = parser.parse_args()
    
    # Validate settings
    try:
        settings.validate()
    except ValueError as e:
        print(json.dumps({"error": f"Configuration error: {str(e)}"}))
        sys.exit(1)
    
    # Initialize database
    init_db()
    
    # Get input
    if args.stdin or not args.input:
        input_str = sys.stdin.read()
    else:
        input_str = args.input
    
    if not input_str.strip():
        print(json.dumps({"error": "No input provided"}))
        sys.exit(1)
    
    # Parse JSON input
    payload = load_json_input(input_str)
    if "error" in payload:
        print(json.dumps(payload))
        sys.exit(1)
    
    # Get action
    action = payload.get("action")
    if not action:
        print(json.dumps({"error": "action field is required"}))
        sys.exit(1)
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Route to appropriate handler
        if action == "start_session":
            result = start_session(payload, db)
        elif action == "send_message":
            result = send_message(payload, db)
        elif action == "generate_education":
            result = generate_education(payload, db)
        elif action == "get_messages":
            result = get_session_messages_list(payload, db)
        else:
            result = {"error": f"Unknown action: {action}"}
        
        # Output result as JSON
        print(json.dumps(result, ensure_ascii=False, indent=None))
        
        # Exit with error code if operation failed
        if "error" in result:
            sys.exit(1)
            
    except Exception as e:
        print(json.dumps({"error": f"Unexpected error: {str(e)}"}))
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

