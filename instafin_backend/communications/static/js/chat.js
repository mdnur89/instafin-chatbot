class ChatManager {
    constructor() {
        this.messageContainer = document.getElementById('chat-messages');
        this.chatForm = document.getElementById('chat-form');
        this.setupWebSocket();
        this.setupEventListeners();
        this.setupFileUpload();
    }

    setupWebSocket() {
        // Get chat session ID from URL
        const pathParts = window.location.pathname.split('/');
        const sessionId = pathParts[pathParts.length - 2];

        // Create WebSocket connection
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.socket = new WebSocket(
            `${wsProtocol}//${window.location.host}/ws/chat/${sessionId}/`
        );

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.socket.onclose = () => {
            console.log('WebSocket connection closed');
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.setupWebSocket(), 5000);
        };
    }

    setupEventListeners() {
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Auto-scroll to bottom when new messages arrive
        const observer = new MutationObserver(() => {
            this.scrollToBottom();
        });
        observer.observe(this.messageContainer, { childList: true });
    }

    setupFileUpload() {
        const fileInput = document.querySelector('input[type="file"]');
        const fileNameDisplay = document.getElementById('file-name');

        fileInput.addEventListener('change', (e) => {
            const fileName = e.target.files[0]?.name;
            fileNameDisplay.textContent = fileName || '';
        });
    }

    handleMessage(data) {
        if (data.type === 'chat_message') {
            this.appendMessage(data.message);
        } else if (data.type === 'typing') {
            this.handleTypingIndicator(data);
        }
    }

    appendMessage(message) {
        const isCurrentUser = message.sender_id === currentUserId; // currentUserId should be set in template
        const messageHtml = `
            <div class="mb-4 ${isCurrentUser ? 'ml-auto' : ''} max-w-[70%]">
                <div class="flex items-start ${isCurrentUser ? 'flex-row-reverse' : ''}">
                    <div class="${isCurrentUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'} rounded-lg px-4 py-2">
                        ${this.escapeHtml(message.content)}
                        ${message.attachment ? `
                            <div class="mt-2">
                                <a href="${message.attachment}" class="text-sm underline" target="_blank">
                                    View Attachment
                                </a>
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="mt-1 text-xs text-gray-500 ${isCurrentUser ? 'text-right' : ''}">
                    ${new Date(message.timestamp).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}
                </div>
            </div>
        `;
        this.messageContainer.insertAdjacentHTML('beforeend', messageHtml);
        this.scrollToBottom();
    }

    async sendMessage() {
        const form = this.chatForm;
        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            if (response.ok) {
                const data = await response.json();
                form.reset();
                document.getElementById('file-name').textContent = '';
                
                // Send message through WebSocket for real-time updates
                this.socket.send(JSON.stringify({
                    type: 'chat_message',
                    message: data.message
                }));
            } else {
                console.error('Failed to send message');
            }
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }

    scrollToBottom() {
        this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize chat manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatManager();
}); 