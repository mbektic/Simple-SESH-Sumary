(function () {
    const dayMs = 24 * 60 * 60 * 1000;
    const container = document.getElementById('calendar-heatmap');

    // helper to compute ISO week number
    function getISOWeek(d) {
        const date = new Date(d.getTime());
        date.setHours(0, 0, 0, 0);
        date.setDate(date.getDate() + 3 - (date.getDay() + 6) % 7);
        const firstThursday = new Date(date.getFullYear(), 0, 4);
        return 1 + Math.round(((date - firstThursday) / dayMs - 3 + (firstThursday.getDay() + 6) % 7) / 7);
    }

    for (let d = new Date(startDate); d <= endDate; d = new Date(d.getTime() + dayMs)) {
        const dateStr = d.toISOString().slice(0, 10);
        const cnt = counts[dateStr] || 0;
        const level = Math.min(4, Math.floor(cnt / 10));
        const cell = document.createElement('div');
        cell.className = 'heatmap-cell level-' + level;

        const weekNum = getISOWeek(d);

        // Create a more detailed tooltip content
        const tooltipContent = `
            <div class="heatmap-tooltip">
                <div class="tooltip-date">${new Date(dateStr).toLocaleDateString(undefined, {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        })}</div>
                <div class="tooltip-plays">${cnt} plays</div>
                <div class="tooltip-week">Week ${weekNum}</div>
            </div>
        `;

        // Initialize tooltip
        tippy(cell, {
            content: tooltipContent,
            allowHTML: true,
            placement: 'top',
            arrow: true,
            theme: 'spotify'
        });

        container.appendChild(cell);
    }
})();