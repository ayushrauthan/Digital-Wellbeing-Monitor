# backend/monitor/activity_logger.py
import time
import uuid
from datetime import datetime, date
from ..analysis.usage_analyzer import UsageAnalyzer
from ..analysis.insights_engine import InsightsEngine

class ActivityLogger:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_session = None
        # Create an instance of the analyzer
        self.usage_analyzer = UsageAnalyzer(db_manager)
        self.insights_engine = InsightsEngine(db_manager)

    def log_activity(self, process_info):
        """
        Logs the current user activity. Starts a new session if the
        active application changes.
        """
        if not process_info:
            self.end_current_session()
            return

        app_name = process_info.get('name')
        window_title = process_info.get('title')

        # If there's no current session or the app has changed, start a new session
        if not self.current_session or self.current_session['app_name'] != app_name:
            self.end_current_session()
            self.start_new_session(process_info)
        else:
            # If the app is the same, we just keep the session running.
            pass

    # In backend/monitor/activity_logger.py, update the start_new_session method

    def start_new_session(self, process_info):
        """Starts a new activity session, now with categorization."""
        session_id = str(uuid.uuid4())
        start_time = datetime.now()
        app_name = process_info.get('name')

        # --- THIS IS THE NEW PART ---
        # Get category details from the database
        category_info = self.db_manager.get_app_category(app_name)

        self.current_session = {
            'session_id': session_id,
            'app_name': app_name,
            'app_path': process_info.get('path'),
            'window_title': process_info.get('title'),
            'category': category_info['category'], # <-- Use fetched category
            'start_timestamp': start_time,
            'productivity_score': category_info['productivity_score'] # <-- Use fetched score
        }
        self.db_manager.add_session(self.current_session)
        print(f"Starting new session for: {self.current_session['app_name']} (Category: {self.current_session['category']})")

    def end_current_session(self):
        """Ends the current activity session and updates the database."""
        if self.current_session:
            end_time = datetime.now()
            start_time = self.current_session['start_timestamp']
            duration = (end_time - start_time).total_seconds()

            self.db_manager.update_session_end_time(
                self.current_session['session_id'],
                end_time,
                duration
            )
            print(f"Ending session for: {self.current_session['app_name']} (Duration: {duration:.2f}s)")

            # After ending a session, update today's statistics
            self.usage_analyzer.aggregate_daily_stats(date.today())
            self.insights_engine.generate_insights()

            self.current_session = None