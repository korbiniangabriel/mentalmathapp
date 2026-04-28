"""Performance tracking and analysis."""

# pyright: reportGeneralTypeIssues=false, reportMissingTypeStubs=false

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from src.database.db_manager import DatabaseManager


@dataclass
class GoalSettings:
    """User-configurable training goals."""

    daily_questions: int = 40
    weekly_sessions: int = 5
    target_accuracy: float = 85.0
    target_avg_time: float = 4.0


class PerformanceTracker:
    """Tracks and analyzes user performance metrics."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_overall_stats(self, days: int | None = None) -> dict[str, float | int]:
        """Get overall performance statistics."""
        stats = self.db.get_performance_stats(days=days)
        stats["current_streak"] = self.db.get_current_streak()
        stats["longest_streak"] = self.db.get_longest_streak()
        return stats

    def get_stats_by_category(self) -> pd.DataFrame:
        """Get performance breakdown by question type."""
        return self.db.get_category_performance()

    def get_stats_by_difficulty(self) -> pd.DataFrame:
        """Get performance breakdown by difficulty level."""
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
        """Get daily trend over the selected number of days."""
        conn = self.db.get_connection()
        cutoff_date = datetime.now() - timedelta(days=days)
        query = """
            SELECT
                DATE(timestamp) as date,
                COUNT(*) as questions,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                CAST(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as accuracy,
                AVG(time_taken_seconds) as avg_time,
                SUM(time_taken_seconds) as total_time
            FROM questions_answered
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """
        df = pd.read_sql_query(
            query,
            conn,
            params=[cutoff_date.strftime("%Y-%m-%d %H:%M:%S")],
        )
        conn.close()

        if df.empty:
            return df

        df["date"] = pd.to_datetime(df["date"])
        df["questions"] = df["questions"].fillna(0).astype(int)
        df["accuracy"] = df["accuracy"].fillna(0.0)
        df["avg_time"] = df["avg_time"].fillna(0.0)
        df["total_time"] = df["total_time"].fillna(0.0)
        return df

    def get_recent_sessions(self, limit: int = 10, days: int | None = None) -> pd.DataFrame:
        """Get recent session summaries."""
        return self.db.get_session_history(limit=limit, days=days)

    def get_time_of_day_performance(self) -> pd.DataFrame:
        """Get performance breakdown by hour of day."""
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

    def identify_weak_areas(self, threshold: float = 0.75) -> list[str]:
        """Identify question types with accuracy below threshold."""
        return self.db.get_weak_areas(threshold)

    def identify_slow_areas(self, threshold: float = 5.0) -> list[str]:
        """Identify question types with average time above threshold."""
        df = self.get_stats_by_category()
        if df.empty:
            return []
        slow = df[df["avg_time"] > threshold]
        return slow["question_type"].tolist()

    def get_session_details(self, session_id: int) -> dict[str, Any] | None:
        """Get detailed information about a specific session."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        session = cursor.fetchone()
        if not session:
            conn.close()
            return None

        query = """
            SELECT * FROM questions_answered
            WHERE session_id = ?
            ORDER BY timestamp
        """
        questions_df = pd.read_sql_query(query, conn, params=[session_id])
        conn.close()
        return {"session": dict(session), "questions": questions_df}

    def get_goal_settings(self) -> GoalSettings:
        """Read persisted goals with defaults."""
        prefs = self.db.get_user_preferences()
        return GoalSettings(
            daily_questions=self._safe_int(prefs.get("goal_daily_questions"), 40),
            weekly_sessions=self._safe_int(prefs.get("goal_weekly_sessions"), 5),
            target_accuracy=self._safe_float(prefs.get("goal_target_accuracy"), 85.0),
            target_avg_time=self._safe_float(prefs.get("goal_target_avg_time"), 4.0),
        )

    def save_goal_settings(self, goals: GoalSettings):
        """Persist goals to user preferences."""
        self.db.set_user_preference("goal_daily_questions", str(goals.daily_questions))
        self.db.set_user_preference("goal_weekly_sessions", str(goals.weekly_sessions))
        self.db.set_user_preference("goal_target_accuracy", f"{goals.target_accuracy:.2f}")
        self.db.set_user_preference("goal_target_avg_time", f"{goals.target_avg_time:.2f}")

    def get_goal_progress(self, lookback_days: int = 7) -> dict[str, float | int | bool]:
        """Calculate progress against personal goals."""
        goals = self.get_goal_settings()
        trend = self.get_historical_trend(days=lookback_days)
        recent_sessions = self.get_recent_sessions(limit=500, days=lookback_days)

        questions_last_week = int(trend["questions"].sum()) if not trend.empty else 0
        sessions_last_week = int(len(recent_sessions.index)) if not recent_sessions.empty else 0

        if not trend.empty:
            weighted_accuracy = float((trend["accuracy"] * trend["questions"]).sum() / max(trend["questions"].sum(), 1))
            avg_time = float((trend["avg_time"] * trend["questions"]).sum() / max(trend["questions"].sum(), 1))
        else:
            weighted_accuracy = 0.0
            avg_time = 0.0

        question_target_week = goals.daily_questions * lookback_days
        session_target_week = goals.weekly_sessions

        question_ratio = min(questions_last_week / max(question_target_week, 1), 2.0)
        session_ratio = min(sessions_last_week / max(session_target_week, 1), 2.0)
        accuracy_ratio = min(weighted_accuracy / max(goals.target_accuracy, 1), 2.0)
        speed_ratio = min(goals.target_avg_time / max(avg_time, 0.1), 2.0) if avg_time > 0 else 0.0

        coaching_score = round((question_ratio + session_ratio + accuracy_ratio + speed_ratio) / 4 * 100, 1)

        return {
            "questions_last_week": questions_last_week,
            "question_target_week": question_target_week,
            "sessions_last_week": sessions_last_week,
            "session_target_week": session_target_week,
            "accuracy_last_week": round(weighted_accuracy, 1),
            "accuracy_target": goals.target_accuracy,
            "avg_time_last_week": round(avg_time, 2),
            "avg_time_target": goals.target_avg_time,
            "question_progress": round(question_ratio * 100, 1),
            "session_progress": round(session_ratio * 100, 1),
            "accuracy_progress": round(accuracy_ratio * 100, 1),
            "speed_progress": round(speed_ratio * 100, 1),
            "coaching_score": coaching_score,
            "goal_hit_questions": questions_last_week >= question_target_week,
            "goal_hit_sessions": sessions_last_week >= session_target_week,
            "goal_hit_accuracy": weighted_accuracy >= goals.target_accuracy,
            "goal_hit_speed": avg_time > 0 and avg_time <= goals.target_avg_time,
        }

    def get_personal_baseline(self, days: int = 30) -> dict[str, float]:
        """Get a baseline profile from historical data."""
        trend = self.get_historical_trend(days=days)
        if trend.empty:
            return {
                "accuracy": 0.0,
                "avg_time": 0.0,
                "daily_questions": 0.0,
                "consistency_days": 0.0,
            }

        total_days = max(days, 1)
        return {
            "accuracy": round(float((trend["accuracy"] * trend["questions"]).sum() / max(trend["questions"].sum(), 1)), 1),
            "avg_time": round(float((trend["avg_time"] * trend["questions"]).sum() / max(trend["questions"].sum(), 1)), 2),
            "daily_questions": round(float(trend["questions"].sum() / total_days), 1),
            "consistency_days": round(float(len(trend.index) / total_days * 100), 1),
        }

    def get_weekly_summary(self, weeks: int = 8) -> pd.DataFrame:
        """Aggregate trends to week-level metrics for analytics charts."""
        days = max(weeks * 7, 7)
        trend = self.get_historical_trend(days=days)
        if trend.empty:
            return trend

        trend = pd.DataFrame(trend).copy()
        trend["week_start"] = trend["date"] - pd.to_timedelta(trend["date"].dt.weekday, unit="D")
        trend["weighted_accuracy"] = trend["accuracy"] * trend["questions"]
        grouped = pd.DataFrame(
            trend.groupby("week_start", as_index=False)
            .agg(
                questions=("questions", "sum"),
                total_time=("total_time", "sum"),
                weighted_acc=("weighted_accuracy", "sum"),
            )
        )
        grouped["accuracy"] = grouped.apply(
            lambda row: row["weighted_acc"] / max(row["questions"], 1),
            axis=1,
        )
        grouped["avg_time"] = grouped.apply(
            lambda row: row["total_time"] / max(row["questions"], 1),
            axis=1,
        )
        result = pd.DataFrame(grouped.loc[:, ["week_start", "questions", "accuracy", "avg_time"]])
        return result

    def get_training_recommendations(self) -> list[dict[str, str]]:
        """Generate focused recommendations for the solo user."""
        recommendations: list[dict[str, str]] = []
        goals = self.get_goal_settings()
        progress = self.get_goal_progress(lookback_days=7)
        baseline = self.get_personal_baseline(days=30)
        weak_areas = self.identify_weak_areas(threshold=0.75)
        slow_areas = self.identify_slow_areas(threshold=5.0)

        if progress["questions_last_week"] < progress["question_target_week"] * 0.7:
            gap = int(progress["question_target_week"] - progress["questions_last_week"])
            recommendations.append(
                {
                    "title": "Raise volume without burning out",
                    "detail": f"You are {gap} questions below your weekly plan. Add one 12-minute sprint on 3 days this week.",
                    "priority": "high",
                }
            )

        if progress["accuracy_last_week"] < goals.target_accuracy:
            recommendations.append(
                {
                    "title": "Stabilize accuracy first",
                    "detail": "Run targeted mode for your weakest category before mixed mode sessions.",
                    "priority": "high",
                }
            )

        if progress["avg_time_last_week"] > goals.target_avg_time and progress["avg_time_last_week"] > 0:
            recommendations.append(
                {
                    "title": "Improve answer speed",
                    "detail": "Use 2-minute sprint with medium difficulty and skip harder questions quickly to keep rhythm.",
                    "priority": "medium",
                }
            )

        if weak_areas:
            focus = ", ".join(area.title() for area in weak_areas[:2])
            recommendations.append(
                {
                    "title": "Focus block",
                    "detail": f"Your lowest-accuracy categories are {focus}. Book two focused sessions this week.",
                    "priority": "medium",
                }
            )

        if slow_areas:
            focus_speed = ", ".join(area.title() for area in slow_areas[:2])
            recommendations.append(
                {
                    "title": "Deliberate speed reps",
                    "detail": f"You are slowest in {focus_speed}. Do 10 rapid-fire reps after each main session.",
                    "priority": "medium",
                }
            )

        if not recommendations:
            recommendations.append(
                {
                    "title": "Excellent momentum",
                    "detail": "You are on plan. Increase difficulty in one session this week to keep progressing.",
                    "priority": "low",
                }
            )

        if baseline["consistency_days"] < 45:
            recommendations.append(
                {
                    "title": "Build consistency",
                    "detail": "Anchor one fixed daily slot. Consistency beats intensity for interview prep speed gains.",
                    "priority": "high",
                }
            )

        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda item: priority_order.get(item["priority"], 3))
        return recommendations[:4]

    @staticmethod
    def _safe_int(value: str | None, fallback: int) -> int:
        try:
            parsed = int(value) if value is not None else fallback
            return parsed if parsed > 0 else fallback
        except ValueError:
            return fallback

    @staticmethod
    def _safe_float(value: str | None, fallback: float) -> float:
        try:
            parsed = float(value) if value is not None else fallback
            return parsed if parsed > 0 else fallback
        except ValueError:
            return fallback
