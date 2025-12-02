"""Tests for question generators."""
import pytest
from src.question_generator.arithmetic import (
    AdditionGenerator, SubtractionGenerator,
    MultiplicationGenerator, DivisionGenerator
)
from src.question_generator.percentage import PercentageGenerator
from src.question_generator.fractions import FractionsGenerator
from src.question_generator.ratios import RatiosGenerator
from src.question_generator.compound import CompoundGenerator
from src.question_generator.estimation import EstimationGenerator


class TestArithmeticGenerators:
    """Test arithmetic question generators."""
    
    def test_addition_generator(self):
        """Test addition question generation."""
        gen = AdditionGenerator()
        
        for difficulty in ['easy', 'medium', 'hard']:
            question = gen.generate(difficulty)
            
            assert question.question_type == 'addition'
            assert question.category == 'arithmetic'
            assert question.difficulty == difficulty
            assert question.correct_answer
            assert '+' in question.question_text
    
    def test_subtraction_generator(self):
        """Test subtraction question generation."""
        gen = SubtractionGenerator()
        
        question = gen.generate('medium')
        
        assert question.question_type == 'subtraction'
        assert question.category == 'arithmetic'
        assert '-' in question.question_text
    
    def test_multiplication_generator(self):
        """Test multiplication question generation."""
        gen = MultiplicationGenerator()
        
        question = gen.generate('hard')
        
        assert question.question_type == 'multiplication'
        assert '×' in question.question_text
        
    def test_division_generator(self):
        """Test division question generation."""
        gen = DivisionGenerator()
        
        question = gen.generate('easy')
        
        assert question.question_type == 'division'
        assert '÷' in question.question_text


class TestPercentageGenerator:
    """Test percentage question generator."""
    
    def test_percentage_generation(self):
        """Test percentage question generation."""
        gen = PercentageGenerator()
        
        for difficulty in ['easy', 'medium', 'hard']:
            question = gen.generate(difficulty)
            
            assert question.question_type == 'percentage'
            assert question.category == 'percentage'
            assert question.correct_answer
            assert question.question_text


class TestFractionsGenerator:
    """Test fractions question generator."""
    
    def test_fractions_generation(self):
        """Test fraction question generation."""
        gen = FractionsGenerator()
        
        question = gen.generate('medium')
        
        assert question.question_type == 'fractions'
        assert question.category == 'fractions'
        assert question.correct_answer


class TestRatiosGenerator:
    """Test ratios question generator."""
    
    def test_ratios_generation(self):
        """Test ratio question generation."""
        gen = RatiosGenerator()
        
        question = gen.generate('easy')
        
        assert question.question_type == 'ratios'
        assert question.category == 'ratios'
        assert question.correct_answer


class TestCompoundGenerator:
    """Test compound question generator."""
    
    def test_compound_generation(self):
        """Test compound question generation."""
        gen = CompoundGenerator()
        
        question = gen.generate('medium')
        
        assert question.question_type == 'compound'
        assert question.category == 'compound'
        assert question.correct_answer


class TestEstimationGenerator:
    """Test estimation question generator."""
    
    def test_estimation_generation(self):
        """Test estimation question generation."""
        gen = EstimationGenerator()
        
        question = gen.generate('easy')
        
        assert question.question_type == 'estimation'
        assert question.category == 'estimation'
        assert question.correct_answer
        assert len(question.acceptable_answers) > 1  # Should have range


def test_all_generators_produce_valid_questions():
    """Test that all generators produce valid questions."""
    generators = [
        AdditionGenerator(),
        SubtractionGenerator(),
        MultiplicationGenerator(),
        DivisionGenerator(),
        PercentageGenerator(),
        FractionsGenerator(),
        RatiosGenerator(),
        CompoundGenerator(),
        EstimationGenerator(),
    ]
    
    for gen in generators:
        for difficulty in ['easy', 'medium', 'hard']:
            question = gen.generate(difficulty)
            
            # Validate question structure
            assert question.question_type
            assert question.category
            assert question.difficulty == difficulty
            assert question.question_text
            assert question.correct_answer
            assert len(question.acceptable_answers) > 0
            assert question.correct_answer in question.acceptable_answers
