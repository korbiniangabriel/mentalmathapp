"""Daily challenge logic.

Everyone gets the same 5 questions on a given day. The seed is derived from
the ISO ordinal of today's date, so the questions stay stable for the day and
roll forward at midnight local time.

Categories used for the daily mix (in order):
    1. arithmetic   (random pick of addition/subtraction/multiplication/division)
    2. percentage
    3. fractions
    4. ratios
    5. estimation

All questions are generated at medium difficulty.
"""

from __future__ import annotations

import random
from datetime import date
from typing import Callable, List, Optional

from src.models.question import Question
from src.question_generator.arithmetic import (
    AdditionGenerator,
    DivisionGenerator,
    MultiplicationGenerator,
    SubtractionGenerator,
)
from src.question_generator.estimation import EstimationGenerator
from src.question_generator.fractions import FractionsGenerator
from src.question_generator.percentage import PercentageGenerator
from src.question_generator.ratios import RatiosGenerator


DAILY_PREF_KEY = "daily_challenge_last"
DAILY_CHALLENGE_SIZE = 5
DAILY_DIFFICULTY = "medium"


def _today_seed(today: Optional[date] = None) -> int:
    """Derive a stable per-day seed from today's ordinal."""
    return (today or date.today()).toordinal()


class DailyChallenge:
    """Builds the daily-challenge question list and tracks completion."""

    def __init__(self, today: Optional[date] = None):
        self._today = today or date.today()
        self._seed = _today_seed(self._today)

    @property
    def today(self) -> date:
        return self._today

    @property
    def seed(self) -> int:
        return self._seed

    def get_questions_for_today(self) -> List[Question]:
        """Return the deterministic 5-question mix for today.

        Implementation note: the underlying generators read from the *global*
        `random` module. To keep them deterministic without modifying them,
        we temporarily seed the global random state, generate, then restore.
        """
        rng = random.Random(self._seed)

        # Pick the arithmetic flavor for today (still part of the seeded pick).
        arithmetic_choices: list[Callable[[], object]] = [
            AdditionGenerator,
            SubtractionGenerator,
            MultiplicationGenerator,
            DivisionGenerator,
        ]
        arithmetic_gen = rng.choice(arithmetic_choices)()

        plan = [
            arithmetic_gen,
            PercentageGenerator(),
            FractionsGenerator(),
            RatiosGenerator(),
            EstimationGenerator(),
        ]

        # Seed the global random module so generators are deterministic.
        # Combine with the index so each slot draws from a different stream.
        prior_state = random.getstate()
        try:
            questions: List[Question] = []
            for idx, generator in enumerate(plan):
                random.seed(self._seed * 31 + idx)
                questions.append(generator.generate(DAILY_DIFFICULTY))
        finally:
            random.setstate(prior_state)

        return questions

    def has_completed_today(self, db_manager) -> bool:
        """True if the user already completed today's daily challenge."""
        if db_manager is None:
            return False
        try:
            stored = db_manager.get_user_preference(DAILY_PREF_KEY)
        except Exception:
            return False
        return stored == self._today.isoformat()

    def mark_completed(self, db_manager) -> None:
        """Persist that today's daily challenge has been completed."""
        if db_manager is None:
            return
        try:
            db_manager.set_user_preference(DAILY_PREF_KEY, self._today.isoformat())
        except Exception:
            # Storage failures shouldn't block the user finishing the session.
            pass
