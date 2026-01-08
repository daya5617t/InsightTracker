/**
 * Modern Loading System
 * Provides loading states, skeleton screens, and progress indicators
 */

class LoadingSystem {
    constructor() {
        this.overlay = null;
        this.init();
    }

    init() {
        this.createOverlay();
        this.bindEvents();
    }

    createOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner-container">
                <div class="spinner spinner-xl"></div>
                <div class="loading-text">Loading...</div>
            </div>
        `;
        document.body.appendChild(overlay);
        this.overlay = overlay;
    }

    bindEvents() {
        // Auto-hide loading on page load
        window.addEventListener('load', () => {
            this.hideGlobalLoading();
        });

        // Handle form submissions
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.hasAttribute('data-loading')) {
                e.preventDefault();
                this.showFormLoading(form);
                setTimeout(() => form.submit(), 500);
            }
        });

        // Handle AJAX requests
        this.interceptAjaxRequests();
    }

    // Global loading overlay
    showGlobalLoading(message = 'Loading...') {
        if (this.overlay) {
            this.overlay.querySelector('.loading-text').textContent = message;
            this.overlay.classList.add('active');
        }
    }

    hideGlobalLoading() {
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }
    }

    // Button loading states
    showButtonLoading(button, text = 'Loading...') {
        const originalText = button.innerHTML;
        button.setAttribute('data-original-text', originalText);
        button.classList.add('btn-loading');
        button.innerHTML = text;
        button.disabled = true;
    }

    hideButtonLoading(button) {
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
            button.removeAttribute('data-original-text');
        }
        button.classList.remove('btn-loading');
        button.disabled = false;
    }

    // Form loading states
    showFormLoading(form, message = 'Processing...') {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            this.showButtonLoading(submitBtn, message);
        }
        this.disableFormInputs(form);
    }

    hideFormLoading(form) {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            this.hideButtonLoading(submitBtn);
        }
        this.enableFormInputs(form);
    }

    disableFormInputs(form) {
        const inputs = form.querySelectorAll('input, select, textarea, button');
        inputs.forEach(input => {
            input.disabled = true;
            input.setAttribute('data-was-disabled', input.disabled);
        });
    }

    enableFormInputs(form) {
        const inputs = form.querySelectorAll('input, select, textarea, button');
        inputs.forEach(input => {
            const wasDisabled = input.getAttribute('data-was-disabled');
            if (wasDisabled === 'false') {
                input.disabled = false;
            }
            input.removeAttribute('data-was-disabled');
        });
    }

    // Skeleton loading for content areas
    showSkeletonLoading(container, type = 'cards') {
        container.classList.add('loading');
        const skeletonHtml = this.generateSkeletonHTML(type);
        container.innerHTML = skeletonHtml;
    }

    hideSkeletonLoading(container) {
        container.classList.remove('loading');
        // The actual content will be loaded via AJAX or other means
    }

    generateSkeletonHTML(type) {
        switch (type) {
            case 'cards':
                return `
                    <div class="skeleton-grid">
                        ${Array(6).fill(0).map(() => `
                            <div class="skeleton-card">
                                <div class="skeleton-header">
                                    <div class="skeleton-title skeleton"></div>
                                    <div class="skeleton-price skeleton"></div>
                                </div>
                                <div class="skeleton-change skeleton"></div>
                                <div class="skeleton-button skeleton"></div>
                            </div>
                        `).join('')}
                    </div>
                `;
            case 'dashboard':
                return `
                    <div class="row mb-4">
                        ${Array(4).fill(0).map(() => `
                            <div class="col-xl-3 col-lg-6 col-md-6 col-sm-12 mb-3">
                                <div class="stat-card">
                                    <div class="stat-icon"><div class="skeleton" style="width: 42px; height: 42px; border-radius: 14px;"></div></div>
                                    <div class="stat-value skeleton" style="width: 60px; height: 24px;"></div>
                                    <div class="stat-label skeleton" style="width: 80px; height: 14px;"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            default:
                return '<div class="skeleton" style="width: 100%; height: 200px;"></div>';
        }
    }

    // Progress indicators
    showProgress(message = 'Processing...', duration = 3000) {
        const progressContainer = document.createElement('div');
        progressContainer.className = 'loading-overlay active';
        progressContainer.innerHTML = `
            <div class="spinner-container">
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <div class="progress-text">${message}</div>
                </div>
            </div>
        `;

        document.body.appendChild(progressContainer);

        const progressFill = progressContainer.querySelector('.progress-fill');
        let progress = 0;

        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                setTimeout(() => {
                    progressContainer.remove();
                }, 500);
            }
            progressFill.style.width = progress + '%';
        }, duration / 10);

        return progressContainer;
    }

    // Card loading states
    showCardLoading(card) {
        card.classList.add('card-loading');
    }

    hideCardLoading(card) {
        card.classList.remove('card-loading');
    }

    // Intercept AJAX requests (basic implementation)
    interceptAjaxRequests() {
        // This is a basic implementation - you might want to use a proper AJAX library
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const loading = new LoadingSystem();
            loading.showGlobalLoading('Loading data...');

            return originalFetch.apply(this, args)
                .then(response => {
                    loading.hideGlobalLoading();
                    return response;
                })
                .catch(error => {
                    loading.hideGlobalLoading();
                    throw error;
                });
        };
    }

    // Utility methods
    showLoadingState(element, type = 'spinner') {
        const loadingClasses = {
            spinner: 'spinner spinner-sm',
            dots: 'dots-loader',
            pulse: 'pulse-loader'
        };

        const loader = document.createElement('div');
        loader.className = loadingClasses[type] || loadingClasses.spinner;

        element.style.position = 'relative';
        element.appendChild(loader);

        return loader;
    }

    hideLoadingState(element) {
        const loaders = element.querySelectorAll('.spinner, .dots-loader, .pulse-loader');
        loaders.forEach(loader => loader.remove());
    }
}

// Initialize loading system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.loadingSystem = new LoadingSystem();

    // Auto-show loading for forms with data-loading attribute
    document.querySelectorAll('form[data-loading]').forEach(form => {
        form.addEventListener('submit', function(e) {
            window.loadingSystem.showFormLoading(this);
        });
    });

    // Auto-show loading for buttons with data-loading attribute
    document.querySelectorAll('button[data-loading], .btn[data-loading]').forEach(button => {
        button.addEventListener('click', function() {
            window.loadingSystem.showButtonLoading(this);
        });
    });
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LoadingSystem;
}
