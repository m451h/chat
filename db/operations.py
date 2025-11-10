"""
Database operations and CRUD functions
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from .models import User, Condition, ChatSession, Message, init_db

# Initialize database
init_db()

# User operations
def create_user(db: Session, user_id: int, name: str) -> User:
    """Create a new user"""
    user = User(id=user_id, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_or_create_user(db: Session, user_id: int, name: str = "کاربر") -> User:
    """Get existing user or create new one"""
    user = get_user_by_id(db, user_id)
    if not user:
        user = create_user(db, user_id, name)
    return user


# Condition operations
def create_condition(db: Session, user_id: int, name: str, name_en: str, data_file: str) -> Condition:
    """Create a new condition for a user"""
    condition = Condition(
        user_id=user_id,
        name=name,
        name_en=name_en,
        data_file=data_file
    )
    db.add(condition)
    db.commit()
    db.refresh(condition)
    return condition

def get_user_conditions(db: Session, user_id: int) -> List[Condition]:
    """Get all conditions for a user"""
    return db.query(Condition).filter(Condition.user_id == user_id).all()

def get_condition_by_id(db: Session, condition_id: int) -> Optional[Condition]:
    """Get condition by ID"""
    return db.query(Condition).filter(Condition.id == condition_id).first()


# Chat session operations
def create_chat_session(db: Session, user_id: int, condition_id: int, title: str = None) -> ChatSession:
    """Create a new chat session"""
    if not title:
        condition = get_condition_by_id(db, condition_id)
        title = f"گفتگو درباره {condition.name}" if condition else "گفتگوی جدید"
    
    session = ChatSession(
        user_id=user_id,
        condition_id=condition_id,
        title=title
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_user_sessions(db: Session, user_id: int, condition_id: Optional[int] = None) -> List[ChatSession]:
    """Get all chat sessions for a user, optionally filtered by condition"""
    query = db.query(ChatSession).filter(ChatSession.user_id == user_id)
    if condition_id:
        query = query.filter(ChatSession.condition_id == condition_id)
    return query.order_by(ChatSession.updated_at.desc()).all()

def get_session_by_id(db: Session, session_id: int) -> Optional[ChatSession]:
    """Get chat session by ID"""
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def update_session_timestamp(db: Session, session_id: int):
    """Update session's last updated timestamp"""
    session = get_session_by_id(db, session_id)
    if session:
        session.updated_at = datetime.utcnow()
        db.commit()


# Message operations
def add_message(db: Session, session_id: int, role: str, content: str) -> Message:
    """Add a message to a chat session"""
    message = Message(
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Update session timestamp
    update_session_timestamp(db, session_id)
    
    return message

def get_session_messages(db: Session, session_id: int, limit: Optional[int] = None) -> List[Message]:
    """Get all messages for a chat session"""
    query = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at)
    if limit:
        # Get the last N messages
        total = query.count()
        if total > limit:
            query = query.offset(total - limit)
    return query.all()

def delete_session(db: Session, session_id: int) -> bool:
    """Delete a chat session and all its messages"""
    session = get_session_by_id(db, session_id)
    if session:
        db.delete(session)
        db.commit()
        return True
    return False
