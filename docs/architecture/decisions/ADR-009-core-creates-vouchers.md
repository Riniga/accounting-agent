# ADR-009: The core creates new vouchers from bank transactions — it never changes one

**Status:** Proposed — accepted together with the MVP-004 plan
**Date:** 2026-10-05

Supersedes [ADR-008](ADR-008-core-writes-derived-files.md) on one point: "never vouchers".
Everything else in ADR-008 still applies.

## Context

ADR-008 let the core write derived files only, and deferred creating vouchers to R3
"with confidence levels and approval policies". Until now a voucher has been typed by
hand, by the treasurer or by an AI agent following the organisation's routine, and the
core has checked the result afterwards.

Typing a voucher copies the date, the amount and the text from the bank statement, picks
the next number and writes the file. None of that is a decision, and each step can go
wrong. The owner wants vouchers to be right, and decided on 2026-10-05 that the tool for
creating them belongs in the core, the same for every organisation, rather than in each
organisation's own project.

Measured on Helsingborgs Judoklubb's 2026 books (counts only, 2026-10-05):

- all 163 vouchers are on the bank account and each has a bank transaction with the same
  date and amount;
- 147 of the 163 voucher texts equal the bank statement's name and message joined as
  `name(message)`, or the name alone when there is no message;
- 43 of the 163 statement rows share their date and amount with another row, so date and
  amount alone do not always identify a transaction.

A voucher is not a derived file. It records the treasurer's decision and cannot be
recreated from other files, so this write needs stricter rules than ADR-008's.

## Decision

**The core creates a new voucher for one bank transaction, on a command given by the
treasurer or an agent. It never changes or removes an existing voucher.**

- **The caller supplies decisions only:** which bank transaction, the account to post it
  against, the supporting documents, a note, and whether the posting is a guess.
- **Everything else comes from the files:** the date, the amount and the text from the
  bank statement file, the next number from the books, and debit and credit from the sign
  of the amount.
- **Refuse rather than write.** Nothing is written when the transaction does not exist or
  already has a voucher, the account is not in the chart, a document is not in the
  documents folder, the books have errors, or the new voucher would add an error.
- **One exception to "errors stop":** a bank transaction that lacks a voucher although
  later ones are booked is an error, and creating that voucher is the fix. That error
  does not block the command.
- **Only new files.** The file is created with exclusive creation, so an existing file is
  never replaced. Its path is built from the number and the date, never from the
  caller's text.
- **Generated lines.** Below the fields the command writes the debit and credit accounts
  with their names and a link to each supporting document, in Swedish, like the reports.
  The fields stay the single source. The reader keeps the generated lines out of the
  voucher's note, and reports a voucher whose generated lines disagree with its fields.
- **A guess stays a guess.** A guessed posting carries the organisation's guessed-posting
  marker and a reason; it is the only confidence level for now.
- **Masking and output:** personal identity numbers are masked in what is written. The
  terminal output names the voucher number, the date, the amount and the accounts —
  never the text, a name or a document's file name.
- **Supporting documents stay optional.** The core does not create a document to satisfy
  a rule.

The approval step is the treasurer's review: the organisation's own history (its
repository or file service) shows each new file, and the reports list every voucher and
every guess.

## Consequences

**Benefits:**

- The date, amount, text and number of a voucher can no longer be mistyped.
- A broken voucher is stopped before it exists, instead of being found afterwards.
- Every organisation on the `front-matter` format gets the same tool and the same rules.
- A voucher can be reviewed without knowing account numbers by heart.

**Trade-offs:**

- The core can now write data that cannot be recreated. The worst case is a wrong new
  voucher; removing it is a manual step and the treasurer's decision.
- The account is still a judgement, and a wrong account passes every check. This decision
  does not make the posting right; it makes everything else right.
- The generated lines repeat what the fields say and can go stale when a voucher is
  changed by hand. A check catches it, but the line then has to be edited.
- Nothing in the file records who created the voucher. The audit trail is the
  organisation's own history until R3 defines one.
- A format writer now exists next to the reader, and the two must agree; a round-trip
  test guards it.
- Two runs at the same moment can pick the same number. The next `validate` reports it.
  Accepted: one person keeps the books.

## Alternatives considered

- **Keep the command in each organisation's project** (extract it later, as ADR-002
  describes): rejected by the owner on 2026-10-05 — creating vouchers is the most central
  step and should be the same everywhere from the start.
- **Wait for R3's confidence levels, approval policies and audit trail:** rejected — the
  errors this removes happen now, and the guessed-posting marker with the treasurer's
  review covers today's need.
- **Store account names as fields:** rejected — the name would live in two places and
  could differ from the chart of accounts.
- **Require a supporting document for every voucher, creating one when none exists:**
  rejected — a document the core makes proves nothing beyond the voucher and the bank
  statement.
- **Let the command also change vouchers:** rejected — changing a voucher is the
  treasurer's explicit decision, voucher by voucher.
