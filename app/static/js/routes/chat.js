/**
 * @description Chat route controller
 */
import { reactive, html } from '../lib.js';

// App chatState
const chatState = reactive({
    chatLoading: false,
    userInput: '',
    chatHistory: [{
        role: 'system',
        content: 'You are a helpful AI assistant. Respond concisely to user input.'
    }],
});

// ============================================================================================
// Chat function
// ============================================================================================
function runChat() {
    // Add user input to chat history
    chatState.chatHistory.push({ content: chatState.userInput, role: 'user' });

    // Clear user input field
    chatState.userInput = '';

    // Send user input to AI
    chatState.chatLoading = true
    fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(chatState.chatHistory),
    }).then(response => response.json()).then(data => {
        // Update chat history with AI response
        chatState.chatHistory.push({ content: data.output, role: 'assistant' });
    }).finally(() => {
        // Update chat loading chatState
        chatState.chatLoading = false;
        // Re-focus on user input (slight delay to ensure focus)
        setTimeout(() => document.getElementById('user-input').focus(), 10);
    });
}

// ============================================================================================
// Watch for CTRL+Enter key press
// ============================================================================================
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        runChat();
    }
});


// ============================================================================================
// Main Chat Template
// ============================================================================================
// Render the app
const template = html`
    <h1 class="display-6 mb-4 pt-5 text-center">AI Chat!</h1>
    <div id="chat-history" class=" shadow-sm border rounded p-3 mb-3" style="height: 300px; overflow-y: auto;">
        <div>
            <!-- Chat history entries -->
            ${() => chatState.chatHistory?.filter(entry => entry.role != 'system')?.map(entry => html`
                <div class="${entry.role === 'user' ? 'text-end' : 'text-start'}">
                    <strong>${entry.role === 'user' ? 'You' : 'AI'}:</strong> ${entry.content}
                </div>
            `)}
        </div>
    </div>
    <div class="input-group">
        <input type="text" id="user-input" disabled="${() => chatState.chatLoading}" class="form-control" 
            placeholder="Type your message... CTRL+Enter to send" 
            value="${() => chatState.userInput}" 
            @keyup="${(e) => {
                // Update user input chatState
                chatState.userInput = e.target.value;
        }}">
        <button class="btn btn-primary" type="submit" disabled="${() => chatState.chatLoading}" @click="${() => runChat()}">Send</button>
    </div>
`;

// ============================================================================================
// Exports
// ============================================================================================
export { chatState, template };