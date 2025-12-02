"""User statistics models."""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class UserStats:
    """Overall user performance statistics."""
    total_questions: int
    total_correct: int
    accuracy: float
    avg_time_per_question: float
    current_streak: int
    longest_streak: int
    total_sessions: int
    total_score: int


@dataclass
class CategoryStats:
    """Performance statistics for a specific category."""
    category: str
    questions_answered: int
    correct_answers: int
    accuracy: float
    avg_time: float


@dataclass
class Badge:
    """Represents an achievement badge."""
    id: int
    badge_name: str
    description: str
    category: str
    icon: str
    earned: bool = False
    earned_timestamp: str = None
