"""Generate insights from performance data."""
from typing import List, Dict
from datetime import datetime, timedelta
from src.models.session import SessionState, SessionSummary
from src.database.db_manager import DatabaseManager
from src.analytics.performance_tracker import PerformanceTracker


class InsightsGenerator:
    """Generates actionable insights from performance data."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize insights generator.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.tracker = PerformanceTracker(db_manager)
    
    def generate_session_insights(self, summary: SessionSummary) -> List[Dict[str, str]]:
        """Generate insights for a completed session.
        
        Args:
            summary: Session summary
            
        Returns:
            List of insight dictionaries with 'text' and 'type' keys
        """
        insights = []
        
        # Accuracy insights
        accuracy = summary.correct_answers / summary.total_questions * 100
        if accuracy == 100:
            insights.append({
                'text': f"🎉 Perfect score! {summary.correct_answers}/{summary.total_questions} correct!",
                'type': 'positive'
            })
        elif accuracy >= 90:
            insights.append({
                'text': f"⭐ Excellent performance! {accuracy:.1f}% accuracy",
                'type': 'positive'
            })
        elif accuracy >= 75:
            insights.append({
                'text': f"👍 Good job! {accuracy:.1f}% accuracy",
                'type': 'neutral'
            })
        else:
            insights.append({
                'text': f"💡 Room for improvement: {accuracy:.1f}% accuracy. Keep practicing!",
                'type': 'neutral'
            })
        
        # Speed insights
        avg_time = summary.avg_time_per_question
        if avg_time < 3.0:
            insights.append({
                'text': f"⚡ Lightning fast! Average {avg_time:.1f}s per question",
                'type': 'positive'
            })
        elif avg_time < 5.0:
            insights.append({
                'text': f"🏃 Good speed! Average {avg_time:.1f}s per question",
                'type': 'positive'
            })
        
        # Compare to historical average
        overall_stats = self.tracker.get_overall_stats()
        if overall_stats['total_questions'] > summary.total_questions:
            hist_accuracy = overall_stats['accuracy']
            hist_avg_time = overall_stats['avg_time']
            
            # Accuracy comparison
            if accuracy > hist_accuracy + 5:
                insights.append({
                    'text': f"📈 Accuracy improved by {accuracy - hist_accuracy:.1f}% from your average!",
                    'type': 'positive'
                })
            elif accuracy < hist_accuracy - 5:
                insights.append({
                    'text': f"📉 Accuracy was {hist_accuracy - accuracy:.1f}% below your average",
                    'type': 'neutral'
                })
            
            # Speed comparison
            if avg_time < hist_avg_time - 0.5:
                improvement = ((hist_avg_time - avg_time) / hist_avg_time) * 100
                insights.append({
                    'text': f"⏱️ {improvement:.0f}% faster than your average!",
                    'type': 'positive'
                })
        
        # Category-specific insights
        category_insights = self._generate_category_insights(summary)
        insights.extend(category_insights)
        
        # Score insights
        if summary.total_score > 1000:
            insights.append({
                'text': f"🏆 Amazing score: {summary.total_score:,} points!",
                'type': 'positive'
            })
        
        return insights[:5]  # Return top 5 insights
    
    def _generate_category_insights(self, summary: SessionSummary) -> List[Dict[str, str]]:
        """Generate category-specific insights."""
        insights = []
        
        # Group results by question type
        by_type = {}
        for result in summary.results:
            q_type = result.question.question_type
            if q_type not in by_type:
                by_type[q_type] = {'correct': 0, 'total': 0, 'time': []}
            
            by_type[q_type]['total'] += 1
            if result.is_correct:
                by_type[q_type]['correct'] += 1
            by_type[q_type]['time'].append(result.time_taken)
        
        # Find best and worst categories
        for q_type, stats in by_type.items():
            if stats['total'] < 3:
                continue
            
            accuracy = stats['correct'] / stats['total'] * 100
            avg_time = sum(stats['time']) / len(stats['time'])
            
            if accuracy == 100:
                insights.append({
                    'text': f"✨ {q_type.title()}: Perfect {stats['correct']}/{stats['total']}!",
                    'type': 'positive'
                })
            elif accuracy < 60:
                insights.append({
                    'text': f"💡 {q_type.title()}: {accuracy:.0f}% accuracy - practice more to improve",
                    'type': 'neutral'
                })
        
        return insights
    
    def generate_weekly_insights(self) -> List[Dict[str, str]]:
        """Generate insights for the past week.
        
        Returns:
            List of weekly insight dictionaries
        """
        insights = []
        
        # Get weekly trend
        weekly_trend = self.tracker.get_historical_trend(days=7)
        
        if len(weekly_trend) == 0:
            return [{
                'text': "👋 Start practicing to see your weekly insights!",
                'type': 'neutral'
            }]
        
        # Practice consistency
        days_practiced = len(weekly_trend)
        if days_practiced >= 7:
            insights.append({
                'text': "🔥 Perfect week! Practiced every day!",
                'type': 'positive'
            })
        elif days_practiced >= 5:
            insights.append({
                'text': f"💪 Great consistency! Practiced {days_practiced} days this week",
                'type': 'positive'
            })
        else:
            insights.append({
                'text': f"📅 Practiced {days_practiced} days this week. Try for more!",
                'type': 'neutral'
            })
        
        # Accuracy trend
        if len(weekly_trend) >= 2:
            recent_accuracy = weekly_trend.iloc[-1]['accuracy']
            earlier_accuracy = weekly_trend.iloc[0]['accuracy']
            
            if recent_accuracy > earlier_accuracy + 5:
                insights.append({
                    'text': f"📈 Accuracy trending up! Improved by {recent_accuracy - earlier_accuracy:.1f}%",
                    'type': 'positive'
                })
        
        # Weak areas
        weak_areas = self.tracker.identify_weak_areas()
        if weak_areas:
            insights.append({
                'text': f"🎯 Focus areas: {', '.join(weak_areas[:3])}",
                'type': 'neutral'
            })
        
        return insights
