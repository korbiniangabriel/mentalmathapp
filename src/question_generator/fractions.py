"""Fraction question generators."""
import random
from fractions import Fraction
from src.question_generator.base import QuestionGenerator
from src.models.question import Question


class FractionsGenerator(QuestionGenerator):
    """Generates fraction conversion and arithmetic questions."""
    
    @property
    def question_type(self) -> str:
        return "fractions"
    
    @property
    def category(self) -> str:
        return "fractions"
    
    def generate(self, difficulty: str) -> Question:
        """Generate a fraction question."""
        if difficulty == "hard":
            question_types = ["fraction_to_decimal", "decimal_to_fraction", "fraction_arithmetic"]
        else:
            question_types = ["fraction_to_decimal", "decimal_to_fraction"]
        
        q_type = random.choice(question_types)
        
        if q_type == "fraction_to_decimal":
            return self._generate_fraction_to_decimal(difficulty)
        elif q_type == "decimal_to_fraction":
            return self._generate_decimal_to_fraction(difficulty)
        else:
            return self._generate_fraction_arithmetic(difficulty)
    
    def _generate_fraction_to_decimal(self, difficulty: str) -> Question:
        """Generate fraction to decimal conversion."""
        if difficulty == "easy":
            fractions = [(1, 2), (1, 4), (3, 4), (1, 5), (2, 5), (3, 5), (4, 5)]
        elif difficulty == "medium":
            fractions = [(3, 8), (5, 8), (1, 6), (5, 6), (2, 7), (3, 7)]
        else:  # hard
            numerator = random.randint(1, 12)
            denominator = random.choice([13, 17, 19, 23])
            fractions = [(numerator, denominator)]

        num, denom = random.choice(fractions)
        # Question text says "round to 2-3 decimal places". Accept the
        # unrounded long form too so users typing the calculator output
        # (e.g. 0.4286) aren't rejected when correct_answer == 0.43.
        exact = num / denom
        answer = round(exact, 4)

        # Generate acceptable answers with different precision levels
        acceptable = list(dict.fromkeys([
            str(round(exact, 2)),
            str(round(exact, 3)),
            str(round(exact, 4)),
            # Unrounded long form (truncated to a reasonable display width).
            f"{exact:.6f}".rstrip("0").rstrip("."),
        ]))

        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"Convert {num}/{denom} to a decimal (round to 2-3 decimal places)",
            correct_answer=str(round(answer, 2)),
            acceptable_answers=acceptable,
            metadata={"numerator": num, "denominator": denom, "type": "fraction_to_decimal"}
        )
    
    def _generate_decimal_to_fraction(self, difficulty: str) -> Question:
        """Generate decimal to fraction conversion."""
        if difficulty == "easy":
            decimals = [0.5, 0.25, 0.75, 0.2, 0.4, 0.6, 0.8]
        elif difficulty == "medium":
            decimals = [0.125, 0.375, 0.625, 0.875, 0.167, 0.833]
        else:  # hard
            decimals = [0.333, 0.667, 0.143, 0.429, 0.571]

        decimal = random.choice(decimals)
        frac = Fraction(decimal).limit_denominator(100)
        correct_answer = f"{frac.numerator}/{frac.denominator}"

        # Build acceptable answers covering:
        # 1. The reduced fraction (canonical correct_answer).
        # 2. The literal decimal interpreted as a fraction (e.g. 0.333 -> "333/1000")
        #    so users who type the literal form aren't rejected by the validator's
        #    0.001 fraction tolerance.
        # 3. The decimal itself as a string -- the validator's numeric/percentage
        #    paths can match this for users who skip fraction format entirely.
        acceptable = [correct_answer]

        # Literal decimal -> fraction (e.g., 0.333 -> 333/1000)
        decimal_str = f"{decimal:.6f}".rstrip("0").rstrip(".")
        if "." in decimal_str:
            decimals_part = decimal_str.split(".")[1]
            denom_pow10 = 10 ** len(decimals_part)
            num_literal = int(round(decimal * denom_pow10))
            literal_frac = f"{num_literal}/{denom_pow10}"
            if literal_frac != correct_answer:
                acceptable.append(literal_frac)
            # Also the reduced literal (e.g. 0.5 -> 5/10 -> 1/2 already covered).
            literal_reduced = Fraction(num_literal, denom_pow10)
            literal_reduced_str = f"{literal_reduced.numerator}/{literal_reduced.denominator}"
            if literal_reduced_str not in acceptable:
                acceptable.append(literal_reduced_str)

        # Plain decimal (str) -- accepted via validator's numeric/percentage path.
        acceptable.append(str(decimal))

        acceptable = list(dict.fromkeys(acceptable))

        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"Convert {decimal} to a simplified fraction (format: numerator/denominator, e.g., 1/2)",
            correct_answer=correct_answer,
            acceptable_answers=acceptable,
            metadata={"decimal": decimal, "type": "decimal_to_fraction"}
        )
    
    def _generate_fraction_arithmetic(self, difficulty: str) -> Question:
        """Generate fraction arithmetic questions (hard mode only)."""
        operations = ["+", "-", "×"]
        op = random.choice(operations)
        
        # Generate simple fractions
        num1, denom1 = random.randint(1, 5), random.choice([2, 3, 4, 5, 6])
        num2, denom2 = random.randint(1, 5), random.choice([2, 3, 4, 5, 6])
        
        frac1 = Fraction(num1, denom1)
        frac2 = Fraction(num2, denom2)
        
        if op == "+":
            result = frac1 + frac2
        elif op == "-":
            result = frac1 - frac2
        else:  # multiplication
            result = frac1 * frac2
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"Calculate: {num1}/{denom1} {op} {num2}/{denom2} (format: numerator/denominator)",
            correct_answer=f"{result.numerator}/{result.denominator}",
            metadata={"frac1": str(frac1), "frac2": str(frac2), "operation": op, "type": "fraction_arithmetic"}
        )
