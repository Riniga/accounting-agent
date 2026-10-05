# Plan: MVP-004 – Create vouchers from bank transactions via core

Reference: [`docs/mvp/MVP-004-create-vouchers.md`](../mvp/MVP-004-create-vouchers.md)

**Status:** In progress (plan approved 2026-10-05)

## 0. Investigation

Carried out 2026-10-05 with read-only commands.

### 0.1 Baseline

| Measure | Value |
|---|---|
| Core | 423 tests pass; coverage floor 97 % |
| Writes today | the bank statement file, the fund-value file and the reports (ADR-008) |
| Helsingborgs Judoklubb's 2026 books | 163 vouchers, all on the bank account; 163 statement rows; 0 vouchers without a statement row |

Measured on the reference copy with a scratchpad script that uses the core's own readers
and prints counts only. The script is not in the repository.

| Question | Count |
|---|---|
| Voucher texts equal to `name(message)`, or the name alone when the message is empty | 147 of 163 |
| Voucher texts equal to `name(message)` exactly | 141 |
| Statement rows without a message | 6 |
| Statement rows that share date and amount with another row | 43, in 11 groups |
| Vouchers with a note / with supporting documents | 62 / 62 |
| Notes whose first line already looks like a generated line | 0 |
| Files in the documents folder / referred to by a voucher / not referred to | 87 / 63 / 24 |
| Document names with a space or a parenthesis | 4 |
| Cost vouchers without a document / after the exempt accounts | 33 / 22 |

### 0.2 Where the MVP needs correcting or completing

1. **"Errors stop" needs one exception.** A bank transaction without a voucher, when
   later transactions are booked, is an error (`bank-unbooked`). Creating that voucher is
   the fix, so that error cannot block the command. **The plan:** every other error
   blocks; `bank-unbooked` does not. Recorded in ADR-009.
2. **Date and amount do not identify a transaction.** 43 of 163 rows share them with
   another row, and those rows have different texts. **The plan:** the caller gives the
   date and the amount, and also the statement row when more than one row has that date
   and amount. `validate` already prints the row.
3. **The domain's bank transaction has no name or message** — deliberately, so nothing
   built on the model can quote them (ADR-007). The voucher's text needs them. **The
   plan:** the text is composed in `formats/`, next to the statement reader, and handed
   to the writer. `BankTransaction` is not changed.
4. **The text rule** is `name(message)`, or the name alone when the message is empty. It
   reproduces 147 of the 163 existing texts. The other 16 are explained in the pilot
   (TODO 7.1); the likely causes are hand edits and removed personal identity numbers.
5. **Generated lines would leak into the reports.** The reader puts everything below the
   fields into the voucher's note, and the voucher list and the to-do report print the
   note. **The plan:** the reader recognises the generated lines by their exact shape,
   only at the top of the body, and keeps them out of the note. No existing note has
   that shape (0 of 62), so existing reports do not change.
6. **The existing write helper replaces files.** `write_text_atomically` ends with a
   replace, which is right for derived files and wrong for vouchers. **The plan:** the
   voucher writer uses exclusive creation and never replaces.
7. **A document's file name cannot be printed.** The detail checks never quote one,
   because it can hold a person's name. The MVP says unused documents "are listed".
   **The plan:** `validate` gives the count; the to-do report, which stays in the
   organisation's project, lists the names.
8. **The to-do report already lists payments without a document.** `validate` only gives
   the count. **The plan:** one warning that names the voucher numbers, with the exempt
   accounts from configuration left out. On the pilot books that is 22 vouchers.
9. **Four document names need angle brackets** to work as a Markdown link (a space or a
   parenthesis). The link is written as `[name](<path/name>)` for every document.
10. **A stale generated line.** When the treasurer changes a voucher's account by hand,
    the generated line no longer matches. **The plan:** different account numbers are an
    error; a name that differs from the chart is a warning, so that renaming an account
    in the chart does not break the books.

### 0.3 Reading rule (interpretations §9)

Two things happened while preparing this plan, on 2026-10-05. Nothing was copied into the
repository.

- The organisation's rules file (`Bokföring/README.md`) and its routine were read as
  Internal. The rules file contains the decision log, with names tied to amounts. This is
  the known issue in the roadmap backlog ("move the decision log out of the rules
  file") and `GAP-F2-CONFIDENTIAL`.
- File names in the reference copy were listed by a file search, including the documents
  folder and a personnel folder. The rule says to count, not list.

From here on the reference copy is only counted, through the core's readers. Noted under
`GAP-F2-CONFIDENTIAL` in TODO 8.4.

### 0.4 Owner decisions (2026-10-05)

1. The command belongs in the core, not in each organisation's project.
2. MVP-004 comes before member management.
3. The generated lines are in Swedish.
4. Errors in the books stop the command, with the exception in §0.2 point 1 (approved
   with the plan).
5. Supporting documents stay optional; the core creates none.
6. Account names are shown in the voucher, but not stored as fields.

### 0.5 Other findings

- **No new dependencies.** `json`, `os`, `re` and `decimal` are standard library.
- **Module boundary.** The domain (`books/`) stays free of I/O (Ruff `TID251`): it
  builds the voucher and decides refusals. `formats/` composes the text, renders the
  file and writes it. The CLI wires them together and prints.
- **The reader and the writer must agree.** A round-trip test — render a voucher, read
  it back, get the same voucher — guards it.
- **Fixtures.** `tests/fixtures/example-full/` already has a statement, a documents
  folder and the books. Tests that write copy the fixture to `tmp_path` first.
- **No new configuration.** The bank account, the statement file, the documents folder,
  the guessed-posting marker and the exempt accounts are already in `organisation.yaml`.

## 1. Goal

When this plan is done:

- `accounting-agent new-voucher <org> --config-dir <dir> --date <YYYY-MM-DD> --amount
  <amount> --account <account> [--row <n>] [--document <name>]… [--note <text>]
  [--guess]` creates one voucher file and prints its number, date, amount and accounts.
- The command refuses, writing nothing, in every case listed in ADR-009.
- A created voucher has the format's fields, then the generated lines:

  ```text
  Debet 5010 Hyra · Kredit 1930 Bankkontot
  Underlag: [20260201-faktura-lokal-1001.pdf](<../../documents/20260201-faktura-lokal-1001.pdf>)

  Gissad kontering: <the caller's reason>
  ```

- The `front-matter` reader keeps generated lines out of the note and reports lines that
  disagree with the fields.
- `validate` names the cost vouchers without a document and counts the unused documents;
  the to-do report lists the unused documents.
- ADR-009 is accepted and ADR-008's status points at it.
- Helsingborgs Judoklubb's treasurer has created a real batch of vouchers with it.

## 2. Scope boundary

- **In:**
  - `src/accounting_agent/books/` — a new module that builds a voucher from a bank
    transaction and decides refusals; the two new document checks in `details.py`;
  - `src/accounting_agent/formats/front_matter.py` — recognising and checking generated
    lines; rendering and writing a voucher;
  - `src/accounting_agent/formats/bank_statement.py` — the text of a statement row;
  - `src/accounting_agent/reports/overview.py` — unused documents in the to-do report;
  - `cli.py`;
  - tests and synthetic fixtures under `tests/`;
  - ADR-009, ADR-008's status line, the glossary, `overview.md`, `current-state.md`,
    `README.md`, `AGENTS.md`, `roadmap.md`, `organisation-projects.md`, the MVP-004
    document, methodology compliance.
- **Out:**
  - changing, reversing or removing vouchers;
  - vouchers without a bank transaction, and vouchers with more than two lines;
  - suggesting an account; machine-readable posting rules;
  - reading or renaming supporting documents;
  - adding generated lines to existing vouchers;
  - a `--dry-run` or batch mode — one voucher per run;
  - member allocation; other book formats; new dependencies;
  - the organisation's own routine document — the organisation updates it.

## 3. Chapters addressed

- **B3** Architecture principles — the domain stays free of I/O; the new write is
  confined to `formats/` and the CLI.
- **B5** Documentation — ADR-009, glossary, README, the organisation guide.
- **C1** SKA 4 — STRIDE pass (§5), for the first write to data that cannot be recreated.
- **D1** — AI-TDD with the owner's review of the tests before each implementation.
- **E4** SKA 3 — masking in the written file and in terminal output.
- **F2** SKA 2 — the reading rule (§0.3); `GAP-F2-CONFIDENTIAL` gets a note.

No gap-register row is expected to close.

## 4. TODOs

Every phase that adds production code follows the MVP-002 pattern: tests first, **STOP
for the owner's review of the tests**, then the implementation. Each test must fail for
the right reason before the implementation is written. Every phase runs `pytest` and
`ruff check` before its commit, and updates `current-state.md` in the same phase.

### Phase 1 — Decisions and branch

- [x] 1.1 The owner merges MVP-003's pull request. Create
  `feature/mvp-004-create-vouchers` from `main`.
  Result: PR #13 is merged; the branch is created from `origin/main` (`98eedd3`). The
  MVP document, this plan and ADR-009 were already on `main` (`e96584d`).
- [x] 1.2 Update the MVP-004 document with a dated correction note per §0.2.
  *Verify:* every change traces to §0.
  Result: a correction note at the top with six points, each tracing to §0.2.
- [x] 1.3 Set ADR-009 to Accepted, change ADR-008's status line to "Accepted — superseded
  in part by ADR-009", and remove "(Proposed)" from the index row.
  *Verify:* ADR-008's body is unchanged (`git diff` shows the status line only).
  Result: done; `git diff` on ADR-008 shows one changed line.
- [x] 1.4 Glossary: generated lines, counter account (motkonto), guessed posting.
  Result: three rows added. The stale "pending PR" for MVP-003 in `roadmap.md` and
  `current-state.md` was also corrected.

Commit: `docs(mvp-004): approve the plan and accept ADR-009`

### Phase 2 — The reader: generated lines

- [x] 2.1 **Tests first** (`tests/test_front_matter_generated.py`; the variants are built
  from the `valid` books by helpers, as in `test_front_matter.py`):
  - a voucher with generated lines reads to the same `Voucher` as one without them, and
    its note holds only the text after the generated lines;
  - a voucher without generated lines reads exactly as today;
  - a line of the same shape further down in the body stays in the note;
  - account numbers in the generated line differ from the fields → error
    `generated-accounts`;
  - an account name differs from the chart → warning `generated-account-name`;
  - the linked documents differ from the `underlag` field → error `generated-documents`;
  - no finding quotes a name, a text or a file name.

  *Verify:* the tests fail for the right reason. **STOP for review.**
  Result: `tests/test_front_matter_generated.py`, 25 tests. 22 fail for the right
  reason: the generated lines end up in the note, and no `generated-*` finding exists.
  3 pass already, as they should: they pin today's behaviour that must not change (a
  line of the same shape further down, a document line without an account line, and
  vouchers without generated lines). The shape locked by the tests:
  - `Debet NNNN <name> · Kredit NNNN <name>` as the first non-blank line of the body;
  - then one `Underlag: [<name>](<<path>/<name>>)` line per document, in the field's
    order, where the path must end with the document's name;
  - the note is whatever follows.

  Also tested: a wrong number gives the error only, not the name warning as well.
- [x] 2.2 Implement in `front_matter.py`. *Verify:* all tests pass; the existing 423
  still pass unchanged.
  Result: 448 tests pass (423 unchanged + 25); coverage 98.85 %, and every new line in
  `front_matter.py` is covered. The body is split after the voucher is read, so the
  fields are read exactly as before; the checks compare the generated lines with the
  voucher's two posting lines and its documents.

Commit: `feat(formats): read and check a voucher's generated lines`

### Phase 3 — The domain: build a voucher

- [x] 3.1 **Tests first** (`tests/test_posting.py`), for a pure function that takes
  the books, the bank transactions, the bank account and the caller's request:
  - money in → debit the bank account, credit the account; money out → the reverse;
  - the number is the highest number plus one;
  - the date and the amount are the transaction's;
  - refused: no transaction with that date and amount; several, and no row given; the
    row given does not have that date and amount; every transaction with that date and
    amount already has a voucher; the account is not in the chart; the account is the
    bank account;
  - refused: a guess without a reason; a guess when no marker is configured;
  - a refusal names the reason, never a text or a name.

  *Verify:* fail for the right reason. **STOP for review.**
  Result: `tests/test_posting.py`, 34 tests. They fail for the right reason:
  `ImportError: cannot import name 'VoucherRefusedError' from 'accounting_agent.books'`.
  API locked by the tests:
  - `VoucherRequest(date, amount, account, row=None, documents=(), note="", guess=False)`;
  - `build_voucher(books, transactions, texts, bank_account, request, documents=None,
    guessed_posting_marker=None) -> Voucher`, where `texts` maps a statement row to the
    voucher text the format composed for it;
  - `VoucherRefusedError` with a `rule`: `transaction-missing`,
    `transaction-ambiguous`, `row-mismatch`, `already-booked`, `account-unknown`,
    `account-is-bank`, `guess-without-reason`, `guess-marker-missing`,
    `document-missing`, `documents-not-configured`, `document-name`, `document-twice`.

  Differences from what was planned, all found while writing the tests:
  - **The function also takes the rows' texts.** Among several rows with the same date
    and amount, the only way to tell which ones already have a voucher is the text: a
    row is booked when as many vouchers as rows have that date, amount and text.
  - **The document refusals are decided here,** not in the CLI, from the set of files
    the CLI lists — the same way `check_details` gets it. Two more were added: the same
    document twice, and a name with the field's separator `;`.
  - **A known limit:** when a voucher's text was edited by hand, its row looks unbooked
    by text. If every row with that date and amount has a voucher, the request is still
    refused on the count. If only some have, the caller could book the edited row twice
    and leave another unbooked; the counts then match and `validate` does not see it.
    The caller chooses the row from `validate`'s list, so this needs a wrong row from
    the caller as well. Accepted; added to §5.
- [x] 3.2 Implement `src/accounting_agent/books/posting.py`; export it from `books`.
  Result: 483 tests pass; coverage 98.90 %, `posting.py` 100 %. One test was added
  with the implementation, for a line the first 34 did not reach: a voucher that is not
  on the bank account does not count as booking a transaction with the same date and
  amount.

Commit: `feat(books): build a voucher from a bank transaction`

### Phase 4 — The format: text, render, write

- [x] 4.1 **Tests first:**
  - `bank_statement`: the text of a row is `name(message)`, the name alone when the
    message is empty; personal identity numbers are masked;
  - `front_matter`: rendering gives the fields in the format's order, the text as a
    quoted string, the generated account line with names from the chart, one link per
    document with angle brackets, the marker line for a guess, then the note;
  - **round trip:** render, read back, get the same voucher — also for a text with
    quotes, a colon, a line break and `---`;
  - writing creates `NNNN_YYYY-MM-DD.md` as UTF-8 without BOM, with LF line endings;
  - writing refuses when the file exists, or when another file has the same number, and
    leaves the folder unchanged.

  *Verify:* fail for the right reason. **STOP for review.**
  Result: `tests/test_voucher_writer.py`, 37 tests. They fail for the right reason:
  `ImportError: cannot import name 'read_voucher_texts' from
  'accounting_agent.formats.bank_statement'`. API locked by the tests:
  - `bank_statement.read_voucher_texts(path) -> dict[int, str]`, statement row → text;
    empty when the file is missing or cannot be read;
  - `front_matter.render_voucher(voucher, account_names, bank_account, link_path) -> str`;
  - `front_matter.voucher_file_name(voucher) -> str`;
  - `front_matter.write_voucher(directory, voucher, content) -> Path`, raising
    `VoucherExistsError`.

  The file's conventions were counted on the pilot's 163 voucher files (counts only),
  and the tests follow them:
  - the `underlag` field is always written, empty when there is no document (163 of
    163 have the line; 101 are empty);
  - several documents are separated by `; ` (3 of 3);
  - a whole amount has no decimals, others have two (no voucher has `.00`, although
    153 statement rows do);
  - a blank line follows the closing `---` (163 of 163).

  Also locked: a voucher that is not one debit line and one credit line of the same
  amount, or that uses an account outside the chart, cannot be rendered (`ValueError`);
  the number must be 1–9999; a missing voucher folder is not created.
- [x] 4.2 Implement.
  Result: 520 tests pass; coverage 98.92 %. Every new line is covered; the uncovered
  lines in the two modules are the same as before this phase.

Commit: `feat(formats): render and write a front-matter voucher`

### Phase 5 — The command

- [x] 5.1 **Tests first** (`tests/test_cli_new_voucher.py`), on a copy of `example-full`
  in `tmp_path`:
  - a successful run creates one file; `validate` then gives no new error, and the
    transaction is no longer unbooked;
  - the output has the number, the date, the amount and the accounts, and no text, name
    or document name;
  - running the same command twice creates one voucher;
  - one test per refusal, each asserting the books folder is byte-identical afterwards:
    missing `books` or `bank` section; a document that is not in the folder; a document
    given when no folder is configured; books with an error; a voucher that would add an
    error;
  - books whose only error is `bank-unbooked` do **not** block, and the command fixes it;
  - new warnings caused by the voucher are printed.

  *Verify:* fail for the right reason. **STOP for review.**
  Result: `tests/test_cli_new_voucher.py`, 29 tests. 25 fail for the right reason:
  argparse does not know the command (`SystemExit: 2`, "invalid choice"). The 4 that
  pass are the malformed-argument tests, which expect exit code 2; they pass for the
  wrong reason until the command exists, and are re-checked in 5.2. Locked by the tests:
  - the arguments: `--date`, `--amount`, `--account` (four digits) are required and
    checked by the parser; `--row`, `--document` (repeatable), `--note`, `--guess`;
  - the output: `Created voucher N (<file name>)`, then the date, the amount, the two
    accounts and the number of documents, then the warnings the voucher added;
  - a refusal is logged as `[rule] message` with exit code 1, and every file under the
    organisation is byte-identical afterwards;
  - the link path is the relative path from the voucher folder to the documents folder.

  The "would add an error" safety net cannot be reached by any request today — every
  known cause is refused earlier — so its test lets a check object to the new voucher.
- [x] 5.2 Implement `new-voucher` in `cli.py`: check before, build, check the books with
  the new voucher added, write, print.
  Result: 552 tests pass; coverage 98.97 %, and every new line in `cli.py` is covered.
  - The four malformed-argument tests now pass for the right reason: the parser rejects
    the value, and nothing is read.
  - Three tests were added with the implementation, for lines the first 29 did not
    reach: a profile without a `checks` section, a file that appears between the read
    and the write (never replaced), and folders on different drives (the link is the
    name alone).
  - Only warnings that name the new voucher are printed. Summaries such as the number
    of unbooked transactions change with every voucher and would otherwise be repeated.
  - Run for real on a copy of the synthetic organisation: the voucher was created, a
    second run was refused as `already-booked`, and `validate` gave `RESULT: OK` with
    no warning left.

Commit: `feat(cli): add the new-voucher command`

### Phase 6 — The document checks

- [x] 6.1 **Tests first:**
  - `details`: one warning `documents-expected` naming the cost vouchers without a
    document, leaving out the exempt accounts; none when there are none;
  - `details`: one info `documents-unused` with the count of files no voucher refers to;
  - the to-do report lists the unused documents' names;
  - the existing `documents-summary` is unchanged.

  *Verify:* fail for the right reason. **STOP for review.**
  Result: 24 new tests — `tests/test_document_checks.py` (13), four in
  `tests/test_reports_summary.py`, `tests/test_cli_documents.py` (7). 22 fail for the
  right reason: `check_details()` has no `no_document_accounts`, and `ReportContext`
  has no `unused_documents`. 2 pass already and pin what must not change: the example
  books give neither finding, and a profile without a documents folder gets no list.

  Differences from what was planned:
  - **`documents-expected` follows the to-do report's rule, not "cost vouchers".** The
    report already lists *money out of the bank* without a document, except the
    accounts configured as needing none. Two definitions of the same thing would
    disagree — a purchase for stock is money out but not a cost account — so the check
    uses the report's rule. The pilot's expected number (22, counted on cost accounts)
    is therefore counted again in TODO 7.2.
  - **One warning per voucher, not one for all.** It matches the other voucher rules,
    and it lets `new-voucher` say exactly when the voucher it just created lacks a
    document.
  - **The fixture `example-full` now configures 6570 as needing no document,** so that
    its books stay without warnings. No existing test changed its expectation.
  - The list in the to-do report is shown when a documents folder is configured, also
    when it is empty ("Inga."), like the report's other sections.
- [x] 6.2 Implement; pass the exempt accounts from the profile to the check.
  Result: 576 tests pass; coverage 98.99 %, every new line covered.
  - One existing test changed its expectation:
    `test_vouchers_without_documents_are_summarised` compared the whole list of
    findings with the summary alone, and its payment without a document now also gets
    `documents-expected`. The summary itself is unchanged. (6.1 said that no existing
    test changed; that was true for the fixture, not for this check.)
  - The report's list is filled in by `report` itself, sorted by name.

Commit: `feat(books): name payments without documents and count unused documents`

### Phase 7 — Pilot

- [ ] 7.1 On the reference copy of the real books, with a scratchpad script that prints
  counts only: for each of the 163 vouchers, build the voucher from its statement row
  and its own account, and compare the fields with the existing ones. Report equal and
  unequal, and the number per kind of difference. *Expected:* 147 equal on the text;
  date, amount, debit and credit equal on all 163.
- [ ] 7.2 `validate` on the reference copy: the same result as before this MVP, plus the
  new findings (expected: 22 vouchers in `documents-expected`, 24 unused documents).
- [ ] 7.3 The owner, as treasurer, creates a real batch of vouchers with the command in
  the organisation's own folder, and reports the counts. *Verify:* `RESULT: OK`, and no
  unbooked transaction before the last voucher.

Commit: `docs(mvp-004): record the pilot result`

### Phase 8 — Documentation and close

- [ ] 8.1 `organisation-projects.md`: the command in "Daily use", the table of what each
  organisation can use, and the `CLAUDE.md` snippet ("create vouchers with the command,
  never by hand").
- [ ] 8.2 `README.md`, `AGENTS.md` (local commands), `overview.md`, `current-state.md`,
  `roadmap.md` (status; member management is next).
- [ ] 8.3 The MVP's "Outcome at close", checked against each acceptance criterion.
- [ ] 8.4 Methodology compliance: the note under `GAP-F2-CONFIDENTIAL` (§0.3).
- [ ] 8.5 `git grep` for organisation-specific values in `src/`: none.

Commit: `docs(mvp-004): document the command and close the MVP`

## 5. Risks / open questions

- **The account is still a judgement.** A wrong account passes every check. The
  treasurer's review of the voucher list is the control; posting rules are in the
  backlog.
- **A wrong voucher cannot be undone by the tool.** Removing it is manual and the
  treasurer's decision. Accepted (ADR-009).
- **The text rule fits 147 of 163.** If the pilot shows a second systematic rule, it is
  added to the format before close; one-off hand edits are accepted.
- **Rows with the same date and amount, and a hand-edited text.** A voucher whose text
  was edited no longer matches its statement row, so that row looks unbooked. The count
  per date and amount still stops a voucher too many, but not the wrong row among
  several (TODO 3.1). Accepted: the voucher holds no link to its statement row, and
  adding one changes the file format.
- **Booking out of date order.** Creating a voucher for a newer transaction first makes
  the older ones `bank-unbooked` errors. That does not block (§0.2 point 1), but the
  routine should stay oldest first.
- **A stale generated line is an error** and stops reports and new vouchers until the
  line is edited. Deliberate: a voucher that shows one account and posts another is what
  this MVP exists to prevent.
- **A file in the documents folder that is not a document** (for example a note) is
  counted as unused. The organisation moves it; the core does not guess.

### Threat model (STRIDE)

```text
Caller (treasurer or AI agent): date, amount, row, account, document names, note
   → CLI → reads books, bank statement, documents folder listing
         → writes ONE new file: <books>/verifikationer/NNNN_YYYY-MM-DD.md
```

- **Spoofing:** no authentication; whoever can run the command can already edit the
  files. The organisation-id guard still applies. Accepted.
- **Tampering:** the caller's values are not trusted.
  - The account must be in the chart.
  - A document must be in the listed folder, so a path outside it is refused.
  - The file path comes from the number and a validated date, never from the caller's
    text.
  - The note is written below the closing `---`; the reader stops at the first one, so a
    note cannot add or change a field. The text is written as one quoted line.
  - Exclusive creation: an existing voucher cannot be replaced.
  - Configured paths are trusted, as in ADR-008.
- **Repudiation:** the file does not say who created it. The organisation's own history
  shows it. Accepted until R3 defines an audit trail.
- **Information disclosure:** the terminal output has no text, name or document name, so
  it is safe to show to an AI tool. The note and the text go to the file only, masked.
  What an AI agent reads in order to choose the account is governed in the organisation
  project, not here.
- **Denial of service:** N/A — a local command.
- **Elevation of privilege:** the command can create one file in the voucher folder and
  nothing else. Two runs at once can pick the same number; the writer refuses a second
  file with the same number when it sees it, and `validate` reports it otherwise.

## 6. Found during this MVP

- *(none yet)*
