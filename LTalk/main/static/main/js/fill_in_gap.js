document.addEventListener('DOMContentLoaded', () => {
    const exerciseArea = document.getElementById('exercise-area');
    const controlsArea = document.getElementById('controls-area');
    const summaryArea = document.getElementById('summary');
    const submitBtn = document.getElementById('submit-btn');
    const nextBtn = document.getElementById('next-btn');
    const correctCountSpan = document.getElementById('correct-count');
    const incorrectCountSpan = document.getElementById('incorrect-count');
    const progressBar = document.getElementById('progress-bar');
    const feedbackArea = document.getElementById('feedback-area');

    let exercise = null;
    let questions = [];
    let currentQuestionIndex = 0;
    let userAnswers = {};
    let correctAnswersCount = 0;
    let incorrectAnswersCount = 0;
    let feedback = {};

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
        controlsArea.style.display = 'none';
    }

    function showLoading() {
        exerciseArea.innerHTML = '<div class="loading">Loading exercise...</div>';
        controlsArea.style.display = 'none';
        summaryArea.style.display = 'none';
        feedbackArea.style.display = 'none';
    }

    // Fisher-Yates (Knuth) Shuffle algorithm
    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]]; // Swap elements
        }
    }

    function createFillInGapQuestion(questionData) {
        const container = document.createElement('div');
        container.className = 'fill-in-gap-container';
        
        // Replace ___ with an input field
        const sentence = questionData.sentence.replace('___', '<input type="text" id="answer-input" class="gap-input" placeholder="Enter word">');
        
        container.innerHTML = `
            <div class="question-sentence">${sentence}</div>
            <div class="question-hint">Word: ${questionData.infinitive} (${questionData.translation})</div>
        `;
        
        return container;
    }

    function updateProgressBar() {
        const totalQuestions = questions.length;
        const progress = ((currentQuestionIndex) / totalQuestions) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
    }

    function showNextQuestion() {
        if (currentQuestionIndex >= questions.length) {
            showSummary();
            return;
        }

        const questionData = questions[currentQuestionIndex];
        
        exerciseArea.innerHTML = '';
        
        // Hide feedback area when showing a new question
        feedbackArea.style.display = 'none';
        
        const questionElement = createFillInGapQuestion(questionData);
        exerciseArea.appendChild(questionElement);
        
        // Show submit button, hide next button
        if (submitBtn) submitBtn.style.display = 'block';
        if (nextBtn) nextBtn.style.display = 'none';
        
        // Update progress bar
        updateProgressBar();
    }

    function recordAnswer() {
        const inputElement = document.getElementById('answer-input');
        if (!inputElement) return;
        
        const questionKey = questions[currentQuestionIndex].key;
        const userAnswer = inputElement.value.trim();
        
        userAnswers[questionKey] = userAnswer;
        
        // Disable input after submission
        inputElement.disabled = true;
        
        // Show next button, hide submit button
        if (submitBtn) submitBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'block';
        
        // Check answer client-side
        const correctAnswer = exercise.correct_answers[questionKey];
        const isCorrect = userAnswer.toLowerCase().trim() === correctAnswer.toLowerCase().trim();
        
        if (isCorrect) {
            correctAnswersCount++;
            showFeedback(questionKey, true, 'Great job!');
        } else {
            incorrectAnswersCount++;
            // Show loading feedback until we get the server response
            showFeedback(questionKey, false, 'Checking your answer...');
            // Submit this single answer immediately to get feedback
            submitSingleAnswer(questionKey, userAnswer);
        }
    }

    async function submitSingleAnswer(questionKey, userAnswer) {
        if (!exercise || !exercise.id) {
            console.error("Cannot submit answer, exercise ID is missing.");
            return;
        }

        const submitUrl = `/api/exercise/${exercise.id}/submit/`;
        // Create a payload with just this answer
        const singleAnswerPayload = { 
            user_answers: { [questionKey]: userAnswer } 
        };

        try {
            const response = await fetch(submitUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(singleAnswerPayload)
            });

            if (response.ok) {
                const result = await response.json();
                
                // Update the feedback if available
                if (result.feedback && result.feedback[questionKey]) {
                    const feedbackContent = feedbackArea.querySelector('.feedback-content');
                    if (feedbackContent) {
                        feedbackContent.textContent = result.feedback[questionKey];
                    }
                }
            } else {
                const errorData = await response.json();
                console.error("Feedback request failed:", errorData);
                // Show basic feedback if server request fails
                const feedbackContent = feedbackArea.querySelector('.feedback-content');
                if (feedbackContent) {
                    feedbackContent.textContent = `The correct answer is "${exercise.correct_answers[questionKey]}".`;
                }
            }
        } catch (error) {
            console.error("Error getting feedback:", error);
            // Show basic feedback if server request fails
            const feedbackContent = feedbackArea.querySelector('.feedback-content');
            if (feedbackContent) {
                feedbackContent.textContent = `The correct answer is "${exercise.correct_answers[questionKey]}".`;
            }
        }
    }

    // Submit all answers at the end for progress tracking
    async function submitResults() {
        if (!exercise || !exercise.id) {
            console.error("Cannot submit results, exercise ID is missing.");
            return;
        }

        const submitUrl = `/api/exercise/${exercise.id}/submit/`;
        const payload = { user_answers: userAnswers };

        console.log("Submitting final results:", payload);

        try {
            const response = await fetch(submitUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Final submission failed:", errorData);
            }
        } catch (error) {
            console.error("Error submitting final results:", error);
        }
    }

    function showSummary() {
        exerciseArea.innerHTML = '';
        controlsArea.style.display = 'none';
        feedbackArea.style.display = 'none';
        summaryArea.style.display = 'block';
        correctCountSpan.textContent = correctAnswersCount;
        incorrectCountSpan.textContent = incorrectAnswersCount;
        
        // Submit all answers to the server
        submitResults();
    }

    function showFeedback(questionKey, isCorrect, feedbackText) {
        feedbackArea.innerHTML = '';
        feedbackArea.style.display = 'block';
        
        const feedbackElement = document.createElement('div');
        feedbackElement.className = isCorrect ? 'feedback correct' : 'feedback incorrect';
        
        feedbackElement.innerHTML = `
            <div class="feedback-header">${isCorrect ? '✓ Correct!' : '✗ Incorrect'}</div>
            <div class="feedback-content">${feedbackText || ''}</div>
        `;
        
        feedbackArea.appendChild(feedbackElement);
    }

    function nextQuestion() {
        currentQuestionIndex++;
        showNextQuestion();
    }

    // --- API Calls ---
    async function fetchOrCreateExercise() {
        showLoading();
        try {
            // Always create a new exercise for each session
            const response = await fetch('/api/exercise/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    wordset: wordsetId,
                    type: 'fill_in_gap'
                })
            });

            if (response.ok) {
                exercise = await response.json();
                console.log("Created new exercise:", exercise);
            } else {
                const errorData = await response.json();
                throw new Error(`Failed to create exercise: ${JSON.stringify(errorData)}`);
            }

            if (exercise && exercise.questions) {
                // Convert questions object into an array of objects, preserving the key
                questions = Object.entries(exercise.questions).map(([key, value]) => ({
                    key: key, // Store the original key
                    sentence: value.sentence,
                    word: value.word,
                    infinitive: value.infinitive,
                    explanation: value.explanation
                }));
                
                if (questions.length === 0) {
                    displayError("This word set has no words to practice.");
                    return;
                }
                
                // Shuffle the questions array
                shuffleArray(questions);
                
                // Initialize UI
                showNextQuestion();
                controlsArea.style.display = 'block';
            } else {
                throw new Error("Exercise data is missing questions.");
            }

        } catch (error) {
            console.error("Error creating exercise:", error);
            displayError(`Error loading fill-in-gap exercise: ${error.message}`);
        }
    }

    // --- Event Listeners ---
    if (submitBtn) {
        submitBtn.addEventListener('click', () => {
            recordAnswer();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            nextQuestion();
        });
    }

    // Handle Enter key for input submission
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const inputElement = document.getElementById('answer-input');
            const submitBtnVisible = submitBtn && submitBtn.style.display !== 'none';
            const nextBtnVisible = nextBtn && nextBtn.style.display !== 'none';
            
            if (inputElement && !inputElement.disabled && submitBtnVisible) {
                recordAnswer();
            } else if (nextBtnVisible) {
                nextQuestion();
            }
        }
    });

    // Initialize
    fetchOrCreateExercise();
}); 