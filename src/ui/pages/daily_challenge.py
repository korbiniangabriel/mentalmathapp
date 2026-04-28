"""Daily challenge page.

Runs the deterministic 5-question daily challenge. Implemented as a small
standalone flow rather than reusing the practice-session component, because
the daily challenge needs a pre-generated question queue (same questions
for everyone today) and the existing session manager generates its own
questions on demand.

Flow:
    - Show the question.
    - Accept an answer (Enter button + plain text input — no fancy auto-advance).
    - Show feedback and a Next button.
    - On the final question, persist a SessionSummary and route to results,
      then mark today as completed in user_preferences.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from src.daily.challenge import DAILY_CHALLENGE_SIZE, DailyChallenge
from src.game_logic.scoring import ScoreCalculator
from src.game_logic.validator import AnswerValidator
from src.models.session import (
    QuestionResult,
    SessionConfig,
    SessionSummary,
)
from src.ui.components import (
    coach_note,
    feedback_display,
    progress_bar_with_label,
    question_display,
)


_DAILY_STATE_KEY = "_daily_state"


def _new_daily_state(challenge: DailyChallenge) -> dict:
    return {
        "date": challenge.today.isoformat(),
        "questions": challenge.get_questions_for_today(),
        "results": [],
        "current_index": 0,
        "combo_count": 0,
        "total_score": 0,
        "start_time": datetime.now(),
        "question_started_at": datetime.now(),
        "show_feedback": False,
        "last_result": None,
    }


def _reset_if_new_day(state: dict, today_iso: str) -> bool:
    return state.get("date") != today_iso


def _go_home():
    st.session_state.page = "home"
    st.rerun()


def show_daily_challenge(db_manager):
    """Display the daily challenge page."""
    challenge = DailyChallenge()
    today_iso = challenge.today.isoformat()

    # Already completed? Render a friendly "come back tomorrow" state.
    if challenge.has_completed_today(db_manager):
        st.markdown("### Daily Challenge")
        coach_note(
            "Done for today",
            "You've already finished today's daily challenge. Come back tomorrow for a fresh five.",
            tone="positive",
        )
        if st.button("Back Home", use_container_width=True):
            _go_home()
        return

    # Initialize / refresh state.
    state = st.session_state.get(_DAILY_STATE_KEY)
    if state is None or _reset_if_new_day(state, today_iso):
        state = _new_daily_state(challenge)
        st.session_state[_DAILY_STATE_KEY] = state

    questions = state["questions"]
    idx = state["current_index"]

    st.markdown("### Daily Challenge")
    st.caption(f"5 questions · seeded for {today_iso} · same for everyone today.")

    progress_bar_with_label(
        current=min(idx, DAILY_CHALLENGE_SIZE),
        total=DAILY_CHALLENGE_SIZE,
        label="Daily progress",
    )

    # End-of-challenge handoff: build summary, save, mark done, route to results.
    if idx >= DAILY_CHALLENGE_SIZE:
        _finalize_daily(db_manager, state, challenge)
        return

    current_question = questions[idx]

    # Feedback view (after a wrong/skipped attempt).
    if state["show_feedback"] and state["last_result"] is not None:
        result = state["last_result"]
        feedback_display(
            result.is_correct,
            result.question.correct_answer,
            result.time_taken,
        )
        if st.button("➡️ Next", key=f"daily_next_{idx}", use_container_width=True):
            state["show_feedback"] = False
            state["last_result"] = None
            state["question_started_at"] = datetime.now()
            st.rerun()
        return

    question_display(current_question)

    answer_key = f"daily_answer_{idx}"
    st.text_input(
        "Answer:",
        key=answer_key,
        placeholder="Enter answer...",
        label_visibility="collapsed",
    )

    col_enter, col_skip = st.columns(2)
    with col_enter:
        enter_clicked = st.button(
            "⏎ Enter",
            key=f"daily_enter_{idx}",
            use_container_width=True,
            type="primary",
        )
    with col_skip:
        skip_clicked = st.button(
            "⏭️ Skip",
            key=f"daily_skip_{idx}",
            use_container_width=True,
        )

    if enter_clicked:
        raw = st.session_state.get(answer_key, "") or ""
        _submit_answer(state, current_question, raw, was_skipped=False)
        st.rerun()
    elif skip_clicked:
        _submit_answer(state, current_question, "", was_skipped=True)
        st.rerun()


def _submit_answer(state: dict, question, raw_answer: str, *, was_skipped: bool):
    """Validate and record the user's answer for the current daily question."""
    answer = (raw_answer or "").strip()

    if was_skipped:
        is_correct = False
    else:
        is_correct = AnswerValidator.validate(answer, question)

    started_at = state.get("question_started_at") or state["start_time"]
    time_taken = max(0.0, (datetime.now() - started_at).total_seconds())

    result = QuestionResult(
        question=question,
        user_answer=answer,
        is_correct=is_correct,
        time_taken=time_taken,
        timestamp=datetime.now(),
        was_skipped=was_skipped,
    )

    if is_correct:
        state["combo_count"] += 1
    else:
        state["combo_count"] = 0

    score = ScoreCalculator.calculate_question_score(result, state["combo_count"])
    state["total_score"] += score
    state["results"].append(result)
    state["current_index"] += 1
    state["question_started_at"] = datetime.now()

    if is_correct:
        # No feedback panel for correct — flow straight to next question.
        state["show_feedback"] = False
        state["last_result"] = None
    else:
        state["show_feedback"] = True
        state["last_result"] = result


def _finalize_daily(db_manager, state: dict, challenge: DailyChallenge):
    """Persist the completed daily-challenge session and route to results."""
    results = state["results"]
    if not results:
        # Defensive: nothing to save.
        st.session_state.pop(_DAILY_STATE_KEY, None)
        _go_home()
        return

    total_questions = len(results)
    correct_answers = sum(1 for r in results if r.is_correct)
    avg_time = round(sum(r.time_taken for r in results) / total_questions, 2)
    duration = int((datetime.now() - state["start_time"]).total_seconds())

    # NOTE: the sessions table's CHECK constraint only allows
    # ('sprint', 'marathon', 'targeted') for mode_type. The daily challenge
    # is fundamentally a fixed-count session, so we persist it as 'marathon'
    # to satisfy the constraint while keeping the gameplay semantics intact.
    # The user's "I did the daily today" flag is stored separately in
    # user_preferences (see DailyChallenge.mark_completed).
    config = SessionConfig(
        mode_type="marathon",
        category="mixed",
        difficulty="medium",
        duration_seconds=None,
        question_count=total_questions,
    )

    summary = SessionSummary(
        session_id=None,
        config=config,
        total_questions=total_questions,
        correct_answers=correct_answers,
        total_score=state["total_score"],
        avg_time_per_question=avg_time,
        duration_seconds=duration,
        results=results,
        timestamp=state["start_time"],
    )

    try:
        session_id = db_manager.save_session(summary)
        summary.session_id = session_id
    except Exception:
        # Persistence failure shouldn't block showing results.
        pass

    # Mark today as done so the home dashboard / mode picker show the locked state.
    challenge.mark_completed(db_manager)

    st.session_state.session_summary = summary
    st.session_state.pop(_DAILY_STATE_KEY, None)
    st.session_state.page = "results"
    st.rerun()
