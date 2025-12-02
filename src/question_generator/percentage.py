"""Percentage question generators."""
import random
from src.question_generator.base import QuestionGenerator
from src.models.question import Question


class PercentageGenerator(QuestionGenerator):
    """Generates percentage calculation questions."""
    
    @property
    def question_type(self) -> str:
        return "percentage"
    
    @property
    def category(self) -> str:
        return "percentage"
    
    def generate(self, difficulty: str) -> Question:
        """Generate a percentage question."""
        question_types = ["find_percentage", "percentage_change", "reverse_percentage"]
        q_type = random.choice(question_types)
        
        if q_type == "find_percentage":
            return self._generate_find_percentage(difficulty)
        elif q_type == "percentage_change":
            return self._generate_percentage_change(difficulty)
        else:
            return self._generate_reverse_percentage(difficulty)
    
    def _generate_find_percentage(self, difficulty: str) -> Question:
        """Generate 'Find X% of Y' questions."""
        if difficulty == "easy":
            percentages = [10, 25, 50, 75]
            percent = random.choice(percentages)
            number = random.randint(1, 20) * 10
        elif difficulty == "medium":
            percent = random.choice([15, 17, 20, 23, 30, 35])
            number = random.randint(50, 500)
        else:  # hard
            percent = round(random.uniform(3.5, 25.5), 1)
            number = random.randint(100, 1000)
        
        answer = round(number * percent / 100, 2)
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"What is {percent}% of {number}?",
            correct_answer=str(answer),
            acceptable_answers=[str(answer), str(int(answer)) if answer == int(answer) else str(answer)],
            metadata={"percent": percent, "number": number, "type": "find_percentage"}
        )
    
    def _generate_percentage_change(self, difficulty: str) -> Question:
        """Generate percentage change questions."""
        if difficulty == "easy":
            old = random.randint(50, 200)
            change_percent = random.choice([10, 20, 25, 50])
            new = old * (1 + change_percent / 100)
        elif difficulty == "medium":
            old = random.randint(50, 300)
            change_percent = random.randint(-30, 50)
            new = old * (1 + change_percent / 100)
        else:  # hard
            old = random.randint(100, 500)
            new = random.randint(80, 600)
            change_percent = round((new - old) / old * 100, 2)
        
        if difficulty != "hard":
            new = int(new)
            answer = change_percent
        else:
            answer = change_percent
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"What is the percentage change from {old} to {int(new)}?",
            correct_answer=str(round(answer, 2)),
            acceptable_answers=[str(round(answer, 2)), str(round(answer, 1)), str(int(answer))],
            metadata={"old_value": old, "new_value": new, "type": "percentage_change"}
        )
    
    def _generate_reverse_percentage(self, difficulty: str) -> Question:
        """Generate reverse percentage questions."""
        if difficulty == "easy":
            x = random.randint(50, 200)
            percent = random.choice([50, 80, 25])
        elif difficulty == "medium":
            x = random.randint(50, 300)
            percent = random.choice([60, 75, 85, 90])
        else:  # hard
            x = random.randint(100, 500)
            percent = random.randint(65, 95)
        
        part = round(x * percent / 100, 2)
        answer = x
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"If {part} is {percent}% of a number, what is the number?",
            correct_answer=str(answer),
            acceptable_answers=[str(answer), str(round(answer, 1))],
            metadata={"part": part, "percent": percent, "type": "reverse_percentage"}
        )
