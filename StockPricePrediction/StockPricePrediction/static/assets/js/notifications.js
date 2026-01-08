/**
 * Modern Notification/Toast System
 * Provides toast notifications with animations and multiple types
 */

class NotificationSystem {
    constructor(options = {}) {
        this.options = {
            position: 'top-right',
            duration: 5000,
            animation: 'slide-in',
            maxNotifications: 5,
            ...options
        };

        this.container = null;
        this.notifications = [];
        this.init();
    }

    init() {
        this.createContainer();
        this.bindEvents();
    }

    createContainer() {
        const container = document.createElement('div');
        container.className = `notifications-container ${this.options.position}`;
        document.body.appendChild(container);
        this.container = container;
    }

    bindEvents() {
        // Handle notification actions
        document.addEventListener('click', (e) => {
            if (e.target.closest('.notification-close')) {
                const notification = e.target.closest('.notification');
                this.dismiss(notification.dataset.id);
            }

            if (e.target.closest('.notification-action')) {
                const action = e.target.closest('.notification-action');
                const notification = action.closest('.notification');
                const actionType = action.dataset.action;

                if (actionType && this.options.onAction) {
                    this.options.onAction(actionType, notification.dataset.id);
                }
            }
        });
    }

    // Show notification
    show(options) {
        const config = {
            type: 'info',
            title: '',
            message: '',
            duration: this.options.duration,
            animation: this.options.animation,
            actions: [],
            persistent: false,
            icon: null,
            ...options
        };

        // Limit notifications
        if (this.notifications.length >= this.options.maxNotifications) {
            this.dismiss(this.notifications[0].id);
        }

        const notification = this.createNotification(config);
        this.notifications.push(notification);
        this.container.appendChild(notification.element);

        // Trigger show animation
        setTimeout(() => {
            notification.element.classList.add('show');
        }, 10);

        // Auto dismiss
        if (!config.persistent && config.duration > 0) {
            notification.timer = setTimeout(() => {
                this.dismiss(notification.id);
            }, config.duration);
        }

        return notification.id;
    }

    createNotification(config) {
        const id = this.generateId();
        const element = document.createElement('div');

        element.className = `notification ${config.type} ${config.animation}`;
        element.dataset.id = id;
        element.setAttribute('role', 'alert');
        element.setAttribute('aria-live', 'assertive');

        const iconHtml = config.icon || this.getDefaultIcon(config.type);
        const actionsHtml = config.actions.length > 0
            ? `<div class="notification-actions">
                ${config.actions.map(action =>
                    `<button class="notification-action" data-action="${action.type}">${action.label}</button>`
                ).join('')}
               </div>`
            : '';

        element.innerHTML = `
            <div class="notification-icon">
                ${iconHtml}
            </div>
            <div class="notification-content">
                ${config.title ? `<div class="notification-title">${config.title}</div>` : ''}
                <div class="notification-message">${config.message}</div>
                ${actionsHtml}
            </div>
            <button class="notification-close" aria-label="Close notification">
                <i class="fas fa-times"></i>
            </button>
            ${!config.persistent && config.duration > 0 ? `<div class="notification-progress" style="animation-duration: ${config.duration}ms"></div>` : ''}
        `;

        return {
            id,
            element,
            timer: null,
            config
        };
    }

    getDefaultIcon(type) {
        const icons = {
            success: '<i class="fas fa-check"></i>',
            error: '<i class="fas fa-exclamation-triangle"></i>',
            warning: '<i class="fas fa-exclamation-circle"></i>',
            info: '<i class="fas fa-info-circle"></i>'
        };
        return icons[type] || icons.info;
    }

    // Dismiss notification
    dismiss(id) {
        const notification = this.notifications.find(n => n.id === id);
        if (!notification) return;

        const element = notification.element;

        // Clear timer
        if (notification.timer) {
            clearTimeout(notification.timer);
        }

        // Start hide animation
        element.classList.add('hide');
        element.classList.remove('show');

        // Remove after animation
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
            this.notifications = this.notifications.filter(n => n.id !== id);
        }, 400);
    }

    // Dismiss all notifications
    dismissAll() {
        this.notifications.forEach(notification => {
            this.dismiss(notification.id);
        });
    }

    // Update notification
    update(id, updates) {
        const notification = this.notifications.find(n => n.id === id);
        if (!notification) return;

        Object.assign(notification.config, updates);

        // Re-render content
        const content = notification.element.querySelector('.notification-content');
        if (updates.title || updates.message) {
            content.innerHTML = `
                ${notification.config.title ? `<div class="notification-title">${notification.config.title}</div>` : ''}
                <div class="notification-message">${notification.config.message}</div>
                ${notification.config.actions && notification.config.actions.length > 0
                    ? `<div class="notification-actions">
                        ${notification.config.actions.map(action =>
                            `<button class="notification-action" data-action="${action.type}">${action.label}</button>`
                        ).join('')}
                       </div>`
                    : ''}
            `;
        }
    }

    // Convenience methods for different types
    success(message, title = '', options = {}) {
        return this.show({ ...options, type: 'success', title, message });
    }

    error(message, title = 'Error', options = {}) {
        return this.show({ ...options, type: 'error', title, message });
    }

    warning(message, title = 'Warning', options = {}) {
        return this.show({ ...options, type: 'warning', title, message });
    }

    info(message, title = 'Info', options = {}) {
        return this.show({ ...options, type: 'info', title, message });
    }

    // Custom notification with actions
    confirm(message, title = 'Confirm', actions = []) {
        return this.show({
            type: 'warning',
            title,
            message,
            actions: actions.length > 0 ? actions : [
                { type: 'confirm', label: 'Yes' },
                { type: 'cancel', label: 'No' }
            ],
            persistent: true
        });
    }

    // Generate unique ID
    generateId() {
        return 'notification_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Set position
    setPosition(position) {
        this.options.position = position;
        this.container.className = `notifications-container ${position}`;
    }

    // Set global duration
    setDuration(duration) {
        this.options.duration = duration;
    }

    // Handle keyboard navigation
    handleKeyboard(e) {
        if (e.key === 'Escape') {
            // Dismiss latest notification
            const latest = this.notifications[this.notifications.length - 1];
            if (latest) {
                this.dismiss(latest.id);
            }
        }
    }
}

// Initialize notification system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.notifications = new NotificationSystem({
        position: 'top-right',
        duration: 5000,
        onAction: (actionType, notificationId) => {
            // Handle custom actions
            console.log('Action triggered:', actionType, notificationId);

            // Example: handle confirm/cancel actions
            if (actionType === 'confirm') {
                window.notifications.success('Action confirmed!');
            } else if (actionType === 'cancel') {
                window.notifications.info('Action cancelled');
            }

            // Dismiss the notification
            window.notifications.dismiss(notificationId);
        }
    });

    // Add keyboard support
    document.addEventListener('keydown', (e) => {
        window.notifications.handleKeyboard(e);
    });
});

// Utility functions for easy access
window.showNotification = (options) => window.notifications.show(options);
window.showSuccess = (message, title, options) => window.notifications.success(message, title, options);
window.showError = (message, title, options) => window.notifications.error(message, title, options);
window.showWarning = (message, title, options) => window.notifications.warning(message, title, options);
window.showInfo = (message, title, options) => window.notifications.info(message, title, options);
window.showConfirm = (message, title, actions) => window.notifications.confirm(message, title, actions);

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationSystem;
}
