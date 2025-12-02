"""Estimation question generators."""
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
        
        acceptable = []
        for val in range(int(min_acceptable), int(max_acceptable) + 1):
            acceptable.append(str(val))
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"Estimate: {a} × {b} (within {int(tolerance*100)}%)",
            correct_answer=str(exact_answer),
            acceptable_answers=acceptable,
            metadata={"operand1": a, "operand2": b, "exact": exact_answer, "tolerance": tolerance, "type": "multiplication"}
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
        
        acceptable = []
        # For division, accept answers rounded to different precision
        for precision in [0, 1, 2]:
            val = round(exact_answer, precision)
            if min_acceptable <= val <= max_acceptable:
                acceptable.append(str(val))
                if precision == 0:
                    acceptable.append(str(int(val)))
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"Estimate: {dividend} ÷ {divisor} (within {int(tolerance*100)}%)",
            correct_answer=str(round(exact_answer, 1)),
            acceptable_answers=list(set(acceptable)),
            metadata={"dividend": dividend, "divisor": divisor, "exact": exact_answer, "tolerance": tolerance, "type": "division"}
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
        
        acceptable = []
        # Accept answers within tolerance
        for val_100 in range(int(min_acceptable * 100), int(max_acceptable * 100) + 1):
            val = val_100 / 100
            acceptable.append(str(round(val, 2)))
            acceptable.append(str(round(val, 1)))
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"Estimate: √{number} (within {tolerance})",
            correct_answer=str(round(exact_answer, 1)),
            acceptable_answers=list(set(acceptable)),
            metadata={"number": number, "exact": exact_answer, "tolerance": tolerance, "type": "square_root"}
        )
