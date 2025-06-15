// Add at the beginning of the file
const translations = {
    'en': {
        'word': 'word',
        'words': 'words', 
        'no_sets_found': 'No public word sets found.',
        'loading': 'Loading...',
        'add_to_my_sets': 'Add to My Sets',
        'added': 'Added!',
        'error': 'Error'
    },
    'uk': {
        'word': 'слово', 
        'words': 'слів',
        'no_sets_found': 'Публічних наборів слів не знайдено.',
        'loading': 'Завантаження...',
        'add_to_my_sets': 'Додати до моїх наборів',
        'added': 'Додано!',
        'error': 'Помилка'
    },
    'ru': {
        'word': 'слово', 
        'words': 'слов',
        'no_sets_found': 'Публичных наборов слов не найдено.',
        'loading': 'Загрузка...',
        'add_to_my_sets': 'Добавить в мои наборы',
        'added': 'Добавлено!',
        'error': 'Ошибка'
    }
};

function t(key) {
    return translations[userLanguage] && translations[userLanguage][key] 
           ? translations[userLanguage][key] 
           : translations['en'][key] || key;
}

// Then use t() in your code:
// Example: loadingElement.textContent = t('loading');

document.addEventListener('DOMContentLoaded', () => {
    let apiUrl = `/api/wordset/?page=1&scope=others`;
    let searchQuery = '';
    const searchInput = document.getElementById('search-input');
    const wordsetsList = document.getElementById('wordsets-list');
    const loadingIndicator = document.getElementById('loading');
    const noWordsetsMsg = document.querySelector('.no-wordsets');

    searchInput.addEventListener('input', () => {
        searchQuery = searchInput.value.trim(); 
        wordsetsList.innerHTML = ''; 

        if (searchQuery === '') {
            apiUrl = `/api/wordset/?page=1&scope=others`;
            getWordSets();
            return;
        }

        fetch(`/api/wordset/?scope=others&search=${encodeURIComponent(searchQuery)}`)
            .then(response => response.json())
            .then(data => {
                wordsetsList.innerHTML = '';
                loadingIndicator.style.display = 'none';

                if (data.results.length > 0) {
                    generateWordSet(data);
                    apiUrl = data.next || null;
                } else {
                    noWordsetsMsg.style.display = 'block';
                    apiUrl = null;
                }
            })
            .catch(err => {
                loadingIndicator.style.display = 'none';
                console.error('Search failed:', err);
                wordsetsList.innerHTML = '<p>Error fetching word sets.</p>';
            });
    });

    function getWordSets() {
        if (!apiUrl) return;
        loadingIndicator.style.display = 'block';
    
        fetch(apiUrl)
            .then(response => response.json())
            .then(data => {
                loadingIndicator.style.display = 'none';
    
                if (data.results.length > 0) {
                    generateWordSet(data);
                    noWordsetsMsg.style.display = 'none';
                    apiUrl = data.next || null;
                } else if (wordsetsList.children.length === 0) {
                    noWordsetsMsg.style.display = 'block';
                }
            })
            .catch(error => {
                loadingIndicator.style.display = 'none';
                console.error('Failed to fetch word sets:', error);
            });
    }

    function generateWordSet(data) {
        data.results.forEach(wordset => {
            const wordsetElement = document.createElement('li');
            wordsetElement.classList.add('word-set');

            wordsetElement.innerHTML = `
                <div class="word-set-content" data-id="${wordset.id}">
                    <div>
                        <div class="word-set-title">${wordset.title}</div>
                        <div class="word-count">${wordset.words.length} words</div>
                    </div>
                </div>
            `;

            wordsetElement.querySelector('.word-set-content').addEventListener("click", function() {
                const id = this.getAttribute("data-id");
                window.location.href = `/wordset/${id}/?from_explore=true`;
            });

            wordsetsList.appendChild(wordsetElement);
        });
    }

    getWordSets();

    window.addEventListener('scroll', function () {
        if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100) {
            if (loadingIndicator.style.display === 'none' && apiUrl !== null) {
                getWordSets();
            }
        }
    });
});
