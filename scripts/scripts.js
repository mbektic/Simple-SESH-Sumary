const themeStyle = document.getElementById("theme-style");
const currentTheme = localStorage.getItem("theme") || "dark";
themeStyle.textContent = currentTheme === "dark" ? DARK_CSS : LIGHT_CSS;
const originalRowCache = {};
const searchTerms = {};

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

        // Re-enable scrolling after fade-out transition
        overlay.addEventListener('transitionend', () => {
            document.body.style.overflow = '';
            document.documentElement.style.overflow = '';
        }, {once: true});
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

        const term = searchInput.value;
        const prefix = tableId.replace(/-(?:\d{4}|all)$/, '');
        searchTerms[prefix] = term;       // save it
        highlightVisibleMatches(term);
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
        // derive a “prefix” like "artist-table" or "track-table" (drops "-2023" or "-all")
        const prefix = tableId.replace(/-(?:\d{4}|all)$/, '');
        searchInput.addEventListener("input", () => {
            const term = searchInput.value;
            searchTerms[prefix] = term;       // save it
            applySearch(term);
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
    const modeToggleText = document.getElementById(`mode-toggle-label`);
    modeToggle.addEventListener("change", () => {
        const newMode = modeToggle.checked ? "playtime" : "playcount";

        document.querySelectorAll('.year-section').forEach(sec => {
            const yr = sec.id.split('-')[1];          // e.g. "all", "2023", etc.
            ["artist-table", "track-table", "album-table"].forEach(base => {
                switchMode(`${base}-${yr}`, newMode);
            });
        });

        modeToggleText.textContent = modeToggle.checked
            ? "Switch to Playcount:"
            : "Switch to Playtime:";
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

// Focus trap utility function
function setupFocusTrap(modalElement) {
    const focusableElements = modalElement.querySelectorAll(
        'a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Handle tab key to trap focus
    modalElement.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            // Shift + Tab
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } 
            // Tab
            else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const settingsBtn = document.getElementById("settings-button");
    const modal = document.getElementById("settings-modal");
    const closeBtn = document.getElementById("close-settings");

    // Set up focus traps for all modals
    setupFocusTrap(modal);
    setupFocusTrap(document.getElementById('info-modal'));
    setupFocusTrap(document.getElementById('every-year-modal'));

    // Open modal
    settingsBtn.addEventListener("click", () => {
        modal.style.display = "flex";
        // Focus the first focusable element
        const firstFocusable = modal.querySelector('a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            setTimeout(() => firstFocusable.focus(), 50);
        }
    });

    // Close modal when the close button is clicked
    closeBtn.addEventListener("click", () => {
        modal.style.display = "none";
        // Return focus to the button that opened the modal
        settingsBtn.focus();
    });

    // Close modal if clicked outside of modal content
    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
            // Return focus to the button that opened the modal
            settingsBtn.focus();
        }
    });

    // Close modals with Escape key
    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            // Close any open modal and return focus
            if (modal.style.display === "flex") {
                modal.style.display = "none";
                settingsBtn.focus();
            }
            if (document.getElementById('info-modal').style.display === "flex") {
                document.getElementById('info-modal').style.display = "none";
                // Return focus to the button that opened the modal
                const infoButtons = document.querySelectorAll('.info-button');
                if (infoButtons.length > 0) infoButtons[0].focus();
            }
            if (document.getElementById('every-year-modal').style.display === "flex") {
                document.getElementById('every-year-modal').style.display = "none";
                // Return focus to the button that opened the modal
                document.getElementById('show-every-year-btn').focus();
            }
        }
    });

    // year-tab click handler
    const yearTabs = document.querySelectorAll('.year-tab');

    // Function to activate a tab
    function activateTab(tab) {
        yearTabs.forEach(t => {
            t.classList.remove('active');
            t.setAttribute('aria-selected', 'false');
        });
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');

        document.querySelectorAll('.year-section').forEach(sec => {
            sec.style.display = 'none';
            sec.setAttribute('aria-hidden', 'true');
        });
        const y = tab.dataset.year;
        const section = document.getElementById(`year-${y}`);
        section.style.display = 'block';
        section.setAttribute('aria-hidden', 'false');

        // restore any saved searches in this section
        section.querySelectorAll('.search-input').forEach(input => {
            // map "artist-table-2023-search" → "artist-table-2023" → prefix "artist-table"
            const tableId = input.id.replace(/-search$/, '');
            const prefix = tableId.replace(/-(?:\d{4}|all)$/, '');
            const term = searchTerms[prefix] || "";
            input.value = term;

            input.dispatchEvent(new Event('input'));
        });
    }

    // Set up tabs for accessibility
    const tabsContainer = document.getElementById('year-tabs');
    tabsContainer.setAttribute('role', 'tablist');
    tabsContainer.setAttribute('aria-label', 'Year selection');

    // Set up sections for accessibility
    document.querySelectorAll('.year-section').forEach(section => {
        section.setAttribute('role', 'tabpanel');
        section.setAttribute('aria-hidden', section.style.display === 'none' ? 'true' : 'false');
    });

    // Add click handler to each tab
    yearTabs.forEach(tab => {
        // Make tabs keyboard focusable
        tab.setAttribute('tabindex', '0');
        tab.setAttribute('role', 'tab');
        tab.setAttribute('aria-selected', tab.classList.contains('active') ? 'true' : 'false');

        // Set aria-controls attribute
        const year = tab.dataset.year;
        tab.setAttribute('aria-controls', `year-${year}`);

        // Click handler
        tab.addEventListener('click', () => {
            activateTab(tab);
        });

        // Keyboard handler - activate on Enter or Space
        tab.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                activateTab(tab);
            }
        });
    });

    // Add arrow key navigation for tabs
    tabsContainer.addEventListener('keydown', (e) => {
        if (e.target.classList.contains('year-tab')) {
            const currentTab = e.target;
            const tabsArray = Array.from(yearTabs);
            const currentIndex = tabsArray.indexOf(currentTab);

            // Right arrow or Down arrow - move to next tab
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                e.preventDefault();
                const nextIndex = (currentIndex + 1) % tabsArray.length;
                tabsArray[nextIndex].focus();
            }
            // Left arrow or Up arrow - move to previous tab
            else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                const prevIndex = (currentIndex - 1 + tabsArray.length) % tabsArray.length;
                tabsArray[prevIndex].focus();
            }
        }
    });

    const everyYearBtn = document.getElementById('show-every-year-btn');
    const everyYearModal = document.getElementById('every-year-modal');
    const closeEveryYearBtn = document.getElementById('close-every-year-modal');
    const infoModal = document.getElementById('info-modal');
    const closeInfoBtn = document.getElementById('close-info-modal');

    everyYearBtn.addEventListener('click', () => {
        everyYearModal.style.display = 'flex';
        // Focus the first focusable element
        const firstFocusable = everyYearModal.querySelector('a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            setTimeout(() => firstFocusable.focus(), 50);
        }
    });

    // close button for every-year-modal
    closeEveryYearBtn.addEventListener('click', () => {
        everyYearModal.style.display = 'none';
        // Return focus to the button that opened the modal
        everyYearBtn.focus();
    });

    // Info-button modal
    document.querySelectorAll('.info-button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('info-modal-text').textContent = btn.dataset.info;
            infoModal.style.display = 'flex';
            // Store the button that opened the modal
            infoModal.dataset.opener = btn.id || '';
            // Focus the first focusable element
            const firstFocusable = infoModal.querySelector('a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                setTimeout(() => firstFocusable.focus(), 50);
            }
        });
    });

    // Close modals when clicking outside
    ['click', 'touchstart'].forEach(evt => {
        window.addEventListener(evt, e => {
            if (e.target.id === 'every-year-modal') {
                e.target.style.display = 'none';
                // Return focus to the button that opened the modal
                everyYearBtn.focus();
            } else if (e.target.id === 'info-modal') {
                e.target.style.display = 'none';
                // Return focus to the button that opened the modal
                const openerId = infoModal.dataset.opener;
                if (openerId) {
                    const opener = document.getElementById(openerId);
                    if (opener) opener.focus();
                }
            }
        });
    });

    // close the info modal
    closeInfoBtn.addEventListener('click', () => {
        infoModal.style.display = 'none';
        // Return focus to the button that opened the modal
        const openerId = infoModal.dataset.opener;
        if (openerId) {
            const opener = document.getElementById(openerId);
            if (opener) opener.focus();
        }
    });
});
