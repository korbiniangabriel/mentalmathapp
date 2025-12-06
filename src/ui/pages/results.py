"""Results page - session summary and insights."""
import streamlit as st
from src.ui.components import (
    celebration_header, stat_card, insight_card, 
    badge_display, streak_flame
)
from src.analytics.insights_generator import InsightsGenerator
from src.gamification.badge_manager import BadgeManager
from src.gamification.streak_tracker import StreakTracker


def show_results(db_manager):
    """Display results page.
    
    Args:
        db_manager: Database manager instance
    """
    if 'session_summary' not in st.session_state:
        st.error("No session summary found")
        if st.button("← Home"):
            st.session_state.page = "home"
            st.rerun()
        return
    
    summary = st.session_state.session_summary
    
    # Initialize managers
    insights_gen = InsightsGenerator(db_manager)
    badge_mgr = BadgeManager(db_manager)
    streak_tracker = StreakTracker(db_manager)
    
    # Header
    celebration_header("🎯 COMPLETE!")
    
    st.markdown("---")
    
    # Main Stats - 2x2 grid
    accuracy = summary.correct_answers / summary.total_questions * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        stat_card("Score", f"{summary.total_score:,}", "🏆")
    
    with col2:
        stat_card("Accuracy", f"{accuracy:.0f}%", "🎯")
    
    col3, col4 = st.columns(2)
    
    with col3:
        stat_card("Correct", f"{summary.correct_answers}/{summary.total_questions}", "📝")
    
    with col4:
        stat_card("Avg Time", f"{summary.avg_time_per_question:.1f}s", "⏱️")
    
    st.markdown("---")
    
    # Insights - compact
    st.subheader("💡 Insights")
    
    insights = insights_gen.generate_session_insights(summary)
    
    for insight in insights:
        insight_card(insight['text'], insight['type'])
    
    # Check for new badges
    newly_earned = badge_mgr.check_earned_badges(summary)
    
    if newly_earned:
        st.markdown("---")
        st.subheader("🎉 New Badges!")
        
        # 3 per row max
        for i in range(0, len(newly_earned), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(newly_earned):
                    with col:
                        badge_display(newly_earned[i + j], earned=True)
        
        st.balloons()
    
    st.markdown("---")
    
    # Streak - compact
    st.subheader("🔥 Streak")
    
    current_streak = streak_tracker.get_current_streak()
    
    if current_streak > 0:
        streak_flame(current_streak)
    else:
        st.info("Start a streak by practicing daily!")
    
    # Performance Breakdown - compact
    with st.expander("📊 Breakdown"):
        by_type = {}
        for result in summary.results:
            q_type = result.question.question_type
            if q_type not in by_type:
                by_type[q_type] = {'total': 0, 'correct': 0, 'total_time': 0}
            
            by_type[q_type]['total'] += 1
            if result.is_correct:
                by_type[q_type]['correct'] += 1
            by_type[q_type]['total_time'] += result.time_taken
        
        for q_type, stats in by_type.items():
            acc = stats['correct'] / stats['total'] * 100
            avg = stats['total_time'] / stats['total']
            st.write(f"**{q_type.title()}**: {stats['correct']}/{stats['total']} ({acc:.0f}%) • {avg:.1f}s")
    
    st.markdown("---")
    
    # Action Buttons - 2 column grid
    st.subheader("Next?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Again", use_container_width=True):
            st.session_state.session_config = {
                'mode_type': summary.config.mode_type,
                'category': summary.config.category,
                'difficulty': summary.config.difficulty,
                'duration_seconds': summary.config.duration_seconds,
                'question_count': summary.config.question_count
            }
            st.session_state.page = "practice_session"
            st.session_state.active_session = None
            st.rerun()
    
    with col2:
        if st.button("⚙️ New Mode", use_container_width=True):
            st.session_state.page = "mode_selection"
            st.rerun()
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()
    
    with col4:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
