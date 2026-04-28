"""Home dashboard page.

Action-first layout:
    1. One big primary CTA: 2-minute sprint.
    2. A row of secondary actions (custom session, drill weakest, daily challenge).
    3. Analytics / recent sessions / recommendations below the fold.

Tone: neutral, inviting. Avoid grading language ("below plan", "coaching score").
Empty state: a friendly welcome card on fresh installs.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from src.analytics.performance_tracker import PerformanceTracker
from src.daily.challenge import DailyChallenge
from src.ui.components import (
    coach_note,
    empty_state,
    hero_panel,
    stat_card,
    streak_flame,
)


def _start_session(config: dict):
    st.session_state.session_config = config
    st.session_state.page = "practice_session"
    st.rerun()


def _start_daily():
    st.session_state.page = "daily"
    st.rerun()


def _go(page: str):
    st.session_state.page = page
    st.rerun()


def _has_coaching_data(coaching_score) -> bool:
    """Coaching score may be None or negative as a sentinel for 'no data yet'."""
    if coaching_score is None:
        return False
    try:
        return float(coaching_score) >= 0
    except (TypeError, ValueError):
        return False


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

    coaching_score = goal_progress.get("coaching_score")
    has_data = overall["total_questions"] > 0 and _has_coaching_data(coaching_score)

    daily = DailyChallenge()
    daily_done = daily.has_completed_today(db_manager)

    # Hero with neutral framing, no "interview-grade" / "cockpit" copy.
    chips = [f"{date.today():%a, %b %d}"]
    if overall["current_streak"]:
        chips.append(f"Streak {int(overall['current_streak'])}d")
    if has_data:
        chips.append(f"7d Accuracy {week_stats['accuracy']:.0f}%")
    chips.append("Daily challenge ready" if not daily_done else "Daily challenge done")

    hero_panel(
        "Mental Math Coach",
        "Quick reps to keep your numbers sharp. Pick a session and go.",
        chips,
    )

    # ---------------- Action-first block ----------------
    if not has_data:
        empty_state(
            "Welcome.",
            "Try a 2-minute sprint to warm up. We'll learn your pace from there.",
            cta_label="Start a 2-min sprint",
            on_click=lambda: _start_session(quick_configs["2m Sprint"]),
            cta_key="empty_start_sprint",
        )
    else:
        st.markdown(
            """
            <div class="primary-cta">
                <div class="primary-cta-eyebrow">Today's quick rep</div>
                <div class="primary-cta-title">Start a 2-min sprint</div>
                <div class="primary-cta-sub">Mixed practice, medium difficulty. Builds rhythm in two minutes.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Start 2-min sprint",
            key="primary_cta_sprint",
            use_container_width=True,
            type="primary",
        ):
            _start_session(quick_configs["2m Sprint"])

    # Secondary action row.
    sec_a, sec_b, sec_c = st.columns(3)
    with sec_a:
        if st.button("Custom Session", key="sec_custom", use_container_width=True):
            _go("mode_selection")
    with sec_b:
        drill_label = f"Drill {primary_focus.title()}"
        if st.button(drill_label, key="sec_drill", use_container_width=True):
            _start_session(quick_configs["Focused 25"])
    with sec_c:
        daily_label = "Daily Challenge ✓" if daily_done else "Daily Challenge"
        if st.button(
            daily_label,
            key="sec_daily",
            use_container_width=True,
            disabled=daily_done,
            help="Done — come back tomorrow." if daily_done else "5 questions, same for everyone today.",
        ):
            _start_daily()

    # If there's no usage history yet, stop here. Don't dump empty analytics.
    if not has_data:
        return

    # ---------------- Status (neutral, not graded) ----------------
    questions_done = int(goal_progress.get("questions_last_week") or 0)
    sessions_done = int(goal_progress.get("sessions_last_week") or 0)
    next_focus = primary_focus.title() if primary_focus and primary_focus != "mixed" else "Mixed practice"

    coach_note(
        "This week so far",
        (
            f"{questions_done} questions across {sessions_done} sessions. "
            f"Coming up: {next_focus} — quick reps to keep momentum."
        ),
        tone="neutral",
    )

    # ---------------- Stats (below the fold) ----------------
    st.subheader("Snapshot")
    top_a, top_b, top_c, top_d = st.columns(4)
    with top_a:
        stat_card("Total Questions", f"{overall['total_questions']:,}", "🧮")
    with top_b:
        accuracy = f"{overall['accuracy']:.1f}%" if overall["total_questions"] else "—"
        stat_card("Lifetime Accuracy", accuracy, "🎯")
    with top_c:
        avg_time = f"{overall['avg_time']:.2f}s" if overall["total_questions"] else "—"
        stat_card("Avg Speed", avg_time, "⚡")
    with top_d:
        streak_days = int(float(overall.get("current_streak", 0)))
        stat_card("Current Streak", f"{streak_days}d", "🔥")

    st.subheader("This Week")
    plan_a, plan_b, plan_c = st.columns(3)
    with plan_a:
        stat_card(
            "Questions",
            f"{goal_progress['questions_last_week']}/{goal_progress['question_target_week']}",
            "📚",
        )
    with plan_b:
        stat_card(
            "Sessions",
            f"{goal_progress['sessions_last_week']}/{goal_progress['session_target_week']}",
            "🗓️",
        )
    with plan_c:
        stat_card(
            "Targets",
            f"{goals.target_accuracy:.0f}% · {goals.target_avg_time:.1f}s",
            "🎛️",
        )

    st.subheader("Trend")
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
            st.caption("Most recent active day vs the prior period.")

    with snap_r:
        streak_days = int(float(overall.get("current_streak", 0)))
        if streak_days > 0:
            streak_flame(streak_days)
        else:
            st.info("No active streak yet. One session today starts it.")

    if recommendations:
        st.subheader("Suggestions")
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

    if st.button("Open Analytics", key="open_analytics", use_container_width=True):
        _go("analytics")
