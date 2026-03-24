console.log("Measuring rowheights ready!");

var rowHeightData = [];

function handleRowHeight(entries, observer) {
    entries.forEach((entry) => {
        const row = entry.target;
        const index = parseInt(row.id);
        if (isNaN(index)) return; // Skip rows without numeric IDs (sentinel, end-of-feed, etc.)

        if (entry.isIntersecting) {
            const height = row.offsetHeight;
            const existingIndex = rowHeightData.findIndex(item => item.doc_id === index);
            if (existingIndex !== -1) {
                rowHeightData[existingIndex].height = height;
            } else {
                rowHeightData.push({ doc_id: index, height: height });
            }
        }
    });

    updateHeightDataStorage();
}

function updateHeightDataStorage() {
    document.getElementById('rowheight_data').value = JSON.stringify(rowHeightData);
}

document.addEventListener('DOMContentLoaded', function() {
    // Pre-initialize every post with height=0 so every post always has an entry
    document.querySelectorAll('tr[id], div.insta-post[id]').forEach(row => {
        const index = parseInt(row.id);
        if (!isNaN(index)) {
            rowHeightData.push({ doc_id: index, height: 0 });
        }
    });
    updateHeightDataStorage();

    const heightObserver = new IntersectionObserver(handleRowHeight, {
        root: null,
        rootMargin: '0px',
        threshold: 0.1,
    });

    document.querySelectorAll('tr[id], div.insta-post[id]').forEach(row => {
        heightObserver.observe(row);
    });

    window.addEventListener('resize', function() {
        document.querySelectorAll('tr[id], div.insta-post[id]').forEach(row => {
            if (row.offsetHeight > 0) {
                handleRowHeight([{ target: row, isIntersecting: true }], heightObserver);
            }
        });
    });
});
