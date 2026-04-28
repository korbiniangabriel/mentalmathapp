"""Session tracking models."""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from src.models.question import Question


@dataclass
class SessionConfig:
    """Configuration for a practice session."""
    mode_type: str  # 'sprint', 'marathon', 'targeted'
    category: str  # 'mixed', 'arithmetic', etc.
    difficulty: str  # 'easy', 'medium', 'hard', 'adaptive'
    duration_seconds: Optional[int] = None  # For sprint mode
    question_count: Optional[int] = None  # For marathon mode


@dataclass
class QuestionResult:
    """Result of a single question attempt."""
    question: Question
    user_answer: str
    is_correct: bool
    time_taken: float
    timestamp: datetime
    was_skipped: bool = False


@dataclass
class SessionState:
    """State of an active practice session."""
    config: SessionConfig
    questions_answered: List[QuestionResult] = field(default_factory=list)
    current_question: Optional[Question] = None
    combo_count: int = 0
    total_score: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    is_complete: bool = False
    # Stamped each time a new current_question is set, so time_taken excludes
    # the previous answer's submission overhead. Falls back to start_time on the
    # first question.
    question_started_at: Optional[datetime] = None


@dataclass
class SessionSummary:
    """Summary of a completed session."""
    session_id: Optional[int]
    config: SessionConfig
    total_questions: int
    correct_answers: int
    total_score: int
    avg_time_per_question: float
    duration_seconds: int
    results: List[QuestionResult]
    timestamp: datetime
