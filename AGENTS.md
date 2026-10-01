# AGENTS.md

Guidance for AI coding agents working in this repository. For library
usage and the public API see [README.md](README.md); for setup, tests,
and linting see [DEVELOPMENT.md](DEVELOPMENT.md).

## What this library does

DapperTable formats tables for printing, similar to `prettytable`, with
two differentiators:

- **CJK double-width handling.** Chinese/Japanese/Korean characters
  display as two columns wide; `wcwidth` is used to compute the actual
  display width so columns align correctly.
- **Pagination for chat APIs.** `PaginationLength` / `PaginationRows`
  split the rendered table into multiple strings, each within the limit a
  downstream API imposes (e.g. Discord's 2000-char message cap).

## Architecture

Single module: `dappertable/__init__.py`. Public surface:

| Symbol | Role |
|---|---|
| `DapperTable` | Builder class: `add_row()`, `edit_row()`, `remove_row()`, `render()`, `get_pages()`, `format_page()` |
| `Column`, `Columns` | Column definitions (name, width, `zero_pad`) and separator |
| `PaginationLength`, `PaginationRows` | Pagination options passed as `pagination_options=` |
| `DapperRow` | One rendered row; `edit()` bypasses column formatting |
| `shorten_string(s, width, placeholder='..')` | Truncate to a display-width budget, respecting CJK |
| `string_width(s)` | Display width of a string (CJK = 2) |
| `format_string_length(s, length)` | Pad/truncate to a display-width budget |
| `DapperTableError` | Raised for invalid configuration / row shape |

Without `columns`, rows are plain strings joined by newlines. With
`columns`, each row is a list matching the column count. `render()`
returns a `str`, or a `list[str]` when pagination is configured.

## Conventions

- **100% coverage** is enforced by `tox` (`--cov-fail-under=100`). New
  code must include tests that exercise every branch.
- Tests live in `tests/test_dappertable.py`; mirror that file's
  per-feature grouping (CJK helpers, table construction, row management,
  errors, pagination).
- `bandit` runs in `tox` — avoid `subprocess`, `eval`, or anything else
  that requires a `# nosec` annotation unless absolutely necessary.

## Stable wire surface

`wcwidth` is pinned exactly in `pyproject.toml` (`==`, not `~=`). The CJK width tables
change between versions and a `~=` upgrade would silently shift column
widths in downstream consumers. Don't relax this constraint without
running the test suite against the new wcwidth and updating expected
widths if they change.
