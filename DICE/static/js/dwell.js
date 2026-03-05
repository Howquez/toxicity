let dwell_threshold = js_vars.dwell_threshold / 100 || 0.5

// Array to store row visibility duration data (preserves full temporal sequence)
var rowVisibilityData = [];

// Start timestamps for currently visible rows: {doc_id: Date.now()}
var visibleRows = {};

// Tracks which rows are currently intersecting (independent of pause state)
var currentlyIntersecting = {};

var isPageVisible = true;

function handleRowVisibility(entries, observer) {
    if (!isPageVisible) return;

    const currentTime = Date.now();
    entries.forEach((entry) => {
        const row = entry.target;
        const index = parseInt(row.id);
        if (isNaN(index)) return;

        if (entry.isIntersecting) {
            currentlyIntersecting[index] = true;
            if (!visibleRows[index]) {
                visibleRows[index] = currentTime;
            }
        } else {
            delete currentlyIntersecting[index];
            if (visibleRows[index]) {
                const duration = (currentTime - visibleRows[index]) / 1000;
                rowVisibilityData.push({ doc_id: index, duration: Number(duration.toFixed(3)) });
                delete visibleRows[index];
            }
        }
    });

    updateViewportData();
}

// Finalize dwell times for all currently visible rows
function updateVisibleRowsDwellTime() {
    const currentTime = Date.now();
    Object.keys(visibleRows).forEach((index) => {
        const duration = (currentTime - visibleRows[index]) / 1000;
        rowVisibilityData.push({ doc_id: parseInt(index), duration: Number(duration.toFixed(3)) });
        delete visibleRows[index];
    });
    updateViewportData();
}

// Append duration=0 for any post that never entered the viewport,
// so every post always has at least one entry in the output.
function finalizeMissingPosts() {
    const seenIds = new Set(rowVisibilityData.map(e => e.doc_id));
    document.querySelectorAll('tr[id], div.insta-post[id]').forEach(row => {
        const index = parseInt(row.id);
        if (!isNaN(index) && !seenIds.has(index)) {
            rowVisibilityData.push({ doc_id: index, duration: 0 });
        }
    });
}

function updateViewportData() {
    document.getElementById('dwell_data').value = JSON.stringify(rowVisibilityData);
}

// Pause dwell tracking (e.g. during simulated network delay or tab switch)
function pauseDwellTracking() {
    if (!isPageVisible) return;
    isPageVisible = false;
    updateVisibleRowsDwellTime();
}

// Resume dwell tracking, restarting timers for posts still in the viewport
function resumeDwellTracking() {
    if (isPageVisible) return;
    isPageVisible = true;
    const currentTime = Date.now();
    Object.keys(currentlyIntersecting).forEach(index => {
        visibleRows[index] = currentTime;
    });
}

function handleVisibilityChange() {
    if (document.hidden) {
        pauseDwellTracking();
    } else {
        resumeDwellTracking();
    }
}

function initializeObserver() {
    const observer = new IntersectionObserver(handleRowVisibility, {
        root: null,
        rootMargin: '0px',
        threshold: dwell_threshold,
    });

    document.querySelectorAll('tr[id], div.insta-post[id]').forEach(row => observer.observe(row));
    console.log('Visibility tracking initialized');
    document.addEventListener('visibilitychange', handleVisibilityChange);
}

function handleSubmit(event) {
    updateVisibleRowsDwellTime(); // Finalize any currently visible posts
    finalizeMissingPosts();       // Pad unseen posts with duration=0
    console.log('Submit button clicked:', event.target.id);
}

window.addEventListener('load', function() {
    if (document.getElementById('loadingScreen').classList.contains('d-none')) {
        initializeObserver();
    } else {
        const checkPreloader = setInterval(function() {
            if (document.getElementById('loadingScreen').classList.contains('d-none')) {
                clearInterval(checkPreloader);
                initializeObserver();
            }
        }, 100);
    }

    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.addEventListener('click', handleSubmit);
    });
});

window.addEventListener('beforeunload', function() {
    updateVisibleRowsDwellTime();
    finalizeMissingPosts();
});
