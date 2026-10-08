# MVP-004 – Create vouchers from bank transactions via core

Roadmap: [R3 – Agent tools & human-in-the-loop](../roadmap.md#r3--agent-tools--human-in-the-loop-planned) ·
Plan: [MVP-004 plan](../plans/MVP-004-create-vouchers.plan.md)

> **Corrected 2026-10-05 (plan §0.2, approved by the owner with the plan):**
>
> - "Errors stop" has one exception: a bank transaction that lacks a voucher although
>   later ones are booked is an error, and creating that voucher is the fix. That error
>   does not block the command (ADR-009).
> - Date and amount do not always identify a bank transaction. The caller also gives the
>   statement row when more than one row has that date and amount.
> - `validate` gives the **number** of documents no voucher refers to. Their names are
>   listed in the to-do report, since a file name can hold a person's name.
> - Cost vouchers without a document are named by voucher number in one warning.
> - Generated lines: account numbers that disagree with the fields are an error; an
>   account name that differs from the chart is a warning.
> - The voucher's text is the statement row's name and message as `name(message)`, or the
>   name alone when there is no message.

## Purpose

Today a voucher is typed by hand, by the treasurer or by an AI agent following the
organisation's routine. The core only checks the result afterwards. Typing copies the
date, the amount and the text from the bank statement, picks the next number and writes
the file — every one of those steps can go wrong, and none of them is a decision.

The owner wants vouchers to be right, and wants the same tool for every organisation
(owner decision 2026-10-05: the tool belongs in the core, not in each organisation's
project). This MVP gives the core a command that writes the voucher. The agent or the
treasurer supplies only the decisions: which account, which supporting document, and
whether the posting is a guess.

## Goals

- A voucher for a bank transaction is created by one command. Its date, amount, text and
  number come from the books and the bank statement, never from the caller.
- A voucher that would break the books is refused before anything is written.
- A voucher can be reviewed without knowing account numbers by heart: it shows the
  accounts' names and a link to each supporting document.
- The only thing left to get wrong is the choice of account and document, and that is
  what the treasurer reviews.

## Context

- MVP-003 delivered bank import, reconciliation (`validate --unbooked` lists bank
  transactions without a voucher), the detail checks and the reports.
- [ADR-008](../architecture/decisions/ADR-008-core-writes-derived-files.md) says the core
  writes only derived files and **never vouchers**, and defers creating vouchers to R3
  "with confidence levels and approval policies". This MVP changes that decision, so it
  needs a new ADR that supersedes ADR-008 on this point.
- A voucher is not a derived file: it records the treasurer's decision and cannot be
  recreated from other files. That is why this write is treated more strictly than the
  writes in MVP-003.
- In the `front-matter` book format, the bookkeeping reads only the fields at the top of
  a voucher file. The text below the fields is free.
- The organisations' own rule already says that scripts and agents may only **create**
  vouchers; an existing voucher is changed only after the treasurer's explicit decision.
- `organisation.yaml` already holds the conventions this needs: the bank account, the
  documents folder, the guessed-posting marker and the accounts that need no document.

## Scope

- **A command that creates one voucher from one bank transaction.** The caller gives:
  - which bank transaction (date and amount, and which one when several are equal);
  - the account to post it against;
  - optionally one or more supporting documents;
  - optionally a note, and whether the posting is a guess.

  The command takes the date, the amount and the text from the bank statement file, takes
  the next voucher number from the books, and decides debit and credit from the sign of
  the amount.
- **Refusals.** Nothing is written when:
  - the bank transaction does not exist, or already has a voucher;
  - the account is not in the chart of accounts;
  - a supporting document is not in the documents folder;
  - the books have errors before the command runs;
  - the file to write already exists.
- **Only new files.** The command never changes or removes an existing voucher.
- **A readable voucher.** Below the fields the command writes generated lines: the debit
  and credit accounts with their names from the chart, a link to each supporting
  document, the guessed-posting marker when the posting is a guess, and the caller's
  note. The fields stay the single source: account names are not stored as fields.
- **Personal identity numbers** are masked in everything the command writes.
- **Checks in `validate`:**
  - the generated account line agrees with the voucher's fields, for vouchers that have
    the line;
  - each cost voucher without a supporting document is listed (today only the count is
    shown), except on the accounts configured as needing none;
  - files in the documents folder that no voucher refers to are listed.
- **Supporting documents stay optional.** A document is required only by warning, for
  costs. The core does not create a document to satisfy the rule.
- **The first book format only:** `front-matter`.
- **A new ADR** that supersedes ADR-008's "never vouchers", with the rules above.
- **A STRIDE pass** in the plan: this is the core's first write to data that cannot be
  recreated.
- **Documentation:** `organisation-projects.md`, including the `CLAUDE.md` snippet for
  organisation projects, says that vouchers are created with the command and not by hand.
- **Pilot on Helsingborgs Judoklubb's 2026 books**, verified with counts and comparisons
  only, as in MVP-002 and MVP-003.

## Out of Scope

- Changing, reversing or removing an existing voucher — the treasurer's decision, and a
  separate command if it is ever needed.
- Vouchers without a bank transaction (accruals, depreciation, moving an amount between
  accounts) and vouchers with more than two lines.
- Suggesting the account, and machine-readable posting rules that warn when the chosen
  account differs from the rule. Backlog: it is the natural next step, but it should
  wait until this command is in use.
- Reading the content of supporting documents (PDF, images), and renaming them.
- Adding the generated lines to vouchers that already exist — that changes existing
  vouchers and needs the treasurer's decision.
- Allocating a payment to a member (member management, backlog).
- Approval workflows and confidence levels beyond the existing guessed-posting marker.
- Aktivitet Förebygger's book format, and JudoSyd.

## Acceptance Criteria

- Synthetic fixtures cover the command with a passing case and one broken case per
  refusal, and each new check with a passing and a broken case.
- A voucher created by the command passes `validate` with no new error, and the bank
  transaction no longer appears in `--unbooked`.
- Every refusal leaves the books folder byte-identical to before the command.
- Running the command twice for the same bank transaction creates one voucher; the
  second run is refused.
- The command's terminal output and findings never quote a voucher text, a counterparty's
  name, a bank message or a document's file name.
- On Helsingborgs Judoklubb's real 2026 books: for each existing voucher on the bank
  account, the fields the command would write from the bank statement and that voucher's
  account are compared with the existing fields. The number of equal and unequal vouchers
  is reported, and each kind of difference is explained.
- The treasurer creates the vouchers for at least one real batch of unbooked
  transactions with the command, and `validate` then gives `RESULT: OK` with no unbooked
  transaction before the last voucher.
- No organisation-specific value is hard-coded in `src/`.
- Tests that express the behaviour exist and are reviewed by the owner before the
  implementation (AI-TDD).
- MVP-001's gates still hold, and the coverage floor is kept or raised.

## Owner decisions (2026-10-05)

1. **Order.** This MVP comes before member management.
2. **Language of the generated lines.** Swedish, like the reports (ADR-008): they are part
   of the organisation's books and are read by the treasurer.
3. **Books with errors.** The command refuses when `validate` gives errors. Warnings do
   not block.

## Outcome at close (2026-10-07)

**Delivered.** Implemented on `feature/mvp-004-create-vouchers`, pending the pull
request. Each criterion was checked against the real system
([plan](../plans/MVP-004-create-vouchers.plan.md), phases 2–7):

- **Fixtures per rule:** synthetic fixtures cover the command, every refusal and each
  new check with a passing and a broken case; 576 tests pass (423 before).
- **A created voucher is valid:** it passes `validate` with no new error, and its bank
  transaction is no longer unbooked — in the tests and on a real run of the command.
- **A refusal writes nothing:** every refusal test compares every file under the
  organisation byte for byte, before and after.
- **Twice gives one voucher:** the second run is refused as `already-booked`.
- **Nothing is quoted:** the output and the refusals never hold a voucher text, a name,
  a bank message or a document's file name; tests assert it for each rule.
- **Compared with the real 2026 books:** each of Helsingborgs Judoklubb's 163 vouchers
  was built again from its statement row and its own account. Number, date, accounts
  and amount were equal on all 163, the text on 147. The 16 texts that differ: 4 hold a
  personal identity number, which the core masks; 1 is the name without the message;
  11 were edited by hand. No second systematic rule was found.
- **A real batch — exceeded.** The criterion asked for one batch of unbooked
  transactions. Instead the owner removed every voucher and all reports in the
  organisation's own project and let the AI agent there build the year from nothing
  with the command, choosing accounts from the organisation's rules and linking the
  supporting documents. The reports' own measures afterwards: 0 errors, 0 unbooked
  transactions, and the bank's balance agrees with the books. Before that, the same
  rebuild in a scratch copy with the originals' decisions gave the same balance on all
  25 accounts.
- **No organisation-specific value in `src/`:** `git grep` for the organisations'
  names, ids, accounts and markers finds none.
- **AI-TDD:** in every phase the tests were written first, shown to fail for the right
  reason and reviewed by the owner before the implementation.
- **MVP-001 gates:** Ruff, the pre-commit hooks, detect-secrets, the instruction-file
  scan and the tests run green locally; coverage 98.99 %, floor 97 %. Semgrep and the
  dependency checks run in the pull request (no dependency changed).

**Left for the treasurer in the rebuilt books**, as the reports list it: 20 guessed
postings, 2 postings on the parking account, and 21 payments without a supporting
document, 9 of them outlays. This is the judgement the command does not make. The
account choices in the rebuilt books have not yet been compared with the earlier ones.

**Changed from the definition** (each recorded in the plan under its TODO):
`documents-expected` follows the to-do report's rule, money out of the bank, and gives
one warning per voucher; unused documents are counted in the terminal and named only in
the to-do report.

**Not proven, or not possible yet:**

- A voucher whose text was edited by hand no longer matches its statement row; among
  several transactions with the same date and amount the wrong row can then be booked
  without `validate` seeing it. Accepted in the plan (§5).
- Books without vouchers have errors while the closing comments refer to vouchers, so a
  rebuild from nothing needs the comments file detached meanwhile.
- Vouchers with more than two lines, and vouchers without a bank transaction, cannot be
  created. Payroll and invoices need both. Next MVP.
