/**
 * @description Main app controller
 * - Handles dynamically loading in the correct part of the website based on the currently viewed route
 */
import { 
    reactive, html,
    routingState, alertingState,
} from './lib.js';
import * as navLib from './partials/nav.js';


// ============================================================================================
// Routing
// ============================================================================================
// Set up the DOM entry point and template cache
const domEntryPoint = document.getElementById('app');
const domTemplateMapCache = new Map();

// Helper function for loading in a route and managing the cache
async function loadRouteTemplate(route) {
    if (!domTemplateMapCache.has(route)) {
        try {
            const routeTemplate = (await import(`./routes/${route}.js`)).template;
            domTemplateMapCache.set(route, routeTemplate);
        } catch (error) {
            console.error(`Failed to load route: ${route}`, error);
            return html`<h1>404 Not Found</h1>`;
        }
    }
    return domTemplateMapCache.get(route);
}

// Main route loader function
async function updateRouteTemplate() {
    // Get the route name from the current route
    let fileName = routingState.routes.find(route => route.url === routingState.currentRoute)?.name;
    if (!fileName) {
        // fileName = '404'; // TODO: Add a 404 route vs. the hard-coded template below
        routingState.currentTemplate = html`<h1>404 Not Found</h1>`;routingState.currentTemplate;
        return;
    }

    // Load the route template
    routingState.currentTemplate = await loadRouteTemplate(fileName);
}

// Run initial route update and watch for changes
updateRouteTemplate();
routingState.$on('currentRoute', updateRouteTemplate);


// ============================================================================================
// Watch for route changes
// ============================================================================================
// Handles route changes when clicking on links
window.addEventListener('click', (e) => {
    e.preventDefault();

    let targetElement = e.target;

    // Traverse up the DOM tree to find the closest anchor tag
    while (targetElement && targetElement.tagName !== 'A') {
        targetElement = targetElement.parentElement;
    }

    if (targetElement && targetElement.href.startsWith(window.location.origin)) {
        const href = targetElement.getAttribute('href');
        console.log('Route change requested:', href);
        window.history.pushState({}, '', href);
        routingState.currentRoute = href;
    } else {
        console.log('No route change requested');
    }
});

// Handles route changes when using the back/forward buttons
window.addEventListener('popstate', () => {
    routingState.currentRoute = window.location.pathname;
});


// ============================================================================================
// Main App Template (i.e. top-level layout)
// ============================================================================================
html`
    ${navLib.template}
    ${() => alertingState.alertVisible ? html`
        <div class="alert alert-${alertingState.alertType} alert-dismissible fade show rounded-0 py-1" role="alert">
            <div class="container position-relative">
                <i class="${alertingState.alertIcon} me-2"></i>
                ${alertingState.alertMessage}
                <span class="position-absolute top-0 end-0" style="cursor: pointer;" @click="${() => alertingState.alertVisible = false}">
                    <i class="bi bi-x-lg"></i>
                </span>
            </div>
        </div>
    ` : ''}
    <main class="container">
        ${() => routingState.currentTemplate}
    </main>
    <!-- TODO: Add a footer -->
`(domEntryPoint);