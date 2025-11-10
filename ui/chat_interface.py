"""
Main chat interface component
"""
import streamlit as st
from sqlalchemy.orm import Session
from typing import Optional

from config.settings import settings
from core import MedicalChatbot
from db import (
    create_chat_session,
    get_session_by_id,
    get_session_messages,
    add_message
)


def initialize_chat_session(
    db: Session,
    chatbot: MedicalChatbot,
    user_id: int,
    condition_id: int,
    condition_name: str,
    data_file: str,
    session_id: Optional[int] = None
):
    """
    Initialize or load a chat session
    
    Args:
        db: Database session
        chatbot: Chatbot instance
        user_id: User ID
        condition_id: Condition ID
        condition_name: Condition name in Persian
        data_file: Path to condition data JSON
        session_id: Existing session ID (optional)
    
    Returns:
        Session ID
    """
    if session_id:
        # Load existing session
        session = get_session_by_id(db, session_id)
        if session:
            # Load messages from database
            messages = get_session_messages(db, session_id)
            
            # Initialize chat messages in Streamlit
            if 'messages' not in st.session_state or st.session_state.get('last_session_id') != session_id:
                st.session_state.messages = [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ]
                st.session_state.last_session_id = session_id
            
            return session_id
    
    # Create new session
    session = create_chat_session(db, user_id, condition_id)
    session_id = session.id
    
    # Generate initial educational content
    st.session_state.messages = []
    st.session_state.last_session_id = session_id
    st.session_state.generating_initial = True
    
    return session_id


def render_chat_interface(
    db: Session,
    chatbot: MedicalChatbot,
    user_id: int,
    condition_id: int,
    condition_name: str,
    data_file: str,
    session_id: Optional[int] = None
):
    """
    Render main chat interface
    
    Args:
        db: Database session
        chatbot: Chatbot instance
        user_id: User ID
        condition_id: Condition ID
        condition_name: Condition name in Persian
        data_file: Path to condition data JSON
        session_id: Existing session ID (optional)
    """
    # Initialize session
    current_session_id = initialize_chat_session(
        db, chatbot, user_id, condition_id, condition_name, data_file, session_id
    )
    
    # Update session state
    if not hasattr(st.session_state, 'current_session_id') or st.session_state.current_session_id != current_session_id:
        st.session_state.current_session_id = current_session_id
    
    # Chat header
    st.title(f"💬 {condition_name}")
    st.caption(f"گفتگو شماره: {current_session_id}")
    st.markdown("---")
    
    # Generate initial educational content if this is a new session
    if st.session_state.get('generating_initial', False):
        with st.spinner(settings.UI_TEXTS["loading"]):
            # Generate educational content with streaming
            response_placeholder = st.empty()
            full_response = ""
            
            for chunk in chatbot.generate_educational_content_stream(
                condition_name, data_file, current_session_id
            ):
                full_response += chunk
                response_placeholder.markdown(full_response)
            
            # Save to database
            add_message(db, current_session_id, "assistant", full_response)
            
            # Add to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })
            st.session_state.generating_initial = False
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input(settings.UI_TEXTS["input_placeholder"]):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Save user message to database
        add_message(db, current_session_id, "user", prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            # Get conversation history for context
            history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages[:-1]  # Exclude current user message
            ]
            
            try:
                # Stream response
                for chunk in chatbot.chat_stream(prompt, current_session_id, history):
                    full_response += chunk
                    response_placeholder.markdown(full_response)
                
                # Save assistant message to database
                add_message(db, current_session_id, "assistant", full_response)
                
                # Add to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })
            
            except Exception as e:
                error_msg = settings.UI_TEXTS["error_api"]
                response_placeholder.error(f"{error_msg}\n\nجزئیات: {str(e)}")


def apply_rtl_styling():
    """Apply RTL (right-to-left) styling for Persian language"""
    st.markdown("""
    <style>
    /* RTL support for Persian */
    .stChatMessage, .stMarkdown, .stTextInput, .stTextArea {
        direction: rtl;
        text-align: right;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        direction: rtl;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    
    /* Button styling */
    .stButton button {
        direction: rtl;
        text-align: center;
    }
    
    /* Better font for Persian */
    * {
        font-family: 'Vazirmatn', 'Tahoma', 'Arial', sans-serif;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    
    /* User message */
    [data-testid="stChatMessageContent"] {
        background-color: #e3f2fd;
    }
    
    /* Improve readability */
    p, div, span {
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)
