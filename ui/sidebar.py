"""
Sidebar component for displaying conditions and chat history
"""
import streamlit as st
from typing import List, Dict
from sqlalchemy.orm import Session

from config.settings import settings
from db import get_user_conditions, get_user_sessions


def render_sidebar(db: Session, user_id: int):
    """
    Render sidebar with user's conditions and chat history
    
    Args:
        db: Database session
        user_id: Current user's ID
    """
    with st.sidebar:
        st.title(settings.UI_TEXTS["sidebar_title"])
        
        # Get user's conditions
        conditions = get_user_conditions(db, user_id)
        
        if not conditions:
            st.info(settings.UI_TEXTS["no_conditions"])
            return
        
        # Display conditions as buttons
        st.subheader("انتخاب بیماری")
        for condition in conditions:
            if st.button(
                condition.name,
                key=f"condition_{condition.id}",
                use_container_width=True
            ):
                # Set selected condition
                st.session_state.selected_condition_id = condition.id
                st.session_state.selected_condition_name = condition.name
                st.session_state.selected_condition_data_file = condition.data_file
                st.session_state.current_session_id = None  # Start new session
                st.rerun()
        
        # Display chat history for selected condition
        if hasattr(st.session_state, 'selected_condition_id'):
            st.divider()
            st.subheader(settings.UI_TEXTS["chat_history_title"])
            
            # New chat button
            if st.button(
                settings.UI_TEXTS["new_chat"],
                use_container_width=True,
                type="primary"
            ):
                st.session_state.current_session_id = None
                st.rerun()
            
            # Get sessions for selected condition
            sessions = get_user_sessions(
                db,
                user_id,
                condition_id=st.session_state.selected_condition_id
            )
            
            if sessions:
                st.caption(f"تعداد: {len(sessions)} گفتگو")
                
                for session in sessions[:10]:  # Show last 10 sessions
                    session_title = session.title or f"گفتگو #{session.id}"
                    
                    # Highlight current session
                    if (hasattr(st.session_state, 'current_session_id') and 
                        st.session_state.current_session_id == session.id):
                        st.markdown(f"**🔹 {session_title}**")
                    else:
                        if st.button(
                            session_title,
                            key=f"session_{session.id}",
                            use_container_width=True
                        ):
                            st.session_state.current_session_id = session.id
                            st.rerun()
            else:
                st.caption("هنوز گفتگویی ثبت نشده است")


def render_condition_selector(conditions: List[Dict]):
    """
    Render initial condition selector when no condition is selected
    
    Args:
        conditions: List of user's conditions
    """
    st.title(settings.UI_TEXTS["app_title"])
    st.markdown("---")
    
    st.header(settings.UI_TEXTS["select_condition"])
    st.write("لطفاً یکی از بیماری‌های خود را انتخاب کنید تا گفتگو را شروع کنیم:")
    
    # Display condition cards
    cols = st.columns(2)
    for idx, condition in enumerate(conditions):
        with cols[idx % 2]:
            if st.button(
                f"🩺 {condition['name']}",
                key=f"select_{condition['name_en']}",
                use_container_width=True,
                help=f"کلیک کنید تا درباره {condition['name']} بیشتر بدانید"
            ):
                return condition
    
    return None
