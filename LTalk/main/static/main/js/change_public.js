document.addEventListener('DOMContentLoaded', function() {
    const toggleEl = document.getElementById("visibility-toggle");
    toggleEl.addEventListener('click', function () {
        const ws_id = toggleEl.dataset.id;
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
        });
})

