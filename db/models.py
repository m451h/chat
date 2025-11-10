"""
Database models for EHR Chatbot
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from config.settings import settings

Base = declarative_base()

class User(Base):
    """User model - represents a patient in the EHR system"""
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)  # 13-digit user ID
    name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conditions = relationship("Condition", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"


class Condition(Base):
    """Condition model - represents a diagnosed medical condition"""
    __tablename__ = 'conditions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), nullable=False)  # Persian name, e.g., "دیابت نوع دو"
    name_en = Column(String(255))  # English name for file lookup
    data_file = Column(String(255))  # Path to JSON data file
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conditions")
    chat_sessions = relationship("ChatSession", back_populates="condition", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Condition(id={self.id}, name={self.name}, user_id={self.user_id})>"


class ChatSession(Base):
    """Chat session model - represents a conversation about a specific condition"""
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    condition_id = Column(Integer, ForeignKey('conditions.id'), nullable=False)
    title = Column(String(255))  # Auto-generated session title
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    condition = relationship("Condition", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, title={self.title}, condition_id={self.condition_id})>"


class Message(Base):
    """Message model - represents a single message in a chat session"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, session_id={self.session_id})>"


# Database initialization
engine = None
SessionLocal = None

def init_db():
    """Initialize database and create tables"""
    global engine, SessionLocal
    
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    return engine, SessionLocal

def get_db():
    """Get database session"""
    if SessionLocal is None:
        init_db()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
