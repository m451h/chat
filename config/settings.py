"""
Application configuration and settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    # Support both OPENAI_BASE_URL and OPENAI_API_BASE for compatibility
    OPENAI_BASE_URL: str = (
        os.getenv("OPENAI_BASE_URL")
        or os.getenv("OPENAI_API_BASE", "")
    )
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000  # Default/fallback
    # Separate token limits for different use cases
    EDUCATIONAL_MAX_TOKENS: int = int(os.getenv("EDUCATIONAL_MAX_TOKENS", "2000"))  # Longer for educational content
    CHAT_MAX_TOKENS: int = int(os.getenv("CHAT_MAX_TOKENS", "500"))  # Shorter for chat responses
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ehr_chatbot.db")
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "EHR Medical Chatbot")
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "4000"))
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    MOCK_DATA_DIR: Path = BASE_DIR / "mock_data"
    
    # Persian UI Texts
    UI_TEXTS = {
        "app_title": "چت‌بات آموزشی پزشکی",
        "sidebar_title": "بیماری‌های شما",
        "chat_history_title": "تاریخچه گفتگوها",
        "new_chat": "گفتگوی جدید",
        "input_placeholder": "سوال خود را بپرسید...",
        "loading": "در حال پردازش...",
        "error_api": "خطا در ارتباط با سرویس. لطفاً دوباره تلاش کنید.",
        "no_conditions": "هیچ بیماری ثبت نشده است.",
        "select_condition": "یک بیماری را انتخاب کنید",
    }
    
    def validate(self):
        """Validate required settings"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in .env file.")
        return True

settings = Settings()
