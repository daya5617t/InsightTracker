// Live updates for stock data
function updateStockPrice(ticker) {
    fetch(`/api/live-price/?ticker=${ticker}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`${ticker}-price`).textContent = `$${data.price}`;
                document.getElementById(`${ticker}-change`).textContent = 
                    `${data.change >= 0 ? '+' : ''}${data.change} (${data.change_percent}%)`;
                document.getElementById(`${ticker}-change`).className = 
                    `change ${data.change >= 0 ? 'positive' : 'negative'}`;
                document.getElementById(`${ticker}-volume`).textContent = data.volume.toLocaleString();
                document.getElementById(`${ticker}-high`).textContent = `$${data.high}`;
                document.getElementById(`${ticker}-low`).textContent = `$${data.low}`;
                document.getElementById(`${ticker}-timestamp`).textContent = data.timestamp;
            }
        })
        .catch(error => console.error('Error:', error));
}

// Update multiple stocks in batch
function updateMultipleStocks(tickers) {
    fetch(`/api/live-prices-batch/?tickers=${tickers.join(',')}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Object.entries(data.data).forEach(([ticker, info]) => {
                    if (!info.error) {
                        updateStockUI(ticker, info);
                    }
                });
            }
        })
        .catch(error => console.error('Error:', error));
}

// Update UI elements for a stock
function updateStockUI(ticker, info) {
    const elements = {
        price: document.getElementById(`${ticker}-price`),
        change: document.getElementById(`${ticker}-change`),
        timestamp: document.getElementById(`${ticker}-timestamp`)
    };

    if (elements.price) elements.price.textContent = `$${info.price}`;
    if (elements.change) {
        elements.change.textContent = `${info.change >= 0 ? '+' : ''}${info.change} (${info.change_percent}%)`;
        elements.change.className = `change ${info.change >= 0 ? 'positive' : 'negative'}`;
    }
    if (elements.timestamp) elements.timestamp.textContent = info.timestamp;
}

// Start periodic updates
function startLiveUpdates(ticker, interval = 5000) {
    updateStockPrice(ticker);
    return setInterval(() => updateStockPrice(ticker), interval);
}

// Market status check
function checkMarketStatus(ticker) {
    fetch(`/api/market-status/?ticker=${ticker}`)
        .then(response => response.json())
        .then(data => {
            const statusElement = document.getElementById('market-status');
            if (statusElement) {
                statusElement.textContent = data.message;
                statusElement.className = `status ${data.is_open ? 'open' : 'closed'}`;
            }
        })
        .catch(error => console.error('Error:', error));
}