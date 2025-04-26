// Form validation functions
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the signup page
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(event) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            if (password !== confirmPassword) {
                event.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            if (password.length < 8) {
                event.preventDefault();
                alert('Password must be at least 8 characters long!');
                return false;
            }
            
            return true;
        });
    }
    
    // Mobile menu toggle for landing page
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    if (mobileMenuBtn) {
        const mainNav = document.querySelector('.main-nav');
        const body = document.body;
        
        // Create overlay element
        const overlay = document.createElement('div');
        overlay.classList.add('overlay');
        body.appendChild(overlay);
        
        // Create close button
        const closeBtn = document.createElement('button');
        closeBtn.classList.add('close-menu');
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        mainNav.prepend(closeBtn);
        
        // Open menu function
        mobileMenuBtn.addEventListener('click', function() {
            mainNav.classList.add('active');
            overlay.classList.add('active');
            body.style.overflow = 'hidden';
        });
        
        // Close menu function
        function closeMenu() {
            mainNav.classList.remove('active');
            overlay.classList.remove('active');
            body.style.overflow = '';
        }
        
        closeBtn.addEventListener('click', closeMenu);
        overlay.addEventListener('click', closeMenu);
        
        // Close menu when clicking on a link
        const navLinks = mainNav.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', closeMenu);
        });
    }
    
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
        setTimeout(function() {
            flashMessages.forEach(function(message) {
                message.style.opacity = '0';
                setTimeout(function() {
                    message.style.display = 'none';
                }, 500);
            });
        }, 5000);
    }
});

// Add transition effect for flash messages
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        .alert {
            transition: opacity 0.5s ease-in-out;
        }
    `;
    document.head.appendChild(style);
});