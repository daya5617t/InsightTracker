// Custom Cursor with Magnetic Attraction and Elastic Effects

class CustomCursor {
    constructor() {
        this.cursor = null;
        this.cursorFollower = null;
        this.mouseX = 0;
        this.mouseY = 0;
        this.followerX = 0;
        this.followerY = 0;
        this.isHovering = false;
        this.init();
    }

    init() {
        // Create cursor elements
        this.createCursorElements();
        
        // Track mouse movement
        document.addEventListener('mousemove', (e) => this.onMouseMove(e));
        
        // Track interactive elements
        this.setupInteractiveElements();
        
        // Animate cursor
        this.animate();
    }

    createCursorElements() {
        // Main cursor dot
        this.cursor = document.createElement('div');
        this.cursor.className = 'custom-cursor';
        this.cursor.style.cssText = `
            position: fixed;
            width: 8px;
            height: 8px;
            background: var(--primary);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            mix-blend-mode: difference;
            transition: transform 0.15s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translate(-50%, -50%);
        `;

        // Follower ring (magnetic effect)
        this.cursorFollower = document.createElement('div');
        this.cursorFollower.className = 'custom-cursor-follower';
        this.cursorFollower.style.cssText = `
            position: fixed;
            width: 40px;
            height: 40px;
            border: 2px solid var(--primary);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9998;
            opacity: 0.5;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translate(-50%, -50%);
        `;

        document.body.appendChild(this.cursor);
        document.body.appendChild(this.cursorFollower);

        // Hide default cursor
        document.body.style.cursor = 'none';
    }

    onMouseMove(e) {
        this.mouseX = e.clientX;
        this.mouseY = e.clientY;

        // Update main cursor immediately
        this.cursor.style.left = this.mouseX + 'px';
        this.cursor.style.top = this.mouseY + 'px';
    }

    animate() {
        // Elastic following effect for the ring
        const dx = this.mouseX - this.followerX;
        const dy = this.mouseY - this.followerY;
        
        // Elastic physics simulation
        this.followerX += dx * 0.15;
        this.followerY += dy * 0.15;

        this.cursorFollower.style.left = this.followerX + 'px';
        this.cursorFollower.style.top = this.followerY + 'px';

        requestAnimationFrame(() => this.animate());
    }

    setupInteractiveElements() {
        // Select all interactive elements
        const interactiveSelectors = [
            'a', 'button', '.btn', '.card', '.stock-card', 
            'input', 'textarea', 'select', '.nav-link',
            '.feature-card', '.stat-box', '.tab-button'
        ];

        interactiveSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                el.addEventListener('mouseenter', () => this.onHoverEnter(el));
                el.addEventListener('mouseleave', () => this.onHoverLeave(el));
            });
        });

        // Watch for dynamically added elements
        const observer = new MutationObserver(() => {
            interactiveSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => {
                    if (!el.dataset.cursorSetup) {
                        el.dataset.cursorSetup = 'true';
                        el.addEventListener('mouseenter', () => this.onHoverEnter(el));
                        el.addEventListener('mouseleave', () => this.onHoverLeave(el));
                    }
                });
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    onHoverEnter(element) {
        this.isHovering = true;
        
        // Enlarge cursor
        this.cursor.style.transform = 'translate(-50%, -50%) scale(2)';
        this.cursor.style.background = 'var(--primary)';
        
        // Expand follower ring
        const rect = element.getBoundingClientRect();
        const width = rect.width;
        const height = rect.height;
        const size = Math.max(width, height) + 20;
        
        this.cursorFollower.style.width = size + 'px';
        this.cursorFollower.style.height = size + 'px';
        this.cursorFollower.style.borderRadius = element.classList.contains('btn') ? '8px' : '50%';
        this.cursorFollower.style.opacity = '0.3';
        this.cursorFollower.style.borderColor = 'var(--primary)';
        
        // Store original transform
        if (!element.dataset.originalTransform) {
            element.dataset.originalTransform = element.style.transform || 'none';
        }
        
        // Magnetic attraction effect - bind to instance
        this.boundMagneticAttraction = (e) => this.magneticAttraction(e, element);
        element.addEventListener('mousemove', this.boundMagneticAttraction);
    }

    onHoverLeave(element) {
        this.isHovering = false;
        
        // Reset cursor
        this.cursor.style.transform = 'translate(-50%, -50%) scale(1)';
        
        // Reset follower ring
        this.cursorFollower.style.width = '40px';
        this.cursorFollower.style.height = '40px';
        this.cursorFollower.style.borderRadius = '50%';
        this.cursorFollower.style.opacity = '0.5';
        
        // Remove magnetic effect
        if (this.boundMagneticAttraction) {
            element.removeEventListener('mousemove', this.boundMagneticAttraction);
        }
        
        // Reset element transform
        element.style.transform = element.dataset.originalTransform || 'none';
        element.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    }

    magneticAttraction(e, element) {
        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        const distanceX = e.clientX - centerX;
        const distanceY = e.clientY - centerY;
        
        // Magnetic pull strength (adjustable, lower = stronger)
        const strength = 0.15;
        const pullX = distanceX * strength;
        const pullY = distanceY * strength;
        
        // Apply magnetic effect to element
        element.style.transform = `translate(${pullX}px, ${pullY}px)`;
        element.style.transition = 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
    }
}

// Initialize custom cursor when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new CustomCursor();
    });
} else {
    new CustomCursor();
}

