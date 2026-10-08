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

## Outcome at close (2026-10-08)

**Delivered.** Implemented on `feature/mvp-006-judosyd-migration`, pending the pull
request. Each criterion was checked against the real system
([plan](../plans/MVP-006-judosyd-books.plan.md)):

- **The format:** a synthetic Swedbank export covers the format with a passing case and
  a broken case per rule; 838 tests pass (798 before).
- **The real exports:** both are read (17 and 1 rows), written as the core's statement
  file and read back with no finding; every row has a balance, and the balances follow
  from the amounts. Counts only.
- **Nothing changes for the first two organisations:** every earlier test passes. The
  first two readers changed in one way — a file in another encoding is refused instead
  of raising a decoding error — and their tests cover it.
- **In JudoSyd's own project** (as the owner passed on the agent's report, counts only):
  the year folder was set up with a new chart of accounts and the opening balance
  carried over, and the year was booked from the bank statement and the supporting
  documents. 17 vouchers, one per bank transaction, none with more than two lines and
  none without a bank transaction. `RESULT: OK`, 0 errors, 2 warnings — both
  `documents-expected`. No unbooked bank transaction. All four supporting documents are
  linked. 3 guessed postings, nothing on the parking account, 13 vouchers without a
  document. The reports were written. The command refused nothing.
- **The bank account's balance agrees with the bank's:** it follows from the result
  above. The statement has balances, so `validate` checks the opening balance against
  the bank's balance before the first transaction, and every transaction has a voucher
  of the same date and amount; no error was reported.
- **No organisation-specific value in `src/`:** `git grep` finds none.
- **Tests first:** written before the implementation and shown to fail for the right
  reason; reviewed with the code (EX-004).
- **MVP-001 gates:** Ruff, the pre-commit hooks, detect-secrets, the instruction-file
  scan and the tests run green locally; coverage 99.15 %, floor 97 %. Semgrep and the
  dependency checks run in the pull request (no dependency changed).

**What the pilot showed:**

- **This organisation needed nothing of MVP-005.** Every voucher was a bank transaction
  against one account.
- **The change of chart of accounts worked through the prompt.** The agent mapped the
  earlier chart to the new one: the bank account and the second account got new numbers,
  two equity accounts became one, the earmarked funds were renumbered, and four accounts
  are the organisation's own, outside the reference chart. Three postings are guesses
  because two earlier accounts have no counterpart in the reference chart.
- **A statement of another account could not be linked to its voucher,** because it lay
  beside the bank export and not in the documents folder. The set-up prompt now says so.
- **The local check missed a new file.** The hooks were run over "all files", which
  means the files git tracks; a new test file was not among them, and the secret scan
  stopped the owner's commit on a test variable's name. The hooks are now run on changed
  and new files alike before a hand-over.

**Left for the treasurer in JudoSyd's project,** as the agent's report lists it: to
approve the mapping of the opening balance and the three guesses; whether a remaining
receivable is written off, which has no bank transaction and no document yet; whether
one cost is taken from earmarked funds or shown in the result; and the missing
supporting documents.

**Not proven, or not possible yet:**

- **The new books were not compared with the earlier system's.** The owner chose new
  books without a parallel run. The old year folder is the way to check.
- **The second bank account is not reconciled.** Its one transaction this year is a
  transfer, booked from the main account's statement.
- **Nothing tells `import-bank` which account's export it is given.** Backlog.
- **Reports as PDF, issuing invoices, and the assistant's mail and notices** are outside
  the core, as decided.
- The credential files in the earlier reference copy are the owner's to remove; whether
  that is done is not known here.
