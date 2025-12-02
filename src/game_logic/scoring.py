"""Scoring system for game sessions."""
from src.models.session import QuestionResult


class ScoreCalculator:
    """Calculates scores and bonuses for questions."""
    
    BASE_POINTS = 100
    
    @staticmethod
    def calculate_base_points(is_correct: bool) -> int:
        """Calculate base points for a question.
        
        Args:
            is_correct: Whether the answer was correct
            
        Returns:
            Base points (100 if correct, 0 if incorrect)
        """
        return ScoreCalculator.BASE_POINTS if is_correct else 0
    
    @staticmethod
    def calculate_combo_multiplier(combo_count: int) -> float:
        """Calculate combo multiplier based on consecutive correct answers.
        
        Args:
            combo_count: Number of consecutive correct answers
            
        Returns:
            Multiplier (1.0, 1.5, 2.0, 2.5, 3.0 max)
        """
        if combo_count < 3:
            return 1.0
        elif combo_count < 5:
            return 1.5
        elif combo_count < 10:
            return 2.0
        elif combo_count < 15:
            return 2.5
        else:
            return 3.0
    
    @staticmethod
    def calculate_speed_bonus(time_taken: float) -> int:
        """Calculate speed bonus based on answer time.
        
        Args:
            time_taken: Time taken in seconds
            
        Returns:
            Bonus points
        """
        if time_taken < 2.0:
            return 100
        elif time_taken < 3.0:
            return 50
        elif time_taken < 5.0:
            return 25
        else:
            return 0
    
    @staticmethod
    def calculate_difficulty_multiplier(difficulty: str) -> float:
        """Calculate multiplier based on difficulty.
        
        Args:
            difficulty: 'easy', 'medium', 'hard', or 'adaptive'
            
        Returns:
            Difficulty multiplier
        """
        multipliers = {
            'easy': 1.0,
            'medium': 1.5,
            'hard': 2.0,
            'adaptive': 1.5
        }
        return multipliers.get(difficulty, 1.0)
    
    @staticmethod
    def calculate_question_score(result: QuestionResult, combo_count: int) -> int:
        """Calculate total score for a question.
        
        Args:
            result: QuestionResult object
            combo_count: Current combo count
            
        Returns:
            Total score for the question
        """
        if not result.is_correct:
            return 0
        
        base = ScoreCalculator.calculate_base_points(result.is_correct)
        combo_mult = ScoreCalculator.calculate_combo_multiplier(combo_count)
        speed_bonus = ScoreCalculator.calculate_speed_bonus(result.time_taken)
        diff_mult = ScoreCalculator.calculate_difficulty_multiplier(result.question.difficulty)
        
        total = int((base * combo_mult + speed_bonus) * diff_mult)
        return total
