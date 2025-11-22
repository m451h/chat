package com.ehr.chatbot.example;

import com.ehr.chatbot.service.ChatbotServiceDirect;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.util.*;

/**
 * Quick start example demonstrating direct Python integration
 * 
 * Prerequisites:
 * - Python 3.8+ installed
 * - Dependencies installed: pip install -r requirements.txt
 * - OPENAI_API_KEY environment variable set
 * 
 * Run with: mvn spring-boot:run
 */
@SpringBootApplication
public class QuickStartExampleDirect {

    @Autowired
    private ChatbotServiceDirect chatbotService;

    public static void main(String[] args) {
        SpringApplication.run(QuickStartExampleDirect.class, args);
    }

    @Bean
    public CommandLineRunner run() {
        return args -> {
            System.out.println("=== EHR Chatbot Direct Integration Example ===\n");

            // 1. Check health
            System.out.println("1. Checking Python chatbot availability...");
            boolean healthy = chatbotService.checkHealth();
            if (healthy) {
                System.out.println("✅ Python chatbot is available\n");
            } else {
                System.out.println("❌ Python chatbot is not available.");
                System.out.println("   Make sure:");
                System.out.println("   - Python is installed and in PATH");
                System.out.println("   - Dependencies are installed: pip install -r requirements.txt");
                System.out.println("   - OPENAI_API_KEY is set\n");
                return;
            }

            // 2. Generate initial educational message
            System.out.println("2. Generating initial educational message...");
            Map<String, Object> conditionData = new HashMap<>();
            conditionData.put("age", 45);
            conditionData.put("gender", "male");
            conditionData.put("diagnosis_date", "2023-01-15");

            String initialMessage;
            try {
                initialMessage = chatbotService.generateInitialMessage(
                    "دیابت نوع 2",
                    conditionData
                );
                System.out.println("Generated message (first 200 chars):");
                System.out.println(initialMessage.substring(0, Math.min(200, initialMessage.length())) + "...\n");
            } catch (ChatbotServiceDirect.ChatbotException e) {
                System.out.println("❌ Error: " + e.getMessage() + "\n");
                return;
            }

            // 3. Start a conversation
            System.out.println("3. Starting a conversation...");
            Integer sessionId = 999;

            // First message
            String question1 = "آیا می‌توانم ورزش کنم؟";
            List<Map<String, Object>> history1 = Arrays.asList(
                Map.of("role", "user", "content", "سلام"),
                Map.of("role", "assistant", "content", 
                    initialMessage.substring(0, Math.min(100, initialMessage.length())))
            );

            String answer1;
            try {
                answer1 = chatbotService.chat(question1, sessionId, history1, conditionData);
                System.out.println("Question: " + question1);
                System.out.println("Answer: " + answer1.substring(0, Math.min(200, answer1.length())) + "...\n");
            } catch (ChatbotServiceDirect.ChatbotException e) {
                System.out.println("❌ Error: " + e.getMessage() + "\n");
                return;
            }

            // Second message (with updated history)
            String question2 = "چه نوع ورزشی توصیه می‌کنید؟";
            List<Map<String, Object>> history2 = Arrays.asList(
                Map.of("role", "user", "content", "سلام"),
                Map.of("role", "assistant", "content", 
                    initialMessage.substring(0, Math.min(100, initialMessage.length()))),
                Map.of("role", "user", "content", question1),
                Map.of("role", "assistant", "content", answer1)
            );

            String answer2;
            try {
                answer2 = chatbotService.chat(question2, sessionId, history2, conditionData);
                System.out.println("Question: " + question2);
                System.out.println("Answer: " + answer2.substring(0, Math.min(200, answer2.length())) + "...\n");
            } catch (ChatbotServiceDirect.ChatbotException e) {
                System.out.println("❌ Error: " + e.getMessage() + "\n");
                return;
            }

            System.out.println("=== Example completed successfully! ===");
        };
    }
}

