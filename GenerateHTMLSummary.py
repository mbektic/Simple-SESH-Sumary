import json
import os
from collections import defaultdict

# How you want to rank the songs. If True, it will base the rankings on how long you listened to the track/artist/album. This also ignores the `MIN_MILLISECONDS` FLAG
PLAYTIME_MODE = False
# Minimum number of milliseconds that you listened to the song. Changing this can drastically alter counts
MIN_MILLISECONDS = 20000
# Directory where your json files are, easyist method is to just drop them in the sesh folder.
INPUT_DIR = "sesh"
# Name/path of the output file. if you don't change this it will be in the same folder as this script with the name summary.html
OUTPUT_FILE = "summary.html"
# The number of items per table page.
ITEMS_PER_PAGE = 10

VERSION = "1.1.0"
GITHUB_URL = "https://github.com/mbektic/Simple-SESH-Sumary/blob/main/CHANGELOG.md"

def ms_to_hms(ms):
    seconds = ms // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def count_plays_from_directory(input_dir, output_html):
    artist_counts = defaultdict(int)
    track_counts = defaultdict(int)
    album_counts = defaultdict(int)

    json_files = [
        os.path.join(input_dir, filename)
        for filename in os.listdir(input_dir)
        if filename.endswith(".json")
    ]

    if not json_files:
        print("⚠️ No JSON files found in the directory.")
        return

    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Error reading {file}: {e}")
            continue

        for entry in data:
            if entry.get("ms_played") is not None:
                if (entry.get("ms_played") > 20000 or PLAYTIME_MODE) and  entry.get("master_metadata_album_artist_name"):
                    artist = entry.get("master_metadata_album_artist_name")
                    track = entry.get("master_metadata_track_name") + " - " + artist
                    album = entry.get("master_metadata_album_album_name") + " - " + artist

                    if PLAYTIME_MODE:
                        if artist:
                            artist_counts[artist] += entry.get("ms_played")
                        if track:
                            track_counts[track] += entry.get("ms_played")
                        if album:
                            album_counts[album] += entry.get("ms_played")
                    else:
                        if artist:
                            artist_counts[artist] += 1
                        if track:
                            track_counts[track] += 1
                        if album:
                            album_counts[album] += 1

    def generate_js():
        return """<script>
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

window.onload = function () {
    paginateTable("artist-table", """ + str(ITEMS_PER_PAGE) + """);
    paginateTable("track-table", """ + str(ITEMS_PER_PAGE) + """);
    paginateTable("album-table", """ + str(ITEMS_PER_PAGE) + """);
};
</script>
        """

    def build_table(title, counts, table_id):
        if PLAYTIME_MODE:
            MODE_STRING = "Time Listened (Hours:Minutes:Seconds)"
            rows = "\n".join(
                f"<tr><td>{rank}</td><td>{name}</td><td>{ms_to_hms(count)}</td></tr>"
                for rank, (name, count) in enumerate(sorted(counts.items(), key=lambda x: x[1], reverse=True), start=1)
            )
        else:
            MODE_STRING = "Plays"
            rows = "\n".join(
                f"<tr><td>{rank}</td><td>{name}</td><td>{count}</td></tr>"
                for rank, (name, count) in enumerate(sorted(counts.items(), key=lambda x: x[1], reverse=True), start=1)
            )
        return f"""
        <h2>{title}</h2>
        <table id="{table_id}">
            <thead>
                <tr><th>Rank</th><th>Name</th><th>{MODE_STRING}</th></tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <div class="pagination" id="{table_id}-nav"></div>
        """

    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Play Counts Summary</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f4f9;
                padding: 20px;
                color: #333;
            }}
            h1, h2 {{
                text-align: center;
            }}
            table {{
                width: 60%;
                margin: 20px auto;
                border-collapse: collapse;
                background-color: #fff;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            th, td {{
                padding: 12px;
                text-align: center;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #007acc;
                color: white;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            .pagination {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 6px;
                margin: 15px auto 40px;
                font-family: sans-serif;
            }}
            .pagination button {{
                background: none;
                border: none;
                padding: 6px 10px;
                font-size: 14px;
                cursor: pointer;
                color: #333;
                border-bottom: 2px solid transparent;
                transition: border-color 0.2s ease;
            }}
            .pagination button.hover {{
               border-color: #999;
            }}
            .pagination button.active {{
                border-color: red;
                font-weight: bold;
                color: red;
            }}
            .pagination button.disabled {{
                color: #ccc;
                cursor: default;
            }}
            .pagination .ellipsis {{
                padding: 6px 8px;
                color: #aaa;
            }}
        </style>
        {generate_js()}
    </head>
    <body>
        <h1>Play Counts Summary</h1>
        {build_table("🎤 Artist Play Counts", artist_counts, "artist-table")}
        {build_table("🎶 Track Play Counts", track_counts, "track-table")}
        {build_table("💿 Album Play Counts", album_counts, "album-table")}
    </body>
    <footer>
      <a href="{GITHUB_URL}">Version: {VERSION}</a>
    </footer>
    </html>
    """

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ HTML report generated: {output_html}")

# Example usage:
# Replace "your_directory_path" with the path to your folder with JSON files
count_plays_from_directory(INPUT_DIR, OUTPUT_FILE)