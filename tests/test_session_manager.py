"""Tests for `SessionManager` lifecycle and skip semantics.

Covers:
- `start_session` stamps `question_started_at` and seeds the first
  question.
- `submit_answer` advances the cursor, records elapsed time, and
  resets/grows the combo as expected for both real attempts and skips.
- Mode termination logic for sprint / marathon / targeted (default 25
  question budget for targeted).
- End-of-session persistence — `was_skipped` round-trips through the
  database.
- Empty `end_session` path raises (Batch B may soften this; we'll
  update the test if the contract changes).
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
import time
from datetime import datetime, timedelta

import pytest

from src.database.db_manager import DatabaseManager
from src.game_logic.session_manager import SessionManager
from src.models.session import SessionConfig, SessionState


@pytest.fixture
def db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseManager(path)
    yield db
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def manager(db):
    return SessionManager(db)


@pytest.fixture
def sprint_config():
    return SessionConfig(
        mode_type="sprint",
        category="arithmetic",
        difficulty="easy",
        duration_seconds=120,
    )


@pytest.fixture
def marathon_config():
    return SessionConfig(
        mode_type="marathon",
        category="arithmetic",
        difficulty="easy",
        question_count=3,
    )


# ---------------------------------------------------------------------------
# Lifecycle.
# ---------------------------------------------------------------------------


class TestStartSession:

    def test_seeds_first_question(self, manager, sprint_config):
        state = manager.start_session(sprint_config)
        assert state.current_question is not None
        assert state.current_question.correct_answer

    def test_question_started_at_stamped(self, manager, sprint_config):
        before = datetime.now()
        state = manager.start_session(sprint_config)
        after = datetime.now()
        assert state.question_started_at is not None
        assert before <= state.question_started_at <= after

    def test_initial_state(self, manager, sprint_config):
        state = manager.start_session(sprint_config)
        assert state.combo_count == 0
        assert state.total_score == 0
        assert state.is_complete is False
        assert state.questions_answered == []


class TestSubmitAnswer:

    def test_correct_answer_advances(self, manager, marathon_config):
        state = manager.start_session(marathon_config)
        first_q = state.current_question
        result = manager.submit_answer(state, first_q.correct_answer)
        assert result.is_correct is True
        assert result.was_skipped is False
        assert state.combo_count == 1
        assert len(state.questions_answered) == 1
        # Next question is loaded with a fresh start time.
        assert state.current_question is not first_q

    def test_time_taken_reflects_elapsed(self, manager, marathon_config):
        state = manager.start_session(marathon_config)
        time.sleep(0.05)
        result = manager.submit_answer(state, state.current_question.correct_answer)
        # 50ms elapsed → time_taken should be at least ~0.04s (allow
        # scheduling jitter).
        assert result.time_taken >= 0.04, result.time_taken

    def test_question_started_at_resets_per_question(self, manager, marathon_config):
        state = manager.start_session(marathon_config)
        ts1 = state.question_started_at

        manager.submit_answer(state, state.current_question.correct_answer)
        ts2 = state.question_started_at
        assert ts2 is not None
        assert ts2 >= ts1

    def test_wrong_answer_resets_combo(self, manager, marathon_config):
        state = manager.start_session(marathon_config)
        manager.submit_answer(state, state.current_question.correct_answer)
        assert state.combo_count == 1
        manager.submit_answer(state, "definitely-not-right")
        assert state.combo_count == 0

    def test_skipped_records_skip_resets_combo(self, manager, marathon_config):
        state = manager.start_session(marathon_config)
        manager.submit_answer(state, state.current_question.correct_answer)
        assert state.combo_count == 1
        result = manager.submit_answer(state, "anything", was_skipped=True)
        assert result.was_skipped is True
        assert result.is_correct is False
        assert state.combo_count == 0
        # Even though the validator might have accepted "anything" against
        # some quirky question, skipped answers can never be correct.

    def test_skipped_correct_answer_still_not_correct(self, manager, marathon_config):
        state = manager.start_session(marathon_config)
        correct_text = state.current_question.correct_answer
        result = manager.submit_answer(state, correct_text, was_skipped=True)
        assert result.was_skipped is True
        assert result.is_correct is False

    def test_submit_without_question_raises(self, manager, sprint_config):
        state = SessionState(config=sprint_config)
        with pytest.raises(ValueError):
            manager.submit_answer(state, "5")


# ---------------------------------------------------------------------------
# Mode termination.
# ---------------------------------------------------------------------------


class TestSessionEnd:

    def test_marathon_ends_when_count_reached(self, manager, marathon_config):
        state = manager.start_session(marathon_config)
        # marathon_config.question_count = 3
        for _ in range(3):
            manager.submit_answer(state, state.current_question.correct_answer)
        assert state.is_complete is True
        assert state.current_question is None

    def test_sprint_ends_when_duration_elapsed(self, manager):
        config = SessionConfig(
            mode_type="sprint",
            category="arithmetic",
            difficulty="easy",
            duration_seconds=0,  # ends after first answer
        )
        state = manager.start_session(config)
        manager.submit_answer(state, state.current_question.correct_answer)
        assert state.is_complete is True

    def test_sprint_continues_within_duration(self, manager):
        config = SessionConfig(
            mode_type="sprint",
            category="arithmetic",
            difficulty="easy",
            duration_seconds=120,
        )
        state = manager.start_session(config)
        manager.submit_answer(state, state.current_question.correct_answer)
        assert state.is_complete is False

    def test_targeted_default_25_questions(self, manager):
        # `question_count=None` → falls back to 25.
        config = SessionConfig(
            mode_type="targeted",
            category="arithmetic",
            difficulty="easy",
        )
        state = manager.start_session(config)
        # We won't churn through 25 — just verify check_session_end
        # uses the default budget.
        assert manager.check_session_end(state) is False
        # Manually pad questions_answered to 25 and re-check.
        state.questions_answered = [None] * 25
        assert manager.check_session_end(state) is True

    def test_targeted_honours_explicit_count(self, manager):
        config = SessionConfig(
            mode_type="targeted",
            category="arithmetic",
            difficulty="easy",
            question_count=5,
        )
        state = manager.start_session(config)
        state.questions_answered = [None] * 5
        assert manager.check_session_end(state) is True


# ---------------------------------------------------------------------------
# Persistence — was_skipped round-trips into the DB.
# ---------------------------------------------------------------------------


class TestPersistence:

    def test_end_session_persists_was_skipped(self, manager, marathon_config, db):
        state = manager.start_session(marathon_config)
        # Question 1: correct. Question 2: skipped. Question 3: wrong.
        manager.submit_answer(state, state.current_question.correct_answer)
        manager.submit_answer(state, "skip", was_skipped=True)
        manager.submit_answer(state, "definitely-wrong")
        assert state.is_complete is True

        summary = manager.end_session(state)
        assert summary.session_id is not None

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_answer, is_correct, was_skipped FROM questions_answered "
            "WHERE session_id = ? ORDER BY id",
            (summary.session_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 3
        # Row 0: correct.
        assert rows[0]["is_correct"] == 1
        assert rows[0]["was_skipped"] == 0
        # Row 1: skipped.
        assert rows[1]["is_correct"] == 0
        assert rows[1]["was_skipped"] == 1
        # Row 2: incorrect attempt.
        assert rows[2]["is_correct"] == 0
        assert rows[2]["was_skipped"] == 0

    def test_end_session_with_no_questions_returns_zero_summary(self, manager, marathon_config):
        # Batch B: 0-answer abandons return a zeroed SessionSummary (and
        # persist it) rather than raising, so the UI's quit-on-empty path
        # doesn't crash.
        state = manager.start_session(marathon_config)
        summary = manager.end_session(state)
        assert summary.total_questions == 0
        assert summary.correct_answers == 0
        assert summary.total_score == 0
        assert summary.results == []
