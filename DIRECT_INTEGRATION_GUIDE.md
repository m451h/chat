# Direct Python-Java Integration Guide

This guide explains how to integrate the Python chatbot directly into your Java backend **without using a REST API**. The Java code executes Python scripts directly via subprocess.

## Architecture

```
┌─────────────┐
│ Java Backend│
│             │
│ ProcessBuilder
│     │
│     └──> python core/chatbot_cli.py
│              │
│              └──> MedicalChatbot (Python)
│                      │
│                      └──> OpenAI API
└─────────────┘
```

## How It Works

1. **Python CLI Script** (`core/chatbot_cli.py`): Accepts JSON via stdin, outputs JSON via stdout
2. **Java Service** (`ChatbotServiceDirect.java`): Uses `ProcessBuilder` to execute Python script
3. **Communication**: JSON over stdin/stdout

## Prerequisites

1. **Python Environment**: Python 3.8+ with all dependencies installed
2. **Environment Variables**: `OPENAI_API_KEY` must be set in the environment where Java runs
3. **Python Path**: Python executable must be in PATH, or specify full path in config

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Windows
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY=your-api-key-here
```

### 3. Configure Java Application

Add to `application.properties`:

```properties
# Python executable (use 'python', 'python3', or full path like 'C:\Python39\python.exe')
chatbot.python.executable=python

# Path to chatbot_cli.py (relative to project root)
chatbot.python.script-path=core/chatbot_cli.py

# Timeout in seconds
chatbot.python.timeout=120
```

### 4. Add Java Dependencies

For Maven (`pom.xml`):

```xml
<dependencies>
    <!-- Spring Boot -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- Jackson for JSON -->
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
    </dependency>
    
    <!-- Logging -->
    <dependency>
        <groupId>org.slf4j</groupId>
        <artifactId>slf4j-api</artifactId>
    </dependency>
</dependencies>
```

## Usage

### Basic Example

```java
@Autowired
private ChatbotServiceDirect chatbotService;

// Generate initial message
Map<String, Object> conditionData = new HashMap<>();
conditionData.put("age", 45);
conditionData.put("gender", "male");

String message = chatbotService.generateInitialMessage(
    "دیابت نوع 2",
    conditionData
);

// Chat
List<Map<String, Object>> history = Arrays.asList(
    Map.of("role", "user", "content", "سلام"),
    Map.of("role", "assistant", "content", "سلام! چطور می‌تونم کمکتون کنم؟")
);

String answer = chatbotService.chat(
    "آیا می‌توانم ورزش کنم؟",
    123,
    history,
    conditionData
);
```

### Using the Controller

The `ChatbotControllerDirect` provides REST endpoints:

```bash
# Health check
GET /api/chatbot/health

# Generate initial message
POST /api/chatbot/generate-initial?conditionName=دیابت نوع 2
Content-Type: application/json
{
  "age": 45,
  "gender": "male"
}

# Chat
POST /api/chatbot/chat
Content-Type: application/json
{
  "question": "آیا می‌توانم ورزش کنم؟",
  "sessionId": 123,
  "conversationHistory": [
    {"role": "user", "content": "سلام"},
    {"role": "assistant", "content": "سلام!"}
  ],
  "conditionData": {
    "age": 45
  }
}
```

## Configuration Options

### Python Executable

**Windows:**
```properties
chatbot.python.executable=C:\Python39\python.exe
# or
chatbot.python.executable=python
```

**Linux/Mac:**
```properties
chatbot.python.executable=python3
# or
chatbot.python.executable=/usr/bin/python3
```

### Script Path

**Relative to project root:**
```properties
chatbot.python.script-path=core/chatbot_cli.py
```

**Absolute path:**
```properties
chatbot.python.script-path=/path/to/ehr_chatbot/core/chatbot_cli.py
```

### Timeout

Adjust timeout based on your needs:
```properties
# 2 minutes for educational content
chatbot.python.timeout=120

# 1 minute for chat
chatbot.python.timeout=60
```

## Error Handling

The service throws `ChatbotException` on errors:

```java
try {
    String message = chatbotService.generateInitialMessage(conditionName, conditionData);
} catch (ChatbotServiceDirect.ChatbotException e) {
    logger.error("Chatbot error: {}", e.getMessage());
    // Handle error
}
```

Common errors:
- **Python not found**: Check `chatbot.python.executable` path
- **Script not found**: Check `chatbot.python.script-path`
- **Timeout**: Increase `chatbot.python.timeout`
- **Missing dependencies**: Ensure Python environment has all packages
- **API key missing**: Set `OPENAI_API_KEY` environment variable

## Performance Considerations

### Process Overhead

Each call spawns a new Python process. For high-throughput scenarios:

1. **Use a connection pool**: Keep Python processes alive (advanced)
2. **Batch requests**: Combine multiple operations when possible
3. **Cache results**: Cache initial educational messages per condition

### Memory

Python processes consume memory. Monitor:
- Number of concurrent requests
- Python process memory usage
- JVM heap size

### Timeout

Set appropriate timeouts:
- Educational content: 60-120 seconds
- Chat: 30-60 seconds

## Troubleshooting

### Python Not Found

**Error**: `java.io.IOException: Cannot run program "python"`

**Solution**:
1. Verify Python is installed: `python --version`
2. Use full path in config: `chatbot.python.executable=C:\Python39\python.exe`
3. Add Python to system PATH

### Script Not Found

**Error**: Script execution fails silently or returns error

**Solution**:
1. Verify script exists: `ls core/chatbot_cli.py`
2. Use absolute path in config
3. Check working directory in ProcessBuilder

### Import Errors

**Error**: Python script fails with `ModuleNotFoundError`

**Solution**:
1. Install dependencies: `pip install -r requirements.txt`
2. Use virtual environment and specify Python from venv
3. Set `PYTHONPATH` environment variable

### Encoding Issues

**Error**: Persian text appears garbled

**Solution**:
- Already handled with UTF-8 encoding in the code
- Ensure terminal/console supports UTF-8

### Timeout Issues

**Error**: `Python script execution timeout`

**Solution**:
1. Increase timeout: `chatbot.python.timeout=180`
2. Check Python script logs for slow operations
3. Optimize Python code if needed

## Testing

### Manual Test

Test the Python script directly:

```bash
# Windows PowerShell
echo '{"command":"health"}' | python core/chatbot_cli.py

# Linux/Mac
echo '{"command":"health"}' | python3 core/chatbot_cli.py
```

### Integration Test

```java
@SpringBootTest
class ChatbotServiceDirectTest {
    
    @Autowired
    private ChatbotServiceDirect chatbotService;
    
    @Test
    void testHealthCheck() {
        assertTrue(chatbotService.checkHealth());
    }
    
    @Test
    void testGenerateInitialMessage() {
        Map<String, Object> data = Map.of("age", 45);
        String message = chatbotService.generateInitialMessage("دیابت نوع 2", data);
        assertNotNull(message);
        assertFalse(message.isEmpty());
    }
}
```

## Advantages vs REST API

✅ **Pros:**
- No separate service to manage
- Lower latency (no network overhead)
- Simpler deployment (no API server)
- Direct access to Python code

❌ **Cons:**
- Process overhead per call
- Less scalable (process spawning)
- Harder to monitor/debug
- Platform-dependent (Python must be installed)

## Production Recommendations

1. **Use REST API** for production (better scalability)
2. **Use direct integration** for:
   - Development/testing
   - Low-traffic applications
   - Embedded systems
   - When you need tight coupling

3. **Hybrid approach**: Use direct integration with a process pool for better performance

## Security Considerations

1. **Input validation**: Validate all inputs before sending to Python
2. **Path security**: Use absolute paths, avoid user input in paths
3. **Resource limits**: Set appropriate timeouts and memory limits
4. **Error messages**: Don't expose internal errors to users

## Next Steps

1. Test the integration with your Java backend
2. Configure paths and timeouts appropriately
3. Add error handling and logging
4. Consider caching for frequently accessed data
5. Monitor performance and adjust as needed

