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
    st.title("📊 Analytics")
    
    if st.button("← Home"):
        st.session_state.page = "home"
        st.rerun()
    
    # Initialize tracker
    tracker = PerformanceTracker(db_manager)
    badge_mgr = BadgeManager(db_manager)
    
    # Time Range Selector - compact
    time_range = st.selectbox(
        "Period:",
        ["7 Days", "30 Days", "All Time"],
        index=1,
        label_visibility="collapsed"
    )
    
    days = {"7 Days": 7, "30 Days": 30, "All Time": 36500}[time_range]
    
    st.markdown("---")
    
    # Key Metrics - 2x2 grid
    st.subheader("📈 Stats")
    
    stats = tracker.get_overall_stats()
    
    col1, col2 = st.columns(2)
    
    with col1:
        stat_card("Questions", f"{stats['total_questions']:,}", "📝")
    
    with col2:
        accuracy = f"{stats['accuracy']:.0f}%" if stats['total_questions'] > 0 else "N/A"
        stat_card("Accuracy", accuracy, "🎯")
    
    col3, col4 = st.columns(2)
    
    with col3:
        avg_time = f"{stats['avg_time']:.1f}s" if stats['total_questions'] > 0 else "N/A"
        stat_card("Avg Time", avg_time, "⏱️")
    
    with col4:
        stat_card("Streak", f"{stats['current_streak']}d", "🔥")
    
    st.markdown("---")
    
    # Performance Trends - tabs for mobile
    st.subheader("📉 Trends")
    
    trend_data = tracker.get_historical_trend(days=days)
    
    if not trend_data.empty:
        tab1, tab2 = st.tabs(["Accuracy", "Speed"])
        
        with tab1:
            fig_accuracy = create_accuracy_trend_chart(trend_data)
            st.plotly_chart(fig_accuracy, use_container_width=True, config={'displayModeBar': False})
        
        with tab2:
            fig_speed = create_speed_trend_chart(trend_data)
            st.plotly_chart(fig_speed, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("📊 Start practicing to see trends!")
    
    st.markdown("---")
    
    # Category Breakdown
    st.subheader("🎯 By Category")
    
    category_data = tracker.get_stats_by_category()
    
    if not category_data.empty:
        tab1, tab2 = st.tabs(["Chart", "Radar"])
        
        with tab1:
            fig_bars = create_category_breakdown_chart(category_data)
            st.plotly_chart(fig_bars, use_container_width=True, config={'displayModeBar': False})
        
        with tab2:
            fig_radar = create_category_radar_chart(category_data)
            st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        
        with st.expander("📋 Data"):
            st.dataframe(category_data, use_container_width=True, hide_index=True)
    else:
        st.info("📊 No category data yet.")
    
    st.markdown("---")
    
    # Weak Areas - compact
    st.subheader("🎯 Improve")
    
    weak_areas = tracker.identify_weak_areas(threshold=0.75)
    slow_areas = tracker.identify_slow_areas(threshold=5.0)
    
    if weak_areas or slow_areas:
        if weak_areas:
            st.write("**Low Accuracy (<75%):**")
            for area in weak_areas:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {area.title()}")
                with col2:
                    if st.button("Go", key=f"p_{area}"):
                        st.session_state.session_config = {
                            'mode_type': 'targeted',
                            'category': area,
                            'difficulty': 'medium',
                            'question_count': 25
                        }
                        st.session_state.page = "practice_session"
                        st.rerun()
        
        if slow_areas:
            st.write("**Slow (>5s):**")
            for area in slow_areas:
                st.write(f"• {area.title()}")
    else:
        st.success("🎉 No weak areas!")
    
    st.markdown("---")
    
    # Achievements - compact display
    st.subheader("🏆 Badges")
    
    all_badges = badge_mgr.get_all_badges()
    earned_badges = [b for b in all_badges if b.earned]
    locked_badges = [b for b in all_badges if not b.earned]
    
    st.write(f"**Earned ({len(earned_badges)}/{len(all_badges)}):**")
    
    if earned_badges:
        # 3 badges per row max on mobile
        for i in range(0, len(earned_badges), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(earned_badges):
                    with col:
                        badge_display(earned_badges[i + j], earned=True)
    else:
        st.info("Complete sessions to earn badges!")
    
    # Locked badges
    with st.expander("🔒 Locked"):
        progress_data = badge_mgr.get_progress_to_badges()
        
        if progress_data:
            for badge_name, info in list(progress_data.items())[:5]:
                badge = info['badge']
                st.write(f"**{badge.icon} {badge.badge_name}**")
                if info['description']:
                    st.progress(
                        min(info['progress'] / info['target'], 1.0),
                        text=info['description']
                    )
        else:
            for i in range(0, min(len(locked_badges), 6), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(locked_badges):
                        with col:
                            badge_display(locked_badges[i + j], earned=False)
    
    st.markdown("---")
    
    # Session History - compact
    st.subheader("📜 History")
    
    history = tracker.get_recent_sessions(limit=20)
    
    if not history.empty:
        history['accuracy_pct'] = (
            history['correct_answers'] / history['total_questions'] * 100
        ).round(0)
        
        # Simplified columns for mobile
        display_columns = ['timestamp', 'mode_type', 'accuracy_pct', 'total_score']
        display_history = history[display_columns].copy()
        display_history.columns = ['Date', 'Mode', 'Acc%', 'Score']
        display_history['Date'] = display_history['Date'].str[:10]
        display_history['Mode'] = display_history['Mode'].str[:3].str.title()
        
        st.dataframe(display_history, use_container_width=True, hide_index=True)
    else:
        st.info("No history yet.")
