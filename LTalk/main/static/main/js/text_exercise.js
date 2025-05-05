document.addEventListener('DOMContentLoaded', () => {
    const exerciseArea = document.getElementById('exercise-area');
    const resultsArea = document.getElementById('results-area');
    const correctCountSpan = document.getElementById('correct-count');
    const resultsDetails = document.getElementById('results-details');
    
    let lithuanianText = '';
    let questions = [];
    let userAnswers = {};
    let correctAnswers = {};
    
    // --- Helper Functions ---
    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return '';
    }
    
    function displayError(message) {
        exerciseArea.innerHTML = `<div class="error-message">${message}</div>`;
    }
    
    function showLoading() {
        exerciseArea.innerHTML = '<div class="loading">Loading exercise...</div>';
        resultsArea.style.display = 'none';
    }
    
    // Load the text and questions from the API
    async function fetchGeminiContent() {
        showLoading();
        
        try {
            const response = await fetch(`/api/text-exercise/?wordset_id=${wordsetId}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to load exercise');
            }
            
            const data = await response.json();
            
            if (!data.text || !data.questions || !Array.isArray(data.questions)) {
                throw new Error('Invalid response format from server');
            }
            
            lithuanianText = data.text;
            questions = data.questions;
            
            // Store correct answers for later checking
            correctAnswers = {};
            questions.forEach((q, index) => {
                correctAnswers[index] = q.correct_answer;
            });
            
            displayExercise();
            
        } catch (error) {
            console.error('Error fetching exercise:', error);
            displayError(`Failed to load exercise: ${error.message}`);
        }
    }
    
    // Display the text and questions in the UI
    function displayExercise() {
        // Create container for text and questions
        const container = document.createElement('div');
        
        // Add the Lithuanian text
        const textArea = document.createElement('div');
        textArea.className = 'text-area';
        textArea.innerHTML = lithuanianText.replace(/\n/g, '<br>');
        container.appendChild(textArea);
        
        // Add each question
        questions.forEach((question, index) => {
            const questionArea = document.createElement('div');
            questionArea.className = 'question-area';
            questionArea.dataset.questionIndex = index;
            
            const questionTitle = document.createElement('div');
            questionTitle.className = 'question-title';
            questionTitle.textContent = `${index + 1}. ${question.question}`;
            questionArea.appendChild(questionTitle);
            
            const choicesList = document.createElement('ul');
            choicesList.className = 'choices-list';
            
            // Add each choice
            question.choices.forEach((choice, choiceIndex) => {
                const choiceItem = document.createElement('li');
                choiceItem.className = 'choice-item';
                choiceItem.textContent = choice;
                choiceItem.dataset.choice = choice;
                
                // Add click handler
                choiceItem.addEventListener('click', () => {
                    // Deselect any previously selected choice in this question
                    const selected = questionArea.querySelector('.selected');
                    if (selected) {
                        selected.classList.remove('selected');
                    }
                    
                    // Select this choice
                    choiceItem.classList.add('selected');
                    
                    // Record user's answer
                    userAnswers[index] = choice;
                    
                    // Check if all questions are answered
                    checkAllAnswered();
                });
                
                choicesList.appendChild(choiceItem);
            });
            
            questionArea.appendChild(choicesList);
            container.appendChild(questionArea);
        });
        
        // Add submit button
        const submitButton = document.createElement('button');
        submitButton.className = 'btn btn-primary';
        submitButton.id = 'submit-all-btn';
        submitButton.textContent = 'Check Answers';
        submitButton.disabled = true; // Disabled until all questions are answered
        submitButton.addEventListener('click', checkAnswers);
        container.appendChild(submitButton);
        
        // Display the content
        exerciseArea.innerHTML = '';
        exerciseArea.appendChild(container);
    }
    
    // Check if all questions have been answered
    function checkAllAnswered() {
        const allAnswered = questions.every((_, index) => userAnswers[index] !== undefined);
        const submitButton = document.getElementById('submit-all-btn');
        
        if (submitButton) {
            submitButton.disabled = !allAnswered;
        }
    }
    
    // Check the user's answers and display results
    function checkAnswers() {
        let correctCount = 0;
        
        // Process each question
        questions.forEach((question, index) => {
            const questionArea = document.querySelector(`.question-area[data-question-index="${index}"]`);
            const userAnswer = userAnswers[index];
            const correctAnswer = correctAnswers[index];
            
            if (userAnswer === correctAnswer) {
                correctCount++;
            }
            
            // Mark the selected answer as correct or incorrect
            const choiceItems = questionArea.querySelectorAll('.choice-item');
            choiceItems.forEach(item => {
                const choice = item.dataset.choice;
                
                if (choice === userAnswer) {
                    if (choice === correctAnswer) {
                        item.classList.add('correct');
                    } else {
                        item.classList.add('incorrect');
                    }
                } else if (choice === correctAnswer) {
                    // Mark the correct answer
                    item.classList.add('correct');
                }
                
                // Disable further selection
                item.style.pointerEvents = 'none';
            });
        });
        
        // Update the results count
        correctCountSpan.textContent = correctCount;
        
        // Disable submit button
        const submitButton = document.getElementById('submit-all-btn');
        if (submitButton) {
            submitButton.disabled = true;
        }
        
        // Show the results area
        resultsArea.style.display = 'block';
        
        // Scroll to results
        resultsArea.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Initialize the exercise
    fetchGeminiContent();
}); 