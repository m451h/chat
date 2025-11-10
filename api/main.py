from pathlib import Path
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config.settings import settings
from core.chatbot import MedicalChatbot
from db import (
    get_db,
    get_or_create_user,
    create_condition,
    get_user_conditions,
    create_chat_session,
    get_user_sessions,
    get_session_by_id,
    add_message,
    get_session_messages,
)


app = FastAPI(
    title="EHR Chatbot API",
    description="FastAPI service mirroring the Streamlit UI flow for frontend integration.",
    version="1.0.0",
)

# Allow all origins by default (customize for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton chatbot
chatbot = MedicalChatbot()


# ====== Schemas ======
class StartSessionRequest(BaseModel):
    user_id: int = Field(..., description="Unique user identifier")
    condition_name: str = Field(..., description="Condition name (display)")
    patient_data: Dict[str, Any] = Field(..., description="Arbitrary patient JSON for this context")


class InitialMessage(BaseModel):
    type: str = Field("education_note", description="Message type")
    content: str = Field(..., description="Model-generated educational content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata")


class StartSessionResponse(BaseModel):
    session_id: int
    user_id: int
    condition_id: int
    condition_name: str
    initial_message: InitialMessage


class SendMessageRequest(BaseModel):
    message: str


class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: datetime


class SendMessageResponse(BaseModel):
    session_id: int
    reply: ChatMessage


class SessionSummary(BaseModel):
    id: int
    title: Optional[str]
    updated_at: Optional[datetime]
    condition_id: int


# ====== Helpers ======
def _save_patient_json_to_mock_data(file_name: str, data: Dict[str, Any]) -> str:
    """
    Save patient JSON into mock_data so existing loader can find it.
    Returns the relative file name stored in the DB.
    """
    mock_dir = settings.MOCK_DATA_DIR
    mock_dir.mkdir(parents=True, exist_ok=True)
    target_path = mock_dir / file_name
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Store only file name; MedicalChatbot loader prefixes MOCK_DATA_DIR
    return file_name


def _db_messages_to_history(messages: List) -> List[Dict[str, str]]:
    """
    Convert DB Message rows to the format expected by chatbot.chat(..., conversation_history=...).
    """
    history: List[Dict[str, str]] = []
    for m in messages:
        if m.role in ("user", "assistant"):
            history.append({"role": m.role, "content": m.content})
    return history


# ====== Routes ======
@app.post("/sessions/start", response_model=StartSessionResponse, summary="Start a chat session with patient JSON")
def start_session(payload: StartSessionRequest, db: Session = Depends(get_db)):
    # Ensure user exists
    user = get_or_create_user(db, payload.user_id)

    # Persist patient JSON to mock_data with unique name
    unique_name = f"api_{payload.user_id}_{uuid.uuid4().hex}.json"
    relative_file_name = _save_patient_json_to_mock_data(unique_name, payload.patient_data)

    # Find or create a condition for this user using provided display name
    existing_conditions = get_user_conditions(db, payload.user_id)
    condition = next((c for c in existing_conditions if c.name == payload.condition_name), None)
    if not condition:
        condition = create_condition(
            db=db,
            user_id=payload.user_id,
            name=payload.condition_name,
            name_en=payload.condition_name,  # reuse name as key
            data_file=relative_file_name,
        )

    # Create chat session
    session = create_chat_session(db, user_id=payload.user_id, condition_id=condition.id)

    # Generate initial educational content
    content = chatbot.generate_educational_content(
        condition_name=payload.condition_name,
        condition_data_file=relative_file_name,
        session_id=session.id,
    )

    # Store messages to DB: system context + assistant note
    add_message(db, session_id=session.id, role="system", content=f"patient_context:{json.dumps(payload.patient_data, ensure_ascii=False)}")
    add_message(db, session_id=session.id, role="assistant", content=content)

    return StartSessionResponse(
        session_id=session.id,
        user_id=payload.user_id,
        condition_id=condition.id,
        condition_name=payload.condition_name,
        initial_message=InitialMessage(
            content=content,
            metadata={"patient_context_digest": True},
        ),
    )


@app.post("/sessions/{session_id}/messages", response_model=SendMessageResponse, summary="Send a chat message to a session")
def send_message(session_id: int, payload: SendMessageRequest, db: Session = Depends(get_db)):
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Load DB history and get assistant reply
    history_rows = get_session_messages(db, session_id=session_id)
    history = _db_messages_to_history(history_rows)
    reply_text = chatbot.chat(
        question=payload.message,
        session_id=session_id,
        conversation_history=history if history else None,
    )

    # Persist both user message and assistant reply
    add_message(db, session_id=session_id, role="user", content=payload.message)
    msg = add_message(db, session_id=session_id, role="assistant", content=reply_text)

    return SendMessageResponse(
        session_id=session_id,
        reply=ChatMessage(role="assistant", content=msg.content, created_at=msg.created_at),
    )


@app.get("/sessions", response_model=List[SessionSummary], summary="List sessions for a user")
def list_sessions(user_id: int, db: Session = Depends(get_db)):
    sessions = get_user_sessions(db, user_id=user_id)
    return [
        SessionSummary(
            id=s.id,
            title=getattr(s, "title", None),
            updated_at=getattr(s, "updated_at", None),
            condition_id=s.condition_id,
        )
        for s in sessions
    ]


@app.get("/sessions/{session_id}/messages", response_model=List[ChatMessage], summary="Get messages for a session")
def get_messages(session_id: int, db: Session = Depends(get_db)):
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    rows = get_session_messages(db, session_id=session_id)
    return [ChatMessage(role=r.role, content=r.content, created_at=r.created_at) for r in rows]


# Health
@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


