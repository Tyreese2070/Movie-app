document.addEventListener('DOMContentLoaded', function () {
    // Check if the toggle button exists before trying to manipulate it
    var toggleButton = document.getElementById('toggle-dark-mode');

    // Check if dark mode is already set in localStorage
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        if (toggleButton) {
            toggleButton.textContent = 'Light Mode';
        }
    } else {
        if (toggleButton) {
            toggleButton.textContent = 'Dark Mode';
        }
    }

    // Only add event listener if the button is present
    if (toggleButton) {
        toggleButton.addEventListener('click', function () {
            // Toggle dark mode class
            document.body.classList.toggle('dark-mode');

            // Update localStorage based on the new mode
            if (document.body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');
                toggleButton.textContent = 'Light Mode';
            } else {
                localStorage.setItem('darkMode', 'disabled');
                toggleButton.textContent = 'Dark Mode';
            }
        });
    }
});
