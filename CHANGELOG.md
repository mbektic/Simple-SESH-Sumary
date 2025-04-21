# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] 2025-04-21
### Added
- Loading screen while the tables are paginating.
- Added missing `<!DOCTYPE html>` to get rid of annoying warning

### Changed
- Move `window.onload` function to `scripts.js`
- Text changes for search boxes and second table column.

### Fixed
- Fixed weird behaviors setting default theme and loading selected theme

## [1.3.0] 2025-04-21
### Added
- Search functionality.
- Added a dark_mode toggle button. 

### Changed
- Rewrote the pagination functions to drastically improve render time. 8-10 seconds with my full data to about 3 in firefox, 1 second in chromium based browsers. 
- Redid the light theme to make it a better along with some other minor styling changes.
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
- Javascript was moved to its own file to make it easier to edit.
- Added milliseconds to playtime mode.

### Fixed
- Fixed table columns jumping around when switching pages. 

## [1.2.0] 2025-04-19
### Added
- New dark mode option

### Changed 
- Styles are now in css files to make them easier to manage, with three files `stlye.css`, `light.css` and `dark.css`
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
- Added a version number to bottom of the HTML page so users can quickly see what version they are using and if there's a new one available

### Changed
- Minor Style changes.

## [1.0.0] - 2025-04-17
### Added
- Initial Release