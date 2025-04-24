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
        prepareWordsJSON();
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

function removeWord(button) {
    const wordItem = button.closest('.word-item');
    if (wordItem) {
        wordItem.remove();
    }
}

function createWordset() {
    prepareWordsJSON();

    const jsonData = document.getElementById('words-json').value;

    fetch('', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: jsonData
    });
}

function prepareWordsJSON() {
    const items = document.querySelectorAll('.word-item');
    const words = Array.from(items).map(item => ({
        word: item.getAttribute('data-word'),
        infinitive: item.getAttribute('data-infinitive'),
        translation: item.getAttribute('data-translation'),
    }));

    document.getElementById('words-json').value = JSON.stringify(words);
}

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