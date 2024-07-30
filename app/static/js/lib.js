import { reactive, watch, html } from 'https://esm.sh/@arrow-js/core';

// ============================================================================================
// Master library for generic helper functions
// ============================================================================================
let showDownConverter;
function toHtml(markdown) {
    if (!showDownConverter) {
        showDownConverter = new showdown.Converter();
        showDownConverter.setOption('simplifiedAutoLink', 'true');
        showDownConverter.setOption('excludeTrailingPunctuationFromURLs', 'true');
        showDownConverter.setOption('strikethrough', 'true');
        showDownConverter.setOption('tables', 'true');
        showDownConverter.setOption('tasklists', 'true');
        showDownConverter.setOption('smoothLivePreview', 'true');
    }
    return showDownConverter.makeHtml(markdown);
}

// ============================================================================================
// Shared Bible Functions
// ============================================================================================
async function searchBible(version, query, limit = 10, context = { add: true, size: 2 }) {
    const urlParams = new URLSearchParams({
        bible_version: version,
        search_text: query,
        max_results: limit,
        add_context: context.add ? 'true' : 'false',
        context_size: context.size,
    });
    const response = await fetch(`/api/bible/search?${urlParams.toString()}`);

    if (!response.ok) {
        return [];
    }

    const bibleResults = await response.json(); // {notes: [], verses: []}

    // Add ranking to the results
    bibleResults.verses = bibleResults.verses.map((verse, index) => {
        if (verse.similarity >= 0.8) {
            verse.rank = {
                name: 'very-high',
                label: 'Very High',
                color: 'bg-danger',
            };
        } else if (verse.similarity > 0.7) {
            verse.rank = {
                name: 'high',
                label: 'High',
                color: 'bg-warning',
            };
        } else if (verse.similarity > 0.6 && verse.relative_similarity > 0.5) {
            verse.rank = {
                name: 'medium',
                label: 'Medium',
                color: 'bg-info',
            };
        } else {
            verse.rank = {
                name: 'low',
                label: 'Low',
                color: 'bg-light',
            };
        }
        return verse;
    });

    return bibleResults;
}

// ============================================================================================
// Shared AI Functions
// ============================================================================================
async function runAIChat(systemPrompt, chatHistory, model='gpt-4o-mini') {
    const _chatHistory = [{role: 'system', content: systemPrompt}, ...chatHistory];
    const response = await fetch('/api/ai/chat?model=' + model, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(_chatHistory),
    });

    if (!response.ok) {
        return { output: 'Failed to communicate with AI.' };
    }

    return response.json();
}

// ============================================================================================
// Shared States
// ============================================================================================
const routingState = reactive({
    currentRoute: window.location.pathname,
    currentTemplate: null,
    // Route Registration | Ensure there is a {name}.js file in the routes folder
    routes: [
        {
            url: '/',
            name: 'home',
            label: 'Home',
            icon: 'bi bi-house-door',
        },
        {
            url: '/chat',
            name: 'chat',
            label: 'Chat',
            icon: 'bi bi-chat-left-text',
        },
    ]
});

const alertingState = reactive({
    alertMessage: '',
    alertType: 'success',
    alertIcon: 'bi bi-info-circle',
    alertVisible: false,
    setAlert: (message, type, icon) => {
        alertingState.alertMessage = message;
        alertingState.alertType = type;
        alertingState.alertIcon = icon || 'bi bi-info-circle';
        alertingState.alertVisible = true;
    },
    hideAlert: () => {
        alertingState.alertVisible = false;
    },
});

// ============================================================================================
// Exports
// ============================================================================================
export { 
    // Arrow.js
    reactive, watch, html,

    // Helper functions
    toHtml,
    searchBible,
    runAIChat,

    // States
    routingState,
    alertingState,
};
