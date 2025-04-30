"""
HTML generation module for Spotify Extended Streaming History.

This module contains functions for generating HTML content for the
Spotify Extended Streaming History summary report.
"""
import json
import logging
from typing import Dict, List, Any, DefaultDict

def ms_to_hms(ms: int) -> str:
    """
    Convert milliseconds to a formatted string hours:minutes:seconds milliseconds.

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

def escape_js_string(s: str) -> str:
    """
    Escape special characters in a string for use in JavaScript template literals.

    Args:
        s (str): The string to escape

    Returns:
        str: The escaped string
    """
    return s.replace("\\", "\\\\").replace("`", "\\`")

def print_file(path: str) -> str:
    """
    Read and return the contents of a file.

    Args:
        path (str): Path to the file to read

    Returns:
        str: Contents of the file

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read due to permission issues.
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

def generate_js(items_per_page: int) -> str:
    """
    Generate JavaScript for the HTML page.

    Args:
        items_per_page (int): Number of items per page in the HTML tables

    Returns:
        str: JavaScript code as a string
    """
    return f"""<script>
    const ITEMS_PER_PAGE = {items_per_page}
    {print_file("scripts/scripts.js")}
    </script>"""

def build_table(title: str, playtime_counts: Dict[str, int], playcount_counts: Dict[str, int], table_id: str) -> str:
    """
    Build HTML tables for artists, tracks, or albums.

    Args:
        title (str): Title of the table
        playtime_counts (Dict[str, int]): Dictionary mapping names to playtime in milliseconds
        playcount_counts (Dict[str, int]): Dictionary mapping names to play counts
        table_id (str): ID for the table

    Returns:
        str: HTML table as a string
    """
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

def build_year_tabs(years: List[int]) -> str:
    """
    Build HTML for year tabs.

    Args:
        years (List[int]): List of years

    Returns:
        str: HTML for year tabs as a string
    """
    return '<button class="year-tab active" data-year="all" role="tab" aria-selected="true" aria-controls="year-all">All</button>' + "".join(
        f'<button class="year-tab" data-year="{yr}" role="tab" aria-selected="false" aria-controls="year-{yr}">{yr}</button>'
        for yr in years
    )

def build_all_section(all_data: Dict[str, DefaultDict[str, int]]) -> str:
    """
    Build HTML for the "All" section with tables for artists, tracks, and albums.

    Args:
        all_data (Dict[str, DefaultDict[str, int]]): Aggregated data for all years

    Returns:
        str: HTML for the "All" section as a string
    """
    sections = '<div class="year-section" id="year-all" style="display: block;">'
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
    return sections

def build_year_sections(years: List[int], yearly: DefaultDict[int, Dict[str, DefaultDict[str, int]]]) -> str:
    """
    Build HTML for per-year sections with tables for artists, tracks, and albums.

    Args:
        years (List[int]): List of years
        yearly (DefaultDict[int, Dict[str, DefaultDict[str, int]]]): Dictionary of yearly statistics

    Returns:
        str: HTML for per-year sections as a string
    """
    sections = ""
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
    return sections

def build_stats_html(stats_data: Dict[str, Any], daily_counts: Dict[str, int]) -> str:
    """
    Build HTML for the statistics section.

    Args:
        stats_data (Dict[str, Any]): Dictionary containing statistics data

    Returns:
        str: HTML for the statistics section as a string
    """

    daily_counts_json = json.dumps({
        d.isoformat(): cnt
        for d, cnt in daily_counts.items()
    })
    first_date = stats_data.get('first_str', "")
    last_date  = stats_data.get('last_str', "")

    return f"""
    <h2>Stats</h2>
    <div id="stats">
      <!-- 1. Overview & Time -->
      <div class="stats-group">
        <h3>Overview & Time</h3>
        <ul>
          <li>Days since first play: {stats_data['days_since_first']}</li>
          <li>Days played: {stats_data['days_played']} ({stats_data['pct_days']:.2f}%)</li>
          <li>First play: {stats_data['first_desc']}</li>
          <li>Last play: {stats_data['last_desc']}</li>
          <li>Total play: {stats_data['total_plays']}</li>
          <li>Total listening time: {stats_data['total_time_str']}</li>
          <li>Average playtime per play: {stats_data['avg_play_str']}</li>
        </ul>
      </div>

      <!-- 2. Library Stats -->
      <div class="stats-group">
        <h3>Library</h3>
        <ul>
          <li>Artists: {stats_data['artists_count']}</li>
          <li>One hit wonders: {stats_data['one_hits']} ({stats_data['pct_one_hits']:.2f}%)</li>
          <li>
            Every-year artists: {stats_data['every_year_count']}
            <button id="show-every-year-btn" class="stats-button">Show</button>
          </li>
          <li>Albums: {stats_data['albums_count']}</li>
          <li>Albums per artist: {stats_data['albums_per_artist']:.1f}</li>
          <li>Tracks: {stats_data['tracks_count']}</li>
          <li>Unique tracks ratio: {stats_data['unique_tracks']}/{stats_data['total_plays']} ({stats_data['unique_ratio_pct']:.2f}%)
            <button class="info-button stats-button" data-info="Unique Tracks ÷ Total Plays × 100">i</button>
          </li>
          <li>Gini coefficient: {stats_data['gini']:.3f}
            <button class="info-button stats-button" 
                    data-info="How evenly you spread listens across artists (0 = perfectly even, 1 = one artist).">i</button>
          </li>
        </ul>
      </div>

      <!-- 3. Milestones -->
      <div class="stats-group">
        <h3>Milestones</h3>
        <ul>
          <li>Eddington number: {stats_data['edd']}
             <button class="info-button stats-button"
                     data-info="This means you have {stats_data['edd']} days with at least {stats_data['edd']} plays.">i</button>
          </li>
          <li>Days to next Eddington ({stats_data['edd']+1}): {stats_data['next_need']}</li>
          <li>Artist cut-over point: {stats_data['art_cut']}
             <button class="info-button stats-button"
                     data-info="This means you have {stats_data['art_cut']} artists with at least {stats_data['art_cut']} plays.">i</button>
          </li>
        </ul>
      </div>

      <!-- 4. Popularity Records -->
      <div class="stats-group">
        <h3>Popularity</h3>
        <ul>
          <li>Most popular year: {stats_data['pop_year']} ({stats_data['pop_year_plays']} plays)</li>
          <li>Most popular month: {stats_data['pop_mon_str']} ({stats_data['pop_mon_plays']} plays)</li>
          <li>Most popular week: {stats_data['week_str']} ({stats_data['week_plays']} plays)</li>
          <li>Most popular day: {stats_data['day_str']} ({stats_data['day_plays']} plays)</li>
          <li>Most skipped track: {stats_data['most_skipped']} ({stats_data['skip_ct']} skips)</li>
        </ul>
      </div>

      <!-- 5. Listening Patterns -->
      <div class="stats-group">
        <h3>Patterns</h3>
        <ul>
          <li>Longest listening streak: {stats_data['max_streak']} days
             ({stats_data['streak_start'].strftime("%b %d, %Y")} – {stats_data['streak_end'].strftime("%b %d, %Y")})
          </li>
          <li>Longest hiatus: {stats_data['longest_hiatus']} days
             {f"({stats_data['hi_start_str']} – {stats_data['hi_end_str']})" if stats_data['longest_hiatus']>0 else ""}
          </li>
          <li>Average plays per active day: {stats_data['avg_plays']:.2f}</li>
          <li>Most active weekday: {stats_data['wd_name']} ({stats_data['wd_count']} plays)</li>
          <li>Peak listening hour: {stats_data['peak_hour_str']} ({stats_data['hour_count']} plays)</li>
          <li>Weekend vs Weekday plays: {stats_data['weekend']}/{stats_data['weekday']} ({stats_data['ratio_pct']:.2f}% weekend)</li>
        </ul>
      </div>

      <!-- 6. Sessions & Behavior -->
      <div class="stats-group">
        <h3>Sessions & Behavior</h3>
        <ul>
          <li>Number of sessions: {stats_data['num_sessions']}
             <button class="info-button stats-button"
                     data-info='A "session" is consecutive plays with <30 min gaps.'>i</button>
          </li>
          <li>Average session length: {stats_data['avg_str']}</li>
          <li>Longest single session: {stats_data['long_str']} on {stats_data['long_date_str']}</li>
          <li>Skip rate: {stats_data['skip_count']}/{stats_data['play_counted']} ({stats_data['skip_rate_pct']:.2f}%)</li>
          <li>Offline vs Online ratio: {stats_data['ratio_str']} ({stats_data['offline_ratio_pct']:.2f}% offline)</li>
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
            <h2 id="every-year-title">Artists played every year({stats_data['every_year_count']})</h2>
            <button id="close-every-year-modal" class="close-button" aria-label="Close artists list">&times;</button>
        </div>
        <ul style="list-style:none; padding:0; margin-top:1em; max-height:60vh; overflow:auto;" role="list" aria-label="Artists played every year">
          {"".join(f"<li>{a}</li>" for a in stats_data['every_year_list'])}
        </ul>
      </div>
    </div>
    
      <div id="heatmap-holder" class="stats-group">
        <h3>Activity Heatmap</h3>
        <div id="calendar-heatmap"></div>
        <div class="heatmap-legend">
          <span>Less</span>
          <div class="heatmap-cell level-0"></div>
          <div class="heatmap-cell level-1"></div>
          <div class="heatmap-cell level-2"></div>
          <div class="heatmap-cell level-3"></div>
          <div class="heatmap-cell level-4"></div>
          <span>More</span>
        </div>
      </div>
    
      <script>
        const startDate = new Date("{first_date}");
        const endDate   = new Date("{last_date}");
        const counts = JSON.parse(`{daily_counts_json}`);
        {print_file("scripts/heatmap.js")}
      </script>
    """

def generate_html_content(tabs: str, sections: str, stats_html: str, items_per_page: int, github_url: str, version: str) -> str:
    """
    Generate the complete HTML content for the summary report.

    Args:
        tabs (str): HTML for year tabs
        sections (str): HTML for year sections
        stats_html (str): HTML for statistics
        items_per_page (int): Number of items per page in the HTML tables
        github_url (str): URL to the GitHub repository
        version (str): Version of the application

    Returns:
        str: Complete HTML content as a string
    """
    return f"""
    <!DOCTYPE html>
    <html style='overflow: hidden;'>
    <head>
        <meta charset="UTF-8">
        <title>Spotify Summary</title>
        {print_styles()}
        {generate_js(items_per_page)}
    </head>
    <body style='overflow: hidden;'>
        {print_file("html/title_bar.html")}

        <div id="year-tabs">{tabs}</div>
        {sections}
        {stats_html}

        {print_file("html/settings_modal.html")}
    </body>
    <footer>
      <a id="version-link" href="{github_url}">Version: {version}</a>
    </footer>
    </html>
    """

def write_html_to_file(html_content: str, output_file: str) -> None:
    """
    Write HTML content to a file.

    Args:
        html_content (str): HTML content to write
        output_file (str): Path to the output file

    Raises:
        IOError: If the file cannot be written
        PermissionError: If the file cannot be written due to permission issues
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"✅ HTML report generated: {output_file}")
    except (IOError, PermissionError) as e:
        logging.error(f"Failed to write HTML report to {output_file}: {e}")
        raise