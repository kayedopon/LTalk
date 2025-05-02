document.addEventListener('DOMContentLoaded', () => {
    const flashcardArea = document.getElementById('flashcard-area');
    const controlsArea = document.getElementById('controls-area');
    const summaryArea = document.getElementById('summary');
    const correctBtn = document.getElementById('correct-btn');
    const incorrectBtn = document.getElementById('incorrect-btn');
    const correctCountSpan = document.getElementById('correct-count');
    const incorrectCountSpan = document.getElementById('incorrect-count');

    let exercise = null;
    let questions = [];
    let currentQuestionIndex = 0;
    let userAnswers = {};
    let correctAnswersCount = 0;
    let incorrectAnswersCount = 0;
    let currentCardElement = null;

    // --- Helper Functions ---
    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return ''; // Fallback if not found (should be passed from template)
    }

    function displayError(message) {
        flashcardArea.innerHTML = `<div class="error-message">${message}</div>`;
        controlsArea.style.display = 'none';
    }

    function showLoading() {
        flashcardArea.innerHTML = '<div class="loading">Loading flashcards...</div>';
        controlsArea.style.display = 'none';
        summaryArea.style.display = 'none';
    }

    // Fisher-Yates (Knuth) Shuffle algorithm
    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]]; // Swap elements
        }
    }

    function createFlashcard(frontText, backText) {
        const container = document.createElement('div');
        container.className = 'flashcard-container';

        const card = document.createElement('div');
        card.className = 'flashcard';
        card.innerHTML = `
            <div class="flashcard-face flashcard-front">${frontText}</div>
            <div class="flashcard-face flashcard-back">${backText}</div>
        `;

        card.addEventListener('click', () => {
            card.classList.toggle('is-flipped');
        });

        container.appendChild(card);
        return container;
    }

    function showNextCard() {
        if (currentQuestionIndex >= questions.length) {
            showSummary();
            submitResults();
            return;
        }

        // Use the shuffled questions array directly
        const questionData = questions[currentQuestionIndex];
        // const questionKey = questionData.key; // We need the original key for userAnswers

        flashcardArea.innerHTML = ''; // Clear previous card
        currentCardElement = createFlashcard(questionData.front, questionData.back);
        flashcardArea.appendChild(currentCardElement);
        controlsArea.style.display = 'block'; // Show controls
    }
    function recordAnswer(isCorrect) {
        // Use the key from the shuffled questions array
        const questionKey = questions[currentQuestionIndex].key;
        if (isCorrect) {
            userAnswers[questionKey] = exercise.correct_answers[questionKey];
            correctAnswersCount++;
        } else {
            userAnswers[questionKey] = "";
            incorrectAnswersCount++;
        }
        currentQuestionIndex++;
        showNextCard();
    }

    function showSummary() {
        flashcardArea.innerHTML = '';
        controlsArea.style.display = 'none';
        summaryArea.style.display = 'block';
        correctCountSpan.textContent = correctAnswersCount;
        incorrectCountSpan.textContent = incorrectAnswersCount;
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
                    type: 'flashcard'
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
                    front: value.front,
                    back: value.back
                }));
                console.log("Questions array before shuffle:", JSON.stringify(questions.map(q => q.front))); // Log before shuffle
                if (questions.length === 0) {
                    displayError("This word set has no words to practice.");
                    return;
                }
                // Shuffle the questions array
                shuffleArray(questions);
                console.log("Questions array AFTER shuffle:", JSON.stringify(questions.map(q => q.front))); // Log after shuffle
                showNextCard();
            } else {
                throw new Error("Exercise data is missing questions.");
            }

        } catch (error) {
            console.error("Error creating exercise:", error);
            displayError(`Error loading flashcards: ${error.message}`);
        }
    }

    async function submitResults() {
        if (!exercise || !exercise.id) {
            console.error("Cannot submit results, exercise ID is missing.");
            return;
        }

        const submitUrl = `/api/exercise/${exercise.id}/submit/`;
        const payload = { user_answers: userAnswers };

        console.log("Submitting answers:", payload);

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

            if (response.ok) {
                const result = await response.json();
                console.log("Submission successful:", result);
                // Optionally update UI based on result.is_correct or progress
            } else {
                const errorData = await response.json();
                console.error("Submission failed:", errorData);
                // Optionally display an error message on the summary page
                const summaryP = summaryArea.querySelector('p'); // Find a place to add error
                if (summaryP) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.textContent = `Error saving progress: ${JSON.stringify(errorData)}`;
                    summaryArea.insertBefore(errorDiv, summaryP.nextSibling);
                }
            }
        } catch (error) {
            console.error("Error submitting results:", error);
             const summaryP = summaryArea.querySelector('p');
             if (summaryP) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.textContent = `Network error saving progress: ${error.message}`;
                    summaryArea.insertBefore(errorDiv, summaryP.nextSibling);
             }
        }
    }

    // --- Event Listeners ---
    correctBtn.addEventListener('click', () => recordAnswer(true));
    incorrectBtn.addEventListener('click', () => recordAnswer(false));

    // --- Initial Load ---
    fetchOrCreateExercise();
});