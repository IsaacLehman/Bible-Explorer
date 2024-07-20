import { reactive, html } from './lib.js';

// ============================================================================================
// Main App.js File
// ============================================================================================

// App State
const state = reactive({
    chatLoading: false,
    userInput: '',
    chatHistory: [{
        role: 'system',
        content: 'You are a helpful AI assistant. Respond concisely to user input.'
    }],
});

// Render the app
html`
    <h1 class="display-6 mb-4 text-center">AI Chat!</h1>
    <div id="chat-history" class="border rounded p-3 mb-3" style="height: 300px; overflow-y: auto;">
        <div>
            <!-- Chat history entries -->
            ${() => state.chatHistory.map(entry => html`
                <div class="${entry.role === 'user' ? 'text-end' : 'text-start'}">
                    <strong>${entry.role === 'user' ? 'You' : 'AI'}:</strong> ${entry.content}
                </div>
            `)}
        </div>
    </div>
    <div class="input-group">
        <input type="text" id="user-input" disabled="${() => state.chatLoading}" class="form-control" placeholder="Type your message..." value="${() => state.userInput}" @change="${(e) => {
            // Update user input state
            state.userInput = e.target.value;
        }}">
        <button class="btn btn-primary" type="submit" disabled="${() => state.chatLoading}" @click="${() => {
            // Add user input to chat history
            state.chatHistory.push({ content: state.userInput, role: 'user' });

            // Clear user input field
            state.userInput = '';

            // Send user input to AI
            state.chatLoading = true
            fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(state.chatHistory),
            }).then(response => response.json()).then(data => {
                // Update chat history with AI response
                state.chatHistory.push({ content: data.output, role: 'assistant' });
            }).finally(() => {
                // Update chat loading state
                state.chatLoading = false;
            });
        }}">Send</button>
    </div>
`(document.getElementById('app'));
