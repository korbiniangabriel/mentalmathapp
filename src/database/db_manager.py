"""Database manager for Mental Math Training App."""
import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import pandas as pd

from src.models.session import SessionConfig, SessionSummary, QuestionResult
from src.models.user_stats import Badge


class DatabaseManager:
    """Manages all database operations."""
    
    def __init__(self, db_path: str = "data/mentalmath.db"):
        """Initialize database connection."""
        self.db_path = db_path
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_db(self):
        """Create tables and insert default data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Read and execute schema
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r') as f:
            schema = f.read()
        cursor.executescript(schema)
        
        # Insert default badges if not exists
        self._insert_default_badges(cursor)
        
        conn.commit()
        conn.close()
    
    def _insert_default_badges(self, cursor):
        """Insert predefined badges."""
        badges = [
            # Milestone Badges
            ("First Steps", "Complete your first session", "milestone", "🎯"),
            ("Century Club", "Answer 100 total questions", "milestone", "💯"),
            ("Veteran", "Answer 1000 total questions", "milestone", "🏆"),
            ("Marathon Finisher", "Complete your first marathon mode", "milestone", "🏃"),
            
            # Performance Badges
            ("Perfectionist", "100% accuracy in a session (min 10 questions)", "performance", "⭐"),
            ("Speed Demon", "10 answers under 3 seconds in one session", "performance", "⚡"),
            ("Lightning Round", "Average under 3s in a session", "performance", "🔥"),
            ("No Miss", "50 consecutive correct answers", "performance", "🎯"),
            
            # Streak Badges
            ("Consistent", "3-day practice streak", "streak", "📅"),
            ("Week Warrior", "7-day practice streak", "streak", "📆"),
            ("Month Master", "30-day practice streak", "streak", "🗓️"),
            
            # Category Mastery Badges
            ("Arithmetic Ace", "95% accuracy over 50 arithmetic questions", "mastery", "➕"),
            ("Percentage Pro", "95% accuracy over 50 percentage questions", "mastery", "📊"),
            ("Fraction Master", "95% accuracy over 50 fraction questions", "mastery", "½"),
            ("Ratio Expert", "95% accuracy over 50 ratio questions", "mastery", "⚖️"),
            ("Compound Champion", "95% accuracy over 50 compound questions", "mastery", "🔗"),
            ("Estimation Guru", "95% accuracy over 50 estimation questions", "mastery", "🎲"),
            
            # Challenge Badges
            ("Hard Mode Hero", "Complete 10 hard mode sessions", "challenge", "💪"),
            ("Mixed Master", "90% accuracy in mixed mode (min 50 questions)", "challenge", "🎨"),
        ]
        
        for badge_name, description, category, icon in badges:
            cursor.execute("""
                INSERT OR IGNORE INTO badges (badge_name, description, category, icon)
                VALUES (?, ?, ?, ?)
            """, (badge_name, description, category, icon))
    
    def save_session(self, summary: SessionSummary) -> int:
        """Save a completed session and return session_id."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate duration
        if summary.duration_seconds:
            duration = summary.duration_seconds
        else:
            duration = int((summary.results[-1].timestamp - summary.results[0].timestamp).total_seconds()) if summary.results else 0
        
        # Insert session
        cursor.execute("""
            INSERT INTO sessions (
                timestamp, mode_type, category, difficulty,
                duration_seconds, total_questions, correct_answers,
                total_score, avg_time_per_question, completed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            summary.timestamp,
            summary.config.mode_type,
            summary.config.category,
            summary.config.difficulty,
            duration,
            summary.total_questions,
            summary.correct_answers,
            summary.total_score,
            summary.avg_time_per_question,
            True
        ))
        
        session_id = cursor.lastrowid
        
        # Save all question results
        for result in summary.results:
            self.save_question_answer(cursor, session_id, result)
        
        # Update daily streak
        self.update_streak(cursor, summary.timestamp.date())
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def save_question_answer(self, cursor, session_id: int, result: QuestionResult):
        """Save individual question result."""
        cursor.execute("""
            INSERT INTO questions_answered (
                session_id, question_type, difficulty, question_text,
                correct_answer, user_answer, is_correct, time_taken_seconds, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            result.question.question_type,
            result.question.difficulty,
            result.question.question_text,
            result.question.correct_answer,
            result.user_answer,
            result.is_correct,
            result.time_taken,
            result.timestamp
        ))
    
    def get_session_history(self, limit: int = 50) -> pd.DataFrame:
        """Retrieve past sessions."""
        conn = self.get_connection()
        query = """
            SELECT * FROM sessions
            WHERE completed = 1
            ORDER BY timestamp DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        return df
    
    def get_questions_by_type(self, question_type: str = None, limit: int = 100) -> pd.DataFrame:
        """Filter questions by category."""
        conn = self.get_connection()
        if question_type:
            query = """
                SELECT * FROM questions_answered
                WHERE question_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(question_type, limit))
        else:
            query = """
                SELECT * FROM questions_answered
                ORDER BY timestamp DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        return df
    
    def get_performance_stats(self) -> Dict:
        """Get aggregate performance statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_questions,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
                AVG(time_taken_seconds) as avg_time
            FROM questions_answered
        """)
        row = cursor.fetchone()
        
        stats = {
            'total_questions': row['total_questions'] or 0,
            'correct_answers': row['correct_answers'] or 0,
            'accuracy': (row['correct_answers'] / row['total_questions'] * 100) if row['total_questions'] > 0 else 0,
            'avg_time': row['avg_time'] or 0
        }
        
        # Session stats
        cursor.execute("SELECT COUNT(*) as total_sessions, SUM(total_score) as total_score FROM sessions")
        session_row = cursor.fetchone()
        stats['total_sessions'] = session_row['total_sessions'] or 0
        stats['total_score'] = session_row['total_score'] or 0
        
        conn.close()
        return stats
    
    def get_user_badges(self) -> List[Badge]:
        """Retrieve earned badges."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT b.*, ub.earned_timestamp
            FROM badges b
            LEFT JOIN user_badges ub ON b.id = ub.badge_id
            ORDER BY b.category, b.id
        """)
        
        badges = []
        for row in cursor.fetchall():
            badge = Badge(
                id=row['id'],
                badge_name=row['badge_name'],
                description=row['description'],
                category=row['category'],
                icon=row['icon'],
                earned=row['earned_timestamp'] is not None,
                earned_timestamp=row['earned_timestamp']
            )
            badges.append(badge)
        
        conn.close()
        return badges
    
    def award_badge(self, badge_name: str) -> bool:
        """Award a badge to the user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get badge_id
            cursor.execute("SELECT id FROM badges WHERE badge_name = ?", (badge_name,))
            row = cursor.fetchone()
            if not row:
                return False
            
            badge_id = row['id']
            
            # Check if already awarded
            cursor.execute("SELECT id FROM user_badges WHERE badge_id = ?", (badge_id,))
            if cursor.fetchone():
                return False  # Already has badge
            
            # Award badge
            cursor.execute("""
                INSERT INTO user_badges (badge_id, earned_timestamp)
                VALUES (?, ?)
            """, (badge_id, datetime.now()))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error awarding badge: {e}")
            return False
        finally:
            conn.close()
    
    def update_streak(self, cursor, activity_date: date):
        """Update daily streak."""
        cursor.execute("""
            INSERT INTO daily_streaks (date, sessions_completed)
            VALUES (?, 1)
            ON CONFLICT(date) DO UPDATE SET sessions_completed = sessions_completed + 1
        """, (activity_date,))
    
    def get_current_streak(self) -> int:
        """Get current consecutive day streak."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date FROM daily_streaks
            ORDER BY date DESC
        """)
        
        dates = [row['date'] for row in cursor.fetchall()]
        conn.close()
        
        if not dates:
            return 0
        
        # Convert strings to dates
        dates = [datetime.strptime(d, '%Y-%m-%d').date() if isinstance(d, str) else d for d in dates]
        
        streak = 0
        current_date = date.today()
        
        for activity_date in dates:
            if activity_date == current_date or activity_date == current_date - timedelta(days=1):
                streak += 1
                current_date = activity_date - timedelta(days=1)
            else:
                break
        
        return streak
    
    def get_longest_streak(self) -> int:
        """Get the longest streak ever achieved."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date FROM daily_streaks
            ORDER BY date ASC
        """)
        
        dates = [row['date'] for row in cursor.fetchall()]
        conn.close()
        
        if not dates:
            return 0
        
        # Convert strings to dates
        dates = [datetime.strptime(d, '%Y-%m-%d').date() if isinstance(d, str) else d for d in dates]
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(dates)):
            if dates[i] == dates[i-1] + timedelta(days=1):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    
    def get_weak_areas(self, threshold: float = 0.75) -> List[str]:
        """Identify categories with accuracy below threshold."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                question_type,
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                CAST(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as accuracy
            FROM questions_answered
            GROUP BY question_type
            HAVING COUNT(*) >= 10
        """)
        
        weak_areas = []
        for row in cursor.fetchall():
            if row['accuracy'] < threshold:
                weak_areas.append(row['question_type'])
        
        conn.close()
        return weak_areas
    
    def get_category_performance(self) -> pd.DataFrame:
        """Get performance breakdown by category."""
        conn = self.get_connection()
        query = """
            SELECT 
                question_type,
                COUNT(*) as questions_answered,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
                CAST(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as accuracy,
                AVG(time_taken_seconds) as avg_time
            FROM questions_answered
            GROUP BY question_type
            ORDER BY questions_answered DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
