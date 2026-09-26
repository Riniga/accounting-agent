# Plan: MVP-003 – Bank import, reconciliation, remaining checks and reports via core

Reference: [`docs/mvp/MVP-003-bank-reconciliation-and-reports.md`](../mvp/MVP-003-bank-reconciliation-and-reports.md)

**Status:** In progress – phase 1 done (plan approved 2026-09-26)

## 0. Investigation

Carried out 2026-09-26 with read-only commands. In Helsingborgs Judoklubb's project only
**code**, `organisation.yaml` and the header rows of the BAS reference chart were read,
per the reading rule in
[`interpretations.md` §9](../methodology-compliance/interpretations.md#9-data-classification-for-ai-use-f2).
No book, bank, supporting-document or member file was opened, and no file names inside a
book folder were listed.

### 0.1 Baseline

| Measure | Value |
|---|---|
| Core | 162 tests, coverage 98.76 %, floor 95 %, Ruff clean |
| `kontroll.py` on the 2026 books | `OK` — 0 errors, 8 warnings, 15 info |
| Warnings | 3 × `dubblett`, 4 × `personuppgift`, 1 × `kontoplan` |
| Info | 6 × `kontoplan`, 3 × `medlemmar` (out of scope), 1 each × `bank`, `fond`, `budget`, `kommentarer`, `att-göra`, `underlag` |
| Organisation files (row counts only) | bank statement 163, fund value 1, budget 13, closing comments 8, to-do 34; BAS reference 4 files; 87 supporting documents; 10 reports |

`kontroll.py` was run with its output redirected to the scratchpad. Only counts per level
and rule were extracted, and the file was deleted.

**Expected core result on the same books, for the rules in scope:** 0 errors; 3
duplicate, 4 personal-number and 1 chart warning; the corresponding info findings; no
unbooked transactions.

### 0.2 Where the MVP needs correcting or completing

1. **The model cannot carry the reports or the BAS check.** `Account` has a number and
   a name only. The organisation's reports group accounts by the chart's `kontogrupp`
   column, and the summary finds equity by the group name "EGET KAPITAL". The BAS check
   compares `kontoklass`, `kontogrupp` and `bas_beskrivning`. **The plan:** `Account`
   gets an optional group and reference description (ADR-007; ADR-006 is accepted and is
   not edited). Aktivitet Förebygger's chart has no group column, so the reports fall
   back to the two-digit BAS group when the group is missing.
2. **A byte-identical bank statement needs the Swedish mask.** The organisation's import
   writes `[personnummer]`; the core's `mask_personal_numbers()` writes
   `[personal number]`. **The plan:** the mask text becomes a parameter. Files the core
   writes (the bank statement file, the reports) use `[personnummer]`; terminal output
   keeps `[personal number]`.
3. **Several `kontroll.py` findings quote data.** The duplicate warning quotes the
   voucher text; the unbooked list and "bank transaction without a voucher" quote the
   counterparty's name; chart warnings quote local names. **The plan:** core findings show
   the date, amount, statement row and voucher number only. The domain's bank-transaction
   model does not even hold the name or the message. "The same unbooked transactions" is
   compared on (date, amount).
4. **Some rules are organisation conventions, not BAS.** Bank fees (6570) need no
   supporting document; the note marker `Gissad kontering`; the text prefix "utlägg";
   the parking account 3008; a note about stock account 1410 in the monthly overview.
   **The plan (owner decision 2026-09-26):** the first four come from configuration; the
   1410 note is dropped.
5. **The supporting-documents folder is not inside the books folder** (`2026/underlag`,
   next to `Bokföring/`). All new paths are configured relative to the configuration
   directory, like `books.path`.
6. **Supporting-document existence needs file I/O,** which the domain may not do
   (ADR-006, Ruff `TID251`). The CLI lists the documents folder and passes the set of
   names to the check.
7. **Some rules can only be proven on fixtures.** The real books have 0 unbooked
   transactions, no bank errors and no parked postings, so for those rules the pilot only
   proves the OK case.
8. **The reports embed a generation timestamp,** so they are compared by figures, as the
   MVP already says, never byte for byte. The core takes the clock as a parameter so that
   its own tests are deterministic.
9. **Stale status documents:** `overview.md`, `current-state.md` and `roadmap.md` still
   say MVP-002 is in progress or pending its pull request; PR #7 is merged. Fixed in
   TODO 1.4.
10. **Reading rule:** a code comment in the organisation's import script contains a first
    name. It was not copied. It is noted under `GAP-F2-CONFIDENTIAL` in TODO 11.3.

### 0.3 The semantics to reproduce (from the organisation's scripts)

**Bank import (`importera_kontoutdrag.py`):**
- The export is detected by its header: `Datum`, `Belopp` and `Saldo` → statement;
  exactly `Datum;Belopp` → fund value; anything else is refused.
- Read as `utf-8-sig`, `;`-separated; rows with only blank cells are skipped.
- Statement: the bank lists newest first; the file is written oldest first. Columns
  `datum;belopp;namn;meddelande;anteckning;saldo`:
  - `datum`: `/` replaced by `-`;
  - `belopp`, `saldo`: spaces and non-breaking spaces removed, `,` → `.`, normalised by
    `Decimal`; empty stays empty;
  - `namn`: `Ytterligare detaljer`, or `Namn` when that is empty;
  - `meddelande`: leading zeros stripped when it is all digits;
  - `anteckning`: `Egna anteckningar`;
  - `namn`, `meddelande` and `anteckning` masked.
- Refused when the export's first date is later than the existing file's first date
  ("fetch the whole year from 1 January"). Otherwise the whole file is replaced.
- Fund value: merged with the existing file by date, written sorted, `datum;värde`.
- Written as UTF-8 without BOM, LF, `;`. The export itself is never changed.

**Reconciliation (`kontroll.py`, `kontrollera_bank`):**
- The statement file: exact header; valid dates and amounts; dates within the fiscal
  year; oldest first. A missing file is info, not an error.
- Bank arithmetic: every end-of-day balance implies an opening balance; they must all be
  equal.
- The opening balance of the bank account must equal the implied balance before the
  first transaction.
- Matching on (date, signed amount), as multisets. The core's signed amount is the
  voucher's net on the bank account (debit − credit), which equals `belopp` under the
  bank-sign rule.
  - booked but not in the statement → error;
  - in the statement, not booked, dated on or before the last voucher → error;
  - after the last voucher → one warning with the count and net; listed as info with
    `--unbooked`.
- A summary info: number of transactions, period and the bank's latest balance.

**Remaining checks (`kontroll.py`):**

| `kontroll.py` rule | What | Severity | Core (rule ids settled in the tests) |
|---|---|---|---|
| `kontoplan` | Account twice | warning | general check |
| `kontoplan` | Local name missing | error | general check |
| `kontoplan` | `kontoklass` ≠ class by first digit | error | `front-matter` reader (format column) |
| `kontoplan` + `kontobas` | On the BAS "do not use" list; reference description differs (warning) or is missing (info: own meaning); unknown group (error); group differs (warning); own accounts not in BAS (info); reference files missing (warning) | as listed | reference-chart checks |
| `verifikation` | Date earlier than the previous voucher | warning | general check |
| `verifikation` | Revenue account (class 3) debited; cost account (classes 4–8) credited | warning | general check |
| `dubblett` | Same date, signed amount and text | warning | general check; no text in the message |
| `underlag` | Supporting document does not exist | error | check with the document set from the CLI |
| `underlag` | N of M vouchers without documents (of which costs) | info | summary |
| `parkering` | Postings on the parking account, net to distribute | info | summary, accounts from configuration |
| `kontoplan` | Unused accounts | info | summary |
| `fond` | Market value vs booked value; invalid value (error) | info | fund check |
| `budget` | Unknown type, invalid amount, unknown account, account on two items, account class not matching the type (errors); totals (info) | as listed | budget check |
| `kommentarer` | id sequence, date, type, accounts and vouchers exist, text present (errors); personal number (warning); count (info) | as listed | closing-comments check |
| `att-göra` | Duplicate id, owner, when, status, dependency, required fields (errors); waiting without a dependency (warning); open count (info) | as listed | to-do check |

**Reports (`generera_redovisning.py`), all to one output folder, overwritten each run:**
- summary; income statement; balance sheet; budget follow-up; monthly overview; general
  ledger with trial balance; voucher list; to-do list; closing comments;
- refused when the checks give errors, unless forced;
- amounts formatted `1 234,50` (non-breaking space, decimal comma); every table cell
  masked; a header with the organisation's name and number, the fiscal year, the period
  up to the last voucher date, and "preliminary";
- the member-fee report, the member section of the summary, and the member rows and
  sections of the to-do report are **not** moved (MVP out of scope).

### 0.4 Owner decisions (2026-09-26)

1. **Reports are in Swedish.** Code, findings and terminal output stay in English
   (documentation.md). Recorded in ADR-008.
2. **The core owns the supplementary file formats** — headers and allowed values (comment
   types, to-do owners `kassör`/`vi`, when, status), as the `front-matter` reader owns
   its files. Configuration gives paths and truly organisation-specific values only.
3. **Conventions in configuration:** the accounts that need no supporting document, the
   guessed-posting marker, the outlay text prefix, and the parking accounts. The 1410 note
   is dropped.
4. **Duplicate key** as `kontroll.py`: date, text and the amount signed as the bank shows
   it. The pilot must show 3 duplicates.
5. **One MVP,** not split into two, although it is large (≈ 11 phases). It is internal
   for now.
6. **The AI tool may run the organisation's scripts for the pilot comparisons,** with
   output redirected to the scratchpad and only counts or equal/not equal reported.

### 0.5 Other findings

- **No new dependencies:** `csv`, `decimal`, `datetime`, `os` (atomic replace) are
  standard library. Markdown is written by hand, as the organisation's script does.
- **Module boundary:** a new `accounting_agent.reports` package renders Markdown strings
  and does no I/O. It falls under the existing global `TID251` ban automatically; the
  CLI writes the files.
- **The existing `example` fixture stays as it is,** so the MVP-002 CLI tests keep their
  exact output. The new sections go into a second synthetic organisation,
  `tests/fixtures/example-full/`.
- **The organisation's name and number** are hard-coded in its report script; in the
  core they come from configuration.
- **The organisation scripts write to fixed paths** (`Bokföring/`, `Redovisning/`). For
  the pilot they are run from a throwaway scratchpad script that redirects those paths to
  the scratchpad.

## 1. Goal

When this plan is done:

- `accounting_agent.books` also holds, without file I/O:
  - `Account` with an optional group and reference description (ADR-007);
  - models for bank transactions (date, amount, balance, row — no name or message), fund
    values, budget items, closing comments, to-do items and the reference chart;
  - reconciliation against the bank;
  - the remaining checks from `kontroll.py` except members.
- `accounting_agent.formats` has a `nordea-csv` export reader, a reader and writer for
  the bank statement and fund-value files, and readers for the reference chart, budget,
  closing comments and to-do list.
- `accounting_agent.reports` renders the nine reports as Swedish Markdown strings.
- `organisation.yaml` has validated optional sections for the bank, the checks, the
  conventions and the reports.
- Commands:
  - `accounting-agent import-bank <org> --config-dir <dir> <export-file>` writes the bank
    statement or fund-value file (never vouchers);
  - `accounting-agent validate … [--balances] [--unbooked]` runs every check in scope
    that is configured;
  - `accounting-agent report <org> --config-dir <dir> [--force]` writes the reports to
    the configured folder, and refuses on errors unless forced.
- Helsingborgs Judoklubb's 2026 books give the same statement file, the same outcome per
  rule and the same report figures as its own scripts.
- ADR-007, ADR-008, the glossary, the architecture documents and
  `organisation-projects.md` describe it.

## 2. Scope boundary

- **In:**
  - `src/accounting_agent/books/` — model extension, new models, reconciliation, checks;
  - `src/accounting_agent/formats/` — `nordea_csv.py`, `bank_statement.py`,
    `reference_chart.py`, `supplements.py` (budget, closing comments, to-do list), and
    the chart columns in `front_matter.py`;
  - `src/accounting_agent/reports/` — new package;
  - `profile.py`, `cli.py`;
  - tests and synthetic fixtures under `tests/`;
  - ADR-007, ADR-008, glossary, `overview.md`, `current-state.md`, `README.md`,
    `AGENTS.md`, `roadmap.md`, `organisation-projects.md`, the MVP-003 document;
  - methodology-compliance updates;
  - **in the Helsingborgs Judoklubb project:** only the new sections in
    `2026/organisation.yaml`, which the owner commits there.
- **Out:**
  - member checks, `medlemmar.csv`, `medlemsbetalningar.csv`, `medlemskontroll.py` and
    the member-fee report, including member measures in the summary and to-do reports;
  - creating or changing vouchers, or suggesting postings for unbooked transactions;
  - bank transaction pages in PDF;
  - other banks' export formats;
  - an Aktivitet Förebygger reader and JudoSyd;
  - scheduling and unattended runs; agent tools (R3);
  - changing or removing the organisation's own scripts;
  - the 1410 stock note;
  - new dependencies.

## 3. Chapters addressed

- **B3** Architecture principles — the reports package stays free of I/O under the
  existing `TID251` boundary; the first write paths are confined to the CLI and
  `formats/`.
- **B5** Documentation — ADR-007, ADR-008, glossary, README, the organisation guide.
- **C1** SKA 4 — STRIDE pass (§5), for the first write and for reports with voucher texts.
- **D1** — AI-TDD with owner review of the tests before each implementation; coverage
  floor re-measured.
- **E4** SKA 3 — masking in written files as well as terminal output.
- **F2** SKA 2 — the reading rule applied to the pilot (`GAP-F2-CONFIDENTIAL`,
  continued).

No gap-register row is expected to close; `GAP-F2-CONFIDENTIAL` gets a note.

## 4. TODOs

Every phase that adds production code follows the MVP-002 pattern: tests first, **STOP for
the owner's review of the tests**, then the implementation. Each test must fail for the
right reason before the implementation is written. Every phase runs `pytest` and
`ruff check` before its commit, and updates `current-state.md` (tests, capabilities) in
the same phase.

### Phase 1 — Decisions and corrections

- [x] 1.1 Update `docs/mvp/MVP-003-bank-reconciliation-and-reports.md` with a dated
  correction note per §0.2 and §0.4:
  - the model extension;
  - `[personnummer]` in written files;
  - no names in findings and `--unbooked`;
  - the conventions in configuration;
  - Swedish reports;
  - the dropped 1410 note.

  *Verify:* every change traces to §0; the acceptance criteria are unchanged in meaning.
  Result: a dated correction note at the top with seven points, each tracing to §0.2 or
  §0.4. The scope's configuration bullet also lists the conventions. The acceptance
  criteria are unchanged.
- [x] 1.2 Write **ADR-007 — supplementary book files and account groups**:
  - `Account` gets an optional group and reference description;
  - bank transactions, fund values, budget, closing comments, to-do items and the
    reference chart get domain models;
  - each file has a core-owned, neutrally named format with its reader in `formats/`;
  - bank transactions carry no counterparty name or message in the domain.

  It references ADR-006, which is not edited. Add the index row. *Verify:* Nygard
  sections present; index row added.
  Result: `ADR-007-supplementary-book-files.md`, accepted; Context, Decision,
  Consequences and Alternatives considered; index row added.
- [x] 1.3 Write **ADR-008 — the core writes derived files, never vouchers**:
  - the first write paths: the bank statement and fund-value files, and the reports;
  - only to configured paths; an atomic replace; the export is never changed;
  - a partial export is refused;
  - reports in Swedish, with `[personnummer]` masking;
  - no reports from books with errors unless forced.

  *Verify:* Nygard sections present; index row added.
  Result: `ADR-008-core-writes-derived-files.md`, accepted; all Nygard sections; index
  row added.
- [x] 1.4 Fix the stale status in `overview.md`, `current-state.md` and `roadmap.md`
  (MVP-002 merged in PR #7; MVP-003 in planning). Extend `glossary.md`: kontoutdrag,
  avstämning, fondvärde, budget, bokslutskommentar, att-göra, parkeringskonto,
  kontogrupp, BAS-kontoplan, resultatrapport, balansrapport, huvudbok, saldobalans,
  verifikationslista. *Verify:* every new model name in §1 is in the glossary.
  Result:
  - `overview.md` (current state, planned evolution, open questions), `current-state.md`
    and the roadmap's "Current Status" now say MVP-002 is merged and MVP-003 in
    progress. The roadmap's stale "MVP-002 has no plan yet" paragraph was removed.
  - 21 glossary rows added, also bank export, bank transaction, unbooked, outlay, budget
    follow-up and monthly overview. Every model named in §1 (bank transaction, fund
    value, budget item, closing comment, to-do item, reference chart, account group) is
    covered; checked by reading §1 against the table.

Commit: `docs(mvp-003): correct the MVP and record ADR-007 and ADR-008`

### Phase 2 — Profile: the new sections

- [ ] 2.1 **Tests first** (`tests/test_profile_sections.py`), all sections optional:
  - `bank`: `export_format` (`nordea-csv`), `statement_file`, `fund_account`,
    `fund_value_file`;
  - `checks`: `reference_chart` (a directory), `documents` (a directory), `budget_file`,
    `comments_file`, `todo_file`;
  - `conventions`: `parking_accounts`, `no_document_accounts` (lists of four-digit
    accounts), `guessed_posting_marker`, `outlay_prefix` (strings);
  - `reports`: `output` (a directory path; may not exist yet), `organisation_name`,
    `organisation_number`.

  Paths resolve relative to the configuration directory. Errors: wrong types, unknown
  export format, non-four-digit accounts, a missing input directory. Unknown sub-keys
  give a warning. A profile without the sections still loads.
  *Verify:* the tests fail for the right reason.
- [ ] 2.2 **STOP — the owner reviews the tests from 2.1.**
- [ ] 2.3 Implement the sections in `profile.py` and add them to `KNOWN_KEYS`.
  *Verify:* all tests pass; Ruff clean; the MVP-002 profile tests unchanged.

Commit: `feat(profile): add bank, checks, conventions and reports sections`

### Phase 3 — Bank import

- [ ] 3.1 **Synthetic fixtures:** `tests/fixtures/bank/` with a small `nordea-csv`
  statement export (newest first, `utf-8-sig`, amounts with spaces and decimal comma, a
  blank row, a name only in `Namn`, one in `Ytterligare detaljer`, an all-digit message
  with leading zeros, Skatteverket's public test number in a message) and a fund-value
  export. Invented names only. *Verify:* each rule in §0.3 "Bank import" is represented.
- [ ] 3.2 **Tests first:**
  - `mask_personal_numbers(text, mask=...)` with the Swedish mask; the default
    unchanged;
  - the export reader: header detection (statement, fund value, refused);
  - the statement writer: exact expected bytes (oldest first, normalised amounts, masked,
    LF, no BOM);
  - the refusal rule; replacing an existing file; fund merge by date;
  - the export file is unchanged afterwards;
  - `import-bank` CLI end to end on a temporary copy of `example-full`: exit codes,
    organisation mismatch, missing `bank` section, a summary line with counts only — no
    names on stdout.

  *Verify:* the tests fail for the right reason.
- [ ] 3.3 **STOP — the owner reviews the fixtures and tests from 3.1–3.2.**
- [ ] 3.4 Implement `formats/nordea_csv.py`, `formats/bank_statement.py` (write path,
  atomic replace) and the `import-bank` command. *Verify:* tests pass; Ruff clean.
  Update `README.md` and `AGENTS.md` (commands).

Commit: `feat(bank): import bank exports into masked statement and fund-value files`

### Phase 4 — Reconciliation

- [ ] 4.1 **Tests first:**
  - the statement-file reader: header, invalid date/amount, outside the fiscal year, not
    oldest first, missing file (info); the domain objects carry no name or message;
  - `reconcile(books, transactions, bank_account)`: a clean case; a bank-balance break;
    an opening-balance mismatch; booked but not in the statement; unbooked before the
    last voucher (error); unbooked after (one warning with count and net); the summary
    info; duplicates of the same (date, amount) as multisets;
  - no message contains a counterparty name or message (a fixture with an invented
    name);
  - `validate` runs reconciliation when `bank` is configured; `--unbooked` lists date,
    amount and statement row only.

  *Verify:* the tests fail for the right reason.
- [ ] 4.2 **STOP — the owner reviews the tests from 4.1.**
- [ ] 4.3 Implement the reader, `books/reconciliation.py` and the CLI wiring.
  *Verify:* tests pass; Ruff clean; README updated (`--unbooked`).

Commit: `feat(books): reconcile the books against the bank statement`

### Phase 5 — Remaining voucher checks and summaries

- [ ] 5.1 **Tests first**, on model objects:
  - duplicate (date, text, bank-signed amount) → warning naming the voucher numbers, not
    the text;
  - date earlier than the previous voucher → warning;
  - revenue account debited, cost account credited → warnings;
  - a missing supporting document, given the set of existing names → error; N of M
    without documents (of which costs) → info;
  - parking accounts from configuration → info with count and net;
  - unused accounts → info;
  - chart: an account twice → warning; a missing name → error.

  CLI: `validate` lists the configured documents folder and passes the names. The
  `valid/` fixture still gives no errors. *Verify:* the tests fail for the right reason.
- [ ] 5.2 **STOP — the owner reviews the tests from 5.1.**
- [ ] 5.3 Implement in `books/checks.py` (or a sibling module if it passes the advisory
  complexity 10) and the CLI wiring. *Verify:* tests pass; Ruff, including C90, clean.

Commit: `feat(books): add duplicate, date-order, account-side and document checks`

### Phase 6 — Chart of accounts against the BAS reference

- [ ] 6.1 **Synthetic fixture:** `tests/fixtures/reference/` — a tiny invented reference
  chart in the four-file format (main accounts, sub-accounts, groups, do-not-use), not a
  copy of BAS. *Verify:* it covers every reference rule in §0.3.
- [ ] 6.2 **Tests first:**
  - the `front-matter` reader keeps `kontogrupp` and `bas_beskrivning` on `Account`, and
    reports a `kontoklass` that does not match the first digit;
  - the reference reader; missing files → one warning and the check skipped;
  - the reference checks, one test per rule; messages never quote the local name.

  *Verify:* the tests fail for the right reason.
- [ ] 6.3 **STOP — the owner reviews the fixture and tests from 6.1–6.2.**
- [ ] 6.4 Implement the model extension, `formats/reference_chart.py`, the checks and the
  wiring. *Verify:* tests pass; Ruff clean; the MVP-002 tests unchanged.

Commit: `feat(books): check the chart of accounts against a reference chart`

### Phase 7 — Fund value, budget, closing comments and to-do list

- [ ] 7.1 **Tests first**, with fixtures in `tests/fixtures/example-full/`:
  - fund value: latest market value vs booked balance → info; invalid value → error;
  - budget: every rule in §0.3 and the totals;
  - closing comments: every rule, including a personal number → warning;
  - to-do list: every rule, with the owners `kassör` and `vi`;
  - a missing optional file → the check is skipped;
  - no message quotes a comment's or task's text.

  *Verify:* the tests fail for the right reason.
- [ ] 7.2 **STOP — the owner reviews the tests from 7.1.**
- [ ] 7.3 Implement the models, `formats/supplements.py`, the checks and the wiring.
  *Verify:* tests pass; Ruff clean.

Commit: `feat(books): check fund value, budget, closing comments and to-do list`

### Phase 8 — Reports I: framework and the accounts

- [ ] 8.1 **Tests first** (`tests/test_reports_*.py`), on `example-full`:
  - amount formatting (`1 234,50`, negative, whole kronor);
  - the header (name, number, fiscal year, period to the last voucher, preliminary) with
    an injected clock;
  - every table cell masked with `[personnummer]`; `|` escaped;
  - income statement, balance sheet (balances, "Balansen stämmer"), general ledger with
    trial balance, voucher list, monthly overview — expected figures computed by hand for
    the fixture;
  - grouping by `Account.group`, and the two-digit fallback without it;
  - `report` CLI: writes the files to the configured folder; refuses on errors (exit 1,
    no files written); `--force`; organisation mismatch; missing `reports` section.

  *Verify:* the tests fail for the right reason.
- [ ] 8.2 **STOP — the owner reviews the tests from 8.1.**
- [ ] 8.3 Implement `accounting_agent/reports/` (pure rendering) and the `report` command.
  *Verify:* tests pass; Ruff clean; `ruff check` shows `reports/` under the `TID251`
  ban (a temporary `import pathlib` there is reported, then removed). README, AGENTS and
  `overview.md` updated.

Commit: `feat(reports): render the income statement, balance sheet, ledger and lists`

### Phase 9 — Reports II: budget, comments, to-do and summary

- [ ] 9.1 **Tests first:**
  - budget follow-up: share of the year, per item, unbudgeted accounts, totals;
  - closing comments: grouped by type with the Swedish headings;
  - to-do: the measures without member measures (errors, unbooked, bank matches,
    parking, guessed postings by the configured marker, payments without documents
    except the configured accounts, outlays first by the configured prefix), then the
    open tasks per owner and when;
  - summary: figures, budget, measures, tasks, the check result and the report links —
    without the member section.

  *Verify:* the tests fail for the right reason.
- [ ] 9.2 **STOP — the owner reviews the tests from 9.1.**
- [ ] 9.3 Implement. *Verify:* tests pass; Ruff clean.

Commit: `feat(reports): render budget follow-up, closing comments, to-do and summary`

### Phase 10 — Pilot: Helsingborgs Judoklubb through the core

- [ ] 10.1 Add the new sections to `HJK - Ekonomi/2026/organisation.yaml` (configuration
  only). *Verify:* `validate` loads it; the owner commits it in the HJK repository.
- [ ] 10.2 **Bank statement:** a throwaway scratchpad script picks the latest statement
  export by header without printing file names. It runs the organisation's import and the
  core's `import-bank`, both with output redirected to the scratchpad, and prints only
  equal / not equal plus row counts. It also compares with the existing
  `kontoutdrag-1930.csv`. *Verify:* equal; any difference is investigated by row number
  and column only.
- [ ] 10.3 **Checks:** run `validate` and `kontroll.py`, reduce both to counts per
  severity and rule, map the rules per §0.3, and compare. Compare the unbooked
  transactions on (date, amount) with `--unbooked` and `--obokförda`. *Verify:* the same
  counts per rule in scope (§0.1: 3 duplicates, 4 personal numbers, 1 chart warning, the
  corresponding info), and 0 unbooked on both sides.
- [ ] 10.4 **Reports:** run `generera_redovisning.py` (output redirected) and `report`
  to the scratchpad. A throwaway script parses both sets of Markdown tables and prints
  only "N of M amounts equal" per report, plus the account numbers that differ. Delete
  the outputs. *Verify:* all equal for the nine reports in scope.

Commit: `docs(mvp-003): record the Helsingborgs Judoklubb pilot result`

### Phase 11 — Close

- [ ] 11.1 Update `docs/development/organisation-projects.md`: what Helsingborgs Judoklubb
  now runs through the core (import, validate, report), the new configuration sections,
  and the Swedish `CLAUDE.md` section. *Verify:* the documented commands run as written
  on `example-full`.
- [ ] 11.2 Re-measure coverage; keep or raise `fail_under`; update interpretations §1.
  *Verify:* `pytest --cov` passes at the floor.
- [ ] 11.3 Gap register: note the pilot and the §0.2 (10) observation under
  `GAP-F2-CONFIDENTIAL`; add a changelog entry and the follow-up plan index row.
  *Verify:* the rows reference this plan.
- [ ] 11.4 Verify each acceptance criterion against the real system:
  - fixtures pass and fail per rule (test run);
  - the statement byte comparison (10.2);
  - `validate` against `kontroll.py` per rule, and the unbooked transactions (10.3);
  - report figures (10.4);
  - `git grep` in `src/` for organisation-specific values (organisation names, ids,
    `1930`, `1350`, `3008`, `6570`, `2026`, `Bokföring`, `Gissad`), expecting none;
  - findings never quote a voucher text, name or message (tests from 4.1, 5.1, 6.2, 7.1);
  - reports written only to the configured folder and masked (tests from 8.1);
  - the MVP-001 gates green (all CI checks locally, then the PR);
  - `git ls-files docs/reference` is empty.

  Fill in "Outcome at close" in the MVP.

Commit: `docs(mvp-003): close MVP-003`

## 5. Risks / open questions

- **Size.** About 11 phases on one branch, against E1 SKA 1's short-lived branches.
  Accepted by the owner (§0.4). Each phase ends in a green, self-contained commit, so the
  branch can be reviewed commit by commit.
- **Reports leaking Confidential data (highest risk).** The voucher list and general
  ledger contain voucher texts by design. Mitigations: written only to the configured
  output folder in the organisation's own project; every cell masked; the pilot compares
  figures only and deletes outputs; stdout shows counts only.
- **Findings quoting data.** The domain's bank transaction has no name or message field,
  and tests assert that no message contains invented fixture names.
- **Masking misses.** The same pattern as the organisation's scripts; a number in an
  unusual format is still possible, as in MVP-002.
- **"Same outcome" is per-rule counts.** `kontroll.py` groups many rules under
  `kontoplan`, `verifikation` and `bank`; the mapping in §0.3 is the basis. On the real
  books many error rules are only proven on fixtures (§0.2 (7)).
- **Byte identity depends on the export.** If the existing statement file was produced
  from an older export, 10.2 compares the two tools on the same export as the primary
  proof, and reports the comparison with the existing file separately.
- **Report figures may differ where the scripts use organisation shortcuts** (equity by
  group name, grouping by `kontogrupp`). The core reads the group from the chart, so the
  figures should match; any difference is investigated by account number.
- **Deferred on purpose:** members (backlog, high priority), other banks, PDF statements,
  Aktivitet Förebygger.

### STRIDE (C1 SKA 4) — new flows: the core writes bank files and reports

```text
bank export (owner's download) → import-bank → masked statement / fund-value file (books folder)
books + statement + supplementary files → validate → masked findings (stdout)
books + supplementary files → report → Swedish Markdown reports (configured output folder)
```

| Threat | Relevance | Mitigation |
|---|---|---|
| **S**poofing | Running one organisation's command against another's files | The profile's organisation check, reused by `import-bank` and `report` |
| **T**ampering | Overwriting the statement file with a partial export; writing outside the configured paths; corrupting vouchers | The refusal rule; writes only to configured paths; atomic replace; never a write path to vouchers (ADR-008); the export is never changed |
| **R**epudiation | Who imported which export | The organisation project's git history shows the statement change; the audit trail is R3 |
| **I**nformation disclosure | Names, messages and personal numbers reaching stdout, AI context or the public repository | No name or message in the domain model; findings without texts; `[personnummer]` masking in written files; reports only in the organisation's folder; synthetic fixtures; pilot output reduced to counts |
| **D**enial of service | Large or malformed exports | Local, owner-controlled input; header detection and per-row errors instead of crashes (tested) |
| **E**levation of privilege | Configured paths pointing outside the organisation folder | Local and owner-controlled; accepted, as in MVP-002. Revisit if the core ever runs on untrusted configuration |

## 6. Found during this MVP

- *(none yet)*
