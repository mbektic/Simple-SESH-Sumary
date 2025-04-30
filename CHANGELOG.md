# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.11.0] 2025-04-30
### Changed
- Refactored GenerateHTMLSummary.py into smaller, more focused modules:
  - Created data_processing.py for data loading and processing functions
  - Created statistics.py for statistics calculation functions
  - Created html_generation.py for HTML generation functions
- Improved code organization and maintainability

## [1.10.0] 2025-04-30
### Added
- Added JSON data structure validation
- Added type hints for better IDE support
- Added proper exception handling for file operations
- Added docstrings to functions
- Added input validation for GUI fields
- Added graceful degradation for missing or corrupt data
- Added comprehensive error handling throughout the application
- Added total plays stat
- Added input validation for GUI fields
- Added graceful degradation for missing or corrupt data
- Added comprehensive error handling throughout the application
- Added keyboard navigation support for all interactive elements
- Added ARIA attributes for improved screen reader support
- Added focus management for modals and dialogs
- Added enhanced user-friendly error messages in the GUI,

### Changed
- Replaced print statements with logging calls

### Fixed
- Fixed highlighting not working after searching and changing the page.

## [1.9.1] 2025-04-30
### Changed
- Regrouped the stats to make them easier to digest.

### Fixed
- You can no longer scroll around while everything is loading, this should also hopefully fix the jumping of the loading screen.
- Fixed where tapping outside the info modal on mobile would not close it. 

## [1.9.0] 2025-04-29
### Added
- Unique Tracks Ratio stat
- Gini Coefficient of Artist Plays stat
- Weekend vs. Weekday Ratio stat
- Number of listening sessions stat
- Average session length stat
- Longest single session stat
- Skip rate stat
- Offline vs. Online ratio stat
- Total listening time stat
- Average playtime per play stat
- Most skipped track stat
- Longest hiatus stat
- Most popular week/day stats

### Changed 
- Changed the info button on stats to match the theme.

## [1.8.0] 2025-04-29
### Added 
- Eddington number stats
- Artist cut-over point stat
- Most popular year/month stats
- Longest Listening Streak stat
- Average Plays per Active Day stat
- Most Active Weekday stat
- Peak Listening Hour stat

### Changed
- Cleaned up stats grouping to make it more human-friendly.

### Fixed
- Fixed jumping of the loading screen on mobile (for real this time)

## [1.7.1] 2025-04-29
### Changed
- General formating changes.  

### Fixed
- Fixed jumping of the loading screen on mobile.

## [1.7.0] 2025-04-29
### Added
- Added a new stats section to the bottom of the page with some general fun stats. 

## [1.6.2] 2025-04-29
### Changed
- Check to ensure the total time played is more than 0 ms to get rid of useless data.

## [1.6.1] 2025-04-29
### Changed
- Search now persists when switching between tabs. 

### Fixed
- Fixed mode toggle not working anymore after the tab update.

## [1.6.0] 2025-04-29
### Added
- Year selector for the tables so you can see the data based off of the year. 

## [1.5.1] 2025-04-22
### Added
- Text highlighting on search terms. 

### Changed
- The page title is now "Spotify Summary"
- Moved the title bar and loading page to a new HTML file
- If there are no search results, a "No results found" message will be shown.
- Milliseconds always now format with three digits for consistency

## [1.5.0] 2025-04-22
### Added
- New header bar with a settings menu and moved the dark theme slide and the play mode switch under it. 

### Changed
- Moved the `PLAYTIME_MODE` setting into the app instead of a config option so one resulting page can view both.
- Switched to spotify green instead of red.
- Moved some of the HTML to its own file `html/settings_moda.html` to make the project easier to manage. I want to move more in the future. 
- Update `print_file()` function to be able to handle emojis 

### Removed
- `PLAYTIME_MODE` setting was removed from the config and the GUI
- The fancy dark mode slider had to go, it was nice looking but a pain in the behind. 

## [1.4.0] 2025-04-21
### Added
- New GUI for the app that makes it easy to edit parameters without editing the config file.

### Changed
- `OUTPUT_FILE` no longer needs .html, and all created files will always be HTML.

### Fixed
- `MIN_MILLISECONDS` wasn't being used so this was fixed.

## [1.3.2] 2025-04-21
### Changed
- Increased the fade out time to one second, so on small datasets it doesn't just look like the screen is flashing
- The size of the loading text and spinner was updated.
- No longer remove the loading screen from the layout in case I need it again. 

## [1.3.1] 2025-04-21
### Added
- Loading screen while the tables are paginating.
- Added missing `<!DOCTYPE html>` to get rid of annoying warning

### Changed
- Move `window.onload` function to `scripts.js`
- Text changes for search boxes and the second table column.

### Fixed
- Fixed weird behaviors setting the default theme and loading the selected theme

## [1.3.0] 2025-04-21
### Added
- Search functionality.
- Added a dark_mode toggle button. 

### Changed
- Rewrote the pagination functions to drastically improve render time. 8–10 seconds with my full data to about 3 in firefox, 1 second in Chromium-based browsers. 
- Redid the light theme to make it better along with some other minor styling changes.
- Imported * from config to clean up code.
- Changed Page Title to "Spotify Streaming History"

### Removed
- Removed `DARK_MODE` config option

## [1.2.3] 2025-04-21
### Added 
- Mobile Styling

### Changed
- Updated playtime column header so it looks better on mobile.
- Moved config variables to their own file for user easy of use. 
- Other minor styling updates. 
- Reduced the page window from 2 to 1 so the page selector fits better. 

## [1.2.2] 2025-04-20
### Changed
- Text updates.

## [1.2.1] 2025-04-20
### Changed
- JavaScript was moved to its own file to make it easier to edit.
- Added milliseconds to playtime mode.

### Fixed
- Fixed table columns jumping around when switching pages. 

## [1.2.0] 2025-04-19
### Added
- New dark mode option

### Changed 
- Styles are now in CSS files to make them easier to manage, with three files `stlye.css`, `light.css` and `dark.css`
- General styling changes for readability.
- Updated `README.md`

## [1.1.3] 2025-04-19
### Changed 
- Playtime chart tables names now say `Play Time` instead of `Play Count`.
- Changed the font to `Courier New - monospace` as it comes off more legible.
- Updated screenshots in readme.

## [1.1.2] 2025-04-19
### Added 
- Added a .gitignore

## [1.1.1] 2025-04-19
### Fixed
- Fixed spelling of `CHANGELOG.md` to be correct.

## [1.1.0] 2025-04-19
### Added
- Added a new `PLAYTIME_MODE` flag that will make the script generate the ranking based off of milliseconds listened instead of raw playcount.
- Added `CHANGELOG.md`
- Added version number to the bottom of the HTML page so users can quickly see what version they are using and if there's a new one available

### Changed
- Minor Style changes.

## [1.0.0] - 2025-04-17
### Added
- Initial Release
