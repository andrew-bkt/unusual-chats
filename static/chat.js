document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const typingIndicator = document.getElementById('typing-indicator');
    const clearChatButton = document.getElementById('clear-chat');
    const goToToolsButton = document.getElementById('go-to-tools');
    const apiResponseContainer = document.getElementById('api-response');

    function addMessage(content, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(isUser ? 'user-message' : 'assistant-message');
        messageElement.innerHTML = `<strong>${isUser ? 'You' : 'Assistant'}:</strong> ${formatMessage(content)}`;
        chatMessages.appendChild(messageElement);
        
        // Animate scroll
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }

    function formatMessage(content) {
        // Handle code blocks
        content = content.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Handle inline code
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Handle line breaks
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }

    function showTypingIndicator() {
        typingIndicator.style.display = 'block';
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }

    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }

    function displayApiResponse(response) {
        if (response.type === 'large_response') {
            apiResponseContainer.innerHTML = `
                <p>${response.summary}</p>
                <button onclick="fetchFullResponse('${response.id}')">Load Full Response</button>
            `;
        } else {
            apiResponseContainer.innerHTML = `<pre>${JSON.stringify(response, null, 2)}</pre>`;
        }
    }

    window.fetchFullResponse = async function(responseId) {
        try {
            const response = await fetch(`/api/response/${responseId}`);
            const data = await response.json();
            apiResponseContainer.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        } catch (error) {
            console.error('Error fetching full response:', error);
            apiResponseContainer.innerHTML += '<p>Error loading full response</p>';
        }
    }

    async function sendMessage(message) {
        addMessage(message, true);
        showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'message': message
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                const decodedChunk = decoder.decode(value, { stream: true });
                const lines = decodedChunk.split('\n');
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const content = line.slice(6);
                        try {
                            const parsedContent = JSON.parse(content);
                            switch(parsedContent.type) {
                                case 'assistant_message':
                                    addMessage(parsedContent.content);
                                    break;
                                case 'tool_output':
                                    displayApiResponse(parsedContent.output);
                                    break;
                                case 'error':
                                    addMessage(`Error: ${parsedContent.content}`);
                                    break;
                                default:
                                    console.warn('Unknown message type:', parsedContent.type);
                            }
                        } catch (error) {
                            console.error('Error parsing server message:', error);
                            addMessage(content);
                        }
                    }
                }
            }

            hideTypingIndicator();
        } catch (error) {
            console.error('Error sending message:', error);
            hideTypingIndicator();
            addMessage('An error occurred while processing your message.');
        }
    }

    messageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (message) {
            messageInput.value = '';
            await sendMessage(message);
        }
    });

    clearChatButton.addEventListener('click', () => {
        chatMessages.innerHTML = '';
        apiResponseContainer.innerHTML = '';
    });

    goToToolsButton.addEventListener('click', () => {
        window.location.href = '/tools';
    });

    // Focus on input when page loads
    messageInput.focus();
});