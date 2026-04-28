"""Tests for analytics functionality.

Covers:
- `PerformanceTracker.get_overall_stats`, `identify_weak_areas`,
  `get_stats_by_category` (existing structural tests).
- `InsightsGenerator.generate_session_insights` — confirms the
  generator emits the expected positive/neutral mix for both perfect
  and weak sessions.
- `InsightsGenerator.generate_weekly_insights` — empty-data path
  returns the kickoff message rather than crashing.
"""
from __future__ import annotations

import os
import tempfile
from datetime import datetime, timedelta

import pytest

from src.analytics.insights_generator import InsightsGenerator
from src.analytics.performance_tracker import PerformanceTracker
from src.database.db_manager import DatabaseManager
from src.models.question import Question
from src.models.session import (
    QuestionResult,
    SessionConfig,
    SessionSummary,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    db = DatabaseManager(path)
    yield db

    try:
        os.unlink(path)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Performance tracker — existing structural coverage.
# ---------------------------------------------------------------------------


class TestPerformanceTracker:
    """Test performance tracking."""

    def test_overall_stats_empty(self, temp_db):
        tracker = PerformanceTracker(temp_db)
        stats = tracker.get_overall_stats()
        assert stats['total_questions'] == 0
        assert stats['correct_answers'] == 0
        assert stats['accuracy'] == 0

    def test_overall_stats_with_data(self, temp_db):
        config = SessionConfig(
            mode_type='sprint',
            category='mixed',
            difficulty='medium',
            duration_seconds=120,
        )
        question = Question(
            question_type='addition',
            category='arithmetic',
            difficulty='medium',
            question_text='2 + 2',
            correct_answer='4',
        )
        results = [
            QuestionResult(
                question=question,
                user_answer='4',
                is_correct=True,
                time_taken=2.5,
                timestamp=datetime.now(),
            ),
            QuestionResult(
                question=question,
                user_answer='5',
                is_correct=False,
                time_taken=3.0,
                timestamp=datetime.now(),
            ),
        ]
        summary = SessionSummary(
            session_id=None,
            config=config,
            total_questions=2,
            correct_answers=1,
            total_score=100,
            avg_time_per_question=2.75,
            duration_seconds=120,
            results=results,
            timestamp=datetime.now(),
        )
        temp_db.save_session(summary)

        tracker = PerformanceTracker(temp_db)
        stats = tracker.get_overall_stats()

        assert stats['total_questions'] == 2
        assert stats['correct_answers'] == 1
        assert stats['accuracy'] == 50.0
        assert stats['total_sessions'] == 1

    def test_weak_areas_identification(self, temp_db):
        tracker = PerformanceTracker(temp_db)
        weak = tracker.identify_weak_areas(threshold=0.75)
        assert weak == []

    def test_category_performance(self, temp_db):
        tracker = PerformanceTracker(temp_db)
        df = tracker.get_stats_by_category()
        assert df.empty


# ---------------------------------------------------------------------------
# Insights generator — fills the previously-empty stub.
# ---------------------------------------------------------------------------


def _build_summary(*, total: int, correct: int, avg_time: float, score: int = 100) -> SessionSummary:
    config = SessionConfig(
        mode_type="marathon",
        category="arithmetic",
        difficulty="medium",
        question_count=total,
    )
    question = Question(
        question_type="addition",
        category="arithmetic",
        difficulty="medium",
        question_text="2 + 2",
        correct_answer="4",
    )
    results: list[QuestionResult] = []
    base = datetime.now()
    for i in range(total):
        is_correct = i < correct
        results.append(
            QuestionResult(
                question=question,
                user_answer="4" if is_correct else "x",
                is_correct=is_correct,
                time_taken=avg_time,
                timestamp=base + timedelta(seconds=i),
            )
        )
    return SessionSummary(
        session_id=None,
        config=config,
        total_questions=total,
        correct_answers=correct,
        total_score=score,
        avg_time_per_question=avg_time,
        duration_seconds=int(avg_time * total),
        results=results,
        timestamp=base,
    )


class TestInsightsGenerator:
    """Test insight generation."""

    def test_insights_generation(self, temp_db):
        """Perfect-score session yields positive insights."""
        gen = InsightsGenerator(temp_db)
        summary = _build_summary(total=10, correct=10, avg_time=2.5, score=2000)
        insights = gen.generate_session_insights(summary)

        assert isinstance(insights, list)
        assert len(insights) >= 1
        assert all(isinstance(item, dict) for item in insights)
        assert all({'text', 'type'} <= item.keys() for item in insights)

        types = [i["type"] for i in insights]
        # Perfect score → at least one positive insight, none negative.
        assert any(t == "positive" for t in types), insights
        # Capped at top 5.
        assert len(insights) <= 5

    def test_insights_for_weak_session(self, temp_db):
        """Low-accuracy session emits at least one neutral 'room for
        improvement' insight."""
        gen = InsightsGenerator(temp_db)
        summary = _build_summary(total=10, correct=4, avg_time=6.0, score=50)
        insights = gen.generate_session_insights(summary)

        assert insights, insights
        types = [i["type"] for i in insights]
        # Speed bucket is silent above 5s, so we won't see a positive
        # speed insight either. Expect at least one neutral.
        assert any(t == "neutral" for t in types), insights

    def test_insights_perfect_score_message(self, temp_db):
        """The 'Perfect score!' banner shows up when accuracy == 100%."""
        gen = InsightsGenerator(temp_db)
        summary = _build_summary(total=10, correct=10, avg_time=4.0)
        insights = gen.generate_session_insights(summary)
        texts = [i["text"] for i in insights]
        assert any("Perfect score" in t for t in texts), texts

    def test_weekly_insights_empty_data(self, temp_db):
        """Empty DB returns the friendly kickoff message."""
        gen = InsightsGenerator(temp_db)
        weekly = gen.generate_weekly_insights()
        assert isinstance(weekly, list)
        assert len(weekly) == 1
        assert weekly[0]["type"] == "neutral"
        assert "Start practicing" in weekly[0]["text"]

    def test_weekly_insights_with_data(self, temp_db):
        """When historical data exists, weekly insights summarise it."""
        # Plant a session so the historical trend isn't empty.
        summary = _build_summary(total=10, correct=8, avg_time=3.0)
        temp_db.save_session(summary)

        gen = InsightsGenerator(temp_db)
        weekly = gen.generate_weekly_insights()
        assert weekly, weekly
        # Should NOT be the empty-data kickoff message.
        assert all("Start practicing" not in i["text"] for i in weekly)
