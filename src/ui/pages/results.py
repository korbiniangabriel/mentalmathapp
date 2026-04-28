"""Results page - session summary and insights."""

from __future__ import annotations

import streamlit as st

from src.analytics.insights_generator import InsightsGenerator
from src.analytics.performance_tracker import PerformanceTracker
from src.gamification.badge_manager import BadgeManager
from src.gamification.streak_tracker import StreakTracker
from src.ui.components import (
    badge_display,
    celebration_header,
    coach_note,
    insight_card,
    stat_card,
    streak_flame,
)


def show_results(db_manager):
    """Display results page."""
    if "session_summary" not in st.session_state:
        st.error("No session summary found")
        if st.button("Back Home"):
            st.session_state.page = "home"
            st.rerun()
        return

    summary = st.session_state.session_summary
    tracker = PerformanceTracker(db_manager)
    insights_gen = InsightsGenerator(db_manager)
    badge_mgr = BadgeManager(db_manager)
    streak_tracker = StreakTracker(db_manager)

    accuracy = summary.correct_answers / max(summary.total_questions, 1) * 100
    duration_min = summary.duration_seconds / 60 if summary.duration_seconds else 0
    goals = tracker.get_goal_settings()

    celebration_header("Session Complete")

    head_a, head_b, head_c, head_d = st.columns(4)
    with head_a:
        stat_card("Score", f"{summary.total_score:,}", "🏆")
    with head_b:
        stat_card("Accuracy", f"{accuracy:.1f}%", "🎯")
    with head_c:
        stat_card("Avg Time", f"{summary.avg_time_per_question:.2f}s", "⚡")
    with head_d:
        stat_card("Duration", f"{duration_min:.1f}m", "⏳")

    if accuracy >= goals.target_accuracy and summary.avg_time_per_question <= goals.target_avg_time:
        coach_note(
            "High-quality session",
            "You hit both quality gates: accuracy and speed. Keep this mode in your weekly rotation.",
            tone="positive",
        )
    elif accuracy < goals.target_accuracy:
        coach_note(
            "Primary fix",
            "Accuracy missed your target. Run a targeted session next to lock fundamentals before speed work.",
            tone="warning",
        )
    else:
        coach_note(
            "Secondary fix",
            "Accuracy is strong; speed is the limiter. Use short sprint blocks to cut response time.",
            tone="neutral",
        )

    st.subheader("Session Insights")
    insights = insights_gen.generate_session_insights(summary)
    for insight in insights:
        insight_card(insight["text"], insight["type"])

    newly_earned = badge_mgr.check_earned_badges(summary)
    if newly_earned:
        st.subheader("New Badges")
        cols = st.columns(min(4, len(newly_earned)))
        for idx, badge in enumerate(newly_earned):
            with cols[idx % len(cols)]:
                badge_display(badge, earned=True)
        st.balloons()

    st.subheader("Category Breakdown")
    by_type: dict[str, dict[str, float | int]] = {}
    for result in summary.results:
        q_type = result.question.question_type
        if q_type not in by_type:
            by_type[q_type] = {"total": 0, "correct": 0, "total_time": 0.0}

        by_type[q_type]["total"] += 1
        if result.is_correct:
            by_type[q_type]["correct"] += 1
        by_type[q_type]["total_time"] += float(result.time_taken)

    if by_type:
        sorted_breakdown = sorted(
            by_type.items(),
            key=lambda item: item[1]["correct"] / max(item[1]["total"], 1),
            reverse=True,
        )
        for q_type, stats in sorted_breakdown:
            total = int(stats["total"])
            correct = int(stats["correct"])
            avg_time = float(stats["total_time"]) / max(total, 1)
            line = f"**{q_type.title()}** · {correct}/{total} · {correct / max(total, 1) * 100:.0f}% · {avg_time:.2f}s"
            st.markdown(line)

    st.subheader("Streak")
    current_streak = streak_tracker.get_current_streak()
    if current_streak > 0:
        streak_flame(current_streak)
    else:
        st.info("No streak yet. A session tomorrow starts your streak run.")

    st.subheader("Next Action")
    nxt_a, nxt_b, nxt_c, nxt_d = st.columns(4)
    with nxt_a:
        if st.button("Run Again", use_container_width=True, type="primary"):
            st.session_state.session_config = {
                "mode_type": summary.config.mode_type,
                "category": summary.config.category,
                "difficulty": summary.config.difficulty,
                "duration_seconds": summary.config.duration_seconds,
                "question_count": summary.config.question_count,
            }
            st.session_state.page = "practice_session"
            st.session_state.active_session = None
            st.rerun()
    with nxt_b:
        if st.button("New Session Setup", use_container_width=True):
            st.session_state.page = "mode_selection"
            st.rerun()
    with nxt_c:
        if st.button("View Analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()
    with nxt_d:
        if st.button("Back Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
