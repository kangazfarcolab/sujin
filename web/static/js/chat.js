// Chat functionality for Sujin Web UI

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const clearChatButton = document.getElementById('clear-chat');
    const tokenUsage = document.getElementById('token-usage');

    // State
    let conversationHistory = {}; // Keyed by agent ID
    let totalTokens = 0;
    let isWaitingForResponse = false;

    // Event listeners
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }

        // Auto-resize textarea
        setTimeout(() => {
            userInput.style.height = 'auto';
            userInput.style.height = (userInput.scrollHeight) + 'px';
        }, 0);
    });

    sendButton.addEventListener('click', sendMessage);

    clearChatButton.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            clearChat();
        }
    });

    // Functions
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message || isWaitingForResponse) return;

        // Get current agent ID
        const currentAgentId = window.agentManager.getCurrentAgentId();
        if (!currentAgentId) {
            addMessageToUI('system', 'Please select an agent first.');
            return;
        }

        // Initialize conversation history for this agent if needed
        if (!conversationHistory[currentAgentId]) {
            conversationHistory[currentAgentId] = [];
        }

        // Add user message to UI
        addMessageToUI('user', message);

        // Add to conversation history
        conversationHistory[currentAgentId].push({
            role: 'user',
            content: message
        });

        // Clear input
        userInput.value = '';
        userInput.style.height = 'auto';

        // Show typing indicator
        showTypingIndicator();

        // Set waiting state
        isWaitingForResponse = true;
        sendButton.disabled = true;

        // Send to API
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                history: conversationHistory[currentAgentId],
                agent_id: currentAgentId
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            hideTypingIndicator();

            if (data.error) {
                // Show error
                addMessageToUI('system', `Error: ${data.error}`);
            } else {
                // Add assistant message to UI
                addMessageToUI('assistant', data.message);

                // Add to conversation history
                conversationHistory[currentAgentId].push({
                    role: 'assistant',
                    content: data.message
                });

                // Update token usage
                if (data.usage) {
                    updateTokenUsage(data.usage);
                }
            }
        })
        .catch(error => {
            // Remove typing indicator
            hideTypingIndicator();

            // Show error
            addMessageToUI('system', `Error: ${error.message}`);
            console.error('Error:', error);
        })
        .finally(() => {
            // Reset waiting state
            isWaitingForResponse = false;
            sendButton.disabled = false;

            // Scroll to bottom
            scrollToBottom();
        });
    }

    function addMessageToUI(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        // Render markdown content
        const renderedContent = marked.parse(content);
        messageContent.innerHTML = renderedContent;

        messageDiv.appendChild(messageContent);

        // Add timestamp for non-system messages
        if (role !== 'system') {
            const metadata = document.createElement('div');
            metadata.className = 'message-metadata';
            metadata.textContent = new Date().toLocaleTimeString();
            messageDiv.appendChild(metadata);
        }

        chatMessages.appendChild(messageDiv);

        // Apply syntax highlighting to code blocks
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });

        // Scroll to bottom
        scrollToBottom();
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';

        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingDiv.appendChild(dot);
        }

        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function updateTokenUsage(usage) {
        totalTokens += usage.total_tokens || 0;
        tokenUsage.innerHTML = `
            <span>Tokens: ${totalTokens} total</span>
            <span>(Last: ${usage.prompt_tokens || 0} prompt, ${usage.completion_tokens || 0} completion)</span>
        `;
    }

    function clearChat() {
        // Get current agent ID
        const currentAgentId = window.agentManager.getCurrentAgentId();
        if (!currentAgentId) {
            return;
        }

        // Clear UI
        chatMessages.innerHTML = '';

        // Add welcome message
        const agentName = document.getElementById('current-agent-name').textContent;
        addMessageToUI('system', `Chat history cleared. You are now chatting with ${agentName}. How can I help you today?`);

        // Clear conversation history for this agent
        conversationHistory[currentAgentId] = [];

        // Reset token usage
        totalTokens = 0;
        tokenUsage.innerHTML = '<span>Tokens: 0</span>';
    }
});
