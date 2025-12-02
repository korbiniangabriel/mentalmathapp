"""Analytics dashboard page."""
import streamlit as st
from src.analytics.performance_tracker import PerformanceTracker
from src.analytics.visualizations import (
    create_accuracy_trend_chart,
    create_speed_trend_chart,
    create_category_breakdown_chart,
    create_category_radar_chart
)
from src.gamification.badge_manager import BadgeManager
from src.ui.components import stat_card, badge_display


def show_analytics_dashboard(db_manager):
    """Display analytics dashboard.
    
    Args:
        db_manager: Database manager instance
    """
    st.title("📊 Analytics Dashboard")
    
    if st.button("← Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("---")
    
    # Initialize tracker
    tracker = PerformanceTracker(db_manager)
    badge_mgr = BadgeManager(db_manager)
    
    # Time Range Selector
    time_range = st.selectbox(
        "Time Range:",
        ["Last 7 Days", "Last 30 Days", "All Time"],
        index=1
    )
    
    days = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "All Time": 36500  # 100 years, effectively all time
    }[time_range]
    
    st.markdown("---")
    
    # Key Metrics Row
    st.subheader("📈 Key Metrics")
    
    stats = tracker.get_overall_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        stat_card("Total Questions", f"{stats['total_questions']:,}", "📝")
    
    with col2:
        accuracy = f"{stats['accuracy']:.1f}%" if stats['total_questions'] > 0 else "N/A"
        stat_card("Overall Accuracy", accuracy, "🎯")
    
    with col3:
        avg_time = f"{stats['avg_time']:.1f}s" if stats['total_questions'] > 0 else "N/A"
        stat_card("Avg Time", avg_time, "⏱️")
    
    with col4:
        stat_card("Current Streak", f"{stats['current_streak']} days", "🔥")
    
    st.markdown("---")
    
    # Performance Trends
    st.subheader("📉 Performance Trends")
    
    trend_data = tracker.get_historical_trend(days=days)
    
    if not trend_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_accuracy = create_accuracy_trend_chart(trend_data)
            st.plotly_chart(fig_accuracy, use_container_width=True)
        
        with col2:
            fig_speed = create_speed_trend_chart(trend_data)
            st.plotly_chart(fig_speed, use_container_width=True)
    else:
        st.info("📊 Start practicing to see your performance trends!")
    
    st.markdown("---")
    
    # Category Breakdown
    st.subheader("🎯 Performance by Category")
    
    category_data = tracker.get_stats_by_category()
    
    if not category_data.empty:
        # Show both chart types
        tab1, tab2 = st.tabs(["Bar Chart", "Radar Chart"])
        
        with tab1:
            fig_bars = create_category_breakdown_chart(category_data)
            st.plotly_chart(fig_bars, use_container_width=True)
        
        with tab2:
            fig_radar = create_category_radar_chart(category_data)
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Data table
        with st.expander("📋 View Data Table"):
            st.dataframe(
                category_data,
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("📊 No category data yet. Complete some sessions!")
    
    st.markdown("---")
    
    # Weak Areas
    st.subheader("🎯 Areas for Improvement")
    
    weak_areas = tracker.identify_weak_areas(threshold=0.75)
    slow_areas = tracker.identify_slow_areas(threshold=5.0)
    
    if weak_areas or slow_areas:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Low Accuracy (<75%):**")
            if weak_areas:
                for area in weak_areas:
                    st.write(f"• {area.title()}")
                    if st.button(f"Practice {area.title()}", key=f"practice_{area}"):
                        config_dict = {
                            'mode_type': 'targeted',
                            'category': area,
                            'difficulty': 'medium',
                            'question_count': 25
                        }
                        st.session_state.session_config = config_dict
                        st.session_state.page = "practice_session"
                        st.rerun()
            else:
                st.success("✓ All areas above 75%!")
        
        with col2:
            st.write("**Slow Response (>5s avg):**")
            if slow_areas:
                for area in slow_areas:
                    st.write(f"• {area.title()}")
            else:
                st.success("✓ All areas under 5s!")
    else:
        st.success("🎉 No weak areas identified. Great job!")
    
    st.markdown("---")
    
    # Achievements Section
    st.subheader("🏆 Achievements")
    
    all_badges = badge_mgr.get_all_badges()
    earned_badges = [b for b in all_badges if b.earned]
    locked_badges = [b for b in all_badges if not b.earned]
    
    # Earned badges
    st.write(f"**Earned Badges ({len(earned_badges)}/{len(all_badges)}):**")
    
    if earned_badges:
        cols = st.columns(min(len(earned_badges), 5))
        for i, badge in enumerate(earned_badges):
            with cols[i % 5]:
                badge_display(badge, earned=True)
    else:
        st.info("Complete sessions to earn badges!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Locked badges (in progress)
    with st.expander("🔒 Locked Badges", expanded=False):
        progress_data = badge_mgr.get_progress_to_badges()
        
        if progress_data:
            for badge_name, info in list(progress_data.items())[:5]:
                badge = info['badge']
                st.write(f"**{badge.icon} {badge.badge_name}**")
                st.write(f"_{badge.description}_")
                if info['description']:
                    st.progress(
                        min(info['progress'] / info['target'], 1.0),
                        text=info['description']
                    )
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            cols = st.columns(min(len(locked_badges), 5))
            for i, badge in enumerate(locked_badges[:10]):
                with cols[i % 5]:
                    badge_display(badge, earned=False)
    
    st.markdown("---")
    
    # Session History
    st.subheader("📜 Session History")
    
    history = tracker.get_recent_sessions(limit=20)
    
    if not history.empty:
        # Add calculated columns
        history['accuracy_pct'] = (
            history['correct_answers'] / history['total_questions'] * 100
        ).round(1)
        
        # Display table
        display_columns = [
            'timestamp', 'mode_type', 'category', 'difficulty',
            'total_questions', 'correct_answers', 'accuracy_pct',
            'total_score', 'avg_time_per_question'
        ]
        
        display_history = history[display_columns].copy()
        display_history.columns = [
            'Date/Time', 'Mode', 'Category', 'Difficulty',
            'Questions', 'Correct', 'Accuracy %',
            'Score', 'Avg Time'
        ]
        
        st.dataframe(
            display_history,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No session history yet. Start practicing!")
