"""Question data models."""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Question:
    """Represents a single math question."""
    question_type: str  # 'addition', 'percentage', etc.
    category: str  # 'arithmetic', 'percentage', etc.
    difficulty: str  # 'easy', 'medium', 'hard'
    question_text: str
    correct_answer: str
    acceptable_answers: List[str] = field(default_factory=list)  # For estimation or rounding
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional info for analytics
    
    def __post_init__(self):
        """Ensure correct_answer is in acceptable_answers."""
        if not self.acceptable_answers:
            self.acceptable_answers = [self.correct_answer]
        elif self.correct_answer not in self.acceptable_answers:
            self.acceptable_answers.append(self.correct_answer)
