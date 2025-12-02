"""Practice session page - core game interface."""
import streamlit as st
from datetime import datetime, timedelta
import time
from src.models.session import SessionConfig, SessionState
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
            if st.button("← Back to Home"):
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
        # End session and save
        summary = st.session_state.session_manager.end_session(session)
        st.session_state.session_summary = summary
        st.session_state.active_session = None
        st.session_state.page = "results"
        st.rerun()
    
    # Top Bar
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        # Timer
        if session.config.mode_type == 'sprint':
            elapsed = (datetime.now() - session.start_time).total_seconds()
            remaining = int(session.config.duration_seconds - elapsed)
            if remaining <= 0:
                # Time's up!
                session.is_complete = True
                st.rerun()
            countdown_timer(remaining)
        else:
            elapsed = int((datetime.now() - session.start_time).total_seconds())
            minutes = elapsed // 60
            seconds = elapsed % 60
            st.metric("⏱️ Time", f"{minutes:02d}:{seconds:02d}")
    
    with col2:
        # Progress
        if session.config.mode_type == 'marathon' or session.config.mode_type == 'targeted':
            total = session.config.question_count
            current = len(session.questions_answered)
            st.metric("📝 Progress", f"{current}/{total}")
        else:
            st.metric("📝 Questions", len(session.questions_answered))
    
    with col3:
        # Score
        st.metric("🏆 Score", f"{session.total_score:,}")
    
    with col4:
        # Quit button
        if st.button("❌"):
            if st.session_state.get('confirm_quit', False):
                # Actually quit
                session.is_complete = True
                st.rerun()
            else:
                st.session_state.confirm_quit = True
                st.rerun()
    
    if st.session_state.get('confirm_quit', False):
        st.warning("⚠️ Click ❌ again to quit session")
    
    st.markdown("---")
    
    # Combo meter
    if session.combo_count > 0:
        combo_meter(session.combo_count)
    
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
                
                # Check if session should end
                if st.session_state.session_manager.check_session_end(session):
                    session.is_complete = True
                
                st.rerun()
        
        # Manual next button
        if st.button("➡️ Next Question", use_container_width=True):
            st.session_state.show_feedback = False
            st.session_state.last_result = None
            st.session_state.feedback_time = None
            
            # Check if session should end
            if st.session_state.session_manager.check_session_end(session):
                session.is_complete = True
            
            st.rerun()
    
    else:
        # Show current question
        if session.current_question:
            question_display(session.current_question)
            
            # Answer input
            with st.form(key="answer_form", clear_on_submit=True):
                answer = st.text_input(
                    "Your Answer:",
                    key="answer_input",
                    placeholder="Enter your answer...",
                    label_visibility="collapsed"
                )
                
                submitted = st.form_submit_button("✓ Submit Answer", use_container_width=True, type="primary")
                
                if submitted and answer:
                    # Process answer
                    result = st.session_state.session_manager.submit_answer(session, answer)
                    st.session_state.last_result = result
                    st.session_state.show_feedback = True
                    st.session_state.feedback_time = datetime.now()
                    st.session_state.confirm_quit = False
                    st.rerun()
    
    # Stats Sidebar
    with st.sidebar:
        st.subheader("📊 Session Stats")
        
        total_q = len(session.questions_answered)
        if total_q > 0:
            correct = sum(1 for r in session.questions_answered if r.is_correct)
            accuracy = correct / total_q * 100
            avg_time = sum(r.time_taken for r in session.questions_answered) / total_q
            
            st.metric("Accuracy", f"{accuracy:.1f}%")
            st.metric("Correct", f"{correct}/{total_q}")
            st.metric("Avg Time", f"{avg_time:.1f}s")
            st.metric("Combo", f"x{session.combo_count}")
        else:
            st.info("Answer questions to see stats")
