# Development Guide

## Architecture Deep Dive

### 1. Core Components

#### Configuration Layer (`config/`)
- **settings.py**: Centralized configuration management
  - Environment variables loading
  - OpenAI model configuration
  - Persian UI text constants
  - Validation logic

#### Database Layer (`db/`)
- **models.py**: SQLAlchemy ORM models
  - `User`: Patient records (13-digit ID)
  - `Condition`: Medical conditions per user
  - `ChatSession`: Conversation sessions
  - `Message`: Individual chat messages
  
- **operations.py**: Database CRUD operations
  - User management (create, get, get_or_create)
  - Condition management
  - Session management (create, list, delete)
  - Message operations (add, retrieve)

#### Core Logic Layer (`core/`)
- **chatbot.py**: Main LangChain integration
  - `MedicalChatbot` class
  - OpenAI GPT-4o-mini setup
  - Conversation memory management
  - Streaming responses
  - Context handling
  
- **prompts.py**: Persian prompt templates
  - Educational content generation
  - Conversational Q&A
  - Summarization (for long conversations)

#### UI Layer (`ui/`)
- **chat_interface.py**: Main chat UI
  - Message display (RTL support)
  - User input handling
  - Response streaming
  - Session initialization
  
- **sidebar.py**: Navigation and history
  - Condition selector buttons
  - Chat history list
  - Session switching

#### Mock Data Layer (`mock_data/`)
- JSON files: Patient condition data
- backend.py: Mock EHR API functions

### 2. Data Flow

```
User Input → Streamlit UI → Chatbot Core → LangChain → OpenAI API
                ↓                ↓
            Database ← Session Management
```

1. **User selects condition** → UI updates, fetches condition data
2. **System generates educational content** → Streams to UI, saves to DB
3. **User asks question** → Saves to DB, sends to LangChain with history
4. **Chatbot responds** → Streams response, saves to DB, updates UI

### 3. Memory Management

**Two-level memory system**:

1. **In-Memory (LangChain)**: 
   - `ConversationBufferWindowMemory`
   - Keeps last N messages for context
   - Session-specific (keyed by session_id)

2. **Persistent (SQLite)**:
   - All messages saved to database
   - Loaded when reopening old sessions
   - Survives app restarts

### 4. Persian Language Support

**RTL (Right-to-Left) Handling**:
- Custom CSS in `chat_interface.py`
- Direction: rtl for all text elements
- Proper alignment for Persian text
- Font selection: Vazirmatn, Tahoma fallback

**Persian Prompts**:
- System prompts in Persian
- Educational content templates
- Conversation guidelines
- Medical terminology

### 5. Streaming Implementation

**Why Streaming?**
- Better UX for long educational content
- Immediate feedback to user
- Lower perceived latency

**Implementation**:
```python
for chunk in chatbot.chat_stream(question, session_id):
    full_response += chunk
    placeholder.markdown(full_response)
```

## Adding New Features

### Add a New Condition

1. **Create JSON data file** in `mock_data/`:
```json
{
  "condition_name": "نام بیماری",
  "condition_name_en": "condition_name",
  "patient_data": {
    "key": "value"
  }
}
```

2. **Update mock backend** in `mock_data/backend.py`:
```python
mock_conditions = {
    user_id: [
        {
            "name": "نام بیماری",
            "name_en": "condition_name",
            "data_file": "condition_name.json"
        }
    ]
}
```

### Extend Database Schema

1. **Add new model** in `db/models.py`:
```python
class NewModel(Base):
    __tablename__ = 'new_table'
    # Add columns
```

2. **Add operations** in `db/operations.py`:
```python
def create_new_model(db: Session, ...):
    # Implementation
```

3. **Update imports** in `db/__init__.py`

### Customize Prompts

Edit `core/prompts.py`:

```python
def get_custom_prompt(params):
    return f"""شما یک...
    {params}
    لطفاً..."""
```

### Add UI Component

1. **Create new file** in `ui/`:
```python
# ui/new_component.py
import streamlit as st

def render_new_component():
    st.write("...")
```

2. **Import in** `ui/__init__.py`

3. **Use in** `main.py`

## Testing

### Manual Testing Checklist

- [ ] User selection works
- [ ] Condition buttons display correctly
- [ ] Educational content generates properly
- [ ] Questions get answered
- [ ] Chat history persists
- [ ] Session switching works
- [ ] Persian text displays correctly (RTL)
- [ ] Error handling for API failures
- [ ] New session creation works

### Unit Testing (Future)

Create `tests/` directory:
```
tests/
├── test_db.py          # Database operations
├── test_chatbot.py     # Core logic
├── test_prompts.py     # Prompt generation
└── conftest.py         # Pytest fixtures
```

## Performance Optimization

### 1. Caching Educational Content
```python
@st.cache_data
def get_educational_content(condition_name, data_file):
    # Cache initial educational notes
```

### 2. Database Indexing
```python
# Add indexes for frequent queries
Index('ix_sessions_user_condition', 
      ChatSession.user_id, 
      ChatSession.condition_id)
```

### 3. Conversation Summarization
For very long conversations, implement periodic summarization:
```python
if len(messages) > 50:
    summary = chatbot.summarize_conversation(messages[:40])
    # Keep summary + recent messages
```

## Production Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "main.py", "--server.port=8501"]
```

### Environment Variables

Production `.env`:
```bash
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:pass@host:5432/dbname
OPENAI_MAX_TOKENS=2000
MAX_CONVERSATION_HISTORY=30
```

### PostgreSQL Migration

Update `config/settings.py`:
```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:pass@localhost/ehr_chatbot"
)
```

Install driver:
```bash
pip install psycopg2-binary
```

### Monitoring

Add logging:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"User {user_id} started session {session_id}")
```

### Security Hardening

1. **Sanitize inputs**: Validate user inputs
2. **Rate limiting**: Limit API calls per user
3. **Encrypt sensitive data**: Use database encryption
4. **Audit logs**: Track all medical data access
5. **HIPAA compliance**: Ensure medical data privacy

## Troubleshooting

### Common Issues

**1. API Key Error**
```
Error: OPENAI_API_KEY is required
```
Solution: Create `.env` file with valid API key

**2. Database Lock**
```
database is locked
```
Solution: Close other connections or use PostgreSQL

**3. Import Errors**
```
ModuleNotFoundError: No module named 'langchain'
```
Solution: `pip install -r requirements.txt`

**4. Persian Text Issues**
```
Text displays left-to-right
```
Solution: Check RTL CSS in `chat_interface.py`

### Debug Mode

Enable verbose logging:
```python
# In core/chatbot.py
ConversationChain(
    llm=self.llm,
    prompt=prompt,
    memory=memory,
    verbose=True  # Enable debug output
)
```

## API Reference

### MedicalChatbot Class

```python
chatbot = MedicalChatbot()

# Generate educational content
content = chatbot.generate_educational_content(
    condition_name="دیابت نوع دو",
    condition_data_file="diabetes_type2.json",
    session_id=1
)

# Stream educational content
for chunk in chatbot.generate_educational_content_stream(...):
    print(chunk)

# Answer question
answer = chatbot.chat(
    question="سوال",
    session_id=1,
    conversation_history=[...]
)

# Stream answer
for chunk in chatbot.chat_stream(...):
    print(chunk)
```

### Database Operations

```python
from db import *

# User operations
user = create_user(db, user_id=1234567890123, name="علی")
user = get_user_by_id(db, 1234567890123)
user = get_or_create_user(db, 1234567890123, "علی")

# Condition operations
condition = create_condition(db, user_id, name, name_en, data_file)
conditions = get_user_conditions(db, user_id)

# Session operations
session = create_chat_session(db, user_id, condition_id)
sessions = get_user_sessions(db, user_id, condition_id)

# Message operations
message = add_message(db, session_id, role, content)
messages = get_session_messages(db, session_id, limit=20)
```

## Contributing Guidelines

1. **Code Style**: Follow PEP 8
2. **Docstrings**: Use Google style
3. **Type Hints**: Add type annotations
4. **Comments**: Write in English
5. **UI Text**: Persian only
6. **Testing**: Add tests for new features
7. **Documentation**: Update this guide

## License

Copyright 2025. All rights reserved.
