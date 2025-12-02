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
        if st.button("← Back to Home"):
            st.session_state.page = "home"
            st.rerun()
        return
    
    summary = st.session_state.session_summary
    
    # Initialize managers
    insights_gen = InsightsGenerator(db_manager)
    badge_mgr = BadgeManager(db_manager)
    streak_tracker = StreakTracker(db_manager)
    
    # Header
    celebration_header("🎯 SESSION COMPLETE!")
    
    st.markdown("---")
    
    # Main Stats
    st.subheader("📈 Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    accuracy = summary.correct_answers / summary.total_questions * 100
    
    with col1:
        stat_card("Final Score", f"{summary.total_score:,}", "🏆")
    
    with col2:
        stat_card("Accuracy", f"{accuracy:.1f}%", "🎯")
    
    with col3:
        stat_card("Questions", f"{summary.correct_answers}/{summary.total_questions}", "📝")
    
    with col4:
        stat_card("Avg Time", f"{summary.avg_time_per_question:.1f}s", "⏱️")
    
    st.markdown("---")
    
    # Insights Section
    st.subheader("💡 Insights")
    
    insights = insights_gen.generate_session_insights(summary)
    
    for insight in insights:
        insight_card(insight['text'], insight['type'])
    
    st.markdown("---")
    
    # Check for new badges
    newly_earned = badge_mgr.check_earned_badges(summary)
    
    if newly_earned:
        st.subheader("🎉 New Badges Earned!")
        
        cols = st.columns(min(len(newly_earned), 4))
        for i, badge in enumerate(newly_earned):
            with cols[i % 4]:
                badge_display(badge, earned=True)
        
        st.balloons()
        st.markdown("---")
    
    # Streak Update
    st.subheader("🔥 Streak Status")
    
    current_streak = streak_tracker.get_current_streak()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if current_streak > 0:
            streak_flame(current_streak)
        else:
            st.info("Start a streak by practicing daily!")
    
    st.markdown("---")
    
    # Performance Breakdown
    with st.expander("📊 Detailed Breakdown", expanded=False):
        # Group results by question type
        by_type = {}
        for result in summary.results:
            q_type = result.question.question_type
            if q_type not in by_type:
                by_type[q_type] = {
                    'total': 0,
                    'correct': 0,
                    'total_time': 0
                }
            
            by_type[q_type]['total'] += 1
            if result.is_correct:
                by_type[q_type]['correct'] += 1
            by_type[q_type]['total_time'] += result.time_taken
        
        # Display breakdown
        for q_type, stats in by_type.items():
            accuracy = stats['correct'] / stats['total'] * 100
            avg_time = stats['total_time'] / stats['total']
            
            st.write(f"**{q_type.title()}**: {stats['correct']}/{stats['total']} "
                    f"({accuracy:.0f}%) • {avg_time:.1f}s avg")
    
    st.markdown("---")
    
    # Action Buttons
    st.subheader("What's Next?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Practice Again\nSame settings", use_container_width=True):
            # Restart with same config
            config_dict = {
                'mode_type': summary.config.mode_type,
                'category': summary.config.category,
                'difficulty': summary.config.difficulty,
                'duration_seconds': summary.config.duration_seconds,
                'question_count': summary.config.question_count
            }
            st.session_state.session_config = config_dict
            st.session_state.page = "practice_session"
            st.session_state.active_session = None
            st.rerun()
        
        if st.button("📊 View Analytics\nDetailed stats", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()
    
    with col2:
        if st.button("⚙️ Change Mode\nNew configuration", use_container_width=True):
            st.session_state.page = "mode_selection"
            st.rerun()
        
        if st.button("🏠 Back to Home\nMain dashboard", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
