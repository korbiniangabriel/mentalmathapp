"""Home dashboard page."""

from __future__ import annotations

from datetime import date

import streamlit as st

from src.analytics.performance_tracker import PerformanceTracker
from src.ui.components import coach_note, hero_panel, stat_card, streak_flame


def _start_session(config: dict):
    st.session_state.session_config = config
    st.session_state.page = "practice_session"
    st.rerun()


def _quick_configs(primary_category: str) -> dict[str, dict]:
    return {
        "2m Sprint": {
            "mode_type": "sprint",
            "category": "mixed",
            "difficulty": "medium",
            "duration_seconds": 120,
            "question_count": None,
        },
        "Focused 25": {
            "mode_type": "targeted",
            "category": primary_category,
            "difficulty": "medium",
            "duration_seconds": None,
            "question_count": 25,
        },
        "Hard 50": {
            "mode_type": "marathon",
            "category": "mixed",
            "difficulty": "hard",
            "duration_seconds": None,
            "question_count": 50,
        },
    }


def show_home_dashboard(db_manager):
    """Display the home dashboard."""
    tracker = PerformanceTracker(db_manager)

    overall = tracker.get_overall_stats()
    week_stats = tracker.get_overall_stats(days=7)
    trend_14d = tracker.get_historical_trend(days=14)
    recent_sessions = tracker.get_recent_sessions(limit=6)
    goals = tracker.get_goal_settings()
    goal_progress = tracker.get_goal_progress(lookback_days=7)
    recommendations = tracker.get_training_recommendations()
    weak_areas = tracker.identify_weak_areas(threshold=0.75)

    primary_focus = str(weak_areas[0]) if weak_areas else "mixed"
    quick_configs = _quick_configs(primary_focus)

    chips = [
        f"{date.today():%a, %b %d}",
        f"Streak {overall['current_streak']}d",
        f"7d Accuracy {week_stats['accuracy']:.0f}%",
        f"Goal Score {goal_progress['coaching_score']:.0f}",
    ]

    hero_panel(
        "Mental Math Coach",
        "Solo training cockpit: set pace, drill weak spots, and track interview-grade readiness.",
        chips,
    )

    if overall["total_questions"] == 0:
        coach_note(
            "Kickoff",
            "Start with a 2-minute sprint. It calibrates your first baseline and unlocks personalized coaching.",
            tone="neutral",
        )
    elif goal_progress["coaching_score"] >= 100:
        coach_note(
            "On pace",
            "You are beating your weekly targets. Keep volume steady and increase one session to hard mode.",
            tone="positive",
        )
    else:
        coach_note(
            "Coach focus",
            f"You are below plan this week. Prioritize {primary_focus.title()} and close the consistency gap first.",
            tone="warning",
        )

    top_a, top_b, top_c, top_d = st.columns(4)
    with top_a:
        stat_card("Total Questions", f"{overall['total_questions']:,}", "🧮")
    with top_b:
        accuracy = f"{overall['accuracy']:.1f}%" if overall["total_questions"] else "--"
        stat_card("Lifetime Accuracy", accuracy, "🎯")
    with top_c:
        avg_time = f"{overall['avg_time']:.2f}s" if overall["total_questions"] else "--"
        stat_card("Avg Speed", avg_time, "⚡")
    with top_d:
        stat_card("This Week Score", f"{goal_progress['coaching_score']:.0f}", "📈", "Goal alignment")

    action_a, action_b, action_c = st.columns([1.2, 1, 1])
    with action_a:
        if st.button("Start Focus Session", use_container_width=True, type="primary"):
            _start_session(
                {
                    "mode_type": "targeted",
                    "category": primary_focus,
                    "difficulty": "medium",
                    "duration_seconds": None,
                    "question_count": 25,
                }
            )
    with action_b:
        if st.button("Custom Session", use_container_width=True):
            st.session_state.page = "mode_selection"
            st.rerun()
    with action_c:
        if st.button("Analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()

    st.subheader("This Week Plan")
    plan_a, plan_b, plan_c = st.columns(3)
    with plan_a:
        stat_card(
            "Question Goal",
            f"{goal_progress['questions_last_week']}/{goal_progress['question_target_week']}",
            "📚",
        )
    with plan_b:
        stat_card(
            "Session Goal",
            f"{goal_progress['sessions_last_week']}/{goal_progress['session_target_week']}",
            "🗓️",
        )
    with plan_c:
        stat_card(
            "Targets",
            f"{goals.target_accuracy:.0f}% · {goals.target_avg_time:.1f}s",
            "🎛️",
        )

    quick_a, quick_b, quick_c = st.columns(3)
    with quick_a:
        if st.button("Run 2m Sprint", use_container_width=True):
            _start_session(quick_configs["2m Sprint"])
    with quick_b:
        if st.button(f"Drill {primary_focus.title()}", use_container_width=True):
            _start_session(quick_configs["Focused 25"])
    with quick_c:
        if st.button("Hard 50 Challenge", use_container_width=True):
            _start_session(quick_configs["Hard 50"])

    st.subheader("Performance Snapshot")
    snap_l, snap_r = st.columns([1.25, 1])

    with snap_l:
        if trend_14d.empty:
            st.info("Complete a session to unlock your trend view.")
        else:
            last_row = trend_14d.iloc[-1]
            previous = trend_14d.iloc[:-1]
            prev_acc = previous["accuracy"].mean() if not previous.empty else last_row["accuracy"]
            prev_speed = previous["avg_time"].mean() if not previous.empty else last_row["avg_time"]

            metric_a, metric_b = st.columns(2)
            with metric_a:
                st.metric(
                    "Latest Daily Accuracy",
                    f"{last_row['accuracy']:.1f}%",
                    f"{last_row['accuracy'] - prev_acc:+.1f}% vs prior",
                )
            with metric_b:
                st.metric(
                    "Latest Daily Speed",
                    f"{last_row['avg_time']:.2f}s",
                    f"{prev_speed - last_row['avg_time']:+.2f}s faster",
                )
            st.caption("Accuracy and speed compare your most recent active day to the prior period.")

    with snap_r:
        streak_days = int(float(overall.get("current_streak", 0)))
        if streak_days > 0:
            streak_flame(streak_days)
        else:
            st.info("No active streak yet. One session today starts it.")

    st.subheader("Coach Recommendations")
    for rec in recommendations:
        tone = "warning" if rec["priority"] == "high" else "neutral"
        coach_note(rec["title"], rec["detail"], tone=tone)

    st.subheader("Recent Sessions")
    if recent_sessions.empty:
        st.info("No completed sessions yet. Start your first session to build history.")
    else:
        for _, session in recent_sessions.iterrows():
            accuracy = session["correct_answers"] / max(session["total_questions"], 1) * 100
            mode_raw = f"{session['mode_type']}"
            category_raw = f"{session['category']}"
            mode_label = mode_raw[:1].upper() + mode_raw[1:]
            category_label = category_raw[:1].upper() + category_raw[1:]
            line = (
                f"**{str(session['timestamp'])[:16]}** · {mode_label} · "
                f"{category_label} · {accuracy:.0f}% · {session['avg_time_per_question']:.2f}s · "
                f"{int(session['total_score']):,} pts"
            )
            st.markdown(line)
