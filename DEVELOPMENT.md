# Development

Setup, tests, and linting for working in this repo. User-facing API and
usage are in [README.md](README.md). For agent-facing internals see
[AGENTS.md](AGENTS.md).

## Setup

Use a virtualenv:

```bash
virtualenv venv
source venv/bin/activate
pip install -e ".[test]"
```

## Running tests

Full suite with linting, security scan, coverage gate (100%) across
py311–py314:

```bash
tox
```

Tests only:

```bash
pytest tests/
```

Tests with HTML coverage report:

```bash
pytest --cov=dappertable/ --cov-report=html --cov-fail-under=100 tests/
# open htmlcov/index.html
```

Single test file or test:

```bash
pytest tests/test_dappertable.py
pytest tests/test_dappertable.py::test_function_name
```

## Linting and security

```bash
pylint dappertable/
bandit -r dappertable/
```

Both run inside `tox` and must pass for a release build.

## Releasing

The version lives in the `VERSION` file (single-line, semver, no `v`
prefix). Bump it and push a tag — CI handles the GitLab Release + PyPI
upload via the shared templates from `tnoff-projects/github-workflows`.
