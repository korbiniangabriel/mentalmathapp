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
        answer = round(num / denom, 4)
        
        # Generate acceptable answers with different precision levels
        acceptable = [
            str(round(answer, 2)),
            str(round(answer, 3)),
            str(round(answer, 4)),
        ]
        
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
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"Convert {decimal} to a simplified fraction (format: numerator/denominator, e.g., 1/2)",
            correct_answer=f"{frac.numerator}/{frac.denominator}",
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
