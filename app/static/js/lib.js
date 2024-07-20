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
// Shared States
// ============================================================================================
const routingState = reactive({
    currentRoute: window.location.pathname,
    currentTemplate: null,
});

// ============================================================================================
// Exports
// ============================================================================================
export { 
    // Arrow.js
    reactive, watch, html,

    // Helper functions
    toHtml,

    // States
    routingState,
};
