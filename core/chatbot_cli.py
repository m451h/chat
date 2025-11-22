"""
Command-line interface for MedicalChatbot
Allows Java backend to call Python chatbot directly via subprocess
"""
import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chatbot import MedicalChatbot
from config.settings import settings


def main():
    """Main CLI entry point"""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        command = input_data.get("command")
        
        # Initialize chatbot (singleton pattern for efficiency)
        if not hasattr(main, "chatbot"):
            main.chatbot = MedicalChatbot()
        
        chatbot = main.chatbot
        
        # Route to appropriate method
        if command == "generate_educational":
            result = handle_generate_educational(chatbot, input_data)
        elif command == "chat":
            result = handle_chat(chatbot, input_data)
        elif command == "health":
            result = {"status": "healthy", "success": True}
        else:
            result = {
                "success": False,
                "error": f"Unknown command: {command}"
            }
        
        # Output JSON result to stdout
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        # Output error as JSON
        error_result = {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)


def handle_generate_educational(chatbot: MedicalChatbot, input_data: dict) -> dict:
    """Handle generate_educational_content command"""
    condition_name = input_data.get("condition_name")
    condition_data = input_data.get("condition_data")
    session_id = input_data.get("session_id", 0)
    
    if not condition_name:
        return {
            "success": False,
            "error": "condition_name is required"
        }
    
    try:
        message = chatbot.generate_educational_content(
            condition_name=condition_name,
            condition_data=condition_data,
            session_id=session_id
        )
        
        return {
            "success": True,
            "message": message
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def handle_chat(chatbot: MedicalChatbot, input_data: dict) -> dict:
    """Handle chat command"""
    question = input_data.get("question")
    session_id = input_data.get("session_id")
    conversation_history = input_data.get("conversation_history")
    condition_data = input_data.get("condition_data")
    
    if not question:
        return {
            "success": False,
            "error": "question is required"
        }
    
    if session_id is None:
        return {
            "success": False,
            "error": "session_id is required"
        }
    
    try:
        answer = chatbot.chat(
            question=question,
            session_id=session_id,
            conversation_history=conversation_history,
            condition_data=condition_data
        )
        
        return {
            "success": True,
            "answer": answer
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


if __name__ == "__main__":
    main()

