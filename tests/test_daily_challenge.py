"""Tests for the daily challenge logic."""

import os
import tempfile
from datetime import date

import pytest

from src.daily.challenge import DAILY_CHALLENGE_SIZE, DAILY_PREF_KEY, DailyChallenge
from src.database.db_manager import DatabaseManager


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseManager(path)
    yield db
    try:
        os.unlink(path)
    except OSError:
        pass


class TestDailyChallenge:
    def test_returns_five_questions(self):
        challenge = DailyChallenge(today=date(2026, 4, 28))
        questions = challenge.get_questions_for_today()
        assert len(questions) == DAILY_CHALLENGE_SIZE

    def test_deterministic_for_same_day(self):
        d = date(2026, 4, 28)
        a = DailyChallenge(today=d).get_questions_for_today()
        b = DailyChallenge(today=d).get_questions_for_today()
        assert [q.question_text for q in a] == [q.question_text for q in b]
        assert [q.correct_answer for q in a] == [q.correct_answer for q in b]

    def test_different_day_gives_different_questions(self):
        a = DailyChallenge(today=date(2026, 4, 28)).get_questions_for_today()
        b = DailyChallenge(today=date(2026, 4, 29)).get_questions_for_today()
        assert [q.question_text for q in a] != [q.question_text for q in b]

    def test_category_mix(self):
        challenge = DailyChallenge(today=date(2026, 4, 28))
        questions = challenge.get_questions_for_today()
        types = [q.question_type for q in questions]

        # Slot 0: arithmetic flavor (addition/subtraction/multiplication/division)
        assert types[0] in {"addition", "subtraction", "multiplication", "division"}
        # Other slots are fixed.
        assert types[1] == "percentage"
        assert types[2] == "fractions"
        assert types[3] == "ratios"
        assert types[4] == "estimation"

    def test_all_medium_difficulty(self):
        questions = DailyChallenge(today=date(2026, 4, 28)).get_questions_for_today()
        for q in questions:
            assert q.difficulty == "medium"

    def test_completion_tracking(self, temp_db):
        challenge = DailyChallenge(today=date(2026, 4, 28))
        assert challenge.has_completed_today(temp_db) is False
        challenge.mark_completed(temp_db)
        assert challenge.has_completed_today(temp_db) is True
        # Stored under the documented key.
        assert temp_db.get_user_preference(DAILY_PREF_KEY) == "2026-04-28"

    def test_completion_resets_next_day(self, temp_db):
        DailyChallenge(today=date(2026, 4, 28)).mark_completed(temp_db)
        tomorrow = DailyChallenge(today=date(2026, 4, 29))
        assert tomorrow.has_completed_today(temp_db) is False

    def test_does_not_pollute_global_random(self):
        """Daily generation must restore the global random state when done."""
        import random

        random.seed(42)
        before = random.random()
        random.seed(42)
        DailyChallenge(today=date(2026, 4, 28)).get_questions_for_today()
        after = random.random()
        assert before == after
