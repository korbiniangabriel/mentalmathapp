"""Session management for practice sessions."""
import random
from datetime import datetime, timedelta
from typing import Optional, List
from src.models.session import SessionConfig, SessionState, SessionSummary, QuestionResult
from src.models.question import Question
from src.game_logic.validator import AnswerValidator
from src.game_logic.scoring import ScoreCalculator
from src.game_logic.difficulty import DifficultyAdjuster
from src.database.db_manager import DatabaseManager

# Import all question generators
from src.question_generator.arithmetic import (
    AdditionGenerator, SubtractionGenerator, 
    MultiplicationGenerator, DivisionGenerator
)
from src.question_generator.percentage import PercentageGenerator
from src.question_generator.fractions import FractionsGenerator
from src.question_generator.ratios import RatiosGenerator
from src.question_generator.compound import CompoundGenerator
from src.question_generator.estimation import EstimationGenerator


class SessionManager:
    """Manages practice session lifecycle."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize session manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.validator = AnswerValidator()
        self.scorer = ScoreCalculator()
        self.difficulty_adjuster = DifficultyAdjuster()
        
        # Initialize question generators
        self.generators = {
            'addition': AdditionGenerator(),
            'subtraction': SubtractionGenerator(),
            'multiplication': MultiplicationGenerator(),
            'division': DivisionGenerator(),
            'percentage': PercentageGenerator(),
            'fractions': FractionsGenerator(),
            'ratios': RatiosGenerator(),
            'compound': CompoundGenerator(),
            'estimation': EstimationGenerator(),
        }
        
        # Category to generator mapping
        self.category_generators = {
            'arithmetic': ['addition', 'subtraction', 'multiplication', 'division'],
            'percentage': ['percentage'],
            'fractions': ['fractions'],
            'ratios': ['ratios'],
            'compound': ['compound'],
            'estimation': ['estimation'],
            'mixed': list(self.generators.keys()),
        }
    
    def start_session(self, config: SessionConfig) -> SessionState:
        """Initialize a new practice session.
        
        Args:
            config: Session configuration
            
        Returns:
            Initial session state
        """
        state = SessionState(
            config=config,
            questions_answered=[],
            current_question=None,
            combo_count=0,
            total_score=0,
            start_time=datetime.now(),
            is_complete=False
        )
        
        # Generate first question
        state.current_question = self.get_next_question(state)
        
        return state
    
    def get_next_question(self, state: SessionState) -> Question:
        """Generate the next appropriate question.
        
        Args:
            state: Current session state
            
        Returns:
            Next question
        """
        # Determine difficulty
        if state.config.difficulty == 'adaptive':
            if len(state.questions_answered) >= 3:
                difficulty = self.difficulty_adjuster.analyze_performance(state.questions_answered)
            else:
                difficulty = self.difficulty_adjuster.get_initial_difficulty()
        else:
            difficulty = state.config.difficulty
        
        # Select category and generator
        if state.config.category == 'targeted':
            # Focus on weak areas
            weak_areas = self.db.get_weak_areas()
            if weak_areas:
                # Map question types to categories
                available_generators = []
                for weak_type in weak_areas:
                    if weak_type in self.generators:
                        available_generators.append(weak_type)
                
                if not available_generators:
                    available_generators = self.category_generators['mixed']
            else:
                available_generators = self.category_generators['mixed']
        else:
            available_generators = self.category_generators[state.config.category]
        
        # Select random generator from available ones
        generator_key = random.choice(available_generators)
        generator = self.generators[generator_key]
        
        # Generate question
        question = generator.generate(difficulty)
        
        return question
    
    def submit_answer(self, state: SessionState, answer: str) -> QuestionResult:
        """Process a submitted answer.
        
        Args:
            state: Current session state
            answer: User's answer
            
        Returns:
            QuestionResult object
        """
        if not state.current_question:
            raise ValueError("No current question")
        
        # Validate answer
        is_correct = self.validator.validate(answer, state.current_question)
        
        # Calculate time taken
        if state.questions_answered:
            time_taken = (datetime.now() - state.questions_answered[-1].timestamp).total_seconds()
        else:
            time_taken = (datetime.now() - state.start_time).total_seconds()
        
        # Create result
        result = QuestionResult(
            question=state.current_question,
            user_answer=answer,
            is_correct=is_correct,
            time_taken=time_taken,
            timestamp=datetime.now()
        )
        
        # Update combo
        if is_correct:
            state.combo_count += 1
        else:
            state.combo_count = 0
        
        # Calculate and add score
        score = self.scorer.calculate_question_score(result, state.combo_count)
        state.total_score += score
        
        # Add to answered questions
        state.questions_answered.append(result)
        
        # Check if session should end
        if self.check_session_end(state):
            state.is_complete = True
            state.current_question = None
        else:
            # Generate next question
            state.current_question = self.get_next_question(state)
        
        return result
    
    def check_session_end(self, state: SessionState) -> bool:
        """Check if session should end.
        
        Args:
            state: Current session state
            
        Returns:
            True if session should end
        """
        if state.config.mode_type == 'sprint':
            # End if time limit reached
            elapsed = (datetime.now() - state.start_time).total_seconds()
            return elapsed >= state.config.duration_seconds
        
        elif state.config.mode_type == 'marathon':
            # End if question count reached
            return len(state.questions_answered) >= state.config.question_count
        
        elif state.config.mode_type == 'targeted':
            # End after default question count
            default_count = state.config.question_count or 25
            return len(state.questions_answered) >= default_count
        
        return False
    
    def end_session(self, state: SessionState) -> SessionSummary:
        """Finalize and save session.
        
        Args:
            state: Session state to finalize
            
        Returns:
            Session summary
        """
        if not state.questions_answered:
            raise ValueError("Cannot end session with no questions answered")
        
        # Calculate statistics
        total_questions = len(state.questions_answered)
        correct_answers = sum(1 for r in state.questions_answered if r.is_correct)
        duration = int((state.questions_answered[-1].timestamp - state.start_time).total_seconds())
        avg_time = sum(r.time_taken for r in state.questions_answered) / total_questions
        
        # Create summary
        summary = SessionSummary(
            session_id=None,
            config=state.config,
            total_questions=total_questions,
            correct_answers=correct_answers,
            total_score=state.total_score,
            avg_time_per_question=round(avg_time, 2),
            duration_seconds=duration,
            results=state.questions_answered,
            timestamp=state.start_time
        )
        
        # Save to database
        session_id = self.db.save_session(summary)
        summary.session_id = session_id
        
        return summary
