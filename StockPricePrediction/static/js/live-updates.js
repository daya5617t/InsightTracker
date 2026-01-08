/**
 * Live Stock Price Updates using Polling
 * Updates prices and charts in real-time
 */

class LiveStockUpdates {
    constructor(options = {}) {
        this.tickers = options.tickers || [];
        this.updateInterval = options.updateInterval || 5000; // 5 seconds default
        this.charts = options.charts || {};
        this.priceElements = options.priceElements || {};
        this.marketStatusElements = options.marketStatusElements || {};
        this.isRunning = false;
        this.updateTimer = null;
        this.maxDataPoints = 100; // Maximum data points to keep in charts
    }

    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this.updatePrices();
        this.updateTimer = setInterval(() => this.updatePrices(), this.updateInterval);
    }

    stop() {
        if (!this.isRunning) return;
        this.isRunning = false;
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    async updatePrices() {
        if (this.tickers.length === 0) return;

        try {
            // Batch update for multiple tickers
            const tickersStr = this.tickers.join(',');
            const response = await fetch(`/api/live-prices-batch/?tickers=${tickersStr}`);
            const data = await response.json();

            if (data.success && data.results) {
                for (const [ticker, priceData] of Object.entries(data.results)) {
                    if (priceData.error) {
                        console.error(`Error fetching ${ticker}:`, priceData.error);
                        continue;
                    }

                    // Update price display
                    this.updatePriceDisplay(ticker, priceData);

                    // Update charts
                    this.updateChart(ticker, priceData);

                    // Update market status
                    this.updateMarketStatus(ticker);
                }
            }
        } catch (error) {
            console.error('Error updating prices:', error);
        }
    }

    async updateSingleTicker(ticker) {
        try {
            const response = await fetch(`/api/live-price/?ticker=${ticker}`);
            const data = await response.json();

            if (data.success) {
                this.updatePriceDisplay(ticker, data);
                this.updateChart(ticker, data);
                this.updateMarketStatus(ticker, data.market_status);
            }
        } catch (error) {
            console.error(`Error updating ${ticker}:`, error);
        }
    }

    updatePriceDisplay(ticker, data) {
        const elements = this.priceElements[ticker] || {};
        
        // Update price
        if (elements.price) {
            elements.price.textContent = `$${data.price.toFixed(2)}`;
            // Add animation
            elements.price.classList.add('price-update');
            setTimeout(() => elements.price.classList.remove('price-update'), 500);
        }

        // Update change
        if (elements.change) {
            const changeText = data.change >= 0 ? `+${data.change.toFixed(2)}` : data.change.toFixed(2);
            elements.change.textContent = changeText;
            elements.change.className = data.change >= 0 ? 'text-success' : 'text-danger';
        }

        // Update change percent
        if (elements.changePercent) {
            const changePercentText = data.change_percent >= 0 
                ? `+${data.change_percent.toFixed(2)}%` 
                : `${data.change_percent.toFixed(2)}%`;
            elements.changePercent.textContent = changePercentText;
            elements.changePercent.className = data.change_percent >= 0 ? 'text-success' : 'text-danger';
        }

        // Update volume
        if (elements.volume) {
            elements.volume.textContent = this.formatNumber(data.volume);
        }

        // Update high/low
        if (elements.high) {
            elements.high.textContent = `$${data.high.toFixed(2)}`;
        }
        if (elements.low) {
            elements.low.textContent = `$${data.low.toFixed(2)}`;
        }
    }

    updateChart(ticker, data) {
        const chart = this.charts[ticker];
        if (!chart) return;

        try {
            const now = new Date();
            const label = now.toLocaleTimeString();

            // Add new data point
            chart.data.labels.push(label);
            chart.data.datasets[0].data.push(data.price);

            // Limit data points
            if (chart.data.labels.length > this.maxDataPoints) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }

            // Update chart
            chart.update('none'); // 'none' mode for smooth updates without animation
        } catch (error) {
            console.error(`Error updating chart for ${ticker}:`, error);
        }
    }

    async updateMarketStatus(ticker, marketStatus = null) {
        if (!marketStatus) {
            try {
                const response = await fetch(`/api/market-status/?ticker=${ticker}`);
                marketStatus = await response.json();
            } catch (error) {
                console.error(`Error fetching market status for ${ticker}:`, error);
                return;
            }
        }

        const element = this.marketStatusElements[ticker];
        if (!element) return;

        const isOpen = marketStatus.is_open;
        const status = marketStatus.status;
        const message = marketStatus.message;

        element.innerHTML = `
            <span class="market-status-badge ${isOpen ? 'market-open' : 'market-closed'}">
                <i class="fas ${isOpen ? 'fa-circle' : 'fa-circle'}"></i>
                ${isOpen ? 'Market Open' : 'Market Closed'}
            </span>
            <small class="text-muted d-block mt-1">${message}</small>
        `;
    }

    formatNumber(num) {
        if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
        return num.toString();
    }

    addTicker(ticker) {
        if (!this.tickers.includes(ticker)) {
            this.tickers.push(ticker);
        }
    }

    removeTicker(ticker) {
        this.tickers = this.tickers.filter(t => t !== ticker);
    }
}

// Global instance
window.liveStockUpdates = window.liveStockUpdates || new LiveStockUpdates();

// Auto-initialize if tickers are provided via data attributes
document.addEventListener('DOMContentLoaded', function() {
    const liveUpdateElements = document.querySelectorAll('[data-live-update]');
    
    liveUpdateElements.forEach(element => {
        const ticker = element.getAttribute('data-ticker');
        const updateInterval = parseInt(element.getAttribute('data-interval')) || 5000;
        
        if (ticker) {
            window.liveStockUpdates.addTicker(ticker);
            
            // Set up price elements
            if (!window.liveStockUpdates.priceElements[ticker]) {
                window.liveStockUpdates.priceElements[ticker] = {};
            }
            
            const priceEl = element.querySelector('[data-price]');
            const changeEl = element.querySelector('[data-change]');
            const changePercentEl = element.querySelector('[data-change-percent]');
            const volumeEl = element.querySelector('[data-volume]');
            const highEl = element.querySelector('[data-high]');
            const lowEl = element.querySelector('[data-low]');
            
            if (priceEl) window.liveStockUpdates.priceElements[ticker].price = priceEl;
            if (changeEl) window.liveStockUpdates.priceElements[ticker].change = changeEl;
            if (changePercentEl) window.liveStockUpdates.priceElements[ticker].changePercent = changePercentEl;
            if (volumeEl) window.liveStockUpdates.priceElements[ticker].volume = volumeEl;
            if (highEl) window.liveStockUpdates.priceElements[ticker].high = highEl;
            if (lowEl) window.liveStockUpdates.priceElements[ticker].low = lowEl;
            
            // Set up market status element
            const statusEl = element.querySelector('[data-market-status]');
            if (statusEl) {
                window.liveStockUpdates.marketStatusElements[ticker] = statusEl;
            }
            
            window.liveStockUpdates.updateInterval = updateInterval;
        }
    });
    
    // Start updates if we have tickers
    if (window.liveStockUpdates.tickers.length > 0) {
        window.liveStockUpdates.start();
    }
});

