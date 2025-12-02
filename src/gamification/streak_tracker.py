"""Streak tracking functionality."""
from datetime import date, timedelta
from typing import Dict
import pandas as pd
from src.database.db_manager import DatabaseManager


class StreakTracker:
    """Tracks and manages practice streaks."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize streak tracker.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def record_activity(self, activity_date: date = None):
        """Record practice activity for a date.
        
        Args:
            activity_date: Date of activity (defaults to today)
        """
        if activity_date is None:
            activity_date = date.today()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO daily_streaks (date, sessions_completed)
            VALUES (?, 1)
            ON CONFLICT(date) DO UPDATE SET sessions_completed = sessions_completed + 1
        """, (activity_date,))
        
        conn.commit()
        conn.close()
    
    def get_current_streak(self) -> int:
        """Calculate current consecutive day streak.
        
        Returns:
            Number of consecutive days
        """
        return self.db.get_current_streak()
    
    def get_longest_streak(self) -> int:
        """Get the longest streak ever achieved.
        
        Returns:
            Longest streak count
        """
        return self.db.get_longest_streak()
    
    def is_streak_at_risk(self) -> bool:
        """Check if streak is about to break.
        
        Returns:
            True if no activity today and streak > 0
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check if practiced today
        today = date.today()
        cursor.execute("""
            SELECT sessions_completed FROM daily_streaks
            WHERE date = ?
        """, (today,))
        
        today_record = cursor.fetchone()
        conn.close()
        
        if today_record:
            return False  # Already practiced today
        
        # Check if had a streak going
        current_streak = self.get_current_streak()
        return current_streak > 0
    
    def get_streak_calendar(self, weeks: int = 8) -> pd.DataFrame:
        """Get calendar view of activity.
        
        Args:
            weeks: Number of weeks to retrieve
            
        Returns:
            DataFrame with date and sessions_completed
        """
        conn = self.db.get_connection()
        
        start_date = date.today() - timedelta(weeks=weeks)
        
        query = """
            SELECT date, sessions_completed
            FROM daily_streaks
            WHERE date >= ?
            ORDER BY date
        """
        
        df = pd.read_sql_query(query, conn, params=(start_date,))
        conn.close()
        
        return df
    
    def get_streak_stats(self) -> Dict:
        """Get comprehensive streak statistics.
        
        Returns:
            Dictionary with streak stats
        """
        return {
            'current_streak': self.get_current_streak(),
            'longest_streak': self.get_longest_streak(),
            'at_risk': self.is_streak_at_risk(),
            'practiced_today': not self.is_streak_at_risk() or self.get_current_streak() == 0
        }
