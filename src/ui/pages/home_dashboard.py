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
    
    # Header - compact for mobile
    st.title("🧮 Mental Math")
    st.caption(date.today().strftime('%a, %b %d'))
    
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
            
            with st.expander("📊 Yesterday", expanded=False):
                st.write(f"**{best_yesterday['correct_answers']}/{best_yesterday['total_questions']}** ({accuracy:.0f}%) • {best_yesterday['avg_time_per_question']:.1f}s avg • {best_yesterday['total_score']:,} pts")
    
    # Quick Stats Row - 2x2 grid
    stats = tracker.get_overall_stats()
    
    col1, col2 = st.columns(2)
    
    with col1:
        streak = streak_tracker.get_current_streak()
        stat_card("Streak", f"{streak}d", "🔥")
    
    with col2:
        stat_card("Questions", f"{stats['total_questions']:,}", "📝")
    
    col3, col4 = st.columns(2)
    
    with col3:
        accuracy = f"{stats['accuracy']:.0f}%" if stats['total_questions'] > 0 else "N/A"
        stat_card("Accuracy", accuracy, "🎯")
    
    with col4:
        avg_time = f"{stats['avg_time']:.1f}s" if stats['total_questions'] > 0 else "N/A"
        stat_card("Avg Time", avg_time, "⏱️")
    
    st.markdown("---")
    
    # Start Practice Button
    if st.button("🎮 START PRACTICE", use_container_width=True, type="primary"):
        st.session_state.page = "mode_selection"
        st.rerun()
    
    st.markdown("---")
    
    # Quick Mode Buttons - stacked for mobile
    st.subheader("⚡ Quick Start")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⚡ Sprint (2m)", use_container_width=True):
            st.session_state.quick_mode = {
                'mode_type': 'sprint',
                'category': 'mixed',
                'difficulty': 'medium',
                'duration_seconds': 120
            }
            st.session_state.page = "practice_session"
            st.rerun()
    
    with col2:
        if st.button("🏃 Marathon (50)", use_container_width=True):
            st.session_state.quick_mode = {
                'mode_type': 'marathon',
                'category': 'mixed',
                'difficulty': 'medium',
                'question_count': 50
            }
            st.session_state.page = "practice_session"
            st.rerun()
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("🎯 Targeted", use_container_width=True):
            st.session_state.quick_mode = {
                'mode_type': 'targeted',
                'category': 'targeted',
                'difficulty': 'medium',
                'question_count': 25
            }
            st.session_state.page = "practice_session"
            st.rerun()
    
    with col4:
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()
    
    st.markdown("---")
    
    # Recent Activity - compact
    st.subheader("📜 Recent")
    
    if recent_sessions.empty:
        st.info("👋 No sessions yet. Start practicing!")
    else:
        display_sessions = recent_sessions.head(5)
        
        for _, session in display_sessions.iterrows():
            accuracy = session['correct_answers'] / session['total_questions'] * 100
            timestamp = session['timestamp'][:10] if isinstance(session['timestamp'], str) else str(session['timestamp'])[:10]
            
            # Single line compact view
            color = "green" if accuracy >= 80 else "orange" if accuracy >= 60 else "red"
            mode_short = session['mode_type'][:3].title()
            
            st.markdown(f"**{timestamp}** • {mode_short} • :{color}[{accuracy:.0f}%] • {session['total_score']:,}pts")
