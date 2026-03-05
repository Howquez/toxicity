console.log("Reactions (likes, replies, and promoted content clicks) ready!");

document.addEventListener('DOMContentLoaded', function() {
    console.log("Document is ready!");

    function toggleLike(button) {
        const icon = button.querySelector('.like-icon');
        const likeCountSpan = button.querySelector('.like-count');
        let originalText = likeCountSpan.textContent;
        let likeCount = parseInt(originalText);

        if (icon.classList.contains('bi-heart')) {
            icon.classList.remove('bi-heart', 'text-secondary');
            icon.classList.add('bi-heart-fill', 'text-danger');
            if (!originalText.includes('K') && !originalText.includes('M')) {
                likeCount++;
            }
        } else {
            icon.classList.remove('bi-heart-fill', 'text-danger');
            icon.classList.add('bi-heart', 'text-secondary');
            if (!originalText.includes('K') && !originalText.includes('M')) {
                likeCount--;
            }
        }

        if (originalText.includes('K') || originalText.includes('M')) {
            likeCountSpan.textContent = originalText;
        } else {
            likeCountSpan.textContent = likeCount.toString();
        }
        console.log("Like toggled for button:", button.id, "; New count:", likeCountSpan.textContent);
    }

    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function() {
            toggleLike(button);
        });
    });

    function collectLikes() {
        let likesData = [];
        document.querySelectorAll('.like-button').forEach(button => {
            let docId = parseInt(button.getAttribute('id').replace('like_button_', ''));
            let icon = button.querySelector('.like-icon');
            let isLiked = icon.classList.contains('bi-heart-fill');
            likesData.push({ doc_id: docId, liked: isLiked });
        });
        console.log("Collected likes data:", JSON.stringify(likesData));
        return likesData;
    }

    function collectReplies() {
        let repliesData = [];
        document.querySelectorAll('.reply-modal-button').forEach(button => {
            let docId = parseInt(button.getAttribute('id').replace('reply_modal_button_', ''));
            const replyField = document.getElementById(`reply_to_item_${docId}`);
            const replyText = replyField.value.trim();
            repliesData.push({ doc_id: docId, reply: replyText, hasReply: !!replyText });
        });
        console.log("Collected replies data:", JSON.stringify(repliesData));
        return repliesData;
    }

    // Helper to get doc_id from element (supports both post and Instagram formats)
    function getDocIdFromElement(element) {
        // Try post format first (.post-content with id="post_X")
        let postContent = element.closest('.post-content');
        if (postContent && postContent.id) {
            return parseInt(postContent.id.replace('post_', ''));
        }
        // Try Instagram format (.insta-post with id="X")
        let instaPost = element.closest('.insta-post');
        if (instaPost && instaPost.id) {
            return parseInt(instaPost.id);
        }
        return null;
    }


    function collectDataHarmonized() {
        return {
            likes: JSON.stringify(collectLikes()),
            replies: JSON.stringify(collectReplies()),
        };
    }

    const submitButtonTop = document.getElementById('submitButtonTop');
    if (submitButtonTop) {
        submitButtonTop.addEventListener('click', function(event) {
            let data = collectDataHarmonized();
            document.getElementById('likes_data').value = data.likes;
            document.getElementById('replies_data').value = data.replies;
            console.log("Data to send:", data);
        });
    }

    const submitButtonBottom = document.getElementById('submitButtonBottom');
    if (submitButtonBottom) {
        submitButtonBottom.addEventListener('click', function(event) {
            let data = collectDataHarmonized();
            document.getElementById('likes_data').value = data.likes;
            document.getElementById('replies_data').value = data.replies;
            console.log("Data to send:", data);
        });
    }

    function displayPostContent(docId, postContent) {
        const replyingPostDiv = document.getElementById(`replying_post_${docId}`);
        replyingPostDiv.textContent = postContent;
    }

    document.querySelectorAll('.reply-button').forEach(button => {
        button.addEventListener('click', function() {
            const docId = this.id.replace('reply_button_', '');
            const postTextElement = document.getElementById("post_text_" + docId);
            if (postTextElement) {
                displayPostContent(docId, postTextElement.textContent);
            }
        });
    });

    // Reply modal: when user submits a reply, update count and turn blue
    document.querySelectorAll('.reply-modal-button').forEach(button => {
        button.addEventListener('click', function() {
            const docId = this.id.replace('reply_modal_button_', '');
            const replyField = document.getElementById(`reply_to_item_${docId}`);
            const replyText = replyField ? replyField.value.trim() : '';

            if (replyText) {
                const replyIcon = document.getElementById(`reply_icon_${docId}`);
                const replyCountSpan = document.getElementById(`reply_count_${docId}`);

                if (replyIcon) {
                    replyIcon.classList.remove('bi-chat', 'text-secondary');
                    replyIcon.classList.add('bi-chat-fill', 'text-primary');
                }

                if (replyCountSpan) {
                    let originalText = replyCountSpan.textContent;
                    if (!originalText.includes('K') && !originalText.includes('M')) {
                        let replyCount = parseInt(originalText) || 0;
                        replyCount++;
                        replyCountSpan.textContent = replyCount.toString();
                    }
                    replyCountSpan.classList.remove('text-secondary');
                    replyCountSpan.classList.add('text-primary');
                }
            }
            console.log("Reply submitted for post:", docId, "; Text:", replyText);
        });
    });
});