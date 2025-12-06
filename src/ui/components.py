"""Reusable UI components."""
import streamlit as st
from src.models.question import Question
from src.models.user_stats import Badge


def stat_card(title: str, value: str, icon: str):
    """Display a metric card.
    
    Args:
        title: Card title
        value: Value to display
        icon: Icon emoji
    """
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-icon">{icon}</div>
            <div class="stat-card-value">{value}</div>
            <div class="stat-card-label">{title}</div>
        </div>
    """, unsafe_allow_html=True)


def combo_meter(combo_count: int, max_combo: int = 15):
    """Display combo meter.
    
    Args:
        combo_count: Current combo count
        max_combo: Maximum combo for visualization
    """
    percentage = min(combo_count / max_combo * 100, 100)
    fire_emojis = "🔥" * min(combo_count // 3, 5)
    
    st.markdown(f"""
        <div class="combo-text">
            {fire_emojis} COMBO x{combo_count} {fire_emojis}
        </div>
        <div class="combo-meter">
            <div class="combo-meter-fill" style="width: {percentage}%;"></div>
        </div>
    """, unsafe_allow_html=True)


def progress_bar_with_label(current: int, total: int, label: str = "Progress"):
    """Display progress bar with label.
    
    Args:
        current: Current progress
        total: Total target
        label: Progress label
    """
    percentage = (current / total * 100) if total > 0 else 0
    
    st.markdown(f"""
        <div>
            <div class="progress-label">
                <span><b>{label}</b></span>
                <span>{current}/{total}</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {percentage}%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def badge_display(badge: Badge, earned: bool):
    """Display a badge with lock/unlock state.
    
    Args:
        badge: Badge object
        earned: Whether badge is earned
    """
    lock_class = "" if earned else "badge-locked"
    
    st.markdown(f"""
        <div class="badge {lock_class}">
            <div class="badge-icon">{badge.icon}</div>
            <div class="badge-name">{badge.badge_name}</div>
            <div class="badge-description">{badge.description}</div>
        </div>
    """, unsafe_allow_html=True)


def insight_card(text: str, card_type: str = "neutral"):
    """Display an insight card.
    
    Args:
        text: Insight text
        card_type: 'positive', 'negative', or 'neutral'
    """
    st.markdown(f"""
        <div class="insight-card insight-{card_type}">
            {text}
        </div>
    """, unsafe_allow_html=True)


def question_display(question: Question):
    """Display question in large, clear text.
    
    Args:
        question: Question object
    """
    st.markdown(f"""
        <div class="question-display">
            {question.question_text}
        </div>
    """, unsafe_allow_html=True)


def countdown_timer(seconds: int):
    """Display countdown timer.
    
    Args:
        seconds: Seconds remaining
    """
    warning_class = "timer-warning" if seconds < 30 else ""
    
    minutes = seconds // 60
    secs = seconds % 60
    
    st.markdown(f"""
        <div class="timer {warning_class}">
            ⏱️ {minutes:02d}:{secs:02d}
        </div>
    """, unsafe_allow_html=True)


def streak_flame(days: int):
    """Display animated flame with streak count.
    
    Args:
        days: Number of days in streak
    """
    flame_size = min(days // 3, 5)
    flames = "🔥" * max(flame_size, 1)
    
    st.markdown(f"""
        <div class="streak-container">
            <div class="streak-flame streak-icon">
                {flames}
            </div>
            <div class="streak-text">
                {days} Day Streak!
            </div>
        </div>
    """, unsafe_allow_html=True)


def feedback_display(is_correct: bool, correct_answer: str = None, time_taken: float = None):
    """Display answer feedback.
    
    Args:
        is_correct: Whether answer was correct
        correct_answer: Correct answer (shown if incorrect)
        time_taken: Time taken in seconds
    """
    if is_correct:
        time_text = f" ({time_taken:.1f}s)" if time_taken else ""
        st.markdown(f"""
            <div class="feedback-correct">
                ✅ CORRECT!{time_text}
            </div>
        """, unsafe_allow_html=True)
    else:
        answer_text = f"<br>Correct answer: {correct_answer}" if correct_answer else ""
        st.markdown(f"""
            <div class="feedback-incorrect">
                ❌ INCORRECT{answer_text}
            </div>
        """, unsafe_allow_html=True)


def celebration_header(text: str):
    """Display celebration header.
    
    Args:
        text: Celebration text
    """
    st.markdown(f"""
        <div class="celebration">
            <div class="celebration-title">{text}</div>
        </div>
    """, unsafe_allow_html=True)
