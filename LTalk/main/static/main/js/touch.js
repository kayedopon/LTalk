// Touch optimization for mobile devices
document.addEventListener('DOMContentLoaded', function() {
    // Add touch feedback to clickable elements
    const clickableElements = document.querySelectorAll('.btn, .word-set-content, .nav-button, .menu-toggle');
    
    clickableElements.forEach(function(element) {
        // Add active class on touch start
        element.addEventListener('touchstart', function() {
            this.classList.add('touch-active');
        }, { passive: true });
        
        // Remove active class on touch end
        element.addEventListener('touchend', function() {
            this.classList.remove('touch-active');
        }, { passive: true });
        
        // Remove active class if touch moves away
        element.addEventListener('touchmove', function() {
            this.classList.remove('touch-active');
        }, { passive: true });
    });
    
    // Implement swipe gestures for flashcards if they exist
    const flashcard = document.querySelector('.flashcard');
    if (flashcard) {
        let startX, startY, endX, endY;
        const minSwipeDistance = 50;
        
        flashcard.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        flashcard.addEventListener('touchend', function(e) {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const distanceX = endX - startX;
            const distanceY = endY - startY;
            
            // Check if the swipe was horizontal and long enough
            if (Math.abs(distanceX) > Math.abs(distanceY) && Math.abs(distanceX) > minSwipeDistance) {
                if (distanceX > 0) {
                    // Right swipe - Next card
                    const nextButton = document.querySelector('.next-button');
                    if (nextButton) nextButton.click();
                } else {
                    // Left swipe - Previous card
                    const prevButton = document.querySelector('.prev-button');
                    if (prevButton) prevButton.click();
                }
            }
            
            // Check if the swipe was vertical and long enough
            if (Math.abs(distanceY) > Math.abs(distanceX) && Math.abs(distanceY) > minSwipeDistance) {
                if (distanceY < 0) {
                    // Swipe up - Flip card
                    flashcard.click();
                }
            }
        }, { passive: true });
    }
}); 