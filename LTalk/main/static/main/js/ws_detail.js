document.addEventListener('DOMContentLoaded', function() {
    const toggleEl = document.getElementById("visibility-toggle");
    const ws_id = toggleEl.dataset.id;
    const button = document.getElementById("add-wordset")

    toggleEl.addEventListener('click', () => changePublic());
    if (button) {
        button.addEventListener("click", () => addWordSet(ws_id));
    }

    function changePublic() {
        const current = toggleEl.dataset.current === "true";
        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        fetch(`/api/wordset/${ws_id}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
                body: JSON.stringify({
                public: !current
                })
            })
            .then(res => {
                if (!res.ok) throw new Error("Failed to update visibility");
        
                return res.json();
            })
            .then(data => {
                toggleEl.dataset.current = data.public;
                toggleEl.textContent = data.public ? "Public" : "Private";
            })
            .catch(err => {
                console.error(err);
                alert("Failed to update visibility.");
        });
    }

    function addWordSet(wordsetId) {
        fetch(`/api/wordset/${wordsetId}/duplicate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken() 
            }
        })
        .then(response => {
            return response.json().then(data => {
                if (!response.ok) {
                    throw new Error(data.error || "Unknown error");
                }
                return data;
            });
        })
        .then(data => {
            if (data)
            {
                window.location.href = `/wordset/${data.id}/`;
            }
            
        })
        .catch(error => {
            alert(error);
        });
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


    
})

