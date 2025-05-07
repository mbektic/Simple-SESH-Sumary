const TRACKS_PER_PAGE = 5;
let currentPage = 0;
let currentList = [];

function renderOTDPage() {
    const start = currentPage * TRACKS_PER_PAGE;
    const end = start + TRACKS_PER_PAGE;
    const slice = currentList.slice(start, end);

    document.getElementById("otd-results").innerHTML = `
    <ol class="otd-list">
      ${slice.map(({track, date, count}) => `
        <li>
          <span class="otd-track">${track}</span>
          <span class="otd-meta">${count}× on ${new Date(date + 'T12:00:00Z').toLocaleDateString()}</span>
        </li>
      `).join("")}
    </ol>
  `;

    const pageLabel = document.getElementById("otd-page-label");
    const totalPages = Math.ceil(currentList.length / TRACKS_PER_PAGE);
    pageLabel.textContent = `Page ${currentPage + 1} of ${totalPages}`;

    document.getElementById("otd-prev").disabled = currentPage === 0;
    document.getElementById("otd-next").disabled = currentPage >= totalPages - 1;
}

function renderOTD(dateStr) {
    const mmdd = dateStr.slice(5, 10);
    currentList = onThisDayData[mmdd] || [];

    if (!currentList.length) {
        document.getElementById("otd-results").innerHTML = `<p>No songs were played more than 2x on this day in past years.</p>`;
        document.getElementById("otd-pagination").style.display = "none";
        return;
    }

    currentList.sort((a, b) => b.count - a.count);

    currentPage = 0;
    const totalPages = Math.ceil(currentList.length / TRACKS_PER_PAGE);
    document.getElementById("otd-pagination").style.display = totalPages > 1 ? "block" : "none";

    renderOTDPage();
}

// Initialization
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("otd-date");
    const today = new Date().toISOString().slice(0, 10);
    input.value = today;
    renderOTD(today);

    input.addEventListener("change", e => {
        renderOTD(e.target.value);
    });

    document.getElementById("otd-prev").addEventListener("click", () => {
        if (currentPage > 0) {
            currentPage--;
            renderOTDPage();
        }
    });

    document.getElementById("otd-next").addEventListener("click", () => {
        if ((currentPage + 1) * TRACKS_PER_PAGE < currentList.length) {
            currentPage++;
            renderOTDPage();
        }
    });
});