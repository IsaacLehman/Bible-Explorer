/**
 * @description Navigation bar controller
 */
import {
    reactive, html,
    routingState,
} from '../lib.js';

// ============================================================================================
// Nav Style Sheet
// ============================================================================================
const chatStyle = `
    nav .route-icon {
        font-size: 0.95rem;
    }
`;
// Add the chat style to the head of the document
document.head.insertAdjacentHTML('beforeend', `<style>${chatStyle}</style>`);

// ============================================================================================
// Helper Functions
// ============================================================================================
function generateRouteLink(route) {
    return html`
        <li class="nav-item">
            <a class="${() => `nav-link ${routingState.currentRoute === route.url ? 'active' : ''}`}"
                href="${route.url}"
                active="${() => routingState.currentRoute === route.url}"
                title="${route.label}"
            >
                <i class="${route.icon} me-1 route-icon"></i> ${route.label}
            </a>
        </li>
    `;
}

// ============================================================================================
// Nav Bar Template
// ============================================================================================
const template = html`
    <nav class="navbar sticky-top navbar-expand-lg border-bottom border-body bg_light shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="./img/icons/bible-explorer-256.png" alt="Bible Explorer Icon" width="30" height="30" class="rounded me-3"> 
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    ${() => routingState.routes.map(route => generateRouteLink(route))}
                </ul>
            </div>
        </div>
    </nav>
`;

// ============================================================================================
// Exports
// ============================================================================================
export {
    template,
};