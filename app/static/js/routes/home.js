/**
 * @description Home route controller
 */
import {
    reactive, html,
    toHtml, searchBible, runAIChat,
    alertingState,
} from '../lib.js';

// ============================================================================================
// App State
// ============================================================================================
const homeState = reactive({
    // Bible Versions
    versions: [
        {
            name: 'kjv',
            abbreviation: 'KJV',
            label: 'King James Version',
            checked: false,
        },
        {
            name: 'asv',
            abbreviation: 'ASV',
            label: 'American Standard Version',
            checked: true,
        },
    ],
    getSelectedVersion: () => {
        return homeState.versions.find(version => version.checked).name;
    },

    // Options
    options: [
        {
            name: 'context',
            label: 'Include Context',
            help: 'Include the surrounding context of the verse in the search results.',
            iconOn: 'bi bi-check-circle-fill',
            iconOff: 'bi bi-check-circle',
            checked: true,
        },
    ],

    // Input Query
    maxQueryLength: 100,
    query: '',

    // Search Results
    loading: false,
    searchResults: [],
    searchStats: [],
    aiResponse: null,

    // Formatters
    getSearchResultsContext: () => {
        return homeState.searchResults.filter(v => v.rank.name !== 'very-low').map(result => {
            return {
                reference: `${result.book_name} ${result.chapter}:${result.verse}`,
                text: result.text,
                context: result.context,
                match: result.rank.label,
            };
        });
    },
});
window.homeState = homeState; // For debugging


// ============================================================================================
// Home Style Sheet
// ============================================================================================
const homeStyle = `
    .bible-search-response-container {
        padding: 2rem !important;
    }
`;
// Add the home style to the head of the document
document.head.insertAdjacentHTML('beforeend', `<style>${homeStyle}</style>`);


// ============================================================================================
// Search Function
// ============================================================================================
async function runBibleSearch() {
    // Validate user input
    if (homeState.query.trim().length === 0) {
        alertingState.setAlert('Please enter a question before searching.', 'danger');
        return;
    };

    // Clear previous search results
    homeState.searchResults = [];
    homeState.searchStats = [];
    homeState.aiResponse = null;

    // Show loading spinner and alert
    alertingState.hideAlert();
    homeState.loading = true;

    // Prepare search parameters
    const version = homeState.getSelectedVersion();
    const context = true; // homeState.options.find(option => option.name === 'context').checked; - REASON: always true so people can click on context even when they didn't ask for it and have it show
    const contextSize = 2;
    const limit = 10;

    // Send search query to the server
    const data = await searchBible(version, homeState.query, limit, { add: context, size: contextSize });

    // Update search results
    homeState.searchResults = data.verses;
    homeState.searchStats = data.notes;

    // Set AI Summary to loading state
    homeState.aiResponse = { output: 'Loading summary...' };
    // Get an AI summary of the responses
    homeState.aiResponse = await runAIChat(
            `You are a Bible explorer assistant. The user will ask a question and we will provide a variety of Bible verses that may answer the question.\n` +
            `Your task is to summarize the verses and provide a concise response to the user's question.\n` +
            `Do your best to provide a helpful and accurate response to the users query based on the provided Bible verses. Try to keep the response pointed and short - do not add any commentary or personal opinion. If you are unsure of the answer, you can say that you are unsure.\n` +
            `Return your response in markdown format.`,
            [{role: 'user', content: `User query: "${homeState.query}"\n\nBible version selected: ${version}\nVerses found (may or may not be relevent): ${JSON.stringify(homeState.getSearchResultsContext())}`}],
            'gpt-4o-mini'
    );
    // Hide the alert
    homeState.loading = false;
}


// ============================================================================================
// Main Home Template
// ============================================================================================
const template = html`
    <div class="py-4"></div>
    <div class="hero p-5 text-center rounded-3 bg_light shadow-sm">
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
            <div class="form-text text-end">${() => homeState.query.length}/${homeState.maxQueryLength}</div>
        </div>
        <div class="d-flex justify-content-center mobile-flex-column">
            ${() => homeState.versions.map(version => html`
                <div class="rounded shadow-sm border_light me-3 option-btn mt-2 mobile-flex-item" @click="${() => {
                    homeState.versions.forEach(v => v.checked = false);
                    version.checked = true;
                }}">
                    <i class="${() => version.checked ? 'bi bi-journal-bookmark-fill' : 'bi bi-journal-bookmark'}"></i>
                    <span class="ms-2">${version.label}</span>
                </div>
            `)}
            ${() => homeState.options.map(option => html`
                <div class="rounded shadow-sm border_light me-3 option-btn mt-2 mobile-flex-item" @click="${() => option.checked = !option.checked}">
                    <i class="${() => option.checked ? option.iconOn : option.iconOff}"></i>
                    <span class="ms-2">${option.label}</span>
                </div>
            `)}
        </div>
        <div class="d-flex justify-content-center mt-3">
            <button type="button" class="btn btn-primary w-75" @click="${() => runBibleSearch()}" disabled="${() => homeState.loading}">
                <i class="bi bi-search me-3"></i> Explore the Bible
                ${() => homeState.loading ? html`... <div class="spinner-border spinner-border-sm text-light ms-1" role="status"></div>` : ''}
            </button>
        </div>
    </div>
    <div class="container mt-4">
        ${() => homeState.aiResponse ? html`
            <div class="card p-3 my-4 border-primary">
                <h5 class="card-title text-muted">Summary</h5>
                <div class="card-text">${toHtml(homeState.aiResponse.output)}</div>
            </div>
        ` : ''}
        <div class="row">
            ${() => homeState.searchResults.filter(v => v.rank.name !== 'very-low').map(result => html`
                <div class="col-md-12">
                    <div class="card p-3 mb-3 position-relative bible-search-response-container">
                        <div class="position-absolute top-0 end-0 text-dark rounded-pill px-3 py-1 mt-1 me-1 ${result.rank.color}">
                            ${result.rank.label}
                        </div>
                        <h5 class="card-title">${result.book_name} ${result.chapter}:${result.verse}</h5>
                        <p class="card-text">${result.text}</p>
                        ${() => homeState.options.find(option => option.name === 'context').checked && result.context?.length > 0 ? html`
                            <hr>
                            <div class="card-text text-muted">
                                <small>Context:</small>
                                <p>
                                ${() => result.context.map((context, index) => {
                                    const verseNumber = result.verse - Math.ceil(result.context.length/2) + (index+1);
                                    if (verseNumber === result.verse) {
                                        return html`<b>${verseNumber}.</b> <b>${context}</b> `;
                                    }
                                    return html`<b>${verseNumber}.</b> <i>${context}</i> `;
                                })}
                            </div>
                        ` : ''}
                    </div>
                </div>
            `)}
        </div>
    </div>
`;

// ============================================================================================
// Exports
// ============================================================================================
export { homeState, template };




/*
Example API response:

{
  "verses": [
    {
      "book_name": "1 John",
      "book_number": 62,
      "chapter": 5,
      "verse": 3,
      "text": "For this is the love of God, that we keep his commandments: and his commandments are not grievous.",
      "similarity": 0.47308325696027076,
      "relative_similarity": 1,
      "context": [
        "¶ Whosoever believeth that Jesus is the Christ is born of God: and every one that loveth him that begat loveth him also that is begotten of him.",
        "By this we know that we love the children of God, when we love God, and keep his commandments.",
        "For this is the love of God, that we keep his commandments: and his commandments are not grievous.",
        "For whatsoever is born of God overcometh the world: and this is the victory that overcometh the world, [even] our faith.",
        "Who is he that overcometh the world, but he that believeth that Jesus is the Son of God?"
      ]
    },
    {
      "book_name": "1 John",
      "book_number": 62,
      "chapter": 4,
      "verse": 8,
      "text": "He that loveth not knoweth not God; for God is love.",
      "similarity": 0.46526552632835183,
      "relative_similarity": 0.44053027377141474,
      "context": [
        "We are of God: he that knoweth God heareth us; he that is not of God heareth not us. Hereby know we the spirit of truth, and the spirit of error.",
        "¶ Beloved, let us love one another: for love is of God; and every one that loveth is born of God, and knoweth God.",
        "He that loveth not knoweth not God; for God is love.",
        "In this was manifested the love of God toward us, because that God sent his only begotten Son into the world, that we might live through him.",
        "Herein is love, not that we loved God, but that he loved us, and sent his Son [to be] the propitiation for our sins."
      ]
    },
    {
      "book_name": "1 John",
      "book_number": 62,
      "chapter": 4,
      "verse": 16,
      "text": "And we have known and believed the love that God hath to us. God is love; and he that dwelleth in love dwelleth in God, and God in him.",
      "similarity": 0.46442770593152993,
      "relative_similarity": 0.3805723179261624,
      "context": [
        "¶ And we have seen and do testify that the Father sent the Son [to be] the Saviour of the world.",
        "Whosoever shall confess that Jesus is the Son of God, God dwelleth in him, and he in God.",
        "And we have known and believed the love that God hath to us. God is love; and he that dwelleth in love dwelleth in God, and God in him.",
        "¶ Herein is our love made perfect, that we may have boldness in the day of judgment: because as he is, so are we in this world.",
        "There is no fear in love; but perfect love casteth out fear: because fear hath torment. He that feareth is not made perfect in love."
      ]
    },
    {
      "book_name": "1 John",
      "book_number": 62,
      "chapter": 4,
      "verse": 7,
      "text": "¶ Beloved, let us love one another: for love is of God; and every one that loveth is born of God, and knoweth God.",
      "similarity": 0.461849966454552,
      "relative_similarity": 0.19609842551737985,
      "context": [
        "They are of the world: therefore speak they of the world, and the world heareth them.",
        "We are of God: he that knoweth God heareth us; he that is not of God heareth not us. Hereby know we the spirit of truth, and the spirit of error.",
        "¶ Beloved, let us love one another: for love is of God; and every one that loveth is born of God, and knoweth God.",
        "He that loveth not knoweth not God; for God is love.",
        "In this was manifested the love of God toward us, because that God sent his only begotten Son into the world, that we might live through him."
      ]
    },
    {
      "book_name": "Deuteronomy",
      "book_number": 5,
      "chapter": 6,
      "verse": 5,
      "text": "And thou shalt love the LORD thy God with all thine heart, and with all thy soul, and with all thy might.",
      "similarity": 0.4591097919711664,
      "relative_similarity": 0,
      "context": [
        "Hear therefore, O Israel, and observe to do [it]; that it may be well with thee, and that ye may increase mightily, as the LORD God of thy fathers hath promised thee, in the land that floweth with milk and honey.",
        "¶ Hear, O Israel: The LORD our God [is] one LORD:",
        "And thou shalt love the LORD thy God with all thine heart, and with all thy soul, and with all thy might.",
        "And these words, which I command thee this day, shall be in thine heart:",
        "And thou shalt teach them diligently unto thy children, and shalt talk of them when thou sittest in thine house, and when thou walkest by the way, and when thou liest down, and when thou risest up."
      ]
    }
  ],
  "notes": [
    {
      "note": "Loaded Bible version: kjv",
      "elapsed_time": 0
    },
    {
      "note": "Got search text embeddings",
      "elapsed_time": 0.4206371307373047
    },
    {
      "note": "Calculated cosine distances",
      "elapsed_time": 0.7713606357574463
    },
    {
      "note": "Sorted verses by similarity",
      "elapsed_time": 0.8027772903442383
    },
    {
      "note": "Added relative similarity scores",
      "elapsed_time": 0.8027772903442383
    },
    {
      "note": "Added context to verses",
      "elapsed_time": 0.872384786605835
    }
  ]
}
*/