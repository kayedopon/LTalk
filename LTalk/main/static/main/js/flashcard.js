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

        const questionKey = Object.keys(exercise.questions)[currentQuestionIndex];
        const questionData = exercise.questions[questionKey];

        flashcardArea.innerHTML = ''; // Clear previous card
        currentCardElement = createFlashcard(questionData.front, questionData.back);
        flashcardArea.appendChild(currentCardElement);
        controlsArea.style.display = 'block'; // Show controls
    }

    function recordAnswer(isCorrect) {
        const questionKey = Object.keys(exercise.questions)[currentQuestionIndex];
        // For flashcards, the "answer" we submit is what was on the back
        userAnswers[questionKey] = exercise.correct_answers[questionKey];

        if (isCorrect) {
            correctAnswersCount++;
        } else {
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
        const apiUrl = `/api/exercise/?wordset=${wordsetId}&type=flashcard`;
        try {
            // 1. Try to fetch existing exercise
            let response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': getCSRFToken() // Needed even for GET if session auth is primary
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.results && data.results.length > 0) {
                    exercise = data.results[0]; // Use the first existing exercise
                    console.log("Fetched existing exercise:", exercise);
                } else {
                    // 2. If not found, create one
                    console.log("No existing exercise found, creating new one...");
                    response = await fetch('/api/exercise/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'X-CSRFToken': getCSRFToken()
                        },
                        body: JSON.stringify({
                            wordset: wordsetId,
                            type: 'flashcard'
                            // questions/answers are generated by backend
                        })
                    });

                    if (response.ok) {
                        exercise = await response.json();
                        console.log("Created new exercise:", exercise);
                    } else {
                        const errorData = await response.json();
                        throw new Error(`Failed to create exercise: ${JSON.stringify(errorData)}`);
                    }
                }
            } else {
                 const errorData = await response.json();
                 throw new Error(`Failed to fetch exercise: ${JSON.stringify(errorData)}`);
            }

            if (exercise && exercise.questions) {
                questions = Object.values(exercise.questions); // Get array of question objects
                if (questions.length === 0) {
                     displayError("This word set has no words to practice.");
                     return;
                }
                showNextCard();
            } else {
                throw new Error("Exercise data is missing questions.");
            }

        } catch (error) {
            console.error("Error fetching or creating exercise:", error);
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