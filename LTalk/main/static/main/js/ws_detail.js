document.addEventListener('DOMContentLoaded', function() {
    const toggleEl = document.getElementById("visibility-toggle");
    const ws_id = toggleEl.dataset.id;
    const addButton = document.getElementById("add-wordset")
    const deleteButton = document.getElementById("delete-wordset")

    toggleEl.addEventListener('click', () => changePublic());
    if (addButton) {
        addButton.addEventListener("click", () => addWordSet(ws_id));
    }

    if (deleteButton) {
        deleteButton.addEventListener("click", () => deleteWordSet(ws_id));
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

    function deleteWordSet(wordsetId) {
        if (!confirm("Are you sure you want to delete this word set? This action cannot be undone.")) {
            return;
        }
    
        fetch(`/api/wordset/${wordsetId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                alert("Word set deleted successfully.");
                window.location.href = '/';
            } else {
                return response.json().then(err => {
                    throw new Error(err.detail || "Failed to delete word set.");
                });
            }
        })
        .catch(error => {
            console.error("Error deleting word set:", error);
            alert("Error deleting word set: " + error.message);
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

