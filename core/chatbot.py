"""
Medical Chatbot core logic using LangChain and OpenAI GPT-4o-mini
"""
import json
from typing import List, Dict, Optional, Generator
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from config.settings import settings
from .prompts import get_educational_prompt, get_conversation_prompt, get_summarization_prompt


class MedicalChatbot:
    """
    Medical chatbot for personalized educational content and Q&A
    Uses LangChain with OpenAI GPT-4o-mini
    """
    
    def __init__(self):
        """Initialize chatbot with OpenAI model"""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            # Use custom base URL if provided (supports OpenAI-compatible endpoints)
            base_url=settings.OPENAI_BASE_URL or None,
            openai_api_key=settings.OPENAI_API_KEY,
            streaming=True
        )
        
        self.conversation_memory = {}  # Session-specific memory
    
    def _load_condition_data(self, data_file: str) -> Dict:
        """Load condition data from JSON file"""
        try:
            file_path = settings.MOCK_DATA_DIR / data_file
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading condition data: {e}")
            return {}
    
    def _get_memory(self, session_id: int) -> ConversationBufferWindowMemory:
        """Get or create conversation memory for a session"""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = ConversationBufferWindowMemory(
                k=settings.MAX_CONVERSATION_HISTORY,
                return_messages=True,
                memory_key="chat_history"
            )
        return self.conversation_memory[session_id]
    
    def _load_conversation_history(self, session_id: int, messages: List[Dict]):
        """Load conversation history into memory"""
        memory = self._get_memory(session_id)
        memory.clear()
        
        for msg in messages:
            if msg['role'] == 'user':
                memory.chat_memory.add_message(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                memory.chat_memory.add_message(AIMessage(content=msg['content']))
    
    def generate_educational_content(
        self,
        condition_name: str,
        condition_data_file: str,
        session_id: int
    ) -> str:
        """
        Generate initial educational content about a condition
        
        Args:
            condition_name: Persian name of the condition
            condition_data_file: Path to JSON file with user's condition data
            session_id: Chat session ID for memory management
        
        Returns:
            Educational content in Persian
        """
        try:
            # Load user's condition data
            condition_data = self._load_condition_data(condition_data_file)
            
            # Generate educational prompt
            prompt = get_educational_prompt(condition_name, condition_data)
            
            # Generate content
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            # Store in memory for context
            memory = self._get_memory(session_id)
            memory.chat_memory.add_message(SystemMessage(
                content=f"اطلاعات بیمار: {json.dumps(condition_data, ensure_ascii=False)}"
            ))
            memory.chat_memory.add_message(AIMessage(content=response.content))
            
            return response.content
        
        except Exception as e:
            print(f"Error generating educational content: {e}")
            return f"متأسفانه در تولید محتوای آموزشی خطایی رخ داد. لطفاً دوباره تلاش کنید.\n\nخطا: {str(e)}"
    
    def generate_educational_content_stream(
        self,
        condition_name: str,
        condition_data_file: str,
        session_id: int
    ) -> Generator[str, None, None]:
        """
        Stream educational content generation for better UX with long responses
        
        Args:
            condition_name: Persian name of the condition
            condition_data_file: Path to JSON file with user's condition data
            session_id: Chat session ID for memory management
        
        Yields:
            Chunks of educational content
        """
        try:
            # Load user's condition data
            condition_data = self._load_condition_data(condition_data_file)
            
            # Generate educational prompt
            prompt = get_educational_prompt(condition_name, condition_data)
            
            # Stream content
            messages = [HumanMessage(content=prompt)]
            full_response = ""
            
            for chunk in self.llm.stream(messages):
                content = chunk.content
                full_response += content
                yield content
            
            # Store in memory after completion
            memory = self._get_memory(session_id)
            memory.chat_memory.add_message(SystemMessage(
                content=f"اطلاعات بیمار: {json.dumps(condition_data, ensure_ascii=False)}"
            ))
            memory.chat_memory.add_message(AIMessage(content=full_response))
        
        except Exception as e:
            error_msg = f"متأسفانه در تولید محتوای آموزشی خطایی رخ داد: {str(e)}"
            yield error_msg
    
    def chat(
        self,
        question: str,
        session_id: int,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Answer user's question about their condition
        
        Args:
            question: User's question in Persian
            session_id: Chat session ID
            conversation_history: Previous messages (from database)
        
        Returns:
            Answer in Persian
        """
        try:
            # Load conversation history if provided
            if conversation_history:
                self._load_conversation_history(session_id, conversation_history)
            
            # Get memory for this session
            memory = self._get_memory(session_id)
            
            # Create conversation chain
            prompt = get_conversation_prompt()
            chain = ConversationChain(
                llm=self.llm,
                prompt=prompt,
                memory=memory,
                input_key="question",
                verbose=False
            )
            
            # Generate response
            response = chain.predict(question=question)
            
            return response
        
        except Exception as e:
            print(f"Error in chat: {e}")
            return f"متأسفانه در پاسخ به سوال شما خطایی رخ داد. لطفاً دوباره تلاش کنید.\n\nخطا: {str(e)}"
    
    def chat_stream(
        self,
        question: str,
        session_id: int,
        conversation_history: Optional[List[Dict]] = None
    ) -> Generator[str, None, None]:
        """
        Stream answer to user's question for better UX
        
        Args:
            question: User's question in Persian
            session_id: Chat session ID
            conversation_history: Previous messages (from database)
        
        Yields:
            Chunks of the answer
        """
        try:
            # Load conversation history if provided
            if conversation_history:
                self._load_conversation_history(session_id, conversation_history)
            
            # Get memory and prepare messages
            memory = self._get_memory(session_id)
            chat_history = memory.load_memory_variables({})['chat_history']
            
            # Build messages
            prompt = get_conversation_prompt()
            messages = prompt.format_messages(chat_history=chat_history, question=question)
            
            # Stream response
            full_response = ""
            for chunk in self.llm.stream(messages):
                content = chunk.content
                full_response += content
                yield content
            
            # Update memory
            memory.chat_memory.add_message(HumanMessage(content=question))
            memory.chat_memory.add_message(AIMessage(content=full_response))
        
        except Exception as e:
            error_msg = f"متأسفانه در پاسخ به سوال شما خطایی رخ داد: {str(e)}"
            yield error_msg
    
    def clear_session_memory(self, session_id: int):
        """Clear memory for a specific session"""
        if session_id in self.conversation_memory:
            del self.conversation_memory[session_id]
