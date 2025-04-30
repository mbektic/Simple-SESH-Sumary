from datetime import datetime, date
import json
import sys
import calendar
from Gui import *
from collections import defaultdict, Counter

# The script version. You can check the changelog at the GitHub URL to see if there is a new version.
VERSION = "1.8.0"
GITHUB_URL = "https://github.com/mbektic/Simple-SESH-Sumary/blob/main/CHANGELOG.md"


def ms_to_hms(ms):
    seconds = ms // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    milliseconds = ms - (hours * 60 * 60 * 1000) - (minutes * 60 * 1000) - (seconds * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02} {milliseconds:03}ms"


def print_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            contents = file.read()
    except UnicodeDecodeError:
        # If utf-8 fails, you can fall back to 'utf-8-sig' or another encoding like 'latin-1'
        with open(path, 'r', encoding='utf-8-sig') as file:
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


def count_plays_from_directory(config):
    yearly = defaultdict(lambda: {
        "artist_counts": defaultdict(int),
        "artist_time": defaultdict(int),
        "track_counts": defaultdict(int),
        "track_time": defaultdict(int),
        "album_counts": defaultdict(int),
        "album_time": defaultdict(int),
    })

    dates_set = set()
    first_ts = None
    first_entry = None
    last_ts = None
    last_entry = None
    artist_set = set()
    album_set = set()
    track_set = set()
    artist_tracks = defaultdict(set)
    daily_counts   = Counter()
    monthly_counts = Counter()
    weekday_counts = Counter()
    hour_counts = Counter()


    MIN_MILLISECONDS = config.MIN_MILLISECONDS
    input_dir = config.INPUT_DIR
    output_html = config.OUTPUT_FILE + ".html"
    ITEMS_PER_PAGE = config.ITEMS_PER_PAGE

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
            if entry.get("ms_played") is not None and entry["ms_played"] > 0:
                if entry.get("master_metadata_album_artist_name"):
                    artist = entry.get("master_metadata_album_artist_name")
                    track = entry.get("master_metadata_track_name") + " - " + artist
                    album = entry.get("master_metadata_album_album_name") + " - " + artist

                    year = datetime.fromisoformat(entry["ts"].replace("Z", "+00:00")).year
                    y = yearly[year]

                    # ─── update stats info ─────────────────────────────────
                    dt = datetime.fromisoformat(entry["ts"].replace("Z", "+00:00"))
                    dates_set.add(dt.date())
                    if first_ts is None or dt < first_ts:
                        first_ts = dt
                        first_entry = entry
                    if last_ts is None or dt > last_ts:
                        last_ts = dt
                        last_entry = entry

                    if entry["ms_played"] > MIN_MILLISECONDS:
                        daily_counts[dt.date()] += 1
                        monthly_counts[(dt.year, dt.month)] += 1
                        weekday_counts[dt.weekday()] += 1
                        hour_counts[dt.hour]        += 1

                    artist_set.add(artist)
                    track_set.add(track)
                    album_set.add(album)
                    artist_tracks[artist].add(track)
                    # ───────────────────────────────────────────────────────────

                    if artist:
                        if entry.get("ms_played") > MIN_MILLISECONDS:
                            y["artist_counts"][artist] += 1
                        y["artist_time"][artist] += entry["ms_played"]
                    if track:
                        if entry.get("ms_played") > MIN_MILLISECONDS:
                            y["track_counts"][track] += 1
                        y["track_time"][track] += entry["ms_played"]
                    if album:
                        if entry.get("ms_played") > MIN_MILLISECONDS:
                            y["album_counts"][album] += 1
                        y["album_time"][album] += entry["ms_played"]

    def generate_js():
        return """<script>
        const ITEMS_PER_PAGE =  """ + str(ITEMS_PER_PAGE) + """
        """ + print_file("scripts/scripts.js") + """
        </script>"""

    def build_table(title, playtime_counts, playcount_counts, table_id):
        clean_title = title[2:]  # Remove emoji
        mode_string_playtime = "Playtime H:M:S ms"
        mode_string_playcount = "Plays"

        # Playtime rows
        playtime_rows = "\n".join(
            f"<tr><td>{rank}</td><td>{name}</td><td>{ms_to_hms(count)}</td></tr>"
            for rank, (name, count) in
            enumerate(sorted(playtime_counts.items(), key=lambda x: x[1], reverse=True), start=1)
        )

        # Play count rows
        playcount_rows = "\n".join(
            f"<tr><td>{rank}</td><td>{name}</td><td>{count}</td></tr>"
            for rank, (name, count) in
            enumerate(sorted(playcount_counts.items(), key=lambda x: x[1], reverse=True), start=1)
        )

        return f"""
        <h2>{title}</h2>
        <input type="text" id="{table_id}-search" placeholder="Search for {clean_title}..." class="search-input" />

        <div id="{table_id}-playcount" style="display: none;">
            <table>
                <thead><tr><th>Rank</th><th>{clean_title}</th><th>{mode_string_playcount}</th></tr></thead>
                <tbody>{playcount_rows}</tbody>
            </table>
        </div>

        <div id="{table_id}-playtime">
            <table>
                <thead><tr><th>Rank</th><th>{clean_title}</th><th>{mode_string_playtime}</th></tr></thead>
                <tbody>{playtime_rows}</tbody>
            </table>
        </div>

        <div class="pagination" id="{table_id}-nav"></div>
        """

    years = sorted(yearly.keys())
    tabs = '<button class="year-tab active" data-year="all">All</button>' + "".join(
        f'<button class="year-tab" data-year="{yr}">{yr}</button>'
        for yr in years
    )
    sections = ""

    all_data = {
        "artist_counts": defaultdict(int),
        "artist_time": defaultdict(int),
        "track_counts": defaultdict(int),
        "track_time": defaultdict(int),
        "album_counts": defaultdict(int),
        "album_time": defaultdict(int),
    }
    for ydata in yearly.values():
        for key in ["artist_counts", "track_counts", "album_counts"]:
            for name, cnt in ydata[key].items():
                all_data[key][name] += cnt
        for key in ["artist_time", "track_time", "album_time"]:
            for name, t in ydata[key].items():
                all_data[key][name] += t

    # “All” section
    sections += '<div class="year-section" id="year-all" style="display: block;">'
    sections += build_table("🎤 Artists",
                            all_data["artist_time"], all_data["artist_counts"],
                            "artist-table-all")
    sections += build_table("🎶 Tracks",
                            all_data["track_time"], all_data["track_counts"],
                            "track-table-all")
    sections += build_table("💿 Albums",
                            all_data["album_time"], all_data["album_counts"],
                            "album-table-all")
    sections += "</div>"

    # per-year sections
    for yr in years:
        style = "none"
        sections += f'<div class="year-section" id="year-{yr}" style="display: {style};">'
        sections += build_table("🎤 Artists",
                                yearly[yr]["artist_time"], yearly[yr]["artist_counts"],
                                f"artist-table-{yr}")
        sections += build_table("🎶 Tracks",
                                yearly[yr]["track_time"], yearly[yr]["track_counts"],
                                f"track-table-{yr}")
        sections += build_table("💿 Albums",
                                yearly[yr]["album_time"], yearly[yr]["album_counts"],
                                f"album-table-{yr}")
        sections += "</div>"

        # ─── compute overall stats ───────────────────────────────────────────
        today = date.today()
        days_since_first = (today - first_ts.date()).days
        days_played = len(dates_set)
        pct_days = days_played / days_since_first * 100

        first_str = first_ts.strftime("%b %d, %Y")
        first_desc = f"{first_str} ({first_entry['master_metadata_album_artist_name']} - {first_entry['master_metadata_track_name']})"
        last_str = last_ts.strftime("%b %d, %Y")
        last_desc = f"{last_str} ({last_entry['master_metadata_album_artist_name']} - {last_entry['master_metadata_track_name']})"

        artists_count = len(artist_set)
        one_hits = sum(1 for a, ts in artist_tracks.items() if len(ts) == 1)
        pct_one_hits = one_hits / artists_count * 100

        # artists present in every year
        year_artist_sets = [
            set(ydata["artist_counts"].keys()) | set(ydata["artist_time"].keys())
            for ydata in yearly.values()
        ]
        every_year_list = sorted(set.intersection(*year_artist_sets))
        every_year_count = len(every_year_list)

        albums_count = len(album_set)
        albums_per_artist = albums_count / artists_count
        tracks_count = len(track_set)

        counts = sorted(daily_counts.values(), reverse=True)
        edd = next((i for i, n in enumerate(counts, start=1) if n < i), len(counts))
        next_need = max(0, (edd + 1) - sum(1 for c in counts if c >= edd + 1))

        # ─── Artist cut-over point ────────────────────────────────
        art_vals = sorted(all_data["artist_counts"].values(), reverse=True)
        art_cut = next((i for i, n in enumerate(art_vals, start=1) if n < i), len(art_vals))

        # ─── Most popular year & month ─────────────────────────────
        year_plays = {y: sum(d["track_counts"].values()) for y, d in yearly.items()}
        pop_year, pop_year_plays = max(year_plays.items(), key=lambda kv: kv[1])

        (pm_y, pm_m), pop_mon_plays = max(monthly_counts.items(), key=lambda kv: kv[1])
        pop_mon_str = f"{calendar.month_name[pm_m]} {pm_y}"

        # — Longest Listening Streak (with date range) —
        from datetime import timedelta

        sorted_dates = sorted(dates_set)
        # initialize
        max_streak = curr_streak = 1
        streak_start = streak_end = sorted_dates[0]
        temp_start = sorted_dates[0]

        for prev_day, next_day in zip(sorted_dates, sorted_dates[1:]):
            if next_day == prev_day + timedelta(days=1):
                curr_streak += 1
            else:
                curr_streak = 1
                temp_start = next_day
            # record a new max
            if curr_streak > max_streak:
                max_streak = curr_streak
                streak_start = temp_start
                streak_end = next_day

        # — Average Plays per Active Day —
        avg_plays = sum(daily_counts.values()) / len(dates_set)

        # — Most Active Weekday —
        wd_index, wd_count = weekday_counts.most_common(1)[0]
        wd_name = calendar.day_name[wd_index]

        # — Peak Listening Hour —
        peak_hour, hour_count = hour_counts.most_common(1)[0]
        hour12 = peak_hour % 12 or 12
        suffix = "AM" if peak_hour < 12 else "PM"
        peak_hour_str = f"{hour12}{suffix}"

        # ─── rebuild stats_html ────────────────────────────────────
        stats_html = f"""
        <h2>Stats</h2>
        <div id="stats">
          <div class="stats-group">
            <h3>General</h3>
            <ul>
              <li>Days since first play: {days_since_first}</li>
              <li>Days played: {days_played} ({pct_days:.2f}%)</li>
              <li>First play: {first_desc}</li>
              <li>Last play: {last_desc}</li>
            </ul>
          </div>
        
          <div class="stats-group">
            <h3>Your Library</h3>
            <ul>
              <li>Artists: {artists_count}</li>
              <li>One hit wonders: {one_hits} ({pct_one_hits:.2f}%)</li>
              <li>
                Every-year artists: {every_year_count}
                <button id="show-every-year-btn" class="stats-button">Show</button>
              </li>
              <li>Albums: {albums_count}</li>
              <li>Albums per artist: {albums_per_artist:.1f}</li>
              <li>Tracks: {tracks_count}</li>
            </ul>
          </div>
        
          <div class="stats-group">
            <h3>Milestones</h3>
            <ul>
              <li>Eddington number: {edd}
                 <button class="info-button"
                         data-info="This means you have {edd} days with at least {edd} plays.">ℹ️</button>
              </li>
              <li>Days to next Eddington ({edd+1}): {next_need}</li>
              <li>Artist cut-over point: {art_cut}
                 <button class="info-button"
                         data-info="This means you have {art_cut} artists with at least {art_cut} plays.">ℹ️</button>
              </li>
              <li>Most popular year: {pop_year} ({pop_year_plays} plays)</li>
              <li>Most popular month: {pop_mon_str} ({pop_mon_plays} plays)</li>
            </ul>
          </div>
        
          <div class="stats-group">
            <h3>Listening Patterns</h3>
            <ul>
              <li>Longest listening streak: {max_streak} days
                  ({streak_start.strftime("%b %d, %Y")} – {streak_end.strftime("%b %d, %Y")})
              </li>
              <li>Average plays per active day: {avg_plays:.2f}</li>
              <li>Most active weekday: {wd_name} ({wd_count} plays)</li>
              <li>Peak listening hour: {peak_hour_str} ({hour_count} plays)</li>
            </ul>
          </div>
        </div>

        <!-- Info modal -->
        <div id="info-modal" class="modal-overlay" style="display:none;">
          <div class="modal-content">
            <div class="modal-header">
                <h2 id="info-modal-text"></h2>
                <span id="close-info-modal" class="close-button">&times;</span>
            </div>
          </div>
        </div>
        
         <!-- hidden modal -->
        <div id="every-year-modal" class="modal-overlay" style="display:none;">
          <div class="modal-content">
            <div class="modal-header">
                <h2>Artists played every year({every_year_count})</h2>
                <span id="close-every-year-modal" class="close-button">&times;</span>
            </div>
            <ul style="list-style:none; padding:0; margin-top:1em; max-height:60vh; overflow:auto;">
              {"".join(f"<li>{a}</li>" for a in every_year_list)}
            </ul>
          </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Spotify Summary</title>
        {print_styles()}
        {generate_js()}
    </head>
    <body>
        {print_file("html/title_bar.html")}
        
        <div id="year-tabs">{tabs}</div>
        {sections}
        {stats_html}
        
        {print_file("html/settings_modal.html")}
    </body>
    <footer>
      <a id="version-link" href="{GITHUB_URL}">Version: {VERSION}</a>
    </footer>
    </html>
    """

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ HTML report generated: {output_html}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'true':
        config = load_config()
        count_plays_from_directory(config)
    else:
        root = tk.Tk()
        app = ConfigApp(root)
        load_style(root)
        root.mainloop()
