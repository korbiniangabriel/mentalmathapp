"""Tests for `BadgeManager`.

One named test per badge condition (19 currently shipped). Each test
uses a temp-file SQLite database, plants the minimum facts needed to
satisfy the condition, then asserts `BadgeManager._check_badge_condition`
returns True. Negative tests confirm the badge is NOT awarded with
insufficient data. End-to-end `check_earned_badges` is covered for the
common path.

Notes:
- The badge manager queries the DB for many checks (`No Miss`, category
  mastery, mixed-mode mastery, hard-mode session count). Helpers below
  insert sessions / questions directly; we don't go through
  `SessionManager` because that would require generating real questions
  for every test.
- "In Form" / "Hot Streak" are mentioned in Batch C — the codebase
  doesn't currently define those badges, so the test for them is marked
  skip.
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import date, datetime, timedelta
from typing import Iterable

import pytest

from src.database.db_manager import DatabaseManager
from src.gamification.badge_manager import BadgeManager
from src.models.question import Question
from src.models.session import (
    QuestionResult,
    SessionConfig,
    SessionSummary,
)


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
def badge_mgr(db):
    return BadgeManager(db)


# ---------------------------------------------------------------------------
# Test helpers — insert synthetic sessions / questions cheaply.
# ---------------------------------------------------------------------------


def _make_summary(
    *,
    mode_type: str = "marathon",
    category: str = "mixed",
    difficulty: str = "medium",
    total_questions: int = 10,
    correct: int = 10,
    avg_time: float = 4.0,
    score: int = 100,
    question_type: str = "addition",
    timestamp: datetime | None = None,
    skip_count: int = 0,
) -> SessionSummary:
    timestamp = timestamp or datetime.now()
    config = SessionConfig(
        mode_type=mode_type,
        category=category,
        difficulty=difficulty,
        question_count=total_questions if mode_type == "marathon" else None,
        duration_seconds=120 if mode_type == "sprint" else None,
    )
    base_q = Question(
        question_type=question_type,
        category=category if category != "mixed" else question_type,
        difficulty=difficulty,
        question_text="Q",
        correct_answer="0",
    )
    results: list[QuestionResult] = []
    for i in range(total_questions):
        is_skip = i < skip_count
        is_correct = (not is_skip) and (i < correct + skip_count)
        results.append(
            QuestionResult(
                question=base_q,
                user_answer="0" if is_correct else "x",
                is_correct=is_correct,
                time_taken=avg_time,
                timestamp=timestamp + timedelta(seconds=i),
                was_skipped=is_skip,
            )
        )
    return SessionSummary(
        session_id=None,
        config=config,
        total_questions=total_questions,
        correct_answers=correct,
        total_score=score,
        avg_time_per_question=avg_time,
        duration_seconds=int(avg_time * total_questions),
        results=results,
        timestamp=timestamp,
    )


def _save(db: DatabaseManager, summary: SessionSummary) -> int:
    return db.save_session(summary)


def _seed_questions(
    db: DatabaseManager,
    *,
    question_type: str,
    correct: int,
    incorrect: int = 0,
    fast: bool = False,
    session_id: int | None = None,
):
    """Insert raw question rows into an existing or new session."""
    conn = db.get_connection()
    cursor = conn.cursor()

    if session_id is None:
        cursor.execute(
            """
            INSERT INTO sessions
                (timestamp, mode_type, category, difficulty,
                 duration_seconds, total_questions, correct_answers,
                 total_score, avg_time_per_question, completed)
            VALUES (?, 'marathon', 'mixed', 'medium', 60, ?, ?, 0, 4.0, 1)
            """,
            (datetime.now(), correct + incorrect, correct),
        )
        session_id = cursor.lastrowid

    base = datetime.now()
    for i in range(correct):
        cursor.execute(
            """
            INSERT INTO questions_answered
                (session_id, question_type, difficulty, question_text,
                 correct_answer, user_answer, is_correct, was_skipped,
                 time_taken_seconds, timestamp)
            VALUES (?, ?, 'medium', 'q', '0', '0', 1, 0, ?, ?)
            """,
            (
                session_id,
                question_type,
                1.5 if fast else 4.0,
                base + timedelta(seconds=i),
            ),
        )
    for i in range(incorrect):
        cursor.execute(
            """
            INSERT INTO questions_answered
                (session_id, question_type, difficulty, question_text,
                 correct_answer, user_answer, is_correct, was_skipped,
                 time_taken_seconds, timestamp)
            VALUES (?, ?, 'medium', 'q', '0', 'x', 0, 0, ?, ?)
            """,
            (
                session_id,
                question_type,
                4.0,
                base + timedelta(seconds=correct + i),
            ),
        )
    conn.commit()
    conn.close()
    return session_id


def _seed_streak(db: DatabaseManager, days: int):
    """Mark the past `days` consecutive days (incl. today) as practiced."""
    conn = db.get_connection()
    cursor = conn.cursor()
    today = date.today()
    for offset in range(days):
        d = today - timedelta(days=offset)
        cursor.execute(
            """
            INSERT INTO daily_streaks (date, sessions_completed)
            VALUES (?, 1)
            ON CONFLICT(date) DO UPDATE SET sessions_completed = sessions_completed + 1
            """,
            (d,),
        )
    conn.commit()
    conn.close()


def _badge(badge_mgr: BadgeManager, name: str):
    for b in badge_mgr.get_all_badges():
        if b.badge_name == name:
            return b
    raise AssertionError(f"badge {name!r} not found in DB")


# ---------------------------------------------------------------------------
# Milestone Badges
# ---------------------------------------------------------------------------


class TestMilestoneBadges:

    def test_first_steps_awarded_after_one_session(self, db, badge_mgr):
        summary = _make_summary(total_questions=1, correct=1)
        _save(db, summary)
        b = _badge(badge_mgr, "First Steps")
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(b, summary, stats) is True

    def test_first_steps_not_awarded_with_no_sessions(self, db, badge_mgr):
        # Build a summary that hasn't been saved.
        summary = _make_summary(total_questions=1, correct=1)
        b = _badge(badge_mgr, "First Steps")
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(b, summary, stats) is False

    def test_century_club_at_100(self, db, badge_mgr):
        summary = _make_summary(total_questions=100, correct=100)
        _save(db, summary)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Century Club"), summary, stats) is True

    def test_century_club_negative(self, db, badge_mgr):
        summary = _make_summary(total_questions=10, correct=10)
        _save(db, summary)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Century Club"), summary, stats) is False

    def test_veteran_at_1000(self, db, badge_mgr):
        # 100 sessions × 10 questions each.
        for _ in range(100):
            _save(db, _make_summary(total_questions=10, correct=10))
        stats = db.get_performance_stats()
        summary = _make_summary(total_questions=10, correct=10)
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Veteran"), summary, stats) is True

    def test_veteran_negative(self, db, badge_mgr):
        summary = _make_summary(total_questions=100, correct=100)
        _save(db, summary)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Veteran"), summary, stats) is False

    def test_marathon_finisher_awarded_on_marathon_session(self, db, badge_mgr):
        summary = _make_summary(mode_type="marathon", total_questions=10, correct=10)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Marathon Finisher"), summary, stats) is True

    def test_marathon_finisher_not_awarded_on_sprint(self, db, badge_mgr):
        summary = _make_summary(mode_type="sprint", total_questions=10, correct=10)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Marathon Finisher"), summary, stats) is False


# ---------------------------------------------------------------------------
# Performance Badges
# ---------------------------------------------------------------------------


class TestPerformanceBadges:

    def test_perfectionist_awarded_perfect_session(self, db, badge_mgr):
        summary = _make_summary(total_questions=10, correct=10)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Perfectionist"), summary, stats) is True

    def test_perfectionist_negative_under_10_questions(self, db, badge_mgr):
        summary = _make_summary(total_questions=5, correct=5)
        stats = db.get_performance_stats()
        # Still 100% but not enough volume.
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Perfectionist"), summary, stats) is False

    def test_perfectionist_negative_imperfect(self, db, badge_mgr):
        summary = _make_summary(total_questions=10, correct=9)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Perfectionist"), summary, stats) is False

    def test_speed_demon_awarded(self, db, badge_mgr):
        # 10 correct + fast (<3s) answers in one session.
        summary = _make_summary(total_questions=10, correct=10, avg_time=2.0)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Speed Demon"), summary, stats) is True

    def test_speed_demon_negative_too_slow(self, db, badge_mgr):
        summary = _make_summary(total_questions=10, correct=10, avg_time=4.0)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Speed Demon"), summary, stats) is False

    def test_lightning_round_awarded(self, db, badge_mgr):
        summary = _make_summary(total_questions=10, correct=8, avg_time=2.5)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Lightning Round"), summary, stats) is True

    def test_lightning_round_negative(self, db, badge_mgr):
        summary = _make_summary(total_questions=10, correct=10, avg_time=3.5)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Lightning Round"), summary, stats) is False

    def test_no_miss_awarded(self, db, badge_mgr):
        # Plant 50 correct rows in a single session.
        _seed_questions(db, question_type="addition", correct=50)
        summary = _make_summary(total_questions=10, correct=10)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "No Miss"), summary, stats) is True

    def test_no_miss_negative_with_one_wrong_recent(self, db, badge_mgr):
        # 49 correct, then 1 wrong as the most recent → fails.
        _seed_questions(db, question_type="addition", correct=49, incorrect=1)
        summary = _make_summary(total_questions=10, correct=10)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "No Miss"), summary, stats) is False

    def test_no_miss_negative_with_too_few_questions(self, db, badge_mgr):
        _seed_questions(db, question_type="addition", correct=49)
        summary = _make_summary(total_questions=10, correct=10)
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "No Miss"), summary, stats) is False


# ---------------------------------------------------------------------------
# Streak Badges
# ---------------------------------------------------------------------------


class TestStreakBadges:

    def test_consistent_3_day(self, db, badge_mgr):
        _seed_streak(db, 3)
        summary = _make_summary()
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Consistent"), summary, stats) is True

    def test_consistent_negative(self, db, badge_mgr):
        _seed_streak(db, 2)
        summary = _make_summary()
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Consistent"), summary, stats) is False

    def test_week_warrior_7_day(self, db, badge_mgr):
        _seed_streak(db, 7)
        summary = _make_summary()
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Week Warrior"), summary, stats) is True

    def test_week_warrior_negative(self, db, badge_mgr):
        _seed_streak(db, 6)
        summary = _make_summary()
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Week Warrior"), summary, stats) is False

    def test_month_master_30_day(self, db, badge_mgr):
        _seed_streak(db, 30)
        summary = _make_summary()
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Month Master"), summary, stats) is True

    def test_month_master_negative(self, db, badge_mgr):
        _seed_streak(db, 14)
        summary = _make_summary()
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Month Master"), summary, stats) is False


# ---------------------------------------------------------------------------
# Category Mastery Badges
# ---------------------------------------------------------------------------


class TestCategoryMastery:

    @pytest.mark.parametrize(
        "badge_name, question_type",
        [
            ("Arithmetic Ace", "addition"),
            ("Percentage Pro", "percentage"),
            ("Fraction Master", "fractions"),
            ("Ratio Expert", "ratios"),
            ("Compound Champion", "compound"),
            ("Estimation Guru", "estimation"),
        ],
    )
    def test_mastery_awarded(self, db, badge_mgr, badge_name, question_type):
        # 50 questions in category, 48 correct → 96% accuracy (>= 95%).
        _seed_questions(db, question_type=question_type, correct=48, incorrect=2)
        summary = _make_summary()
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, badge_name), summary, stats) is True

    def test_mastery_negative_too_few_questions(self, db, badge_mgr):
        # 30 correct < 50 minimum.
        _seed_questions(db, question_type="addition", correct=30)
        summary = _make_summary()
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Arithmetic Ace"), summary, stats) is False

    def test_mastery_negative_low_accuracy(self, db, badge_mgr):
        # 50 questions but 90% accuracy < 95%.
        _seed_questions(db, question_type="addition", correct=45, incorrect=5)
        summary = _make_summary()
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Arithmetic Ace"), summary, stats) is False


# ---------------------------------------------------------------------------
# Challenge Badges
# ---------------------------------------------------------------------------


class TestChallengeBadges:

    def test_hard_mode_hero_at_10(self, db, badge_mgr):
        for _ in range(10):
            _save(db, _make_summary(difficulty="hard", total_questions=5, correct=5))
        summary = _make_summary(difficulty="hard")
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Hard Mode Hero"), summary, stats) is True

    def test_hard_mode_hero_negative(self, db, badge_mgr):
        for _ in range(5):
            _save(db, _make_summary(difficulty="hard", total_questions=5, correct=5))
        summary = _make_summary(difficulty="hard")
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Hard Mode Hero"), summary, stats) is False

    def test_mixed_master_awarded(self, db, badge_mgr):
        # Plant 5 mixed-mode sessions of 10 questions, all correct → 100%
        # over 50.
        for _ in range(5):
            _save(db, _make_summary(category="mixed", total_questions=10, correct=10))
        summary = _make_summary(category="mixed")
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Mixed Master"), summary, stats) is True

    def test_mixed_master_negative_low_accuracy(self, db, badge_mgr):
        # 50 mixed questions, 40 correct → 80% < 90%.
        for _ in range(5):
            _save(db, _make_summary(category="mixed", total_questions=10, correct=8))
        summary = _make_summary(category="mixed")
        stats = db.get_performance_stats()
        assert badge_mgr._check_badge_condition(_badge(badge_mgr, "Mixed Master"), summary, stats) is False


# ---------------------------------------------------------------------------
# End-to-end: check_earned_badges actually awards.
# ---------------------------------------------------------------------------


class TestCheckEarnedBadges:

    def test_first_steps_end_to_end(self, db, badge_mgr):
        summary = _make_summary(total_questions=1, correct=1)
        _save(db, summary)
        newly_earned = badge_mgr.check_earned_badges(summary)
        names = {b.badge_name for b in newly_earned}
        assert "First Steps" in names

    def test_already_earned_not_re_awarded(self, db, badge_mgr):
        summary = _make_summary(total_questions=1, correct=1)
        _save(db, summary)
        first_pass = badge_mgr.check_earned_badges(summary)
        names = {b.badge_name for b in first_pass}
        assert "First Steps" in names

        # Run again with same conditions — should not re-award.
        second_pass = badge_mgr.check_earned_badges(summary)
        assert all(b.badge_name != "First Steps" for b in second_pass)


# ---------------------------------------------------------------------------
# Batch C extension badges
# ---------------------------------------------------------------------------


class TestBatchCBadges:
    """Recent-form badges added by Batch C."""

    def test_in_form_awarded(self, db, badge_mgr):
        # 50 non-skipped attempts at 100% — comfortably clears the 90% bar.
        summary = _make_summary(total_questions=50, correct=50)
        _save(db, summary)
        # Re-instantiate so it sees the persisted data and the Batch C-
        # registered badge rows.
        badge_mgr = BadgeManager(db)
        earned = {b.badge_name for b in badge_mgr.check_earned_badges(summary)}
        assert "In Form" in earned

    def test_in_form_not_awarded_below_threshold(self, db, badge_mgr):
        # 50 attempts at 80% — under the 90% bar, no In Form.
        summary = _make_summary(total_questions=50, correct=40)
        _save(db, summary)
        badge_mgr = BadgeManager(db)
        earned = {b.badge_name for b in badge_mgr.check_earned_badges(summary)}
        assert "In Form" not in earned

    def test_hot_streak_awarded(self, db, badge_mgr):
        # 12 correct in a row in one session, no skips: scans summary.results
        # and finds the run.
        summary = _make_summary(total_questions=12, correct=12)
        _save(db, summary)
        badge_mgr = BadgeManager(db)
        earned = {b.badge_name for b in badge_mgr.check_earned_badges(summary)}
        assert "Hot Streak" in earned

    def test_hot_streak_not_awarded_when_run_too_short(self, db, badge_mgr):
        # 9 correct in a row is one short.
        summary = _make_summary(total_questions=9, correct=9)
        _save(db, summary)
        badge_mgr = BadgeManager(db)
        earned = {b.badge_name for b in badge_mgr.check_earned_badges(summary)}
        assert "Hot Streak" not in earned
