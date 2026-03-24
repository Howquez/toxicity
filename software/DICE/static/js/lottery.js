document.addEventListener('DOMContentLoaded', function () {
    const enterBtn = document.getElementById('lotteryEnterBtn');
    const field    = document.getElementById('lottery_signup');

    if (!enterBtn) return;

    enterBtn.addEventListener('click', function () {
        // Record sign-up
        if (field) field.value = 'true';

        // Update button to confirm entry
        enterBtn.textContent = '✅ You\'re in the draw!';
        enterBtn.disabled = true;
        enterBtn.style.background = '#198754';
        enterBtn.classList.remove('lottery-cta');

        // Show toast
        const toastEl = document.getElementById('lotteryToast');
        if (toastEl) new bootstrap.Toast(toastEl, { delay: 4000 }).show();
    });
});
