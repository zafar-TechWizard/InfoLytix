// Wait for DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function() {
    const sidebar = document.getElementById("sidebar");
    const headerButtons = document.querySelector(".header-buttons");
    const conversationsList = document.getElementById("conversations-list");
    const buyCoffee = document.querySelector('.byeMecoffee');
    const searchInput = document.getElementById("chat-search");
    const loadingEl = document.getElementById("conversations-loading");
    const errorEl = document.getElementById("conversations-error");
    const externalNewChat = document.getElementById("externalNewChat");
    let conversations = [];
    let searchTimeout;

    // Initial state with improved transitions
    buyCoffee.style.opacity = '0';
    buyCoffee.style.transform = 'translateX(-10px)';
    buyCoffee.style.transition = 'opacity 0.3s ease-out, transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)';

    
    // Add transition properties to elements that will animate
    sidebar.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
    headerButtons.style.transition = 'opacity 0.3s ease-out, transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
    conversationsList.style.transition = 'opacity 0.3s ease-out, transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)';

    // Toggle sidebar with improved animation
    document.getElementById("toggle-sidebar").addEventListener("click", function() {
        // Add transform to smooth out the width change
        if (sidebar.classList.contains('w-16')) {
            headerButtons.style.transform = 'translateX(0)';
            headerButtons.style.opacity = '1';
            buyCoffee.style.transform = 'translateX(0)';
            buyCoffee.style.opacity = '1';
        } else {
            headerButtons.style.transform = 'translateX(-10px)';
            headerButtons.style.opacity = '0';
            buyCoffee.style.transform = 'translateX(-20px)';
            buyCoffee.style.opacity = '0';
        }

        sidebar.classList.toggle("w-64");
        sidebar.classList.toggle("w-16");
        headerButtons.classList.toggle("hidden");
        conversationsList.classList.toggle("visible");
        document.getElementById("externalNewChat").classList.toggle("hidden");
    });

    // Debounced search
    searchInput.addEventListener("input", (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.toLowerCase();
        
        document.getElementById("search-loading").classList.remove("hidden");
        
        searchTimeout = setTimeout(() => {
            const filtered = conversations.filter(convo => 
                convo.title.toLowerCase().includes(query)
            );
            renderConversations(filtered);
            document.getElementById("search-loading").classList.add("hidden");
        }, 300); // 300ms debounce
    });

    // Load conversations with error handling
    async function loadConversations() {
        try {
            loadingEl.classList.add("visible");
            errorEl.classList.remove("visible");
            
            const response = await fetch("/api/conversations");
            if (!response.ok) throw new Error('Failed to fetch');
            
            const data = await response.json();
            if (data.status) {
                conversations = data.titles;
                renderConversations(conversations);
                loadingEl.classList.remove("visible"); // Add this line to hide loading
            }
        } catch (error) {
            console.error("Failed to load conversations:", error);
            errorEl.classList.add("visible");
        } finally {
            loadingEl.classList.remove("visible");
        }
    }

    function renderConversations(convos) {
        if (!conversationsList) return;
        
        const currentConvoId = window.location.pathname.split("/").pop();
        conversationsList.innerHTML = convos.map(convo => {
            const lastMessage = convo.messages?.[0]?.user || '';
            const preview = lastMessage.length > 30 ? lastMessage.substring(0, 30) + '...' : lastMessage;

            const updateTime = convo.updated_at ? new Date(convo.updated_at) : new Date(convo.last_updated);
            
            return `
                <div class="conversation-wrapper">
                    <a href="/chat.infolytix/${convo.convo_id}" 
                    class="conversation-item ${currentConvoId === convo.convo_id ? 'active' : ''}">
                        <div class="conversation-content">
                            <div class="conversation-title">${convo.title}</div>
                            <div class="conversation-time">${timeAgo(updateTime)}</div>
                            <button class="delete-button" data-convo-id="${convo.convo_id}">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                        </div>
                    </a>
                </div>
            `;
        }).join("");

        document.querySelectorAll('.delete-button').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const convoId = btn.dataset.convoId;
                if (confirm('Are you sure you want to delete this conversation?')) {
                    try {
                        const response = await fetch(`/api/conversations/${convoId}`, {
                            method: 'DELETE'
                        });
                        
                        if (response.ok) {
                            // If we're on the deleted conversation's page, redirect to main chat
                            if (window.location.pathname.includes(convoId)) {
                                window.location.href = '/chat.infolytix';
                            } else {
                                // Otherwise just refresh the conversation list
                                loadConversations();
                            }
                        } else {
                            throw new Error('Failed to delete conversation');
                        }
                    } catch (error) {
                        console.error('Error deleting conversation:', error);
                        alert('Failed to delete conversation. Please try again.');
                    }
                }
            });
        });
    }

    // Search functionality
    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = conversations.filter(convo => 
            convo.title.toLowerCase().includes(query)
        );
        renderConversations(filtered);
    });

    // Time ago function
    function timeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        const intervals = {
            year: 31536000,
            month: 2592000,
            week: 604800,
            day: 86400,
            hour: 3600,
            minute: 60
        };
        
        for (const [unit, secondsInUnit] of Object.entries(intervals)) {
            const interval = Math.floor(seconds / secondsInUnit);
            if (interval >= 1) {
                return interval === 1 ? `1 ${unit} ago` : `${interval} ${unit}s ago`;
            }
        }
        return "Just now";
    }

    // Initial load
    loadConversations();
    
    // Refresh conversations periodically
    setInterval(loadConversations, 15000); // Every 30 seconds
});


document.addEventListener("DOMContentLoaded", function() {

    // Add search button click handler
    const searchBtn = document.querySelector('.search-btn');
    const chatSearch = document.querySelector('.chat-search');

    searchBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        chatSearch.classList.toggle('hidden');
        if (!chatSearch.classList.contains('hidden')) {
            document.getElementById('chat-search').focus();
        }
    });

    // Close search when clicking outside
    document.addEventListener('click', function(e) {
        if (!chatSearch.contains(e.target) && !searchBtn.contains(e.target)) {
            chatSearch.classList.add('hidden');
        }
    });

    // Add click event to button
    triggerBtn.addEventListener("click", function(e) {
        e.stopPropagation();
        if (popupContent.style.display === "block") {
        popupContent.style.display = "none";
        } else {
        popupContent.style.display = "block";
        }
    });

    // Close when clicking outside
    document.addEventListener("click", function(e) {
        if (!popupContent.contains(e.target) && e.target !== triggerBtn) {
        popupContent.style.display = "none";
        }
    });
});


