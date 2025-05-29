/**
 * Main JavaScript for FactCheck application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            
            // Toggle hamburger icon
            const bars = this.querySelectorAll('.bar');
            bars[0].classList.toggle('rotate-45');
            bars[1].classList.toggle('opacity-0');
            bars[2].classList.toggle('rotate-negative-45');
        });
    }
    
    // Close flash messages
    const closeFlashButtons = document.querySelectorAll('.close-flash');
    
    closeFlashButtons.forEach(button => {
        button.addEventListener('click', function() {
            const flashMessage = this.closest('.flash-message');
            flashMessage.style.opacity = '0';
            setTimeout(() => {
                flashMessage.style.display = 'none';
            }, 300);
        });
    });
    
    // Animation on scroll
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    const checkIfInView = function() {
        animateElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('active');
            }
        });
    };
    
    // Check on load
    checkIfInView();
    
    // Check on scroll
    window.addEventListener('scroll', checkIfInView);
    
    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        if (question) {
            question.addEventListener('click', function() {
                // Toggle current item
                item.classList.toggle('active');
                
                // Close other items
                faqItems.forEach(otherItem => {
                    if (otherItem !== item && otherItem.classList.contains('active')) {
                        otherItem.classList.remove('active');
                    }
                });
            });
        }
    });
    
    // Confidence circle animation
    const confidenceCircles = document.querySelectorAll('.confidence-circle');
    
    confidenceCircles.forEach(circle => {
        const confidenceValue = circle.getAttribute('data-value');
        circle.style.setProperty('--confidence-value', confidenceValue);
        
        // For values over 50%, we need to add another element
        if (confidenceValue > 50) {
            const rightFill = document.createElement('div');
            rightFill.classList.add('confidence-circle-fill', 'right');
            circle.appendChild(rightFill);
        }
    });
    
    // Share functionality
    const shareButtons = document.querySelectorAll('.share-button');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const platform = this.getAttribute('data-platform');
            const url = window.location.href;
            const title = document.title;
            
            let shareUrl;
            
            switch (platform) {
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;
                    break;
                case 'linkedin':
                    shareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`;
                    break;
                case 'email':
                    shareUrl = `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(url)}`;
                    break;
            }
            
            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        });
    });
    
    // Copy to clipboard functionality
    const copyLinkButton = document.querySelector('.copy-link');
    
    if (copyLinkButton) {
        copyLinkButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = window.location.href;
            
            // Create a temporary input element
            const tempInput = document.createElement('input');
            tempInput.value = url;
            document.body.appendChild(tempInput);
            
            // Select and copy the URL
            tempInput.select();
            document.execCommand('copy');
            
            // Remove the temporary input
            document.body.removeChild(tempInput);
            
            // Show success message
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-check"></i> Zkopírováno';
            
            // Reset button text after 2 seconds
            setTimeout(() => {
                this.innerHTML = originalText;
            }, 2000);
        });
    }
    
    // Quiz functionality
    const quizForm = document.querySelector('.quiz-form');
    
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            // Form submission is handled by the server
            // This is just for potential client-side validation
            
            // Check if all questions are answered
            const questions = this.querySelectorAll('.quiz-question');
            let allAnswered = true;
            
            questions.forEach(question => {
                const answered = question.querySelector('input[type="radio"]:checked');
                if (!answered) {
                    allAnswered = false;
                    question.classList.add('unanswered');
                } else {
                    question.classList.remove('unanswered');
                }
            });
            
            if (!allAnswered) {
                e.preventDefault();
                alert('Prosím odpovězte na všechny otázky.');
                
                // Scroll to first unanswered question
                const firstUnanswered = document.querySelector('.quiz-question.unanswered');
                if (firstUnanswered) {
                    firstUnanswered.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    }
    
    // Payment form validation
    const paymentForm = document.querySelector('.payment-form');
    
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            // Basic form validation
            const cardNumber = this.querySelector('#card_number');
            const cardExpiry = this.querySelector('#card_expiry');
            const cardCvc = this.querySelector('#card_cvc');
            
            let isValid = true;
            
            if (cardNumber && !validateCardNumber(cardNumber.value)) {
                isValid = false;
                cardNumber.classList.add('invalid');
            } else if (cardNumber) {
                cardNumber.classList.remove('invalid');
            }
            
            if (cardExpiry && !validateCardExpiry(cardExpiry.value)) {
                isValid = false;
                cardExpiry.classList.add('invalid');
            } else if (cardExpiry) {
                cardExpiry.classList.remove('invalid');
            }
            
            if (cardCvc && !validateCardCvc(cardCvc.value)) {
                isValid = false;
                cardCvc.classList.add('invalid');
            } else if (cardCvc) {
                cardCvc.classList.remove('invalid');
            }
            
            if (!isValid) {
                e.preventDefault();
                alert('Prosím zkontrolujte údaje o platební kartě.');
            }
        });
        
        // Helper functions for payment validation
        function validateCardNumber(number) {
            // Remove spaces and dashes
            number = number.replace(/[\s-]/g, '');
            return /^\d{16}$/.test(number);
        }
        
        function validateCardExpiry(expiry) {
            return /^\d{2}\/\d{2}$/.test(expiry);
        }
        
        function validateCardCvc(cvc) {
            return /^\d{3,4}$/.test(cvc);
        }
    }
    
    // Custom file input
    const fileInputs = document.querySelectorAll('.custom-file-input');
    
    fileInputs.forEach(input => {
        const fileNameDisplay = input.nextElementSibling;
        
        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
            } else {
                fileNameDisplay.textContent = 'Žádný soubor nevybrán';
            }
        });
    });
    
    // Tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            
            const tooltipElement = document.createElement('div');
            tooltipElement.classList.add('tooltip');
            tooltipElement.textContent = tooltipText;
            
            document.body.appendChild(tooltipElement);
            
            const rect = this.getBoundingClientRect();
            const tooltipRect = tooltipElement.getBoundingClientRect();
            
            tooltipElement.style.top = `${rect.top - tooltipRect.height - 10 + window.scrollY}px`;
            tooltipElement.style.left = `${rect.left + (rect.width / 2) - (tooltipRect.width / 2)}px`;
            
            this.addEventListener('mouseleave', function onMouseLeave() {
                document.body.removeChild(tooltipElement);
                this.removeEventListener('mouseleave', onMouseLeave);
            });
        });
    });
});
