"""Analytics dashboard page."""

from __future__ import annotations

import streamlit as st

from src.analytics.performance_tracker import GoalSettings, PerformanceTracker
from src.analytics.visualizations import (
    create_accuracy_trend_chart,
    create_category_breakdown_chart,
    create_category_radar_chart,
    create_heatmap_chart,
    create_progress_gauge,
    create_question_volume_chart,
    create_speed_trend_chart,
    create_weekly_consistency_chart,
)
from src.gamification.badge_manager import BadgeManager
from src.ui.components import badge_display, coach_note, hero_panel, stat_card


def show_analytics_dashboard(db_manager):
    """Display analytics dashboard."""
    tracker = PerformanceTracker(db_manager)
    badge_mgr = BadgeManager(db_manager)

    days_lookup = {"7 Days": 7, "30 Days": 30, "90 Days": 90, "All Time": 36500}
    selected_range = st.selectbox("Time range", list(days_lookup.keys()), index=1)
    days = days_lookup[selected_range]

    overall = tracker.get_overall_stats(days=days)
    trend_data = tracker.get_historical_trend(days=days)
    weekly_data = tracker.get_weekly_summary(weeks=8)
    category_data = tracker.get_stats_by_category()
    time_of_day_data = tracker.get_time_of_day_performance()
    goal_progress = tracker.get_goal_progress(lookback_days=7)
    recommendations = tracker.get_training_recommendations()
    weak_areas = tracker.identify_weak_areas(threshold=0.75)
    slow_areas = tracker.identify_slow_areas(threshold=5.0)

    hero_panel(
        "Analytics Command Center",
        "Monitor output, quality, and consistency. Tune goals and training blocks like a performance system.",
        [selected_range, f"Coaching score {goal_progress['coaching_score']:.0f}", "Single-user private data"],
    )

    nav_a, nav_b, nav_c = st.columns(3)
    with nav_a:
        if st.button("Back Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with nav_b:
        if st.button("Session Builder", use_container_width=True):
            st.session_state.page = "mode_selection"
            st.rerun()
    with nav_c:
        if weak_areas:
            if st.button(f"Train {str(weak_areas[0]).title()}", use_container_width=True, type="primary"):
                st.session_state.session_config = {
                    "mode_type": "targeted",
                    "category": weak_areas[0],
                    "difficulty": "medium",
                    "duration_seconds": None,
                    "question_count": 25,
                }
                st.session_state.page = "practice_session"
                st.rerun()
        else:
            if st.button("Start Session", use_container_width=True, type="primary"):
                st.session_state.page = "mode_selection"
                st.rerun()

    top_a, top_b, top_c, top_d = st.columns(4)
    with top_a:
        stat_card("Questions", f"{int(overall['total_questions']):,}", "🧮")
    with top_b:
        accuracy = f"{overall['accuracy']:.1f}%" if overall["total_questions"] else "--"
        stat_card("Accuracy", accuracy, "🎯")
    with top_c:
        speed = f"{overall['avg_time']:.2f}s" if overall["total_questions"] else "--"
        stat_card("Avg Time", speed, "⚡")
    with top_d:
        stat_card("Sessions", f"{int(overall['total_sessions'])}", "📦")

    if goal_progress["coaching_score"] >= 100:
        coach_note(
            "Signal",
            "You are meeting or exceeding goal profile across volume, consistency, and quality.",
            tone="positive",
        )
    else:
        coach_note(
            "Signal",
            "Your coaching score is below 100. Focus on the top recommendation block and re-check in 7 days.",
            tone="warning",
        )

    st.subheader("Goal Progress")
    gauge_a, gauge_b = st.columns(2)
    with gauge_a:
        acc_gauge = create_progress_gauge(
            current=float(goal_progress["accuracy_last_week"]),
            target=float(goal_progress["accuracy_target"]),
            title="Weekly Accuracy vs Target",
        )
        st.plotly_chart(acc_gauge, use_container_width=True, config={"displayModeBar": False})
    with gauge_b:
        volume_gauge = create_progress_gauge(
            current=float(goal_progress["questions_last_week"]),
            target=float(goal_progress["question_target_week"]),
            title="Weekly Volume vs Target",
        )
        st.plotly_chart(volume_gauge, use_container_width=True, config={"displayModeBar": False})

    with st.expander("Edit Goal Settings", expanded=False):
        current_goals = tracker.get_goal_settings()
        goal_daily_questions = st.slider("Daily question goal", min_value=10, max_value=150, value=current_goals.daily_questions)
        goal_weekly_sessions = st.slider("Weekly session goal", min_value=2, max_value=14, value=current_goals.weekly_sessions)
        goal_target_accuracy = st.slider(
            "Target accuracy (%)",
            min_value=60,
            max_value=99,
            value=int(current_goals.target_accuracy),
        )
        goal_target_avg_time = st.slider(
            "Target average time (seconds)",
            min_value=1.0,
            max_value=8.0,
            value=float(current_goals.target_avg_time),
            step=0.1,
        )

        if st.button("Save Goals", type="primary"):
            tracker.save_goal_settings(
                GoalSettings(
                    daily_questions=goal_daily_questions,
                    weekly_sessions=goal_weekly_sessions,
                    target_accuracy=float(goal_target_accuracy),
                    target_avg_time=goal_target_avg_time,
                )
            )
            st.success("Goals updated.")
            st.rerun()

    st.subheader("Trend Analysis")
    if trend_data.empty:
        st.info("Complete more sessions to unlock trend analytics.")
    else:
        trend_tab_a, trend_tab_b, trend_tab_c = st.tabs(["Accuracy", "Speed", "Volume"])
        with trend_tab_a:
            st.plotly_chart(
                create_accuracy_trend_chart(trend_data),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with trend_tab_b:
            st.plotly_chart(
                create_speed_trend_chart(trend_data),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with trend_tab_c:
            st.plotly_chart(
                create_question_volume_chart(trend_data),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    st.subheader("Category Intelligence")
    if category_data.empty:
        st.info("Category analytics appear after a few sessions.")
    else:
        cat_a, cat_b = st.columns([1.35, 1])
        with cat_a:
            st.plotly_chart(
                create_category_breakdown_chart(category_data),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with cat_b:
            st.plotly_chart(
                create_category_radar_chart(category_data),
                use_container_width=True,
                config={"displayModeBar": False},
            )

        if weak_areas:
            st.write("**Weak categories (<75% accuracy):** " + ", ".join(str(area).title() for area in weak_areas))
        if slow_areas:
            st.write("**Slow categories (>5s):** " + ", ".join(str(area).title() for area in slow_areas))

        action_cols = st.columns(3)
        if weak_areas:
            with action_cols[0]:
                if st.button(f"Train {str(weak_areas[0]).title()}", use_container_width=True):
                    st.session_state.session_config = {
                        "mode_type": "targeted",
                        "category": weak_areas[0],
                        "difficulty": "medium",
                        "duration_seconds": None,
                        "question_count": 25,
                    }
                    st.session_state.page = "practice_session"
                    st.rerun()
        with action_cols[1]:
            if st.button("Open Session Builder", use_container_width=True):
                st.session_state.page = "mode_selection"
                st.rerun()
        with action_cols[2]:
            if st.button("Back Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

    st.subheader("Consistency & Timing")
    consistency_a, consistency_b = st.columns(2)
    with consistency_a:
        if weekly_data.empty:
            st.info("Need more historical sessions for weekly consistency analytics.")
        else:
            st.plotly_chart(
                create_weekly_consistency_chart(weekly_data),
                use_container_width=True,
                config={"displayModeBar": False},
            )
    with consistency_b:
        if time_of_day_data.empty:
            st.info("Complete sessions at different times to view timing performance.")
        else:
            st.plotly_chart(
                create_heatmap_chart(time_of_day_data),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    st.subheader("Coach Recommendations")
    for rec in recommendations:
        tone = "warning" if rec["priority"] == "high" else "neutral"
        coach_note(rec["title"], rec["detail"], tone=tone)

    st.subheader("Badges")
    all_badges = badge_mgr.get_all_badges()
    earned_badges = [badge for badge in all_badges if badge.earned]
    locked_badges = [badge for badge in all_badges if not badge.earned]

    st.write(f"Earned {len(earned_badges)}/{len(all_badges)} badges")
    if earned_badges:
        for idx in range(0, len(earned_badges), 4):
            cols = st.columns(4)
            for offset, col in enumerate(cols):
                if idx + offset < len(earned_badges):
                    with col:
                        badge_display(earned_badges[idx + offset], earned=True)
    else:
        st.info("No badges yet. Complete sessions to start unlocking progression milestones.")

    with st.expander("Locked Badges"):
        for idx in range(0, min(8, len(locked_badges)), 4):
            cols = st.columns(4)
            for offset, col in enumerate(cols):
                if idx + offset < len(locked_badges):
                    with col:
                        badge_display(locked_badges[idx + offset], earned=False)

    st.subheader("Recent History")
    history = tracker.get_recent_sessions(limit=25)
    if history.empty:
        st.info("No completed sessions yet.")
    else:
        history = history.copy()
        history["Accuracy"] = (history["correct_answers"] / history["total_questions"] * 100).round(1)
        history["Date"] = history["timestamp"].apply(lambda value: str(value)[:16])
        history["Mode"] = history["mode_type"].apply(lambda value: str(value).capitalize())
        history["Category"] = history["category"].apply(lambda value: str(value).capitalize())
        history["Speed"] = history["avg_time_per_question"].round(2)
        history["Score"] = history["total_score"].astype(int)
        st.dataframe(
            history[["Date", "Mode", "Category", "Accuracy", "Speed", "Score"]],
            use_container_width=True,
            hide_index=True,
        )
