/**
 * @description Home route controller
 */
import {
    reactive, html,
    toHtml
} from '../lib.js';

// ============================================================================================
// App State
// ============================================================================================
const homeState = reactive({
    maxQueryLength: 100,
    versions: [
        {
            name: 'KJV',
            label: 'King James Version',
            checked: false,
        },
        {
            name: 'ASV',
            label: 'American Standard Version',
            checked: true,
        },
    ],
    getSelectedVersion: () => {
        return this.versions.find(version => version.checked).name;
    },
    query: '',
    // TODO
});


// ============================================================================================
// Chat Style Sheet
// ============================================================================================
const homeStyle = `
    
`;
// Add the home style to the head of the document
document.head.insertAdjacentHTML('beforeend', `<style>${homeStyle}</style>`);


// ============================================================================================
// Main Home Template
// ============================================================================================
const template = html`
    <h1 class="display-6 mb-4 pt-5 text-center">Bible Explorer</h1>
    <!-- TODO: Text area to ask a question about the bible and then radio options below for the differnt bible versions (KJV and ASV) and then toggles to include context. Below that will be the search results -->
    <div class="container">
        <div class="col-md-12">
            <textarea class="form-control" id="question" rows="1" placeholder="Ask a question about the Bible..." maxlength="${homeState.maxQueryLength}" value="${() => homeState.query}" @keyup="${(e) => {
                let newQuery = e.target.value
                if (newQuery.length > homeState.maxQueryLength) {
                    newQuery = newQuery.slice(0, homeState.maxQueryLength)
                }
                homeState.query = newQuery
            }}"></textarea>
            <div class="form-text text-end text-light">${() => homeState.query.length}/${homeState.maxQueryLength}</div>
        </div>
        <div class="d-flex justify-content-center mt-2">
            ${() => homeState.versions.map(version => html`
                <div class="p-3 border rounded shadow-sm bg_light me-3" @click="${() => {
                    homeState.versions.forEach(v => v.checked = false);
                    version.checked = true;
                }}">
                    <i class="${() => version.checked ? 'bi bi-journal-bookmark-fill' : 'bi bi-journal-bookmark'}"></i>
                    <span class="ms-2">${version.label}</span>
                </div>
            `)}
         
            <div class="p-3 border rounded shadow-sm bg_light">
                <div class="form-check-reverse">
                    <input class="form-check-input" type="checkbox" id="context">
                    <label class="form-check-label me-2" for="context">
                        Include Context
                    </label>
                </div>
            </div>
        </div>
        <div class="d-flex justify-content-center mt-4">
            <button type="button" class="btn btn-primary w-75">Search</button>
        </div>
    </div>
`;

// ============================================================================================
// Exports
// ============================================================================================
export { homeState, template };