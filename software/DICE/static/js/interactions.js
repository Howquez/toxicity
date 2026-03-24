console.log("inconsequential interactions ready!");


// REPOSTS (Frontend only)
var repostButtons = document.querySelectorAll(".repost-button");

repostButtons.forEach(function(repostButton) {
    var repostCount = repostButton.querySelector(".repost-count");
    var repostIcon  = repostButton.querySelector(".repost-icon");

    repostButton.addEventListener("click", function() {
        let originalText = repostCount.textContent;
        let repostNum = parseInt(originalText.replace(/[^0-9]/g, '')); // Remove non-numeric characters

        if (repostButton.classList.contains("reposted")) {
            repostButton.classList.remove("reposted");
            if (!originalText.includes('K') && !originalText.includes('M')) {
                repostNum--; // Decrement if no 'K' or 'M'
                repostCount.textContent = repostNum.toString();
            }
            repostIcon.className="bi bi-arrow-repeat text-secondary repost-icon";
            repostIcon.removeAttribute("style");
        } else {
            repostButton.classList.add("reposted");
            if (!originalText.includes('K') && !originalText.includes('M')) {
                repostNum++; // Increment if no 'K' or 'M'
                repostCount.textContent = repostNum.toString();
            }
            repostIcon.className="bi bi-arrow-repeat text-primary repost-icon";
            repostIcon.style="font-weight: bold"; // Adjust style to indicate active state
        }
    });
});


// SHARES (Frontend only)
var shareButtons = document.querySelectorAll(".share-button");

shareButtons.forEach(function(shareButton) {
    var shareIcon  = shareButton.querySelector(".share-icon");

    shareButton.addEventListener("click", function() {
      if (shareButton.classList.contains("shared")) {
        shareButton.classList.remove("shared");
        shareIcon.className="bi bi-upload text-secondary share-icon";
        shareIcon.removeAttribute("style")
    } else {
        shareButton.classList.add("shared");
        shareIcon.className="bi bi-upload text-primary share-icon";
        shareIcon.style="-webkit-text-stroke: 0.5px"
    }
});
});
