"""
EHR Medical Chatbot - Main Application Entry Point

A production-ready medical educational chatbot for Persian-speaking users
Built with LangChain, OpenAI GPT-4o-mini, and Streamlit
"""
import streamlit as st
from sqlalchemy.orm import Session

from config.settings import settings
from db import init_db, get_db, get_or_create_user, create_condition, get_user_conditions
from core import MedicalChatbot
from ui import render_chat_interface, render_sidebar
from ui.chat_interface import apply_rtl_styling
from ui.sidebar import render_condition_selector
from mock_data.backend import get_user_by_id, get_user_conditions as fetch_user_conditions


def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title=settings.UI_TEXTS["app_title"],
        page_icon="🩺",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply RTL styling
    apply_rtl_styling()


def initialize_user(db: Session, user_id: int):
    """
    Initialize user and their conditions in the database
    
    Args:
        db: Database session
        user_id: User ID from EHR system
    """
    # Fetch user data from mock backend
    user_data = get_user_by_id(user_id)
    
    if not user_data:
        st.error("کاربر یافت نشد. لطفاً شناسه کاربری صحیح را وارد کنید.")
        st.stop()
    
    # Get or create user in local database
    user = get_or_create_user(db, user_id, user_data["name"])
    
    # Fetch and sync user's conditions
    conditions_data = fetch_user_conditions(user_id)
    existing_conditions = get_user_conditions(db, user_id)
    
    # Add conditions that don't exist in local database
    existing_names = {cond.name_en for cond in existing_conditions}
    
    for condition_data in conditions_data:
        if condition_data["name_en"] not in existing_names:
            create_condition(
                db,
                user_id,
                condition_data["name"],
                condition_data["name_en"],
                condition_data["data_file"]
            )
    
    return user


def main():
    """Main application entry point"""
    # Setup page
    setup_page_config()
    
    # Validate settings
    try:
        settings.validate()
    except ValueError as e:
        st.error(f"خطای پیکربندی: {str(e)}")
        st.info("لطفاً فایل .env را با کلید API خود ایجاد کنید. از .env.example به عنوان الگو استفاده کنید.")
        st.code("""
# نمونه فایل .env
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./ehr_chatbot.db
        """)
        st.stop()
    
    # Initialize database
    init_db()
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = MedicalChatbot()
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Mock user login - in production, this would come from authentication
        # For demo purposes, we'll use a simple user ID selector
        if 'user_id' not in st.session_state:
            st.title(settings.UI_TEXTS["app_title"])
            st.markdown("---")
            
            st.subheader("ورود به سیستم")
            st.write("برای تست، یک کاربر را انتخاب کنید:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("علی احمدی (دیابت + فشار خون)", use_container_width=True):
                    st.session_state.user_id = 1234567890123
                    st.rerun()
            
            with col2:
                if st.button("فاطمه محمدی (فشار خون)", use_container_width=True):
                    st.session_state.user_id = 9876543210987
                    st.rerun()
            
            with col3:
                if st.button("حسین رضایی (آسم)", use_container_width=True):
                    st.session_state.user_id = 1111222233334
                    st.rerun()
            
            st.markdown("---")
            st.caption("در نسخه واقعی، احراز هویت از طریق سیستم EHR انجام می‌شود.")
            return
        
        # Initialize user
        user_id = st.session_state.user_id
        user = initialize_user(db, user_id)
        
        # Get user's conditions
        conditions = get_user_conditions(db, user_id)
        
        if not conditions:
            st.warning(settings.UI_TEXTS["no_conditions"])
            return
        
        # Render sidebar
        render_sidebar(db, user_id)
        
        # Main content area
        if not hasattr(st.session_state, 'selected_condition_id'):
            # Show condition selector
            st.title(settings.UI_TEXTS["app_title"])
            st.markdown("---")
            
            st.header(settings.UI_TEXTS["select_condition"])
            st.write("لطفاً یکی از بیماری‌های خود را از منوی سمت راست انتخاب کنید.")
            
            # Display available conditions
            st.subheader("بیماری‌های ثبت شده:")
            for condition in conditions:
                st.info(f"🩺 {condition.name}")
        
        else:
            # Render chat interface for selected condition
            render_chat_interface(
                db,
                st.session_state.chatbot,
                user_id,
                st.session_state.selected_condition_id,
                st.session_state.selected_condition_name,
                st.session_state.selected_condition_data_file,
                st.session_state.get('current_session_id')
            )
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
