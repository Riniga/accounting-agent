# Roadmap

This roadmap describes the major development stages and capabilities planned for
Accounting Agent.

Each roadmap area is implemented through one or more MVPs. Once an MVP has been created, it
becomes the source of truth for that work — this file should stay a lightweight index, not
a duplicate of MVP content. See `docs/development/methodology.md` "Roadmap".

---

## Current Status

**MVP-002 is implemented and pending its pull request.**
[MVP-002 – Common book model and validation via core](mvp/MVP-002-common-book-model.md)
delivered:
- a general double-entry book model (ADR-006);
- a reader for the `front-matter` book format;
- the general book checks;
- `accounting-agent validate`, with masked output.

Helsingborgs Judoklubb's real 2026 books validate through the core with the same outcome
as its own tool, and identical balances. Next: the Aktivitet Förebygger reader or MVP-003
(bank import and reconciliation) — to be prioritised.

*Earlier:* **R1 – Foundation is done** (MVP-001, merged in PR #5).
[MVP-001 – Walking skeleton & baseline analysis](mvp/MVP-001-walking-skeleton.md) delivered:
- the `accounting-agent` package (v0.1.0, 29 tests);
- six CI quality gates, each proven to block;
- branch protection;
- the licence;
- the first methodology assessment.

The next focus is R2, through
[MVP-002 – Common book model and validation via core](mvp/MVP-002-common-book-model.md),
which is defined but has no plan yet. The largest open methodology items are no second
reviewer (EX-001), and the AI-data gaps `GAP-F2-CONFIDENTIAL` and `GAP-F2-DPA`. Apply the
reading rule for `docs/reference/` (interpretations §9) when the MVP-002 analysis starts.

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
* MVP-003 – Bank statement import and reconciliation via core — the bank statement is
  imported and reconciled against the vouchers through the core.
* MVP-004 – Reports via core — the reports Helsingborgs Judoklubb and Aktivitet Förebygger
  both generate today, produced once by the core.

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

* Remove the remaining template leftovers — `.github/workflows/dast.yml` and the example
  section in `docs/methodology-compliance/interpretations.md`. The owner does this together
  with MVP-002. `_LÄS-MIG-FÖRST.md` and the EXAMPLE MVP and plan were removed in `947b599`.
* Raise the coverage floor once MVP-002's domain code has a stable baseline
  (interpretations §1).
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
