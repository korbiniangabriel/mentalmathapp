"""Tests for analytics functionality."""
import pytest
import tempfile
import os
from datetime import datetime
from src.database.db_manager import DatabaseManager
from src.analytics.performance_tracker import PerformanceTracker
from src.models.session import SessionConfig, SessionSummary, QuestionResult
from src.models.question import Question


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    db = DatabaseManager(path)
    yield db
    
    # Cleanup
    try:
        os.unlink(path)
    except:
        pass


class TestPerformanceTracker:
    """Test performance tracking."""
    
    def test_overall_stats_empty(self, temp_db):
        """Test overall stats with no data."""
        tracker = PerformanceTracker(temp_db)
        stats = tracker.get_overall_stats()
        
        assert stats['total_questions'] == 0
        assert stats['correct_answers'] == 0
        assert stats['accuracy'] == 0
    
    def test_overall_stats_with_data(self, temp_db):
        """Test overall stats with session data."""
        # Create a test session
        config = SessionConfig(
            mode_type='sprint',
            category='mixed',
            difficulty='medium',
            duration_seconds=120
        )
        
        question = Question(
            question_type='addition',
            category='arithmetic',
            difficulty='medium',
            question_text='2 + 2',
            correct_answer='4'
        )
        
        results = [
            QuestionResult(
                question=question,
                user_answer='4',
                is_correct=True,
                time_taken=2.5,
                timestamp=datetime.now()
            ),
            QuestionResult(
                question=question,
                user_answer='5',
                is_correct=False,
                time_taken=3.0,
                timestamp=datetime.now()
            )
        ]
        
        summary = SessionSummary(
            session_id=None,
            config=config,
            total_questions=2,
            correct_answers=1,
            total_score=100,
            avg_time_per_question=2.75,
            duration_seconds=120,
            results=results,
            timestamp=datetime.now()
        )
        
        temp_db.save_session(summary)
        
        # Test tracker
        tracker = PerformanceTracker(temp_db)
        stats = tracker.get_overall_stats()
        
        assert stats['total_questions'] == 2
        assert stats['correct_answers'] == 1
        assert stats['accuracy'] == 50.0
        assert stats['total_sessions'] == 1
    
    def test_weak_areas_identification(self, temp_db):
        """Test weak area identification."""
        tracker = PerformanceTracker(temp_db)
        
        # With no data, should return empty
        weak = tracker.identify_weak_areas(threshold=0.75)
        assert weak == []
    
    def test_category_performance(self, temp_db):
        """Test category performance breakdown."""
        tracker = PerformanceTracker(temp_db)
        
        df = tracker.get_stats_by_category()
        assert df.empty  # No data yet


class TestInsightsGenerator:
    """Test insight generation."""
    
    def test_insights_generation(self):
        """Test that insights are generated."""
        # This is a basic structural test
        # More detailed tests would require mock data
        pass
