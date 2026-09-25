# Accounting Agent

The shared core for AI-assisted bookkeeping in small non-profit organisations. Each
organisation keeps its own private project with data, chart of accounts, rules and
configuration; this repository holds the general functionality they share — never their
data.

**Status:** early development (0.1.0) — a walking skeleton: the package, a minimal `run`
command and all CI quality gates ([MVP-001](docs/mvp/MVP-001-walking-skeleton.md)). No
bookkeeping functionality yet; that starts with [MVP-002](docs/mvp/MVP-002-common-book-model.md).
**Owner:** Rickard Nisses-Gagnér (product and technical owner, sole maintainer).
**Licence:** [PolyForm Noncommercial 1.0.0](LICENSE) — free for any noncommercial use,
including by non-profit organisations; commercial use is not permitted
([ADR-005](docs/architecture/decisions/ADR-005-noncommercial-licence.md)).

## Vision

A shared AI-based financial administrator that can work for several organisations through
the same codebase, with strictly separated data, rules and permissions. See
[`docs/vision.md`](docs/vision.md).

## Workspace Structure

```text
src/accounting_agent/  The core package: organisation profile + `accounting-agent` command
tests/                 Tests and synthetic fixtures (no real data — ADR-003)

docs/
    Architecture, development process, standards, roadmap, MVPs and implementation plans
```

> **Note**
>
> The organisation projects (JudoSyd,
> Helsingborgs Judoklubb, Aktivitet Förebygger) are separate private repositories and are
> never part of this one ([ADR-003](docs/architecture/decisions/ADR-003-no-real-data-in-core-repo.md)).

## Development Process

Every change follows the same lightweight process:

```text
Roadmap
    ↓
MVP
    ↓
Implementation Plan
    ↓
Implementation
    ↓
Test
    ↓
Pull Request
```

See [`docs/development/methodology.md`](docs/development/methodology.md) for the full
process, and [`AGENTS.md`](AGENTS.md) for how AI tools work within it.

## Getting Started

1. Read [`AGENTS.md`](AGENTS.md) — the canonical instruction file for how work happens
   here (human or AI).
2. Follow [`docs/development/setup.md`](docs/development/setup.md) and
   [`environment.md`](docs/development/environment.md) to set up your local environment.
3. Read [`docs/standards/`](docs/standards/) — coding, testing, git, documentation,
   dependencies.
4. Read the project idea in [`docs/initial-idea.md`](docs/initial-idea.md) and the active
   MVP in [`docs/mvp/`](docs/mvp/).

## Quick start

Requires Conda (Miniconda or Anaconda) and Git — details in
[`docs/development/setup.md`](docs/development/setup.md).

```bash
# install
git clone git@github.com:riniga/accounting-agent.git
cd accounting-agent
conda env create -f environment.yml
conda activate accounting-agent
pip install -e .
pre-commit install

# test
pytest -q

# run (against the synthetic example organisation)
accounting-agent run example --config-dir tests/fixtures/example
```

An organisation project runs `accounting-agent run <organisation> --config-dir <path>`
against the directory that holds its `organisation.yaml`:

```yaml
organisation: hbg-judo      # lowercase id; must match the command's <organisation>
features:
  accounting: true
  payroll: false
```

## Required GitHub Actions secrets

None currently. CI runs on pull requests only and needs no secrets; there is no CD.

## Documentation

| Area | Location |
|------|----------|
| Architecture | [`docs/architecture/`](docs/architecture/) |
| Development process | [`docs/development/methodology.md`](docs/development/methodology.md) |
| Standards | [`docs/standards/`](docs/standards/) |
| Organisation methodology | [`docs/methodology/`](docs/methodology/) |
| Methodology compliance (internal) | [`docs/methodology-compliance/`](docs/methodology-compliance/) |
| Roadmap | [`docs/roadmap.md`](docs/roadmap.md) |
| MVPs | [`docs/mvp/`](docs/mvp/) |
| Implementation plans | [`docs/plans/`](docs/plans/) |
