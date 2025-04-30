"""
Generate HTML summary from Spotify Extended Streaming History.

This script generates an HTML summary report from Spotify Extended Streaming History
JSON files. It uses the data_processing, statistics, and html_generation modules
to process the data, calculate statistics, and generate the HTML report.
"""
import logging
import sys
from typing import Any

from Gui import *
from data_processing import load_spotify_data, process_spotify_data, aggregate_yearly_data
from html_generation import build_year_tabs, build_all_section, build_year_sections, build_stats_html, \
    generate_html_content, write_html_to_file
from statistics import calculate_all_stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# The script version. You can check the changelog at the GitHub URL to see if there is a new version.
VERSION = "1.11.0"
GITHUB_URL = "https://github.com/mbektic/Simple-SESH-Sumary/blob/main/CHANGELOG.md"


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
    MIN_MILLISECONDS = config.MIN_MILLISECONDS
    input_dir = config.INPUT_DIR
    output_html = config.OUTPUT_FILE + ".html"
    ITEMS_PER_PAGE = config.ITEMS_PER_PAGE

    # Load Spotify data from JSON files
    entries = load_spotify_data(input_dir)
    if not entries:
        logging.warning("No valid entries found in the input directory.")
        return

    # Process Spotify data
    (
        yearly, dates_set, first_ts, first_entry, last_ts, last_entry,
        artist_set, album_set, track_set, artist_tracks, daily_counts,
        monthly_counts, weekday_counts, hour_counts, play_times,
        play_counted, skip_count, offline_count, track_skip_counts
    ) = process_spotify_data(entries, MIN_MILLISECONDS)

    # Aggregate yearly data
    all_data = aggregate_yearly_data(yearly)

    # Calculate all statistics
    stats_data = calculate_all_stats(
        yearly, all_data, dates_set, first_ts, first_entry, last_ts, last_entry,
        artist_set, album_set, track_set, artist_tracks, daily_counts,
        monthly_counts, weekday_counts, hour_counts, play_times,
        play_counted, skip_count, offline_count, track_skip_counts
    )

    # Build HTML content
    years = sorted(yearly.keys())
    tabs = build_year_tabs(years)
    all_section = build_all_section(all_data)
    year_sections = build_year_sections(years, yearly)
    sections = all_section + year_sections
    stats_html = build_stats_html(stats_data)

    # Generate complete HTML content
    html_content = generate_html_content(
        tabs, sections, stats_html, ITEMS_PER_PAGE, GITHUB_URL, VERSION
    )

    # Write HTML content to file
    write_html_to_file(html_content, output_html)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'true':
        config = load_config()
        count_plays_from_directory(config)
    else:
        root = tk.Tk()
        app = ConfigApp(root)
        load_style(root)
        root.mainloop()