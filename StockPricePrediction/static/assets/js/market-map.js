// Global Market Map functionality
let marketMap = null;
let markersLayer = null;

function initializeMap() {
    // Initialize the map centered on the world view
    marketMap = L.map('market-map').setView([20, 0], 2);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(marketMap);
    
    // Create a layer for market indicators
    markersLayer = L.layerGroup().addTo(marketMap);
    
    // Load market data
    loadGlobalMarketData();
}

function loadGlobalMarketData() {
    fetch('/api/global-markets/')
        .then(response => response.json())
        .then(data => {
            updateMarketIndicators(data);
        })
        .catch(error => {
            console.error('Error loading global market data:', error);
            showMapError('Failed to load global market data');
        });
}

function updateMarketIndicators(data) {
    // Clear existing markers
    markersLayer.clearLayers();
    
    // Market locations and their coordinates
    const markets = {
        'NYSE': [40.7128, -74.0060],
        'NASDAQ': [40.7589, -73.9851],
        'LSE': [51.5074, -0.1278],
        'TSE': [35.6762, 139.6503],
        'SSE': [31.2304, 121.4737],
        'HKEX': [22.3193, 114.1694],
        'FSE': [50.1109, 8.6821],
        'BSE': [18.9257, 72.8353]
    };
    
    // Add market indicators to the map
    Object.entries(data.markets).forEach(([market, info]) => {
        if (markets[market]) {
            const [lat, lng] = markets[market];
            const status = info.change >= 0 ? 'up' : 'down';
            const change = info.change.toFixed(2);
            
            const marker = L.marker([lat, lng])
                .bindPopup(`
                    <strong>${market}</strong><br>
                    Index: ${info.index}<br>
                    Change: <span class="${status}">${change}%</span><br>
                    Volume: ${formatNumber(info.volume)}
                `);
            
            markersLayer.addLayer(marker);
        }
    });
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US', {
        notation: 'compact',
        compactDisplay: 'short'
    }).format(num);
}

function showMapError(message) {
    const errorDiv = document.getElementById('analytics-error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

// Initialize map when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const mapContainer = document.getElementById('market-map');
    if (mapContainer) {
        initializeMap();
        
        // Refresh data every 5 minutes
        setInterval(loadGlobalMarketData, 300000);
    }
});