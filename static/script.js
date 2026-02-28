// ============================================
// SCROLL REVEAL ANIMATION
// ============================================

/**
 * Reveals elements on scroll for smooth entrance animations
 */
function revealOnScroll() {
    const reveals = document.querySelectorAll('.reveal');
    
    reveals.forEach(element => {
        const windowHeight = window.innerHeight;
        const elementTop = element.getBoundingClientRect().top;
        const revealPoint = 100;
        
        if (elementTop < windowHeight - revealPoint) {
            element.classList.add('active');
        }
    });
}

// ============================================
// SMOOTH SCROLL FOR NAVIGATION LINKS
// ============================================

/**
 * Enables smooth scrolling for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            
            // Skip empty anchors
            if (href === '#') return;
            
            e.preventDefault();
            
            const targetElement = document.querySelector(href);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ============================================
// NAVBAR SCROLL EFFECT
// ============================================

/**
 * Adds shadow to navbar when scrolling
 */
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.boxShadow = 'none';
        }
    });
}

// ============================================
// FEATURE CARDS STAGGER ANIMATION
// ============================================

/**
 * Adds staggered entrance animation to feature cards
 */
function initFeatureCardsAnimation() {
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// ============================================
// FLOW STEPS ANIMATION
// ============================================

/**
 * Animates encryption flow steps on scroll
 */
function initFlowStepsAnimation() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                }, entry.target.dataset.delay || 0);
            }
        });
    }, {
        threshold: 0.2
    });
    
    const flowSteps = document.querySelectorAll('.flow-step');
    flowSteps.forEach((step, index) => {
        step.style.opacity = '0';
        step.style.transform = 'translateX(-30px)';
        step.style.transition = 'all 0.5s ease-out';
        step.dataset.delay = index * 50;
        observer.observe(step);
    });
}

// ============================================
// SCREENSHOT HOVER EFFECT
// ============================================

/**
 * Adds zoom effect on screenshot hover
 */
function initScreenshotHover() {
    const screenshots = document.querySelectorAll('.screenshot-frame img');
    
    screenshots.forEach(img => {
        img.style.transition = 'transform 0.3s ease';
        
        img.parentElement.addEventListener('mouseenter', () => {
            img.style.transform = 'scale(1.05)';
        });
        
        img.parentElement.addEventListener('mouseleave', () => {
            img.style.transform = 'scale(1)';
        });
    });
}

// ============================================
// TYPING EFFECT FOR HERO TITLE (Optional)
// ============================================

/**
 * Creates a typing effect for the hero title
 * Uncomment to enable
 */
function initTypingEffect() {
    const heroTitle = document.querySelector('.hero-title');
    if (!heroTitle) return;
    
    const text = heroTitle.textContent;
    heroTitle.textContent = '';
    heroTitle.style.opacity = '1';
    
    let i = 0;
    const typingSpeed = 50;
    
    function typeWriter() {
        if (i < text.length) {
            heroTitle.textContent += text.charAt(i);
            i++;
            setTimeout(typeWriter, typingSpeed);
        }
    }
    
    // Uncomment to enable typing effect
    // typeWriter();
}

// ============================================
// INTERSECTION OBSERVER FOR ANIMATIONS
// ============================================

/**
 * Generic intersection observer for reveal animations
 */
function initIntersectionObserver() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    });
    
    // Add 'reveal' class to sections for animation
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.classList.add('reveal');
        observer.observe(section);
    });
}

// ============================================
// COPY GITHUB LINK FUNCTIONALITY (Optional)
// ============================================

/**
 * Adds ability to copy GitHub link to clipboard
 */
function initCopyGithubLink() {
    const githubLinks = document.querySelectorAll('a[href*="github.com"]');
    
    githubLinks.forEach(link => {
        link.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            
            const url = link.href;
            navigator.clipboard.writeText(url).then(() => {
                // Show a temporary tooltip
                showTooltip(link, 'Link copied!');
            });
        });
    });
}

/**
 * Shows a temporary tooltip
 */
function showTooltip(element, message) {
    const tooltip = document.createElement('div');
    tooltip.textContent = message;
    tooltip.style.cssText = `
        position: absolute;
        background: #22d3ee;
        color: #0f172a;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        pointer-events: none;
        z-index: 9999;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px';
    tooltip.style.top = rect.bottom + 10 + 'px';
    
    setTimeout(() => tooltip.style.opacity = '1', 10);
    
    setTimeout(() => {
        tooltip.style.opacity = '0';
        setTimeout(() => tooltip.remove(), 300);
    }, 2000);
}

// ============================================
// PRELOAD IMAGES
// ============================================

/**
 * Preloads screenshot images for better performance
 */
function preloadImages() {
    const images = [
        'screenshots/initiator-handshake.png',
        'screenshots/responder-handshake.png',
        'screenshots/server.png'
    ];
    
    images.forEach(src => {
        const img = new Image();
        img.src = src;
    });
}

// ============================================
// INITIALIZE ALL FUNCTIONS ON PAGE LOAD
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Core functionality
    initSmoothScroll();
    initNavbarScroll();
    initIntersectionObserver();
    
    // Animations
    setTimeout(initFeatureCardsAnimation, 300);
    initFlowStepsAnimation();
    initScreenshotHover();
    
    // Optional features
    // initTypingEffect(); // Uncomment to enable
    // initCopyGithubLink(); // Uncomment to enable
    
    // Preload images
    preloadImages();
    
    // Scroll reveal
    window.addEventListener('scroll', revealOnScroll);
    revealOnScroll(); // Initial check
    
    // Log initialization
    console.log('🔒 Secure Chat Application website loaded successfully');
});

// ============================================
// EASTER EGG: CONSOLE MESSAGE
// ============================================

console.log('%c🛡️ Secure Chat Application', 'color: #22d3ee; font-size: 24px; font-weight: bold;');
console.log('%cEnd-to-End Encrypted Messaging System', 'color: #cbd5e1; font-size: 14px;');
console.log('%cBuilt with Python, Cryptography, and Sockets', 'color: #94a3b8; font-size: 12px;');
console.log('%cGitHub: https://github.com/bajajaditi1910-design/secure-chat-app', 'color: #22d3ee; font-size: 12px;');
