# Roadmap

This roadmap describes the major development stages and capabilities planned for
Accounting Agent.

Each roadmap area is implemented through one or more MVPs. Once an MVP has been created, it
becomes the source of truth for that work — this file should stay a lightweight index, not
a duplicate of MVP content. See `docs/development/methodology.md` "Roadmap".

---

## Current Status

**MVP-003 is in progress.**
[MVP-003 – Bank import, reconciliation, remaining checks and reports via core](mvp/MVP-003-bank-reconciliation-and-reports.md)
has an approved [plan](plans/MVP-003-bank-reconciliation-and-reports.plan.md) and is
being implemented on its branch. Its decisions are ADR-007 (supplementary book files) and
ADR-008 (the core writes derived files, never vouchers).

*Earlier:* **MVP-002 is merged** (PR #7).
[MVP-002 – Common book model and validation via core](mvp/MVP-002-common-book-model.md)
delivered:
- a general double-entry book model (ADR-006);
- a reader for the `front-matter` book format;
- the general book checks;
- `accounting-agent validate`, with masked output.

Helsingborgs Judoklubb's real 2026 books validate through the core with the same outcome
as its own tool, and identical balances.

*Earlier:* **R1 – Foundation is done** (MVP-001, merged in PR #5).
[MVP-001 – Walking skeleton & baseline analysis](mvp/MVP-001-walking-skeleton.md) delivered:
- the `accounting-agent` package (v0.1.0, 29 tests);
- six CI quality gates, each proven to block;
- branch protection;
- the licence;
- the first methodology assessment.

The largest open methodology items are no second reviewer (EX-001), and the AI-data gaps
`GAP-F2-CONFIDENTIAL` and `GAP-F2-DPA`. The reading rule for `docs/reference/`
(interpretations §9) applies to all extraction work.

---

## R1 – Foundation (Done)

Establishes the core repository with its stack, CI quality gates and methodology baseline,
plus an analysis of the existing organisation projects that tells us what to extract first.

* [MVP-001 – Walking skeleton & baseline analysis](mvp/MVP-001-walking-skeleton.md) —
  installable package with a minimal `run` CLI, CI gates, first methodology assessment,
  and an analysis of the Helsingborgs Judoklubb project.

## R2 – Helsingborgs Judoklubb pilot via core (Ongoing)

Establishes the common data model and the import → matching → posting → validation →
report chain in the core, with Helsingborgs Judoklubb as the first organisation running on it.

* [MVP-002 – Common book model and validation via core](mvp/MVP-002-common-book-model.md) —
  accounts, opening balances and vouchers modelled once in the core, with the general book
  checks; Helsingborgs Judoklubb validated through it, Aktivitet Förebygger's format
  compared.
* Aktivitet Förebygger reader — a reader for the table-format books (multi-line vouchers,
  voucher series) into the same core model; needed before R5. Found in the MVP-002 plan's
  investigation (§0.1).
* [MVP-003 – Bank import, reconciliation, remaining checks and reports via core](mvp/MVP-003-bank-reconciliation-and-reports.md)
  — Helsingborgs Judoklubb's agent tooling (bank import, reconciliation, the rest of
  `kontroll.py`, the reports) through the core, except member management. It replaces
  the earlier headings "MVP-003 bank import" and "MVP-004 reports" (owner decision
  2026-09-26).

## R3 – Agent tools & human-in-the-loop (Planned)

Establishes the defined agent tools, confidence levels, approval policies and the audit
trail — and decides how the core is exposed to the agent in each organisation project.

## R4 – JudoSyd migration (Planned)

Moves JudoSyd onto the core, adding PDF import, Gmail, Discord and scheduled runs as general
capabilities.

## R5 – Aktivitet Förebygger migration (Planned)

Moves Aktivitet Förebygger onto the core as a stress test, adding payroll, salary
documentation, payments and stricter approval rules as general capabilities.

## Backlog of ideas to be implemented / fixed

Ideas that come up while working on an MVP land here, not in the MVP. Format:
`* (YYYY-MM-DD, MVP-NNN) the idea`. Fixes found during an MVP are made on its branch
instead — see `docs/development/methodology.md` "Found during an MVP".

* (2026-09-26, MVP-002) **Member management via core — high priority, next after
  MVP-003.** This covers Helsingborgs Judoklubb's `medlemskontroll.py`, the member checks
  in `kontroll.py` (the member register and the member payments linked to vouchers) and
  the member-fee report. It was left out of MVP-003 by owner decision. It handles
  personal data about members and children, so it needs its own STRIDE pass, and the
  reading rule (interpretations §9) applies strictly.
* (2026-09-26, MVP-002) **No links to real consumers in this repository.** Another
  association must be able to use the core without finding any trace of the current
  organisations.
  - Remove every reference to real organisations and their specific values — names, ids
    such as `hbg-judo`, bank accounts, years, folder names — from code, **tests** (for
    example the `"Hbg Judo"` example in `tests/test_profile.py`) and user-facing docs
    (README, `organisation-projects.md`, the glossary). Use invented examples instead.
  - The code already contains none (`git grep` in `src/` is empty).
  - To decide when cleaning: what happens to the project-history documents that describe
    the real organisations (`initial-idea.md`, vision, roadmap, MVPs, plans, ADRs,
    methodology compliance). Make them neutral, or move them to a private repository?
  - Consider adding it as a principle in the vision, and as an automated check (a CI grep
    for known consumer names).

* Remove the remaining template leftovers — `.github/workflows/dast.yml` and the example
  section in `docs/methodology-compliance/interpretations.md`. The owner does this together
  with MVP-002. `_LÄS-MIG-FÖRST.md` and the EXAMPLE MVP and plan were removed in `947b599`.
* Front-matter reader: add tests for invalid UTF-8 in a *voucher* file and a blank line
  inside front matter (both implemented, not yet tested). Consider splitting
  `_read_front_matter`, which is at the advisory complexity value 10.
* Helsingborgs Judoklubb project: move the decision log ("Rättelser och beslut") out of the
  bookkeeping rules file, so that the rules can be read without personal data
  (`GAP-F2-CONFIDENTIAL`).

* Relate the books' storage and audit trail to the Swedish Bookkeeping Act
  (bokföringslagen) — archiving and verification requirements. Not critical now.
* Event-based runs in addition to scheduled ones (from the initial idea).

---

## Maintaining the Roadmap

- Update "Current Status" whenever a roadmap area's status changes.
- Add a new `## R<n> – <Area>` section when a genuinely new phase starts; don't retrofit
  history into it.
- Keep MVP links current — an MVP is the source of truth for its own scope, this file just
  points at it.
