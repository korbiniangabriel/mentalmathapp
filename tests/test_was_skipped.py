"""Behavioral tests for the `was_skipped` column.

These tests verify the *intent* of Batch S: skipped questions should
not poison accuracy or weak-area routing. The actual `WHERE
was_skipped = 0` filters live in Batch C — until that batch lands,
the analytics paths still count skips as wrong, so the strict
"skips excluded from accuracy" assertion is marked skip with a clear
reason.

What we DO test today:
- The DB column accepts and stores `was_skipped = 1`.
- `save_question_answer` writes the value through.
- Skipped questions show up in `get_questions_by_type` (raw fetch).
- `was_skipped=False` survives a save round-trip too.

What we DON'T test until Batch C:
- `get_weak_areas` excluding skipped rows from the denominator.
- `get_performance_stats` excluding skipped rows from accuracy.
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import datetime, timedelta

import pytest

from src.database.db_manager import DatabaseManager
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


def _summary_with_mix(skipped_count: int, wrong_count: int, correct_count: int) -> SessionSummary:
    """Build a summary with a mix of correct / wrong / skipped answers."""
    config = SessionConfig(
        mode_type="marathon",
        category="arithmetic",
        difficulty="easy",
        question_count=skipped_count + wrong_count + correct_count,
    )
    base_q = Question(
        question_type="addition",
        category="arithmetic",
        difficulty="easy",
        question_text="2+2",
        correct_answer="4",
    )
    results: list[QuestionResult] = []
    base_ts = datetime.now()
    for i in range(skipped_count):
        results.append(
            QuestionResult(
                question=base_q,
                user_answer="",
                is_correct=False,
                time_taken=4.0,
                timestamp=base_ts + timedelta(seconds=i),
                was_skipped=True,
            )
        )
    for i in range(wrong_count):
        results.append(
            QuestionResult(
                question=base_q,
                user_answer="x",
                is_correct=False,
                time_taken=4.0,
                timestamp=base_ts + timedelta(seconds=skipped_count + i),
                was_skipped=False,
            )
        )
    for i in range(correct_count):
        results.append(
            QuestionResult(
                question=base_q,
                user_answer="4",
                is_correct=True,
                time_taken=4.0,
                timestamp=base_ts + timedelta(
                    seconds=skipped_count + wrong_count + i
                ),
                was_skipped=False,
            )
        )

    total = skipped_count + wrong_count + correct_count
    return SessionSummary(
        session_id=None,
        config=config,
        total_questions=total,
        correct_answers=correct_count,
        total_score=100,
        avg_time_per_question=4.0,
        duration_seconds=int(4.0 * total),
        results=results,
        timestamp=base_ts,
    )


# ---------------------------------------------------------------------------
# was_skipped survives the DB round-trip.
# ---------------------------------------------------------------------------


class TestRoundTrip:

    def test_skipped_value_persists(self, db):
        summary = _summary_with_mix(skipped_count=2, wrong_count=1, correct_count=2)
        sid = db.save_session(summary)

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT was_skipped, is_correct FROM questions_answered "
            "WHERE session_id = ? ORDER BY id",
            (sid,),
        )
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 5
        # First 2 are skipped, next 1 wrong, last 2 correct.
        assert [r["was_skipped"] for r in rows] == [1, 1, 0, 0, 0]
        assert [r["is_correct"] for r in rows] == [0, 0, 0, 1, 1]

    def test_no_skips_round_trips_zero(self, db):
        summary = _summary_with_mix(skipped_count=0, wrong_count=1, correct_count=1)
        sid = db.save_session(summary)

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT was_skipped FROM questions_answered WHERE session_id = ?",
            (sid,),
        )
        rows = cursor.fetchall()
        conn.close()
        assert all(row["was_skipped"] == 0 for row in rows)


# ---------------------------------------------------------------------------
# Skipped rows still appear in raw fetch (`get_questions_by_type`).
# ---------------------------------------------------------------------------


class TestRawFetchIncludesSkips:

    def test_get_questions_by_type_includes_skipped(self, db):
        summary = _summary_with_mix(skipped_count=2, wrong_count=0, correct_count=1)
        db.save_session(summary)
        df = db.get_questions_by_type("addition")
        assert len(df) == 3
        # Filter to was_skipped == 1 → should get 2 rows.
        assert int((df["was_skipped"] == 1).sum()) == 2


# ---------------------------------------------------------------------------
# Analytics filters — pending Batch C.
# ---------------------------------------------------------------------------


@pytest.mark.skip(
    reason=(
        "Depends on Batch C — `DatabaseManager.get_performance_stats` and "
        "`get_weak_areas` need a `WHERE was_skipped = 0` filter to "
        "exclude skipped rows from accuracy. Once Batch C lands, unskip "
        "these tests."
    )
)
class TestAnalyticsExcludesSkipped:

    def test_performance_stats_excludes_skipped(self, db):
        # 5 skipped + 0 wrong + 5 correct → with skip filter, accuracy
        # should be 100% (5/5 correct out of 5 non-skipped).
        summary = _summary_with_mix(skipped_count=5, wrong_count=0, correct_count=5)
        db.save_session(summary)

        stats = db.get_performance_stats()
        # Without filter: 5/10 = 50%. With filter: 5/5 = 100%.
        assert stats["accuracy"] == pytest.approx(100.0)

    def test_weak_areas_excludes_skipped(self, db):
        # If skips were poisoning weak-area detection, this category
        # would show <75% accuracy and be flagged. With Batch C, only
        # the real attempts (5/5 = 100%) count and it's NOT a weak
        # area.
        summary = _summary_with_mix(skipped_count=10, wrong_count=0, correct_count=5)
        db.save_session(summary)
        weak = db.get_weak_areas(threshold=0.75)
        assert "addition" not in weak
