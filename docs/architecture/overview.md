# Architecture Overview

<!--
Keep this file current: update it in the same PR as any change to workspace structure,
major components, dependencies, or the build/deploy process (see
docs/standards/documentation.md).
-->

## Project Overview

Accounting Agent is the shared core for AI-assisted bookkeeping in several small non-profit
organisations (JudoSyd, Helsingborgs Judoklubb, Aktivitet Förebygger). Each organisation
keeps its own private project with data, chart of accounts, rules and configuration; this
public repository is meant to hold the general functionality they share. See
[`docs/vision.md`](../vision.md) and the [initial idea](../initial-idea.md).

**Current state: there is no code yet.** The repository contains documentation, the
development methodology, and tool configuration inherited from the project template. The
first code arrives with [MVP-001](../mvp/MVP-001-walking-skeleton.md).

## Current Workspace Structure

```text
.github/              CI workflow, Dependabot, PR template, Copilot pointer (from template)
.claude/              Claude Code permission settings
docs/
    initial-idea.md   The original project idea (historical input, unchanged)
    vision.md, roadmap.md
    architecture/     This overview, current state, ADRs
    mvp/, plans/      MVP-001 and its plan
    development/      Local setup, environment, tools, repo settings, process
    standards/        Coding, testing, git, documentation, dependencies, threat modelling
    methodology/      The development methodology (21 chapters, areas A–F)
    methodology-compliance/  This project's standing against the methodology (empty baseline)
    claude-prompts/   Reusable prompts for initialising, planning and closing MVPs
    reference/        Local, git-ignored copies of the organisation projects (ADR-003)
scripts/
    scan_instruction_files.py   Hidden-Unicode scan of AGENTS.md / CLAUDE.md (used by CI)
pyproject.toml, pytest.ini, environment.yml, requirements.in, .pre-commit-config.yaml
                      Python tool configuration from the template — still contains
                      placeholders; adapted in MVP-001
```

## Major Components

None yet. The planned package is described under
[Planned Evolution of the Workspace](#planned-evolution-of-the-workspace).

## Existing Dependencies

### Runtime

None — no application code exists.

### Development Environment

Configured but not yet verified: Conda (`environment.yml`) with Python and a pip-tools lock
compiled from `requirements.in` (Ruff, pre-commit). `requirements-lock.txt` does not exist
yet.

### Build

None.

### AI Assistants

Claude Code is the primary AI coding assistant. GitHub Copilot is kept as an option
(`.github/copilot-instructions.md`). Both follow [`AGENTS.md`](../../AGENTS.md).

## Build and Development Process

### Environment Setup

See [`docs/development/setup.md`](../development/setup.md) and
[`environment.md`](../development/environment.md). Not yet runnable until MVP-001 generates
the lock file and sets the environment name.

### Running Tests

`pytest` from the repository root. No tests exist yet.

### Development Workflow

`Roadmap → MVP → Plan → Implementation → Test → Pull Request` — see
[`docs/development/methodology.md`](../development/methodology.md) and
[`AGENTS.md`](../../AGENTS.md).

### Git Workflow

Feature branches off `main`, merged through pull requests — see
[`docs/standards/git.md`](../standards/git.md). There is a single maintainer; the
non-author review requirement is handled as a documented exception (ADR-001).

### CI/CD

`.github/workflows/ci.yml` (from the template) defines the gates that run on pull requests
to `main`: Ruff, dependency lock/licence check, SAST, secret scan, instruction-file scan and
tests. It still contains placeholders and has **never run**; it is adapted and made green in
MVP-001. There is no CD.

### Deployment

None. The agent runs locally on the owner's machine; there is no hosted environment.

## Architectural Observations

- **Two-layer split:** a public, organisation-agnostic core (this repository) and private
  organisation projects that hold data and configuration (ADR-002, ADR-003).
- **AI decides, code executes:** the LLM does understanding and judgement; deterministic
  Python does bookkeeping operations, validation and integrations, exposed to the agent as
  defined tools.
- **Files, not a database:** books as CSV and Markdown, configuration as YAML (ADR-004).
- **Extract, don't design ahead:** functionality moves into the core only once a working
  function exists in an organisation project to generalise.

## Planned Evolution of the Workspace

*Everything in this section is planned, not existing.*

- **MVP-001 (planned):** a single package in `src/accounting_agent/` with tests in
  `tests/`, a console command `accounting-agent run <org> --config-dir <path>` that loads
  and validates an organisation profile (`organisation.yaml`), synthetic fixtures under
  `tests/fixtures/`, and working CI gates.
- **Planned module areas** (from the initial idea, added only as extraction justifies
  them): importers (bank CSV, PDF, e-mail), accounting (transactions, matching, posting,
  validation), payroll, reporting, integrations (Gmail, Discord), agent tools/workflow, and
  a common data model (transaction, voucher, account, document) with a confidence value and
  an audit trail.
- **Consumption by organisation projects (undecided):** each organisation project runs
  Claude Code as the agent locally, on a schedule. Whether it reaches the core as an
  installed package, through scripts, or through an MCP server is decided in R3.

## Open Questions and Areas Not Yet Implemented

- How organisation projects consume the core and how the layers stay separate yet
  reachable (package / scripts / MCP) — Unknown – to be decided (R3).
- Python version and tool versions — to be verified in MVP-001.
- The common data model and file schemas — Unknown – to be decided (MVP-002 onward).
- Confidence thresholds and approval levels per operation — Unknown – to be decided (R3).
- Local scheduler mechanism — Unknown – to be decided.
- Relation to the Swedish Bookkeeping Act (archiving, verification) — backlog, not critical
  now.
