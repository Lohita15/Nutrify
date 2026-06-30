// ========================================
// NutriFy - Main JavaScript
// Global functionality and utilities
// ========================================

// Smooth scroll for nav links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Add animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, observerOptions);

// Observe all fade-in elements
document.querySelectorAll('.fade-in').forEach(el => {
    observer.observe(el);
});

// Navbar background on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 10) {
        navbar.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.boxShadow = 'var(--shadow-sm)';
    }
});

// Mobile menu toggle (if needed)
const setupMobileMenu = () => {
    const navLinks = document.querySelector('.nav-links');
    const navLink = document.querySelectorAll('.nav-link');
    
    navLink.forEach(link => {
        link.addEventListener('click', () => {
            // Close mobile menu if open
            if (navLinks) {
                navLinks.style.display = 'none';
                setTimeout(() => {
                    navLinks.style.display = 'flex';
                }, 300);
            }
        });
    });
};

setupMobileMenu();

// Utility functions
const API_BASE = window.location.origin + '/api';

/**
 * Post file to API
 */
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('image', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload_meal`, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Upload error:', error);
        throw error;
    }
}

/**
 * Get meal analysis result
 */
async function getMealResult() {
    try {
        const response = await fetch(`${API_BASE}/meal_analysis_result`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Fetch result error:', error);
        throw error;
    }
}

// Export functions for use in other scripts
window.NutriFy = {
    uploadFile,
    getMealResult,
    API_BASE
};
