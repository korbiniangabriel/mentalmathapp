"""Practice session page — thin shell around the practice_loop component.

The custom component (``src/components/practice_loop``) owns the entire
client-side game loop (timer, question, input, score, combo, skip, quit).
This page only sets up (pre-generate questions, mount component) and tears
down (replay results through SessionManager for combo/score/persistence).
"""
from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from src.components.practice_loop import practice_loop
from src.game_logic.session_manager import SessionManager
from src.models.session import SessionConfig


def _make_config(state) -> SessionConfig | None:
    raw = state.get("session_config") or state.get("quick_mode")
    if not raw:
        return None
    return SessionConfig(
        mode_type=raw["mode_type"],
        category=raw["category"],
        difficulty=raw["difficulty"],
        duration_seconds=raw.get("duration_seconds"),
        question_count=raw.get("question_count"),
    )


def _pregenerate(sm: SessionManager, sess, target: int):
    """Materialise `target` questions up front so the JS loop never starves."""
    qs = []
    if sess.current_question is not None:
        qs.append(sess.current_question)
    for _ in range(max(0, target - len(qs))):
        qs.append(sm.get_next_question(sess))
    return qs


def _serialize(questions):
    out = []
    for idx, q in enumerate(questions):
        acceptable = [str(a) for a in (q.acceptable_answers or [q.correct_answer])]
        out.append({
            "id": idx,
            "text": q.question_text,
            "acceptable_answers": acceptable,
            "correct_answer": str(q.correct_answer),
            "needs_fraction_keyboard": any("/" in a for a in acceptable),
        })
    return out


def _replay(sm: SessionManager, sess, questions, results):
    """Walk component results through submit_answer so scoring/persistence run."""
    for cr in results:
        qid = cr.get("question_id")
        if qid is None or qid >= len(questions):
            continue
        sess.current_question = questions[qid]
        sess.question_started_at = datetime.now() - timedelta(seconds=float(cr.get("time_taken") or 0))
        sm.submit_answer(sess, cr.get("user_answer") or "", was_skipped=bool(cr.get("was_skipped")))
    sess.is_complete = True


def show_practice_session(db_manager):
    if "session_manager" not in st.session_state:
        st.session_state.session_manager = SessionManager(db_manager)
    sm: SessionManager = st.session_state.session_manager

    if not st.session_state.get("active_session") or not st.session_state.get("_practice_questions"):
        config = _make_config(st.session_state)
        if config is None:
            st.error("No session configuration found.")
            if st.button("← Home"):
                st.session_state.page = "home"
                st.rerun()
            return
        sess = sm.start_session(config)
        target = max(60, int(config.duration_seconds or 0) // 2 + 20) if config.mode_type == "sprint" else int(config.question_count or 25) + 5
        st.session_state.active_session = sess
        st.session_state._practice_questions = _pregenerate(sm, sess, target)
        st.session_state._practice_key = "practice_loop_" + sess.start_time.strftime("%Y%m%d%H%M%S%f")

    sess = st.session_state.active_session
    questions = st.session_state._practice_questions

    st.markdown(f"### {sess.config.mode_type.title()} Session")

    result = practice_loop(
        questions=_serialize(questions),
        mode=sess.config.mode_type,
        duration_seconds=sess.config.duration_seconds,
        question_count=sess.config.question_count,
        category_label=sess.config.category.title(),
        difficulty_label=sess.config.difficulty.title(),
        key=st.session_state._practice_key,
        height=640,
    )

    if result and result.get("completed"):
        comp_results = result.get("results") or []
        if comp_results:
            _replay(sm, sess, questions, comp_results)
            try:
                st.session_state.session_summary = sm.end_session(sess)
            except ValueError:
                st.session_state.session_summary = None
        else:
            st.session_state.session_summary = None
        st.session_state.active_session = None
        st.session_state._practice_questions = None
        st.session_state._practice_key = None
        st.session_state.page = "results" if st.session_state.session_summary else "home"
        st.rerun()
