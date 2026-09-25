# Developer Tools

This document lists the tools required for local development and explains their role.

## Required tools

| Tool | Purpose | Install |
|------|---------|---------|
| Miniconda | Python environment and package management | `winget install Anaconda.Miniconda3` |
| Python 3.13 | Runtime — managed via Conda, not installed separately | Included in `environment.yml` |
| Git | Version control | `winget install Git.Git` |
| pytest | Test runner — managed via Conda | Included in `environment.yml` |
| Ruff | Formatter and linter (record the tool choice as an ADR) — the CI check `Ruff` and the pre-commit hook | Included in `environment.yml` |
| pre-commit | Runs the local Git hooks | Included in `environment.yml`; then `pre-commit install` (see `environment.md`) |

## AI coding assistants

| Tool | Purpose | Install |
|------|---------|---------|
| Claude Code | Primary AI coding assistant | Per Anthropic documentation |
| GitHub Copilot | Secondary AI coding assistant | Per GitHub documentation |

## Miniconda setup

Install Miniconda:

```powershell
winget install Anaconda.Miniconda3
```

Keep Conda up to date:

```bash
conda update conda
conda update --all
```

Add the `conda-forge` channel if not already configured:

```bash
conda config --add channels conda-forge
```

## Git setup

Install Git:

```powershell
winget install Git.Git
```

Create an SSH key for GitHub:

```bash
ssh-keygen -t ed25519 -C "your description"
```

Add the public key to GitHub under **Settings → SSH and GPG keys**.

Clone the repository:

```bash
git clone <your-repo-ssh-url>
```

## Optional tools

No additional tools beyond those listed above are required for the current workspace.
