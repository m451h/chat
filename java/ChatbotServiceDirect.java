package com.ehr.chatbot.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Direct integration with Python chatbot via subprocess execution
 * Calls chatbot_cli.py directly without REST API
 */
@Service
public class ChatbotServiceDirect {

    private static final Logger logger = LoggerFactory.getLogger(ChatbotServiceDirect.class);
    
    private final String pythonExecutable;
    private final String chatbotScriptPath;
    private final ObjectMapper objectMapper;
    private final int timeoutSeconds;

    public ChatbotServiceDirect(
            @Value("${chatbot.python.executable:python}") String pythonExecutable,
            @Value("${chatbot.python.script-path:core/chatbot_cli.py}") String chatbotScriptPath,
            @Value("${chatbot.python.timeout:120}") int timeoutSeconds
    ) {
        this.pythonExecutable = pythonExecutable;
        this.chatbotScriptPath = chatbotScriptPath;
        this.timeoutSeconds = timeoutSeconds;
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Check if Python chatbot is available
     */
    public boolean checkHealth() {
        try {
            Map<String, Object> request = new HashMap<>();
            request.put("command", "health");
            
            Map<String, Object> response = executePythonScript(request);
            return response != null && Boolean.TRUE.equals(response.get("success"));
        } catch (Exception e) {
            logger.error("Health check failed", e);
            return false;
        }
    }

    /**
     * Generate initial educational message about a condition
     *
     * @param conditionName Persian name of the condition
     * @param conditionData Optional patient condition data
     * @return Generated educational message
     */
    public String generateInitialMessage(String conditionName, Map<String, Object> conditionData) {
        Map<String, Object> request = new HashMap<>();
        request.put("command", "generate_educational");
        request.put("condition_name", conditionName);
        request.put("condition_data", conditionData);
        request.put("session_id", 0);

        try {
            Map<String, Object> response = executePythonScript(request);
            
            if (response == null) {
                throw new ChatbotException("No response from Python script");
            }
            
            Boolean success = (Boolean) response.get("success");
            if (success == null || !success) {
                String error = (String) response.get("error");
                throw new ChatbotException("Failed to generate initial message: " + error);
            }
            
            return (String) response.get("message");
        } catch (ChatbotException e) {
            throw e;
        } catch (Exception e) {
            throw new ChatbotException("Error calling Python chatbot", e);
        }
    }

    /**
     * Send a chat message and get response
     *
     * @param question User's question
     * @param sessionId Unique session identifier
     * @param conversationHistory Previous messages in the conversation
     * @param conditionData Optional patient condition data
     * @return Bot's response
     */
    @SuppressWarnings("unchecked")
    public String chat(
            String question,
            Integer sessionId,
            List<Map<String, Object>> conversationHistory,
            Map<String, Object> conditionData
    ) {
        Map<String, Object> request = new HashMap<>();
        request.put("command", "chat");
        request.put("question", question);
        request.put("session_id", sessionId);
        request.put("conversation_history", conversationHistory);
        request.put("condition_data", conditionData);

        try {
            Map<String, Object> response = executePythonScript(request);
            
            if (response == null) {
                throw new ChatbotException("No response from Python script");
            }
            
            Boolean success = (Boolean) response.get("success");
            if (success == null || !success) {
                String error = (String) response.get("error");
                throw new ChatbotException("Chat failed: " + error);
            }
            
            return (String) response.get("answer");
        } catch (ChatbotException e) {
            throw e;
        } catch (Exception e) {
            throw new ChatbotException("Error calling Python chatbot", e);
        }
    }

    /**
     * Execute Python script with JSON input/output
     */
    @SuppressWarnings("unchecked")
    private Map<String, Object> executePythonScript(Map<String, Object> request) throws Exception {
        // Convert request to JSON
        String jsonInput = objectMapper.writeValueAsString(request);
        
        logger.debug("Executing Python script: {} with input: {}", chatbotScriptPath, jsonInput);
        
        // Build process command
        ProcessBuilder processBuilder = new ProcessBuilder(
            pythonExecutable,
            chatbotScriptPath
        );
        
        // Set working directory to project root (adjust if needed)
        File scriptFile = new File(chatbotScriptPath);
        if (scriptFile.exists()) {
            processBuilder.directory(scriptFile.getParentFile().getParentFile());
        }
        
        // Redirect error stream to output for debugging
        processBuilder.redirectErrorStream(true);
        
        // Start process
        Process process = processBuilder.start();
        
        // Write JSON input to stdin
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(process.getOutputStream(), StandardCharsets.UTF_8))) {
            writer.write(jsonInput);
            writer.flush();
        }
        
        // Read JSON output from stdout
        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
        }
        
        // Wait for process to complete
        boolean finished = process.waitFor(timeoutSeconds, TimeUnit.SECONDS);
        if (!finished) {
            process.destroyForcibly();
            throw new ChatbotException("Python script execution timeout after " + timeoutSeconds + " seconds");
        }
        
        int exitCode = process.exitValue();
        if (exitCode != 0) {
            throw new ChatbotException("Python script exited with code " + exitCode + ". Output: " + output);
        }
        
        // Parse JSON response
        String jsonOutput = output.toString().trim();
        if (jsonOutput.isEmpty()) {
            throw new ChatbotException("Empty response from Python script");
        }
        
        return objectMapper.readValue(jsonOutput, Map.class);
    }

    /**
     * Custom exception for chatbot errors
     */
    public static class ChatbotException extends RuntimeException {
        public ChatbotException(String message) {
            super(message);
        }

        public ChatbotException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}

