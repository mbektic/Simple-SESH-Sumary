function paginateTable(tableId, pageSize) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));
    const totalPages = Math.ceil(rows.length / pageSize);

    let currentPage = 1;

    function renderPage(page) {
        currentPage = page;
        rows.forEach((row, index) => {
            row.style.display = (index >= (page - 1) * pageSize && index < page * pageSize) ? "" : "none";
        });
        renderPagination();
    }

    function renderPagination() {
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

        // Prev button
        createButton("Prev", currentPage - 1, false, currentPage === 1);

        // Page buttons
        const pageWindow = 2;
        const startPage = Math.max(1, currentPage - pageWindow);
        const endPage = Math.min(totalPages, currentPage + pageWindow);

        if (startPage > 1) {
            createButton("1", 1);
            if (startPage > 2) {
                const ellipsis = document.createElement("span");
                ellipsis.className = "ellipsis";
                ellipsis.textContent = "...";
                nav.appendChild(ellipsis);
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            createButton(i, i, i === currentPage);
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsis = document.createElement("span");
                ellipsis.className = "ellipsis";
                ellipsis.textContent = "...";
                nav.appendChild(ellipsis);
            }
            createButton(totalPages, totalPages);
        }

        // Next button
        createButton("Next", currentPage + 1, false, currentPage === totalPages);
    }

    renderPage(currentPage);
}