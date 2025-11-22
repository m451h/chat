# Direct Python-Java Integration Summary

## Overview

This integration allows your Java backend to call the Python chatbot **directly** without using a REST API. Java executes Python scripts via `ProcessBuilder` and communicates via JSON over stdin/stdout.

## Files Created

### Python Side
- **`core/chatbot_cli.py`** - Command-line interface that accepts JSON input and outputs JSON

### Java Side
- **`java/ChatbotServiceDirect.java`** - Main service class that executes Python scripts
- **`java/ChatbotControllerDirect.java`** - REST controller example
- **`java/ChatbotServiceDirectTest.java`** - Integration tests
- **`java/QuickStartExampleDirect.java`** - Working example
- **`java/application.properties.example`** - Configuration template

### Documentation
- **`DIRECT_INTEGRATION_GUIDE.md`** - Complete integration guide
- **`java/README_DIRECT.md`** - Quick reference

### Testing
- **`test_chatbot_cli.py`** - Test script for Python CLI

## Quick Start

### 1. Test Python CLI

```bash
# Test the CLI directly
python test_chatbot_cli.py

# Or manually
echo '{"command":"health"}' | python core/chatbot_cli.py
```

### 2. Configure Java

Add to `application.properties`:

```properties
chatbot.python.executable=python
chatbot.python.script-path=core/chatbot_cli.py
chatbot.python.timeout=120
```

### 3. Use in Java

```java
@Autowired
private ChatbotServiceDirect chatbotService;

// Generate initial message
String message = chatbotService.generateInitialMessage(
    "دیابت نوع 2",
    Map.of("age", 45, "gender", "male")
);

// Chat
String answer = chatbotService.chat(
    "آیا می‌توانم ورزش کنم؟",
    123,
    conversationHistory,
    conditionData
);
```

## How It Works

```
Java Code
    │
    ├─> ProcessBuilder.execute("python core/chatbot_cli.py")
    │
    ├─> Write JSON to stdin
    │   {
    │     "command": "chat",
    │     "question": "سلام",
    │     "session_id": 123
    │   }
    │
    └─> Read JSON from stdout
        {
          "success": true,
          "answer": "سلام! چطور می‌تونم کمکتون کنم؟"
        }
```

## Commands Supported

### 1. Health Check
```json
{"command": "health"}
```

### 2. Generate Educational Content
```json
{
  "command": "generate_educational",
  "condition_name": "دیابت نوع 2",
  "condition_data": {"age": 45},
  "session_id": 0
}
```

### 3. Chat
```json
{
  "command": "chat",
  "question": "آیا می‌توانم ورزش کنم؟",
  "session_id": 123,
  "conversation_history": [
    {"role": "user", "content": "سلام"},
    {"role": "assistant", "content": "سلام!"}
  ],
  "condition_data": {"age": 45}
}
```

## Configuration

### Required
- Python 3.8+ installed
- Python dependencies: `pip install -r requirements.txt`
- `OPENAI_API_KEY` environment variable

### Optional
- `chatbot.python.executable` - Python executable path (default: "python")
- `chatbot.python.script-path` - Path to chatbot_cli.py (default: "core/chatbot_cli.py")
- `chatbot.python.timeout` - Timeout in seconds (default: 120)

## Advantages

✅ **No REST API needed** - Direct integration  
✅ **Simple deployment** - No separate service  
✅ **Low latency** - No network overhead  
✅ **Full control** - Direct access to Python code  

## Limitations

⚠️ **Process overhead** - Each call spawns a new process  
⚠️ **Less scalable** - Not ideal for high throughput  
⚠️ **Platform dependent** - Requires Python installation  
⚠️ **Harder to monitor** - No HTTP metrics  

## When to Use

**Use Direct Integration When:**
- Low to medium traffic
- Development/testing
- Embedded systems
- Tight coupling needed
- Simple deployment preferred

**Use REST API When:**
- High traffic/throughput
- Production systems
- Need horizontal scaling
- Multiple consumers
- Better observability needed

## Troubleshooting

### Python Not Found
```properties
# Use full path
chatbot.python.executable=C:\Python39\python.exe
```

### Script Not Found
```properties
# Use absolute path
chatbot.python.script-path=/full/path/to/core/chatbot_cli.py
```

### Import Errors
```bash
# Install dependencies
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Timeout
```properties
# Increase timeout
chatbot.python.timeout=180
```

## Next Steps

1. ✅ Test Python CLI: `python test_chatbot_cli.py`
2. ✅ Configure Java application properties
3. ✅ Run integration tests: `mvn test`
4. ✅ Integrate into your Java backend
5. ✅ Add error handling and logging
6. ✅ Monitor performance

## Support

For issues:
1. Check `DIRECT_INTEGRATION_GUIDE.md` for detailed troubleshooting
2. Test Python CLI directly: `python test_chatbot_cli.py`
3. Check Java logs for ProcessBuilder errors
4. Verify Python environment and dependencies

