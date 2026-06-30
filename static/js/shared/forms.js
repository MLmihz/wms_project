document.addEventListener('DOMContentLoaded', function () {
    const currentUrlName = document.body.dataset.urlName || '';

    // Highlight the active navigation item based on current Django URL name.
    document.querySelectorAll('.nav-link[data-active-for]').forEach(function (link) {
        const activeFor = (link.dataset.activeFor || '').split(/\s+/).filter(Boolean);
        if (activeFor.includes(currentUrlName)) {
            link.classList.add('is-active');
            link.setAttribute('aria-current', 'page');
        }
    });

    const navToggle = document.querySelector('.navbar-toggle');
    const primaryNav = document.getElementById('primary-nav');
    if (navToggle && primaryNav) {
        navToggle.addEventListener('click', function () {
            const isOpen = primaryNav.classList.toggle('is-open');
            navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
    }

    // Client-side confirm-password check for all registration/account creation forms.
    document.querySelectorAll('form').forEach(function (form) {
        const passwordInput = form.querySelector('input[name="password"]');
        const confirmInput = form.querySelector('input[name="confirm_password"]');
        if (!passwordInput || !confirmInput) return;

        function syncValidationMessage() {
            const mismatch = confirmInput.value !== '' && confirmInput.value !== passwordInput.value;
            confirmInput.setCustomValidity(mismatch ? 'Passwords do not match.' : '');
        }

        passwordInput.addEventListener('input', syncValidationMessage);
        confirmInput.addEventListener('input', syncValidationMessage);
        form.addEventListener('submit', function () {
            syncValidationMessage();
        });
    });

    // Reusable auto-submit behavior for filter selects.
    document.querySelectorAll('select[data-auto-submit="true"]').forEach(function (select) {
        select.addEventListener('change', function () {
            if (select.form) {
                select.form.submit();
            }
        });
    });
});
