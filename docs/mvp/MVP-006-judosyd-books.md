# MVP-006 – JudoSyd's books in the core's format

Roadmap: [R4 – JudoSyd migration](../roadmap.md#r4--judosyd-migration-ongoing) ·
Plan: [MVP-006 plan](../plans/MVP-006-judosyd-books.plan.md)

> **Approved by the owner 2026-10-08, with the answers below.** The first proposal, the
> same day, was to build the books *alongside* the existing bookkeeping system and
> compare the two before any switch. The owner chose otherwise: JudoSyd starts new books
> for 2026 in the core's format, exactly as the first two organisations did, and keeps
> the old year folder aside for the time being.

## Purpose

Helsingborgs Judoklubb and Aktivitet Förebygger keep their books through the core. The
owner decided on 2026-10-08 that JudoSyd is next, and that it is to be done the same way:
as alike the first two as possible.

JudoSyd's books have been kept in a commercial bookkeeping system. An AI assistant
already works for its treasurer, but it does not keep the books: it handles incoming
mail, files invoices and receipts, and summarises exported reports. This MVP gives
JudoSyd books in the core's format for 2026, built from its bank statement and its
supporting documents.

## Goals

- JudoSyd's bank transactions are imported and reconciled through the core.
- JudoSyd's 2026 is kept in the core's format, built with `new-voucher`.
- JudoSyd changes its chart of accounts in the move, and its opening balance is carried
  over to the new chart.
- The treasurer gets the core's reports, and a list of what is guessed and what lacks a
  supporting document.

## Context

- The core has one book format, and an organisation adopts it by building its books
  again from its bank statement and supporting documents; the core does not convert
  books ([ADR-010](../architecture/decisions/ADR-010-one-book-format.md)).
- [MVP-004](MVP-004-create-vouchers.md) and [MVP-005](MVP-005-multi-line-vouchers.md)
  gave the command for that, and two prompts that set up an organisation's year folder
  and book a year.
- JudoSyd's new year folder has the same layout as the first two organisations'. Its
  reference copy was looked at by shape only (2026-10-08):
  - a BAS reference chart in four files, as the core reads today;
  - two bank exports from Swedbank, one per account: comma-separated, in Windows-1252,
    newest first, with a title line, a header row, the bank's row number and a balance
    after every transaction. 17 transactions on the main account, 1 on the other;
  - four supporting documents;
  - the opening balance as a text report from the earlier system, 11 accounts in the
    earlier chart; and a short budget note.
- The roadmap's R4 said the migration adds "PDF import, Gmail, Discord and scheduled runs
  as general capabilities". JudoSyd's assistant has those in its own project, and they
  serve one organisation. Code moves to the core only when a second organisation uses it
  (ADR-002).

## Scope

- **A Swedbank bank export format**, `swedbank-csv`, so that JudoSyd's bank transactions
  can be imported and reconciled, balances included.
- **JudoSyd's year folder set up in the core's format**, with the existing set-up prompt.
  The prompt is extended for what is new here: **a change of chart of accounts**, where
  the opening balance from the earlier chart is mapped to the new one and the mapping is
  the treasurer's to approve.
- **JudoSyd's 2026 booked with `new-voucher`**, from the bank statement and the
  supporting documents, by the agent in JudoSyd's project, with the existing prompt.
- **Documentation:** the organisation guide, and the two prompts.

## Out of Scope

- **Comparing with the earlier system's books**, as the first proposal had it. The old
  year folder stays aside; the treasurer can compare when there is a reason to.
- **Reconciling the second bank account.** The core reconciles one bank account. A
  transaction on the other account is a voucher without a bank transaction, with that
  account's statement as its supporting document — as for a tax account. Backlog.
- **Reports as PDF.** The board gets Markdown for now, and PDF by hand; a later MVP,
  perhaps.
- **Issuing invoices and sending reminders.** The core records an invoice; it does not
  produce one. The owner accepts that.
- **Moving mail, calendar, notices or scheduling into the core.** They stay in JudoSyd's
  project until a second organisation needs them.
- **Completing the supporting documents.** They are not all in the year folder yet; the
  reports say which vouchers lack one.
- **VAT.** JudoSyd is not registered for VAT.
- **Member management**, and earlier years in the archive.

## Acceptance Criteria

- A synthetic Swedbank export covers the new format with a passing case and a broken
  case per rule.
- JudoSyd's real exports are read, written as the core's statement file and read back
  with no finding, and the bank's own balances add up. Counts only.
- Every existing test passes, and nothing changes for the first two organisations.
- In JudoSyd's own project: the year folder is set up with the new chart of accounts and
  the opening balance carried over; `validate` gives `RESULT: OK`; every transaction on
  the main bank account has a voucher; the reports are written. Reported with counts
  only.
- The bank account's balance in the books agrees with the bank's balance on the last
  day of the statement.
- No organisation-specific value is hard-coded in `src/`.
- The tests are written first and shown to fail for the right reason (EX-004).
- MVP-001's gates still hold, and the coverage floor is kept or raised.

## Owner decisions (2026-10-08)

1. **New books, like the others.** A new year folder for 2026 in the core's format; the
   old one stays aside for the time being. No parallel run.
2. **The bank exports** are in the organisation's project, and in the reference copy.
3. **The fiscal year** is the calendar year.
4. **Customer invoices:** the core does not issue them, and that is accepted.
5. **VAT:** JudoSyd has an organisation number and is registered, but not for VAT.
6. **Reports:** Markdown for now. PDF is made by hand, and may become an MVP later.
7. **Supporting documents** are not complete yet. The booking run reports what is
   guessed and what is missing; the treasurer completes it then.
8. **The chart of accounts changes** in the move.

## Outcome at close (YYYY-MM-DD)
