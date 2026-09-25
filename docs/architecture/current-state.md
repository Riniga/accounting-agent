# Current Architecture State

Short reference for the current state of the workspace. For full context see
[`overview.md`](overview.md). Keep this current — it's the quick-scan version; update it
in the same PR as any change to an app's status, test count, or key capabilities.

## Applications

| App | Status | Tests | Key capabilities |
|-----|--------|-------|-------------------|
| `accounting-agent` (`src/accounting_agent/`, v0.1.0) | Implemented — walking skeleton (MVP-001); MVP-002 in progress | 150 | organisation profile loading/validation (incl. `books` section), `run <org> --config-dir` command, book model (vouchers with posting lines and series), balances, findings, personal-number masking, `front-matter` format reader, general book checks |

Organisation projects (JudoSyd, Helsingborgs Judoklubb, Aktivitet Förebygger) are separate
private repositories and are not tracked here (ADR-002, ADR-003).

## Shared package

Not applicable — this repository is a single package, and it is itself the shared core
([ADR-002](decisions/ADR-002-python-core-repository.md)).

## Conventions

See [`docs/standards/`](../standards/). Project-specific:
- no real organisation data in this repository, synthetic fixtures only
  ([ADR-003](decisions/ADR-003-no-real-data-in-core-repo.md));
- books as CSV/Markdown and configuration as YAML
  ([ADR-004](decisions/ADR-004-csv-and-markdown-storage.md));
- no AI trailer in commit messages — AI assistance is marked in the pull request
  (interpretations §7).

## Dependencies

| Dependency | Kind | Why |
|---|---|---|
| Python 3.14 | runtime (Conda) | Target version, chosen in MVP-001 |
| PyYAML | runtime | Reads `organisation.yaml` |
| Ruff, pre-commit, pytest, pytest-cov | development | Formatting/lint, local hooks, tests and the coverage gate |

## Test counts

| Package | Tests | Coverage |
|---|---|---|
| `accounting_agent` | 150 (profile 20, profile books 21, CLI 9, book model 12, balances 5, findings 4, masking 12, front-matter reader 42, checks 25) | 98.59% (floor 90 %) |

## Methodology compliance

See [`docs/methodology-compliance/`](../methodology-compliance/) — first assessment
2026-09-25, with the standing at a glance in its README.
