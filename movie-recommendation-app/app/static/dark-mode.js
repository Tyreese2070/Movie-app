document.addEventListener('DOMContentLoaded', function () {
    // Check if the toggle button exists
    var toggleButton = document.getElementById('toggle-dark-mode');

    // Check current mode in local storage
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

    // Only check for click if button is on the page
    if (toggleButton) {
        toggleButton.addEventListener('click', function () {
            // Toggle dark mode class
            document.body.classList.toggle('dark-mode');

            // Update local storage
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
