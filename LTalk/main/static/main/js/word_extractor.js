function displayResult(result) {
    const resultDiv = document.getElementById('result');
    if (result.error) {
        resultDiv.innerHTML = `<div class="error-message">${result.error}</div>`;
        return;
    }

    const wordsList = document.createElement('ul');
    wordsList.className = 'words-list';

    result.words.forEach(item => {
        const li = document.createElement('li');
        li.className = 'word-item';
        li.innerHTML = `
            <span class="word">${item.word}</span>
            <span class="infinitive">(${item.infinitive})</span>
            <span class="translation">${item.translation}</span>
        `;
        wordsList.appendChild(li);
    });

    resultDiv.innerHTML = '';
    resultDiv.appendChild(wordsList);
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);

        try {
            const response = await fetch('', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            displayResult(result);
        } catch (error) {
            displayResult({ error: 'An error occurred while processing your request.' });
        }
    });
});
