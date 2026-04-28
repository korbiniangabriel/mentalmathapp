"""Mode selection page."""

from __future__ import annotations

import streamlit as st

from src.analytics.performance_tracker import PerformanceTracker
from src.ui.components import coach_note, hero_panel, stat_card


def _get_tracker() -> PerformanceTracker | None:
    db_manager = st.session_state.get("db_manager")
    if not db_manager:
        return None
    return PerformanceTracker(db_manager)


def show_mode_selection():
    """Display mode selection page."""
    tracker = _get_tracker()
    weak_areas = tracker.identify_weak_areas(threshold=0.75) if tracker else []
    recommended_category = str(weak_areas[0]) if weak_areas else "mixed"

    hero_panel(
        "Session Builder",
        "Create a deliberate practice block: choose mode, category, and difficulty with clear intent.",
        [f"Recommended focus: {recommended_category.title()}", "Adaptive coaching ready"],
    )

    if st.button("Back to Dashboard"):
        st.session_state.page = "home"
        st.rerun()

    coach_note(
        "Design principle",
        "Use sprint for speed, marathon for endurance, and targeted sessions for fixing weak categories.",
        tone="neutral",
    )

    mode_type = st.radio(
        "Session mode",
        ["Sprint", "Marathon", "Targeted"],
        horizontal=True,
    )

    duration_seconds = None
    question_count = None
    if mode_type == "Sprint":
        duration_seconds = st.select_slider(
            "Duration",
            options=[60, 120, 180, 300],
            value=120,
            format_func=lambda value: f"{value // 60} min",
        )
        workload_label = f"{duration_seconds // 60} min speed block"
    elif mode_type == "Marathon":
        question_count = st.select_slider(
            "Question count",
            options=[25, 50, 75, 100],
            value=50,
        )
        workload_label = f"{question_count} questions endurance block"
    else:
        question_count = st.select_slider(
            "Question count",
            options=[15, 25, 40, 60],
            value=25,
        )
        workload_label = f"{question_count} questions focused repair"

    categories = {
        "Mixed": "mixed",
        "Arithmetic": "arithmetic",
        "Percentage": "percentage",
        "Fractions": "fractions",
        "Ratios": "ratios",
        "Compound": "compound",
        "Estimation": "estimation",
    }

    if mode_type == "Targeted":
        target_strategy = st.radio(
            "Targeting strategy",
            ["Auto weakest areas", "Pick one category"],
            horizontal=True,
        )
        if target_strategy == "Auto weakest areas":
            category = "targeted"
            category_label = "Auto weakest areas"
        else:
            default_index = list(categories.values()).index(recommended_category) if recommended_category in categories.values() else 0
            category_label = st.selectbox("Focus category", list(categories.keys()), index=default_index)
            category = categories[category_label]
    else:
        default_index = list(categories.values()).index(recommended_category) if recommended_category in categories.values() else 0
        category_label = st.selectbox("Category", list(categories.keys()), index=default_index)
        category = categories[category_label]

    difficulties = {
        "Easy": "easy",
        "Medium": "medium",
        "Hard": "hard",
        "Adaptive": "adaptive",
    }
    difficulty_display = st.radio(
        "Difficulty",
        list(difficulties.keys()),
        horizontal=True,
        index=1,
    )
    difficulty = difficulties[difficulty_display]

    st.subheader("Session Preview")
    p1, p2, p3 = st.columns(3)
    with p1:
        stat_card("Mode", mode_type, "🧭")
    with p2:
        stat_card("Workload", workload_label, "📦")
    with p3:
        stat_card("Difficulty", difficulty_display, "🎚️")

    if mode_type == "Targeted" and category == "targeted":
        coach_note(
            "Auto Targeting",
            "The app will route questions to weak areas based on your historical accuracy profile.",
            tone="positive",
        )

    if st.button("Start Session", use_container_width=True, type="primary"):
        st.session_state.session_config = {
            "mode_type": mode_type.lower(),
            "category": category,
            "difficulty": difficulty,
            "duration_seconds": duration_seconds,
            "question_count": question_count,
        }
        st.session_state.page = "practice_session"
        st.rerun()
