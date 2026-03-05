// Focal line dwell tracker
// Records cumulative time each post spends covering a horizontal reference line
// at a configurable vertical position within the viewport (default: 0.33).

const FOCAL_Y_SHARE = (typeof js_vars !== 'undefined' && js_vars.focal_line_position !== undefined)
    ? js_vars.focal_line_position
    : 0.33;

const focalDurations = {};   // { doc_id: cumulative_seconds }
let focalElementId   = null;
let focalStartTime   = null;
let isFocalActive    = true;

function getFocalElementId() {
    const focalY = window.innerHeight * FOCAL_Y_SHARE;
    for (const row of document.querySelectorAll('tr[id]')) {
        const id = parseInt(row.id);
        if (isNaN(id)) continue;
        const rect = row.getBoundingClientRect();
        if (rect.top <= focalY && rect.bottom > focalY) return id;
    }
    return null;
}

function commitFocalTime() {
    if (focalElementId !== null && focalStartTime !== null) {
        const elapsed = (Date.now() - focalStartTime) / 1000;
        focalDurations[focalElementId] = (focalDurations[focalElementId] || 0) + elapsed;
        focalStartTime = null;
    }
}

function saveFocalData() {
    const field = document.getElementById('focal_line_data');
    if (!field) return;
    const arr = Object.entries(focalDurations).map(([doc_id, duration]) => ({
        doc_id: parseInt(doc_id),
        duration: parseFloat(duration.toFixed(3)),
    }));
    field.value = JSON.stringify(arr);
}

function updateFocalElement() {
    if (!isFocalActive) return;
    const newId = getFocalElementId();
    if (newId !== focalElementId) {
        commitFocalTime();
        focalElementId = newId;
        focalStartTime = newId !== null ? Date.now() : null;
    }
    saveFocalData();
}

function pauseFocalTracking() {
    if (!isFocalActive) return;
    commitFocalTime();
    isFocalActive = false;
    saveFocalData();
}

function resumeFocalTracking() {
    if (isFocalActive) return;
    isFocalActive = true;
    focalElementId = getFocalElementId();
    focalStartTime = focalElementId !== null ? Date.now() : null;
}

function finalizeFocalData() {
    commitFocalTime();
    saveFocalData();
}

// Listen on the feed column (scrolls inside its container, not on window)
document.addEventListener('DOMContentLoaded', function () {
    const feed = document.getElementById('feedColumn');
    if (feed) feed.addEventListener('scroll', updateFocalElement, { passive: true });
    window.addEventListener('resize', updateFocalElement, { passive: true });

    document.addEventListener('visibilitychange', function () {
        if (document.hidden) pauseFocalTracking(); else resumeFocalTracking();
    });

    document.querySelectorAll('button[type="submit"]').forEach(btn => {
        btn.addEventListener('click', finalizeFocalData);
    });

    // Initialize once preloader hides
    const checkPreloader = setInterval(function () {
        if (document.getElementById('loadingScreen').classList.contains('d-none')) {
            clearInterval(checkPreloader);
            updateFocalElement();
        }
    }, 100);
});

window.addEventListener('beforeunload', finalizeFocalData);
