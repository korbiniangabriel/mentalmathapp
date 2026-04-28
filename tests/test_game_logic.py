"""Tests for game logic primitives.

Covers:
- `AnswerValidator` smoke tests (the deep coverage lives in
  `test_validator.py` — this file just keeps the existing assertions
  working).
- `ScoreCalculator` (base points, combo multiplier, speed bonus,
  difficulty multiplier, and the combined `calculate_question_score`).
- `DifficultyAdjuster` (adaptive ramp-up / ramp-down behaviour and
  bounded ends).
"""
from __future__ import annotations

from datetime import datetime

import pytest

from src.game_logic.difficulty import DifficultyAdjuster
from src.game_logic.scoring import ScoreCalculator
from src.game_logic.validator import AnswerValidator
from src.models.question import Question
from src.models.session import QuestionResult


def _q(correct: str = "4", difficulty: str = "easy") -> Question:
    return Question(
        question_type="addition",
        category="arithmetic",
        difficulty=difficulty,
        question_text="2 + 2",
        correct_answer=correct,
    )


def _result(is_correct: bool, time_taken: float, difficulty: str = "easy") -> QuestionResult:
    return QuestionResult(
        question=_q(difficulty=difficulty),
        user_answer="4" if is_correct else "wrong",
        is_correct=is_correct,
        time_taken=time_taken,
        timestamp=datetime.now(),
    )


# ---------------------------------------------------------------------------
# Validator smoke (kept from the original test file).
# ---------------------------------------------------------------------------


class TestAnswerValidator:
    """Basic smoke for the validator — exhaustive coverage in test_validator.py."""

    def test_exact_match(self):
        question = _q("4")
        assert AnswerValidator.validate("4", question) is True
        assert AnswerValidator.validate("5", question) is False

    def test_numeric_tolerance(self):
        question = Question(
            question_type="percentage",
            category="percentage",
            difficulty="medium",
            question_text="What is 15% of 200?",
            correct_answer="30",
        )
        assert AnswerValidator.validate("30", question) is True
        assert AnswerValidator.validate("30.0", question) is True

    def test_percentage_formats(self):
        question = Question(
            question_type="percentage",
            category="percentage",
            difficulty="easy",
            question_text="Change?",
            correct_answer="15",
            acceptable_answers=["15", "15.0"],
        )
        assert AnswerValidator.validate("15", question) is True

    def test_fraction_parsing(self):
        question = Question(
            question_type="fractions",
            category="fractions",
            difficulty="easy",
            question_text="Convert to fraction",
            correct_answer="1/2",
        )
        assert AnswerValidator.validate("1/2", question) is True


# ---------------------------------------------------------------------------
# Scoring.
# ---------------------------------------------------------------------------


class TestScoreCalculator:

    def test_base_points(self):
        assert ScoreCalculator.calculate_base_points(True) == 100
        assert ScoreCalculator.calculate_base_points(False) == 0

    def test_combo_multiplier(self):
        assert ScoreCalculator.calculate_combo_multiplier(0) == 1.0
        assert ScoreCalculator.calculate_combo_multiplier(2) == 1.0
        assert ScoreCalculator.calculate_combo_multiplier(3) == 1.5
        assert ScoreCalculator.calculate_combo_multiplier(4) == 1.5
        assert ScoreCalculator.calculate_combo_multiplier(5) == 2.0
        assert ScoreCalculator.calculate_combo_multiplier(9) == 2.0
        assert ScoreCalculator.calculate_combo_multiplier(10) == 2.5
        assert ScoreCalculator.calculate_combo_multiplier(14) == 2.5
        assert ScoreCalculator.calculate_combo_multiplier(15) == 3.0
        assert ScoreCalculator.calculate_combo_multiplier(20) == 3.0  # capped at 3.0

    def test_speed_bonus(self):
        assert ScoreCalculator.calculate_speed_bonus(1.5) == 100
        assert ScoreCalculator.calculate_speed_bonus(2.0) == 50  # boundary: < 3
        assert ScoreCalculator.calculate_speed_bonus(2.5) == 50
        assert ScoreCalculator.calculate_speed_bonus(4.0) == 25
        assert ScoreCalculator.calculate_speed_bonus(5.0) == 0  # boundary: not < 5
        assert ScoreCalculator.calculate_speed_bonus(6.0) == 0

    def test_difficulty_multiplier(self):
        assert ScoreCalculator.calculate_difficulty_multiplier("easy") == 1.0
        assert ScoreCalculator.calculate_difficulty_multiplier("medium") == 1.5
        assert ScoreCalculator.calculate_difficulty_multiplier("hard") == 2.0
        # Batch B: 'adaptive' is dead-code fallback (generators always emit
        # easy/medium/hard); kept as a 1.0 no-inflation fallback.
        assert ScoreCalculator.calculate_difficulty_multiplier("adaptive") == 1.0
        # Unknown difficulty falls back to 1.0.
        assert ScoreCalculator.calculate_difficulty_multiplier("nonsense") == 1.0

    def test_question_score_incorrect_is_zero(self):
        assert ScoreCalculator.calculate_question_score(_result(False, 1.0), 5) == 0

    def test_question_score_combo_and_difficulty(self):
        # Correct, fast, hard, combo=10 → (100 * 2.5 + 100) * 2.0 == 700
        score = ScoreCalculator.calculate_question_score(
            _result(True, 1.5, difficulty="hard"), 10
        )
        assert score == 700


# ---------------------------------------------------------------------------
# Difficulty adjuster.
# ---------------------------------------------------------------------------


class TestDifficultyAdjuster:

    def test_initial_difficulty(self):
        assert DifficultyAdjuster.get_initial_difficulty() == "medium"

    def test_too_few_results_returns_medium(self):
        assert DifficultyAdjuster.analyze_performance([]) == "medium"
        assert DifficultyAdjuster.analyze_performance(
            [_result(True, 1.0, "easy")]
        ) == "medium"

    def test_difficulty_increases_on_high_perf(self):
        # 7 fast correct answers at 'easy' → bump to 'medium'.
        results = [_result(True, 2.0, "easy") for _ in range(7)]
        assert DifficultyAdjuster.analyze_performance(results) == "medium"

    def test_difficulty_increases_to_hard(self):
        results = [_result(True, 2.0, "medium") for _ in range(7)]
        assert DifficultyAdjuster.analyze_performance(results) == "hard"

    def test_hard_already_at_max(self):
        results = [_result(True, 2.0, "hard") for _ in range(7)]
        # Already at max → stays at hard.
        assert DifficultyAdjuster.analyze_performance(results) == "hard"

    def test_difficulty_decreases_on_low_acc(self):
        # accuracy 1/7 ≈ 14% → drop a level from current 'hard'.
        question = _q(difficulty="hard")
        results = [
            QuestionResult(
                question=question,
                user_answer="x",
                is_correct=(i == 0),
                time_taken=5.0,
                timestamp=datetime.now(),
            )
            for i in range(7)
        ]
        assert DifficultyAdjuster.analyze_performance(results) == "medium"

    def test_difficulty_holds_in_middle_band(self):
        # accuracy=4/7≈57% — lower bound 60% → drops one level. So craft
        # a 5/7 ≈ 71% case to hold.
        question = _q(difficulty="medium")
        results = [
            QuestionResult(
                question=question,
                user_answer="x",
                is_correct=(i < 5),
                time_taken=5.0,
                timestamp=datetime.now(),
            )
            for i in range(7)
        ]
        assert DifficultyAdjuster.analyze_performance(results) == "medium"

    def test_easy_is_floor(self):
        # Already easy + bad performance → stays easy.
        question = _q(difficulty="easy")
        results = [
            QuestionResult(
                question=question,
                user_answer="x",
                is_correct=False,
                time_taken=10.0,
                timestamp=datetime.now(),
            )
            for _ in range(7)
        ]
        assert DifficultyAdjuster.analyze_performance(results) == "easy"
