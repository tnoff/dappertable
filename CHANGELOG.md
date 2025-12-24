# Changelog

All notable changes to DapperTable will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.4] - 2025-12-23

## Changed
- Updated `chunk_list_by_length` to account for newlines in pagination length

## [0.2.3] - 2025-12-17

### Added
- `enclosure_start` and `enclosure_end` parameters to wrap table content on every page
- Enclosure wrapping accounts for character width in pagination calculations
- Support for separate opening and closing enclosure strings
- Common use case: wrapping tables in markdown code blocks for Discord/Slack bots

### Changed
- Updated `chunk_list_by_length` to account for enclosure overhead
- Print method now wraps content with enclosures before adding prefix/suffix

## [0.2.2] - 2025-12-17

### Added
- `prefix` and `suffix` parameters to DapperTable
- Prefix appears only on first page, suffix only on last page
- Smart pagination accounting for prefix/suffix lengths with `PaginationLength`
- Automatic handling of overflow - creates separate pages for prefix/suffix if content doesn't fit
- Validation to ensure prefix/suffix don't exceed pagination length

### Changed
- Updated `chunk_list_by_length` to handle prefix on first chunk and suffix on last chunk
- Print method updated to add prefix/suffix at appropriate positions

## [0.2.1] - 2025-10-11

### Added
- `get_paginated_rows()` method to access paginated row data before printing
- `print_rows()` method to print specific row lists
- Ability to manually edit `DapperRow` objects after pagination

### Changed
- Refactored pagination logic to allow access to rows before final output

## [0.2.0] - 2025-10-02

### Changed
- **Breaking**: Switched from custom CJK width calculation to `wcwidth` library
- Improved accuracy of display width calculations for wide characters
- Cleaned up string width and formatting logic
- Better handling of non-printable characters

### Fixed
- More accurate CJK character width calculations using industry-standard wcwidth

## [0.1.6] - 2025-09-20

### Fixed
- Removed unnecessary trailing spaces in last column when formatting tables
- Improved table alignment and readability

## [0.1.5] - 2025-09-20

### Fixed
- Improved East Asian character formatting logic
- Better handling of mixed CJK and ASCII content
- More accurate padding calculations for wide characters

## [0.1.4] - 2025-09-20

### Added
- `PaginationLength` option to split tables by total character length
- Useful for API message length limits (e.g., Discord max message length)
- Automatic calculation of optimal page breaks

## [0.1.3] - 2025-09-17

### Added
- `zero_pad_index` option for table headers
- Automatically pads index columns with leading zeros for cleaner output
- Dynamic zero padding adjusts as table grows

## [0.1.2] - 2025-09-17

### Added
- `edit_row()` method to modify existing table rows
- Validation for edit operations
- Support for editing both formatted and unformatted rows

## [0.1.1] - 2025-09-16

### Added
- `collapse_newlines` option (default: True)
- Removes double newlines from table output for cleaner formatting
- Can be disabled for cases where precise newline control is needed

## [0.1.0] - 2025-09-12

### Changed
- **Breaking**: Major refactor from message pagination to table printing library
- Renamed from MessagePagination to DapperTable
- Complete rewrite focused on table formatting with CJK character support
- New header system with `DapperTableHeader` and `DapperTableHeaderOptions`
- Support for pagination by rows (`PaginationRows`)

### Added
- Proper table formatting with headers and separators
- Column width management with automatic truncation
- East Asian character width support
- Custom separators between columns

## [0.0.9] - 2024-11-27

### Changed
- Modernized codebase
- Updated dependencies
- Code quality improvements
