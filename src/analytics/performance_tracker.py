"""Performance tracking and analysis."""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
from src.database.db_manager import DatabaseManager


class PerformanceTracker:
    """Tracks and analyzes user performance metrics."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize performance tracker.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def get_overall_stats(self) -> Dict:
        """Get overall performance statistics.
        
        Returns:
            Dictionary with overall stats
        """
        stats = self.db.get_performance_stats()
        stats['current_streak'] = self.db.get_current_streak()
        stats['longest_streak'] = self.db.get_longest_streak()
        return stats
    
    def get_stats_by_category(self) -> pd.DataFrame:
        """Get performance breakdown by question type.
        
        Returns:
            DataFrame with category-wise stats
        """
        return self.db.get_category_performance()
    
    def get_stats_by_difficulty(self) -> pd.DataFrame:
        """Get performance breakdown by difficulty level.
        
        Returns:
            DataFrame with difficulty-wise stats
        """
        conn = self.db.get_connection()
        query = """
            SELECT 
                difficulty,
                COUNT(*) as questions_answered,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
                CAST(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as accuracy,
                AVG(time_taken_seconds) as avg_time
            FROM questions_answered
            GROUP BY difficulty
            ORDER BY 
                CASE difficulty
                    WHEN 'easy' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'hard' THEN 3
                    ELSE 4
                END
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_historical_trend(self, days: int = 30) -> pd.DataFrame:
        """Get performance trend over time.
        
        Args:
            days: Number of days to look back
            
        Returns:
            DataFrame with daily performance trends
        """
        conn = self.db.get_connection()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as questions,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                CAST(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as accuracy,
                AVG(time_taken_seconds) as avg_time
            FROM questions_answered
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """
        df = pd.read_sql_query(query, conn, params=(cutoff_date,))
        conn.close()
        return df
    
    def get_time_of_day_performance(self) -> pd.DataFrame:
        """Get performance breakdown by hour of day.
        
        Returns:
            DataFrame with hourly performance stats
        """
        conn = self.db.get_connection()
        query = """
            SELECT 
                CAST(strftime('%H', timestamp) AS INTEGER) as hour,
                COUNT(*) as questions,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                CAST(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as accuracy,
                AVG(time_taken_seconds) as avg_time
            FROM questions_answered
            GROUP BY hour
            ORDER BY hour
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def identify_weak_areas(self, threshold: float = 0.75) -> List[str]:
        """Identify question types with accuracy below threshold.
        
        Args:
            threshold: Accuracy threshold (0.0 to 1.0)
            
        Returns:
            List of weak category names
        """
        return self.db.get_weak_areas(threshold)
    
    def identify_slow_areas(self, threshold: float = 5.0) -> List[str]:
        """Identify question types with average time above threshold.
        
        Args:
            threshold: Time threshold in seconds
            
        Returns:
            List of slow category names
        """
        df = self.get_stats_by_category()
        if df.empty:
            return []
        
        slow = df[df['avg_time'] > threshold]
        return slow['question_type'].tolist()
    
    def get_recent_sessions(self, limit: int = 10) -> pd.DataFrame:
        """Get recent session summaries.
        
        Args:
            limit: Number of sessions to retrieve
            
        Returns:
            DataFrame with session data
        """
        return self.db.get_session_history(limit)
    
    def get_session_details(self, session_id: int) -> Dict:
        """Get detailed information about a specific session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary with session details
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        session = cursor.fetchone()
        
        if not session:
            return None
        
        # Get questions for this session
        query = """
            SELECT * FROM questions_answered
            WHERE session_id = ?
            ORDER BY timestamp
        """
        questions_df = pd.read_sql_query(query, conn, params=(session_id,))
        
        conn.close()
        
        return {
            'session': dict(session),
            'questions': questions_df
        }
