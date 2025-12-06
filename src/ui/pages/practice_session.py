"""Practice session page - core game interface."""
import streamlit as st
from datetime import datetime
from src.models.session import SessionConfig
from src.game_logic.session_manager import SessionManager
from src.ui.components import (
    question_display, combo_meter, feedback_display,
    countdown_timer, progress_bar_with_label
)


def show_practice_session(db_manager):
    """Display practice session page.
    
    Args:
        db_manager: Database manager instance
    """
    # Initialize session manager
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager(db_manager)
    
    # Initialize or get session state
    if 'active_session' not in st.session_state or st.session_state.active_session is None:
        # Get config from either mode selection or quick mode
        if 'session_config' in st.session_state:
            config_dict = st.session_state.session_config
        elif 'quick_mode' in st.session_state:
            config_dict = st.session_state.quick_mode
        else:
            st.error("No session configuration found")
            if st.button("← Home"):
                st.session_state.page = "home"
                st.rerun()
            return
        
        # Create SessionConfig object
        config = SessionConfig(
            mode_type=config_dict['mode_type'],
            category=config_dict['category'],
            difficulty=config_dict['difficulty'],
            duration_seconds=config_dict.get('duration_seconds'),
            question_count=config_dict.get('question_count')
        )
        
        # Start session
        st.session_state.active_session = st.session_state.session_manager.start_session(config)
        st.session_state.last_result = None
        st.session_state.show_feedback = False
        st.session_state.feedback_time = None
    
    session = st.session_state.active_session
    
    # Check if session is complete
    if session.is_complete:
        summary = st.session_state.session_manager.end_session(session)
        st.session_state.session_summary = summary
        st.session_state.active_session = None
        st.session_state.page = "results"
        st.rerun()
    
    # Top Bar - simplified 3 columns for mobile
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if session.config.mode_type == 'sprint':
            elapsed = (datetime.now() - session.start_time).total_seconds()
            remaining = int(session.config.duration_seconds - elapsed)
            if remaining <= 0:
                session.is_complete = True
                st.rerun()
            countdown_timer(remaining)
        else:
            elapsed = int((datetime.now() - session.start_time).total_seconds())
            st.metric("⏱️", f"{elapsed//60}:{elapsed%60:02d}")
    
    with col2:
        if session.config.mode_type in ['marathon', 'targeted']:
            total = session.config.question_count
            current = len(session.questions_answered)
            st.metric("📝", f"{current}/{total}")
        else:
            st.metric("📝", len(session.questions_answered))
    
    with col3:
        if st.button("❌", help="Quit"):
            if st.session_state.get('confirm_quit', False):
                session.is_complete = True
                st.rerun()
            else:
                st.session_state.confirm_quit = True
                st.rerun()
    
    # Score display - compact
    st.markdown(f"**🏆 {session.total_score:,}**")
    
    if st.session_state.get('confirm_quit', False):
        st.warning("⚠️ Click ❌ again to quit")
    
    # Combo meter
    if session.combo_count > 0:
        combo_meter(session.combo_count)
    
    st.markdown("---")
    
    # Show feedback if available
    if st.session_state.show_feedback and st.session_state.last_result:
        result = st.session_state.last_result
        feedback_display(
            result.is_correct,
            result.question.correct_answer,
            result.time_taken
        )
        
        # Auto-advance after 1.5 seconds
        if st.session_state.feedback_time:
            elapsed = (datetime.now() - st.session_state.feedback_time).total_seconds()
            if elapsed >= 1.5:
                st.session_state.show_feedback = False
                st.session_state.last_result = None
                st.session_state.feedback_time = None
                
                if st.session_state.session_manager.check_session_end(session):
                    session.is_complete = True
                
                st.rerun()
        
        # Manual next button
        if st.button("➡️ Next", use_container_width=True):
            st.session_state.show_feedback = False
            st.session_state.last_result = None
            st.session_state.feedback_time = None
            
            if st.session_state.session_manager.check_session_end(session):
                session.is_complete = True
            
            st.rerun()
    
    else:
        # Show current question
        if session.current_question:
            question_display(session.current_question)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Answer input - optimized for mobile
            with st.form(key="answer_form", clear_on_submit=True):
                answer = st.text_input(
                    "Answer:",
                    key="answer_input",
                    placeholder="Enter answer...",
                    label_visibility="collapsed",
                    help="Tap here to enter your answer"
                )
                
                # Submit button with better mobile touch target
                submitted = st.form_submit_button("✓ Submit", use_container_width=True, type="primary")
                
                if submitted and answer:
                    result = st.session_state.session_manager.submit_answer(session, answer)
                    st.session_state.last_result = result
                    st.session_state.show_feedback = True
                    st.session_state.feedback_time = datetime.now()
                    st.session_state.confirm_quit = False
                    st.rerun()
    
    # Stats in expander instead of sidebar (better for mobile)
    with st.expander("📊 Stats"):
        total_q = len(session.questions_answered)
        if total_q > 0:
            correct = sum(1 for r in session.questions_answered if r.is_correct)
            accuracy = correct / total_q * 100
            avg_time = sum(r.time_taken for r in session.questions_answered) / total_q
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Accuracy", f"{accuracy:.0f}%")
                st.metric("Correct", f"{correct}/{total_q}")
            with col2:
                st.metric("Avg Time", f"{avg_time:.1f}s")
                st.metric("Combo", f"x{session.combo_count}")
        else:
            st.info("Answer questions to see stats")
