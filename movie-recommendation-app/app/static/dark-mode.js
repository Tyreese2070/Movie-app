document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggle-dark-mode");

    // Apply saved dark mode preference on page load
    if (localStorage.getItem("darkMode") === "enabled") {
        document.body.classList.add("dark-mode");
        toggleButton.textContent = "Light Mode";
    }

    // Toggle dark mode on button click
    toggleButton.addEventListener("click", function () {
        const isDarkMode = document.body.classList.toggle("dark-mode");
        localStorage.setItem("darkMode", isDarkMode ? "enabled" : "disabled");
        toggleButton.textContent = isDarkMode ? "Light Mode" : "Dark Mode";
    });
});
