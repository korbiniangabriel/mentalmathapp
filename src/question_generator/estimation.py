"""Estimation question generators.

Note on tolerance: estimation questions are wider than the validator's default
1% relative tolerance, but we intentionally don't widen the validator yet --
that's slated for Batch B. For now we expose the question's intended tolerance
through `metadata.min_acceptable` / `metadata.max_acceptable` and ship a small
set of acceptable string forms (rounded to nearest 10/100/1000) instead of
materializing every integer in the range. Users whose answers fall within the
validator's 1% relative band will be accepted; the wider estimation band is
recorded for future use.
"""
import random
import math
from src.question_generator.base import QuestionGenerator
from src.models.question import Question


class EstimationGenerator(QuestionGenerator):
    """Generates estimation questions with acceptable ranges."""

    @property
    def question_type(self) -> str:
        return "estimation"

    @property
    def category(self) -> str:
        return "estimation"

    def generate(self, difficulty: str) -> Question:
        """Generate an estimation question."""
        question_types = ["multiplication", "division", "square_root"]
        q_type = random.choice(question_types)

        if q_type == "multiplication":
            return self._generate_multiplication_estimation(difficulty)
        elif q_type == "division":
            return self._generate_division_estimation(difficulty)
        else:
            return self._generate_square_root_estimation(difficulty)

    @staticmethod
    def _rounded_forms(exact_value: float, min_acc: float, max_acc: float) -> list:
        """Return rounded forms of `exact_value` (nearest 10/100/1000) that
        fall within [min_acc, max_acc]. Always includes the exact value (in
        both int and float string forms when applicable)."""
        forms = []
        # Always include both int and float string forms of the exact value
        # so users typing "200" or "200.0" both match.
        if exact_value == int(exact_value):
            forms.append(str(int(exact_value)))
            forms.append(f"{int(exact_value)}.0")
        else:
            forms.append(str(exact_value))

        for step in (10, 100, 1000):
            rounded = round(exact_value / step) * step
            if min_acc <= rounded <= max_acc:
                forms.append(str(int(rounded)))

        # Dedupe preserving order.
        return list(dict.fromkeys(forms))

    def _generate_multiplication_estimation(self, difficulty: str) -> Question:
        """Generate multiplication estimation questions."""
        if difficulty == "easy":
            a = random.randint(20, 99)
            b = random.randint(10, 30)
            tolerance = 0.1  # 10%
        elif difficulty == "medium":
            a = random.randint(100, 500)
            b = random.randint(20, 99)
            tolerance = 0.08  # 8%
        else:  # hard
            a = random.randint(200, 999)
            b = random.randint(20, 99)
            tolerance = 0.05  # 5%

        exact_answer = a * b
        min_acceptable = exact_answer * (1 - tolerance)
        max_acceptable = exact_answer * (1 + tolerance)

        # Small set of acceptable forms (no integer-range materialization).
        acceptable = self._rounded_forms(exact_answer, min_acceptable, max_acceptable)

        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"Estimate: {a} × {b} (within {int(tolerance*100)}%)",
            correct_answer=str(exact_answer),
            acceptable_answers=acceptable,
            metadata={
                "operand1": a,
                "operand2": b,
                "exact": exact_answer,
                "tolerance": tolerance,
                "min_acceptable": min_acceptable,
                "max_acceptable": max_acceptable,
                "type": "multiplication",
            },
        )

    def _generate_division_estimation(self, difficulty: str) -> Question:
        """Generate division estimation questions."""
        if difficulty == "easy":
            divisor = random.randint(5, 20)
            dividend = divisor * random.randint(20, 100)
            tolerance = 0.1  # 10%
        elif difficulty == "medium":
            divisor = random.randint(10, 50)
            dividend = random.randint(500, 2000)
            tolerance = 0.08  # 8%
        else:  # hard
            divisor = random.randint(20, 99)
            dividend = random.randint(1000, 9999)
            tolerance = 0.05  # 5%

        exact_answer = round(dividend / divisor, 2)
        min_acceptable = exact_answer * (1 - tolerance)
        max_acceptable = exact_answer * (1 + tolerance)

        # Acceptable: exact value (rounded to 1 decimal as canonical), plus a
        # small set of rounded-to-precision forms within tolerance. No huge lists.
        canonical = str(round(exact_answer, 1))
        acceptable = [canonical]
        for precision in [0, 1, 2]:
            val = round(exact_answer, precision)
            if min_acceptable <= val <= max_acceptable:
                acceptable.append(str(val))
                if precision == 0:
                    acceptable.append(str(int(val)))
        # Also include the exact answer as-is.
        acceptable.append(str(exact_answer))
        acceptable = list(dict.fromkeys(acceptable))

        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"Estimate: {dividend} ÷ {divisor} (within {int(tolerance*100)}%)",
            correct_answer=canonical,
            acceptable_answers=acceptable,
            metadata={
                "dividend": dividend,
                "divisor": divisor,
                "exact": exact_answer,
                "tolerance": tolerance,
                "min_acceptable": min_acceptable,
                "max_acceptable": max_acceptable,
                "type": "division",
            },
        )

    def _generate_square_root_estimation(self, difficulty: str) -> Question:
        """Generate square root estimation questions."""
        if difficulty == "easy":
            # Numbers close to perfect squares
            base = random.randint(5, 12)
            offset = random.randint(-5, 5)
            number = base * base + offset
            tolerance = 0.5
        elif difficulty == "medium":
            number = random.randint(50, 200)
            tolerance = 0.5
        else:  # hard
            number = random.randint(100, 500)
            tolerance = 1.0

        exact_answer = math.sqrt(number)
        min_acceptable = exact_answer - tolerance
        max_acceptable = exact_answer + tolerance

        # Small set: canonical (rounded to 1 decimal), 2-decimal exact, integer
        # round, and the boundary integers within tolerance.
        canonical = str(round(exact_answer, 1))
        acceptable = [canonical, str(round(exact_answer, 2))]
        for int_candidate in (math.floor(exact_answer), round(exact_answer), math.ceil(exact_answer)):
            if min_acceptable <= int_candidate <= max_acceptable:
                acceptable.append(str(int(int_candidate)))
        acceptable = list(dict.fromkeys(acceptable))

        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"Estimate: √{number} (within {tolerance})",
            correct_answer=canonical,
            acceptable_answers=acceptable,
            metadata={
                "number": number,
                "exact": exact_answer,
                "tolerance": tolerance,
                "min_acceptable": min_acceptable,
                "max_acceptable": max_acceptable,
                "type": "square_root",
            },
        )
