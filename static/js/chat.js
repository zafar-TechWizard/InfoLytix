document.addEventListener("DOMContentLoaded", function () {
    const chatMessages = document.getElementById("chat-messages");
    const chatInput = document.getElementById("chat-input");
    const chatForm = document.getElementById("chat-form");
    const sendBtn = document.getElementById("send-btn");


    let convoId = window.location.pathname.split("/").pop(); // Get convo_id from URL
    let isWaitingForResponse = false;

    let userMessages = document.querySelectorAll(".user-message").length;
    let botMessages = document.querySelectorAll(".bot-message").length;

    // Load conversation history
    async function loadConversationHistory() {
        try {
            const response = await fetch(`/api/conversations/${convoId}/history`);
            if (!response.ok) throw new Error('Failed to fetch history');
            
            const data = await response.json();
            if (data.status && data.messages) {
                chatMessages.innerHTML = ''; // Clear existing messages
                data.messages.forEach(msg => {
                    appendMessage(msg.user, 'user', false);
                    if (msg.bot) {
                        appendMessage(msg.bot, 'bot', false);
                    }
                });
                scrollToBottom();
            }
        } catch (error) {
            console.error("Failed to load conversation:", error);
            appendMessage("⚠️ Failed to load conversation history.", "bot");
        }
    }

    // If there's only one user message and no bot message, fetch response
    if (userMessages === 1 && botMessages === 0) {
        let userQuery = document.querySelector(".user-message .message-content").innerText;

        if (userQuery) {
            fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: userQuery, convo_id: convoId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    appendMessage(data.response, "bot");
                } else {
                    appendMessage("⚠️ Error fetching response. Try again.", "bot");
                }
            })
            .catch(error => {
                console.error("Chat API error:", error);
                chatMessages.removeChild(loadingDiv);
                appendMessage("⚠️ Error fetching response. Try again.", "bot");
            })
            .finally(() => {
                isWaitingForResponse = false;
                sendBtn.disabled = false;
                sendBtn.classList.remove("opacity-50", "cursor-not-allowed");
            });
        }
    }




    function typeWriter(element, text) {
        return new Promise((resolve) => {
            let i = 0;
            element.innerHTML = '';
            const words = text.split(' ');
            
            function type() {
                if (i < words.length) {
                    element.innerHTML += (i > 0 ? ' ' : '') + words[i];
                    i++;
                    scrollToBottom()
                    setTimeout(type, 10); // Adjust word typing speed
                } else {
                    resolve();
                }
            }
            type();
        });
    }


    function scrollToBottom() {
        const chatMessages = document.getElementById("chat-messages");
        if (!chatMessages) {
            console.error("Chat messages container not found!");
            return;
        }
    
        // Calculate scroll distance
        const scrollDistance = chatMessages.scrollHeight - chatMessages.clientHeight;
        
        // Get the last message
        const lastMessage = chatMessages.lastElementChild;
        
        // Add new-message class only to the last message
        if (lastMessage) {
            lastMessage.classList.add('new-message');
            
            // Remove the class after animation completes
            setTimeout(() => {
                lastMessage.classList.remove('new-message');
            }, 800);
        }
    
        // Smooth scroll to bottom
        chatMessages.scrollTo({
            top: scrollDistance +50,
            behavior: 'smooth'
        });
    }
    
    const chatContainer = document.getElementById("chat-container");
    console.log("Scroll height:", chatContainer.scrollHeight);
    console.log("Current scroll position:", chatContainer.scrollTop);

    function appendMessage(content, sender) {
        const messageDiv = document.createElement("div");
        // messageDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
        messageDiv.classList.add("message", `${sender}-message`);

        const contentWrapper = document.createElement("div");
        contentWrapper.classList.add("message-content");

        if (sender === "user") {
            contentWrapper.innerHTML = content;
            messageDiv.appendChild(contentWrapper);
            chatMessages.appendChild(messageDiv);
            setTimeout(scrollToBottom, 100);
        } else {
            // content = content.response.replace(/\n/g, "<br>") // Replace new lines with <br>
            //     .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // Bold text
            //     .replace(/```([\s\S]*?)```/g, "<pre><cmd>$1</cmd></pre>"); // Code blocks
            
                // For bot messages
            contentWrapper.innerHTML = '<span class="typing-indicator">●●●</span>';
            messageDiv.appendChild(contentWrapper);
            chatMessages.appendChild(messageDiv);
            setTimeout(() => {
                typeWriter(contentWrapper, content).then(() => {
                    // scrollToBottom();
                });
            }, 10); // Small delay before starting to type
        }
    }

    function showLoading() {
        const loadingDiv = document.createElement("div");
        loadingDiv.classList.add("message", "bot-message", "loading-message");
        loadingDiv.innerHTML = '<div class="typing-indicator">●●●</div>';
        chatMessages.appendChild(loadingDiv);
        scrollToBottom();
        return loadingDiv;
    }


    // ✅ Handle form submission without reloading
    chatForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const query = chatInput.value.trim();
        if (!query || isWaitingForResponse) return;

        isWaitingForResponse = true; // Disable sending until response arrives
        sendBtn.disabled = true;
        chatInput.disabled = true;
        sendBtn.classList.add("opacity-50", "cursor-not-allowed");

        appendMessage(query, "user");
        chatInput.value = "";

        const loadingDiv = showLoading();

        fetch(`/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, convo_id: convoId }) // Send convo_id if exists
        })
        .then(response => response.json())
        .then(data => {
            chatMessages.removeChild(loadingDiv);
            if (data.success) {
                appendMessage(data.response, "bot");
            } else {
                appendMessage("⚠️ Error fetching response. Try again.", "bot");
            }
        })
        .catch(error => {
            console.error("Chat API error:", error);
            chatMessages.removeChild(loadingDiv);
            appendMessage("⚠️ Error fetching response. Try again.", "bot");
        })
        .finally(() => {
            isWaitingForResponse = false;
            sendBtn.disabled = false;
            chatInput.disabled = false;
            chatInput.focus();
            sendBtn.classList.remove("opacity-50", "cursor-not-allowed");
        });
    });
    scrollToBottom();

    
});
