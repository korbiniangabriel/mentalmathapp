"""Arithmetic question generators."""
import random
from src.question_generator.base import QuestionGenerator
from src.models.question import Question


class AdditionGenerator(QuestionGenerator):
    """Generates addition questions."""
    
    @property
    def question_type(self) -> str:
        return "addition"
    
    @property
    def category(self) -> str:
        return "arithmetic"
    
    def generate(self, difficulty: str) -> Question:
        """Generate an addition question."""
        if difficulty == "easy":
            a = random.randint(10, 99)
            b = random.randint(10, 99)
        elif difficulty == "medium":
            a = random.randint(100, 999)
            b = random.randint(100, 999)
        else:  # hard
            a = random.randint(1000, 9999)
            b = random.randint(1000, 9999)
        
        answer = a + b
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"{a:,} + {b:,}",
            correct_answer=str(answer),
            metadata={"operand1": a, "operand2": b, "operation": "addition"}
        )


class SubtractionGenerator(QuestionGenerator):
    """Generates subtraction questions."""
    
    @property
    def question_type(self) -> str:
        return "subtraction"
    
    @property
    def category(self) -> str:
        return "arithmetic"
    
    def generate(self, difficulty: str) -> Question:
        """Generate a subtraction question."""
        if difficulty == "easy":
            a = random.randint(20, 99)
            b = random.randint(10, a)
        elif difficulty == "medium":
            a = random.randint(200, 999)
            b = random.randint(100, a)
        else:  # hard
            a = random.randint(2000, 9999)
            b = random.randint(1000, a)
        
        answer = a - b
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"{a:,} - {b:,}",
            correct_answer=str(answer),
            metadata={"operand1": a, "operand2": b, "operation": "subtraction"}
        )


class MultiplicationGenerator(QuestionGenerator):
    """Generates multiplication questions."""
    
    @property
    def question_type(self) -> str:
        return "multiplication"
    
    @property
    def category(self) -> str:
        return "arithmetic"
    
    def generate(self, difficulty: str) -> Question:
        """Generate a multiplication question."""
        if difficulty == "easy":
            a = random.randint(2, 9)
            b = random.randint(10, 99)
        elif difficulty == "medium":
            a = random.randint(10, 99)
            b = random.randint(10, 99)
        else:  # hard
            a = random.randint(10, 99)
            b = random.randint(100, 999)
        
        answer = a * b
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"{a:,} × {b:,}",
            correct_answer=str(answer),
            metadata={"operand1": a, "operand2": b, "operation": "multiplication"}
        )


class DivisionGenerator(QuestionGenerator):
    """Generates division questions."""
    
    @property
    def question_type(self) -> str:
        return "division"
    
    @property
    def category(self) -> str:
        return "arithmetic"
    
    def generate(self, difficulty: str) -> Question:
        """Generate a division question."""
        if difficulty == "easy":
            # Easy: 2-digit ÷ 1-digit with whole results
            divisor = random.randint(2, 9)
            quotient = random.randint(5, 15)
            dividend = divisor * quotient
        elif difficulty == "medium":
            # Medium: 3-digit ÷ 2-digit with whole results
            divisor = random.randint(10, 30)
            quotient = random.randint(10, 50)
            dividend = divisor * quotient
        else:  # hard
            # Hard: deterministic whole-number quotient using mental-math-friendly
            # divisors. Avoids the decimal-rounding ambiguity where the user types
            # an integer answer and the validator's 1% tolerance gives inconsistent
            # results.
            divisor = random.choice([4, 5, 8, 16, 20, 25])
            quotient = random.randint(20, 80)
            dividend = divisor * quotient

        answer = dividend // divisor

        # Always-whole answers for every difficulty -> the int form is canonical.
        # Including both string forms helps users who type "143" vs "143.0".
        acceptable = list(dict.fromkeys([str(answer), str(int(answer))]))

        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"{dividend:,} ÷ {divisor}",
            correct_answer=str(answer),
            acceptable_answers=acceptable,
            metadata={"dividend": dividend, "divisor": divisor, "operation": "division"}
        )
