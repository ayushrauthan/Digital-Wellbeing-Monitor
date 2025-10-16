# backend/monitor/system_monitor.py

import threading
import time
from .process_tracker import get_active_process_info
from .activity_logger import ActivityLogger

class SystemMonitor:
    def __init__(self, db_manager):
        self.stop_event = threading.Event()
        # Pass the db_manager instance to the logger
        self.activity_logger = ActivityLogger(db_manager)
        self.monitor_thread = threading.Thread(target=self._monitor_activity, daemon=True)

    def _monitor_activity(self):
        """The main monitoring loop that tracks the active window."""
        print("System monitor thread started.")
        while not self.stop_event.is_set():
            active_process = get_active_process_info()
            print(f"DEBUG: Active Process Info = {active_process}")
            self.activity_logger.log_activity(active_process)
            
            # Check for activity every 3 seconds
            time.sleep(3) 
        
        # When stopping, make sure to end the last session
        self.activity_logger.end_current_session()
        print("System monitor thread stopped.")

    def start(self):
        """Starts the monitoring thread."""
        if not self.monitor_thread.is_alive():
            self.monitor_thread.start()

    def stop(self):
        """Stops the monitoring thread gracefully."""
        self.stop_event.set()
        self.monitor_thread.join()