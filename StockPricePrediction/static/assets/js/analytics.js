// Analytics functionality
let analyticsChart = null;

function initializeAnalytics() {
    // Initialize analytics dashboard elements
    setupChartContainers();
    loadMarketOverview();
    setupEventListeners();
}

function setupChartContainers() {
    const containers = [
        'market-overview-chart',
        'sector-performance-chart',
        'volume-analysis-chart'
    ];
    
    containers.forEach(id => {
        const container = document.getElementById(id);
        if (container) {
            container.style.height = '300px';
        }
    });
}

function loadMarketOverview() {
    fetch('/api/market-overview/')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAnalyticsError('Failed to load market overview');
                return;
            }
            updateMarketOverviewChart(data);
            updateMarketStats(data);
        })
        .catch(error => {
            console.error('Error loading market overview:', error);
            showAnalyticsError('Failed to load market data');
        });
}

function updateMarketOverviewChart(data) {
    const ctx = document.getElementById('market-overview-chart');
    if (!ctx) return;

    if (analyticsChart) {
        analyticsChart.destroy();
    }

    analyticsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Market Index',
                data: data.values,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

function updateMarketStats(data) {
    const statsContainer = document.getElementById('market-stats');
    if (!statsContainer || !data.stats) return;

    const stats = data.stats;
    statsContainer.innerHTML = `
        <div class="stat-item">
            <span class="stat-label">Market Cap</span>
            <span class="stat-value">${formatCurrency(stats.marketCap)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Volume</span>
            <span class="stat-value">${formatNumber(stats.volume)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Advancing Stocks</span>
            <span class="stat-value">${stats.advancing}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Declining Stocks</span>
            <span class="stat-value">${stats.declining}</span>
        </div>
    `;
}

function setupEventListeners() {
    const timeframeButtons = document.querySelectorAll('.timeframe-selector');
    timeframeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const timeframe = button.dataset.timeframe;
            updateTimeframe(timeframe);
        });
    });
}

function updateTimeframe(timeframe) {
    fetch(`/api/market-overview/${timeframe}/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAnalyticsError('Failed to update timeframe');
                return;
            }
            updateMarketOverviewChart(data);
        })
        .catch(error => {
            console.error('Error updating timeframe:', error);
            showAnalyticsError('Failed to update chart');
        });
}

function showAnalyticsError(message) {
    const errorDiv = document.getElementById('analytics-error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function formatNumber(value) {
    return new Intl.NumberFormat('en-US', {
        notation: 'compact',
        compactDisplay: 'short'
    }).format(value);
}

// Initialize analytics when page loads
document.addEventListener('DOMContentLoaded', initializeAnalytics);