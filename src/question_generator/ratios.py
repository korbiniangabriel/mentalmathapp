"""Ratio question generators."""
import random
from src.question_generator.base import QuestionGenerator
from src.models.question import Question


class RatiosGenerator(QuestionGenerator):
    """Generates ratio questions."""
    
    @property
    def question_type(self) -> str:
        return "ratios"
    
    @property
    def category(self) -> str:
        return "ratios"
    
    def generate(self, difficulty: str) -> Question:
        """Generate a ratio question."""
        if difficulty == "easy":
            return self._generate_simple_ratio(difficulty)
        elif difficulty == "medium":
            return self._generate_three_way_ratio(difficulty)
        else:  # hard
            return self._generate_ratio_word_problem(difficulty)
    
    def _generate_simple_ratio(self, difficulty: str) -> Question:
        """Generate simple ratio questions."""
        ratio_a = random.randint(2, 9)
        ratio_b = random.randint(2, 9)
        
        if random.choice([True, False]):
            # Given A, find B
            value_a = ratio_a * random.randint(2, 10)
            value_b = value_a * ratio_b // ratio_a
            answer = value_b
            question_text = f"If A:B is {ratio_a}:{ratio_b} and A = {value_a}, what is B?"
        else:
            # Given B, find A
            value_b = ratio_b * random.randint(2, 10)
            value_a = value_b * ratio_a // ratio_b
            answer = value_a
            question_text = f"If A:B is {ratio_a}:{ratio_b} and B = {value_b}, what is A?"
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=question_text,
            correct_answer=str(answer),
            metadata={"ratio_a": ratio_a, "ratio_b": ratio_b, "type": "simple_ratio"}
        )
    
    def _generate_three_way_ratio(self, difficulty: str) -> Question:
        """Generate three-way ratio questions."""
        ratio_a = random.randint(1, 5)
        ratio_b = random.randint(2, 6)
        ratio_c = random.randint(3, 7)
        
        total = random.randint(50, 300)
        # Adjust total to be divisible by sum of ratios
        ratio_sum = ratio_a + ratio_b + ratio_c
        total = (total // ratio_sum) * ratio_sum
        
        value_a = total * ratio_a // ratio_sum
        value_b = total * ratio_b // ratio_sum
        value_c = total * ratio_c // ratio_sum
        
        # Ask for one of the values
        which = random.choice(['A', 'B', 'C'])
        if which == 'A':
            answer = value_a
        elif which == 'B':
            answer = value_b
        else:
            answer = value_c
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=f"If A:B:C is {ratio_a}:{ratio_b}:{ratio_c} and the total is {total}, what is {which}?",
            correct_answer=str(answer),
            metadata={"ratios": [ratio_a, ratio_b, ratio_c], "total": total, "type": "three_way_ratio"}
        )
    
    def _generate_ratio_word_problem(self, difficulty: str) -> Question:
        """Generate ratio word problems in trading context."""
        wins = random.randint(2, 7)
        losses = random.randint(1, 5)
        
        if random.choice([True, False]):
            # Given winning trades, find losing trades
            actual_wins = wins * random.randint(5, 20)
            actual_losses = actual_wins * losses // wins
            answer = actual_losses
            question_text = f"You have {wins} winning trades for every {losses} losing trades. If you had {actual_wins} winning trades, how many losing trades did you have?"
        else:
            # Given losing trades, find winning trades
            actual_losses = losses * random.randint(5, 20)
            actual_wins = actual_losses * wins // losses
            answer = actual_wins
            question_text = f"You have {wins} winning trades for every {losses} losing trades. If you had {actual_losses} losing trades, how many winning trades did you have?"
        
        return Question(
            question_type=self.question_type,
            category=self.category,
            difficulty=difficulty,
            question_text=question_text,
            correct_answer=str(answer),
            metadata={"win_ratio": wins, "loss_ratio": losses, "type": "word_problem"}
        )
