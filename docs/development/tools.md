# Developer Tools

The tools required for local development and their role. Installation steps are in
[`setup.md`](setup.md).

## Required tools

| Tool | Purpose | Install |
|------|---------|---------|
| Miniconda (or Anaconda) | Provides Python and the environment | `winget install Anaconda.Miniconda3` |
| Python 3.14 | Runtime — managed via Conda, not installed separately | `environment.yml` |
| Git | Version control | `winget install Git.Git` |
| pytest + pytest-cov | Test runner and coverage gate | `requirements-lock.txt` |
| Ruff | Formatter and linter — the CI check `Ruff` and the pre-commit hook | `requirements-lock.txt` |
| pre-commit | Runs the local Git hooks (Ruff, file validators, detect-secrets) | `requirements-lock.txt`, then `pre-commit install` |
| pip-tools | Compiles `requirements.in` into `requirements-lock.txt` — only needed when changing dependencies | `pip install pip-tools` |

## AI coding assistants

| Tool | Purpose | Install |
|------|---------|---------|
| Claude Code | Primary AI coding assistant | Per Anthropic documentation |
| GitHub Copilot | Optional secondary assistant (reads `AGENTS.md`) | Per GitHub documentation |

## Optional tools

| Tool | Purpose |
|------|---------|
| GitHub CLI (`gh`) | Inspect and apply repository settings — see [`repo-settings.md`](repo-settings.md) |
