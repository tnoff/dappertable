# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DapperTable is a Python library for formatting tables with f-strings, similar to prettytable but with better support for East Asian characters that have double-width spacing. The library handles CJK (Chinese, Japanese, Korean) character formatting correctly and can split tables into multiple strings for API message length limits.

## Development Commands

### Testing
- Run tests: `pytest tests/`
- Run tests with coverage: `pytest --cov=dappertable/ --cov-report=html --cov-fail-under=100 tests/`
- Run linting: `pylint dappertable/`
- Run all tests across Python versions: `tox`

### Build
- Build package: `python setup.py sdist bdist_wheel`

## Architecture

### Core Components

**Main Library (`dappertable/__init__.py`)**:
- `DapperTable` class: Main table formatting class that handles headers, rows, and output formatting
- `shorten_string_cjk()`: Truncates strings while respecting CJK double-width characters
- `string_length_cjk()`: Calculates proper string length including CJK characters
- `format_string_length()`: Adjusts format lengths for CJK character spacing
- `DapperTableException`: Custom exception class

### Key Features

**CJK Character Support**: The library properly handles East Asian characters that display as double-width, ensuring correct table alignment. This is the primary differentiator from other table libraries.

**Table Pagination**: Tables can be split into multiple strings using `rows_per_message` parameter, useful for APIs with message length limits (like Discord bots).

**Table Structure**: 
- Headers defined with `{'name': 'column_name', 'length': width}`
- Rows added individually with `add_row()`
- Output via `print()` method returns string or list of strings

### Testing Structure

All tests are in `tests/test_dappertable.py` with 100% coverage requirement. Tests cover:
- CJK character handling functions
- Table creation and row management  
- Error conditions and exceptions
- Pagination functionality