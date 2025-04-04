// Agent management functionality for Sujin Web UI

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const agentList = document.getElementById('agent-list');
    const serviceStatus = document.getElementById('service-status');
    const newAgentButton = document.getElementById('new-agent-button');
    const agentModal = document.getElementById('agent-modal');
    const closeModal = document.getElementById('close-modal');
    const cancelAgent = document.getElementById('cancel-agent');
    const agentForm = document.getElementById('agent-form');
    const currentAgentName = document.getElementById('current-agent-name');
    const agentModel = document.getElementById('agent-model');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // State
    let agents = [];
    let currentAgentId = null;
    let serviceConnected = false;

    // Initialize
    checkServiceStatus();

    // Event listeners
    newAgentButton.addEventListener('click', showAgentModal);
    closeModal.addEventListener('click', hideAgentModal);
    cancelAgent.addEventListener('click', hideAgentModal);
    agentForm.addEventListener('submit', createAgent);

    // Functions
    function checkServiceStatus() {
        updateServiceStatus('connecting', 'Connecting to agent service...');

        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    updateServiceStatus('online', 'Agent service online');
                    serviceConnected = true;
                    loadAgents();
                } else if (data.status === 'warning') {
                    updateServiceStatus('warning', data.message);
                    serviceConnected = true;
                    loadAgents();
                } else {
                    updateServiceStatus('offline', data.message || 'Agent service offline');
                    serviceConnected = false;
                }
            })
            .catch(error => {
                console.error('Error checking service status:', error);
                updateServiceStatus('offline', 'Cannot connect to agent service');
                serviceConnected = false;
            });
    }

    // Agent service is always started automatically by the web UI

    function updateServiceStatus(status, message) {
        serviceStatus.className = `service-status ${status}`;
        serviceStatus.innerHTML = `<i class="fas fa-${getStatusIcon(status)}"></i> ${message}`;
    }

    function getStatusIcon(status) {
        switch (status) {
            case 'online': return 'check-circle';
            case 'offline': return 'times-circle';
            case 'warning': return 'exclamation-circle';
            case 'connecting': return 'circle-notch fa-spin';
            default: return 'question-circle';
        }
    }

    function loadAgents() {
        // Show loading state
        agentList.innerHTML = `
            <div class="loading-indicator">
                <i class="fas fa-spinner fa-spin"></i> Loading agents...
            </div>
        `;

        fetch('/api/agents')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                agents = data.agents || [];

                if (agents.length === 0) {
                    agentList.innerHTML = `
                        <div class="empty-state">
                            <p>No agents configured.</p>
                            <p>Click the + button to create your first agent.</p>
                        </div>
                    `;
                    disableChat();
                } else {
                    renderAgentList(agents, data.default_agent_id);

                    // Set current agent to default if available
                    if (data.default_agent_id && !currentAgentId) {
                        selectAgent(data.default_agent_id);
                    }
                }
            })
            .catch(error => {
                console.error('Error loading agents:', error);
                agentList.innerHTML = `
                    <div class="error-state">
                        <p>Error loading agents: ${error.message}</p>
                        <p>Make sure the agent service is running.</p>
                        <button id="retry-load-agents" class="primary-button">Retry</button>
                    </div>
                `;

                // Add retry button event listener
                setTimeout(() => {
                    const retryButton = document.getElementById('retry-load-agents');
                    if (retryButton) {
                        retryButton.addEventListener('click', loadAgents);
                    }
                }, 100);
            });
    }

    function renderAgentList(agents, defaultAgentId) {
        agentList.innerHTML = '';

        agents.forEach(agent => {
            const agentElement = document.createElement('div');
            agentElement.className = `agent-item ${agent.id === currentAgentId ? 'active' : ''}`;
            agentElement.dataset.agentId = agent.id;

            agentElement.innerHTML = `
                <div class="agent-item-info">
                    <div class="agent-item-name">${agent.name}</div>
                    <div class="agent-item-model">${agent.model}</div>
                </div>
                <div class="agent-item-actions">
                    ${agent.id === defaultAgentId ?
                        '<span class="agent-default" title="Default agent"><i class="fas fa-star"></i></span>' :
                        '<button class="agent-action set-default" title="Set as default"><i class="far fa-star"></i></button>'}
                    <button class="agent-action delete" title="Delete agent"><i class="fas fa-trash"></i></button>
                </div>
            `;

            // Add click event to select agent
            agentElement.addEventListener('click', function(e) {
                // Don't select if clicking on action buttons
                if (!e.target.closest('.agent-item-actions')) {
                    selectAgent(agent.id);
                }
            });

            // Add click events for actions
            const setDefaultButton = agentElement.querySelector('.set-default');
            if (setDefaultButton) {
                setDefaultButton.addEventListener('click', function(e) {
                    e.stopPropagation();
                    setDefaultAgent(agent.id);
                });
            }

            const deleteButton = agentElement.querySelector('.delete');
            if (deleteButton) {
                deleteButton.addEventListener('click', function(e) {
                    e.stopPropagation();
                    deleteAgent(agent.id, agent.name);
                });
            }

            agentList.appendChild(agentElement);
        });
    }

    function selectAgent(agentId) {
        // Update current agent
        currentAgentId = agentId;

        // Update UI
        document.querySelectorAll('.agent-item').forEach(item => {
            item.classList.toggle('active', item.dataset.agentId === agentId);
        });

        // Find the agent in the list
        const agent = agents.find(a => a.id === agentId);
        if (agent) {
            currentAgentName.textContent = agent.name;
            agentModel.textContent = agent.model;
            enableChat();

            // Clear chat messages and add welcome message
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.innerHTML = '';
            addSystemMessage(`You are now chatting with ${agent.name}. How can I help you today?`);
        }
    }

    function setDefaultAgent(agentId) {
        fetch('/api/agents/default', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                agent_id: agentId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadAgents(); // Refresh the agent list
            } else {
                console.error('Error setting default agent:', data.error);
                alert(`Error setting default agent: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error setting default agent:', error);
            alert('Error setting default agent. Please try again.');
        });
    }

    function deleteAgent(agentId, agentName) {
        if (confirm(`Are you sure you want to delete the agent "${agentName}"?`)) {
            fetch(`/api/agents/${agentId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // If we deleted the current agent, clear the current agent
                    if (currentAgentId === agentId) {
                        currentAgentId = null;
                        currentAgentName.textContent = 'No Agent Selected';
                        agentModel.textContent = '';
                        disableChat();

                        // Clear chat messages and add message
                        const chatMessages = document.getElementById('chat-messages');
                        chatMessages.innerHTML = '';
                        addSystemMessage('Agent deleted. Please select another agent or create a new one.');
                    }

                    loadAgents(); // Refresh the agent list
                } else {
                    console.error('Error deleting agent:', data.error);
                    alert(`Error deleting agent: ${data.error}`);
                }
            })
            .catch(error => {
                console.error('Error deleting agent:', error);
                alert('Error deleting agent. Please try again.');
            });
        }
    }

    function showAgentModal() {
        agentModal.classList.add('active');
        agentForm.reset();

        // Pre-fill API URL if available from environment
        fetch('/api/config')
            .then(response => response.json())
            .then(data => {
                const apiUrlInput = document.getElementById('api-url');
                if (data.api_url && !apiUrlInput.value) {
                    apiUrlInput.value = data.api_url;
                }
            })
            .catch(error => {
                console.error('Error loading config:', error);
            });
    }

    function hideAgentModal() {
        agentModal.classList.remove('active');
    }

    function createAgent(e) {
        e.preventDefault();

        // Get form data
        const formData = new FormData(agentForm);
        const agentData = {
            name: formData.get('name'),
            description: formData.get('description') || `Agent ${formData.get('name')}`,
            api_url: formData.get('api_url'),
            api_key: formData.get('api_key'),
            model: formData.get('model')
        };

        // Create agent
        fetch('/api/agents', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(agentData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.id) {
                hideAgentModal();
                loadAgents();
                selectAgent(data.id);
            } else {
                console.error('Error creating agent:', data.error);
                alert(`Error creating agent: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error creating agent:', error);
            alert('Error creating agent. Please try again.');
        });
    }

    function enableChat() {
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.placeholder = 'Type your message here...';
    }

    function disableChat() {
        userInput.disabled = true;
        sendButton.disabled = true;
        userInput.placeholder = 'Select an agent to start chatting...';
    }

    function addSystemMessage(message) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = `<p>${message}</p>`;

        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Expose functions to window for use in chat.js
    window.agentManager = {
        getCurrentAgentId: function() {
            return currentAgentId;
        },
        isServiceConnected: function() {
            return serviceConnected;
        },
        refreshAgents: function() {
            loadAgents();
        }
    };
});
