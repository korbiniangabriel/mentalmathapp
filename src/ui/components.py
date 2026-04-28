"""Reusable UI components."""

from collections.abc import Iterable

import streamlit as st

from src.models.question import Question
from src.models.user_stats import Badge


def hero_panel(title: str, subtitle: str, chips: Iterable[str] | None = None):
    """Display a branded hero panel used on top-level pages."""
    chips = list(chips or [])
    chips_html = "".join(f"<span class='hero-chip'>{chip}</span>" for chip in chips)
    st.markdown(
        f"""
        <section class="hero-shell">
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
            <div class="hero-chip-row">{chips_html}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def stat_card(title: str, value: str, icon: str, supporting_text: str | None = None):
    """Display a metric card."""
    support = f"<div class='stat-card-support'>{supporting_text}</div>" if supporting_text else ""
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-card-icon">{icon}</div>
            <div class="stat-card-value">{value}</div>
            <div class="stat-card-label">{title}</div>
            {support}
        </div>
        """,
        unsafe_allow_html=True,
    )


def coach_note(title: str, text: str, tone: str = "neutral"):
    """Display a compact coaching note."""
    normalized_tone = tone if tone in {"positive", "neutral", "warning"} else "neutral"
    st.markdown(
        f"""
        <div class="coach-note coach-note-{normalized_tone}">
            <div class="coach-note-title">{title}</div>
            <div class="coach-note-body">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def combo_meter(combo_count: int, max_combo: int = 15):
    """Display combo meter."""
    percentage = min(combo_count / max_combo * 100, 100)
    display_multiplier = 1.0
    if combo_count >= 15:
        display_multiplier = 3.0
    elif combo_count >= 10:
        display_multiplier = 2.5
    elif combo_count >= 5:
        display_multiplier = 2.0
    elif combo_count >= 3:
        display_multiplier = 1.5

    st.markdown(
        f"""
        <div class="combo-text">Combo x{combo_count} ({display_multiplier:.1f}x scoring)</div>
        <div class="combo-meter">
            <div class="combo-meter-fill" style="width: {percentage}%;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar_with_label(current: int, total: int, label: str = "Progress"):
    """Display progress bar with label."""
    percentage = (current / total * 100) if total > 0 else 0
    st.markdown(
        f"""
        <div>
            <div class="progress-label">
                <span>{label}</span>
                <span>{current}/{total}</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {percentage}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_display(badge: Badge, earned: bool):
    """Display a badge with lock/unlock state."""
    lock_class = "" if earned else "badge-locked"
    st.markdown(
        f"""
        <div class="badge {lock_class}">
            <div class="badge-icon">{badge.icon}</div>
            <div class="badge-name">{badge.badge_name}</div>
            <div class="badge-description">{badge.description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(text: str, card_type: str = "neutral"):
    """Display an insight card."""
    normalized_type = card_type if card_type in {"positive", "negative", "neutral"} else "neutral"
    st.markdown(
        f"""
        <div class="insight-card insight-{normalized_type}">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def question_display(question: Question):
    """Display question in large, clear text."""
    st.markdown(
        f"""
        <div class="question-display">
            {question.question_text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def countdown_timer(seconds: int):
    """Display countdown timer."""
    warning_class = "timer-warning" if seconds < 30 else ""
    minutes = seconds // 60
    secs = seconds % 60
    st.markdown(
        f"""
        <div class="timer {warning_class}">
            {minutes:02d}:{secs:02d}
        </div>
        """,
        unsafe_allow_html=True,
    )


def streak_flame(days: int):
    """Display animated flame with streak count."""
    flames = "🔥" * max(min(days // 5 + 1, 4), 1)
    st.markdown(
        f"""
        <div class="streak-container">
            <div class="streak-flame streak-icon">{flames}</div>
            <div class="streak-text">{days} day streak</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feedback_display(is_correct: bool, correct_answer: str | None = None, time_taken: float | None = None):
    """Display answer feedback."""
    if is_correct:
        time_text = f" in {time_taken:.1f}s" if time_taken else ""
        st.markdown(
            f"""
            <div class="feedback-correct">Correct{time_text}</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        answer_text = f"<br><span class='feedback-answer'>Answer: {correct_answer}</span>" if correct_answer else ""
        st.markdown(
            f"""
            <div class="feedback-incorrect">Not quite{answer_text}</div>
            """,
            unsafe_allow_html=True,
        )


def celebration_header(text: str):
    """Display celebration header."""
    st.markdown(
        f"""
        <div class="celebration">
            <div class="celebration-title">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
