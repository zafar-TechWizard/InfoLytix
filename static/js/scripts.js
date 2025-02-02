
const searchSection = document.getElementById('search-section');
const resultsSection = document.getElementById('results-section');
const mainTitle = document.getElementById('main-title');
const subTitle = document.getElementById('sub-title');
const responseDiv = document.getElementById('response');
const sourcesDiv = document.getElementById('sources');
const searchForm = document.getElementById('search-form');

// Perform search and fetch results from the backend
async function performSearch(event) {
    event.preventDefault();

    const queryInput = document.getElementById('query-input');
    const query = queryInput.value.trim();

    if (!query) return;

    

    
    console.log('query: ',query)

    // Fetch data from backend
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        if (!response.ok) {
            throw new Error('Failed to fetch results. Please try again.');
        }

        const data = await response.json();
        queryInput.value = ''
        // Update UI with results
        responseDiv.innerHTML = data.response.replace(/\n/g, "<br>") // Replace new lines with <br>
                                    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // Bold text
                                     // Inline code
                                    .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>"); // Code blocks
        // responseDiv.innerHTML = data.response
        // responseDiv.textContent = data.response;

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

// Add event listener to the form
searchForm.addEventListener('submit', performSearch);
