# backend/analysis/usage_analyzer.py
from datetime import date

class UsageAnalyzer:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def aggregate_daily_stats(self, for_date=None):
        # ... (this part remains the same)
        if for_date is None:
            for_date = date.today()

        print(f"Aggregating daily statistics for: {for_date}")
        self.db_manager.aggregate_daily_stats(for_date)

        # --- ADD THIS CALL ---
        # After aggregating, update the goal progress
        self._update_all_goal_progress()

    def _update_all_goal_progress(self):
        """Fetches all active goals and updates their progress."""
        print("Updating goal progress...")
        goals = self.db_manager.get_active_goals()
        today_stats = self.db_manager.get_daily_stats_for_date(date.today())

        if not today_stats:
            return # Can't update goals if there are no stats for today

        for goal in goals:
            # This logic checks what kind of goal it is
            if goal['goal_type'] == 'MAX_TIME_CATEGORY':
                # The 'target_unit' tells us which column to look at in daily_statistics
                # e.g., 'social_time'
                category_time = today_stats.get(goal['target_unit'], 0)
                self.db_manager.update_goal_progress(goal['id'], category_time)