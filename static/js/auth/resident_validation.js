document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');
    const phoneInput = document.getElementById('phone_number');
    const form = document.querySelector('.auth-form form');

    if (!form) return;

    // Helper: create or reuse an error message element right after a given input
    function getOrCreateError(input, id) {
        let error = document.getElementById(id);
        if (!error) {
            error = document.createElement('p');
            error.id = id;
            error.className = 'field-error';
            input.insertAdjacentElement('afterend', error);
        }
        return error;
    }

    // ---------- Password length validation ----------
    if (passwordInput) {
        const passwordError = getOrCreateError(passwordInput, 'password-error');
        passwordError.style.display = 'none';

        function validatePassword() {
            if (passwordInput.value.length > 0 && passwordInput.value.length < 8) {
                passwordError.textContent = 'Password must be at least 8 characters long.';
                passwordError.style.display = 'block';
                return false;
            }
            passwordError.style.display = 'none';
            return true;
        }

        passwordInput.addEventListener('input', validatePassword);
    }

    // ---------- Confirm password match validation ----------
    if (confirmInput) {
        const confirmError = getOrCreateError(confirmInput, 'confirm-password-error');
        confirmError.style.display = 'none';

        function validateConfirm() {
            if (confirmInput.value.length > 0 && confirmInput.value !== passwordInput.value) {
                confirmError.textContent = 'Passwords do not match.';
                confirmError.style.display = 'block';
                return false;
            }
            confirmError.style.display = 'none';
            return true;
        }

        confirmInput.addEventListener('input', validateConfirm);
        passwordInput.addEventListener('input', validateConfirm);
    }

    // ---------- Phone number validation ----------
    if (phoneInput) {
        const phoneError = getOrCreateError(phoneInput, 'phone-error');
        phoneError.style.display = 'none';

        function validatePhone() {
            // Strip anything that's not a digit, as the user types
            phoneInput.value = phoneInput.value.replace(/\D/g, '');

            if (phoneInput.value.length > 0 && phoneInput.value.length !== 10) {
                phoneError.textContent = 'Phone number must be exactly 10 digits.';
                phoneError.style.display = 'block';
                return false;
            }
            phoneError.style.display = 'none';
            return true;
        }

        phoneInput.addEventListener('input', validatePhone);
    }

    // ---------- Block submission if any rule is violated ----------
    form.addEventListener('submit', function (event) {
        let valid = true;

        if (passwordInput && passwordInput.value.length < 8) {
            valid = false;
            const passwordError = document.getElementById('password-error');
            passwordError.textContent = 'Password must be at least 8 characters long.';
            passwordError.style.display = 'block';
        }

        if (confirmInput && confirmInput.value !== passwordInput.value) {
            valid = false;
            const confirmError = document.getElementById('confirm-password-error');
            confirmError.textContent = 'Passwords do not match.';
            confirmError.style.display = 'block';
        }

        if (phoneInput && phoneInput.value.length > 0 && phoneInput.value.length !== 10) {
            valid = false;
            const phoneError = document.getElementById('phone-error');
            phoneError.textContent = 'Phone number must be exactly 10 digits.';
            phoneError.style.display = 'block';
        }

        if (!valid) {
            event.preventDefault();
        }
    });
});