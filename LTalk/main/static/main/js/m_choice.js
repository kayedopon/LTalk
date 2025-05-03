document.addEventListener('DOMContentLoaded', () => {
    const choiceArea = document.getElementById('m_choice-area');
    const summaryArea = document.getElementById('summary');
    const correctCountSpan = document.getElementById('correct-count');
    const incorrectCountSpan = document.getElementById('incorrect-count');

    let exercise = null;
    let questions = [];
    let currentQuestionIndex = 0;
    let userAnswers = {};
    let correctAnswersCount = 0;
    let incorrectAnswersCount = 0;
    let currentQuestionElement = null;

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
        choiceArea.innerHTML = `<div class="error-message">${message}</div>`;
    }

    function showLoading() {
        choiceArea.innerHTML = '<div class="loading">Loading questions...</div>';
        summaryArea.style.display = 'none';
    }


    function showNextQuestion() {
        if (currentQuestionIndex >= questions.length) {
            showSummary();
            submitResults();
            return;
        }
    
        const questionKey = Object.keys(exercise.questions)[currentQuestionIndex];
        const questionData = exercise.questions[questionKey];
    
        choiceArea.innerHTML = `
            <div id="question-block">
                <div id="question-text" class="question-text"></div>
                <div id="options" class="options-container"></div>
                <div id="feedback" class="feedback"></div>
                <button id="next-btn" class="next-btn">Next</button>
            </div>
        `;
        const questionBlock = document.getElementById('question-block');
        const questionText = document.getElementById('question-text');
        const optionsContainer = document.getElementById('options');
        const feedback = document.getElementById('feedback');
        const nextBtn = document.getElementById('next-btn');
    
        questionText.textContent = questionData.question;
        optionsContainer.innerHTML = '';
        feedback.style.display = 'none';
        nextBtn.style.display = 'none';
    
        questionData.choices.forEach(choice => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.textContent = choice;
    
            btn.addEventListener('click', () => {
                const isCorrect = choice === exercise.correct_answers[questionKey];
                recordAnswer(isCorrect);
                feedback.textContent = isCorrect ? '✅ Correct!' : `❌ Incorrect. Correct: ${exercise.correct_answers[questionKey]}`;
                feedback.style.display = 'block';
    
                const allButtons = optionsContainer.querySelectorAll('button');
                allButtons.forEach(b => b.disabled = true);
    
                nextBtn.style.display = 'inline-block';
            });
    
            optionsContainer.appendChild(btn);
        });
    
        nextBtn.onclick = showNextQuestion;
        questionBlock.style.display = 'block';
    }
    

    function recordAnswer(isCorrect) {
        const questionKey = Object.keys(exercise.questions)[currentQuestionIndex];
        // Submit what the user actually did
        if (isCorrect) {
            userAnswers[questionKey] = exercise.correct_answers[questionKey];
            correctAnswersCount++;
        } else {
            // Use a special value or leave blank to indicate incorrect
            userAnswers[questionKey] = ""; // or null
            incorrectAnswersCount++;
        }
        currentQuestionIndex++;
        // showNextCard();
    }
    

    function showSummary() {
        choiceArea.innerHTML = '';
        summaryArea.style.display = 'block';
        correctCountSpan.textContent = correctAnswersCount;
        incorrectCountSpan.textContent = incorrectAnswersCount;
    }

    async function fetchOrCreateExercise() {
        showLoading();
        const apiUrl = `/api/exercise/?wordset=${wordsetId}&type=multiple_choice`;
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
                            type: 'multiple_choice'
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
                showNextQuestion();
            } else {
                throw new Error("Exercise data is missing questions.");
            }

        } catch (error) {
            console.error("Error fetching or creating exercise:", error);
            displayError(`Error loading questions`);
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

    // --- Initial Load ---
    fetchOrCreateExercise();

})