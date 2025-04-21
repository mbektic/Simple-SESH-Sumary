function paginateTable(tableId, pageSize) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector("tbody");
    const searchInput = document.getElementById(`${tableId}-search`);

    // Cache original full dataset as cloned rows
    const originalRows = Array.from(tbody.querySelectorAll("tr")).map(tr => tr.cloneNode(true));
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

        renderPage(1);
    }

    // Hook up search input
    if (searchInput) {
        searchInput.addEventListener("input", () => {
            applySearch(searchInput.value);
        });
    }

    renderPage(currentPage);
}


document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("theme-toggle");
  const themeStyle = document.getElementById("theme-style");

  const currentTheme = localStorage.getItem("theme") || "{'dark' if DARK_MODE else 'light'}";
  themeStyle.textContent = currentTheme === "dark" ? DARK_CSS : LIGHT_CSS;
  toggle.checked = currentTheme === "dark";

  toggle.addEventListener("change", () => {
    const isDark = toggle.checked;
    themeStyle.textContent = isDark ? DARK_CSS : LIGHT_CSS;
    localStorage.setItem("theme", isDark ? "dark" : "light");
  });
})