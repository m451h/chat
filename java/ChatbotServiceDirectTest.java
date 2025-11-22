package com.ehr.chatbot.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Integration tests for ChatbotServiceDirect
 * 
 * Prerequisites:
 * - Python 3.8+ installed and in PATH
 * - All Python dependencies installed (pip install -r requirements.txt)
 * - OPENAI_API_KEY environment variable set
 */
@SpringBootTest
@TestPropertySource(properties = {
    "chatbot.python.executable=python",
    "chatbot.python.script-path=core/chatbot_cli.py",
    "chatbot.python.timeout=120"
})
public class ChatbotServiceDirectTest {

    @Autowired
    private ChatbotServiceDirect chatbotService;

    @BeforeEach
    void setUp() {
        // Verify Python chatbot is available
        boolean healthy = chatbotService.checkHealth();
        assertTrue(healthy, 
            "Python chatbot is not available. " +
            "Make sure Python is installed, dependencies are installed, " +
            "and OPENAI_API_KEY is set.");
    }

    @Test
    void testHealthCheck() {
        boolean healthy = chatbotService.checkHealth();
        assertTrue(healthy);
    }

    @Test
    void testGenerateInitialMessage() {
        Map<String, Object> conditionData = new HashMap<>();
        conditionData.put("age", 45);
        conditionData.put("gender", "male");
        conditionData.put("diagnosis_date", "2023-01-15");

        String message = chatbotService.generateInitialMessage(
            "دیابت نوع 2",
            conditionData
        );

        assertNotNull(message);
        assertFalse(message.isEmpty());
        System.out.println("Generated message (first 200 chars):");
        System.out.println(message.substring(0, Math.min(200, message.length())) + "...");
    }

    @Test
    void testGenerateInitialMessageWithoutData() {
        String message = chatbotService.generateInitialMessage(
            "دیابت نوع 2",
            null
        );

        assertNotNull(message);
        assertFalse(message.isEmpty());
    }

    @Test
    void testChat() {
        Integer sessionId = 12345;
        String question = "آیا می‌توانم ورزش کنم؟";

        Map<String, Object> conditionData = new HashMap<>();
        conditionData.put("age", 45);
        conditionData.put("gender", "male");

        List<Map<String, Object>> history = Arrays.asList(
            Map.of("role", "user", "content", "سلام"),
            Map.of("role", "assistant", "content", "سلام! چطور می‌تونم کمکتون کنم؟")
        );

        String answer = chatbotService.chat(
            question,
            sessionId,
            history,
            conditionData
        );

        assertNotNull(answer);
        assertFalse(answer.isEmpty());
        System.out.println("Chat answer (first 200 chars):");
        System.out.println(answer.substring(0, Math.min(200, answer.length())) + "...");
    }

    @Test
    void testChatWithoutHistory() {
        Integer sessionId = 12346;
        String question = "سلام";

        String answer = chatbotService.chat(
            question,
            sessionId,
            null,
            null
        );

        assertNotNull(answer);
        assertFalse(answer.isEmpty());
    }

    @Test
    void testChatWithNestedConditionData() {
        Integer sessionId = 12347;
        String question = "در مورد بیماری من بگویید";

        Map<String, Object> conditionData = new HashMap<>();
        conditionData.put("age", 45);
        conditionData.put("gender", "male");
        
        // Nested structure
        Map<String, Object> medications = new HashMap<>();
        medications.put("name", "Metformin");
        medications.put("dose", "500mg");
        conditionData.put("medications", Arrays.asList(medications));

        String answer = chatbotService.chat(
            question,
            sessionId,
            null,
            conditionData
        );

        assertNotNull(answer);
        assertFalse(answer.isEmpty());
    }

    @Test
    void testErrorHandling() {
        // Test with invalid input
        assertThrows(ChatbotServiceDirect.ChatbotException.class, () -> {
            chatbotService.generateInitialMessage(null, null);
        });
    }
}

