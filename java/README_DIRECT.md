# Direct Python Integration - Java Client

This directory contains Java code for **direct integration** with the Python chatbot (no REST API).

## Architecture

Java → ProcessBuilder → Python Script → MedicalChatbot

## Files

- `ChatbotServiceDirect.java` - Main service class
- `ChatbotControllerDirect.java` - REST controller example
- `ChatbotServiceDirectTest.java` - Integration tests
- `QuickStartExampleDirect.java` - Working example
- `application.properties.example` - Configuration template

## Quick Start

### 1. Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY=your-api-key
```

### 2. Configure

Add to `application.properties`:

```properties
chatbot.python.executable=python
chatbot.python.script-path=core/chatbot_cli.py
chatbot.python.timeout=120
```

### 3. Use It

```java
@Autowired
private ChatbotServiceDirect chatbotService;

// Generate message
String message = chatbotService.generateInitialMessage(
    "دیابت نوع 2",
    Map.of("age", 45)
);

// Chat
String answer = chatbotService.chat(
    "سوال من",
    123,
    conversationHistory,
    conditionData
);
```

## Configuration

### Python Executable

**Windows:**
```properties
chatbot.python.executable=python
# or full path
chatbot.python.executable=C:\Python39\python.exe
```

**Linux/Mac:**
```properties
chatbot.python.executable=python3
```

### Script Path

Relative to project root:
```properties
chatbot.python.script-path=core/chatbot_cli.py
```

Absolute path:
```properties
chatbot.python.script-path=/path/to/ehr_chatbot/core/chatbot_cli.py
```

## Testing

### Manual Test

Test Python script directly:

```bash
echo '{"command":"health"}' | python core/chatbot_cli.py
```

### Run Tests

```bash
mvn test
```

## Troubleshooting

### Python Not Found
- Check Python is in PATH: `python --version`
- Use full path in config

### Script Not Found
- Verify `core/chatbot_cli.py` exists
- Use absolute path if needed

### Import Errors
- Install dependencies: `pip install -r requirements.txt`
- Check Python environment

### Timeout
- Increase `chatbot.python.timeout`
- Check Python script performance

## See Also

- `DIRECT_INTEGRATION_GUIDE.md` - Complete integration guide
- `../core/chatbot_cli.py` - Python CLI script

