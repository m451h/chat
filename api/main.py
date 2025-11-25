"""
FastAPI application for EHR Chatbot API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chatbot import MedicalChatbot
from api.models import (
    GenerateInitialMessageRequest,
    GenerateInitialMessageResponse,
    ChatRequest,
    ChatResponse,
    Message
)
from config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="EHR Chatbot API",
    description="API for medical educational chatbot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware to allow Java backend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Java backend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot instance (lazy initialization)
chatbot = None


def get_chatbot():
    """Get or initialize chatbot instance"""
    global chatbot
    if chatbot is None:
        try:
            chatbot = MedicalChatbot()
        except Exception as e:
            print(f"Error initializing chatbot: {e}")
            import traceback
            traceback.print_exc()
            raise
    return chatbot


@app.on_event("startup")
async def startup_event():
    """Validate settings and initialize chatbot on startup"""
    print("🚀 Starting EHR Chatbot API...")
    try:
        settings.validate()
        print("✅ Settings validated")
        # Initialize chatbot on startup to catch errors early
        get_chatbot()
        print("✅ Chatbot initialized")
        print("✅ API started successfully!")
        print(f"📚 API Docs: http://localhost:8000/docs")
        print(f"🔍 Health Check: http://localhost:8000/health")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        import traceback
        traceback.print_exc()
        print("⚠️  Server will start but endpoints may not work properly")
        # Don't raise - let the server start but endpoints will fail gracefully


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the frontend HTML page"""
    web_file = Path(__file__).parent.parent / "web" / "index.html"
    if web_file.exists():
        with open(web_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Fallback to API info page if web file doesn't exist
        return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EHR Chatbot API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #2c3e50; }
            .status { background: #27ae60; color: white; padding: 10px; border-radius: 5px; }
            a { color: #3498db; text-decoration: none; margin-right: 20px; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🩺 EHR Chatbot API</h1>
        <div class="status">✅ API is running!</div>
        <h2>Available Endpoints:</h2>
        <ul>
            <li><a href="/docs">📚 Interactive API Documentation (Swagger UI)</a></li>
            <li><a href="/redoc">📖 Alternative API Documentation (ReDoc)</a></li>
            <li><a href="/health">💚 Health Check</a></li>
            <li><strong>POST</strong> /generate-initial-message - Generate initial educational message</li>
            <li><strong>POST</strong> /chat - Chat with the bot</li>
        </ul>
        <h2>Quick Test:</h2>
        <p>Try the <a href="/docs">API documentation</a> to test the endpoints interactively.</p>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/generate-initial-message", response_model=GenerateInitialMessageResponse)
async def generate_initial_message(request: GenerateInitialMessageRequest):
    """
    Generate initial educational message based on context
    
    Args:
        request: Contains context with treatment_plan_name and condition_data
    
    Returns:
        Generated educational message
    """
    try:
        context = request.context
        chatbot_instance = get_chatbot()
        
        # Generate educational content using non-streaming version
        message = chatbot_instance.generate_educational_content(
            treatment_plan_name=context.treatment_plan_name,
            condition_data=context.condition_data,
            session_id=0  # Session will be managed by Java backend
        )
        
        return GenerateInitialMessageResponse(
            message=message,
            success=True
        )
    
    except Exception as e:
        print(f"Error in generate_initial_message: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating initial message: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat messages from user
    
    Args:
        request: Contains question, session_id, conversation_history, and optional condition_data
    
    Returns:
        Chat response from the chatbot
    """
    try:
        # Convert Pydantic Message models to dict format expected by chatbot
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        # Call non-streaming chat function
        chatbot_instance = get_chatbot()
        answer = chatbot_instance.chat(
            question=request.question,
            session_id=request.session_id,
            conversation_history=conversation_history,
            condition_data=request.condition_data
        )
        
        return ChatResponse(
            answer=answer,
            success=True
        )
    
    except Exception as e:
        print(f"Error in chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

