# Plan: MVP-005 – Vouchers with several lines, and without a bank transaction

Reference: [`docs/mvp/MVP-005-multi-line-vouchers.md`](../mvp/MVP-005-multi-line-vouchers.md)

**Status:** In progress (plan approved 2026-10-07)

## 0. Investigation

Carried out 2026-10-07 with read-only commands.

### 0.1 Baseline

| Measure | Value |
|---|---|
| Core, on `main` after MVP-004 (PR #14) | 576 tests pass; coverage 98.99 %, floor 97 % |
| Commands | `run`, `validate`, `import-bank`, `report`, `new-voucher` |
| Book format | one debit account, one credit account and one amount per voucher |
| Bank export formats | `nordea-csv` only; `import-bank` calls that reader directly |

Where the code assumes two lines per voucher:

| Place | Assumption |
|---|---|
| `formats/front_matter.py`, reader | one `debet`, one `kredit`; a repeated field is an error |
| `formats/front_matter.py`, generated lines | one line `Debet … · Kredit …` |
| `formats/front_matter.py`, `render_voucher()` | refuses anything but one debit and one credit line |
| `books/posting.py`, `build_voucher()` | one account against the bank account |
| `cli.py`, `new-voucher` | `--account`; the output unpacks two lines |

Where it does not: the model (`Voucher.lines`), the general checks (`voucher-unbalanced`,
`voucher-same-account`, `voucher-unknown-account`), balances, reconciliation (the net on
the bank account), the detail checks and the reports all iterate over the lines.

Aktivitet Förebygger's reference material for 2026, by shape only:

| Material | Shape |
|---|---|
| Supporting documents | 11 Markdown files: 8 invoices, 3 payslips with gross salary, tax and net salary |
| Reference chart | four CSV files, as the core reads today |
| Bank export | 16 rows, **no header row**, 5 fields `date;text;amount;currency;` with an empty last field; UTF-8 with BOM; amounts with a thousands point and a decimal comma; newest first; every row SEK; no balance column; no quoted fields |
| Second statement | 4 quoted columns; first the organisation's name and number, an opening-balance row, then date, text, amount and balance, and a closing-balance row. Not a bank export: it looks like a tax-account statement |

### 0.2 Where the MVP needs correcting or completing

1. **The form of a line.** The MVP proposes repeated `debet:` and `kredit:` fields with
   an account and an amount. **The plan:** a voucher is in one of two forms, never mixed:
   - *simple* — one `debet` and one `kredit` with an account only; the amount is
     `belopp`. Exactly today's form;
   - *lines* — any number of `debet` and `kredit` fields, each `<account> <amount>`,
     with a positive amount. The lines are kept in the order they are written.
2. **`belopp` in the lines form** (owner decision 3): the net on the bank account, signed
   as the bank shows it, or the voucher's total when the bank account is not among the
   lines. A `belopp` that disagrees with the lines is an error. This replaces the
   bank-sign rule for the lines form.
3. **Balance is checked where it already is.** The reader reads an unbalanced voucher
   and the general check reports it (`voucher-unbalanced`); the format gets no second
   rule for it.
4. **`voucher-same-account` stays an error.** A voucher that debits and credits the same
   account is still refused. Two debit lines on the same account are allowed — two
   employees' salaries, for example.
5. **Generated lines for several lines.** One generated line per posting, with the
   amount: `Debet 7010 Löner 30000`. A voucher in the simple form keeps today's single
   line, so every voucher `new-voucher` has created so far stays valid.
6. **The writer chooses the form.** One debit and one credit line of the same amount is
   written in the simple form, exactly as today; anything else in the lines form.
7. **A voucher without a bank transaction has nothing behind it but its document.**
   **The plan:** `documents-expected` also names a voucher that is not on the bank
   account and has no supporting document. A warning, as today — documents stay
   optional (owner decision, MVP-004).
8. **Running twice.** A bank transaction can be booked once; a voucher without one has
   no such anchor. **The plan:** the command refuses a voucher without a bank
   transaction when a voucher with the same date, text and lines exists.
9. **The bank export format is not selected today.** `import-bank` calls the Nordea
   reader whatever `bank.export_format` says. **The plan:** the configured format
   selects the reader.
10. **A statement without balances cannot be checked against itself.** Reconciliation
    skips the balance arithmetic and the opening-balance check silently when no row has
    a balance. **The plan:** an info finding says so, so that "the bank agrees" is not
    read as more than it is.
11. **Not registered for VAT** (owner, 2026-10-07): the pilot has no VAT line. A VAT line
    is an ordinary line and needs nothing of its own.

### 0.3 Reading rule (interpretations §9)

The new reference material holds supporting documents and bank files, which are
Confidential. They were read by shape: counts, extensions, column counts, header rows,
and lines with letters and digits masked.

One command meant to print table header rows also printed five data rows from the
payslips: three gross salary amounts and two line descriptions. Nothing was copied into
the repository. Noted under `GAP-F2-CONFIDENTIAL` in TODO 9.4.

The organisation's number is in the second statement's first row. It is not used in the
repository.

### 0.4 Owner decisions (2026-10-07)

1. One book format; organisations adapt to it (ADR-010). No reader for another book
   format.
2. Aktivitet Förebygger's bank is Sparbanken Syd. Its export reader is part of this MVP.
3. Aktivitet Förebygger is not registered for VAT.
4. `belopp` stays in a voucher with several lines (§0.2 point 2).
5. No voucher series: one number sequence per year.
6. The tax account is not reconciled in this MVP; its events are vouchers without a bank
   transaction.
7. Approved with the plan: the `duplicate` refusal for vouchers without a bank
   transaction (§0.2 point 8), and `documents-expected` for them (§0.2 point 7).

### 0.5 Other findings

- **No new dependencies.**
- **Module boundary** as in MVP-004: the domain builds and refuses, `formats/` reads,
  renders and writes, the CLI wires and prints.
- **Bank export name:** `sparbanken-syd-csv`, after the bank, like `nordea-csv`.
- **The reader's field parser is at the advisory complexity value** (roadmap backlog).
  Reading repeated fields is a reason to split it; the split is part of phase 2, with
  no change in behaviour for existing files.
- **Fixtures:** a second set of synthetic books with vouchers in the lines form, so that
  `valid` and the tests that count its findings stay untouched.

## 1. Goal

When this plan is done:

- A voucher file can be in the lines form:

  ```text
  ---
  verifikation: 12
  datum: 2026-04-25
  text: "Lön april"
  belopp: -21000
  debet: 7010 30000
  kredit: 2710 9000
  kredit: 1930 21000
  underlag: 20260425-lonespecifikation.md
  ---

  Debet 7010 Löner 30000
  Kredit 2710 Personalskatt 9000
  Kredit 1930 Bankkontot 21000
  Underlag: [20260425-lonespecifikation.md](<../../underlag/20260425-lonespecifikation.md>)
  ```

- `new-voucher` has three uses:
  - `--date … --amount … --account …` — a bank transaction against one account (today);
  - `--date … --amount … --debit <account>=<amount> --credit <account>=<amount> …` — a
    bank transaction against several accounts; the bank line comes from the statement;
  - `--date … --text … --debit … --credit …`, without `--amount` — a voucher without a
    bank transaction.
- `import-bank` reads the export format that `bank.export_format` names, and
  `sparbanken-syd-csv` is one.
- ADR-010 is accepted and ADR-006's status points at it.
- Aktivitet Förebygger's project keeps its 2026 books in the core's format, with at
  least one salary payment and one issued invoice created by the command.

## 2. Scope boundary

- **In:**
  - `src/accounting_agent/formats/front_matter.py` — the lines form in the reader, the
    generated lines and the writer;
  - `src/accounting_agent/formats/` — a `sparbanken_syd_csv.py` export reader;
  - `src/accounting_agent/books/posting.py` — several lines, and no bank transaction;
  - `src/accounting_agent/books/details.py` — `documents-expected` for vouchers off the
    bank account; `books/reconciliation.py` — the info finding for no balances;
  - `profile.py`, `cli.py`;
  - tests and synthetic fixtures under `tests/`;
  - ADR-010, ADR-006's status line, the glossary, `overview.md` (the "Book formats"
    section), `current-state.md`, `README.md`, `AGENTS.md`, `roadmap.md`,
    `organisation-projects.md`, the MVP-005 document, methodology compliance;
  - a prompt under `docs/claude-prompts/` for setting up an organisation in the core's
    format.
- **Out:**
  - voucher series;
  - reconciling the tax account, and reading its statement;
  - calculating tax, employer's contributions, VAT or holiday pay;
  - reading supporting documents;
  - changing or removing vouchers;
  - converting books from another layout;
  - renaming `books.format` or its value;
  - member management; new dependencies.

## 3. Chapters addressed

- **B3** Architecture principles — one format (ADR-010); the domain stays free of I/O.
- **B5** Documentation — ADR-010, glossary, README, the organisation guide.
- **C1** SKA 4 — STRIDE pass (§5): a new input (lines and a caller-supplied text) and a
  new external file format.
- **D1** — AI-TDD with the owner's review of the tests before each implementation.
- **E4** SKA 3 — masking in the new export reader and in caller-supplied text.
- **F2** SKA 2 — the reading rule (§0.3); `GAP-F2-CONFIDENTIAL` gets a note.

No gap-register row is expected to close.

## 4. TODOs

Every phase that adds production code follows the MVP-002 pattern: tests first, **STOP
for the owner's review of the tests**, then the implementation. Each test must fail for
the right reason before the implementation is written. Every phase runs `pytest` and
`ruff check` before its commit, and updates `current-state.md` in the same phase.

### Phase 1 — Decisions

- [x] 1.1 Update the MVP-005 document with a dated correction note per §0.2.
  *Verify:* every change traces to §0.
  Result: a correction note with eight points; seven trace to §0.2, and the last (one
  voucher, at most one bank transaction) to §5.
- [x] 1.2 Set ADR-010 to Accepted; change ADR-006's status line to "Accepted — superseded
  in part by ADR-010"; add the index row. *Verify:* ADR-006's body is unchanged.
  Result: done; `git diff` on ADR-006 shows the status line only.
- [x] 1.3 Rewrite `overview.md` "Book formats": one format, what belongs to others
  (bank exports), and what an organisation does to adopt the format. Update the table in
  `organisation-projects.md`. *Verify:* no document says a reader per organisation is
  planned, except as history.
  Result: the section is rewritten; the two-format comparison is gone from it and stays
  in the MVP-002 plan as history. "Planned evolution" no longer lists a second reader,
  and the workspace tree says "the book format's reader and writer". The organisation
  guide's table drops the "Book format" column.
- [x] 1.4 Glossary: the simple form and the lines form.
  Result: two rows.

Commit: `docs(mvp-005): approve the plan and accept ADR-010`

### Phase 2 — The reader: the lines form

- [x] 2.1 **Tests first** (`tests/test_front_matter_lines.py`, fixtures under
  `tests/fixtures/books/lines/`):
  - a voucher in the lines form is read with its lines in the written order, debits and
    credits mixed;
  - a voucher in the simple form is read exactly as today, and `valid` gives no finding;
  - two debit lines on the same account are read as two lines;
  - `belopp` equals the net on the bank account, or the total without one; otherwise
    error `amount-mismatch`;
  - an unbalanced voucher is read, and `check_books` reports `voucher-unbalanced`;
  - errors: a line that is not `<account> <amount>` (`invalid-line`); a negative or zero
    amount on a line (`invalid-line`); forms mixed, or a repeated field without an
    amount (`lines-mixed`); only debit lines or only credit lines (`missing-field`);
  - documents, note and number are read as in the simple form;
  - no finding quotes a text or a name.

  *Verify:* the tests fail for the right reason. **STOP for review.**
  Result: `tests/test_front_matter_lines.py`, 32 tests, and the synthetic books
  `tests/fixtures/books/lines/` with five vouchers: a salary paid from the bank (three
  lines), the employer's contribution (two lines in the lines form), an invoice and its
  payment (the simple form), and a salary run without the bank account (four lines, two
  on the same account, a credit written first). 27 fail for the right reason: today's
  reader gives `duplicate-field` and `bank-sign` for the lines form. 5 pass already: two
  pin the simple form, and three assert that findings quote nothing, which today's
  findings do not either. Locked by the tests:
  - the form is *lines* when a `debet` or `kredit` field is repeated or carries an
    amount; otherwise *simple*;
  - a line is `<account> <amount>`, the amount positive with at most two decimals;
    anything else is `invalid-line` and the voucher is skipped;
  - a line without an amount in the lines form is `lines-mixed`, and the voucher is
    skipped;
  - `amount-mismatch` when `belopp` is not the net on the bank account, or the total
    without one; the voucher is still read from its lines;
  - the simple form keeps `bank-sign`; other fields still give `duplicate-field`;
  - an unknown account, an unbalanced voucher and an account on both sides are left to
    the general checks.
- [ ] 2.2 Implement; split the field parser where it helps. *Verify:* the 576 existing
  tests pass unchanged.

Commit: `feat(formats): read vouchers with several posting lines`

### Phase 3 — Generated lines and the writer

- [ ] 3.1 **Tests first:**
  - the reader recognises one generated line per posting at the top of the body, keeps
    them out of the note, and checks side, account and amount against the fields
    (`generated-accounts`), names against the chart (`generated-account-name`);
  - today's single line is still recognised for the simple form;
  - `render_voucher()` writes one debit and one credit line of the same amount in the
    simple form, byte for byte as today, and anything else in the lines form;
  - `belopp` is the bank net, or the total;
  - **round trip:** render, read back, get the same voucher — three lines, five lines,
    two lines on one account, no bank account;
  - a voucher that does not balance, or has a line of zero, cannot be rendered.

  *Verify:* fail for the right reason. **STOP for review.**
- [ ] 3.2 Implement.

Commit: `feat(formats): render vouchers with several lines and their generated lines`

### Phase 4 — The domain: several lines, and no bank transaction

- [ ] 4.1 **Tests first** (`tests/test_posting.py`, extended):
  - a bank transaction against several lines: the bank line is added from the
    transaction; refused when the lines do not add up to the bank amount
    (`lines-unbalanced`), when a line is on the bank account (`account-is-bank`), on an
    unknown account, or with an amount that is not positive (`line-amount`);
  - `--account` and lines together are refused (`account-and-lines`);
  - a voucher without a bank transaction: the date, the text and the lines are the
    caller's; refused when it does not balance (`lines-unbalanced`), has fewer than two
    lines, has no text (`text-missing`), has the bank account among its lines
    (`bank-without-transaction`), is dated outside the fiscal year
    (`date-outside-year`), or equals an existing voucher in date, text and lines
    (`duplicate`);
  - the text and the note are masked;
  - every MVP-004 test passes unchanged.

  *Verify:* fail for the right reason. **STOP for review.**
- [ ] 4.2 Implement.

Commit: `feat(books): build vouchers with several lines and without a bank transaction`

### Phase 5 — The command

- [ ] 5.1 **Tests first** (`tests/test_cli_new_voucher_lines.py`), on a copy of the
  fixtures:
  - a salary payment: one bank transaction, three accounts; the file is as in §1;
    `validate` gives no new error and the transaction is no longer unbooked;
  - an issued invoice without a bank transaction, then its payment as a bank
    transaction against the receivable account;
  - `--debit` and `--credit` take `<account>=<amount>` and are checked by the parser;
  - the output names the number, the date and each line's side, account and amount —
    never the text, the note or a document's name;
  - one test per refusal, each asserting that every file is byte-identical afterwards;
  - running the same voucher without a bank transaction twice creates one;
  - every MVP-004 command test passes unchanged.

  *Verify:* fail for the right reason. **STOP for review.**
- [ ] 5.2 Implement.

Commit: `feat(cli): let new-voucher take several lines and no bank transaction`

### Phase 6 — The bank export

- [ ] 6.1 **Tests first** (`tests/test_sparbanken_syd_csv.py`, a synthetic export in
  `tests/fixtures/bank/`):
  - the export is read into statement rows, oldest first: the date, the amount
    normalised from `1.234,56`, the text as the name, no message, no balance;
  - personal identity numbers in the text are masked;
  - refused: a row with another number of fields, a date or an amount that cannot be
    read, a currency other than SEK, an empty file;
  - `bank.export_format` selects the reader, and `nordea-csv` works as before;
  - the statement file written from it is read by `validate`, and reconciliation gives
    an info finding that the statement has no balances, so the bank's arithmetic and the
    opening balance are not checked;
  - a partial export is refused as today;
  - no message quotes a text.

  *Verify:* fail for the right reason. **STOP for review.**
- [ ] 6.2 Implement.

Commit: `feat(formats): read the sparbanken-syd-csv bank export`

### Phase 7 — Documents, reports and the first organisation

- [ ] 7.1 **Tests first:**
  - `documents-expected` names a voucher without a bank line and without a document;
  - the voucher list, the general ledger, the income statement and the balance sheet
    show a voucher with several lines, line by line, with the right totals.

  *Verify:* fail for the right reason, or pass already and pin today's behaviour.
  **STOP for review.**
- [ ] 7.2 Implement what the tests need.
- [ ] 7.3 On the reference copy of Helsingborgs Judoklubb's books, counts and equal/not
  equal only: `validate` and the report figures before and after this MVP.
  *Expected:* identical, apart from findings this MVP adds on purpose.

Commit: `feat(books): expect documents for vouchers without a bank transaction`

### Phase 8 — Pilot: Aktivitet Förebygger

- [ ] 8.1 Write `docs/claude-prompts/set-up-organisation-project.md`: lets Claude Code in
  an organisation's project create `organisation.yaml`, the chart of accounts and the
  opening balance in the core's format, import the bank export and reach `RESULT: OK`
  with no vouchers.
- [ ] 8.2 The owner runs it in Aktivitet Förebygger's project, then lets the agent book
  2026 from the bank statement and the supporting documents. *Verify, counts only:* at
  least one salary payment and one issued invoice created by the command;
  `RESULT: OK`; no unbooked bank transaction.

Commit: `docs(mvp-005): record the pilot result`

### Phase 9 — Documentation and close

- [ ] 9.1 `organisation-projects.md`: the two new uses of the command, the lines form,
  and the `CLAUDE.md` snippet.
- [ ] 9.2 `README.md`, `AGENTS.md`, `overview.md`, `current-state.md`, `roadmap.md`
  (status; member management is next).
- [ ] 9.3 The MVP's "Outcome at close", checked against each acceptance criterion.
- [ ] 9.4 Methodology compliance: the note under `GAP-F2-CONFIDENTIAL` (§0.3).
- [ ] 9.5 `git grep` for organisation-specific values in `src/`: none.

Commit: `docs(mvp-005): document the lines form and close the MVP`

## 5. Risks / open questions

- **A voucher without a bank transaction is only as right as its caller.** Nothing
  outside the books confirms the date or the amounts. The supporting document is the
  evidence, and the check for it is a warning. The treasurer's review is the control.
- **The amounts are not calculated.** A payslip with a wrong tax gives a wrong voucher
  that balances. Out of scope by decision.
- **No balances from Sparbanken Syd.** The opening balance of the bank account and the
  bank's own arithmetic cannot be checked for Aktivitet Förebygger. An info finding
  says so. Whether the bank offers an export with balances is worth asking.
- **The export has no header row,** so nothing but the shape of its rows tells that it
  is the right kind of file. The reader refuses anything that does not fit exactly.
- **Two forms in one format.** A reader of the files meets both. They never mix within
  a voucher, and the simple form stays the common case.
- **The tax account** is booked from its statement by hand, as vouchers without a bank
  transaction, with no reconciliation (backlog).
- **One voucher, at most one bank transaction.** Reconciliation pairs a bank row with
  a voucher on date and the net on the bank account. A salary run that the bank pays as
  several transactions is therefore one voucher without the bank account — the net as a
  liability — and one simple voucher per payment. Letting a voucher cover several bank
  rows would mean rebuilding reconciliation; not planned.

### Threat model (STRIDE)

```text
Caller (treasurer or AI agent): date, amount, row, lines (account=amount), text,
                                document names, note
   → CLI → reads books, bank statement, documents folder listing
         → writes ONE new file: <books>/verifikationer/NNNN_YYYY-MM-DD.md

Bank export (a file the treasurer downloaded) → import-bank → the statement file
```

- **Spoofing:** as in MVP-004 — whoever can run the command can already edit the files.
  Accepted.
- **Tampering:**
  - Lines: each account must be in the chart; each amount is parsed by the argument
    parser; the lines must balance. The bank line is never the caller's.
  - The text of a voucher without a bank transaction is the caller's. It is written as
    one quoted line, so it cannot add or change a field, and it is masked.
  - The export: a headerless file is trusted only as far as its shape. Every row must
    have the expected fields; a text is data and is never interpreted.
  - Everything else as in MVP-004: exclusive creation, the path from the number and the
    date, documents only from the folder listing.
- **Repudiation:** as in MVP-004 — the organisation's own history.
- **Information disclosure:** the output and the refusals never hold the text, the note
  or a document's name. The export's texts can hold names; they go to the statement
  file only, masked for personal identity numbers.
- **Denial of service:** N/A — local commands.
- **Elevation of privilege:** a caller can now create a balanced voucher between any
  accounts in the chart, without a bank transaction behind it. That is what the feature
  is; the bank account is excluded, so the bank's balance cannot be changed this way.

## 6. Found during this MVP

- *(none yet)*
