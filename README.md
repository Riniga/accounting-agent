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

# run and validate (against the synthetic example organisation)
accounting-agent run example --config-dir tests/fixtures/example
accounting-agent validate example --config-dir tests/fixtures/example --balances
```

An organisation project points the commands at the directory that holds its
`organisation.yaml`:

```yaml
organisation: hbg-judo      # lowercase id; must match the command's <organisation>
features:
  accounting: true
  payroll: false
books:                      # needed by `validate`
  path: Bokföring           # relative to this file's directory
  format: front-matter      # the book file format (ADR-006)
  fiscal_year: 2026
  bank_account: "1930"
bank:                       # needed by `import-bank` (ADR-008)
  export_format: nordea-csv # the bank's export format
  statement_file: Bokföring/kontoutdrag.csv
  fund_account: "1350"      # optional, together with fund_value_file
  fund_value_file: Bokföring/fondvärde.csv
```

`accounting-agent validate <organisation> --config-dir <path>` reads the books and checks
them:
- It reports findings as `ERROR` / `WARNING` / `INFO`, and exits 1 on any error.
- It never prints a voucher's text, and masks personal identity numbers in all output.
- `--balances` also lists the balance per account.
- With a `bank` section it also reconciles the books against the statement file: the
  bank's own balances, the opening balance, and every bank voucher against a bank
  transaction and the reverse. `--unbooked` lists the transactions after the last voucher
  by date, amount and row — never by name or message.

`accounting-agent import-bank <organisation> --config-dir <path> <export>` turns a file
downloaded from the bank into the organisation's statement file or fund-value file:
- The export's header tells which; the export itself is never changed.
- The statement file is replaced, oldest transaction first. An export that starts later
  than the existing file is refused, since it would drop transactions.
- Fund values are merged by date.
- Personal identity numbers are masked as `[personnummer]` in the written file. The
  terminal shows only file names, dates and counts.

## Required GitHub Actions secrets

None currently. CI runs on pull requests only and needs no secrets; there is no CD.

## Documentation

| Area | Location |
|------|----------|
| Architecture | [`docs/architecture/`](docs/architecture/) |
| Using the core from an organisation project | [`docs/development/organisation-projects.md`](docs/development/organisation-projects.md) |
| Development process | [`docs/development/methodology.md`](docs/development/methodology.md) |
| Standards | [`docs/standards/`](docs/standards/) |
| Organisation methodology | [`docs/methodology/`](docs/methodology/) |
| Methodology compliance (internal) | [`docs/methodology-compliance/`](docs/methodology-compliance/) |
| Roadmap | [`docs/roadmap.md`](docs/roadmap.md) |
| MVPs | [`docs/mvp/`](docs/mvp/) |
| Implementation plans | [`docs/plans/`](docs/plans/) |
