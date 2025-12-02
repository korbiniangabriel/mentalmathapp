"""Answer validation logic."""
import re
from src.models.question import Question


class AnswerValidator:
    """Validates user answers against correct answers."""
    
    @staticmethod
    def validate(user_answer: str, question: Question) -> bool:
        """Validate if user answer is correct.
        
        Args:
            user_answer: User's answer as string
            question: Question object with correct answer and acceptable answers
            
        Returns:
            True if answer is correct
        """
        if not user_answer or not user_answer.strip():
            return False
        
        user_answer = user_answer.strip()
        
        # Check against all acceptable answers
        for acceptable in question.acceptable_answers:
            if AnswerValidator._compare_answers(user_answer, acceptable):
                return True
        
        return False
    
    @staticmethod
    def _compare_answers(user_answer: str, correct_answer: str) -> bool:
        """Compare two answers with various tolerance methods."""
        # Remove whitespace
        user_answer = user_answer.strip()
        correct_answer = correct_answer.strip()
        
        # Exact string match
        if user_answer.lower() == correct_answer.lower():
            return True
        
        # Handle percentage formats (15%, 15, 0.15)
        user_pct = AnswerValidator._extract_percentage(user_answer)
        correct_pct = AnswerValidator._extract_percentage(correct_answer)
        if user_pct is not None and correct_pct is not None:
            return abs(user_pct - correct_pct) < 0.1
        
        # Handle fraction formats
        if '/' in user_answer and '/' in correct_answer:
            user_frac = AnswerValidator._parse_fraction(user_answer)
            correct_frac = AnswerValidator._parse_fraction(correct_answer)
            if user_frac is not None and correct_frac is not None:
                return abs(user_frac - correct_frac) < 0.001
        
        # Numeric comparison with tolerance
        try:
            user_num = float(user_answer.replace(',', ''))
            correct_num = float(correct_answer.replace(',', ''))
            
            # Use relative tolerance for large numbers, absolute for small
            if abs(correct_num) > 10:
                return abs(user_num - correct_num) / abs(correct_num) < 0.01
            else:
                return abs(user_num - correct_num) < 0.1
        except ValueError:
            pass
        
        return False
    
    @staticmethod
    def _extract_percentage(text: str) -> float:
        """Extract percentage value from text."""
        text = text.strip()
        
        # Remove % sign if present
        if text.endswith('%'):
            try:
                return float(text[:-1])
            except ValueError:
                return None
        
        # Try as decimal (0.15 = 15%)
        try:
            val = float(text)
            if 0 <= val <= 1:
                return val * 100
            elif -100 <= val <= 100:
                return val
        except ValueError:
            pass
        
        return None
    
    @staticmethod
    def _parse_fraction(text: str) -> float:
        """Parse fraction string to decimal."""
        try:
            if '/' in text:
                parts = text.split('/')
                if len(parts) == 2:
                    numerator = float(parts[0].strip())
                    denominator = float(parts[1].strip())
                    if denominator != 0:
                        return numerator / denominator
        except (ValueError, ZeroDivisionError):
            pass
        
        return None
