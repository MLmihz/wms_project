document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('report-form');
    if (!form) return;

    const locationInput = document.getElementById('id_location');
    const locationError = document.getElementById('location-error');

    form.addEventListener('submit', function (event) {
        let isValid = true;

        if (locationInput.value.trim() === '') {
            locationError.classList.remove('hidden');
            isValid = false;
        } else {
            locationError.classList.add('hidden');
        }

        if (!isValid) {
            event.preventDefault();
        }
    });

    locationInput.addEventListener('input', function () {
        if (locationInput.value.trim() !== '') {
            locationError.classList.add('hidden');
        }
    });
});