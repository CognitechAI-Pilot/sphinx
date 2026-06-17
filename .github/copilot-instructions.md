# AI Agent Instructions — CognitechAI-Pilot / sphinx

> This file defines the operating instructions for the AI Coding & Ticket-Creation Agent
> assigned to maintain the `sphinx` repository in the `CognitechAI-Pilot` GitHub organization.

---

## 1. Identity & Scope

| Property | Value |
|---|---|
| **Agent role** | Coder & Ticket Creator |
| **GitHub repo** | `https://github.com/CognitechAI-Pilot/sphinx` |
| **GitHub org** | `CognitechAI-Pilot` |
| **Default branch** | `master` |
| **JIRA instance** | `https://cognitech-team.atlassian.net` |
| **Primary language** | Python |
| **Communication language** | English (en-US) |

---

## 2. Repository Layout

```
sphinx/
├── .github/              # CI/CD workflows and GitHub configuration
├── .codecov.yml          # Code-coverage thresholds
├── .git-blame-ignore-revs
├── .gitattributes
├── .gitignore
├── .mailmap
├── .prettierrc.toml      # Prettier formatter (JS/TS assets)
├── .pytest.toml          # pytest configuration
├── .readthedocs.yml      # ReadTheDocs build configuration
├── .ruff.toml            # Ruff linter & formatter rules
├── AUTHORS.rst
├── CHANGES.rst           # Changelog — always update on every release
├── CODE_OF_CONDUCT.rst
├── CONTRIBUTING.rst
├── EXAMPLES.rst
├── LICENSE.rst
├── Makefile              # Common dev tasks (lint, test, docs, release)
├── README.rst
├── bindep.txt            # OS-level binary dependencies
├── doc/                  # Sphinx documentation source
├── package.json          # Node.js tooling (prettier, etc.)
├── package-lock.json
├── pyproject.toml        # Python project metadata & build config (PEP 517)
├── pyrefly.toml          # Pyrefly type-checking config
├── sphinx/               # Main Python package source
├── tests/                # pytest test suite
├── tox.ini               # tox test-environment matrix
├── ty.toml               # ty type-checker config
├── utils/                # Internal utilities and helper scripts
└── uv.lock               # uv dependency lock file
```

---

## 3. Toolchain

| Tool | Purpose | Config file |
|---|---|---|
| **uv** | Package & virtual-env management | `uv.lock` |
| **tox** | Test environment matrix | `tox.ini` |
| **pytest** | Unit & integration testing | `.pytest.toml` |
| **ruff** | Linting and code formatting | `.ruff.toml` |
| **prettier** | Formatting non-Python assets | `.prettierrc.toml` |
| **pyrefly / ty** | Static type checking | `pyrefly.toml`, `ty.toml` |
| **codecov** | Coverage reporting | `.codecov.yml` |
| **ReadTheDocs** | Documentation hosting | `.readthedocs.yml` |

---

## 4. Branching & Commit Conventions

### Branching Strategy
- `master` — stable, protected default branch; never force-push.
- Feature work → branch off `master` with prefix:
  - `feature/<short-description>`
  - `fix/<short-description>`
  - `chore/<short-description>`
  - `docs/<short-description>`
- Branch names must be lowercase, hyphen-separated, ≤ 60 chars.

### Commit Message Format (Conventional Commits)
```
<type>(<scope>): <short summary>

[optional body]

[optional footer: Refs JIRA-<id> | Closes #<github-issue>]
```
**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

**Example:**
```
feat(builders): add parallel build support

Implements concurrent builder execution using asyncio.
Reduces full-docs build time by ~40%.

Refs SPHINX-42
```

---

## 5. Pull Request Workflow

1. **Always** open PRs against `master`.
2. PR title must follow Conventional Commits format.
3. PR body **must** include:
   - Summary of changes
   - Link to the JIRA ticket (`Refs SPHINX-<id>`)
   - Testing notes (what was tested, how to verify)
   - Breaking-change notice (if applicable)
4. Request a Copilot review via `request_copilot_review` before assigning human reviewers.
5. Do **not** merge until all CI checks pass and at least one approval is received.
6. Squash-merge preferred for feature branches; rebase-merge for hotfixes.

---

## 6. JIRA Task Creation Rules

### When to Create a JIRA Ticket
Create a JIRA issue for **every** of the following:
- New feature request or user story
- Bug or defect discovered in code review or CI
- Documentation gap
- Dependency upgrade (when non-trivial)
- Technical debt / refactoring task
- CI/CD pipeline change

### JIRA Instance
```
URL  : https://cognitech-team.atlassian.net
Org  : cognitech-team
```

### Required Fields for Every Ticket
| Field | Requirement |
|---|---|
| **Summary** | Clear, concise title (≤ 100 chars) |
| **Description** | Context, acceptance criteria, links to relevant code/PR |
| **Issue Type** | Story / Bug / Task / Sub-task (use `ListIssueTypes_V2` to verify) |
| **Project Key** | Retrieve via `ListProjects_V3` before creating |
| **Labels** | At minimum: `sphinx`, `ai-agent` |

### Linking Tickets to GitHub
- Always include the GitHub PR or issue URL in the JIRA ticket description.
- Always include `Refs JIRA-<key>` in the Git commit footer.

---

## 7. Code Quality Standards

- All Python code **must** pass `ruff check` and `ruff format --check` with zero errors.
- All code changes **must** maintain or improve test coverage (tracked via codecov).
- New public functions/classes **must** have docstrings following NumPy or Google style.
- Type annotations are required for all new function signatures.
- Run `tox` locally (or ensure CI passes) before opening any PR.

---

## 8. Documentation

- User-facing changes must be reflected in `doc/` and `CHANGES.rst`.
- `CHANGES.rst` entries follow the format:
  ```
  * `#<github-issue>`: <Short description of change>. (Contributed by @username)
  ```
- ReadTheDocs will auto-build on every merge to `master`.

---

## 9. Dependency Management

- Use **uv** to add/remove/upgrade dependencies.
- After any dependency change, commit the updated `uv.lock`.
- Do not edit `uv.lock` manually.
- Keep `bindep.txt` up to date with any new OS-level system dependencies.

---

## 10. Security

- Never commit secrets, tokens, credentials, or API keys.
- Run secret scanning (`run_secret_scanning`) on every diff before pushing.
- Report security issues privately — do not open public GitHub issues for vulnerabilities.

---

## 11. Agent Decision Flow

```
User Request
    │
    ├─ Requires code change?
    │       ├─ Yes → Create JIRA ticket → Create branch → Implement → Open PR → Request Copilot review
    │       └─ No  → Answer directly
    │
    ├─ Requires JIRA ticket only?
    │       └─ Yes → ListResources → ListProjects → ListIssueTypes → CreateIssue
    │
    └─ Requires information lookup?
            └─ Yes → Search repo, issues, PRs, commits as needed → Respond
```

---

## 12. Contacts & Ownership

| Role | GitHub User | Email |
|---|---|---|
| Repository Maintainer | `Chamodya-ka` | Chamodya@AICognitech.onmicrosoft.com |

---

*Last updated: 2026-06-17 by AI Agent (Coder & Ticket Creator)*
