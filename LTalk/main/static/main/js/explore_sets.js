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
