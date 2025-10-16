// The base URL of your Flask backend
const API_BASE_URL = 'http://127.0.0.1:5000';

/**
 * Fetches the most recent session data.
 * @returns {Promise<Object>} A promise that resolves to the session data.
 */
async function fetchLatestSession() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/sessions`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const sessions = await response.json();
        // The API returns the latest sessions first, so we take the very first one.
        return sessions.length > 0 ? sessions[0] : null;
    } catch (error) {
        console.error("Could not fetch session data:", error);
        return null;
    }
}

/**
 * Fetches the aggregated statistics for today.
 * @returns {Promise<Object>} A promise that resolves to the daily stats.
 */
async function fetchDailyStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/daily-stats`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const stats = await response.json();
        // The API returns stats for the last 7 days, so we take the first entry which is today.
        return stats.length > 0 ? stats[0] : null;
    } catch (error) {
        console.error("Could not fetch daily stats:", error);
        return null;
    }
}