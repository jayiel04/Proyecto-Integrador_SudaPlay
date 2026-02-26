document.addEventListener('DOMContentLoaded', function () {
    const popup = document.getElementById('login-error-popup');
    const closeBtn = document.getElementById('close-login-error-popup');
    const loginInputs = document.querySelectorAll('input[name="username"], input[name="password"]');

    function hidePopup() {
        if (!popup) return;
        popup.classList.add('is-hiding');
        setTimeout(function () {
            popup.style.display = 'none';
        }, 260);
    }

    loginInputs.forEach(function (input) {
        input.classList.add('login-input-error-flash');
        setTimeout(function () {
            input.classList.remove('login-input-error-flash');
        }, 2600);
    });

    if (popup && closeBtn) {
        closeBtn.addEventListener('click', function () {
            hidePopup();
        });
        setTimeout(hidePopup, 3400);
    }
});
