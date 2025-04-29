const themeStyle = document.getElementById("theme-style");
const currentTheme = localStorage.getItem("theme") || "dark";
themeStyle.textContent = currentTheme === "dark" ? DARK_CSS : LIGHT_CSS;
const originalRowCache = {};

window.onload = () => {
    const overlay = document.getElementById('loading-overlay');

    requestAnimationFrame(() => {
        document.querySelectorAll('.year-section').forEach(sec => {
            const yr = sec.id.split('-')[1];
            paginateTable(`artist-table-${yr}`, ITEMS_PER_PAGE);
            paginateTable(`track-table-${yr}`, ITEMS_PER_PAGE);
            paginateTable(`album-table-${yr}`, ITEMS_PER_PAGE);
        });

        // Trigger the fade-out
        overlay.classList.add('fade-out');
    });
};

function paginateTable(tableId, pageSize) {
    const mode = document.querySelector(`#${tableId}-playcount`).style.display !== 'none' ? 'playcount' : 'playtime';
    const visibleTable = document.querySelector(`#${tableId}-${mode} table`);
    const tbody = visibleTable.querySelector("tbody");
    const searchInput = document.getElementById(`${tableId}-search`);
    const cacheKey = `${tableId}-${mode}`;

    if (!originalRowCache[cacheKey]) {
        originalRowCache[cacheKey] = Array.from(tbody.querySelectorAll("tr")).map(tr => tr.cloneNode(true));
    }

    const originalRows = originalRowCache[cacheKey];
    let filteredRows = [...originalRows];
    let currentPage = 1;

    function renderPage(page) {
        currentPage = page;
        const start = (page - 1) * pageSize;
        const end = page * pageSize;
        const frag = document.createDocumentFragment();

        filteredRows.slice(start, end).forEach(tr => {
            frag.appendChild(tr.cloneNode(true));
        });

        tbody.innerHTML = "";
        tbody.appendChild(frag);

        requestAnimationFrame(renderPagination);
    }

    function renderPagination() {
        const totalPages = Math.ceil(filteredRows.length / pageSize);
        const nav = document.getElementById(`${tableId}-nav`);
        nav.innerHTML = "";

        function createButton(label, page, active = false, disabled = false) {
            const btn = document.createElement("button");
            btn.textContent = label;
            if (active) btn.classList.add("active");
            if (disabled) btn.disabled = true;
            btn.onclick = () => renderPage(page);
            nav.appendChild(btn);
        }

        createButton("Prev", currentPage - 1, false, currentPage === 1);

        const pageWindow = 1;
        const startPage = Math.max(1, currentPage - pageWindow);
        const endPage = Math.min(totalPages, currentPage + pageWindow);

        if (startPage > 1) {
            createButton("1", 1);
            if (startPage > 2) nav.appendChild(document.createTextNode("..."));
        }

        for (let i = startPage; i <= endPage; i++) {
            createButton(i, i, i === currentPage);
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) nav.appendChild(document.createTextNode("..."));
            createButton(totalPages, totalPages);
        }

        createButton("Next", currentPage + 1, false, currentPage === totalPages);
    }

    function applySearch(term) {
        const lowerTerm = term.toLowerCase();

        filteredRows = originalRows.filter(tr =>
            tr.textContent.toLowerCase().includes(lowerTerm)
        );

        if (filteredRows.length === 0) {
            const colCount = originalRows[0]?.children.length || 1;
            const noResultsRow = document.createElement("tr");
            const td = document.createElement("td");
            td.style.height = "300px";
            td.colSpan = colCount;
            td.textContent = "No results found.";
            td.style.textAlign = "center";
            noResultsRow.appendChild(td);
            filteredRows = [noResultsRow];
        }

        renderPage(1);

        // Highlight matches only if there are results
        if (filteredRows.length > 0 && filteredRows[0].textContent !== "No results found.") {
            highlightVisibleMatches(term);
        }
    }

    function highlightVisibleMatches(term) {
        if (!term) return;

        const regex = new RegExp(`(${term})`, "gi");
        const tbody = document.querySelector(`#${tableId}-${mode} table tbody`);
        const rows = tbody.querySelectorAll("tr");

        rows.forEach(row => {
            row.querySelectorAll("td").forEach(cell => {
                const originalText = cell.textContent;
                cell.innerHTML = originalText.replace(regex, `<span class="highlight">$1</span>`);
            });
        });
    }

    if (searchInput) {
        searchInput.addEventListener("input", () => {
            applySearch(searchInput.value);
        });
    }

    renderPage(currentPage);
}

document.addEventListener("DOMContentLoaded", () => {
    // Theme mode toggle
    const toggle = document.getElementById("theme-toggle");
    toggle.checked = currentTheme === "dark";

    toggle.addEventListener("change", () => {
        const isDark = toggle.checked;
        themeStyle.textContent = isDark ? DARK_CSS : LIGHT_CSS;
        localStorage.setItem("theme", isDark ? "dark" : "light");
    });

    // Global mode toggle
    const modeToggle = document.getElementById("global-mode-toggle");
    const modeToggleText = document.getElementById(`mode-toggle-label`)
    ;
    modeToggle.addEventListener("change", () => {
        const newMode = modeToggle.checked ? "playtime" : "playcount";

        ["artist-table", "track-table", "album-table"].forEach(tableId => {
            switchMode(tableId, newMode);
        });

        modeToggleText.textContent = modeToggle.checked ? "Switch to Playcount:" : "Switch to Playtime:";
    });
})


function switchMode(tableId, mode) {
    const playcountDiv = document.getElementById(`${tableId}-playcount`);
    const playtimeDiv = document.getElementById(`${tableId}-playtime`);

    if (mode === 'playcount') {
        playcountDiv.style.display = 'block';
        playtimeDiv.style.display = 'none';
    } else {
        playcountDiv.style.display = 'none';
        playtimeDiv.style.display = 'block';
    }

    paginateTable(tableId, ITEMS_PER_PAGE);
}

document.addEventListener("DOMContentLoaded", () => {
    const settingsBtn = document.getElementById("settings-button");
    const modal = document.getElementById("settings-modal");
    const closeBtn = document.getElementById("close-settings");

    // Open modal
    settingsBtn.addEventListener("click", () => {
        modal.style.display = "flex";
    });

    // Close modal when close button is clicked
    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // Close modal if clicked outside of modal content
    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });

    // year-tab click handler
    document.querySelectorAll('.year-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.year-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            document.querySelectorAll('.year-section').forEach(sec => {
                sec.style.display = 'none';
            });

            const y = tab.dataset.year;
            document.getElementById(`year-${y}`).style.display = 'block';
        });
    });
});