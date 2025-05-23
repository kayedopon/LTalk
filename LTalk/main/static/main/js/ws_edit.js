// This function send data to endpoint where wordset will be created
async function sendWordSet() {
    const wordsetId = document.getElementById('wordset-id').getAttribute('data-id');
    const csrfToken = getCSRFToken();

    const data = {
        title: document.getElementById('wordset-title').value,
        description: document.getElementById('wordset-description').value,
        public: document.getElementById('wordset-public').checked,
        words: JSON.parse(document.getElementById('words-json').value)
    };

    try {
        const response = await fetch(`/api/wordset/${wordsetId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            window.location.href = `/wordset/${wordsetId}/`;
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


function displayResult(result) {
    const resultDiv = document.getElementById('wordset-edit');

    if (result.error) {
        resultDiv.innerHTML = `<div class="error-message">${result.error}</div>`;
        return;
    }

    const form  = document.createElement('form');
    form.id     = 'word-form';
    form.method = 'post';             // used only by JS; server will be hit via fetch
    form.onsubmit = (e) => {
        e.preventDefault();          
        prepareWordsJSON();           // collects values from inputs
        sendWordSet();               
    };

    /* CSRF hidden field + title/description */
    const csrfToken = getCSRFToken();
    form.innerHTML = `
        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
        <input type="hidden" name="words_json" id="words-json">
        <input type="text"   name="wordset_title" id="wordset-title"
            class="wordset-input" placeholder="Enter word set title" required>
        <input type="text"   name="wordset_description" id="wordset-description"
            class="wordset-input" placeholder="Short description (optional)">
        <label class="privacy-toggle">
            <input type="checkbox" id="wordset-public">
            <span>Make&nbsp;public</span>
        </label>
    `;
    console.log("|||")

    /* ----- 2. table-like container with editable cells ------------------ */
    const container = document.createElement('div');
    container.className = 'words-container';

    /* header row */
    container.innerHTML = `
        <div class="words-header">
            <div class="header-word">Word</div>
            <div class="header-infinitive">Base form</div>
            <div class="header-translation">Translation</div>
            <div class="header-actions">Actions</div>
        </div>
    `;

    /* list of rows */
    const list = document.createElement('ul');
    list.className = 'words-list';

    result.words.forEach((item, idx) => {
        const li = document.createElement('li');
        li.className = 'word-item';

        li.innerHTML = `
            <input type="text" class="word-input"        value="${item.word}"
                   data-field="word">
            <input type="text" class="infinitive-input" value="${item.infinitive}"
                   data-field="infinitive">
            <input type="text" class="translation-input"value="${item.translation}"
                   data-field="translation">
            <button type="button" class="remove-btn" onclick="removeWord(this)">
                Delete
            </button>
        `;
        list.appendChild(li);
    });

    container.appendChild(list);
    form.appendChild(container);


    const submitBtn = document.createElement('button');
    submitBtn.type = 'submit';
    submitBtn.className = 'upload-button';
    submitBtn.textContent = 'Edit Word Set';
    form.appendChild(submitBtn);


    resultDiv.innerHTML = '';
    resultDiv.appendChild(form);

    document.getElementById('wordset-title').value = result.title;
    document.getElementById('wordset-description').value = result.description;
    document.getElementById('wordset-public').checked = result.public;
}


function prepareWordsJSON() {
    const items = document.querySelectorAll('.word-item');
    const words = Array.from(items).map(item => {
        const obj = {};
        item.querySelectorAll('input[data-field]').forEach(inp => {
            obj[inp.dataset.field] = inp.value.trim();
        });
        return obj;
    });
    document.getElementById('words-json').value = JSON.stringify(words);
}

function removeWord(btn) {
    btn.closest('.word-item').remove();
}

async function fetchWords() {
    const wordsetId = document.getElementById('wordset-id').getAttribute('data-id');
    document.getElementById('wordset-edit').innerHTML = '<div class="loading-message">Loading words…</div>';

    try {

        const response = await fetch(`/api/wordset/${wordsetId}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Accept': 'application/json'
            }
        })

        const result = await response.json();

        displayResult(result);

    } catch (err) {
        displayResult({ error: 'An error occurred while processing your request.' });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    fetchWords();
});