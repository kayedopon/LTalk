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

// Add this to word_extractor.js
const translations = {
    'en': {
        'word': 'Word',
        'infinitive': 'Infinitive',
        'translation': 'Translation',
        'add_word': 'Add Word',
        'remove': 'Remove',
        'file_selected': 'file selected',
        'files_selected': 'files selected',
        'no_files': 'No files selected',
        'processing': 'Processing...',
        'save_word_set': 'Save Word Set'
    },
    'uk': {
        'word': 'Слово',
        'infinitive': 'Інфінітив',
        'translation': 'Переклад',
        'add_word': 'Додати слово',
        'remove': 'Видалити',
        'file_selected': 'файл вибрано',
        'files_selected': 'файлів вибрано',
        'no_files': 'Файли не вибрані',
        'processing': 'Обробка...',
        'save_word_set': 'Зберегти набір слів'
    },
    'ru': {
        'word': 'Слово',
        'infinitive': 'Инфинитив',
        'translation': 'Перевод',
        'add_word': 'Добавить слово',
        'remove': 'Удалить',
        'file_selected': 'файл выбран',
        'files_selected': 'файлов выбрано',
        'no_files': 'Файлы не выбраны',
        'processing': 'Обработка...',
        'save_word_set': 'Сохранить набор слов'
    }
};

function t(key) {
    return translations[userLanguage] && translations[userLanguage][key] 
           ? translations[userLanguage][key] 
           : translations['en'][key] || key;
}

// Then use t() in your code:
// Example: removeButton.textContent = t('remove');

// This function send data to endpoint where wordset will be created
async function sendWordSet() {
    const csrfToken = getCSRFToken();

    const data = {
        title: document.getElementById('wordset-title').value,
        description: document.getElementById('wordset-description').value,
        public: document.getElementById('wordset-public').checked,
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
            window.location.href = `/wordset/${result.id}/`;
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
    console.log(result)
    const resultDiv = document.getElementById('result');

    /* ----- error handling unchanged ----- */
    if (result.error) {
        resultDiv.innerHTML = `<div class="error-message">${result.error}</div>`;
        return;
    }

    /* ----- 1. build the edit-form -------------------------------------- */
    const form = document.createElement('form');
    form.id = 'word-form';
    form.method = 'post';
    
    
    
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
        <input type="text" name="wordset_title" id="wordset-title"
            class="wordset-input" placeholder="Enter word set title" required>
        <input type="text" name="wordset_description" id="wordset-description"
            class="wordset-input" placeholder="Short description (optional)">
        <label class="privacy-toggle">
            <input type="checkbox" id="wordset-public">
            <span>Make&nbsp;public</span>
        </label>
        <div class="words-container" id="words-container"></div>
        <button type="button" class="new-word" id="new-word">Add new word</button>
    `;
    let container = form.querySelector("#words-container");
    const newWord = form.querySelector("#new-word");
    newWord.addEventListener('click', addNewWord);

    // header row
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
                   data-field="word" required>
            <input type="text" class="infinitive-input" value="${item.infinitive}"
                   data-field="infinitive" required>
            <input type="text" class="translation-input"value="${item.translation}"
                   data-field="translation" required>
            <button type="button" class="remove-btn" onclick="removeWord(this)">
                Delete
            </button>
        `;
        list.appendChild(li);
    });

    container.appendChild(list);

    /* submit button */
    const submitBtn = document.createElement('button');
    submitBtn.type = 'submit';
    submitBtn.className = 'upload-button';
    submitBtn.id = 'create-wordset';
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

    const wordsList = document.querySelector(".words-list");
    if (wordsList.children.length == 0) {
        const btn = document.getElementById('create-wordset');
        btn.remove();  
    }
}

function addNewWord() {
    const form = document.getElementById('word-form');
    let container = form.querySelector('.words-container');
    let list = container.querySelector('.words-list');

    if (!list) {
        container.innerHTML = `
            <div class="words-header">
                <div class="header-word">Word</div>
                <div class="header-infinitive">Base form</div>
                <div class="header-translation">Translation</div>
                <div class="header-actions">Actions</div>
            </div>
        `;
        list = document.createElement('ul');
        list.className = 'words-list';
        container.appendChild(list);

        form.onsubmit = (e) => {
            e.preventDefault();           
            prepareWordsJSON();           
            sendWordSet();              
        };

    }

    if (list.children.length === 0) {
        const submitBtn = document.createElement('button');
        submitBtn.type = 'submit';
        submitBtn.className = 'upload-button';
        submitBtn.id = 'create-wordset'
        submitBtn.textContent = 'Create Word Set';
        form.appendChild(submitBtn);
    }

    const li = document.createElement('li');
    li.className = 'word-item';

    li.innerHTML = `
        <input type="text" class="word-input"       
                data-field="word" required>
        <input type="text" class="infinitive-input" 
                data-field="infinitive" required>
        <input type="text" class="translation-input"
                data-field="translation" required>
        <button type="button" class="remove-btn" onclick="removeWord(this)">
            Delete
        </button>
    `;
    list.appendChild(li);
}

// DOMContentLoaded listener to handle the form submission asynchronously
document.addEventListener('DOMContentLoaded', function() {
    const chosenFiles = [];     // each element is the actual File object
    const form = document.getElementById('form1');
    const imageInput = document.getElementById('image-input');
    const fileNameSpan = document.getElementById('file-name');
    const fileListUl   = document.getElementById('file-list');

    const addWord = document.getElementById('new-word');

    addWord.addEventListener('click', addNewWord)

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
            console.log(err)
            displayResult({ error: 'An error occurred while processing your request.' });
        }
    });
});