# Roadmap

This roadmap describes the major development stages and capabilities planned for
Accounting Agent.

Each roadmap area is implemented through one or more MVPs. Once an MVP has been created, it
becomes the source of truth for that work — this file should stay a lightweight index, not
a duplicate of MVP content. See `docs/development/methodology.md` "Roadmap".

---

## Current Status

**MVP-004 is implemented and pending its pull request.**
[MVP-004 – Create vouchers from bank transactions via core](mvp/MVP-004-create-vouchers.md)
delivered `new-voucher`: one command creates the voucher for a bank transaction from the
caller's decisions, and refuses rather than writes a wrong one (ADR-009). Helsingborgs
Judoklubb's whole 2026 was built again from nothing with it. Next: vouchers with several
lines and vouchers without a bank transaction, which payroll and invoices need (owner
direction 2026-10-07, see R2); then member management via core.

*Earlier:* **MVP-003 is merged** (PR #13).
[MVP-003 – Bank import, reconciliation, remaining checks and reports via core](mvp/MVP-003-bank-reconciliation-and-reports.md)
delivered:
- bank import (`import-bank`, the `nordea-csv` format) into masked statement and
  fund-value files — the core's first writes (ADR-008);
- reconciliation against the bank, and every other check in `kontroll.py` except members;
- the reports as Swedish Markdown (`report`);
- models and core-owned formats for the supplementary files (ADR-007).

Helsingborgs Judoklubb's 2026 books give the same statement file, the same check
outcome and the same report figures as its own scripts.

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
* ~~Aktivitet Förebygger reader — a reader for the table-format books.~~ **Dropped by
  owner decision 2026-10-07: the core has one book format, and organisations adapt to
  it.** The platform is meant for many organisations, so a reader per organisation does
  not scale. Aktivitet Förebygger moves its books to the core's format. Where the
  format cannot hold what an organisation needs, the one format is extended: it must
  get vouchers with several lines and vouchers without a bank transaction. To record
  as an ADR that supersedes ADR-006's "each file format has its own reader", in the
  next MVP.
* [MVP-003 – Bank import, reconciliation, remaining checks and reports via core](mvp/MVP-003-bank-reconciliation-and-reports.md)
  — Helsingborgs Judoklubb's agent tooling (bank import, reconciliation, the rest of
  `kontroll.py`, the reports) through the core, except member management. It replaces
  the earlier headings "MVP-003 bank import" and "MVP-004 reports" (owner decision
  2026-09-26).

## R3 – Agent tools & human-in-the-loop (Planned)

Establishes the defined agent tools, confidence levels, approval policies and the audit
trail — and decides how the core is exposed to the agent in each organisation project.

* [MVP-004 – Create vouchers from bank transactions via core](mvp/MVP-004-create-vouchers.md)
  — **implemented, pending its pull request.** One command writes the voucher from the bank
  statement; the agent or the treasurer supplies only the account, the supporting
  document and whether it is a guess. Supersedes ADR-008's "never vouchers" with a new
  ADR.

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
  MVP-004** (owner decision 2026-10-05; before that, next after MVP-003). This covers Helsingborgs Judoklubb's `medlemskontroll.py`, the member checks
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

* (2026-10-05, MVP-004) Machine-readable posting rules: the voucher command warns when
  the chosen account differs from the organisation's rule for that kind of transaction.
  Wait until the command from MVP-004 is in use.
* (2026-10-05, MVP-004) Supporting documents named from what is known when they are
  saved (date, direction, amount), never from a voucher number, so that a document can
  be paired with an unbooked bank transaction by a script.

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
