/**
 * Main JavaScript for FactCheck application
 * This file contains common functionality used across the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    const userActions = document.querySelector('.user-actions');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            userActions.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
            
            if (mobileMenuToggle.classList.contains('active')) {
                mobileMenuToggle.innerHTML = '<i class="fas fa-times"></i>';
            } else {
                mobileMenuToggle.innerHTML = '<i class="fas fa-bars"></i>';
            }
        });
    }
    
    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
        
        // Manual dismiss
        const closeBtn = message.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 300);
            });
        }
    });
    
    // Support banner interactions
    const supportBanner = document.querySelector('.support-banner');
    const bannerClose = document.querySelector('.banner-close');
    
    if (supportBanner && bannerClose) {
        bannerClose.addEventListener('click', function() {
            supportBanner.style.display = 'none';
            
            // Store preference in localStorage
            localStorage.setItem('support_banner_closed', 'true');
        });
        
        // Check if banner was previously closed
        if (localStorage.getItem('support_banner_closed') === 'true') {
            supportBanner.style.display = 'none';
        }
        
        // Reset banner after 7 days
        const lastClosed = localStorage.getItem('support_banner_closed_date');
        if (lastClosed) {
            const daysSinceClosed = (new Date() - new Date(lastClosed)) / (1000 * 60 * 60 * 24);
            if (daysSinceClosed > 7) {
                localStorage.removeItem('support_banner_closed');
                localStorage.removeItem('support_banner_closed_date');
            }
        }
        
        if (localStorage.getItem('support_banner_closed') === 'true') {
            localStorage.setItem('support_banner_closed_date', new Date().toISOString());
        }
    }
    
    // Animate elements when they come into view
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 50) {
                element.classList.add('animated');
            }
        });
    };
    
    // Run on load
    animateOnScroll();
    
    // Run on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Gamification elements
    const updateProgressBars = function() {
        const progressBars = document.querySelectorAll('.progress-bar');
        
        progressBars.forEach(bar => {
            const value = parseInt(bar.getAttribute('data-value'));
            const max = parseInt(bar.getAttribute('data-max'));
            const percentage = (value / max) * 100;
            
            const fill = bar.querySelector('.progress-fill');
            if (fill) {
                fill.style.width = `${percentage}%`;
            }
        });
    };
    
    // Run on load
    updateProgressBars();
    
    // Tooltips
    const initTooltips = function() {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        
        tooltips.forEach(tooltip => {
            tooltip.addEventListener('mouseenter', function() {
                const text = this.getAttribute('data-tooltip');
                
                const tooltipElement = document.createElement('div');
                tooltipElement.classList.add('tooltip');
                tooltipElement.textContent = text;
                
                document.body.appendChild(tooltipElement);
                
                const rect = this.getBoundingClientRect();
                const tooltipRect = tooltipElement.getBoundingClientRect();
                
                tooltipElement.style.top = `${rect.top - tooltipRect.height - 10 + window.scrollY}px`;
                tooltipElement.style.left = `${rect.left + (rect.width / 2) - (tooltipRect.width / 2) + window.scrollX}px`;
                
                tooltipElement.classList.add('visible');
            });
            
            tooltip.addEventListener('mouseleave', function() {
                const tooltipElement = document.querySelector('.tooltip');
                if (tooltipElement) {
                    tooltipElement.classList.remove('visible');
                    
                    setTimeout(() => {
                        tooltipElement.remove();
                    }, 300);
                }
            });
        });
    };
    
    // Run on load
    initTooltips();
    
    // Form validation
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            let isValid = true;
            
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // Add error message if not exists
                    let errorMessage = field.parentNode.querySelector('.error-message');
                    if (!errorMessage) {
                        errorMessage = document.createElement('div');
                        errorMessage.classList.add('error-message');
                        errorMessage.textContent = 'Toto pole je povinné';
                        field.parentNode.appendChild(errorMessage);
                    }
                } else {
                    field.classList.remove('error');
                    
                    // Remove error message if exists
                    const errorMessage = field.parentNode.querySelector('.error-message');
                    if (errorMessage) {
                        errorMessage.remove();
                    }
                }
            });
            
            // Email validation
            const emailFields = form.querySelectorAll('input[type="email"]');
            emailFields.forEach(field => {
                if (field.value.trim() && !isValidEmail(field.value)) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // Add error message if not exists
                    let errorMessage = field.parentNode.querySelector('.error-message');
                    if (!errorMessage) {
                        errorMessage = document.createElement('div');
                        errorMessage.classList.add('error-message');
                        errorMessage.textContent = 'Zadejte platný email';
                        field.parentNode.appendChild(errorMessage);
                    } else {
                        errorMessage.textContent = 'Zadejte platný email';
                    }
                }
            });
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    });
    
    // Helper function to validate email
    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    // Support page amount selection
    const amountOptions = document.querySelectorAll('.amount-option');
    const customAmountInput = document.getElementById('custom-amount');
    const amountInput = document.getElementById('amount');
    
    if (amountOptions.length > 0 && amountInput) {
        amountOptions.forEach(option => {
            option.addEventListener('click', function() {
                // Remove active class from all options
                amountOptions.forEach(opt => opt.classList.remove('active'));
                
                // Add active class to clicked option
                this.classList.add('active');
                
                // Update hidden input value
                const amount = this.getAttribute('data-amount');
                amountInput.value = amount;
                
                // If custom option, focus on input
                if (amount === 'custom' && customAmountInput) {
                    customAmountInput.focus();
                    customAmountInput.style.display = 'block';
                } else if (customAmountInput) {
                    customAmountInput.style.display = 'none';
                }
            });
        });
        
        // Handle custom amount input
        if (customAmountInput) {
            customAmountInput.addEventListener('input', function() {
                amountInput.value = this.value;
            });
        }
    }
    
    // Payment method selection
    const paymentMethods = document.querySelectorAll('.payment-method');
    const paymentMethodInput = document.getElementById('payment_method');
    
    if (paymentMethods.length > 0 && paymentMethodInput) {
        paymentMethods.forEach(method => {
            method.addEventListener('click', function() {
                // Remove active class from all methods
                paymentMethods.forEach(m => m.classList.remove('active'));
                
                // Add active class to clicked method
                this.classList.add('active');
                
                // Update hidden input value
                const paymentMethod = this.getAttribute('data-method');
                paymentMethodInput.value = paymentMethod;
            });
        });
    }
    
    // Quiz functionality
    const quizContainer = document.querySelector('.quiz-container');
    
    if (quizContainer) {
        const quizQuestions = quizContainer.querySelectorAll('.quiz-question');
        const nextButton = quizContainer.querySelector('.quiz-next');
        const prevButton = quizContainer.querySelector('.quiz-prev');
        const submitButton = quizContainer.querySelector('.quiz-submit');
        const progressBar = quizContainer.querySelector('.quiz-progress-fill');
        
        let currentQuestion = 0;
        
        // Show current question
        const showQuestion = function(index) {
            quizQuestions.forEach((question, i) => {
                if (i === index) {
                    question.style.display = 'block';
                } else {
                    question.style.display = 'none';
                }
            });
            
            // Update progress bar
            if (progressBar) {
                progressBar.style.width = `${((index + 1) / quizQuestions.length) * 100}%`;
            }
            
            // Update buttons
            if (prevButton) {
                prevButton.style.display = index === 0 ? 'none' : 'block';
            }
            
            if (nextButton && submitButton) {
                if (index === quizQuestions.length - 1) {
                    nextButton.style.display = 'none';
                    submitButton.style.display = 'block';
                } else {
                    nextButton.style.display = 'block';
                    submitButton.style.display = 'none';
                }
            }
        };
        
        // Initialize
        if (quizQuestions.length > 0) {
            showQuestion(currentQuestion);
            
            // Next button
            if (nextButton) {
                nextButton.addEventListener('click', function() {
                    if (currentQuestion < quizQuestions.length - 1) {
                        currentQuestion++;
                        showQuestion(currentQuestion);
                    }
                });
            }
            
            // Previous button
            if (prevButton) {
                prevButton.addEventListener('click', function() {
                    if (currentQuestion > 0) {
                        currentQuestion--;
                        showQuestion(currentQuestion);
                    }
                });
            }
            
            // Quiz options
            const quizOptions = quizContainer.querySelectorAll('.quiz-option');
            
            quizOptions.forEach(option => {
                option.addEventListener('click', function() {
                    const questionId = this.closest('.quiz-question').getAttribute('data-question-id');
                    const optionId = this.getAttribute('data-option-id');
                    
                    // Remove selected class from all options in this question
                    const questionOptions = this.closest('.quiz-question').querySelectorAll('.quiz-option');
                    questionOptions.forEach(opt => opt.classList.remove('selected'));
                    
                    // Add selected class to clicked option
                    this.classList.add('selected');
                    
                    // Update hidden input
                    const input = document.querySelector(`input[name="quiz_${questionId}"]`);
                    if (input) {
                        input.value = optionId;
                    }
                });
            });
            
            // Submit button
            if (submitButton) {
                submitButton.addEventListener('click', function() {
                    // Collect answers
                    const answers = {};
                    
                    quizQuestions.forEach(question => {
                        const questionId = question.getAttribute('data-question-id');
                        const input = document.querySelector(`input[name="quiz_${questionId}"]`);
                        
                        if (input) {
                            answers[questionId] = input.value;
                        }
                    });
                    
                    // Submit answers
                    const quizForm = document.getElementById('quiz-form');
                    if (quizForm) {
                        const answersInput = document.createElement('input');
                        answersInput.type = 'hidden';
                        answersInput.name = 'answers';
                        answersInput.value = JSON.stringify(answers);
                        
                        quizForm.appendChild(answersInput);
                        quizForm.submit();
                    }
                });
            }
        }
    }
});
