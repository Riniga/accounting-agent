# MVP-003 – Bank import, reconciliation, remaining checks and reports via core

Roadmap: [R2 – Helsingborgs Judoklubb pilot via core](../roadmap.md#r2--helsingborgs-judoklubb-pilot-via-core-ongoing) ·
Plan: [MVP-003 plan](../plans/MVP-003-bank-reconciliation-and-reports.plan.md)

> **Corrected 2026-09-26 (plan §0.2 and §0.4, approved by the owner):**
>
> - The book model is extended: an account gets an optional group and reference
>   description, and the bank statement, fund value, budget, closing comments, to-do list
>   and reference chart get models of their own (ADR-007). The core owns these file
>   formats, including their allowed values; configuration gives paths and
>   organisation-specific values only.
> - Files the core writes — the bank statement and the reports — mask personal identity
>   numbers as `[personnummer]`, as the organisation's scripts do, so that the statement
>   can be byte-identical. Terminal output keeps `[personal number]`.
> - Findings and the `--unbooked` list show dates, amounts, statement rows and voucher
>   numbers — never a counterparty's name or a message, unlike `kontroll.py`. "The same
>   unbooked transactions" is compared on date and amount.
> - Organisation conventions come from configuration: accounts that need no supporting
>   document, the guessed-posting marker, the outlay text prefix and the parking accounts.
>   The monthly overview's fixed note about one stock account is dropped.
> - The reports are in Swedish; code, findings and terminal output stay in English
>   (ADR-008).
> - Duplicates use `kontroll.py`'s key: date, text and the amount as the bank shows it.
> - The MVP stays one MVP, although it is large.

## Purpose

After MVP-002 the core can read and check an organisation's books, but everything else in
Helsingborgs Judoklubb's bookkeeping tooling still runs on the organisation's own
scripts: importing the bank statement, reconciling it against the vouchers, the remaining
checks, and producing the accounts (the reports). The owner expected the core to cover
that tooling. This MVP moves it into the core, so that Helsingborgs Judoklubb can run its
routine through the core, except member management.

Aktivitet Förebygger produces largely the same reports with its own code, so the reports
are built for the core's general model, not for one organisation.

## Goals

- A bank export becomes the organisation's bank statement file through the core, with
  personal identity numbers masked.
- The core reconciles the books against the bank and says exactly what is unbooked or
  missing, as `kontroll.py` does today.
- Every check in Helsingborgs Judoklubb's `kontroll.py` except the member checks runs in
  the core.
- The core produces the accounts — income statement, balance sheet, general ledger and
  the others — from the books, and refuses to when the books are broken.
- Helsingborgs Judoklubb can replace `importera_kontoutdrag.py`, `kontroll.py` (except
  members) and `generera_redovisning.py` (except the member-fee report) with the core.

## Context

- MVP-002 delivered the general book model (ADR-006), the `front-matter` reader, the
  general book checks and `accounting-agent validate`. It was verified on Helsingborgs
  Judoklubb's real 2026 books.
- The tooling to move is in the organisation project's `2026/agent/`:
  - `importera_kontoutdrag.py` — bank export (Nordea CSV) → `kontoutdrag-1930.csv` and
    `fondvärde-1350.csv`, with personal-number masking;
  - `kontroll.py` — beyond what MVP-002 covered: bank reconciliation, BAS chart check,
    duplicates, date order, revenue/cost-account warnings, supporting documents, fund
    value, budget, closing comments, the to-do list, parking and unused-account
    summaries;
  - `generera_redovisning.py` — ten Markdown reports.
- `medlemskontroll.py`, the member checks in `kontroll.py` and the member-fee report are
  **not** moved (owner decision 2026-09-26; backlog).
- The core is public: it must stay free of organisation-specific values (MVP-002
  criterion). The bank's export format is named after the bank format, not the
  organisation.

## Scope

- **Bank import:**
  - a reader for the bank's export format;
  - writing the organisation's bank statement file and fund-value file, including
    Helsingborgs Judoklubb's rule of refusing an export that starts later than the
    existing file;
  - masking personal identity numbers;
  - leaving the original export untouched.

  This is the core's first **write**. It writes bank statement and fund-value files only
  — **never vouchers**.
- **Reconciliation:**
  - the bank's own balance arithmetic;
  - the opening balance compared with the bank's balance before the first transaction;
  - each bank transaction against a voucher on the bank account, and the reverse;
  - a list of unbooked transactions (`--unbooked`).

  Findings never quote a counterparty's name or a message.
- **The remaining checks from `kontroll.py`, except the member checks:**
  - the chart of accounts against the BAS reference chart;
  - duplicate vouchers;
  - date order;
  - revenue-account-debited and cost-account-credited warnings;
  - supporting documents that do not exist;
  - fund market value compared with the booked value;
  - budget file consistency;
  - closing-comments file consistency;
  - to-do list consistency;
  - parking-account and unused-account summaries;
  - the share of vouchers without supporting documents.
- **Reports** as Markdown, from the model, to a configured output folder:
  - summary, without the member part;
  - income statement;
  - balance sheet;
  - budget follow-up;
  - monthly overview;
  - general ledger;
  - voucher list;
  - to-do list;
  - closing comments.

  No reports are produced when the books have errors, unless explicitly forced.
  Personal identity numbers are masked.
- **Configuration** in `organisation.yaml`: all organisation-specific values come from
  configuration, not code. That covers the bank export format and the statement files,
  the fund account, the parking accounts, the BAS reference chart, the documents folder,
  the budget / comments / to-do files, the report output folder, the organisation's
  name and number for report headers, and the conventions: accounts that need no
  supporting document, the guessed-posting marker and the outlay text prefix.
- **Pilot on Helsingborgs Judoklubb's 2026 books:** same outcome as `kontroll.py` for
  every check in scope, and the same figures as `generera_redovisning.py` in every report
  in scope. It is verified with counts and comparisons only, as in MVP-002.
- Update `docs/development/organisation-projects.md`: what Helsingborgs Judoklubb now runs
  through the core.

## Out of Scope

- Member checks, member payments and the member-fee report (`medlemskontroll.py`) —
  backlog, high priority.
- Creating or changing vouchers; suggesting postings; agent tools, confidence, approval
  policies (R3).
- Importing the bank's transaction pages (PDF) — Helsingborgs Judoklubb's own plan (V5).
- Aktivitet Förebygger's reader, and JudoSyd.
- Scheduling and running unattended.
- Changing or removing anything in the organisation project's own scripts. Retiring them
  is the organisation's decision once the core covers them.

## Acceptance Criteria

- Synthetic fixtures — bank exports, statement files, BAS reference, budget, comments,
  to-do list, supporting documents — cover each new rule with a passing case and a broken
  variant.
- Importing Helsingborgs Judoklubb's real bank export through the core gives a statement
  file identical to the one `importera_kontoutdrag.py` produces. Verified by a byte
  comparison that reports equal / not equal only.
- On the real 2026 books, `validate` reports the same outcome per rule as `kontroll.py`
  for every check in scope, and the same unbooked transactions.
- Every report in scope shows the same figures as `generera_redovisning.py` on the same
  books. Verified by comparing the amounts per account and the totals, with counts only.
- No organisation-specific value is hard-coded in `src/`.
- **Findings** never quote a voucher text, a counterparty's name or a bank message.
- **Reports** do contain voucher texts, since the voucher list and the general ledger are
  the accounts themselves. They are written only to the organisation's own output folder,
  and personal identity numbers are masked in them.
- MVP-001's gates still hold, and the coverage floor is kept or raised.

## Outcome at close (YYYY-MM-DD)

<!-- Fill in when the MVP is actually closed. -->
