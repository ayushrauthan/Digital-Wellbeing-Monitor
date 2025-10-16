# backend/app.py
import sqlite3
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from .database.db_manager import DatabaseManager
from .monitor.system_monitor import SystemMonitor

system_monitor = None
db_manager = None 

def create_app():
    # --- THIS LINE IS CORRECTED ---
    # We explicitly tell Flask that the static files (CSS, JS) are served from the root URL.
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    
    CORS(app)
    
    global db_manager, system_monitor
    
    db_manager = DatabaseManager()
    system_monitor = SystemMonitor(db_manager)
    system_monitor.start()

    # This route will now serve your main index.html file
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    # --- YOUR EXISTING API ROUTES REMAIN THE SAME ---
    @app.route('/api/sessions')
    def get_sessions():
        conn = db_manager._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT app_name, window_title, duration_seconds FROM activity_sessions ORDER BY start_timestamp DESC LIMIT 10")
        sessions = cursor.fetchall()
        conn.close()
        return jsonify(sessions)

    @app.route('/api/daily-stats')
    def get_daily_stats():
        conn = db_manager._get_connection()
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, total_active_time, productive_time, social_time, 
                   entertainment_time, utility_time, productivity_score 
            FROM daily_statistics 
            ORDER BY date DESC LIMIT 7
        """)
        stats = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in stats])

    @app.route('/api/health-insights')
    def get_health_insights():
        conn = db_manager._get_connection()
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute("SELECT insight_title, insight_description, generated_date FROM health_insights ORDER BY generated_date DESC LIMIT 10")
        insights = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in insights])

    @app.route('/api/goals')
    def get_goals():
        goals = db_manager.get_active_goals()
        return jsonify(goals)

    return app