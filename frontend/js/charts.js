document.addEventListener('DOMContentLoaded', () => {
    // DEBUG 1: Check if the script is running at all.
    console.log("charts.js script loaded and running.");

    const ctx = document.getElementById('categoryChart').getContext('2d');
    let categoryChart = null; // Variable to hold the chart instance

    async function createOrUpdateChart() {
        const dailyStats = await fetchDailyStats();

        // DEBUG 2: See what data we received from the backend.
        console.log("Fetched daily stats:", dailyStats);

        if (dailyStats) {
            // DEBUG 3: Confirm that we are entering the block to draw the chart.
            console.log("Daily stats exist. Creating or updating chart.");

            // Convert seconds to minutes for easier reading
            const productiveMinutes = (dailyStats.productive_time / 60);
            const socialMinutes = (dailyStats.social_time / 60);
            const utilityMinutes = (dailyStats.utility_time / 60);
            const entertainmentMinutes = (dailyStats.entertainment_time / 60);

            const chartData = {
                labels: ['Productive', 'Social', 'Utility', 'Entertainment'],
                datasets: [{
                    label: 'Time Spent (in minutes)',
                    data: [productiveMinutes, socialMinutes, utilityMinutes, entertainmentMinutes],
                    backgroundColor: [
                        '#5CB85C', // Success Green
                        '#A23B72', // Secondary Purple
                        '#2E86AB', // Primary Blue
                        '#F0AD4E', // Warning Orange
                    ],
                    borderWidth: 1
                }]
            };

            // If the chart doesn't exist yet, create it
            if (!categoryChart) {
                categoryChart = new Chart(ctx, {
                    type: 'bar',
                    data: chartData,
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: 'Minutes' }
                            }
                        },
                        responsive: true
                    }
                });
            } else {
                // If it already exists, just update its data for a smooth refresh
                categoryChart.data = chartData;
                categoryChart.update();
            }
        }
    }
    
    // Create the chart when the page first loads
    createOrUpdateChart();
    // Set it to automatically update every 10 seconds
    setInterval(createOrUpdateChart, 10000);
});