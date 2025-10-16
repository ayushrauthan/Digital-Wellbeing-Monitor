# backend/database/db_manager.py
from datetime import datetime, date
import sqlite3
import os

class DatabaseManager:
    """Manages the SQLite database connection and table creation."""
    
    # --- CORRECTED __INIT__ METHOD ---
    def __init__(self, db_path='data', db_name='wellness.db'):
        """Initializes the database manager, creates tables, and seeds initial data."""
        # Ensure the data directory exists
        os.makedirs(db_path, exist_ok=True)
        # This line creates the db_filepath attribute needed by other methods
        self.db_filepath = os.path.join(db_path, db_name)
        
        # Call all setup methods in the correct order
        self._create_tables()
        self._seed_initial_categories()
        self._seed_initial_goals()

    def _get_connection(self):
        """Creates and returns a new database connection."""
        return sqlite3.connect(self.db_filepath)

    def _create_tables(self):
        """Creates all necessary tables if they don't already exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 1. activity_sessions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            app_name TEXT NOT NULL,
            app_path TEXT,
            window_title TEXT,
            category TEXT NOT NULL,
            start_timestamp DATETIME NOT NULL,
            end_timestamp DATETIME,
            duration_seconds INTEGER,
            cpu_usage_avg REAL,
            memory_usage_avg REAL,
            productivity_score REAL,
            break_taken BOOLEAN DEFAULT 0,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. daily_statistics Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_statistics (
            date DATE PRIMARY KEY,
            total_active_time INTEGER NOT NULL,
            productive_time INTEGER DEFAULT 0,
            social_time INTEGER DEFAULT 0,
            entertainment_time INTEGER DEFAULT 0,
            utility_time INTEGER DEFAULT 0,
            break_time INTEGER DEFAULT 0,
            number_of_breaks INTEGER DEFAULT 0,
            app_switches INTEGER DEFAULT 0,
            productivity_score REAL DEFAULT 0.0,
            wellbeing_score REAL DEFAULT 0.0,
            longest_session_minutes INTEGER DEFAULT 0,
            most_used_app TEXT,
            total_applications INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. application_categories Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS application_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            app_path TEXT,
            category TEXT NOT NULL,
            productivity_weight REAL DEFAULT 1.0,
            is_user_defined BOOLEAN DEFAULT 0,
            auto_classified BOOLEAN DEFAULT 1,
            classification_confidence REAL DEFAULT 1.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(app_name, app_path)
        );
        """)

        # 4. user_settings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            data_type TEXT DEFAULT 'string',
            category TEXT DEFAULT 'general',
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 5. health_insights Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insight_type TEXT NOT NULL,
            insight_title TEXT NOT NULL,
            insight_description TEXT NOT NULL,
            priority_level INTEGER DEFAULT 1,
            is_actionable BOOLEAN DEFAULT 1,
            action_taken BOOLEAN DEFAULT 0,
            generated_date DATE NOT NULL,
            expiry_date DATE,
            data_source TEXT,
            confidence_score REAL DEFAULT 1.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 6. break_sessions Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS break_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            break_type TEXT NOT NULL,
            start_timestamp DATETIME NOT NULL,
            end_timestamp DATETIME,
            duration_seconds INTEGER,
            was_scheduled BOOLEAN DEFAULT 0,
            user_rating INTEGER,
            break_activity TEXT,
            effectiveness_score REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 7. productivity_goals Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS productivity_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_name TEXT NOT NULL,
            goal_type TEXT NOT NULL,
            target_value REAL NOT NULL,
            target_unit TEXT NOT NULL,
            current_value REAL DEFAULT 0.0,
            start_date DATE NOT NULL,
            end_date DATE,
            is_active BOOLEAN DEFAULT 1,
            achievement_date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 8. system_metrics Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            cpu_usage_percent REAL,
            memory_usage_percent REAL,
            disk_usage_percent REAL,
            active_processes INTEGER,
            system_load_avg REAL,
            temperature_celsius REAL,
            battery_percent REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()
        conn.close()
        print("Database and tables created successfully.")
    
    def _seed_initial_categories(self):
        """Seeds the database with some default application categories."""
        default_apps = [
            ('Notepad.exe', 'Productive', 1.5),
            ('Code.exe', 'Productive', 1.5),
            ('cmd.exe', 'Utility', 1.0),
            ('explorer.exe', 'Utility', 1.0),
            ('chrome.exe', 'Social', -1.0),
            ('msedge.exe', 'Social', -1.0),
            ('firefox.exe', 'Social', -1.0)
        ]
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT OR IGNORE INTO application_categories (app_name, category, productivity_weight)
            VALUES (?, ?, ?)
        """, default_apps)
        conn.commit()
        conn.close()
        print("Initial categories seeded.")

    def _seed_initial_goals(self):
        """Seeds the database with a default productivity goal."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM productivity_goals LIMIT 1")
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO productivity_goals (goal_name, goal_type, target_value, target_unit, start_date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                'Limit Social Media', 
                'MAX_TIME_CATEGORY', 
                3600, 
                'social_time', 
                date.today()
            ))
            conn.commit()
            print("Default goal seeded.")
        conn.close()

    def add_session(self, session_data):
        """Adds a new activity session to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO activity_sessions (session_id, app_name, app_path, window_title, category, start_timestamp, productivity_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data['session_id'],
            session_data['app_name'],
            session_data['app_path'],
            session_data['window_title'],
            session_data['category'],
            session_data['start_timestamp'],
            session_data['productivity_score']
        ))
        conn.commit()
        conn.close()

    def update_session_end_time(self, session_id, end_time, duration):
        """Updates the end time and duration of a session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE activity_sessions
            SET end_timestamp = ?, duration_seconds = ?, updated_at = ?
            WHERE session_id = ?
        """, (end_time, duration, datetime.now(), session_id))
        conn.commit()
        conn.close()
    
    def aggregate_daily_stats(self, for_date):
        """Calculates and saves detailed statistics for a given date."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_statistics (
                date, total_active_time, productive_time, social_time, 
                entertainment_time, utility_time, productivity_score
            )
            SELECT
                DATE(start_timestamp) as stat_date,
                SUM(duration_seconds) as total_duration,
                SUM(CASE WHEN category = 'Productive' THEN duration_seconds ELSE 0 END) as productive,
                SUM(CASE WHEN category = 'Social' THEN duration_seconds ELSE 0 END) as social,
                SUM(CASE WHEN category = 'Entertainment' THEN duration_seconds ELSE 0 END) as entertainment,
                SUM(CASE WHEN category = 'Utility' THEN duration_seconds ELSE 0 END) as utility,
                SUM(duration_seconds * productivity_score) / SUM(duration_seconds) as avg_prod_score
            FROM
                activity_sessions
            WHERE
                DATE(start_timestamp) = ? AND duration_seconds IS NOT NULL
            GROUP BY
                stat_date
            ON CONFLICT(date) DO UPDATE SET
                total_active_time = excluded.total_active_time,
                productive_time = excluded.productive_time,
                social_time = excluded.social_time,
                entertainment_time = excluded.entertainment_time,
                utility_time = excluded.utility_time,
                productivity_score = excluded.productivity_score;
        """, (for_date,))
        conn.commit()
        conn.close()

    def get_app_category(self, app_name):
        """Retrieves the category for a given application name."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category, productivity_weight FROM application_categories WHERE app_name = ?", (app_name,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {'category': result[0], 'productivity_score': result[1]}
        return {'category': 'Uncategorized', 'productivity_score': 0}
    
    def get_daily_stats_for_date(self, for_date):
        """Fetches the daily statistics for a specific date."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_statistics WHERE date = ?", (for_date,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def check_insight_exists(self, insight_type, for_date):
        """Checks if a specific type of insight already exists for a given date."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM health_insights WHERE insight_type = ? AND generated_date = ?", (insight_type, for_date))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def add_health_insight(self, insight_data):
        """Adds a new health insight to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO health_insights (insight_type, insight_title, insight_description, generated_date)
            VALUES (?, ?, ?, ?)
        """, (
            insight_data['insight_type'],
            insight_data['insight_title'],
            insight_data['insight_description'],
            insight_data['generated_date']
        ))
        conn.commit()
        conn.close()

    def get_active_goals(self):
        """Retrieves all active goals from the database."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productivity_goals WHERE is_active = 1")
        goals = cursor.fetchall()
        conn.close()
        return [dict(goal) for goal in goals]

    def update_goal_progress(self, goal_id, current_value):
        """Updates the current value of a specific goal."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE productivity_goals
            SET current_value = ?, updated_at = ?
            WHERE id = ?
        """, (current_value, datetime.now(), goal_id))
        conn.commit()
        conn.close()