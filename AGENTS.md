# AGENTS.md

Guidance for AI coding agents working in this repository. For library
usage and the public API see [README.md](README.md); for setup, tests,
and linting see [DEVELOPMENT.md](DEVELOPMENT.md).

## What this library does

DapperTable formats tables for printing — similar to `prettytable`, with
two differentiators:

- **CJK double-width handling.** Chinese/Japanese/Korean characters
  display as two columns wide; `wcwidth` is used to compute the actual
  display width so columns align correctly.
- **Pagination for chat APIs.** `rows_per_message` splits the rendered
  table into multiple strings, each ≤ the limit a downstream API
  imposes (e.g. Discord's 2000-char message cap).

## Architecture

Single module: `dappertable/__init__.py`. Public surface:

| Symbol | Role |
|---|---|
| `DapperTable` | Builder class — `add_row()`, `print()` |
| `shorten_string_cjk(s, length)` | Truncate to a display-width budget, respecting CJK |
| `string_length_cjk(s)` | Display width of a string (CJK = 2) |
| `format_string_length(s, length)` | Pad/truncate to a display-width budget |
| `DapperTableException` | Raised for invalid configuration / row shape |

Headers are dicts: `{'name': '<col>', 'length': <width>}`. Rows are added
positionally with `add_row(...)` and must match the header count.
`print()` returns a `str` (single rendered table) or a `list[str]` when
`rows_per_message` is set.

## Conventions

- **100% coverage** is enforced by `tox` (`--cov-fail-under=100`). New
  code must include tests that exercise every branch.
- Tests live in `tests/test_dappertable.py`; mirror that file's
  per-feature grouping (CJK helpers, table construction, row management,
  errors, pagination).
- `bandit` runs in `tox` — avoid `subprocess`, `eval`, or anything else
  that requires a `# nosec` annotation unless absolutely necessary.

## Stable wire surface

`wcwidth==0.7.0` is pinned exactly (not `~=`). The CJK width tables
change between versions and a `~=` upgrade would silently shift column
widths in downstream consumers. Don't relax this constraint without
running the test suite against the new wcwidth and updating expected
widths if they change.
