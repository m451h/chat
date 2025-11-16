"""
Pydantic models for API request/response
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class ContextData(BaseModel):
    """Context data structure for initial message generation"""
    condition_name: str
    condition_data: Optional[Dict[str, Any]] = None


class GenerateInitialMessageRequest(BaseModel):
    """Request model for generating initial educational message"""
    context: ContextData


class GenerateInitialMessageResponse(BaseModel):
    """Response model for initial educational message"""
    message: str
    success: bool = True
    error: Optional[str] = None


class Message(BaseModel):
    """Single message in conversation history"""
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str
    session_id: int
    conversation_history: Optional[List[Message]] = None
    condition_data: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str
    success: bool = True
    error: Optional[str] = None

