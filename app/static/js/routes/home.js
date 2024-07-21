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
    // Bible Versions
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

    // Options
    options: [
        {
            name: 'context',
            label: 'Include Context',
            help: 'Include the surrounding context of the verse in the search results.',
            iconOn: 'bi bi-check-circle-fill',
            iconOff: 'bi bi-check-circle',
            checked: false,
        },
    ],

    // Input Query
    maxQueryLength: 100,
    query: '',

    // Search Results
    searchResults: [],
});


// ============================================================================================
// Chat Style Sheet
// ============================================================================================
const homeStyle = `
    .hero {
        background-color: hsl(200 20% 58% / 1);
    }

    .option-btn {
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1.5rem;
    }
    .option-btn:hover {
        background-color: hsl(205 87% 92% / 1);
    }
    .option-btn:active {
        background-color: hsl(205 87% 89% / 1);
    }
    .option-btn .bi {
        font-size: 1.25rem;
    }
`;
// Add the home style to the head of the document
document.head.insertAdjacentHTML('beforeend', `<style>${homeStyle}</style>`);


// ============================================================================================
// Main Home Template
// ============================================================================================
const template = html`
    <div class="py-4"></div>
    <div class="hero p-5 text-center rounded-3">
        <img class="bi mt-4 mb-3 rounded" src="./img/icons/bible-explorer-256.png" alt="Bible Explorer Icon" width="72" height="72">
        <h1 class="text-body-emphasis">Bible Explorer</h1>
        <p class="mx-auto fs-5 text-muted">Search the Bible with ease!</p>
    </div>
    <!-- TODO: Text area to ask a question about the bible and then radio options below for the differnt bible versions (KJV and ASV) and then toggles to include context. Below that will be the search results -->
    <div class="container mt-5">
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
        <div class="d-flex justify-content-center">
            ${() => homeState.versions.map(version => html`
                <div class="rounded shadow-sm bg_light me-3 option-btn mt-2" @click="${() => {
                    homeState.versions.forEach(v => v.checked = false);
                    version.checked = true;
                }}">
                    <i class="${() => version.checked ? 'bi bi-journal-bookmark-fill' : 'bi bi-journal-bookmark'}"></i>
                    <span class="ms-2">${version.label}</span>
                </div>
            `)}
            ${() => homeState.options.map(option => html`
                <div class="rounded shadow-sm bg_light me-3 option-btn mt-2" @click="${() => option.checked = !option.checked}">
                    <i class="${() => option.checked ? option.iconOn : option.iconOff}"></i>
                    <span class="ms-2">${option.label}</span>
                </div>
            `)}
        </div>
        <div class="d-flex justify-content-center mt-3">
            <button type="button" class="btn btn-primary w-75">Search</button>
        </div>
    </div>
`;

// ============================================================================================
// Exports
// ============================================================================================
export { homeState, template };