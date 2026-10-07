# Current Architecture State

Short reference for the current state of the workspace. For full context see
[`overview.md`](overview.md). Keep this current — it's the quick-scan version; update it
in the same PR as any change to an app's status, test count, or key capabilities.

## Applications

| App | Status | Tests | Key capabilities |
|-----|--------|-------|-------------------|
| `accounting-agent` (`src/accounting_agent/`, v0.1.0) | Implemented — MVP-001 walking skeleton, MVP-002 book model and validation (merged, PR #7), MVP-003 bank import, reconciliation, checks and reports (merged, PR #13); MVP-004 creating vouchers (merged, PR #14); MVP-005 vouchers with several lines in progress | 749 | organisation profile loading/validation (incl. `books`, `bank`, `checks`, `conventions` and `reports` sections), `run`, `validate`, `import-bank`, `report` and `new-voucher` commands, Swedish Markdown reports (summary, to-do, income statement, balance sheet, budget follow-up, monthly overview, general ledger, voucher list, closing comments), bank import into masked statement and fund-value files from the `nordea-csv` and `sparbanken-syd-csv` exports, selected by `bank.export_format`, reconciliation against the bank statement (`validate --unbooked`), detail checks (duplicates, date order, account sides, supporting documents — missing, expected for payments out of the bank, and unused files in the documents folder — parking and unused accounts), the chart against a BAS reference chart, fund value, budget, closing comments and to-do list, book model (vouchers with posting lines and series), balances, findings, personal-number masking, `front-matter` format reader (the simple form and the lines form with any number of posting lines; incl. a voucher's generated lines, kept out of the note and checked against the fields — ADR-009), general book checks, building a new voucher — a bank transaction against one account or several lines, or no bank transaction — with refusals (`new-voucher`, ADR-009), the voucher text of a statement row, rendering (either form, with one generated line per posting in the lines form) and exclusive writing of a `front-matter` voucher file |

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
| `accounting_agent` | 423 (profile 20, profile books 21, profile sections 66, bank import 27, bank statement reader 13, reconciliation 15, CLI validate bank 6, detail checks 18, CLI validate details 5, reference chart 19, supplements 22, supplement readers 13, reports format 9, reports 17, reports overview 18, CLI report 10, CLI encoding 1, CLI run 9, CLI validate 12, book model 12, balances 5, findings 4, masking 14, front-matter reader 42, checks 25) | 98.82% (floor 97 %) |

## Methodology compliance

See [`docs/methodology-compliance/`](../methodology-compliance/) — first assessment
2026-09-25, with the standing at a glance in its README.
