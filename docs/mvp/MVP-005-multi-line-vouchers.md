# MVP-005 – Vouchers with several lines, and without a bank transaction

Roadmap: [R3 – Agent tools & human-in-the-loop](../roadmap.md#r3--agent-tools--human-in-the-loop-planned) ·
Plan: [MVP-005 plan](../plans/MVP-005-multi-line-vouchers.plan.md)

> **Corrected 2026-10-08 (owner decision, plan phase 10):** the lines form does not
> repeat `debet:` and `kredit:`. The pilot showed that Markdown tools read the fields as
> YAML and fail on a repeated key. Each of the two fields lists its lines instead,
> separated by semicolons — `kredit: 2710 9000; 1930 21000` — and the debit lines come
> before the credit lines. The example under "Scope" is updated to this form.
>
> **Corrected 2026-10-07 (plan §0.2, approved by the owner with the plan):**
>
> - A voucher is in one of two forms, never mixed: the *simple* form of today, or the
>   *lines* form with any number of `debet` and `kredit` fields, each with an account
>   and a positive amount.
> - Balance is checked by the general check (`voucher-unbalanced`), not by the format.
>   A voucher that debits and credits the same account is still an error; two debit
>   lines on the same account are allowed.
> - Generated lines: one line per posting, with the amount, in the lines form. The
>   simple form keeps its single line. The writer uses the simple form for one debit
>   and one credit line of the same amount, exactly as today.
> - `documents-expected` also names a voucher that is not on the bank account and has no
>   supporting document. A warning; documents stay optional.
> - The command refuses a voucher without a bank transaction when a voucher with the
>   same date, text and lines exists.
> - `import-bank` selects the export reader from `bank.export_format`; until now it
>   always used the Nordea reader.
> - A statement without balances gives an info finding: the bank's arithmetic and the
>   opening balance cannot be checked. Sparbanken Syd's export has no balance column.
> - A voucher belongs to at most one bank transaction. A salary run paid as several
>   bank transactions is one voucher without the bank account, and one simple voucher
>   per payment.

## Purpose

After MVP-004 the core creates a voucher for a bank transaction with one account against
the bank account. That covers Helsingborgs Judoklubb. It does not cover an organisation
that pays salaries or issues invoices:

- a salary payment is at least three lines — the gross salary, the tax withheld and the
  net amount from the bank;
- an issued invoice, an employer's contribution or a tax-account event has no bank
  transaction on the day it is recorded.

Aktivitet Förebygger does both. The owner decided on 2026-10-07 that the core has **one
book format** and that organisations adapt to it; where the format cannot hold what an
organisation needs, the one format is extended. This MVP extends it, so that Aktivitet
Förebygger can keep its books in the core's format from its supporting documents.

## Goals

- A voucher in the core's format can have any number of posting lines.
- A bank transaction can be posted against several accounts with one command.
- A voucher can be created for an event that has no bank transaction.
- Every voucher that exists today is read exactly as before, and stays valid.
- The one-format decision is recorded, and the core's documents no longer describe a
  reader per organisation.

## Context

- [MVP-004](MVP-004-create-vouchers.md) delivered `new-voucher`, the format's writer and
  the generated lines (ADR-009). It left out, on purpose, "vouchers without a bank
  transaction and vouchers with more than two lines".
- The core's model already holds vouchers with any number of lines, and the general
  checks already require that debits equal credits (ADR-006). What holds two lines only
  is the file format — one `debet` field, one `kredit` field, one `belopp` — and with
  it the reader, the writer, the generated lines and `new-voucher`.
- The reports iterate over a voucher's lines and need no change in principle.
- ADR-006 says "each file format has its own reader", and the roadmap had a reader for
  Aktivitet Förebygger's table format. The owner dropped that on 2026-10-07.
- Aktivitet Förebygger's project now has the same layout as Helsingborgs Judoklubb's.
  The reference material for 2026 was looked at by shape only (2026-10-07):
  - 11 supporting documents as Markdown: 8 invoices and 3 payslips, the payslips with
    gross salary, tax and net salary;
  - a BAS reference chart in four files, as the core already reads;
  - a bank export **without a header row** — date, text, amount with a decimal comma and
    a thousands point, currency — and without a balance column. The core reads only the
    `nordea-csv` export today;
  - a second statement with the organisation's name, an opening and a closing balance
    and four quoted columns. It looks like a tax-account statement.

## Scope

- **The format holds several lines.** A voucher file can state each posting line with
  its account and amount. The form with one `debet`, one `kredit` and one `belopp` stays
  valid and means what it means today:

  ```text
  ---
  verifikation: 12
  datum: 2026-04-25
  text: "Lön april"
  belopp: -21000
  debet: 7010 30000
  kredit: 2710 9000; 1930 21000
  underlag: 20260425-lonespecifikation.md
  ---
  ```

- **The reader** reads both forms into the same model and reports a voucher whose lines
  do not balance, or whose `belopp` disagrees with its lines.
- **The writer and the generated lines** handle any number of lines: each account is
  shown with its name and, when there are more than two lines, its amount.
- **`new-voucher` for a bank transaction with several accounts.** The caller gives the
  accounts and amounts on the other side; the bank line still comes from the bank
  statement. The command refuses when the lines do not add up to the bank amount.
- **`new-voucher` without a bank transaction.** The caller gives the date, the text and
  every line. The command refuses when the lines do not balance, when an account is not
  in the chart, when the date is outside the fiscal year, or when the bank account is
  among the lines — a voucher on the bank account always comes from a bank transaction.
- **Everything from MVP-004 still holds:** only new files, nothing written on a refusal,
  masked text and notes, output without texts or names, the guessed-posting marker.
- **Aktivitet Förebygger's bank export** as a second bank export format, so that its
  bank transactions can be imported and reconciled. Bank export formats belong to the
  banks; several of them do not contradict "one book format".
- **A new ADR** for the one-format decision, superseding ADR-006's "each file format has
  its own reader". The architecture overview's comparison of two book formats is
  replaced by what an organisation does to adopt the format.
- **Documentation:** the organisation guide and its `CLAUDE.md` snippet, with the two
  new ways to use the command.
- **Pilot on Aktivitet Förebygger's 2026 books**, built in its own project from its
  supporting documents, verified with counts only: at least one salary payment and one
  issued invoice created with the command; `validate` gives `RESULT: OK`; every bank
  transaction has a voucher.

## Out of Scope

- **Voucher series.** The format has one number sequence per year, and Aktivitet
  Förebygger adopts it.
- **Reconciling a second statement** — the tax account against its account in the books.
  Until then a tax-account event is a voucher without a bank transaction, with the
  statement as its supporting document. Backlog.
- **Calculating anything:** tax, employer's contributions, VAT or holiday pay. The
  supporting document says the amounts; the caller gives them; the core checks that they
  balance.
- **Reading supporting documents.** The agent in the organisation's project reads them.
- **Suggesting accounts**, and machine-readable posting rules (backlog from MVP-004).
- **Changing or removing a voucher.**
- **Converting Aktivitet Förebygger's earlier books.** They are built again in the
  core's format, as Helsingborgs Judoklubb's were.
- **Member management** — next after this MVP.

## Acceptance Criteria

- Synthetic fixtures cover each new rule with a passing and a broken case: a voucher
  with several lines, one that does not balance, one whose `belopp` disagrees, a bank
  transaction against several accounts, a voucher without a bank transaction, and each
  new refusal.
- Every existing test passes unchanged, and Helsingborgs Judoklubb's 2026 books give the
  same `validate` result and the same report figures as before this MVP.
- A voucher with several lines that the command creates is read back as the same
  voucher, passes `validate`, and appears in the reports with every line.
- A bank transaction posted against several accounts is no longer unbooked, and the
  bank's balance agrees with the books.
- Every refusal leaves the books byte-identical.
- The terminal output and the refusals never quote a voucher text, a name, a bank
  message or a document's file name.
- Aktivitet Förebygger's bank export is imported into the core's statement file, with
  personal identity numbers masked, and a partial export is refused as today.
- In Aktivitet Förebygger's own project: a salary payment and an issued invoice are
  created with the command from their supporting documents, `validate` gives
  `RESULT: OK`, and no bank transaction is unbooked. Reported with counts only.
- No organisation-specific value is hard-coded in `src/`.
- Tests that express the behaviour exist and are reviewed by the owner before the
  implementation (AI-TDD).
- MVP-001's gates still hold, and the coverage floor is kept or raised.

## Owner decisions (2026-10-07)

1. **The bank export.** Aktivitet Förebygger's bank is Sparbanken Syd. Its export reader
   is part of this MVP, as `sparbanken-syd-csv`.
2. **VAT.** Aktivitet Förebygger is a non-profit association and is not registered for
   VAT. The pilot has no VAT line.
3. **`belopp` in a voucher with several lines.** It stays, as the amount the bank shows —
   or the voucher's total when the bank account is not among the lines — so that a
   voucher can still be matched against the bank by eye.
4. **No series.** One number sequence, also for Aktivitet Förebygger.
5. **The tax account.** Not reconciled in this MVP; its events are vouchers without a
   bank transaction.

## Outcome at close (YYYY-MM-DD)
