"""Reusable UI components."""

from collections.abc import Iterable
from typing import Callable, Optional

import streamlit as st

from src.models.question import Question
from src.models.user_stats import Badge


def _combo_stage(combo_count: int) -> tuple[int, float]:
    """Return (stage, scoring_multiplier) for a given combo count.

    Stages:
        0: no animation        (combo < 3)
        1: subtle pulse        (combo >= 3)
        2: glow                 (combo >= 5)
        3: ring rotation        (combo >= 10)
        4: sparkle ring         (combo >= 15)
    """
    if combo_count >= 15:
        return 4, 3.0
    if combo_count >= 10:
        return 3, 2.5
    if combo_count >= 5:
        return 2, 2.0
    if combo_count >= 3:
        return 1, 1.5
    return 0, 1.0


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
    """Display combo meter (backward-compatible: no escalation visuals)."""
    percentage = min(combo_count / max_combo * 100, 100)
    _, display_multiplier = _combo_stage(combo_count)

    st.markdown(
        f"""
        <div class="combo-text">Combo x{combo_count} ({display_multiplier:.1f}x scoring)</div>
        <div class="combo-meter">
            <div class="combo-meter-fill" style="width: {percentage}%;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def combo_glow(combo_count: int, max_combo: int = 15):
    """Display combo meter with escalation visuals (pulse/glow/ring/sparkle).

    Use this in places that want the celebratory effect; ``combo_meter`` is
    kept for callers that want the plain bar.
    """
    percentage = min(combo_count / max_combo * 100, 100)
    stage, display_multiplier = _combo_stage(combo_count)
    stage_class = f"combo-stage-{stage}" if stage > 0 else ""
    wrapper_class = "combo-glow" if stage > 0 else ""

    st.markdown(
        f"""
        <div class="{wrapper_class}">
            <div class="combo-text">Combo x{combo_count} ({display_multiplier:.1f}x scoring)</div>
            <div class="combo-meter {stage_class}">
                <div class="combo-meter-fill" style="width: {percentage}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def animated_score(value: int | float, key: str = "score", label: str = "Score"):
    """A score chip that count-ups on each render whose ``key`` changes.

    The animation re-runs whenever ``key`` changes (e.g. after a correct
    answer). We do this by including ``key`` in a CSS class so Streamlit
    sees a different DOM and re-applies the keyframe.
    """
    safe_key = "".join(ch if ch.isalnum() else "_" for ch in str(key))
    formatted = f"{int(value):,}" if isinstance(value, (int,)) or float(value).is_integer() else f"{value:,.1f}"
    st.markdown(
        f"""
        <span class="score-chip" data-key="{safe_key}">
            <span class="score-chip-label">{label}</span>
            <span class="score-chip-value" data-mm-anim="{safe_key}">{formatted}</span>
        </span>
        """,
        unsafe_allow_html=True,
    )


def milestone_hint(text: str, progress: int, target: int, icon: str = "🎯"):
    """Render a small "X more for Y" chip used to surface near-miss badges."""
    if target <= 0:
        return
    pct = max(0.0, min(progress / target * 100.0, 100.0))
    st.markdown(
        f"""
        <div class="milestone-hint">
            <span class="milestone-hint-icon">{icon}</span>
            <span class="milestone-hint-text">{text}</span>
            <span class="milestone-hint-progress">
                <span class="milestone-hint-fill" style="width: {pct:.0f}%;"></span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(
    title: str,
    body: str,
    cta_label: Optional[str] = None,
    on_click: Optional[Callable[[], None]] = None,
    *,
    cta_key: Optional[str] = None,
):
    """A friendly empty-state card for fresh-install screens.

    If ``cta_label`` and ``on_click`` are both supplied, a primary button
    is rendered below the card. The CTA is a regular Streamlit button so
    Streamlit can wire up the callback without HTML form posts.
    """
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-state-title">{title}</div>
            <div class="empty-state-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if cta_label and on_click:
        if st.button(
            cta_label,
            key=cta_key or f"empty_state_cta_{title}",
            use_container_width=True,
            type="primary",
        ):
            on_click()


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
