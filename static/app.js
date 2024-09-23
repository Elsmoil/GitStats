// app.js

// This script adds basic interactivity, like showing a loading animation
// when the form is submitted or validating the input field.

document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const repoNameSelect = document.querySelector('select[name="repo_name"]');
    const repoUrlInput = document.querySelector('input[name="repo_url"]');
    const loadingIndicator = document.createElement('div');

    // Create a loading spinner element (basic example)
    loadingIndicator.innerHTML = '<p>Loading...</p>';
    loadingIndicator.style.display = 'none';
    loadingIndicator.style.position = 'fixed';
    loadingIndicator.style.top = '50%';
    loadingIndicator.style.left = '50%';
    loadingIndicator.style.transform = 'translate(-50%, -50%)';
    loadingIndicator.style.backgroundColor = '#fff';
    loadingIndicator.style.padding = '20px';
    loadingIndicator.style.border = '1px solid #ccc';
    loadingIndicator.style.boxShadow = '0 0 10px rgba(0,0,0,0.1)';
    document.body.appendChild(loadingIndicator);

    // Form submission event
    form.addEventListener('submit', function (event) {
        const repoName = repoNameSelect.value.trim();
        const repoUrl = repoUrlInput.value.trim();

        if (!repoName && !repoUrl) {
            event.preventDefault();  // Prevent form submission
            alert('Please select a repository from GitHub or enter a repository URL.');
            return;
        }

        // Show the loading indicator
        loadingIndicator.style.display = 'block';
    });
});

