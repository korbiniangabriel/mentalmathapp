"""Exhaustive tests for `AnswerValidator`.

The validator is the single most failure-prone module in the codebase
because every generator funnels through it. These tests exercise:

- Exact string match (case-insensitive).
- Numeric tolerance (1% relative for |answer| > 10, 0.1 absolute for ≤10).
- Percentage extraction across "15", "15%", "0.15".
- Fraction parsing within decimal tolerance.
- Comma-stripped, whitespace-stripped numerics.
- Empty / None / whitespace-only rejection.
- Iteration over `acceptable_answers`.
- Edge cases: scientific notation, negatives, trailing zeros.
"""
from __future__ import annotations

import pytest

from src.game_logic.validator import AnswerValidator
from src.models.question import Question


def _q(correct: str, *, acceptable=None, qtype: str = "addition", category: str = "arithmetic") -> Question:
    """Build a `Question` with the minimum fields required by the validator."""
    return Question(
        question_type=qtype,
        category=category,
        difficulty="easy",
        question_text="<test>",
        correct_answer=correct,
        acceptable_answers=list(acceptable) if acceptable is not None else [],
    )


class TestExactMatch:
    """String-equality (case-insensitive) hits the fast path."""

    @pytest.mark.parametrize(
        "user, correct, expected",
        [
            ("5", "5", True),
            ("FIVE", "five", True),
            ("Five", "FIVE", True),
            ("hello", "hello", True),
            ("hello", "world", False),
            ("5", "6", False),
        ],
    )
    def test_exact_match(self, user, correct, expected):
        assert AnswerValidator.validate(user, _q(correct)) is expected


class TestNumericTolerance:
    """Boundaries for the 1%-relative / 0.1-absolute split at |answer| == 10."""

    # Small-number absolute tolerance (|correct| <= 10): < 0.1.
    def test_small_number_just_passes(self):
        # 0.099 < 0.1 → accepted
        assert AnswerValidator.validate("5.099", _q("5")) is True

    def test_small_number_just_fails(self):
        # 0.10001 not strictly < 0.1 → rejected via numeric path; but exact
        # string compare also fails, so overall False.
        assert AnswerValidator.validate("5.11", _q("5")) is False

    def test_small_number_negative_diff(self):
        assert AnswerValidator.validate("4.95", _q("5")) is True
        assert AnswerValidator.validate("4.85", _q("5")) is False

    # Large-number relative tolerance (|correct| > 10): < 1%.
    def test_large_number_just_passes(self):
        # 1% of 1000 == 10. 1009 / 1000 → 0.9% → accepted.
        assert AnswerValidator.validate("1009", _q("1000")) is True

    def test_large_number_just_fails(self):
        # 11 / 1000 → 1.1% → rejected.
        assert AnswerValidator.validate("1011", _q("1000")) is False

    def test_boundary_exactly_ten(self):
        # |correct| == 10 → falls into the absolute branch (`> 10` is strict).
        assert AnswerValidator.validate("10.05", _q("10")) is True
        assert AnswerValidator.validate("10.2", _q("10")) is False


class TestPercentageExtraction:
    """`15` ≡ `15%` ≡ `0.15` should all match a percentage-typed answer."""

    @pytest.mark.parametrize("user", ["15", "15%", "15.0", "0.15"])
    def test_all_forms_match_15_percent(self, user):
        question = _q("15", qtype="percentage", category="percentage")
        assert AnswerValidator.validate(user, question) is True

    def test_percent_sign_with_decimal(self):
        question = _q("15", qtype="percentage", category="percentage")
        # "0.15" should be interpreted as 15% via the decimal-fraction branch.
        assert AnswerValidator.validate("0.15", question) is True

    def test_obvious_mismatch(self):
        question = _q("15", qtype="percentage", category="percentage")
        assert AnswerValidator.validate("25", question) is False


class TestFractionParsing:
    """Fraction strings are normalised via `_parse_fraction`."""

    def test_identical_fractions(self):
        assert AnswerValidator.validate("1/2", _q("1/2")) is True

    def test_equivalent_fractions(self):
        # 2/4 == 1/2 within 0.001.
        assert AnswerValidator.validate("2/4", _q("1/2")) is True

    def test_cross_format_decimal_to_fraction(self):
        # "1/3" vs "0.333" — only matches because the numeric path tries
        # comparing as floats AFTER fraction parse fails (one side has '/').
        # The validator falls through fraction logic when only ONE side has
        # '/', so this should match via... actually neither: the fraction
        # branch requires both sides to have '/'. The numeric branch tries
        # float('1/3') which raises. So this should NOT validate.
        assert AnswerValidator.validate("1/3", _q("0.333")) is False

    def test_cross_format_decimal_user_to_fraction_correct(self):
        # User submits "0.333", correct answer "1/3" → numeric branch sees
        # float("1/3") which fails. Fraction branch needs '/' on both sides.
        # Result: False.
        assert AnswerValidator.validate("0.333", _q("1/3")) is False

    def test_zero_denominator_safe(self):
        # Should not raise.
        assert AnswerValidator.validate("1/0", _q("1/2")) is False


class TestCommaAndWhitespace:
    """Validator strips whitespace and commas inside numeric coercion."""

    def test_comma_strip(self):
        assert AnswerValidator.validate("1,000", _q("1000")) is True

    def test_whitespace_strip(self):
        assert AnswerValidator.validate(" 5 ", _q("5")) is True

    def test_inner_whitespace_around_fraction(self):
        # `_parse_fraction` strips whitespace around each side of `/`.
        assert AnswerValidator.validate("1 / 2", _q("1/2")) is True


class TestEmptyAndNone:
    """Empty / whitespace-only / None inputs must be rejected."""

    @pytest.mark.parametrize("bad", ["", "   ", "\t\n"])
    def test_blank_rejected(self, bad):
        assert AnswerValidator.validate(bad, _q("5")) is False

    def test_none_rejected(self):
        # The validator's truthiness check protects against None.
        assert AnswerValidator.validate(None, _q("5")) is False


class TestAcceptableAnswersIteration:
    """Validator must walk the full `acceptable_answers` list."""

    def test_match_first(self):
        question = _q("4", acceptable=["4", "four", "IV"])
        assert AnswerValidator.validate("4", question) is True

    def test_match_middle(self):
        question = _q("4", acceptable=["four", "IV", "4"])
        assert AnswerValidator.validate("four", question) is True

    def test_match_last(self):
        question = _q("4", acceptable=["IV", "four", "4"])
        # __post_init__ ensures correct_answer is in the list.
        assert AnswerValidator.validate("4", question) is True

    def test_no_match_anywhere(self):
        question = _q("4", acceptable=["four", "IV"])
        assert AnswerValidator.validate("zzz", question) is False

    def test_correct_answer_auto_appended(self):
        # __post_init__ guarantees correct_answer is in acceptable_answers.
        question = _q("4", acceptable=["four"])
        assert "4" in question.acceptable_answers


class TestEdgeCases:
    """Quirky number formats Python's float() handles."""

    def test_scientific_notation(self):
        # "1e3" == 1000 numerically.
        assert AnswerValidator.validate("1e3", _q("1000")) is True

    def test_negative_numbers(self):
        assert AnswerValidator.validate("-5", _q("-5")) is True
        assert AnswerValidator.validate("-5.0", _q("-5")) is True
        # |correct| == 5, absolute tolerance 0.1.
        assert AnswerValidator.validate("-4.95", _q("-5")) is True
        assert AnswerValidator.validate("-5.5", _q("-5")) is False

    def test_trailing_zeros(self):
        assert AnswerValidator.validate("5.00", _q("5")) is True
        assert AnswerValidator.validate("5.0000", _q("5")) is True

    def test_plus_prefix(self):
        # Python's float() accepts a leading '+'.
        assert AnswerValidator.validate("+5", _q("5")) is True

    def test_garbage_string_rejected(self):
        assert AnswerValidator.validate("abc", _q("5")) is False

    def test_mixed_number_string(self):
        # "5 apples" can't be parsed as a number nor an exact match.
        assert AnswerValidator.validate("5 apples", _q("5")) is False
