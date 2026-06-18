# Sphinx

[![CI Status](https://github.com/CognitechAI-Pilot/sphinx/actions/workflows/main.yml/badge.svg)](https://github.com/CognitechAI-Pilot/sphinx/actions)
[![codecov](https://codecov.io/gh/CognitechAI-Pilot/sphinx/branch/master/graph/badge.svg)](https://codecov.io/gh/CognitechAI-Pilot/sphinx)
[![Documentation Status](https://readthedocs.org/projects/sphinx/badge/?version=latest)](https://sphinx.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/license-BSD-blue.svg)](LICENSE.rst)

Sphinx is a powerful documentation generator that translates a set of reStructuredText source files into various output formats, including HTML, LaTeX, PDF, and more.

---

## Table of Contents

- [Quickstart](#quickstart)
- [Running Tests](#running-tests)
- [Linting and Formatting](#linting-and-formatting)
- [Type Checking](#type-checking)
- [Building the Documentation](#building-the-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Quickstart

### Prerequisites

This project uses [`uv`](https://github.com/astral-sh/uv) for package and virtual environment management.

Install `uv` if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/CognitechAI-Pilot/sphinx.git
cd sphinx
```

2. **Create a virtual environment and install dependencies:**

```bash
uv sync
```

This command reads `pyproject.toml` and `uv.lock` to install all required dependencies into a local `.venv`.

3. **Activate the virtual environment:**

```bash
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

4. **Verify installation:**

```bash
python -c "import sphinx; print(sphinx.__version__)"
```

---

## Running Tests

This project uses [`pytest`](https://pytest.org) for unit and integration testing, and [`tox`](https://tox.wiki) to manage test environments across multiple Python versions.

### Run tests with pytest (quick, current environment)

```bash
pytest
```

> pytest is configured via `.pytest.toml`.

### Run tests with tox (full matrix — recommended before opening a PR)

```bash
tox
```

> tox is configured via `tox.ini` and covers all supported Python versions.

### Run a specific test file or test case

```bash
pytest tests/test_builders.py
pytest tests/test_builders.py::TestHTMLBuilder::test_basic
```

### Run tests with coverage report

```bash
pytest --cov=sphinx --cov-report=term-missing
```

Coverage thresholds are enforced via `.codecov.yml`.

---

## Linting and Formatting

This project uses [`ruff`](https://docs.astral.sh/ruff/) for both linting and code formatting.

### Check for linting issues

```bash
ruff check .
```

### Auto-fix linting issues

```bash
ruff check --fix .
```

### Check formatting

```bash
ruff format --check .
```

### Auto-format code

```bash
ruff format .
```

> Ruff is configured via `.ruff.toml`. All code **must** pass `ruff check` and `ruff format --check` with zero errors before a PR can be merged.

### Non-Python assets (JS/TS)

```bash
npx prettier --check .
npx prettier --write .
```

> Prettier is configured via `.prettierrc.toml`.

---

## Type Checking

Two type checkers are supported:

### Pyrefly

```bash
pyrefly check
```

> Configured via `pyrefly.toml`.

### ty

```bash
ty check
```

> Configured via `ty.toml`.

---

## Building the Documentation

Documentation source lives in `doc/` and is hosted on [ReadTheDocs](https://sphinx.readthedocs.io).

### Build HTML docs locally

```bash
make docs
```

Or using Sphinx directly:

```bash
cd doc
make html
```

The built documentation will be in `doc/_build/html/`.

> ReadTheDocs auto-builds on every merge to `master`. Configuration is in `.readthedocs.yml`.

---

## Contributing

We welcome contributions! Please follow the workflow below.

### Branching

Branch off `master` using one of the following prefixes:

| Prefix | Purpose |
|---|---|
| `feature/<short-description>` | New features |
| `fix/<short-description>` | Bug fixes |
| `docs/<short-description>` | Documentation changes |
| `chore/<short-description>` | Maintenance / tooling |

Branch names must be **lowercase**, **hyphen-separated**, and **≤ 60 characters**.

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

[optional body]

[optional footer: Refs JIRA-<id> | Closes #<github-issue>]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

**Example:**

```
docs(readme): add quickstart and contributing guide

Adds uv quickstart, tox/pytest instructions, ruff workflow,
and contribution guidelines.

Refs CAP-3
```

### Pull Request Checklist

Before opening a PR, ensure:

- [ ] All tests pass: `tox`
- [ ] No linting errors: `ruff check .`
- [ ] Code is formatted: `ruff format --check .`
- [ ] New public functions/classes have docstrings (NumPy or Google style)
- [ ] Type annotations added to all new function signatures
- [ ] `CHANGES.rst` updated with a changelog entry
- [ ] PR title follows Conventional Commits format
- [ ] PR body includes a link to the relevant JIRA ticket (`Refs CAP-<id>`)

### Changelog

All user-facing changes must be recorded in `CHANGES.rst` using this format:

```
* `#<github-issue>`: <Short description of change>. (Contributed by @username)
```

### Code of Conduct

Please read [CODE_OF_CONDUCT.rst](CODE_OF_CONDUCT.rst) before contributing.

---

## License

This project is licensed under the BSD License — see [LICENSE.rst](LICENSE.rst) for details.
