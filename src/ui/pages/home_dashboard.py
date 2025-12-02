"""Home dashboard page."""
import streamlit as st
from datetime import date, timedelta
from src.ui.components import stat_card, streak_flame
from src.analytics.performance_tracker import PerformanceTracker
from src.gamification.streak_tracker import StreakTracker


def show_home_dashboard(db_manager):
    """Display the home dashboard.
    
    Args:
        db_manager: Database manager instance
    """
    tracker = PerformanceTracker(db_manager)
    streak_tracker = StreakTracker(db_manager)
    
    # Header
    st.title("🧮 Mental Math Trainer")
    st.markdown(f"**{date.today().strftime('%A, %B %d, %Y')}**")
    
    st.markdown("---")
    
    # Yesterday's best session popup
    yesterday = date.today() - timedelta(days=1)
    recent_sessions = tracker.get_recent_sessions(limit=10)
    
    if not recent_sessions.empty:
        yesterday_sessions = recent_sessions[
            recent_sessions['timestamp'].str.startswith(str(yesterday))
        ]
        
        if not yesterday_sessions.empty:
            best_yesterday = yesterday_sessions.iloc[0]
            accuracy = best_yesterday['correct_answers'] / best_yesterday['total_questions'] * 100
            
            with st.expander("📊 Yesterday's Performance", expanded=False):
                st.info(f"""
                **Best Session:** {best_yesterday['correct_answers']}/{best_yesterday['total_questions']} 
                correct ({accuracy:.0f}%) • {best_yesterday['avg_time_per_question']:.1f}s avg time
                
                **Score:** {best_yesterday['total_score']:,} points
                """)
    
    # Quick Stats Row
    stats = tracker.get_overall_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        streak = streak_tracker.get_current_streak()
        stat_card("Current Streak", f"{streak} days", "🔥")
    
    with col2:
        stat_card("Total Questions", f"{stats['total_questions']:,}", "📝")
    
    with col3:
        accuracy = f"{stats['accuracy']:.1f}%" if stats['total_questions'] > 0 else "N/A"
        stat_card("Overall Accuracy", accuracy, "🎯")
    
    with col4:
        avg_time = f"{stats['avg_time']:.1f}s" if stats['total_questions'] > 0 else "N/A"
        stat_card("Avg Time", avg_time, "⏱️")
    
    st.markdown("---")
    
    # Start Practice Button (prominent)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎮 START PRACTICE", use_container_width=True, type="primary"):
            st.session_state.page = "mode_selection"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Mode Buttons
    st.subheader("Quick Start")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⚡ Sprint Mode\n2-minute challenge", use_container_width=True):
            st.session_state.quick_mode = {
                'mode_type': 'sprint',
                'category': 'mixed',
                'difficulty': 'medium',
                'duration_seconds': 120
            }
            st.session_state.page = "practice_session"
            st.rerun()
        
        if st.button("🎯 Targeted Practice\nFocus on weak areas", use_container_width=True):
            st.session_state.quick_mode = {
                'mode_type': 'targeted',
                'category': 'targeted',
                'difficulty': 'medium',
                'question_count': 25
            }
            st.session_state.page = "practice_session"
            st.rerun()
    
    with col2:
        if st.button("🏃 Marathon Mode\n50 questions", use_container_width=True):
            st.session_state.quick_mode = {
                'mode_type': 'marathon',
                'category': 'mixed',
                'difficulty': 'medium',
                'question_count': 50
            }
            st.session_state.page = "practice_session"
            st.rerun()
        
        if st.button("📊 View Analytics\nDetailed statistics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()
    
    st.markdown("---")
    
    # Recent Activity
    st.subheader("Recent Sessions")
    
    if recent_sessions.empty:
        st.info("👋 No sessions yet. Start practicing to see your progress!")
    else:
        # Show last 5 sessions
        display_sessions = recent_sessions.head(5)
        
        for _, session in display_sessions.iterrows():
            accuracy = session['correct_answers'] / session['total_questions'] * 100
            
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                timestamp = session['timestamp'][:10] if isinstance(session['timestamp'], str) else str(session['timestamp'])[:10]
                st.write(f"**{timestamp}** • {session['mode_type'].title()}")
            
            with col2:
                st.write(f"{session['category'].title()}")
            
            with col3:
                st.write(f"{session['correct_answers']}/{session['total_questions']}")
            
            with col4:
                color = "green" if accuracy >= 80 else "orange" if accuracy >= 60 else "red"
                st.markdown(f":{color}[{accuracy:.0f}%]")
            
            with col5:
                st.write(f"{session['total_score']:,} pts")
