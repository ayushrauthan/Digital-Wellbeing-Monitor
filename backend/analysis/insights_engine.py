# backend/analysis/insights_engine.py
from datetime import datetime, timedelta, date
from ..utils.notifier import NotificationManager

class InsightsEngine:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.notifier = NotificationManager()

    def generate_insights(self):
        """Runs all insight generation rules."""
        self._check_for_long_sessions()
        # We will add more rules here in the future, like checking for late-night usage.

    # In backend/analysis/insights_engine.py, replace this entire method

    def _check_for_long_sessions(self):
        """Checks for long productive sessions and generates an insight."""
        today_stats = self.db_manager.get_daily_stats_for_date(date.today())

        # For testing, you can use a shorter time like (1 * 30)
        if today_stats and today_stats['productive_time'] > (1 * 30):
            insight_exists = self.db_manager.check_insight_exists(
                insight_type='LONG_SESSION', 
                for_date=date.today()
            )

            if not insight_exists:
                insight_data = {
                    'insight_type': 'LONG_SESSION',
                    'insight_title': 'Time for a Break!',
                    'insight_description': 'You have been working hard. Remember to take short breaks to stretch and rest your eyes.',
                    'generated_date': date.today()
                }
                self.db_manager.add_health_insight(insight_data)
                print("Generated new insight: Time for a Break!")

                # --- THIS IS NOW IN THE CORRECT PLACE ---
                # It will only run IF a new insight is created.
                self.notifier.send_notification(
                    title=insight_data['insight_title'],
                    message=insight_data['insight_description']
                )