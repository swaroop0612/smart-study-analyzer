/**
 * Smart Study Analyzer - Main JavaScript
 * Handles home page interactions and global utilities.
 */

// API base URL - change this when deploying
const API_BASE_URL = "http://127.0.0.1:5000";


/**
 * Smooth scroll for nav links
 */
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('href');
            const target = document.querySelector(targetId);
            
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
