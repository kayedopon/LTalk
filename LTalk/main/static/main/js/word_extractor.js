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
// ---------------------------------------------------------------------------
// REPLACEMENT displayResult – now renders editable <input> fields
// ---------------------------------------------------------------------------
function displayResult(result) {
    const resultDiv = document.getElementById('result');

    /* ----- error handling unchanged ----- */
    if (result.error) {
        resultDiv.innerHTML = `<div class="error-message">${result.error}</div>`;
        return;
    }

    /* ----- 1. build the edit-form -------------------------------------- */
    const form  = document.createElement('form');
    form.id     = 'word-form';
    form.method = 'post';             // used only by JS; server will be hit via fetch
    form.onsubmit = (e) => {
        e.preventDefault();           // we’ll handle submit manually
        prepareWordsJSON();           // collects values from inputs
        sendWordSet();                // your existing POST /api/wordset/
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
    `;

    /* ----- 2. table-like container with editable cells ------------------ */
    const container = document.createElement('div');
    container.className = 'words-container';

    /* header row */
    container.innerHTML = `
        <div class="words-header">
            <div class="header-word">Word</div>
            <div class="header-infinitive">Infinitive</div>
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

    /* submit button */
    const submitBtn = document.createElement('button');
    submitBtn.type = 'submit';
    submitBtn.className = 'upload-button';
    submitBtn.textContent = 'Create Word Set';
    form.appendChild(submitBtn);

    /* ----- 3. render the whole thing in #result ------------------------- */
    resultDiv.innerHTML = '';
    resultDiv.appendChild(form);
}

/* --------------------------------------------------------------------- */
/* helpers stay basically the same                                       */
/* --------------------------------------------------------------------- */
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

// DOMContentLoaded listener to handle the form submission asynchronously
document.addEventListener('DOMContentLoaded', function() {
    const chosenFiles = [];     // each element is the actual File object
    const form = document.getElementById('form1');
    const imageInput = document.getElementById('image-input');
    const fileNameSpan = document.getElementById('file-name');
    const fileListUl   = document.getElementById('file-list');

    // ---------- helper to refresh the visible list ----------
    function renderFileList() {
        // fallback: show the first file’s name inline (your old UI)
        if (chosenFiles.length === 0) {
            fileNameSpan.textContent = '';
        } else {
            fileNameSpan.textContent = `${chosenFiles.length} file(s) selected`;
        }

        // nicer list under the button
        fileListUl.innerHTML = '';
        chosenFiles.forEach((file, idx) => {
            const li = document.createElement('li');
            li.textContent = file.name;
            // (optional) add a small “×” so user can remove a file
            const removeBtn = document.createElement('button');
            removeBtn.textContent = '✕';
            removeBtn.type = 'button';
            removeBtn.className = 'remove-file-btn';
            removeBtn.onclick = () => {
                chosenFiles.splice(idx, 1);
                renderFileList();
            };
            li.appendChild(removeBtn);
            fileListUl.appendChild(li);
        });
    }

    // ---------- when user picks files ----------
    imageInput.addEventListener('change', () => {
        // append every newly selected file to the persistent array
        for (const file of imageInput.files) {
            chosenFiles.push(file);
        }
        renderFileList();

        // IMPORTANT: reset the <input> so the same file can be chosen again
        imageInput.value = '';
    });

    // ---------- when the form is submitted ----------
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (chosenFiles.length === 0) {
            alert('Pick at least one image first');
            return;
        }

        const formData = new FormData();
        for (const file of chosenFiles) {
            formData.append('image', file);            // same field name as before
        }
        formData.append('csrfmiddlewaretoken', getCSRFToken());

        document.getElementById('result').innerHTML =
            '<div class="loading-message">Loading words…</div>';

        try {
            const response = await fetch('/api/process-photo/', {
                method: 'POST',
                body:   formData,
                credentials: 'same-origin'
            });
            const result = await response.json();
            displayResult(result);

            // on success you might want to clear files
            chosenFiles.length = 0;
            renderFileList();
        } catch (err) {
            displayResult({ error: 'An error occurred while processing your request.' });
        }
    });
});