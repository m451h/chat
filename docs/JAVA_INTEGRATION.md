# Java Integration Guide

This guide explains how to integrate the EHR Chatbot with your Java-based backend by calling the Python CLI script directly.

## Overview

Instead of using the FastAPI server, you can call the Python script (`cli.py`) directly from Java using `ProcessBuilder`. This approach:

- ✅ No need to run a separate API server
- ✅ Direct execution of Python code
- ✅ Simple JSON-based communication
- ✅ Works with any Java application

## Prerequisites

1. **Python Environment**: Ensure Python 3.8+ is installed and accessible from your Java application
2. **Dependencies**: Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables**: Set up `.env` file with `OPENAI_API_KEY` and other settings

## Quick Start

### 1. Basic Java Code

```java
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeUnit;

public class ChatbotClient {
    public String callPython(String jsonInput) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder(
            "python",  // or "python3" or full path
            "cli.py",  // path to cli.py
            jsonInput
        );
        
        Process process = pb.start();
        
        // Read output
        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
        }
        
        process.waitFor(30, TimeUnit.SECONDS);
        return output.toString();
    }
}
```

### 2. Example Usage

```java
// Start a session
String jsonInput = "{\"action\":\"start_session\",\"user_id\":1234567890123,\"condition_name\":\"دیابت نوع 2\",\"patient_data\":{\"age\":45},\"generate_initial_content\":true}";
String response = callPython(jsonInput);
// Response: {"success":true,"session_id":1,"user_id":1234567890123,...}

// Send a message
String jsonInput2 = "{\"action\":\"send_message\",\"session_id\":1,\"message\":\"سوال من چیست؟\"}";
String response2 = callPython(jsonInput2);
// Response: {"success":true,"session_id":1,"reply":{"role":"assistant","content":"...",...}}
```

## Available Actions

### 1. Start Session

Start a new chat session for a user and condition.

**Input:**
```json
{
  "action": "start_session",
  "user_id": 1234567890123,
  "condition_name": "دیابت نوع 2",
  "patient_data": {
    "age": 45,
    "medications": ["metformin"],
    "blood_sugar": 180
  },
  "generate_initial_content": true
}
```

**Response:**
```json
{
  "success": true,
  "session_id": 1,
  "user_id": 1234567890123,
  "condition_id": 1,
  "condition_name": "دیابت نوع 2",
  "initial_message": {
    "type": "education_note",
    "content": "محتوای آموزشی..."
  }
}
```

### 2. Send Message

Send a user message to an existing session and get a response.

**Input:**
```json
{
  "action": "send_message",
  "session_id": 1,
  "message": "آیا باید متفورمین را قبل از غذا مصرف کنم؟"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": 1,
  "reply": {
    "role": "assistant",
    "content": "بله، معمولاً متفورمین...",
    "created_at": "2025-01-15T10:30:00"
  }
}
```

### 3. Generate Educational Content

Generate educational content for an existing session.

**Input:**
```json
{
  "action": "generate_education",
  "session_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "session_id": 1,
  "content": "محتوای آموزشی کامل..."
}
```

### 4. Get Messages

Retrieve all messages for a session.

**Input:**
```json
{
  "action": "get_messages",
  "session_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "session_id": 1,
  "messages": [
    {
      "role": "system",
      "content": "patient_context:{...}",
      "created_at": "2025-01-15T10:00:00"
    },
    {
      "role": "assistant",
      "content": "...",
      "created_at": "2025-01-15T10:01:00"
    }
  ]
}
```

## Error Handling

All responses include an `error` field if something goes wrong:

```json
{
  "error": "Session 1 not found"
}
```

The script exits with a non-zero exit code on errors, so check `process.exitValue()` in Java.

## Best Practices

### 1. Use a JSON Library

Instead of manually building JSON strings, use a JSON library:

**With Jackson:**
```java
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

ObjectMapper mapper = new ObjectMapper();
ObjectNode request = mapper.createObjectNode();
request.put("action", "start_session");
request.put("user_id", 1234567890123L);
request.put("condition_name", "دیابت نوع 2");

ObjectNode patientData = mapper.createObjectNode();
patientData.put("age", 45);
request.set("patient_data", patientData);

String jsonInput = mapper.writeValueAsString(request);
```

**With Gson:**
```java
import com.google.gson.JsonObject;

JsonObject request = new JsonObject();
request.addProperty("action", "start_session");
request.addProperty("user_id", 1234567890123L);
request.addProperty("condition_name", "دیابت نوع 2");

JsonObject patientData = new JsonObject();
patientData.addProperty("age", 45);
request.add("patient_data", patientData);

String jsonInput = request.toString();
```

### 2. Handle Timeouts

Set appropriate timeouts for long-running operations:

```java
boolean finished = process.waitFor(60, TimeUnit.SECONDS);
if (!finished) {
    process.destroyForcibly();
    throw new TimeoutException("Script execution timed out");
}
```

### 3. Handle Encoding

Ensure UTF-8 encoding for Persian text:

```java
BufferedReader reader = new BufferedReader(
    new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8)
);
```

### 4. Path Configuration

Make paths configurable:

```java
String pythonPath = System.getProperty("chatbot.python.path", "python");
String scriptPath = System.getProperty("chatbot.script.path", "cli.py");
```

Or use environment variables or configuration files.

### 5. Logging

Log requests and responses for debugging:

```java
logger.debug("Sending request: " + jsonInput);
String response = callPython(jsonInput);
logger.debug("Received response: " + response);
```

## Performance Considerations

1. **Process Overhead**: Each call spawns a new Python process. For high-frequency calls, consider:
   - Caching session data
   - Batching operations
   - Using a connection pool pattern (though this requires keeping Python process alive)

2. **Database Location**: Ensure the SQLite database file is accessible and not locked by multiple processes.

3. **Concurrent Requests**: SQLite may have issues with concurrent writes. Consider:
   - Using a file-based lock
   - Using PostgreSQL instead of SQLite
   - Serializing requests

## Troubleshooting

### Python Not Found
```
Error: Cannot run program "python"
```
**Solution**: Use full path to Python executable or ensure Python is in PATH.

### Script Not Found
```
Error: Cannot run program "cli.py"
```
**Solution**: Use absolute path to `cli.py` or set working directory.

### Encoding Issues
If Persian text appears garbled, ensure UTF-8 encoding is used throughout.

### Timeout Issues
If operations take too long, increase timeout or optimize patient data size.

## Example Service Class

Here's a complete example service class:

```java
@Service
public class EHRChatbotService {
    private static final Logger logger = LoggerFactory.getLogger(EHRChatbotService.class);
    
    private final String pythonPath;
    private final String scriptPath;
    private final ObjectMapper objectMapper;
    
    @Value("${chatbot.python.path:python}")
    private String pythonPath;
    
    @Value("${chatbot.script.path:cli.py}")
    private String scriptPath;
    
    public ChatbotResponse startSession(StartSessionRequest request) {
        try {
            ObjectNode jsonRequest = objectMapper.createObjectNode();
            jsonRequest.put("action", "start_session");
            jsonRequest.put("user_id", request.getUserId());
            jsonRequest.put("condition_name", request.getConditionName());
            jsonRequest.set("patient_data", objectMapper.valueToTree(request.getPatientData()));
            jsonRequest.put("generate_initial_content", request.isGenerateInitialContent());
            
            String response = executePython(jsonRequest.toString());
            return objectMapper.readValue(response, ChatbotResponse.class);
        } catch (Exception e) {
            logger.error("Failed to start session", e);
            throw new ChatbotException("Failed to start session", e);
        }
    }
    
    private String executePython(String jsonInput) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder(pythonPath, scriptPath, jsonInput);
        Process process = pb.start();
        
        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
        }
        
        boolean finished = process.waitFor(30, TimeUnit.SECONDS);
        if (!finished) {
            process.destroyForcibly();
            throw new TimeoutException("Python script timed out");
        }
        
        if (process.exitValue() != 0) {
            throw new IOException("Python script failed: " + output.toString());
        }
        
        return output.toString();
    }
}
```

## Next Steps

1. Integrate the `EHRChatbotClient` class into your Java backend
2. Create service methods that wrap the chatbot calls
3. Add proper error handling and logging
4. Configure paths and timeouts via application properties
5. Test with real patient data

For questions or issues, refer to the main README or contact the development team.

