"""Difficulty adjustment logic for adaptive mode."""
from typing import List, Tuple
from src.models.session import QuestionResult


class DifficultyAdjuster:
    """Adjusts difficulty based on player performance."""

    WINDOW_SIZE = 7  # Look at last 7 questions

    # Step-up: high accuracy AND fast average time
    UP_ACCURACY = 0.9
    UP_AVG_TIME = 4.0
    # Step-down: low accuracy
    DOWN_ACCURACY = 0.6

    @staticmethod
    def _window_metrics(window: List[QuestionResult]) -> Tuple[float, float]:
        """Return (accuracy, avg_time) for a non-empty window."""
        accuracy = sum(1 for r in window if r.is_correct) / len(window)
        avg_time = sum(r.time_taken for r in window) / len(window)
        return accuracy, avg_time

    @staticmethod
    def analyze_performance(recent_results: List[QuestionResult]) -> str:
        """Analyze recent performance and suggest difficulty adjustment.

        Hysteresis (Batch B):
            With >= 2 * WINDOW_SIZE answered questions, require BOTH the most
            recent window AND the immediately preceding window to satisfy the
            step criterion before changing difficulty. This prevents a single
            bad streak from yanking the user down a level mid-session.

            With fewer answers we fall back to single-window logic so the
            adapter still moves early in a session.

        Args:
            recent_results: List of recent QuestionResult objects

        Returns:
            Suggested difficulty: 'easy', 'medium', or 'hard'
        """
        if len(recent_results) < 3:
            return 'medium'  # Start with medium until we have data

        window_size = DifficultyAdjuster.WINDOW_SIZE
        recent_window = recent_results[-window_size:]
        current_difficulty = recent_window[-1].question.difficulty

        recent_acc, recent_time = DifficultyAdjuster._window_metrics(recent_window)

        # Hysteresis path: need a prior window of the same size to confirm.
        if len(recent_results) >= 2 * window_size:
            prior_window = recent_results[-2 * window_size:-window_size]
            prior_acc, prior_time = DifficultyAdjuster._window_metrics(prior_window)

            recent_says_up = (
                recent_acc >= DifficultyAdjuster.UP_ACCURACY
                and recent_time < DifficultyAdjuster.UP_AVG_TIME
            )
            prior_says_up = (
                prior_acc >= DifficultyAdjuster.UP_ACCURACY
                and prior_time < DifficultyAdjuster.UP_AVG_TIME
            )
            if recent_says_up and prior_says_up:
                return DifficultyAdjuster._increase_difficulty(current_difficulty)

            recent_says_down = recent_acc < DifficultyAdjuster.DOWN_ACCURACY
            prior_says_down = prior_acc < DifficultyAdjuster.DOWN_ACCURACY
            if recent_says_down and prior_says_down:
                return DifficultyAdjuster._decrease_difficulty(current_difficulty)

            # No two-window agreement -> hold steady (this is the whole point
            # of hysteresis: damp out the jitter).
            return current_difficulty

        # Fallback: single-window logic for early sessions.
        if recent_acc >= DifficultyAdjuster.UP_ACCURACY and recent_time < DifficultyAdjuster.UP_AVG_TIME:
            return DifficultyAdjuster._increase_difficulty(current_difficulty)
        elif recent_acc < DifficultyAdjuster.DOWN_ACCURACY:
            return DifficultyAdjuster._decrease_difficulty(current_difficulty)
        else:
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
