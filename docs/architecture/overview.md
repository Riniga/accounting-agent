# Architecture Overview

<!--
Keep this file current: update it in the same PR as any change to workspace structure,
major components, dependencies, or the build/deploy process (see
docs/standards/documentation.md).
-->

## Project Overview

Accounting Agent is the shared core for AI-assisted bookkeeping in several small non-profit
organisations (JudoSyd, Helsingborgs Judoklubb, Aktivitet Förebygger). Each organisation
keeps its own private project with data, chart of accounts, rules and configuration. This
public repository holds the general functionality they share. See
[`docs/vision.md`](../vision.md) and the [initial idea](../initial-idea.md).
Swedish bookkeeping terms and their English names in the code are in the
[glossary](glossary.md).

**Current state (after MVP-001):** a walking skeleton. It is one installable package with
an organisation-profile loader and a minimal `accounting-agent run` command, behind a full
set of CI quality gates. There is no bookkeeping functionality yet. It starts with
[MVP-002](../mvp/MVP-002-common-book-model.md).

## Current Workspace Structure

```text
src/accounting_agent/   The core package (ADR-002)
    __init__.py         Package version
    __main__.py         `python -m accounting_agent`
    cli.py              `accounting-agent` command line (argparse)
    profile.py          Organisation profile: organisation.yaml → OrganisationProfile
tests/                  pytest suite; fixtures/ holds synthetic organisations only (ADR-003)
docs/                   Vision, roadmap, architecture + ADRs, MVPs, plans, standards,
                        development setup, methodology + compliance, Claude prompts
docs/reference/         Local, git-ignored copies of the private organisation projects
scripts/                scan_instruction_files.py (hidden-Unicode scan, used by CI)
.github/                CI workflow, Dependabot, PR template, Copilot pointer
.claude/                Claude Code permission settings
pyproject.toml          Package metadata + Ruff/coverage configuration
environment.yml         Conda: Python 3.14 + the pip lock
requirements.in / requirements-lock.txt   Pip sources / hash-pinned lock
LICENSE                 PolyForm Noncommercial 1.0.0 (ADR-005)
```

## Major Components

### `accounting_agent` (package)

- **`profile.py`** reads and validates `organisation.yaml` from an organisation's
  configuration directory:
  - `organisation` must be a lowercase slug;
  - `features` must map names to real booleans;
  - unknown top-level keys produce a warning, not an error;
  - the file is read with `yaml.safe_load`.

  It returns an immutable `OrganisationProfile` or raises `ProfileError`. This is the only
  place organisation-specific settings enter the core.
- **`cli.py`** provides `accounting-agent run <organisation> --config-dir <path>`. It
  loads the profile and refuses to run if `<organisation>` doesn't match the profile. It
  logs the enabled and disabled features to stderr, and exits 0 (ok), 1 (invalid profile
  or mismatch) or 2 (usage error).

Nothing depends on the package yet. The organisation projects start consuming it from
MVP-002 onward.

## Existing Dependencies

### Runtime

- **PyYAML** — parses `organisation.yaml`. The standard library has no YAML parser.

### Development Environment

- **Conda** (conda-forge only) provides **Python 3.14**.
- **pip**, from `requirements-lock.txt` (hash-pinned, compiled with pip-tools), provides
  Ruff, pre-commit, pytest and pytest-cov (plus colorama, pinned for cross-platform lock
  stability).

### Build

- **setuptools** is the build backend. The version comes from
  `accounting_agent.__version__`. There is no published release.

### AI Assistants

- **Claude Code** is the primary assistant; GitHub Copilot is optional. Both follow
  [`AGENTS.md`](../../AGENTS.md).
- `.claude/settings.json` requires in-the-moment approval for commit, push, delete and
  `gh pr merge`.

## Build and Development Process

### Environment Setup

See [`docs/development/setup.md`](../development/setup.md). The commands were verified from
a fresh clone in MVP-001.

### Running Tests

`pytest -q` from the repository root. The coverage floor is 90 % (`pyproject.toml`); the
measured baseline is 96.47 %.

### Development Workflow

`Roadmap → MVP → Plan → Implementation → Test → Pull Request` — see
[`docs/development/methodology.md`](../development/methodology.md) and
[`AGENTS.md`](../../AGENTS.md).

### Git Workflow

One feature branch per MVP off `main`, merged through a pull request (see
[`docs/standards/git.md`](../standards/git.md) and interpretations §8).

`main` is protected by the ruleset "Protect main":
- no direct pushes or force pushes, and no deletion — for anyone;
- a pull request is required, with 6 required checks;
- 0 required approvals — single-maintainer exception EX-001.

### CI/CD

`.github/workflows/ci.yml` runs on pull requests to `main` and on pushes to `main`. `Ruff`
runs first; the other checks run after it:
- `Ruff` — format and lint;
- `Dependencies` — lock drift, `pip-audit`, licence allowlist;
- `SAST` — Semgrep;
- `Secret scan` — detect-secrets;
- `Instruction file scan` — hidden Unicode;
- `Run tests` — pytest with the coverage gate, in the Conda environment.

Every gate was shown to fail on deliberately broken code. The same Ruff and detect-secrets
checks run locally as pre-commit hooks. There is no CD.

### Deployment

None. The core is installed locally and run on the owner's machine; the organisation
projects will run it on a local schedule.

## Architectural Observations

- **Two-layer split:** a public, organisation-agnostic core (this repository) and private
  organisation projects that hold data and configuration (ADR-002, ADR-003). The profile's
  organisation check is the first guard against running one organisation's command against
  another's data.
- **AI decides, code executes:** the LLM does understanding and judgement; deterministic
  Python does bookkeeping operations, validation and integrations, exposed to the agent as
  defined tools (R3).
- **Files, not a database:** books as CSV and Markdown, configuration as YAML (ADR-004).
- **Extract, don't design ahead:** functionality moves into the core only once a working
  function exists in an organisation project to generalise. MVP-001's baseline analysis
  found the book model (chart of accounts, opening balance, one Markdown file per voucher)
  to be the strongest overlap, so it is extracted first (MVP-002).

## Planned Evolution of the Workspace

*Everything in this section is planned, not existing.*

- **MVP-002:** book-model classes (account, opening balance, voucher), readers for the
  organisation files, and the general validation checks. This brings a domain/IO split
  inside the package and a decision on module-boundary tooling (`GAP-B3-BOUNDARIES`).
- **Later module areas** (from the initial idea, added only as extraction justifies them):
  bank import and reconciliation (MVP-003), reports (MVP-004), agent tools, confidence
  and approval policies, and the audit trail (R3), integrations (R4), payroll (R5).
- **Consumption by organisation projects (undecided, R3):** Claude Code acts as the agent
  in each organisation project, locally and on a schedule. JudoSyd already does this with
  `claude -p` and its own MCP servers. Whether the core is reached as an installed
  package, through scripts or through an MCP server is decided in R3.

## Open Questions and Areas Not Yet Implemented

- How organisation projects consume the core (package / scripts / MCP) — Unknown – to be
  decided (R3).
- The data model's file schemas beyond the book model — MVP-002 onward.
- Confidence thresholds and approval levels per operation — Unknown – to be decided (R3).
- Local scheduler mechanism — Unknown – to be decided.
- Relation to the Swedish Bookkeeping Act (archiving, verification) — backlog.
- Methodology gaps and exceptions — see
  [`docs/methodology-compliance/`](../methodology-compliance/README.md), notably EX-001
  (no second reviewer).
