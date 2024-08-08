/**
 * @description Chat route controller
 */
import { 
    reactive, html,
    toHtml, runAIChat,
    alertingState,
} from '../lib.js';

// ============================================================================================
// App State
// ============================================================================================
const chatState = reactive({
    chatLoading: false,
    userInput: '',
    systemPrompt: 'You are a helpful AI assistant. Respond concisely to user input in Markdown format.',
    chatHistory: [],
});

// ============================================================================================
// Chat Style Sheet
// ============================================================================================
const chatStyle = `
    #chat-history table {
        width: 100%;
        border-collapse: collapse;
    }
    #chat-history td {
        padding: 10px;
        border: 1px solid #ddd;
    }
    #chat-history tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    #chat-history tr:hover {
        background-color: #f1f1f1;
    }

    .chat-box > p:last-child {
        margin-bottom: 0;
    }
        
    .chat-box {
        width: auto;
        max-width: 80%;
        min-width: 20%;
    }
    
    .user-chat {
        background-color: white;
        margin-left: auto;
    }

    .assistant-chat {
        background-color:  var(--light-bg);
        margin-right: auto;
    }
`;
// Add the chat style to the head of the document
document.head.insertAdjacentHTML('beforeend', `<style>${chatStyle}</style>`);

// ============================================================================================
// Chat function
// ============================================================================================
function runChat() {
    // Validate user input
    if (chatState.userInput.trim().length === 0) {
        alertingState.setAlert('Please enter a message before sending.', 'danger');
        return;
    };

    // Add user input to chat history
    chatState.chatHistory.push({ content: chatState.userInput, role: 'user' });

    setTimeout(() => {
        // Scroll to the bottom of the chat history
        document.getElementById('chat-history').scrollTop = document.getElementById('chat-history').scrollHeight;
    }, 10);

    // Clear user input field
    chatState.userInput = '';

    // Send user input to AI
    chatState.chatLoading = true;
    runAIChat(chatState.systemPrompt, chatState.chatHistory, 'llama-3.1-70b-versatile').then(data => {
        // Update chat history with AI response
        chatState.chatHistory.push({ content: data.output, role: 'assistant' });
    }).finally(() => {
        // Update chat loading chatState
        chatState.chatLoading = false;
        setTimeout(() => {
            // Re-focus on user input (slight delay to ensure focus)
            document.getElementById('user-input').focus()
            // Scroll to the bottom of the chat history
            document.getElementById('chat-history').scrollTop = document.getElementById('chat-history').scrollHeight;
        }, 10);
    });
}

// ============================================================================================
// Watch for CTRL+Enter key press
// ============================================================================================
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey && window.location.pathname === '/chat') {
        runChat();
    }
});

// ============================================================================================
// Main Chat Template
// ============================================================================================
const template = html`
    <h1 class="display-6 my-3 text-center">AI Chat!</h1>
    <div id="chat-history" class="border rounded p-3 mb-3" style="height: 500px; overflow-y: auto;">
        <div class="d-flex flex-column gap-2">
            <!-- Chat history entries -->
            ${() => chatState.chatHistory?.filter(entry => entry.role != 'system')?.map(entry => html`
                <div class="${`chat-box ${entry.role}-chat rounded shadow-sm p-2`}">
                    <small><strong>${entry.role === 'user' ? '<i class="bi bi-person me-2"></i> You' : '<i class="bi bi-cpu me-2"></i> AI'}</strong></small>
                    <hr class="my-1">
                    ${toHtml(entry.content)}
                </div>
            `)}
        </div>
    </div>
    <div class="input-group">
        <textarea type="text" id="user-input" disabled="${() => chatState.chatLoading}" class="form-control"
            rows="1"
            placeholder="Type your message... CTRL+Enter to send" 
            value="${() => chatState.userInput}" 
            @keyup="${(e) => {
                // Update user input chatState
                chatState.userInput = e.target.value;
        }}"></textarea>
        <button class="btn btn-primary" type="submit" disabled="${() => chatState.chatLoading}" @click="${() => runChat()}">Send</button>
    </div>
`;

// ============================================================================================
// Exports
// ============================================================================================
export { chatState, template };