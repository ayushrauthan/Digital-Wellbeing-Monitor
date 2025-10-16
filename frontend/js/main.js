// Wait until the entire HTML page is loaded before running the script.
document.addEventListener('DOMContentLoaded', () => {
    // Get references to the HTML elements we want to update.
    const currentAppElement = document.getElementById('current-app');
    const activeTimeElement = document.getElementById('active-time');
    const prodScoreElement = document.getElementById('prod-score');

    /**
     * A helper function to format seconds into a more readable "Xh Ym" format.
     * @param {number} totalSeconds - The total seconds to format.
     * @returns {string} The formatted time string.
     */
    function formatTime(totalSeconds) {
        if (isNaN(totalSeconds) || totalSeconds < 0) {
            return '0h 0m';
        }
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }

    /**
     * The main function to update all dashboard data.
     */
    async function updateDashboard() {
        // Fetch the latest session data from the API.
        const latestSession = await fetchLatestSession();
        if (latestSession && latestSession.length > 0) {
            // The API returns an array: [app_name, window_title, duration]
            const appName = latestSession[0];
            currentAppElement.textContent = appName || 'No active application';
        } else {
            currentAppElement.textContent = 'Idle';
        }

        // Fetch the daily statistics from the API.
        const dailyStats = await fetchDailyStats();
        if (dailyStats) {
            activeTimeElement.textContent = formatTime(dailyStats.total_active_time);
            // Format the productivity score to two decimal places.
            prodScoreElement.textContent = dailyStats.productivity_score.toFixed(2);
        } else {
            activeTimeElement.textContent = '0h 0m';
            prodScoreElement.textContent = '--';
        }
    }

    // Run the update function immediately when the page loads.
    updateDashboard();

    // And then, set it to run again every 5 seconds to keep the data fresh.
    setInterval(updateDashboard, 5000); // 5000 milliseconds = 5 seconds
});