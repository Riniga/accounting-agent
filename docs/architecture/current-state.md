# Current Architecture State

Short reference for the current state of the workspace. For full context see
[`overview.md`](overview.md). Keep this current — it's the quick-scan version; update it
in the same PR as any change to an app's status, test count, or key capabilities.

## Applications

| App | Status | Tests | Key capabilities |
|-----|--------|-------|-------------------|
| `accounting-agent` (core package, `src/accounting_agent/`) | Planned (MVP-001) | 0 | *(none yet — planned: `run <org>` CLI, organisation profile loading/validation)* |

Organisation projects (JudoSyd, Helsingborgs Judoklubb, Aktivitet Förebygger) are separate
private repositories and are not tracked here (ADR-002, ADR-003).

## Shared package

Not applicable — this repository is a single package, and it is itself the shared core
([ADR-002](decisions/ADR-002-python-core-repository.md)).

## Conventions

See [`docs/standards/`](../standards/). Project-specific: no real organisation data in this
repository, synthetic fixtures only ([ADR-003](decisions/ADR-003-no-real-data-in-core-repo.md));
books as CSV/Markdown, configuration as YAML ([ADR-004](decisions/ADR-004-csv-and-markdown-storage.md)).

## Dependencies

None yet — no runtime dependencies exist.

## Test counts

0 — no code or tests yet.

## Methodology compliance

See [`docs/methodology-compliance/`](../methodology-compliance/) — first assessment is part of
MVP-001.
