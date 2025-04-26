// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Variables
    const header = document.querySelector('header');
    const hamburger = document.querySelector('.hamburger');
    const navbar = document.querySelector('.navbar');
    const navLinks = document.querySelectorAll('.nav-links a');
    const testimonialSlider = document.getElementById('testimonial-slider');
    const testimonials = document.querySelectorAll('.testimonial');
    const prevTestimonialBtn = document.getElementById('prev-testimonial');
    const nextTestimonialBtn = document.getElementById('next-testimonial');
    const contactForm = document.querySelector('.contact-form');
    const newsletterForm = document.querySelector('.newsletter-form');
    
    // Sticky header on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    
    // Mobile menu toggle
    hamburger.addEventListener('click', function() {
        navbar.classList.toggle('active');
        
        // Animate hamburger to X
        this.classList.toggle('active');
        
        // When active, add these styles to hamburger bars
        if (this.classList.contains('active')) {
            document.querySelectorAll('.bar')[0].style.transform = 'rotate(-45deg) translate(-5px, 6px)';
            document.querySelectorAll('.bar')[1].style.opacity = '0';
            document.querySelectorAll('.bar')[2].style.transform = 'rotate(45deg) translate(-5px, -6px)';
        } else {
            document.querySelectorAll('.bar')[0].style.transform = 'none';
            document.querySelectorAll('.bar')[1].style.opacity = '1';
            document.querySelectorAll('.bar')[2].style.transform = 'none';
        }
    });
    
    // Close mobile menu when a link is clicked
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navbar.classList.remove('active');
            hamburger.classList.remove('active');
            document.querySelectorAll('.bar')[0].style.transform = 'none';
            document.querySelectorAll('.bar')[1].style.opacity = '1';
            document.querySelectorAll('.bar')[2].style.transform = 'none';
        });
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Offset for the fixed header
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Testimonial slider
    let currentTestimonial = 0;
    
    function showTestimonial(index) {
        if (index < 0) {
            currentTestimonial = testimonials.length - 1;
        } else if (index >= testimonials.length) {
            currentTestimonial = 0;
        } else {
            currentTestimonial = index;
        }
        
        testimonialSlider.style.transform = `translateX(-${currentTestimonial * 100}%)`;
    }
    
    prevTestimonialBtn.addEventListener('click', function() {
        showTestimonial(currentTestimonial - 1);
    });
    
    nextTestimonialBtn.addEventListener('click', function() {
        showTestimonial(currentTestimonial + 1);
    });
    
    // Auto-advance testimonials
    let testimonialInterval = setInterval(() => {
        showTestimonial(currentTestimonial + 1);
    }, 6000);
    
    // Pause auto-advance on hover
    testimonialSlider.addEventListener('mouseenter', () => {
        clearInterval(testimonialInterval);
    });
    
    testimonialSlider.addEventListener('mouseleave', () => {
        testimonialInterval = setInterval(() => {
            showTestimonial(currentTestimonial + 1);
        }, 6000);
    });
    
    // Form submission handling
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value;
            
            // Basic validation
            if (!name || !email || !message) {
                alert('Please fill in all required fields.');
                return;
            }
            
            // Here you would normally send the data to a server
            // For demo purposes, we'll just show a success message
            alert('Thank you for your message! We will get back to you soon.');
            this.reset();
        });
    }
    
    // Newsletter form
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[type="email"]').value;
            
            if (!email) {
                alert('Please enter your email address.');
                return;
            }
            
            // Here you would normally subscribe the user
            alert('Thank you for subscribing to our newsletter!');
            this.reset();
        });
    }
    
    // Animate stats on scroll
    const statNumbers = document.querySelectorAll('.stat-item h3');
    let animatedStats = false;
    
    function animateStats() {
        if (animatedStats) return;
        
        const statsSection = document.querySelector('.stats');
        if (!statsSection) return;
        
        const statsSectionPosition = statsSection.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (statsSectionPosition < screenPosition) {
            statNumbers.forEach(stat => {
                const targetNumber = parseInt(stat.textContent.replace(/,|[+]/g, ''));
                let currentNumber = 0;
                const increment = Math.ceil(targetNumber / 40); // Divide into 40 steps
                const duration = 1500; // Animation duration in ms
                const interval = duration / (targetNumber / increment);
                
                const counter = setInterval(() => {
                    currentNumber += increment;
                    if (currentNumber >= targetNumber) {
                        stat.textContent = stat.textContent.includes('+') 
                            ? targetNumber.toLocaleString() + '+' 
                            : targetNumber.toLocaleString();
                        clearInterval(counter);
                    } else {
                        stat.textContent = stat.textContent.includes('+')
                            ? currentNumber.toLocaleString() + '+'
                            : currentNumber.toLocaleString();
                    }
                }, interval);
            });
            
            animatedStats = true;
        }
    }
    
    // Animate sections on scroll
    function animateSections() {
        const sections = document.querySelectorAll('section');
        
        sections.forEach(section => {
            const sectionTop = section.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (sectionTop < windowHeight * 0.75) {
                section.classList.add('in-view');
            }
        });
        
        animateStats();
    }
    
    // Add animation classes to CSS
    const style = document.createElement('style');
    style.textContent = `
        section {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        section.in-view {
            opacity: 1;
            transform: translateY(0);
        }
        
        .services-container, .steps-container, .testimonial-container {
            transition-delay: 0.2s;
        }
        
        .service-card, .step, .testimonial {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .in-view .service-card, .in-view .step, .in-view .testimonial {
            opacity: 1;
            transform: translateY(0);
        }
        
        .service-card:nth-child(1), .step:nth-child(1), .testimonial:nth-child(1) {
            transition-delay: 0.1s;
        }
        
        .service-card:nth-child(2), .step:nth-child(2), .testimonial:nth-child(2) {
            transition-delay: 0.2s;
        }
        
        .service-card:nth-child(3), .step:nth-child(3), .testimonial:nth-child(3) {
            transition-delay: 0.3s;
        }
        
        .service-card:nth-child(4), .step:nth-child(4), .testimonial:nth-child(4) {
            transition-delay: 0.4s;
        }
    `;
    document.head.appendChild(style);
    
    // Initial check for elements in view on page load
    setTimeout(animateSections, 100);
    
    // Check for elements on scroll
    window.addEventListener('scroll', animateSections);
    
    // Active navigation highlighting based on scroll position
    function highlightNav() {
        const scrollPosition = window.scrollY;
        
        // Get all sections that have an ID
        const sections = document.querySelectorAll('section[id]');
        
        // Loop through sections to find the one in view
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100; // Adjust for header
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                // Remove active class from all links
                navLinks.forEach(link => {
                    link.classList.remove('active');
                });
                
                // Add active class to corresponding link
                const activeLink = document.querySelector(`.nav-links a[href="#${sectionId}"]`);
                if (activeLink) {
                    activeLink.classList.add('active');
                }
            }
        });
    }
    
    window.addEventListener('scroll', highlightNav);
    
    // Run initial highlight
    highlightNav();
});