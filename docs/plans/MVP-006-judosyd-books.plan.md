# Plan: MVP-006 – JudoSyd's books in the core's format

Reference: [`docs/mvp/MVP-006-judosyd-books.md`](../mvp/MVP-006-judosyd-books.md)

**Status:** Implemented – pending PR (MVP approved 2026-10-08)

## 0. Investigation

Carried out 2026-10-08 with read-only commands.

### 0.1 Baseline

| Measure | Value |
|---|---|
| Core, on `main` after MVP-005 (PR #15) | 798 tests pass; coverage 99.13 %, floor 97 % |
| Organisations keeping books through the core | 2 |
| Bank export formats | `nordea-csv`, `sparbanken-syd-csv` |
| Prompts for an organisation project | set up, book the year, update, two tests |

What JudoSyd has, from its own instruction documents and from the shape of its new
reference copy:

| | |
|---|---|
| Books until now | In a commercial bookkeeping system, not in files |
| The treasurer's assistant | Claude Code on the treasurer's computer; reads mail and calendar, sends notices, files documents; does not keep books |
| New year folder | The same layout as the first two organisations' |
| Reference chart | Four CSV files, as the core reads today |
| Bank | Swedbank; two exports, one per account |
| Supporting documents | 4 files |
| Opening balance | A text report from the earlier system: 11 accounts, in the earlier chart, tab-separated, amounts with a decimal comma |
| Budget | A short note, 9 lines |

The Swedbank export, by shape:

| | |
|---|---|
| Encoding and line endings | Windows-1252, CRLF, no BOM |
| Line 1 | A title line that starts with `*`: what, the period, when it was created |
| Line 2 | The header: `Radnr,Clnr,Kontonr,Produkt,Valuta,Bokfdag,Transdag,Valutadag,Referens,Text,Belopp,Saldo` |
| Rows | 12 comma-separated fields; product, reference and text in quotes; amounts with a decimal point |
| Order | Newest first; the bank's row number runs 1..N |
| Balance | After every transaction; in both files it follows from the amounts, row by row |
| Main account | 17 transactions, 2026-01-02 to 2026-09-23; 16 have a reference; the booking date equals the transaction date on 13 |
| Other account | 1 transaction |

### 0.2 Where the first proposal needed correcting

1. **Not alongside.** The first proposal built the books beside the earlier system and
   compared the two. The owner wants the same way as for the first two: new books in a
   new year folder. The comparison and its prompt are dropped.
2. **The roadmap's R4 described another migration.** It said the migration adds mail,
   notices and scheduling as general capabilities. Those stay in JudoSyd's project
   (ADR-002); this MVP is about the books.
3. **A change of chart of accounts is new.** The first two organisations kept their
   charts. Here the opening balance exists in the earlier chart only. **The plan:** the
   set-up prompt asks the agent for a mapping from the earlier accounts to the new ones,
   with the balance kept account by account and in total, for the treasurer to approve.
   The core does not convert: the agent writes the opening balance file.
4. **Two bank accounts.** The core reconciles one. **The plan:** the main account is the
   bank account; a transaction on the other is a voucher without a bank transaction,
   with that account's statement as its document — as the second organisation did for
   its tax account. A transfer between the two shows on the main account's statement
   and is booked from there.
5. **Another bank's export in another encoding crashed the readers.** The first two
   readers decoded the file as UTF-8 and raised a decoding error on a Windows-1252 file,
   instead of refusing it. **The plan:** decoding is shared, and a file in another
   encoding is refused like any other file that is not the bank's.
6. **Which date.** The export has three. The booking date is the one the balance follows,
   and the one a bank statement is ordered by. The voucher is dated by it.
7. **The text.** The export has a text and a reference. They become the statement's name
   and message, so a voucher's text is `text(reference)`, by the rule the first
   organisation's texts follow.
8. **The status documents still said MVP-005 is pending its pull request.** It is merged
   (PR #15). Corrected.

### 0.3 Reading rule and secrets (interpretations §9, C4)

- The earlier reference copy of JudoSyd's project holds **credential files** for the
  assistant's two servers. They were listed by name in a file search and were **not
  opened**. The owner removes them from the reference copy (TODO 4.5).
- The assistant's state file and run logs, and the earlier books, bank papers, invoices,
  receipts and reports, were not opened. The archive's folder names were listed; its
  files were counted.
- The new reference copy — bank exports, opening balance, budget and supporting
  documents — was read **by shape**: line and field counts, the header row, and lines
  with every letter and digit masked. Order and balances were checked by a script that
  printed true or false. Nothing from it is in the repository.
- The real exports were run through the finished reader, with counts as the only output.

### 0.4 Owner decisions (2026-10-08)

1. Helsingborgs Judoklubb and Aktivitet Förebygger are considered migrated. JudoSyd is
   next.
2. New books for 2026 in the core's format, in a new year folder; the old one stays
   aside. No parallel run and no comparison in this MVP.
3. The fiscal year is the calendar year.
4. The core not issuing invoices is accepted.
5. JudoSyd is not registered for VAT.
6. Reports as Markdown for now; PDF by hand, perhaps an MVP later.
7. The supporting documents are not complete; the booking run reports what is missing.
8. The chart of accounts changes in the move.
9. The work is to be as alike the first two organisations' as possible.

### 0.5 Other findings

- **No new dependencies.**
- **Nothing new is written.** The MVP adds a reader; `new-voucher` and the reports are
  used as they are.
- **The work is handed over as `AGENTS.md` says:** the tests first without a review
  stop, no commit by the AI tool, a report at the end.

## 1. Goal

When this plan is done:

- `import-bank` reads Swedbank's export, selected by `bank.export_format: swedbank-csv`.
- The set-up prompt handles a change of chart of accounts, and both prompts say what to
  do with a second bank account.
- JudoSyd's project has its 2026 in the core's format: the new chart, the opening
  balance carried over, every transaction on the main bank account booked, and the
  reports written.

## 2. Scope boundary

- **In:**
  - `src/accounting_agent/formats/` — `swedbank_csv.py`; shared decoding in
    `bank_export.py`; `profile.py` and `cli.py` for the format's name;
  - tests and a synthetic export under `tests/`;
  - `docs/claude-prompts/` — the set-up and booking prompts;
  - the organisation guide, README, the architecture documents, the roadmap, the MVP-006
    document, methodology compliance;
  - **in JudoSyd's project** (by the owner and the agent there): the year folder and
    the books.
- **Out:**
  - a comparison with the earlier system;
  - reconciling a second bank account;
  - reports as PDF; issuing invoices;
  - mail, calendar, notices and scheduling in the core;
  - earlier years; member management; new dependencies.

## 3. Chapters addressed

- **B3** Architecture principles — the reuse rule (ADR-002) applied to the integrations.
- **B5** Documentation — the organisation guide and the prompts.
- **C1** SKA 4 — STRIDE pass (§5) for a new external file format.
- **C4** — credential files in the reference copy (§0.3).
- **D1** — tests first (EX-004).
- **F2** SKA 2 — the reading rule (§0.3).

## 4. TODOs

Each phase that adds production code: the tests first, shown to fail for the right
reason, then the implementation. No stop for a review of the tests (EX-004). The AI tool
does not commit.

### Phase 1 — Decisions and documents

- [x] 1.1 Rewrite the MVP-006 document and this plan with the owner's answers.
  Result: the first proposal was never committed; both documents now describe what was
  approved, and the MVP's note says what the first proposal was.
- [x] 1.2 Roadmap: R4 says what this MVP does; the integrations become a backlog item;
  the stale status of MVP-005 is corrected.

### Phase 2 — The Swedbank export

- [x] 2.1 Tests first (`tests/test_swedbank_csv.py`, a synthetic export in
  `tests/fixtures/bank/`): the rows oldest first, dated by the booking date, the text as
  the name and the reference as the message, the balance kept, personal identity numbers
  masked; a text with a comma as one field; the title line optional; a file saved as
  UTF-8 accepted; every departure from the shape refused, naming the file and the row
  and never the content; the profile selects the reader, and each reader refuses the
  other banks' files.
  Result: 40 tests. They failed for the right reason, at collection:
  `ModuleNotFoundError: No module named 'accounting_agent.formats.swedbank_csv'`.
- [x] 2.2 Implement `formats/swedbank_csv.py`; add the format to the profile and to
  `import-bank`'s readers.
  Result: 838 tests pass; coverage 99.15 %, the new reader 100 %.
  - The bank's row numbers must run 1..N: a gap means that rows are missing, and the
    file is refused.
  - A file with transactions of more than one account is refused. The message gives the
    number of accounts, not their numbers.
  - Decoding is shared (`decode_export()` in `bank_export.py`). The first two readers
    now refuse a file in another encoding instead of raising a decoding error (§0.2
    point 5); the tests that give each reader the other banks' files cover it.
  - On the reference copy, counts only: both real exports are read (17 and 1 rows),
    written as a statement file and read back with no finding; every row has a balance,
    and the balances follow from the amounts.

### Phase 3 — The prompts

- [x] 3.1 `set-up-organisation-project.md`: the Swedbank format among those the core
  reads; a change of chart of accounts, with a mapping of the opening balance for the
  treasurer to approve; one bank account is the bank account, and what to do with
  another.
- [x] 3.2 `book-the-year.md`: a transaction on another account than the bank account is
  a voucher without a bank transaction, with that account's statement as its document.
  Result: both prompts updated. Not tried on a synthetic organisation again: the
  commands they describe did not change.

### Phase 4 — Pilot: JudoSyd

- [x] 4.1 The owner runs `set-up-organisation-project.md` in JudoSyd's project, and
  approves the proposal: the configuration, the new chart of accounts, and the mapping
  of the opening balance. *Verify:* `RESULT: OK` with no voucher; one `[unbooked]` row
  per bank transaction; no `bank-no-balances`.
- [x] 4.2 The owner runs `book-the-year.md`, and approves the posting templates.
- [x] 4.3 *Verify, counts only:* the number of vouchers; `RESULT: OK`; no unbooked bank
  transaction; guesses, vouchers without a document, and anything the command refused;
  the bank account's balance in the books against the bank's last balance.
  Result (2026-10-08, as the owner passed on the agent's report):
  - 17 vouchers, one per bank transaction; none with more than two lines, none without
    a bank transaction;
  - `RESULT: OK (errors: 0, warnings: 2, info: 4)`; both warnings are
    `documents-expected`;
  - no unbooked bank transaction; all 4 supporting documents linked;
  - 3 guessed postings; nothing on the parking account; 13 vouchers without a document
    — money in, the two payments the warnings name, and one on an account that needs
    none;
  - the command refused nothing;
  - 8 reports written;
  - the opening balance was carried over to the new chart: the bank account and the
    second account renumbered, two equity accounts merged, the earmarked funds
    renumbered, four accounts of the organisation's own.

  The report does not state the bank balance against the bank's. It follows from the
  result: the statement has balances, `validate` gave no error, so the opening balance
  equals the bank's balance before the first transaction, and every transaction has a
  voucher of the same date and amount.

  The agent's report ends with decisions for the treasurer: the mapping of the opening
  balance, the three guesses, a remaining receivable, and one cost taken from earmarked
  funds. None concerns the core.
- [x] 4.4 What the pilot shows the core lacks: add it here if it is small, with tests
  first; otherwise a backlog item.
  Result: nothing in the code. One thing in the prompts: the second account's statement
  could not be linked as a supporting document, because it lay beside the bank export
  and a document is linked from the documents folder only. The set-up prompt now tells
  the agent to propose that the treasurer moves such a statement there.
- [ ] 4.5 The owner removes the credential files from the earlier reference copy (§0.3).

### Phase 5 — Documentation and close

- [x] 5.1 The organisation guide, README, the architecture documents, the roadmap.
  Result: updated with the format and the prompts; the status lines are updated again
  at the close.
- [x] 5.2 The MVP's "Outcome at close", criterion by criterion.
  Result: written 2026-10-08.
- [x] 5.3 Methodology compliance: the note on the credential files and the reading rule.
- [x] 5.4 `git grep` for organisation-specific values in `src/`: none. The export format
  is named after the bank.

## 5. Risks / open questions

- **The old books stop being the books for 2026.** The earlier system holds the year so
  far; the new folder is built from the bank statement and the documents, not from it.
  If the two differ, nothing in this MVP shows it. The owner chose this; the old year
  folder stays as the way to check.
- **The opening balance is mapped by hand** from one chart to another. A wrong mapping
  gives books that balance and are wrong. The mapping is approved by the treasurer, and
  the total must be the same before and after; the bank account's opening balance is
  also checked against the bank's balances by `validate`.
- **The supporting documents are incomplete.** Many postings will be guesses or lack a
  document until the treasurer completes them. The reports list both.
- **The second bank account is not reconciled.** Its balance rests on the treasurer.
- **Giving `import-bank` the other account's export** would replace the statement file
  with the wrong account's rows, if that export starts no later than the existing file.
  Nothing in the configuration says which account is the bank account at the bank.
  Backlog.
- **Without the earlier system, nothing issues invoices or gives an accounts-receivable
  report.** Accepted by the owner.
- **Credential files in the earlier reference copy** (§0.3). Not opened; to be removed.

### Threat model (STRIDE)

```text
Bank export (a file the treasurer downloaded) → import-bank → the statement file
```

- **Spoofing / Elevation of privilege:** nothing new; no new command and no new write.
- **Tampering:** the export is trusted only as far as its shape: the header must be the
  bank's, every row must have its fields, the bank's row numbers must run without a gap,
  and one file holds one account. A text is data and is never interpreted.
- **Repudiation:** N/A.
- **Information disclosure:** the export's texts and references go to the statement file
  only, masked for personal identity numbers. No message quotes them, or an account
  number. The account and clearing numbers are read to check that the file holds one
  account, and are not written anywhere.
- **Denial of service:** N/A — local commands.

## 6. Found during this MVP

- `chore`: Dependabot's version updates are grouped into one pull request per ecosystem
  a week (`.github/dependabot.yml`). With "branch must be up to date" on `main`, every
  merged update made the others stale, and each had to be updated and re-run in turn.
  The owner asked for it on this branch (2026-10-08); committed on its own (`48b59f1`).
- `fix` (tests): a test variable was named `SECRET`, and the secret scan stopped the
  owner's commit on it. Renamed. The local hooks had been run with `--all-files`, which
  covers tracked files only; the new test file was untracked. Before a hand-over the
  hooks are now run on changed and new files alike.
