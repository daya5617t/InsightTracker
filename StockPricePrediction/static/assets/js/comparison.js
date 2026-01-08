// Stock comparison functionality
let comparisonChart = null;

function initializeComparison() {
    const stock1Input = document.getElementById('stock1');
    const stock2Input = document.getElementById('stock2');
    const compareBtn = document.getElementById('compare-btn');
    
    if (compareBtn) {
        compareBtn.addEventListener('click', () => {
            const stock1 = stock1Input.value;
            const stock2 = stock2Input.value;
            if (stock1 && stock2) {
                compareStocks(stock1, stock2);
            }
        });
    }
}

function compareStocks(stock1, stock2) {
    showLoader();
    
    // Fetch data for both stocks
    Promise.all([
        fetch(`/api/live-price/?ticker=${stock1}`).then(res => res.json()),
        fetch(`/api/live-price/?ticker=${stock2}`).then(res => res.json())
    ])
    .then(([data1, data2]) => {
        if (data1.success && data2.success) {
            updateComparisonUI(data1, data2);
            createComparisonChart(data1, data2);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Failed to fetch comparison data');
    })
    .finally(() => {
        hideLoader();
    });
}

function updateComparisonUI(data1, data2) {
    // Update metrics
    document.getElementById('stock1-price').textContent = `$${data1.price}`;
    document.getElementById('stock2-price').textContent = `$${data2.price}`;
    
    document.getElementById('stock1-change').textContent = 
        `${data1.change >= 0 ? '+' : ''}${data1.change}%`;
    document.getElementById('stock2-change').textContent = 
        `${data2.change >= 0 ? '+' : ''}${data2.change}%`;
    
    document.getElementById('stock1-volume').textContent = data1.volume.toLocaleString();
    document.getElementById('stock2-volume').textContent = data2.volume.toLocaleString();
}

function createComparisonChart(data1, data2) {
    const ctx = document.getElementById('comparison-chart').getContext('2d');
    
    if (comparisonChart) {
        comparisonChart.destroy();
    }
    
    comparisonChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: generateTimeLabels(),
            datasets: [
                {
                    label: data1.ticker,
                    data: normalizeData(data1.history),
                    borderColor: '#f59e0b',
                    tension: 0.4
                },
                {
                    label: data2.ticker,
                    data: normalizeData(data2.history),
                    borderColor: '#10b981',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

function generateTimeLabels() {
    const labels = [];
    const now = new Date();
    for (let i = 30; i >= 0; i--) {
        labels.push(new Date(now - i * 86400000).toLocaleDateString());
    }
    return labels;
}

function normalizeData(data) {
    if (!data || !data.length) {
        return Array(31).fill(null);
    }
    const baseValue = data[0];
    return data.map(value => (value / baseValue * 100));
}

function showLoader() {
    const loader = document.getElementById('comparison-loader');
    if (loader) loader.style.display = 'block';
}

function hideLoader() {
    const loader = document.getElementById('comparison-loader');
    if (loader) loader.style.display = 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('comparison-error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

// Initialize comparison functionality when page loads
document.addEventListener('DOMContentLoaded', initializeComparison);