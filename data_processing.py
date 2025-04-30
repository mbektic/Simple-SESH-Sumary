"""
Data processing module for Spotify Extended Streaming History.

This module contains functions for loading, validating, and processing
Spotify Extended Streaming History data.
"""
import json
import logging
import os
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set, DefaultDict

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

def load_spotify_data(input_dir: str) -> List[Dict[str, Any]]:
    """
    Load Spotify streaming history data from JSON files in the specified directory.

    Args:
        input_dir (str): Directory containing JSON files

    Returns:
        List[Dict[str, Any]]: List of valid Spotify streaming history entries

    Raises:
        FileNotFoundError: If the input directory does not exist
    """
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist")

    json_files = [
        os.path.join(input_dir, filename)
        for filename in os.listdir(input_dir)
        if filename.endswith(".json")
    ]

    if not json_files:
        logging.warning("⚠️ No JSON files found in the directory.")
        return []

    all_entries = []

    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate the JSON data structure
            if not validate_spotify_json(data):
                logging.warning(f"⚠️ File {file} has invalid data structure, skipping")
                continue

            all_entries.extend(data)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"⚠️ Error reading {file}: {e}")
            continue
        except ValueError as e:
            logging.error(f"⚠️ Invalid data format in {file}: {e}")
            continue

    return all_entries

def process_spotify_data(entries: List[Dict[str, Any]], min_milliseconds: int) -> Tuple[
    DefaultDict[int, Dict[str, DefaultDict[str, int]]],
    Set[datetime.date],
    datetime,
    Dict[str, Any],
    datetime,
    Dict[str, Any],
    Set[str],
    Set[str],
    Set[str],
    DefaultDict[str, Set[str]],
    Counter,
    Counter,
    Counter,
    Counter,
    List[datetime],
    int,
    int,
    int,
    Counter
]:
    """
    Process Spotify streaming history entries and extract statistics.

    Args:
        entries (List[Dict[str, Any]]): List of Spotify streaming history entries
        min_milliseconds (int): Minimum milliseconds for a play to count

    Returns:
        Tuple containing various statistics:
            - yearly: Dictionary of yearly statistics
            - dates_set: Set of dates played
            - first_ts: First timestamp
            - first_entry: First entry
            - last_ts: Last timestamp
            - last_entry: Last entry
            - artist_set: Set of artists
            - album_set: Set of albums
            - track_set: Set of tracks
            - artist_tracks: Dictionary mapping artists to their tracks
            - daily_counts: Counter of plays per day
            - monthly_counts: Counter of plays per month
            - weekday_counts: Counter of plays per weekday
            - hour_counts: Counter of plays per hour
            - play_times: List of play timestamps
            - play_counted: Total number of plays counted
            - skip_count: Number of skipped tracks
            - offline_count: Number of offline plays
            - track_skip_counts: Counter of skips per track
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

    for entry in entries:
        try:
            # Skip entries with no playtime or missing required fields
            if not entry.get("ms_played") or entry["ms_played"] <= 0:
                continue

            # Skip entries with a missing timestamp
            if "ts" not in entry:
                logging.warning(f"Entry missing timestamp, skipping: {entry.get('master_metadata_track_name', 'Unknown track')}")
                continue

            # Process entries with artist information
            if entry.get("master_metadata_album_artist_name"):
                # Get the artist name or use fallback
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

                if entry["ms_played"] > min_milliseconds:
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
                if entry.get("ms_played") > min_milliseconds:
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

    return (
        yearly, dates_set, first_ts, first_entry, last_ts, last_entry,
        artist_set, album_set, track_set, artist_tracks, daily_counts,
        monthly_counts, weekday_counts, hour_counts, play_times,
        play_counted, skip_count, offline_count, track_skip_counts
    )

def aggregate_yearly_data(yearly: DefaultDict[int, Dict[str, DefaultDict[str, int]]]) -> Dict[str, DefaultDict[str, int]]:
    """
    Aggregate yearly data into a single "all years" dataset.

    Args:
        yearly (DefaultDict[int, Dict[str, DefaultDict[str, int]]]): Dictionary of yearly statistics

    Returns:
        Dict[str, DefaultDict[str, int]]: Aggregated statistics for all years
    """
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
    
    return all_data