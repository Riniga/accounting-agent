# Gap register

Every open gap between this project and [the development methodology](../methodology/index.md)
(or your own organisation's equivalent).

If you keep a "known gaps" table anywhere else (e.g. `docs/architecture/current-state.md`),
point it here instead of duplicating — this file is the one source of truth.

A living document (methodology D3 BÖR 2): rows are added when a gap is found, updated as
follow-up plans progress, and struck through (`~~GAP-ID~~`) when closed.

**Last updated:** 2026-09-25

**Changelog**

- 2026-09-26 — MVP-002 closed `GAP-E4-MASKING` (all `validate` output masked; findings
  never quote voucher text) and `GAP-B3-BOUNDARIES` (a declared public API in
  `accounting_agent.books`, and a domain boundary enforced by Ruff `TID251`). Coverage
  floor raised to 95 %. `GAP-F2-CONFIDENTIAL`: the reading rule held for the pilot (counts
  only), but listing Aktivitet Förebygger's voucher file names exposed counterparty names.
  The row stays open.
- 2026-09-25 — First assessment (MVP-001, step 5.2). Areas A–F assessed; all rows below
  opened. MVP-001 already closed its own work: CI gates, branch protection, Dependabot,
  private vulnerability reporting, coverage floor and licence.
  Same day: owner confirmed an individual Pro plan with the training setting on
  (exception EX-003) and local-admin daily use (GAP-A1-PRIVILEGE). EX-003 closed the same
  day: the owner turned the training setting off.

<!-- A running changelog of what each delivered plan closed, newest first. Keep entries
     terse — what shipped, and which gap IDs it closed/reopened/re-scoped. This is the
     first thing anyone (human or AI) should read to understand what's already done before
     starting new work on this area. -->

## Legend

- **Severity**
  - `H` — blocks a core methodology guarantee (unenforced review, no secret-scanning, no
    SAST/SCA, no coverage gate, CI check chain incomplete).
  - `M` — a required control that is scheduled, or an owner/central decision that is
    pending.
  - `L` — a recommendation, a polish item, or a dormant/not-yet-applicable requirement.
- **Owner** — `platform` (a follow-up plan closes it), `owner` (a repo-settings or policy
  action for a named person), or a named organisational function (external dependency).
- **Status** — `open` · `in progress (P<n>)` · `closed` · `external — tracking` ·
  `not applicable yet`.

## Register

### Severity H

| ID | Chapter | Gap | Owner | Follow-up | Status |
|----|---------|-----|-------|-----------|--------|
| GAP-D2-REVIEW | D2 SKA 2–3, D3 SKA 3 | No non-author review; the ruleset requires 0 approvals | owner | Second reviewer → approvals 1 + `CODEOWNERS` (EX-001) | open — exception EX-001 |
| GAP-F1-SELFMERGE | F1 SKA 1, 6 | Claude Code acts through the owner's credentials, and with 0 approvals nothing in GitHub stops it merging a green PR | owner | Partly mitigated: `gh pr merge` requires in-the-moment approval in `.claude/settings.json`. Closes with GAP-D2-REVIEW | open |
| GAP-F2-CONFIDENTIAL | F2 SKA 2 | Personal data from an organisation project's rules file entered the AI tool's context during the baseline analysis (2026-09-25) | owner | Reading rule in interpretations §9. The HJK project should move its decision log out of the rules file. 2026-09-26: the pilot followed the rule (counts only); listing Aktivitet Förebygger's voucher file names exposed counterparty names (not copied). Rule: never list file names inside a voucher or book folder | open |

### Severity M

| ID | Chapter | Gap | Owner | Follow-up | Status |
|----|---------|-----|-------|-----------|--------|
| GAP-A2-AGREEMENT | A2 SKA 1–2 | Individual Pro plan, not an organisation agreement. The model-training setting was turned off 2026-09-25 (EX-003, closed); retention follows the individual-plan terms, not verified | owner | Accept for a one-person project, or move to a commercial plan if the project grows | open |
| GAP-F2-DPA | F2 SKA 3 | No data processing agreement with the AI provider (individual plan), although personal data can reach it (GAP-F2-CONFIDENTIAL) | owner | A DPA needs a commercial plan; until then, keep Confidential data out of AI context (interpretations §9) | open |
| GAP-F2-CLASSIFICATION | F2 SKA 1 | The classification covers this repository only (interpretations §9), not the organisations' own AI use | owner | Decide per organisation project | open |
| ~~GAP-E4-MASKING~~ | E4 SKA 3 | No automated masking of personal identity numbers in logs; needed once the core reads voucher texts | platform | [MVP-002](../plans/MVP-002-common-book-model.plan.md): `mask_personal_numbers()` on every output line; findings never quote voucher text | closed |
| GAP-E1-AITRAILER | E1 SKA 5 | Commits from 2026-09-25 carry an AI `Co-Authored-By` trailer | platform | No trailers from MVP-001 phase 5; published history not rewritten (interpretations §7) | in progress (MVP-001) |
| GAP-C3-PRIORITY | C3 SKA 3 | No written vulnerability prioritisation or response times | owner | Add to `SECURITY.md` | open |

### Severity L

| ID | Chapter | Gap | Owner | Follow-up | Status |
|----|---------|-----|-------|-----------|--------|
| GAP-A1-WORKSTATION | A1 SKA 1, 7 | Personal, unmanaged workstation, which also holds the organisation projects' data | owner | Owner decision — accept or improve (e.g. disk encryption, separate user) | open |
| GAP-A1-PRIVILEGE | A1 SKA 4 | Daily work runs as a local administrator (confirmed 2026-09-25) | owner | Use a standard user and elevate only when needed | open |
| ~~GAP-B3-BOUNDARIES~~ | B3 SKA 2–3 | No declared public API or tool-enforced module boundaries | platform | [MVP-002](../plans/MVP-002-common-book-model.plan.md): `books.__all__`; Ruff `TID251` banned-api (interpretations §3) | closed |
| GAP-B5-README | B5 SKA 1 | README lacks install/run/test commands | platform | MVP-001 step 6.1 | in progress (MVP-001) |
| GAP-B5-DOCTEST | B5 SKA 5 | Setup commands in `docs/development/` not validated automatically | platform | — | open |
| GAP-C2-SBOM | C2 SKA 1 | SBOM not generated automatically (no release pipeline) | platform | When releases exist | not applicable yet |
| GAP-C2-REACHABILITY | C2 SKA 2 | SCA without reachability analysis | platform | Revisit when the dependency count grows | open |
| GAP-C2-SHAPIN | C2 (supply chain) | GitHub Actions pinned to version tags, not commit SHAs | platform | — | open |
| GAP-C2-DEPENDABOT-LOCK | C2 SKA 3, 5 | Dependabot may not recompile `requirements-lock.txt` (compiled with `--no-header`), so its PRs could fail the drift check | platform | Verify on the first Dependabot pip PR | open |
| GAP-D1-AITDD | D1 SKA 5 | AI-written tests were not reviewed before implementation in MVP-001 phase 2 | owner | Tests reviewed in PR #5 (EX-002) | open — closes at PR #5 review |
| GAP-E1-WORKITEM | E1 SKA 6, D3 SKA 3 | PR ↔ work-item link is by convention only | platform | No built-in GitHub enforcement; revisit with a second reviewer | open |
| GAP-F3-FLAG | F3 SKA 8 | Changes to instruction files not specially flagged in review | platform | `CODEOWNERS` rule once a second reviewer exists | open |

### External dependencies (not a platform gap)

| ID | Chapter | Item | Owner to confirm | Status |
|----|---------|------|------------------|--------|
| GAP-C3-SAFEHARBOR | C3 SKA 2 | Legally reviewed safe-harbor wording (pending in the methodology itself) | Methodology owner | external — tracking |

## Follow-up plan index

<!-- One row per plan that closes gaps from this register, in delivery order. -->

| Plan | Closes |
|------|--------|
| [MVP-001](../plans/MVP-001-walking-skeleton.plan.md) | Baseline; GAP-B5-README, GAP-E1-AITRAILER in progress |
| [MVP-002](../plans/MVP-002-common-book-model.plan.md) | ~~GAP-E4-MASKING~~, ~~GAP-B3-BOUNDARIES~~ |
