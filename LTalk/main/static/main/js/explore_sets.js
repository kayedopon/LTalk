document.addEventListener('DOMContentLoaded', () => {

    let apiUrl = `/api/wordset/?page=1&scope=others`;

    function getWordSets() {
        try {
            fetch(apiUrl, {
                method: 'GET',
            })
            .then(response => response.json())
            .then(data => {
                if (data.results.length > 0) {
                    
                    generateWordSet(data);

                    if (data.next) {
                        apiUrl = data.next
                        console.log(apiUrl)
                        
                    } else {
                        apiUrl = null
                    }
                } else {
                    console.log("No wordsets available.");
                }
                console.log(data)
            })
        } catch (error) {
            console.log(error)
        }
    }

    function generateWordSet(data)
    {
        data.results.forEach(wordset => {
            const wordsetElement = document.createElement('li');
            wordsetElement.classList.add('word-set');

            wordsetElement.innerHTML = `
                <div class="word-set-info" data-id="${wordset.id}" style="cursor: pointer;">
                    <h8 class="word-set-title">${wordset.title}</h8>
                    <div class="word-set-details">
                        <span class="word-count">${wordset.words.length} words</span>
                    </div>
                </div>
            `;

            wordsetElement.getElementsByClassName('word-set-info')
            wordsetElement.addEventListener("click", function() {
                window.location.href = `/wordset/${wordset.id}/?from_explore=true`;  
            });

            document.getElementById('wordsets-list').appendChild(wordsetElement);
        });


    }

    getWordSets();

    window.addEventListener('scroll', function() {
        if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100) {

            if (document.getElementById('loading').style.display === 'none' && apiUrl !== null) {
                getWordSets();
            }
        }
    });
});

