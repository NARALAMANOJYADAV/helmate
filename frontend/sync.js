/**
 * HELMET AI - Sync Engine
 * Simplified to use the current browser port for all requests.
 */

function getApiUrl(endpoint) {
    if (!endpoint) return '';
    if (endpoint.startsWith('http')) return endpoint;

    return endpoint.startsWith('/') ? endpoint : '/' + endpoint;
}

/**
 * Syncs the page links and forms to ensure they use proper absolute paths.
 */
function syncLinks() {
    console.log("[Sync] Initializing relative path sync...");

    // 1. Sync ALL Form Actions
    document.querySelectorAll('form').forEach(form => {
        const action = form.getAttribute('action');
        if (action && !action.startsWith('http')) {
            form.action = getApiUrl(action);
        }
    });

    // 2. Sync ALL Internal Links
    document.querySelectorAll('a').forEach(link => {
        const href = link.getAttribute('href');
        if (href && !href.startsWith('http') && !href.startsWith('#') && !href.startsWith('javascript:')) {
            link.href = getApiUrl(href);
        }
    });

    // 3. Sync Specific Camera Streams / Images
    const stream = document.getElementById('processedFrame') || document.getElementById('cameraStream');
    if (stream && !stream.src.includes('data:')) {
        const currentSrc = stream.getAttribute('src');
        if (currentSrc && !currentSrc.startsWith('http')) {
            stream.src = getApiUrl(currentSrc);
        }
    }
}

// Global exposure for other scripts (app.js)
window.getApiUrl = getApiUrl;

// Auto-run on load
document.addEventListener('DOMContentLoaded', syncLinks);
