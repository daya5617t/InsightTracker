// Smooth Page Transitions

class PageTransitions {
    constructor() {
        this.transitionElement = null;
        this.init();
    }

    init() {
        this.createTransitionElement();
        this.setupLinkIntercepts();
    }

    createTransitionElement() {
        this.transitionElement = document.createElement('div');
        this.transitionElement.className = 'page-transition';
        document.body.appendChild(this.transitionElement);
    }

    setupLinkIntercepts() {
        document.querySelectorAll('a[href^="/"]').forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                
                // Skip if external link or anchor link
                if (href.startsWith('http') || href.startsWith('#') || link.hasAttribute('target')) {
                    return;
                }

                e.preventDefault();
                this.transitionOut(() => {
                    window.location.href = href;
                });
            });
        });
    }

    transitionOut(callback) {
        this.transitionElement.classList.add('active');
        
        setTimeout(() => {
            if (callback) callback();
        }, 300);
    }

    transitionIn() {
        this.transitionElement.classList.remove('active');
        setTimeout(() => {
            this.transitionElement.classList.add('exit');
            setTimeout(() => {
                this.transitionElement.classList.remove('exit', 'active');
            }, 300);
        }, 100);
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new PageTransitions();
    });
} else {
    new PageTransitions();
}

// Transition in when page loads
window.addEventListener('load', () => {
    const transitions = new PageTransitions();
    transitions.transitionIn();
});


