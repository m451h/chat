import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeUnit;

/**
 * Example Java code for calling the Python EHR Chatbot CLI
 * 
 * This demonstrates how to invoke the Python script from Java using ProcessBuilder.
 * The script accepts JSON input and returns JSON output.
 */
public class EHRChatbotClient {
    
    private final String pythonPath;
    private final String scriptPath;
    private final int timeoutSeconds;
    
    /**
     * Constructor
     * @param pythonPath Path to Python executable (e.g., "python" or "python3" or full path)
     * @param scriptPath Path to cli.py script
     * @param timeoutSeconds Timeout for script execution in seconds
     */
    public EHRChatbotClient(String pythonPath, String scriptPath, int timeoutSeconds) {
        this.pythonPath = pythonPath;
        this.scriptPath = scriptPath;
        this.timeoutSeconds = timeoutSeconds;
    }
    
    /**
     * Execute a chatbot command and return JSON response
     * @param jsonInput JSON string with action and parameters
     * @return JSON response string
     * @throws IOException If execution fails
     * @throws InterruptedException If process is interrupted
     * @throws TimeoutException If execution times out
     */
    public String execute(String jsonInput) throws IOException, InterruptedException, TimeoutException {
        ProcessBuilder processBuilder = new ProcessBuilder(
            pythonPath,
            scriptPath,
            jsonInput
        );
        
        // Set working directory (optional, adjust as needed)
        // processBuilder.directory(new File("/path/to/ehr_chatbot"));
        
        // Redirect error stream to output stream to capture all output
        processBuilder.redirectErrorStream(true);
        
        Process process = processBuilder.start();
        
        // Read output
        StringBuilder output = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
        }
        
        // Wait for process to complete with timeout
        boolean finished = process.waitFor(timeoutSeconds, TimeUnit.SECONDS);
        if (!finished) {
            process.destroyForcibly();
            throw new TimeoutException("Python script execution timed out");
        }
        
        int exitCode = process.exitValue();
        String result = output.toString().trim();
        
        if (exitCode != 0) {
            throw new IOException("Python script failed with exit code " + exitCode + ": " + result);
        }
        
        return result;
    }
    
    /**
     * Start a new chat session
     * @param userId User ID
     * @param conditionName Condition name (e.g., "دیابت نوع 2")
     * @param patientData Patient data as JSON object string
     * @param generateInitialContent Whether to generate initial educational content
     * @return JSON response
     */
    public String startSession(int userId, String conditionName, String patientData, boolean generateInitialContent) 
            throws IOException, InterruptedException, TimeoutException {
        String jsonInput = String.format(
            "{\"action\":\"start_session\",\"user_id\":%d,\"condition_name\":\"%s\",\"patient_data\":%s,\"generate_initial_content\":%s}",
            userId, conditionName, patientData, generateInitialContent
        );
        return execute(jsonInput);
    }
    
    /**
     * Send a message to an existing session
     * @param sessionId Session ID
     * @param message User message
     * @return JSON response
     */
    public String sendMessage(int sessionId, String message) 
            throws IOException, InterruptedException, TimeoutException {
        // Escape JSON special characters in message
        String escapedMessage = message
            .replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t");
        
        String jsonInput = String.format(
            "{\"action\":\"send_message\",\"session_id\":%d,\"message\":\"%s\"}",
            sessionId, escapedMessage
        );
        return execute(jsonInput);
    }
    
    /**
     * Generate educational content for a session
     * @param sessionId Session ID
     * @return JSON response
     */
    public String generateEducation(int sessionId) 
            throws IOException, InterruptedException, TimeoutException {
        String jsonInput = String.format(
            "{\"action\":\"generate_education\",\"session_id\":%d}",
            sessionId
        );
        return execute(jsonInput);
    }
    
    /**
     * Get all messages for a session
     * @param sessionId Session ID
     * @return JSON response
     */
    public String getMessages(int sessionId) 
            throws IOException, InterruptedException, TimeoutException {
        String jsonInput = String.format(
            "{\"action\":\"get_messages\",\"session_id\":%d}",
            sessionId
        );
        return execute(jsonInput);
    }
    
    // Example usage
    public static void main(String[] args) {
        try {
            // Initialize client
            // Adjust paths based on your environment
            EHRChatbotClient client = new EHRChatbotClient(
                "python",  // or "python3" or full path like "C:\\Python39\\python.exe"
                "cli.py",  // or full path like "C:\\path\\to\\ehr_chatbot\\cli.py"
                30  // 30 second timeout
            );
            
            // Example 1: Start a session
            String patientData = "{\"age\":45,\"medications\":[\"metformin\"],\"blood_sugar\":180}";
            String response1 = client.startSession(
                1234567890123L,
                "دیابت نوع 2",
                patientData,
                true
            );
            System.out.println("Start session response: " + response1);
            
            // Parse response to get session_id (using a JSON library like Jackson or Gson)
            // For this example, we'll assume session_id is 1
            
            // Example 2: Send a message
            String response2 = client.sendMessage(1, "آیا باید متفورمین را قبل از غذا مصرف کنم؟");
            System.out.println("Send message response: " + response2);
            
            // Example 3: Get all messages
            String response3 = client.getMessages(1);
            System.out.println("Get messages response: " + response3);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

/**
 * Alternative approach using JSON library (recommended)
 * 
 * Instead of manually building JSON strings, use a JSON library like:
 * - Jackson (com.fasterxml.jackson.core:jackson-databind)
 * - Gson (com.google.code.gson:gson)
 * 
 * Example with Jackson:
 * 
 * import com.fasterxml.jackson.databind.ObjectMapper;
 * import com.fasterxml.jackson.databind.node.ObjectNode;
 * 
 * ObjectMapper mapper = new ObjectMapper();
 * ObjectNode request = mapper.createObjectNode();
 * request.put("action", "start_session");
 * request.put("user_id", 1234567890123L);
 * request.put("condition_name", "دیابت نوع 2");
 * request.putObject("patient_data").put("age", 45);
 * request.put("generate_initial_content", true);
 * 
 * String jsonInput = mapper.writeValueAsString(request);
 * String response = client.execute(jsonInput);
 * 
 * ObjectNode responseJson = (ObjectNode) mapper.readTree(response);
 * int sessionId = responseJson.get("session_id").asInt();
 */

