"""Base question generator class."""
from abc import ABC, abstractmethod
from src.models.question import Question


class QuestionGenerator(ABC):
    """Abstract base class for question generators."""
    
    @property
    @abstractmethod
    def question_type(self) -> str:
        """Return the specific question type (e.g., 'addition', 'multiplication')."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Return the category (e.g., 'arithmetic', 'percentage')."""
        pass
    
    @abstractmethod
    def generate(self, difficulty: str) -> Question:
        """Generate a question of the specified difficulty.
        
        Args:
            difficulty: 'easy', 'medium', or 'hard'
            
        Returns:
            Question object
        """
        pass
    
    def validate_answer(self, user_answer: str, correct_answer: str) -> bool:
        """Basic answer validation.
        
        Args:
            user_answer: User's answer as string
            correct_answer: Correct answer as string
            
        Returns:
            True if answers match
        """
        try:
            # Try numeric comparison first
            return abs(float(user_answer.strip()) - float(correct_answer.strip())) < 0.01
        except ValueError:
            # Fall back to string comparison
            return user_answer.strip().lower() == correct_answer.strip().lower()
