// Reveal on Scroll Animations

class RevealOnScroll {
    constructor() {
        this.elements = [];
        this.observer = null;
        this.init();
    }

    init() {
        // Check for reduced motion preference
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            // Show all elements immediately
            document.querySelectorAll('.reveal-on-scroll, .reveal-on-scroll-left, .reveal-on-scroll-right, .reveal-on-scroll-scale').forEach(el => {
                el.classList.add('revealed');
            });
            return;
        }

        // Setup Intersection Observer
        this.observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('revealed');
                        // Optional: unobserve after revealing
                        this.observer.unobserve(entry.target);
                    }
                });
            },
            {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            }
        );

        // Observe all reveal elements
        this.observeElements();
        
        // Watch for dynamically added elements
        this.watchForNewElements();
    }

    observeElements() {
        const selectors = [
            '.reveal-on-scroll',
            '.reveal-on-scroll-left',
            '.reveal-on-scroll-right',
            '.reveal-on-scroll-scale'
        ];

        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                this.observer.observe(el);
            });
        });
    }

    watchForNewElements() {
        const observer = new MutationObserver(() => {
            const selectors = [
                '.reveal-on-scroll',
                '.reveal-on-scroll-left',
                '.reveal-on-scroll-right',
                '.reveal-on-scroll-scale'
            ];

            selectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => {
                    if (!el.classList.contains('revealed')) {
                        this.observer.observe(el);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new RevealOnScroll();
    });
} else {
    new RevealOnScroll();
}


