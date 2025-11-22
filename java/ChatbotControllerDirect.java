package com.ehr.chatbot.controller;

import com.ehr.chatbot.service.ChatbotServiceDirect;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * REST Controller for direct Python chatbot integration
 * Exposes chatbot functionality to your frontend/other services
 */
@RestController
@RequestMapping("/api/chatbot")
public class ChatbotControllerDirect {

    @Autowired
    private ChatbotServiceDirect chatbotService;

    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        boolean healthy = chatbotService.checkHealth();
        return ResponseEntity.ok(Map.of(
            "status", healthy ? "healthy" : "unhealthy",
            "success", healthy
        ));
    }

    /**
     * Generate initial educational message
     */
    @PostMapping("/generate-initial")
    public ResponseEntity<?> generateInitialMessage(
            @RequestParam String conditionName,
            @RequestBody(required = false) Map<String, Object> conditionData
    ) {
        try {
            String message = chatbotService.generateInitialMessage(conditionName, conditionData);
            return ResponseEntity.ok(Map.of(
                "message", message,
                "success", true
            ));
        } catch (ChatbotServiceDirect.ChatbotException e) {
            return ResponseEntity.status(500)
                    .body(Map.of(
                        "error", e.getMessage(),
                        "success", false
                    ));
        }
    }

    /**
     * Chat endpoint
     */
    @PostMapping("/chat")
    public ResponseEntity<?> chat(@RequestBody ChatRequest request) {
        try {
            String answer = chatbotService.chat(
                request.getQuestion(),
                request.getSessionId(),
                request.getConversationHistory(),
                request.getConditionData()
            );
            return ResponseEntity.ok(Map.of(
                "answer", answer,
                "success", true
            ));
        } catch (ChatbotServiceDirect.ChatbotException e) {
            return ResponseEntity.status(500)
                    .body(Map.of(
                        "error", e.getMessage(),
                        "success", false
                    ));
        }
    }

    /**
     * Request wrapper for chat endpoint
     */
    public static class ChatRequest {
        private String question;
        private Integer sessionId;
        private List<Map<String, Object>> conversationHistory;
        private Map<String, Object> conditionData;

        public String getQuestion() {
            return question;
        }

        public void setQuestion(String question) {
            this.question = question;
        }

        public Integer getSessionId() {
            return sessionId;
        }

        public void setSessionId(Integer sessionId) {
            this.sessionId = sessionId;
        }

        public List<Map<String, Object>> getConversationHistory() {
            return conversationHistory;
        }

        public void setConversationHistory(List<Map<String, Object>> conversationHistory) {
            this.conversationHistory = conversationHistory;
        }

        public Map<String, Object> getConditionData() {
            return conditionData;
        }

        public void setConditionData(Map<String, Object> conditionData) {
            this.conditionData = conditionData;
        }
    }
}

