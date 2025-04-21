import json
import os
from Config import *
from collections import defaultdict

# The script version. You can check the changelog at the GitHub URL to see if there is a new version.
VERSION = "1.3.1"
GITHUB_URL = "https://github.com/mbektic/Simple-SESH-Sumary/blob/main/CHANGELOG.md"


def ms_to_hms(ms):
    seconds = ms // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    milliseconds = ms - (hours * 60 * 60 * 1000) - (minutes * 60 * 1000) - (seconds * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02} {milliseconds}ms"


def print_file(path):
    with open(path, 'r') as file:
        contents = file.read()
    return contents


def escape_js_string(s):
    return s.replace("\\", "\\\\").replace("`", "\\`")


def print_styles():
    base_style = print_file("style/style.css")
    dark_style = print_file("style/dark.css")
    light_style = print_file("style/light.css")

    return f"""
    <style id="base-style">
        {base_style}
    </style>
    <style id="theme-style">
        {dark_style}
    </style>
    <script>
        const DARK_CSS = `{escape_js_string(dark_style)}`;
        const LIGHT_CSS = `{escape_js_string(light_style)}`;
    </script>
    """


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
                if (entry.get("ms_played") > 20000 or PLAYTIME_MODE) and entry.get("master_metadata_album_artist_name"):
                    artist = entry.get("master_metadata_album_artist_name")
                    track = entry.get("master_metadata_track_name") + " - " + artist
                    album = entry.get("master_metadata_album_album_name") + " - " + artist

                    if PLAYTIME_MODE and entry.get("ms_played") > 0:
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
        const ITEMS_PER_PAGE =  """ + str(ITEMS_PER_PAGE) + """
        """ + print_file("scripts/scripts.js") + """
        </script>"""

    def build_table(title, counts, table_id):
        if PLAYTIME_MODE:
            MODE_STRING = "Playtime H:M:S ms"
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

        # Clean title for column header (remove emoji and trim spacing)
        clean_title = title[2:]

        return f"""
        <h2>{title}</h2>
        <input type="text" id="{table_id}-search" placeholder="Search for {clean_title}..." class="search-input" />
        <table id="{table_id}">
            <thead>
                <tr><th>Rank</th><th>{clean_title}</th><th>{MODE_STRING}</th></tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <div class="pagination" id="{table_id}-nav"></div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Play Counts Summary</title>
        {print_styles()}
        {generate_js()}
    </head>
    <body>
        <div id="loading-overlay">
          <div class="spinner"></div>
          <div class="loading-text">Loading…</div>
        </div>
        
        <h1>Spotify Streaming History</h1>
        {build_table("🎤 Artists", artist_counts, "artist-table")}
        {build_table("🎶 Tracks", track_counts, "track-table")}
        {build_table("💿 Albums", album_counts, "album-table")}
    </body>
    <footer>
      <a id="version-link" href="{GITHUB_URL}">Version: {VERSION}</a>
          <div class="theme-toggle-wrapper">
          <input type="checkbox" id="theme-toggle" />
          <label for="theme-toggle" class="theme-toggle">
            <span class="icon sun">☀️</span>
            <span class="icon moon">🌙</span>
            <span class="ball"></span>
          </label>
        </div>
    </footer>
    </html>
    """

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ HTML report generated: {output_html}")


count_plays_from_directory(INPUT_DIR, OUTPUT_FILE)
