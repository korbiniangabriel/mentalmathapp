"""Badge management and checking."""
from typing import List, Dict
from src.models.user_stats import Badge
from src.models.session import SessionSummary
from src.database.db_manager import DatabaseManager


class BadgeManager:
    """Manages badge definitions and checking."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize badge manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def check_earned_badges(self, summary: SessionSummary) -> List[Badge]:
        """Check which badges were earned in this session.
        
        Args:
            summary: Session summary
            
        Returns:
            List of newly earned badges
        """
        newly_earned = []
        all_badges = self.get_all_badges()
        stats = self.db.get_performance_stats()
        
        for badge in all_badges:
            if badge.earned:
                continue  # Already has this badge
            
            if self._check_badge_condition(badge, summary, stats):
                # Award the badge
                if self.db.award_badge(badge.badge_name):
                    badge.earned = True
                    newly_earned.append(badge)
        
        return newly_earned
    
    def _check_badge_condition(self, badge: Badge, summary: SessionSummary, stats: Dict) -> bool:
        """Check if badge condition is met.
        
        Args:
            badge: Badge to check
            summary: Session summary
            stats: Overall user stats
            
        Returns:
            True if badge should be awarded
        """
        name = badge.badge_name
        
        # Milestone Badges
        if name == "First Steps":
            return stats['total_sessions'] >= 1
        
        elif name == "Century Club":
            return stats['total_questions'] >= 100
        
        elif name == "Veteran":
            return stats['total_questions'] >= 1000
        
        elif name == "Marathon Finisher":
            return summary.config.mode_type == "marathon"
        
        # Performance Badges
        elif name == "Perfectionist":
            accuracy = summary.correct_answers / summary.total_questions
            return accuracy == 1.0 and summary.total_questions >= 10
        
        elif name == "Speed Demon":
            fast_answers = sum(1 for r in summary.results if r.is_correct and r.time_taken < 3.0)
            return fast_answers >= 10
        
        elif name == "Lightning Round":
            return summary.avg_time_per_question < 3.0 and summary.total_questions >= 10
        
        elif name == "No Miss":
            # Check for 50 consecutive correct answers across sessions
            return self._check_consecutive_correct(50)
        
        # Streak Badges
        elif name == "Consistent":
            return self.db.get_current_streak() >= 3
        
        elif name == "Week Warrior":
            return self.db.get_current_streak() >= 7
        
        elif name == "Month Master":
            return self.db.get_current_streak() >= 30
        
        # Category Mastery Badges
        elif name == "Arithmetic Ace":
            return self._check_category_mastery("arithmetic", 50, 0.95)
        
        elif name == "Percentage Pro":
            return self._check_category_mastery("percentage", 50, 0.95)
        
        elif name == "Fraction Master":
            return self._check_category_mastery("fractions", 50, 0.95)
        
        elif name == "Ratio Expert":
            return self._check_category_mastery("ratios", 50, 0.95)
        
        elif name == "Compound Champion":
            return self._check_category_mastery("compound", 50, 0.95)
        
        elif name == "Estimation Guru":
            return self._check_category_mastery("estimation", 50, 0.95)
        
        # Challenge Badges
        elif name == "Hard Mode Hero":
            return self._count_hard_mode_sessions() >= 10
        
        elif name == "Mixed Master":
            return self._check_mixed_mode_mastery(50, 0.90)
        
        return False
    
    def _check_consecutive_correct(self, required: int) -> bool:
        """Check for consecutive correct answers."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT is_correct FROM questions_answered
            ORDER BY timestamp DESC
            LIMIT ?
        """, (required,))
        
        results = cursor.fetchall()
        conn.close()
        
        if len(results) < required:
            return False
        
        return all(r['is_correct'] == 1 for r in results)
    
    def _check_category_mastery(self, category: str, min_questions: int, min_accuracy: float) -> bool:
        """Check if user has mastered a category."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Map category to question types
        category_types = {
            'arithmetic': ['addition', 'subtraction', 'multiplication', 'division'],
            'percentage': ['percentage'],
            'fractions': ['fractions'],
            'ratios': ['ratios'],
            'compound': ['compound'],
            'estimation': ['estimation']
        }
        
        types = category_types.get(category, [category])
        placeholders = ','.join('?' * len(types))
        
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM questions_answered
            WHERE question_type IN ({placeholders})
        """, types)
        
        row = cursor.fetchone()
        conn.close()
        
        if row['total'] < min_questions:
            return False
        
        accuracy = row['correct'] / row['total']
        return accuracy >= min_accuracy
    
    def _count_hard_mode_sessions(self) -> int:
        """Count number of hard mode sessions completed."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM sessions
            WHERE difficulty = 'hard' AND completed = 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        return row['count']
    
    def _check_mixed_mode_mastery(self, min_questions: int, min_accuracy: float) -> bool:
        """Check mixed mode mastery."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM questions_answered qa
            JOIN sessions s ON qa.session_id = s.id
            WHERE s.category = 'mixed'
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row['total'] < min_questions:
            return False
        
        accuracy = row['correct'] / row['total']
        return accuracy >= min_accuracy
    
    def get_all_badges(self) -> List[Badge]:
        """Get all badges with earned status.
        
        Returns:
            List of all badges
        """
        return self.db.get_user_badges()
    
    def get_user_badges(self) -> List[Badge]:
        """Get only earned badges.
        
        Returns:
            List of earned badges
        """
        all_badges = self.get_all_badges()
        return [b for b in all_badges if b.earned]
    
    def get_progress_to_badges(self) -> Dict[str, Dict]:
        """Show progress toward unearned badges.
        
        Returns:
            Dictionary mapping badge names to progress info
        """
        progress = {}
        all_badges = self.get_all_badges()
        stats = self.db.get_performance_stats()
        
        for badge in all_badges:
            if badge.earned:
                continue
            
            name = badge.badge_name
            prog_info = {'badge': badge, 'progress': 0, 'target': 100, 'description': ''}
            
            # Calculate progress for each badge type
            if name == "Century Club":
                prog_info['progress'] = stats['total_questions']
                prog_info['target'] = 100
                prog_info['description'] = f"{stats['total_questions']}/100 questions answered"
            
            elif name == "Veteran":
                prog_info['progress'] = stats['total_questions']
                prog_info['target'] = 1000
                prog_info['description'] = f"{stats['total_questions']}/1000 questions answered"
            
            elif name == "Week Warrior":
                streak = self.db.get_current_streak()
                prog_info['progress'] = streak
                prog_info['target'] = 7
                prog_info['description'] = f"{streak}/7 day streak"
            
            elif name == "Month Master":
                streak = self.db.get_current_streak()
                prog_info['progress'] = streak
                prog_info['target'] = 30
                prog_info['description'] = f"{streak}/30 day streak"
            
            # Add more progress calculations as needed
            
            if prog_info['description']:
                progress[name] = prog_info
        
        return progress
