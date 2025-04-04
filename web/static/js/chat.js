// Chat functionality for Sujin Web UI

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const clearChatButton = document.getElementById('clear-chat');
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const tokenUsage = document.getElementById('token-usage');
    
    // State
    let conversationHistory = [];
    let totalTokens = 0;
    let isWaitingForResponse = false;
    
    // Check API status on load
    checkApiStatus();
    
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
        
        // Add user message to UI
        addMessageToUI('user', message);
        
        // Add to conversation history
        conversationHistory.push({
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
                history: conversationHistory
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            hideTypingIndicator();
            
            if (data.error) {
                // Show error
                addMessageToUI('system', `Error: ${data.error}`);
                setStatus('error');
            } else {
                // Add assistant message to UI
                addMessageToUI('assistant', data.message);
                
                // Add to conversation history
                conversationHistory.push({
                    role: 'assistant',
                    content: data.message
                });
                
                // Update token usage
                if (data.usage) {
                    updateTokenUsage(data.usage);
                }
                
                setStatus('online');
            }
        })
        .catch(error => {
            // Remove typing indicator
            hideTypingIndicator();
            
            // Show error
            addMessageToUI('system', `Error: ${error.message}`);
            setStatus('error');
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
        // Clear UI
        chatMessages.innerHTML = '';
        
        // Add welcome message
        addMessageToUI('system', 'Chat history cleared. How can I help you today?');
        
        // Clear conversation history
        conversationHistory = [];
        
        // Reset token usage
        totalTokens = 0;
        tokenUsage.innerHTML = '<span>Tokens: 0</span>';
    }
    
    function checkApiStatus() {
        setStatus('loading');
        
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    setStatus('online');
                } else {
                    setStatus('offline');
                    addMessageToUI('system', `API Status: ${data.message}`);
                }
            })
            .catch(error => {
                setStatus('offline');
                addMessageToUI('system', `Error checking API status: ${error.message}`);
                console.error('Error checking API status:', error);
            });
    }
    
    function setStatus(status) {
        statusIndicator.className = `status-indicator ${status}`;
        
        switch (status) {
            case 'online':
                statusText.textContent = 'Online';
                break;
            case 'offline':
                statusText.textContent = 'Offline';
                break;
            case 'loading':
                statusText.textContent = 'Connecting...';
                break;
            case 'error':
                statusText.textContent = 'Error';
                break;
            default:
                statusText.textContent = status;
        }
    }
});
