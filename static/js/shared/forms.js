document.addEventListener('DOMContentLoaded', function () {
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
