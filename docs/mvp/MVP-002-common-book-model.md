# MVP-002 – Common book model and validation via core

Roadmap: [R2 – Helsingborgs Judoklubb pilot via core](../roadmap.md#r2--helsingborgs-judoklubb-pilot-via-core-planned) ·
Plan: not yet written (created with `docs/claude-prompts/create-plan-prompt.md` once MVP-001 is closed)

## Purpose

Helsingborgs Judoklubb and Aktivitet Förebygger keep their books in the same way — a chart
of accounts and an opening balance as CSV, plus one Markdown file per voucher — but each has
its own code to read and check them. That is exactly the duplication the project exists to
remove, and it sits at the bottom of everything else: import, matching, posting, reports
and agent tools all need a correct, shared understanding of "the books".

MVP-001's baseline analysis (see its plan, §0) showed this book model — not bank import,
which is specific to one bank and one organisation — to be the strongest overlap between
the existing projects. It is therefore the first functionality to extract.

## Goals

- The core has one model of the books — accounts, opening balances, vouchers — that is
  independent of any organisation.
- The core can tell whether an organisation's books are internally consistent, with the
  same rigour as Helsingborgs Judoklubb's current checks, and says so in a way both people
  and an agent can act on (error / warning / info, with an exit code).
- Helsingborgs Judoklubb's books are validated through the core instead of through its own
  code for these checks — the first real organisation using the core.
- We know whether Aktivitet Förebygger's books fit the same model, and what is missing if
  not.

## Context

- MVP-001 delivers the package skeleton, the `run` command, organisation profiles
  (`organisation.yaml`) and the CI gates this MVP builds on.
- Helsingborgs Judoklubb's current validation lives in `kontroll.py` in its own project;
  its book format is documented in that project's bookkeeping README. Aktivitet Förebygger
  uses the same kind of voucher files, but also has voucher series (for example customer
  invoices vs. bank).
- Books are files, not a database
  ([ADR-004](../architecture/decisions/ADR-004-csv-and-markdown-storage.md)); the core holds
  no real data, so it is tested with synthetic books
  ([ADR-003](../architecture/decisions/ADR-003-no-real-data-in-core-repo.md)).
- How organisation projects consume the core long-term is still open (R3). For this MVP the
  core is simply installed locally and run as a command against the organisation's folder.

## Scope

- Core models for **account** (chart of accounts), **opening balance** and **voucher**
  (number, date, text, amount, debit account, credit account, supporting documents, free
  text).
- Reading those from an organisation's files: chart of accounts CSV, opening balance CSV,
  and a folder of Markdown voucher files with front matter. Where the files are, and
  organisation-specific values such as the bank account and the parking accounts, come from
  the organisation's configuration, not from code.
- The general checks:
  - The opening balance sums to zero.
  - Voucher numbers run 1..N without gaps or duplicates, and file names match their fields.
  - Required fields are present and unknown fields are flagged.
  - Every account used exists in the chart of accounts.
  - Debit and credit are different accounts.
  - The sign of the amount is consistent with the bank account's side.
  - Personal identity numbers in voucher text are flagged.
- Personal identity numbers are masked in everything the core logs or reports, because
  voucher texts can contain them (methodology E4 SKA 3; gap `GAP-E4-MASKING`).
- Account balances computed from the opening balance plus the vouchers.
- A command, `accounting-agent validate` (or an extension of `run` — decided in the plan),
  that reports findings as error / warning / info and exits non-zero on error.
- Helsingborgs Judoklubb's project gets the organisation configuration it needs and is
  validated through the core.
- A written comparison against Aktivitet Förebygger's voucher format: what fits, and what
  would need to change (for example voucher series).
- A short glossary of the Swedish bookkeeping terms (verifikation, kontoplan, ingående
  balans, …) and the English names used in the core.

## Out of Scope

- Bank statement import and bank ↔ voucher reconciliation — MVP-003.
- Reports (income statement, balance sheet, general ledger, …) — a later MVP.
- Creating or changing vouchers. The core only reads in this MVP; the rule that agents may
  only add vouchers, never change existing ones, becomes relevant once writing exists.
- Members, member payments, budget, comments and to-do lists — organisation-specific for
  now.
- Migrating Aktivitet Förebygger or JudoSyd onto the core.
- Agent tools, LLM calls, confidence values, approval policies.
- Replacing the whole of Helsingborgs Judoklubb's `kontroll.py` — only the checks listed
  above move. The rest stays in the organisation project until later MVPs.

## Acceptance Criteria

- Synthetic example books in `tests/fixtures/` pass validation. Deliberately broken
  variants — one per check — produce the expected error or warning.
- Run against Helsingborgs Judoklubb's real books (in its own project, not in this
  repository), the core reports the same outcome for the checks in scope as `kontroll.py`
  does today, and account balances match to the öre.
- No Helsingborgs Judoklubb name, account number or other organisation-specific value is
  hard-coded in the core. It all comes from configuration.
- The Aktivitet Förebygger comparison is written down, and any gap is either handled or
  recorded as a follow-up.
- Everything from MVP-001's gates still holds: CI green, coverage floor held, no real data
  committed.

## Outcome at close (YYYY-MM-DD)

<!-- Fill in when the MVP is actually closed. -->
