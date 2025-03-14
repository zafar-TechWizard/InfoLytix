document.addEventListener("DOMContentLoaded", function () {
    const searchSection = document.getElementById('search-section');
    const resultsSection = document.getElementById('results-section');
    const mainTitle = document.getElementById('main-title');
    const subTitle = document.getElementById('sub-title');
    const responseDiv = document.getElementById('response');
    const sourcesDiv = document.getElementById('sources');
    const searchForm = document.getElementById('search-form');
    const queryInput = document.getElementById('query-input');
    const searchIcon = document.querySelector('.filterBorder');

    // Debugging: Check if script is loading multiple times
    console.log("Script Loaded");

    // Perform search and fetch results from the backend
    async function performSearch(event) {
        event.preventDefault();

        const query = queryInput.value.trim();

        if (!query) return;

        console.log('Query:', query);

        // Fetch data from backend
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query }),
            });

            console.log('Received response from backend');

            if (!response.ok) {
                throw new Error('Failed to fetch results. Please try again.');
            }

            const data = await response.json();
            queryInput.value = '';

            // Update UI with results
            responseDiv.innerHTML = data.response.replace(/\n/g, "<br>") // Replace new lines with <br>
                .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // Bold text
                .replace(/```([\s\S]*?)```/g, "<pre><cmd>$1</cmd></pre>"); // Code blocks
            
            // Clear previous sources
            sourcesDiv.innerHTML = '';

            // Add sources dynamically
            data.sources.forEach((source) => {
                const sourceElement = document.createElement('div');
                sourceElement.className = 'text-gray-400';
                sourceElement.innerHTML = `
                    <a href="${source.link}" target="_blank" class="text-blue-500 hover:underline">
                        ${source.name}
                    </a>
                `;
                sourcesDiv.appendChild(sourceElement);
            });

            // Transition search bar to the upper position
            searchSection.classList.add('min-h-[20vh]');
            searchSection.classList.remove('min-h-screen');
            resultsSection.classList.remove('hidden');
        } catch (error) {
            alert(error.message);
        }
    }

    // Attach event listener to the search form (if not already attached)
    if (!searchForm.dataset.listenerAttached) {
        searchForm.dataset.listenerAttached = true;

        searchForm.addEventListener('submit', (event) => {
            event.preventDefault();
            performSearch(event);
        });

        console.log("Event listener attached to search form.");
    } else {
        console.warn("Event listener was already attached!");
    }

    // Attach event listener to the search icon click
    if (searchIcon) {
        searchIcon.addEventListener("click", function () {
            searchForm.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
        });

        console.log("Search icon event listener attached.");
    } else {
        console.warn("Search icon not found.");
    }
});
