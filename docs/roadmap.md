# Roadmap

This roadmap describes the major development stages and capabilities planned for
Accounting Agent.

Each roadmap area is implemented through one or more MVPs. Once an MVP has been created, it
becomes the source of truth for that work — this file should stay a lightweight index, not
a duplicate of MVP content. See `docs/development/methodology.md` "Roadmap".

---

## Current Status

R1 is complete once PR #5 is merged:
[MVP-001 – Walking skeleton & baseline analysis](mvp/MVP-001-walking-skeleton.md) delivered
the `accounting-agent` package (v0.1.0), CI quality gates proven to block, branch
protection, the licence and the first methodology assessment. The next focus is R2,
through [MVP-002 – Common book model and validation via core](mvp/MVP-002-common-book-model.md)
(defined, plan not yet written). Before MVP-002 reads any more organisation material with
an AI tool, exception EX-003 (the AI tool's training setting) should be closed.

---

## R1 – Foundation (Done — pending merge of PR #5)

Establishes the core repository with its stack, CI quality gates and methodology baseline,
plus an analysis of the existing organisation projects that tells us what to extract first.

* [MVP-001 – Walking skeleton & baseline analysis](mvp/MVP-001-walking-skeleton.md) —
  installable package with a minimal `run` CLI, CI gates, first methodology assessment,
  and an analysis of the Helsingborgs Judoklubb project.

## R2 – Helsingborgs Judoklubb pilot via core (Planned)

Establishes the common data model and the import → matching → posting → validation →
report chain in the core, with Helsingborgs Judoklubb as the first organisation running on it.

* [MVP-002 – Common book model and validation via core](mvp/MVP-002-common-book-model.md) —
  accounts, opening balances and vouchers modelled once in the core, with the general book
  checks; Helsingborgs Judoklubb validated through it, Aktivitet Förebygger's format
  compared.
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
