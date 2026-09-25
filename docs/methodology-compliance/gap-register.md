# Gap register

Every open gap between this project and [the development methodology](../methodology/index.md)
(or your own organisation's equivalent).

If you keep a "known gaps" table anywhere else (e.g. `docs/architecture/current-state.md`),
point it here instead of duplicating — this file is the one source of truth.

A living document (methodology D3 BÖR 2): rows are added when a gap is found, updated as
follow-up plans progress, and struck through (`~~GAP-ID~~`) when closed.

**Last updated:** *(date of last change)*

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
<!-- Add rows as gaps are found during the initial assessment (see the area files in this
     directory, using _template.md). -->

### Severity M

| ID | Chapter | Gap | Owner | Follow-up | Status |
|----|---------|-----|-------|-----------|--------|

### Severity L

| ID | Chapter | Gap | Owner | Follow-up | Status |
|----|---------|-----|-------|-----------|--------|

### External dependencies (not a platform gap)

| ID | Chapter | Item | Owner to confirm | Status |
|----|---------|------|------------------|--------|

## Follow-up plan index

<!-- One row per plan that closes gaps from this register, in delivery order. -->

| Plan | Closes |
|------|--------|
