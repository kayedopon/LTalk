// This function prepares the words data as a JSON string for submission
function prepareWordsJSON() {
    const items = document.querySelectorAll('.word-item');
    const words = Array.from(items).map(item => ({
        word: item.getAttribute('data-word'),
        infinitive: item.getAttribute('data-infinitive'),
        translation: item.getAttribute('data-translation'),
    }));

    document.getElementById('words-json').value = JSON.stringify(words);
}

// This function send data to endpoint where wordset will be created
async function sendWordSet() {
    const csrfToken = getCSRFToken();

    const data = {
        title: document.getElementById('wordset-title').value,
        description: document.getElementById('wordset-description').value,
        words: JSON.parse(document.getElementById('words-json').value)
    };

    try {
        const response = await fetch('/api/wordset/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        console.log(response);

        if (response.ok) {
            displayResult(result); // here we should redirect user to wordlist
        } else {
            displayResult({ error: result.detail || 'An error occurred while processing your request.' });
        }
    } catch (error) {
        console.error('Request failed:', error);
        displayResult({ error: 'An error occurred while processing your request.' });
    }
}


// This function handles word deletion when a user clicks on the delete button
function removeWord(button) {
    const wordItem = button.closest('.word-item');
    if (wordItem) {
        wordItem.remove();
    }
}

// This function retrieves the CSRF token from cookies
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

// This function sends the form data and displays the result
function displayResult(result) {
    const resultDiv = document.getElementById('result');
    if (result.error) {
        resultDiv.innerHTML = `<div class="error-message">${result.error}</div>`;
        return;
    }
   
    const form  = document.createElement('form');
    form.id = 'word-form';
    form.method = 'post';
    const wordsList = document.createElement('ul');
    form.onsubmit = (e) => {
        e.preventDefault();
        prepareWordsJSON();
        sendWordSet();

        return true;
    };

    const csrfToken = getCSRFToken();
    form.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                      <input type="hidden" name="words_json" id="words-json">
                      <input type="text" name="wordset_title" id="wordset-title" class="wordset-input" placeholder="Enter word set title" required>
                      <input type="text" name="wordset_description" id="wordset-description" class="wordset-input" placeholder="Short description (optional)">`;

    wordsList.className = 'words-list';

    result.words.forEach(item => {
        const li = document.createElement('li');
        li.className = 'word-item';
        li.setAttribute('data-word', item.word);
        li.setAttribute('data-infinitive', item.infinitive);
        li.setAttribute('data-translation', item.translation);
        li.innerHTML = `
            <span class="word">${item.word}</span>
            <span class="infinitive">(${item.infinitive})</span>
            <span class="translation">${item.translation}</span>
            <button type="button" class="remove-btn" onclick="removeWord(this)">Delete</button>
        `;
        wordsList.appendChild(li);
    });

    const submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.className = 'upload-button';
    submitButton.textContent = 'Create Word Set';

    form.appendChild(wordsList);
    form.appendChild(submitButton);

    resultDiv.innerHTML = '';
    resultDiv.appendChild(form);
}

// DOMContentLoaded listener to handle the form submission asynchronously
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('form1');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);

        try {
            const response = await fetch('/photo-processing', {
                method: 'POST',
                body: formData,
            });
            const result = await response.json();
            displayResult(result);
        } catch (error) {
            displayResult({ error: 'An error occurred while processing your request.' });
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('form1');
    const imageInput = document.getElementById('image-input');
    const fileNameSpan = document.getElementById('file-name');

    imageInput.addEventListener('change', function() {
        if (imageInput.files.length > 0) {
            fileNameSpan.textContent = imageInput.files[0].name;
        } else {
            fileNameSpan.textContent = '';
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);

        // Show loading message
        document.getElementById('result').innerHTML = '<div class="loading-message">Loading words...</div>';

        try {
            const response = await fetch('/photo-processing', {
                method: 'POST',
                body: formData,
            });
            const result = await response.json();
            displayResult(result);
        } catch (error) {
            displayResult({ error: 'An error occurred while processing your request.' });
        }
    });
});