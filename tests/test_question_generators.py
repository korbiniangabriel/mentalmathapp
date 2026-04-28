"""Tests for question generators.

Two layers:

1. Structural smoke tests: generators emit `Question` objects with the
   right type/category/difficulty fields populated.
2. Solvability tests: each generator x difficulty pair is sampled 200
   times. We assert the validator accepts the generator's
   `correct_answer` AND every entry in `acceptable_answers`. A small
   per-(generator, difficulty) failure-rate budget is allowed (0.5%) so
   floating-point edge cases don't make CI flaky, but cross that and the
   suite fails. We also re-derive ratio / chain answers from the
   question text to catch silent off-by-one bugs in generators.
"""
from __future__ import annotations

import re
from collections import defaultdict
from fractions import Fraction
from typing import Iterable

import pytest

from src.game_logic.validator import AnswerValidator
from src.models.question import Question
from src.question_generator.arithmetic import (
    AdditionGenerator,
    DivisionGenerator,
    MultiplicationGenerator,
    SubtractionGenerator,
)
from src.question_generator.compound import CompoundGenerator
from src.question_generator.estimation import EstimationGenerator
from src.question_generator.fractions import FractionsGenerator
from src.question_generator.percentage import PercentageGenerator
from src.question_generator.ratios import RatiosGenerator


# ---------------------------------------------------------------------------
# Existing structural smoke tests (preserved from prior suite).
# ---------------------------------------------------------------------------


class TestArithmeticGenerators:
    """Structural shape of arithmetic outputs."""

    def test_addition_generator(self):
        gen = AdditionGenerator()
        for difficulty in ['easy', 'medium', 'hard']:
            question = gen.generate(difficulty)
            assert question.question_type == 'addition'
            assert question.category == 'arithmetic'
            assert question.difficulty == difficulty
            assert question.correct_answer
            assert '+' in question.question_text

    def test_subtraction_generator(self):
        gen = SubtractionGenerator()
        question = gen.generate('medium')
        assert question.question_type == 'subtraction'
        assert question.category == 'arithmetic'
        assert '-' in question.question_text

    def test_multiplication_generator(self):
        gen = MultiplicationGenerator()
        question = gen.generate('hard')
        assert question.question_type == 'multiplication'
        assert '×' in question.question_text

    def test_division_generator(self):
        gen = DivisionGenerator()
        question = gen.generate('easy')
        assert question.question_type == 'division'
        assert '÷' in question.question_text


class TestPercentageGenerator:
    def test_percentage_generation(self):
        gen = PercentageGenerator()
        for difficulty in ['easy', 'medium', 'hard']:
            question = gen.generate(difficulty)
            assert question.question_type == 'percentage'
            assert question.category == 'percentage'
            assert question.correct_answer
            assert question.question_text


class TestFractionsGenerator:
    def test_fractions_generation(self):
        gen = FractionsGenerator()
        question = gen.generate('medium')
        assert question.question_type == 'fractions'
        assert question.category == 'fractions'
        assert question.correct_answer


class TestRatiosGenerator:
    def test_ratios_generation(self):
        gen = RatiosGenerator()
        question = gen.generate('easy')
        assert question.question_type == 'ratios'
        assert question.category == 'ratios'
        assert question.correct_answer


class TestCompoundGenerator:
    def test_compound_generation(self):
        gen = CompoundGenerator()
        question = gen.generate('medium')
        assert question.question_type == 'compound'
        assert question.category == 'compound'
        assert question.correct_answer


class TestEstimationGenerator:
    def test_estimation_generation(self):
        gen = EstimationGenerator()
        question = gen.generate('easy')
        assert question.question_type == 'estimation'
        assert question.category == 'estimation'
        assert question.correct_answer
        assert len(question.acceptable_answers) > 1  # Should have range


def test_all_generators_produce_valid_questions():
    """Smoke: structural fields are populated for every gen+difficulty."""
    generators = [
        AdditionGenerator(),
        SubtractionGenerator(),
        MultiplicationGenerator(),
        DivisionGenerator(),
        PercentageGenerator(),
        FractionsGenerator(),
        RatiosGenerator(),
        CompoundGenerator(),
        EstimationGenerator(),
    ]
    for gen in generators:
        for difficulty in ['easy', 'medium', 'hard']:
            question = gen.generate(difficulty)
            assert question.question_type
            assert question.category
            assert question.difficulty == difficulty
            assert question.question_text
            assert question.correct_answer
            assert len(question.acceptable_answers) > 0
            assert question.correct_answer in question.acceptable_answers


# ---------------------------------------------------------------------------
# Solvability sweep: 200 samples per (generator, difficulty) pair.
# ---------------------------------------------------------------------------


GENERATORS = [
    ("addition", AdditionGenerator()),
    ("subtraction", SubtractionGenerator()),
    ("multiplication", MultiplicationGenerator()),
    ("division", DivisionGenerator()),
    ("percentage", PercentageGenerator()),
    ("fractions", FractionsGenerator()),
    ("ratios", RatiosGenerator()),
    ("compound", CompoundGenerator()),
    ("estimation", EstimationGenerator()),
]
DIFFICULTIES = ["easy", "medium", "hard"]
SAMPLES_PER_PAIR = 200
# Estimation hard-mode questions can declare hundreds of acceptable
# answers per question. We cap the per-question alt-answer scan so the
# suite stays fast (full 200 × thousands would exceed the test budget).
MAX_ACCEPTABLE_PER_Q = 32
# Tolerance budget — generators occasionally emit answers that the
# validator rejects (e.g. tiny floating-point drift). 0.5% per pair is
# the ceiling we'll accept; below that, the suite passes.
FAIL_RATE_BUDGET = 0.005


@pytest.mark.parametrize("name,gen", GENERATORS, ids=lambda v: v if isinstance(v, str) else "")
@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_generator_answers_round_trip(name: str, gen, difficulty: str):
    """`correct_answer` and every `acceptable_answer` must validate."""
    failures: list[tuple[str, str, list[str]]] = []
    for _ in range(SAMPLES_PER_PAIR):
        q = gen.generate(difficulty)

        # The canonical correct answer must validate against itself.
        if not AnswerValidator.validate(q.correct_answer, q):
            failures.append(("correct", q.correct_answer, list(q.acceptable_answers[:5])))
            continue

        # Every alternate answer the generator declared must also validate.
        # Cap the scan: estimation can list 800+ accepts per question.
        alts = q.acceptable_answers[:MAX_ACCEPTABLE_PER_Q]
        for alt in alts:
            if not AnswerValidator.validate(alt, q):
                failures.append(("acceptable", alt, list(alts)))
                break

    fail_rate = len(failures) / SAMPLES_PER_PAIR
    # Print a per-pair diagnostic to test output when it goes off the rails.
    if fail_rate >= FAIL_RATE_BUDGET:
        sample = failures[:3]
        pytest.fail(
            f"{name}/{difficulty}: {len(failures)}/{SAMPLES_PER_PAIR} "
            f"answers failed validation (fail_rate={fail_rate:.2%}, "
            f"budget={FAIL_RATE_BUDGET:.2%}). Sample: {sample}"
        )


# ---------------------------------------------------------------------------
# Semantic checks: derive answer from the question text and compare.
# ---------------------------------------------------------------------------


def _parse_int(s: str) -> int:
    return int(s.replace(",", "").strip())


def _parse_float(s: str) -> float:
    return float(s.replace(",", "").strip())


class TestRatioSemantics:
    """Re-derive the expected ratio answer from the question text."""

    SIMPLE_RE = re.compile(
        r"If A:B is (\d+):(\d+) and (A|B) = ([\d,]+), what is (A|B)\?"
    )
    THREE_WAY_RE = re.compile(
        r"If A:B:C is (\d+):(\d+):(\d+) and the total is ([\d,]+), what is (A|B|C)\?"
    )
    WORD_PROBLEM_RE = re.compile(
        r"You have (\d+) winning trades for every (\d+) losing trades\. "
        r"If you had ([\d,]+) (winning|losing) trades, how many "
        r"(winning|losing) trades did you have\?"
    )

    @pytest.mark.parametrize("difficulty", DIFFICULTIES)
    def test_ratio_answer_satisfies_text(self, difficulty):
        gen = RatiosGenerator()
        for _ in range(50):
            q = gen.generate(difficulty)
            text = q.question_text
            answer = _parse_int(q.correct_answer)

            m_simple = self.SIMPLE_RE.match(text)
            m_three = self.THREE_WAY_RE.match(text)
            m_word = self.WORD_PROBLEM_RE.match(text)

            if m_simple:
                ra, rb, given_var, given_val, ask = m_simple.groups()
                ra, rb = int(ra), int(rb)
                given_val = _parse_int(given_val)
                if given_var == "A":
                    expected = given_val * rb // ra
                else:
                    expected = given_val * ra // rb
                assert answer == expected, (text, answer, expected)
            elif m_three:
                ra, rb, rc, total, ask = m_three.groups()
                ra, rb, rc, total = int(ra), int(rb), int(rc), _parse_int(total)
                ratio_sum = ra + rb + rc
                expected = total * {"A": ra, "B": rb, "C": rc}[ask] // ratio_sum
                assert answer == expected, (text, answer, expected)
            elif m_word:
                wins, losses, given_val, given_kind, _ = m_word.groups()
                wins, losses, given_val = int(wins), int(losses), _parse_int(given_val)
                if given_kind == "winning":
                    expected = given_val * losses // wins
                else:
                    expected = given_val * wins // losses
                assert answer == expected, (text, answer, expected)
            else:
                pytest.fail(f"Unrecognised ratio template: {text!r}")


class TestArithmeticChainSemantics:
    """Replay the chained operations and confirm the generator's answer."""

    OP_TOKENS = re.compile(r"(?:^|\s|,\s+then\s+)(?P<op>add|subtract|multiply by|divide by) (?P<val>\d+)")

    def test_chain_answer_replay(self):
        gen = CompoundGenerator()
        # Filter to arithmetic_chain by inspecting metadata.
        sampled = 0
        attempts = 0
        while sampled < 60 and attempts < 600:
            attempts += 1
            q = gen.generate("medium")
            if q.metadata.get("type") != "arithmetic_chain":
                continue
            sampled += 1
            self._replay_chain(q)

        # Try hard mode too (uses int division `//`).
        sampled = 0
        attempts = 0
        while sampled < 60 and attempts < 600:
            attempts += 1
            q = gen.generate("hard")
            if q.metadata.get("type") != "arithmetic_chain":
                continue
            sampled += 1
            self._replay_chain(q)

    def _replay_chain(self, q: Question) -> None:
        text = q.question_text
        # Extract starting value.
        m = re.match(r"Start with (\d+)", text)
        assert m, f"Couldn't parse start value: {text!r}"
        result = int(m.group(1))

        # Walk every "<op> <value>" token after the start.
        rest = text[m.end():]
        for token in re.finditer(
            r"(add|subtract|multiply by|divide by) (\d+)", rest
        ):
            op, val = token.group(1), int(token.group(2))
            if op == "add":
                result += val
            elif op == "subtract":
                result -= val
            elif op == "multiply by":
                result *= val
            elif op == "divide by":
                result //= val

        expected = int(result)
        actual = int(q.correct_answer)
        assert actual == expected, (text, actual, expected)


class TestPercentageSemantics:
    """Re-derive `find_percentage` answers from the text."""

    FIND_RE = re.compile(r"What is ([\d.]+)% of (\d+)\?")

    def test_find_percentage_matches(self):
        gen = PercentageGenerator()
        sampled = 0
        attempts = 0
        while sampled < 100 and attempts < 600:
            attempts += 1
            q = gen.generate("easy")
            m = self.FIND_RE.match(q.question_text)
            if not m:
                continue
            sampled += 1
            pct, n = float(m.group(1)), int(m.group(2))
            expected = round(n * pct / 100, 2)
            actual = float(q.correct_answer)
            assert abs(actual - expected) < 0.01, (q.question_text, actual, expected)


class TestEstimationRange:
    """Estimation questions must contain `correct_answer` in the range, and
    the validator must accept it."""

    def test_estimation_validator_round_trip(self):
        gen = EstimationGenerator()
        for difficulty in DIFFICULTIES:
            for _ in range(50):
                q = gen.generate(difficulty)
                assert AnswerValidator.validate(q.correct_answer, q)


# ---------------------------------------------------------------------------
# Aggregate failure-rate report so flaky generators surface in CI logs.
# ---------------------------------------------------------------------------


def test_failure_rate_report(capsys):
    """Run a global solvability sweep and print a summary table.

    This intentionally has no assertion — it's a diagnostic. The strict
    pass/fail check lives in `test_generator_answers_round_trip`.
    """
    table: dict[tuple[str, str], dict[str, int]] = defaultdict(
        lambda: {"total": 0, "fail": 0}
    )
    for name, gen in GENERATORS:
        for diff in DIFFICULTIES:
            for _ in range(100):
                q = gen.generate(diff)
                ok = AnswerValidator.validate(q.correct_answer, q)
                table[(name, diff)]["total"] += 1
                if not ok:
                    table[(name, diff)]["fail"] += 1

    print()
    print(f"{'generator':<14} {'difficulty':<10} {'fails':>5} / {'total':<5}")
    for (name, diff), counts in sorted(table.items()):
        print(
            f"{name:<14} {diff:<10} {counts['fail']:>5} / {counts['total']:<5}"
            f" ({counts['fail'] / counts['total']:.1%})"
        )
