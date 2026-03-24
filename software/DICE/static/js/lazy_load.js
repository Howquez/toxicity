// Number of posts to show per batch. Adjust here if needed.
const BATCH_SIZE = 8;

document.addEventListener('DOMContentLoaded', function () {
    const rows = Array.from(document.querySelectorAll('#post_table tbody tr[id]'));
    const endRow = document.querySelector('#submitButtonBottom').closest('tr');

    // Nothing to lazy-load if the feed fits in a single batch
    if (rows.length <= BATCH_SIZE) return;

    let loadedCount = BATCH_SIZE;

    // Hide all posts beyond the first batch
    rows.slice(BATCH_SIZE).forEach(row => { row.style.display = 'none'; });

    // Hide the end-of-feed row until all posts are revealed
    endRow.style.display = 'none';

    // Spinner row that acts as the scroll sentinel
    const sentinel = document.createElement('tr');
    sentinel.id = 'lazy-load-sentinel';
    sentinel.innerHTML = `
        <td class="text-center py-4 border-0">
            <div class="spinner-border spinner-border-sm text-secondary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </td>`;
    rows[BATCH_SIZE - 1].insertAdjacentElement('afterend', sentinel);

    function revealNextBatch() {
        const nextBatch = rows.slice(loadedCount, loadedCount + BATCH_SIZE);
        nextBatch.forEach(row => { row.style.display = ''; });
        loadedCount += nextBatch.length;

        // Resume dwell tracking now that new posts are visible
        resumeDwellTracking();
    resumeFocalTracking();

        if (loadedCount >= rows.length) {
            sentinel.remove();
            endRow.style.display = '';
        } else {
            rows[loadedCount - 1].insertAdjacentElement('afterend', sentinel);
            io.observe(sentinel);
        }
    }

    let io;
    io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                io.unobserve(sentinel);

                // Pause dwell tracking during the simulated network delay
                pauseDwellTracking();
        pauseFocalTracking();

                setTimeout(revealNextBatch, js_vars.batch_delay);
            }
        });
    }, { threshold: 0.1 });

    io.observe(sentinel);
});
