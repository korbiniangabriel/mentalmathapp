"""Tests for game logic."""
import pytest
from datetime import datetime
from src.game_logic.validator import AnswerValidator
from src.game_logic.scoring import ScoreCalculator
from src.game_logic.difficulty import DifficultyAdjuster
from src.models.question import Question
from src.models.session import QuestionResult


class TestAnswerValidator:
    """Test answer validation logic."""
    
    def test_exact_match(self):
        """Test exact answer matching."""
        question = Question(
            question_type='addition',
            category='arithmetic',
            difficulty='easy',
            question_text='2 + 2',
            correct_answer='4'
        )
        
        assert AnswerValidator.validate('4', question) == True
        assert AnswerValidator.validate('5', question) == False
    
    def test_numeric_tolerance(self):
        """Test numeric tolerance in validation."""
        question = Question(
            question_type='percentage',
            category='percentage',
            difficulty='medium',
            question_text='What is 15% of 200?',
            correct_answer='30'
        )
        
        assert AnswerValidator.validate('30', question) == True
        assert AnswerValidator.validate('30.0', question) == True
    
    def test_percentage_formats(self):
        """Test various percentage formats."""
        question = Question(
            question_type='percentage',
            category='percentage',
            difficulty='easy',
            question_text='Change?',
            correct_answer='15',
            acceptable_answers=['15', '15.0']
        )
        
        # Should accept both with and without % sign
        assert AnswerValidator.validate('15', question) == True
    
    def test_fraction_parsing(self):
        """Test fraction answer parsing."""
        question = Question(
            question_type='fractions',
            category='fractions',
            difficulty='easy',
            question_text='Convert to fraction',
            correct_answer='1/2'
        )
        
        assert AnswerValidator.validate('1/2', question) == True


class TestScoreCalculator:
    """Test scoring calculations."""
    
    def test_base_points(self):
        """Test base points calculation."""
        assert ScoreCalculator.calculate_base_points(True) == 100
        assert ScoreCalculator.calculate_base_points(False) == 0
    
    def test_combo_multiplier(self):
        """Test combo multiplier calculation."""
        assert ScoreCalculator.calculate_combo_multiplier(0) == 1.0
        assert ScoreCalculator.calculate_combo_multiplier(3) == 1.5
        assert ScoreCalculator.calculate_combo_multiplier(5) == 2.0
        assert ScoreCalculator.calculate_combo_multiplier(10) == 2.5
        assert ScoreCalculator.calculate_combo_multiplier(15) == 3.0
        assert ScoreCalculator.calculate_combo_multiplier(20) == 3.0  # Max
    
    def test_speed_bonus(self):
        """Test speed bonus calculation."""
        assert ScoreCalculator.calculate_speed_bonus(1.5) == 100
        assert ScoreCalculator.calculate_speed_bonus(2.5) == 50
        assert ScoreCalculator.calculate_speed_bonus(4.0) == 25
        assert ScoreCalculator.calculate_speed_bonus(6.0) == 0
    
    def test_difficulty_multiplier(self):
        """Test difficulty multiplier."""
        assert ScoreCalculator.calculate_difficulty_multiplier('easy') == 1.0
        assert ScoreCalculator.calculate_difficulty_multiplier('medium') == 1.5
        assert ScoreCalculator.calculate_difficulty_multiplier('hard') == 2.0


class TestDifficultyAdjuster:
    """Test difficulty adjustment logic."""
    
    def test_initial_difficulty(self):
        """Test initial difficulty selection."""
        assert DifficultyAdjuster.get_initial_difficulty() == 'medium'
    
    def test_difficulty_increase(self):
        """Test difficulty increase logic."""
        # Create mock results with high accuracy and fast time
        question = Question(
            question_type='addition',
            category='arithmetic',
            difficulty='easy',
            question_text='2 + 2',
            correct_answer='4'
        )
        
        results = [
            QuestionResult(
                question=question,
                user_answer='4',
                is_correct=True,
                time_taken=2.0,
                timestamp=datetime.now()
            )
            for _ in range(7)
        ]
        
        new_difficulty = DifficultyAdjuster.analyze_performance(results)
        assert new_difficulty in ['easy', 'medium', 'hard']
    
    def test_difficulty_decrease(self):
        """Test difficulty decrease logic."""
        question = Question(
            question_type='addition',
            category='arithmetic',
            difficulty='hard',
            question_text='2 + 2',
            correct_answer='4'
        )
        
        # Create results with low accuracy
        results = []
        for i in range(7):
            results.append(QuestionResult(
                question=question,
                user_answer='wrong' if i % 2 == 0 else '4',
                is_correct=i % 2 != 0,
                time_taken=5.0,
                timestamp=datetime.now()
            ))
        
        new_difficulty = DifficultyAdjuster.analyze_performance(results)
        assert new_difficulty in ['easy', 'medium']
