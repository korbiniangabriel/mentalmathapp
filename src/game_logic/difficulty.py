"""Difficulty adjustment logic for adaptive mode."""
from typing import List
from src.models.session import QuestionResult


class DifficultyAdjuster:
    """Adjusts difficulty based on player performance."""
    
    WINDOW_SIZE = 7  # Look at last 7 questions
    
    @staticmethod
    def analyze_performance(recent_results: List[QuestionResult]) -> str:
        """Analyze recent performance and suggest difficulty adjustment.
        
        Args:
            recent_results: List of recent QuestionResult objects
            
        Returns:
            Suggested difficulty: 'easy', 'medium', or 'hard'
        """
        if len(recent_results) < 3:
            return 'medium'  # Start with medium until we have data
        
        # Use only most recent results (up to WINDOW_SIZE)
        window = recent_results[-DifficultyAdjuster.WINDOW_SIZE:]
        
        # Calculate metrics
        accuracy = sum(1 for r in window if r.is_correct) / len(window)
        avg_time = sum(r.time_taken for r in window) / len(window)
        
        # Get current difficulty from most recent question
        current_difficulty = window[-1].question.difficulty
        
        # Decision logic
        if accuracy >= 0.9 and avg_time < 4.0:
            # Performing very well - increase difficulty
            return DifficultyAdjuster._increase_difficulty(current_difficulty)
        elif accuracy < 0.6:
            # Struggling - decrease difficulty
            return DifficultyAdjuster._decrease_difficulty(current_difficulty)
        else:
            # Performing adequately - maintain difficulty
            return current_difficulty
    
    @staticmethod
    def _increase_difficulty(current: str) -> str:
        """Increase difficulty level."""
        if current == 'easy':
            return 'medium'
        elif current == 'medium':
            return 'hard'
        else:
            return 'hard'  # Already at max
    
    @staticmethod
    def _decrease_difficulty(current: str) -> str:
        """Decrease difficulty level."""
        if current == 'hard':
            return 'medium'
        elif current == 'medium':
            return 'easy'
        else:
            return 'easy'  # Already at min
    
    @staticmethod
    def get_initial_difficulty() -> str:
        """Get initial difficulty for adaptive mode."""
        return 'medium'
