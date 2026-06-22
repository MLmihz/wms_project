document.addEventListener('DOMContentLoaded', function () {
    const table = document.getElementById('schedule-table');
    if (!table) return;

    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const zoneFilter = document.getElementById('zone-filter');
    const typeFilter = document.getElementById('type-filter');
    const noResults = document.getElementById('no-results');

    const zones = new Set();
    const types = new Set();
    rows.forEach(row => {
        zones.add(row.dataset.zone);
        types.add(row.dataset.wasteType);
    });

    zones.forEach(zone => {
        const option = document.createElement('option');
        option.value = zone;
        option.textContent = zone;
        zoneFilter.appendChild(option);
    });

    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        typeFilter.appendChild(option);
    });

    function applyFilters() {
        const selectedZone = zoneFilter.value;
        const selectedType = typeFilter.value;
        let visibleCount = 0;

        rows.forEach(row => {
            const zoneMatch = !selectedZone || row.dataset.zone === selectedZone;
            const typeMatch = !selectedType || row.dataset.wasteType === selectedType;
            const shouldShow = zoneMatch && typeMatch;

            row.style.display = shouldShow ? '' : 'none';
            if (shouldShow) visibleCount++;
        });

        noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }

    zoneFilter.addEventListener('change', applyFilters);
    typeFilter.addEventListener('change', applyFilters);
});