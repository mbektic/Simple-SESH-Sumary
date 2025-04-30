import calendar
import json
import logging
import sys
from collections import defaultdict, Counter
from datetime import datetime, date, timedelta
from typing import Dict, List, Any

from Gui import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# The script version. You can check the changelog at the GitHub URL to see if there is a new version.
VERSION = "1.10.0"
GITHUB_URL = "https://github.com/mbektic/Simple-SESH-Sumary/blob/main/CHANGELOG.md"


def ms_to_hms(ms: int) -> str:
    """
    Convert milliseconds to a formatted hours:minutes:seconds milliseconds string.

    Args:
        ms (int): Milliseconds to convert

    Returns:
        str: Formatted string in the format "HH:MM:SS MSSms"
    """
    seconds = ms // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    milliseconds = ms - (hours * 60 * 60 * 1000) - (minutes * 60 * 1000) - (seconds * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02} {milliseconds:03}ms"


def print_file(path: str) -> str:
    """
    Read and return the contents of a file.

    Args:
        path (str): Path to the file to read

    Returns:
        str: Contents of the file

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read due to permission issues
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            contents = file.read()
    except UnicodeDecodeError:
        # If utf-8 fails, you can fall back to 'utf-8-sig' or another encoding like 'latin-1'
        try:
            with open(path, 'r', encoding='utf-8-sig') as file:
                contents = file.read()
        except UnicodeDecodeError:
            # If utf-8-sig also fails, try latin-1 as a last resort
            logging.warning(f"Failed to decode {path} with utf-8 and utf-8-sig, trying latin-1")
            with open(path, 'r', encoding='latin-1') as file:
                contents = file.read()
    except (FileNotFoundError, PermissionError) as e:
        logging.error(f"Error reading file {path}: {e}")
        raise
    return contents


def escape_js_string(s: str) -> str:
    """
    Escape special characters in a string for use in JavaScript template literals.

    Args:
        s (str): The string to escape

    Returns:
        str: The escaped string
    """
    return s.replace("\\", "\\\\").replace("`", "\\`")


def validate_spotify_json(data: List[Dict[str, Any]]) -> bool:
    """
    Validate the structure of Spotify streaming history JSON data.

    Args:
        data (List[Dict[str, Any]]): The parsed JSON data to validate

    Returns:
        bool: True if the data is valid, False otherwise

    Raises:
        ValueError: If the data is not a list or is empty
    """
    if not isinstance(data, list):
        raise ValueError("Spotify data must be a list of entries")

    if not data:
        logging.warning("Spotify data is empty")
        return False

    # Check a sample of entries (first 10 or all if less than 10)
    sample_size = min(10, len(data))
    sample = data[:sample_size]

    required_fields = ['ts', 'ms_played']
    optional_metadata_fields = [
        'master_metadata_album_artist_name',
        'master_metadata_track_name',
        'master_metadata_album_album_name'
    ]

    valid_entries = 0

    for entry in sample:
        if not isinstance(entry, dict):
            continue

        # Check required fields
        if all(field in entry for field in required_fields):
            valid_entries += 1

    # If at least 70% of the sample entries are valid, consider the data valid
    return (valid_entries / sample_size) >= 0.7


def print_styles() -> str:
    """
    Read CSS files and return HTML style tags with the CSS content.

    Returns:
        str: HTML style tags and JavaScript constants with CSS content

    Raises:
        FileNotFoundError: If any of the CSS files cannot be found
    """
    try:
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
    except Exception as e:
        logging.error(f"Error loading CSS files: {e}")
        raise


def count_plays_from_directory(config: Any) -> None:
    """
    Process Spotify streaming history JSON files and generate an HTML summary report.

    Args:
        config: Configuration object with attributes:
            - MIN_MILLISECONDS: Minimum milliseconds for a play to count
            - INPUT_DIR: Directory containing JSON files
            - OUTPUT_FILE: Base name for the output HTML file
            - ITEMS_PER_PAGE: Number of items per page in the HTML tables

    Returns:
        None

    Raises:
        FileNotFoundError: If the input directory does not exist
        PermissionError: If files cannot be read or written due to permission issues
    """
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
    daily_counts = Counter()
    monthly_counts = Counter()
    weekday_counts = Counter()
    hour_counts = Counter()
    play_times = []
    play_counted = 0
    skip_count = 0
    offline_count = 0
    track_skip_counts = Counter()

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
        logging.warning("⚠️ No JSON files found in the directory.")
        return

    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate the JSON data structure
            if not validate_spotify_json(data):
                logging.warning(f"⚠️ File {file} has invalid data structure, skipping")
                continue

        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"⚠️ Error reading {file}: {e}")
            continue
        except ValueError as e:
            logging.error(f"⚠️ Invalid data format in {file}: {e}")
            continue

        for entry in data:
            try:
                # Skip entries with no play time or missing required fields
                if not entry.get("ms_played") or entry["ms_played"] <= 0:
                    continue

                # Skip entries with missing timestamp
                if "ts" not in entry:
                    logging.warning(f"Entry missing timestamp, skipping: {entry.get('master_metadata_track_name', 'Unknown track')}")
                    continue

                # Process entries with artist information
                if entry.get("master_metadata_album_artist_name"):
                    # Get artist name or use fallback
                    artist = entry.get("master_metadata_album_artist_name", "Unknown Artist")

                    # Handle missing track or album names gracefully
                    track_name = entry.get("master_metadata_track_name", "Unknown Track")
                    album_name = entry.get("master_metadata_album_album_name", "Unknown Album")

                    # Create full track and album identifiers
                    track = f"{track_name} - {artist}"
                    album = f"{album_name} - {artist}"

                    # Parse timestamp with error handling
                    try:
                        dt = datetime.fromisoformat(entry["ts"].replace("Z", "+00:00"))
                        year = dt.year
                    except (ValueError, TypeError) as e:
                        logging.warning(f"Invalid timestamp format in entry, using current year: {e}")
                        dt = datetime.now()
                        year = dt.year

                    y = yearly[year]

                    # ─── update stats info ─────────────────────────────────
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
                        hour_counts[dt.hour] += 1
                        play_times.append(dt)
                        play_counted += 1
                        if entry.get("offline"):
                            offline_count += 1

                    if entry.get("skipped"):
                        skip_count += 1
                        track_skip_counts[track] += 1

                    artist_set.add(artist)
                    track_set.add(track)
                    album_set.add(album)
                    artist_tracks[artist].add(track)
                    # ───────────────────────────────────────────────────────────

                    # Update counts and times
                    if entry.get("ms_played") > MIN_MILLISECONDS:
                        y["artist_counts"][artist] += 1
                        y["track_counts"][track] += 1
                        y["album_counts"][album] += 1

                    # Update play times
                    y["artist_time"][artist] += entry["ms_played"]
                    y["track_time"][track] += entry["ms_played"]
                    y["album_time"][album] += entry["ms_played"]
            except Exception as e:
                # Catch any unexpected errors during entry processing
                logging.error(f"Error processing entry: {e}")
                continue

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
    tabs = '<button class="year-tab active" data-year="all" role="tab" aria-selected="true" aria-controls="year-all">All</button>' + "".join(
        f'<button class="year-tab" data-year="{yr}" role="tab" aria-selected="false" aria-controls="year-{yr}">{yr}</button>'
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
        try:
            today = date.today()

            # Handle case where no valid entries were found
            if first_ts is None:
                logging.warning("No valid entries found with timestamps, using default values for stats")
                days_since_first = 0
                days_played = 0
                pct_days = 0
                first_str = "N/A"
                first_desc = "No data available"
                last_str = "N/A"
                last_desc = "No data available"
            else:
                days_since_first = (today - first_ts.date()).days
                days_played = len(dates_set)
                pct_days = days_played / days_since_first * 100 if days_since_first > 0 else 0

                # Format first entry details with fallbacks for missing data
                first_str = first_ts.strftime("%b %d, %Y")
                first_artist = first_entry.get('master_metadata_album_artist_name', 'Unknown Artist')
                first_track = first_entry.get('master_metadata_track_name', 'Unknown Track')
                first_desc = f"{first_str} ({first_artist} - {first_track})"

                # Format last entry details with fallbacks for missing data
                last_str = last_ts.strftime("%b %d, %Y")
                last_artist = last_entry.get('master_metadata_album_artist_name', 'Unknown Artist')
                last_track = last_entry.get('master_metadata_track_name', 'Unknown Track')
                last_desc = f"{last_str} ({last_artist} - {last_track})"
        except Exception as e:
            logging.error(f"Error computing basic stats: {e}")
            days_since_first = 0
            days_played = 0
            pct_days = 0
            first_str = "Error"
            first_desc = "Error computing stats"
            last_str = "Error"
            last_desc = "Error computing stats"

        try:
            # Calculate artist statistics with error handling
            artists_count = len(artist_set)
            if artists_count > 0:
                one_hits = sum(1 for a, ts in artist_tracks.items() if len(ts) == 1)
                pct_one_hits = one_hits / artists_count * 100
            else:
                logging.warning("No artists found, using default values for artist stats")
                one_hits = 0
                pct_one_hits = 0

            # Calculate artists present in every year with error handling
            if yearly:
                try:
                    year_artist_sets = [
                        set(ydata["artist_counts"].keys()) | set(ydata["artist_time"].keys())
                        for ydata in yearly.values()
                    ]
                    if year_artist_sets:
                        every_year_list = sorted(set.intersection(*year_artist_sets))
                        every_year_count = len(every_year_list)
                    else:
                        every_year_list = []
                        every_year_count = 0
                except Exception as e:
                    logging.error(f"Error computing every-year artists: {e}")
                    every_year_list = []
                    every_year_count = 0
            else:
                every_year_list = []
                every_year_count = 0

            # Calculate album and track statistics with error handling
            albums_count = len(album_set)
            tracks_count = len(track_set)

            # Avoid division by zero
            if artists_count > 0:
                albums_per_artist = albums_count / artists_count
            else:
                albums_per_artist = 0
        except Exception as e:
            logging.error(f"Error computing library stats: {e}")
            artists_count = 0
            one_hits = 0
            pct_one_hits = 0
            every_year_list = []
            every_year_count = 0
            albums_count = 0
            albums_per_artist = 0
            tracks_count = 0

        try:
            # Calculate Eddington number with error handling
            counts = sorted(daily_counts.values(), reverse=True)
            if counts:
                edd = next((i for i, n in enumerate(counts, start=1) if n < i), len(counts))
                next_need = max(0, (edd + 1) - sum(1 for c in counts if c >= edd + 1))
            else:
                logging.warning("No daily counts found, using default values for Eddington number")
                edd = 0
                next_need = 0

            # ─── Artist cut-over point ────────────────────────────────
            try:
                art_vals = sorted(all_data["artist_counts"].values(), reverse=True)
                if art_vals:
                    art_cut = next((i for i, n in enumerate(art_vals, start=1) if n < i), len(art_vals))
                else:
                    art_cut = 0
            except Exception as e:
                logging.error(f"Error computing artist cut-over point: {e}")
                art_cut = 0

            # ─── Most popular year/month/week/dau ─────────────────────────────
            # Most popular year
            try:
                if yearly:
                    year_plays = {y: sum(d["track_counts"].values()) for y, d in yearly.items()}
                    if year_plays:
                        pop_year, pop_year_plays = max(year_plays.items(), key=lambda kv: kv[1])
                    else:
                        pop_year, pop_year_plays = "N/A", 0
                else:
                    pop_year, pop_year_plays = "N/A", 0
            except Exception as e:
                logging.error(f"Error computing most popular year: {e}")
                pop_year, pop_year_plays = "N/A", 0

            # Most popular month
            try:
                if monthly_counts:
                    (pm_y, pm_m), pop_mon_plays = max(monthly_counts.items(), key=lambda kv: kv[1])
                    pop_mon_str = f"{calendar.month_name[pm_m]} {pm_y}"
                else:
                    pop_mon_str, pop_mon_plays = "N/A", 0
            except Exception as e:
                logging.error(f"Error computing most popular month: {e}")
                pop_mon_str, pop_mon_plays = "N/A", 0

            # Most popular week
            try:
                weekly_counts = Counter()
                for d, cnt in daily_counts.items():
                    # d.isocalendar() → (year, weeknumber, weekday)
                    yr, wk, _ = d.isocalendar()
                    weekly_counts[(yr, wk)] += cnt

                if weekly_counts:
                    (wy, ww), week_plays = weekly_counts.most_common(1)[0]
                    week_start = datetime.strptime(f"{wy}-W{ww}-1", "%G-W%V-%u").date()
                    week_end = week_start + timedelta(days=6)
                    week_str = f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"
                else:
                    week_str, week_plays = "N/A", 0
            except Exception as e:
                logging.error(f"Error computing most popular week: {e}")
                week_str, week_plays = "N/A", 0

            # — Most popular day (single date) —
            try:
                if daily_counts:
                    most_day, day_plays = daily_counts.most_common(1)[0]
                    day_str = most_day.strftime("%b %d, %Y")
                else:
                    day_str, day_plays = "N/A", 0
            except Exception as e:
                logging.error(f"Error computing most popular day: {e}")
                day_str, day_plays = "N/A", 0
        except Exception as e:
            logging.error(f"Error computing milestone stats: {e}")
            edd = 0
            next_need = 0
            art_cut = 0
            pop_year, pop_year_plays = "N/A", 0
            pop_mon_str, pop_mon_plays = "N/A", 0
            week_str, week_plays = "N/A", 0
            day_str, day_plays = "N/A", 0

        # — Longest Listening Streak (with date range) —
        try:
            sorted_dates = sorted(dates_set)
            if sorted_dates:
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
            else:
                logging.warning("No dates found, using default values for streak stats")
                max_streak = 0
                streak_start = streak_end = None
        except Exception as e:
            logging.error(f"Error computing listening streak: {e}")
            max_streak = 0
            streak_start = streak_end = None

        # — Average Plays per Active Day —
        try:
            if dates_set:
                avg_plays = sum(daily_counts.values()) / len(dates_set)
            else:
                avg_plays = 0
        except Exception as e:
            logging.error(f"Error computing average plays per day: {e}")
            avg_plays = 0

        # — Most Active Weekday —
        try:
            if weekday_counts:
                wd_index, wd_count = weekday_counts.most_common(1)[0]
                wd_name = calendar.day_name[wd_index]
            else:
                wd_name, wd_count = "N/A", 0
        except Exception as e:
            logging.error(f"Error computing most active weekday: {e}")
            wd_name, wd_count = "N/A", 0

        # — Peak Listening Hour —
        try:
            if hour_counts:
                peak_hour, hour_count = hour_counts.most_common(1)[0]
                hour12 = peak_hour % 12 or 12
                suffix = "AM" if peak_hour < 12 else "PM"
                peak_hour_str = f"{hour12}{suffix}"
            else:
                peak_hour_str, hour_count = "N/A", 0
        except Exception as e:
            logging.error(f"Error computing peak listening hour: {e}")
            peak_hour_str, hour_count = "N/A", 0

        # ─── Unique Tracks Ratio ───────────────────────────────────
        try:
            total_plays = sum(all_data["track_counts"].values())
            unique_tracks = len(track_set)
            if total_plays > 0:
                unique_ratio_pct = unique_tracks / total_plays * 100
            else:
                unique_ratio_pct = 0
        except Exception as e:
            logging.error(f"Error computing unique tracks ratio: {e}")
            total_plays = 0
            unique_tracks = 0
            unique_ratio_pct = 0

        # ─── Gini Coefficient of Artist Plays ─────────────────────
        try:
            vals = sorted(all_data["artist_counts"].values())
            n = len(vals)
            if n and sum(vals):
                weighted = sum((i + 1) * v for i, v in enumerate(vals))
                gini = (2 * weighted) / (n * sum(vals)) - (n + 1) / n
            else:
                gini = 0
        except Exception as e:
            logging.error(f"Error computing Gini coefficient: {e}")
            gini = 0

        # ─── Weekend vs Weekday Ratio ────────────────────────────
        try:
            weekend = weekday_counts[5] + weekday_counts[6]  # Sat=5, Sun=6
            weekday = sum(weekday_counts[i] for i in range(5))
            ratio_pct = weekend / weekday * 100 if weekday else 0
        except Exception as e:
            logging.error(f"Error computing weekend vs weekday ratio: {e}")
            weekend = 0
            weekday = 0
            ratio_pct = 0

        # ─── Listening session stats ───────────────────────────
        try:
            play_times.sort()
            sessions = []
            if play_times:
                start = prev = play_times[0]
                gap = timedelta(minutes=30)
                for t in play_times[1:]:
                    if t - prev > gap:
                        sessions.append((start, prev))
                        start = t
                    prev = t
                sessions.append((start, prev))

            num_sessions = len(sessions)
            durations = [(end - start) for start, end in sessions]
            total_dur = sum(durations, timedelta())
            avg_session = total_dur / num_sessions if num_sessions else timedelta()

            if durations:
                # find the longest session and its start
                longest_dur = max(durations)
                idx = durations.index(longest_dur)
                longest_start, longest_end = sessions[idx]
            else:
                longest_dur = timedelta()
                longest_start = longest_end = None

            # format durations
            avg_str = ms_to_hms(int(avg_session.total_seconds() * 1000))
            avg_str = avg_str[:-6]
            long_str = ms_to_hms(int(longest_dur.total_seconds() * 1000))
            long_str = long_str[:-6]
            # format date for the longest session
            if longest_start:
                long_date_str = longest_start.strftime("%b %d, %Y")
            else:
                long_date_str = "N/A"
        except Exception as e:
            logging.error(f"Error computing listening session stats: {e}")
            num_sessions = 0
            avg_str = "00:00:00"
            long_str = "00:00:00"
            long_date_str = "N/A"

        # ─── Skip rate and offline/online ratio ─────────────────────
        try:
            if play_counted > 0:
                online_count = play_counted - offline_count
                skip_rate_pct = (skip_count / play_counted * 100)
                offline_ratio_pct = (offline_count / play_counted * 100)
                ratio_str = f"{offline_count}:{online_count}"
            else:
                online_count = 0
                skip_rate_pct = 0
                offline_ratio_pct = 0
                ratio_str = "0:0"
        except Exception as e:
            logging.error(f"Error computing skip rate and offline ratio: {e}")
            online_count = 0
            skip_rate_pct = 0
            offline_ratio_pct = 0
            ratio_str = "0:0"

        # ─── Total listening time and average per play ─────────────
        try:
            total_ms = sum(all_data["track_time"].values())
            total_plays = sum(all_data["track_counts"].values())
            total_time_str = ms_to_hms(total_ms)
            total_time_str = total_time_str[:-6]

            if total_plays > 0:
                avg_play_ms = total_ms / total_plays
                avg_play_str = ms_to_hms(int(avg_play_ms))
                avg_play_str = avg_play_str[:-6]
            else:
                avg_play_str = "00:00:00"
        except Exception as e:
            logging.error(f"Error computing total listening time: {e}")
            total_ms = 0
            total_plays = 0
            total_time_str = "00:00:00"
            avg_play_str = "00:00:00"

        # ─── Most skipped track ───────────────────────────────────
        try:
            if track_skip_counts:
                most_skipped, skip_ct = track_skip_counts.most_common(1)[0]
            else:
                most_skipped, skip_ct = "N/A", 0
        except Exception as e:
            logging.error(f"Error computing most skipped track: {e}")
            most_skipped, skip_ct = "N/A", 0

        # ─── Longest Hiatus ───────────────────────────────────────
        try:
            longest_hiatus = 0
            hiatus_start = hiatus_end = None

            # Only compute if we have enough dates
            if len(sorted_dates) > 1:
                for prev_day, next_day in zip(sorted_dates, sorted_dates[1:]):
                    gap = (next_day - prev_day).days - 1
                    if gap > longest_hiatus:
                        longest_hiatus = gap
                        hiatus_start = prev_day + timedelta(days=1)
                        hiatus_end = next_day - timedelta(days=1)

                if longest_hiatus > 0:
                    hi_start_str = hiatus_start.strftime("%b %d, %Y")
                    hi_end_str = hiatus_end.strftime("%b %d, %Y")
                else:
                    hi_start_str = hi_end_str = None
            else:
                hi_start_str = hi_end_str = None
        except Exception as e:
            logging.error(f"Error computing longest hiatus: {e}")
            longest_hiatus = 0
            hi_start_str = hi_end_str = None

        # ─── rebuild stats_html ────────────────────────────────────
        stats_html = f"""
        <h2>Stats</h2>
        <div id="stats">
          <!-- 1. Overview & Time -->
          <div class="stats-group">
            <h3>Overview & Time</h3>
            <ul>
              <li>Days since first play: {days_since_first}</li>
              <li>Days played: {days_played} ({pct_days:.2f}%)</li>
              <li>First play: {first_desc}</li>
              <li>Last play: {last_desc}</li>
              <li>Total play: {total_plays}</li>
              <li>Total listening time: {total_time_str}</li>
              <li>Average playtime per play: {avg_play_str}</li>
            </ul>
          </div>

          <!-- 2. Library Stats -->
          <div class="stats-group">
            <h3>Library</h3>
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
              <li>Unique tracks ratio: {unique_tracks}/{total_plays} ({unique_ratio_pct:.2f}%)
                <button class="info-button stats-button" data-info="Unique Tracks ÷ Total Plays × 100">i</button>
              </li>
              <li>Gini coefficient: {gini:.3f}
                <button class="info-button stats-button" 
                        data-info="How evenly you spread listens across artists (0 = perfectly even, 1 = one artist).">i</button>
              </li>
            </ul>
          </div>

          <!-- 3. Milestones -->
          <div class="stats-group">
            <h3>Milestones</h3>
            <ul>
              <li>Eddington number: {edd}
                 <button class="info-button stats-button"
                         data-info="This means you have {edd} days with at least {edd} plays.">i</button>
              </li>
              <li>Days to next Eddington ({edd+1}): {next_need}</li>
              <li>Artist cut-over point: {art_cut}
                 <button class="info-button stats-button"
                         data-info="This means you have {art_cut} artists with at least {art_cut} plays.">i</button>
              </li>
            </ul>
          </div>

          <!-- 4. Popularity Records -->
          <div class="stats-group">
            <h3>Popularity</h3>
            <ul>
              <li>Most popular year: {pop_year} ({pop_year_plays} plays)</li>
              <li>Most popular month: {pop_mon_str} ({pop_mon_plays} plays)</li>
              <li>Most popular week: {week_str} ({week_plays} plays)</li>
              <li>Most popular day: {day_str} ({day_plays} plays)</li>
              <li>Most skipped track: {most_skipped} ({skip_ct} skips)</li>
            </ul>
          </div>

          <!-- 5. Listening Patterns -->
          <div class="stats-group">
            <h3>Patterns</h3>
            <ul>
              <li>Longest listening streak: {max_streak} days
                 ({streak_start.strftime("%b %d, %Y")} – {streak_end.strftime("%b %d, %Y")})
              </li>
              <li>Longest hiatus: {longest_hiatus} days
                 {f"({hi_start_str} – {hi_end_str})" if longest_hiatus>0 else ""}
              </li>
              <li>Average plays per active day: {avg_plays:.2f}</li>
              <li>Most active weekday: {wd_name} ({wd_count} plays)</li>
              <li>Peak listening hour: {peak_hour_str} ({hour_count} plays)</li>
              <li>Weekend vs Weekday plays: {weekend}/{weekday} ({ratio_pct:.2f}% weekend)</li>
            </ul>
          </div>

          <!-- 6. Sessions & Behavior -->
          <div class="stats-group">
            <h3>Sessions & Behavior</h3>
            <ul>
              <li>Number of sessions: {num_sessions}
                 <button class="info-button stats-button"
                         data-info="A “session” is consecutive plays with <30 min gaps.">i</button>
              </li>
              <li>Average session length: {avg_str}</li>
              <li>Longest single session: {long_str} on {long_date_str}</li>
              <li>Skip rate: {skip_count}/{play_counted} ({skip_rate_pct:.2f}%)</li>
              <li>Offline vs Online ratio: {ratio_str} ({offline_ratio_pct:.2f}% offline)</li>
            </ul>
          </div>
        </div>

        <!-- Info modal -->
        <div id="info-modal" class="modal-overlay" style="display:none;" role="dialog" aria-modal="true" aria-labelledby="info-modal-text" aria-hidden="true">
          <div class="modal-content">
            <div class="modal-header">
                <h2 id="info-modal-text"></h2>
                <button id="close-info-modal" class="close-button" aria-label="Close information">&times;</button>
            </div>
          </div>
        </div>

         <!-- hidden modal -->
        <div id="every-year-modal" class="modal-overlay" style="display:none;" role="dialog" aria-modal="true" aria-labelledby="every-year-title" aria-hidden="true">
          <div class="modal-content">
            <div class="modal-header">
                <h2 id="every-year-title">Artists played every year({every_year_count})</h2>
                <button id="close-every-year-modal" class="close-button" aria-label="Close artists list">&times;</button>
            </div>
            <ul style="list-style:none; padding:0; margin-top:1em; max-height:60vh; overflow:auto;" role="list" aria-label="Artists played every year">
              {"".join(f"<li>{a}</li>" for a in every_year_list)}
            </ul>
          </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html style='overflow: hidden;'>
    <head>
        <meta charset="UTF-8">
        <title>Spotify Summary</title>
        {print_styles()}
        {generate_js()}
    </head>
    <body style='overflow: hidden;'>
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

    try:
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"✅ HTML report generated: {output_html}")
    except (IOError, PermissionError) as e:
        logging.error(f"Failed to write HTML report to {output_html}: {e}")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'true':
        config = load_config()
        count_plays_from_directory(config)
    else:
        root = tk.Tk()
        app = ConfigApp(root)
        load_style(root)
        root.mainloop()
