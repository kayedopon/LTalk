document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.type-button');
    const lists = document.querySelectorAll('.progress-list');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const type = button.getAttribute('data-type');

            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            lists.forEach(list => {
                list.style.display = list.getAttribute('data-type') === type ? 'block' : 'none';
            });
        });
    });

    if (buttons.length > 0) {
        buttons[0].click();
    }
});
