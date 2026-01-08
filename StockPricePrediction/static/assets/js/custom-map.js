// Custom Geographic Map Visualization (No Plotly Required)

class CustomGeographicMap {
    constructor(containerId, data) {
        this.container = document.getElementById(containerId);
        this.data = data || [];
        this.width = 0;
        this.height = 0;
        this.init();
    }

    init() {
        if (!this.container) return;
        
        this.width = this.container.offsetWidth || 800;
        this.height = this.container.offsetHeight || 600;
        
        // Country coordinates (simplified world map positions)
        this.countryCoords = {
            'United States': { x: 0.25, y: 0.35 },
            'India': { x: 0.65, y: 0.55 },
            'China': { x: 0.75, y: 0.40 },
            'Japan': { x: 0.85, y: 0.40 },
            'United Kingdom': { x: 0.48, y: 0.25 },
            'Canada': { x: 0.25, y: 0.20 },
            'Germany': { x: 0.52, y: 0.30 },
            'France': { x: 0.50, y: 0.30 },
            'Brazil': { x: 0.35, y: 0.70 },
            'Australia': { x: 0.80, y: 0.80 },
            'Netherlands': { x: 0.51, y: 0.28 },
            'Switzerland': { x: 0.52, y: 0.32 },
            'Taiwan': { x: 0.78, y: 0.45 },
            'South Korea': { x: 0.82, y: 0.40 },
            'Mexico': { x: 0.20, y: 0.50 },
            'Argentina': { x: 0.32, y: 0.85 },
            'South Africa': { x: 0.55, y: 0.90 },
            'Spain': { x: 0.48, y: 0.35 },
            'Italy': { x: 0.53, y: 0.33 },
            'Sweden': { x: 0.54, y: 0.20 },
            'Norway': { x: 0.53, y: 0.18 },
            'Denmark': { x: 0.52, y: 0.26 },
            'Hong Kong': { x: 0.77, y: 0.45 },
            'Singapore': { x: 0.75, y: 0.60 }
        };

        this.render();
    }

    getColor(performance) {
        if (performance >= 5) return '#22c55e'; // Green
        if (performance >= 0) return '#84cc16'; // Light green
        if (performance >= -2) return '#eab308'; // Yellow
        return '#ef4444'; // Red
    }

    getSize(count) {
        return Math.max(8, Math.min(30, count * 1.5));
    }

    render() {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        svg.setAttribute('viewBox', '0 0 1000 600');
        svg.style.background = 'var(--bg-secondary)';
        svg.style.borderRadius = 'var(--radius-lg)';

        // Create world map background (simplified continents)
        this.drawContinents(svg);

        // Draw country markers
        this.data.forEach(country => {
            const coords = this.countryCoords[country.country];
            if (!coords) return;

            const x = coords.x * 1000;
            const y = coords.y * 600;
            const size = this.getSize(country.stocks_count);
            const color = this.getColor(country.avg_performance);

            // Draw marker circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', x);
            circle.setAttribute('cy', y);
            circle.setAttribute('r', size);
            circle.setAttribute('fill', color);
            circle.setAttribute('opacity', '0.8');
            circle.setAttribute('stroke', '#fff');
            circle.setAttribute('stroke-width', '2');
            circle.style.cursor = 'pointer';
            circle.setAttribute('data-country', country.country);
            
            // Add hover effect
            circle.addEventListener('mouseenter', (e) => {
                e.target.setAttribute('r', size * 1.3);
                e.target.setAttribute('opacity', '1');
                this.showTooltip(e, country);
            });
            
            circle.addEventListener('mouseleave', (e) => {
                e.target.setAttribute('r', size);
                e.target.setAttribute('opacity', '0.8');
                this.hideTooltip();
            });

            svg.appendChild(circle);

            // Draw country label
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', x);
            text.setAttribute('y', y + size + 15);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('fill', 'var(--text-primary)');
            text.setAttribute('font-size', '12');
            text.setAttribute('font-weight', '600');
            text.textContent = country.country;
            svg.appendChild(text);
        });

        // Clear container and add SVG
        this.container.innerHTML = '';
        this.container.appendChild(svg);

        // Add legend
        this.addLegend(svg);
    }

    drawContinents(svg) {
        // Simplified continent shapes (rectangles for simplicity)
        const continents = [
            { x: 100, y: 150, width: 300, height: 200, name: 'North America', fill: 'rgba(31, 41, 55, 0.3)' },
            { x: 100, y: 350, width: 250, height: 200, name: 'South America', fill: 'rgba(31, 41, 55, 0.3)' },
            { x: 450, y: 100, width: 200, height: 150, name: 'Europe', fill: 'rgba(31, 41, 55, 0.3)' },
            { x: 450, y: 250, width: 300, height: 200, name: 'Asia', fill: 'rgba(31, 41, 55, 0.3)' },
            { x: 450, y: 450, width: 200, height: 100, name: 'Africa', fill: 'rgba(31, 41, 55, 0.3)' },
            { x: 750, y: 450, width: 200, height: 100, name: 'Oceania', fill: 'rgba(31, 41, 55, 0.3)' }
        ];

        continents.forEach(continent => {
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', continent.x);
            rect.setAttribute('y', continent.y);
            rect.setAttribute('width', continent.width);
            rect.setAttribute('height', continent.height);
            rect.setAttribute('fill', continent.fill);
            rect.setAttribute('stroke', 'var(--border-light)');
            rect.setAttribute('stroke-width', '1');
            rect.setAttribute('rx', '5');
            svg.appendChild(rect);
        });
    }

    showTooltip(event, country) {
        // Remove existing tooltip
        const existing = document.querySelector('.map-tooltip');
        if (existing) existing.remove();

        const tooltip = document.createElement('div');
        tooltip.className = 'map-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            background: var(--bg-elevated);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            padding: var(--space-md);
            color: var(--text-primary);
            font-size: var(--font-size-sm);
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            pointer-events: none;
            min-width: 200px;
        `;

        const performance = country.avg_performance || 0;
        const color = this.getColor(performance);
        
        tooltip.innerHTML = `
            <div style="font-weight: 700; margin-bottom: var(--space-xs); color: var(--text-primary);">
                ${country.country}
            </div>
            <div style="margin-bottom: var(--space-xs);">
                <span style="color: var(--text-secondary);">Stocks:</span>
                <span style="color: var(--text-primary); font-weight: 600;"> ${country.stocks_count}</span>
            </div>
            <div>
                <span style="color: var(--text-secondary);">Performance:</span>
                <span style="color: ${color}; font-weight: 700;"> ${performance >= 0 ? '+' : ''}${performance}%</span>
            </div>
        `;

        document.body.appendChild(tooltip);

        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
    }

    hideTooltip() {
        const tooltip = document.querySelector('.map-tooltip');
        if (tooltip) tooltip.remove();
    }

    addLegend(svg) {
        const legend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        legend.setAttribute('transform', 'translate(50, 50)');

        const legendTitle = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        legendTitle.setAttribute('x', 0);
        legendTitle.setAttribute('y', 0);
        legendTitle.setAttribute('fill', 'var(--text-primary)');
        legendTitle.setAttribute('font-size', '14');
        legendTitle.setAttribute('font-weight', '700');
        legendTitle.textContent = 'Performance';
        legend.appendChild(legendTitle);

        const items = [
            { color: '#22c55e', label: '≥5%' },
            { color: '#84cc16', label: '0-5%' },
            { color: '#eab308', label: '-2-0%' },
            { color: '#ef4444', label: '<-2%' }
        ];

        items.forEach((item, index) => {
            const y = 25 + index * 25;

            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', 10);
            circle.setAttribute('cy', y);
            circle.setAttribute('r', 8);
            circle.setAttribute('fill', item.color);
            circle.setAttribute('stroke', '#fff');
            circle.setAttribute('stroke-width', '1');
            legend.appendChild(circle);

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', 25);
            text.setAttribute('y', y + 4);
            text.setAttribute('fill', 'var(--text-secondary)');
            text.setAttribute('font-size', '12');
            text.textContent = item.label;
            legend.appendChild(text);
        });

        svg.appendChild(legend);
    }
}

// Initialize map when DOM is ready
if (typeof window !== 'undefined') {
    window.CustomGeographicMap = CustomGeographicMap;
}


