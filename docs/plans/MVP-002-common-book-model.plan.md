# Plan: MVP-002 – Common book model and validation via core

Reference: [`docs/mvp/MVP-002-common-book-model.md`](../mvp/MVP-002-common-book-model.md)

**Status:** In progress — phases 1–5 done, phase 6 next.

## 0. Investigation

Carried out 2026-09-25 with read-only commands. When reading the organisation projects,
only **code** was read, per the reading rule in
[`interpretations.md` §9](../methodology-compliance/interpretations.md#9-data-classification-for-ai-use-f2).
No book, voucher, bank or member file was opened.

### 0.1 The MVP's premise was wrong: Aktivitet Förebygger's books are not "the same"

The MVP (and MVP-001 plan §0) says Helsingborgs Judoklubb and Aktivitet Förebygger "keep
their books in the same way". Reading both projects' code (`kontroll.py`,
`bygg-redovisning.py`) shows they share only the **concept**. The format and the voucher
model differ:

| | Helsingborgs Judoklubb | Aktivitet Förebygger |
|---|---|---|
| Voucher file | Front matter between `---` lines, **one** debit/credit pair, amount signed as the bank shows it | A **Markdown table**: `\| **Key** \| value \|` rows, then **several posting lines** `\| account \| name \| debit \| credit \|` |
| Numbering | 1..N, file name `NNNN_YYYY-MM-DD.md` | **Voucher series** (letters, e.g. K, B), numbered 1..N per series; any file name |
| Chart of accounts | 5 columns: class, group, account, BAS description, local name | 3 columns: account, name, type |
| Opening balance | One signed column (debit +, credit −) | Separate debit and credit columns |
| Tolerance | Rejects a BOM; CRLF gives a warning | Reads `utf-8-sig`, tolerant |

**What the plan does instead — approved by the owner 2026-09-25:**
- The core model is **general double-entry**: a voucher has an optional **series**, a
  number and **N posting lines** (account, debit, credit). A Helsingborgs Judoklubb voucher
  becomes two lines. Aktivitet Förebygger's vouchers fit the same model later, without
  changing it.
- This MVP implements **one reader**, for the front-matter format that Helsingborgs
  Judoklubb uses. The format gets a neutral name, `front-matter`, not an organisation name.
- Aktivitet Förebygger is compared **on paper**, as the MVP already says. An
  Aktivitet Förebygger reader becomes its own later MVP.
- The "amount sign vs. bank account" rule belongs to the **front-matter format**, which
  records amounts "as the bank shows them". It is not a property of the double-entry model,
  so the reader checks it, not the general checks.
- The MVP document is corrected in TODO 1.1. The roadmap gets the Aktivitet Förebygger
  reader as a new item.

### 0.2 Front matter is not YAML

`kontroll.py` parses the front matter with its own line-based reader:
- `key: value` on each line;
- a value starting with `"` is decoded as a **JSON string**;
- unknown keys, duplicate keys and missing required keys are errors.

A YAML parser would turn `belopp: -1305.55` into a float and `datum: 2026-03-05` into a
date object. **The core therefore gets its own parser with the same semantics.** Amounts
become `Decimal` directly from the text, validated against `-?\d+(\.\d{1,2})?`, exactly as
`kontroll.py` does. PyYAML stays for `organisation.yaml` only.

### 0.3 The exact semantics to reproduce (from `kontroll.py`)

- **Files:** `kontoplan.csv`, `ingående-balans.csv` and `verifikationer/`. The CSV files
  are UTF-8 without BOM, semicolon-separated, with an exact header row and LF line endings.
  A BOM is an error. CRLF is a warning. Wrong header or column count is an error. An empty
  row is a warning.
- **Voucher fields:**
  - required: `verifikation`, `datum`, `text`, `belopp`, `debet`, `kredit`;
  - optional: `underlag`, which may list several files separated by `;`;
  - the free text below the front matter is the note.
- **Checks:**
  - the file name's number and date must match the fields;
  - numbering must be exactly 1..N;
  - `debet` and `kredit` must be different accounts, and both must exist in the chart;
  - sign rule: debit bank → amount ≥ 0; credit bank → amount ≤ 0; bank not involved →
    amount ≥ 0;
  - personal identity number pattern in `text` → warning;
  - the opening balance must sum to 0, each account at most once, balance accounts only
    (first digit 1 or 2).
- **Balances:** opening balance + |amount| on the debit account − |amount| on the credit
  account (debit +, credit −).
- **The fiscal year** is taken from the folder name (`2026/`). The core takes it from
  configuration instead.

### 0.4 Baseline on the real books (aggregates only)

`kontroll.py` was run in the Helsingborgs Judoklubb project with its output redirected to a
temporary file. Only level and rule counts were extracted, and the file was deleted.

| Measure | Value |
|---|---|
| Chart of accounts / opening-balance rows / vouchers | 33 / 8 / 163 |
| Result | `OK` — 0 errors, 8 warnings, 15 info |
| Warnings in this MVP's scope | 4 × personal identity number in voucher text |
| Warnings outside scope | 3 × duplicate, 1 × other |

**Expected core result on the same books:** 0 errors, 4 personal-identity-number warnings,
and all account balances equal to `kontroll.py --saldon`.

**Core baseline:** 29 tests, 96.47 % coverage, floor 90 %.

### 0.5 Checks in scope — owner decision 2026-09-25

The MVP's seven checks, plus the neighbouring general checks the owner accepted:
- zero amount;
- missing text;
- date outside the fiscal year;
- opening balance: unknown account, not a balance account, or the same account twice;
- chart of accounts: account number not four digits.

**Deferred:**
- "revenue account debited" / "cost account credited" warnings;
- the duplicate-voucher warning;
- date order;
- validation against the BAS chart (`kontobas/`);
- existence of supporting documents (MVP-003, with documents);
- parking-account and unused-account summaries (reports). The owner decided the parking
  accounts wait until a check or report needs them.

### 0.6 Other findings

- `profile.py` ignores unknown top-level keys with a warning. The new `books:` section
  must be added to `KNOWN_KEYS`.
- **Module boundary (`GAP-B3-BOUNDARIES`):** Ruff's `TID251` (`banned-api`) exists. With a
  global ban on file-I/O modules plus `per-file-ignores` for the reader and CLI packages,
  the domain package can be kept free of I/O without a new dependency. Verified: `ruff rule
  TID251`.
- **Comparing against the real books without exposing data** works as in 0.4: run, filter
  to counts, delete the output. Balances are compared by a throwaway script in the
  scratchpad, never committed, that prints only "N of M accounts equal". **The owner
  approved the AI tool running this comparison (2026-09-25).**
- **Configuration location:** `HJK - Ekonomi/2026/organisation.yaml`, with
  `books.path: Bokföring` and `fiscal_year: 2026` — one file per year, like the project's
  folders (owner decision).
- **No new dependencies:** `csv`, `decimal`, `json`, `re` and `pathlib` are all standard
  library.

## 1. Goal

When this plan is done:

- `accounting_agent.books` is a pure domain package, free of I/O:
  - model classes `Account`, `OpeningBalance`, `PostingLine` and `Voucher` (optional
    series, N lines), plus `Books`;
  - `Finding` with `Severity` (error / warning / info);
  - `compute_balances()`;
  - the general checks;
  - masking of personal identity numbers.
- `accounting_agent.formats.front_matter` reads an organisation's chart-of-accounts CSV,
  opening-balance CSV and voucher folder into `Books`. It reports parse-level and
  format-level findings, including the bank-sign rule.
- `organisation.yaml` has a validated `books:` section with `path`, `format`,
  `fiscal_year` and `bank_account`.
- `accounting-agent validate <org> --config-dir <path> [--balances]` prints findings
  grouped by severity, never echoes voucher text, masks all output, and exits 1 on any
  error.
- Helsingborgs Judoklubb's 2026 books validate through the core, with the same in-scope
  outcome as `kontroll.py` and identical balances.
- ADR-006, a glossary, the Aktivitet Förebygger comparison and the updated architecture
  docs describe it.

## 2. Scope boundary

- **In:**
  - `src/accounting_agent/books/` — model, balances, findings, checks, masking;
  - `src/accounting_agent/formats/front_matter.py`;
  - `profile.py` (`books` section) and `cli.py` (`validate`);
  - tests and synthetic fixtures under `tests/`;
  - Ruff `banned-api` configuration in `pyproject.toml`;
  - ADR-006, `docs/architecture/glossary.md`, `docs/architecture/overview.md` and
    `current-state.md`, `README.md`, `AGENTS.md` (structure table);
  - corrections to the MVP-002 document and the roadmap;
  - the Aktivitet Förebygger comparison;
  - methodology-compliance updates (gap rows, interpretations §1);
  - **in the Helsingborgs Judoklubb project:** only a new `2026/organisation.yaml`,
    which the owner commits there.
- **Out:**
  - an Aktivitet Förebygger (table-format) reader;
  - writing or changing vouchers;
  - bank import and reconciliation;
  - supporting-document existence;
  - reports and balance *reports* (only the `--balances` listing);
  - BAS/`kontobas` validation;
  - the revenue/cost, duplicate and date-order warnings;
  - parking accounts;
  - changing `run`;
  - changing or removing anything in `kontroll.py` or other organisation-project code;
  - agent tools and LLM calls;
  - new dependencies.

## 3. Chapters addressed

- **B3** Architecture principles — domain/IO split, enforced by Ruff `TID251`; closes
  `GAP-B3-BOUNDARIES`.
- **B4** Data modelling (spirit) — the core validates the file store's integrity; the
  store has no constraints of its own.
- **B5** Documentation — ADR-006, glossary, README.
- **C1** SKA 4 — STRIDE pass (§5).
- **D1** — AI-TDD with owner review of the tests before each implementation; coverage
  floor re-measured and raised (interpretations §1).
- **E4** SKA 3 — masking of personal identity numbers in all output; closes
  `GAP-E4-MASKING`.
- **F2** SKA 2 — the reading rule (§9) is applied to the pilot and the comparison; no
  Confidential data enters AI context (`GAP-F2-CONFIDENTIAL`, continued).

## 4. TODOs

Every phase that adds production code follows the same pattern: tests first, **STOP for the
owner's review of the tests**, then the implementation. Each test must fail for the right
reason before the implementation is written.

### Phase 1 — Correct the MVP, decide the model

- [x] 1.1 Update `docs/mvp/MVP-002-common-book-model.md` per §0.1 and §0.5:
  - the general model (series, N lines);
  - one reader, for the `front-matter` format;
  - the check list from §0.5;
  - no parking accounts;
  - the Aktivitet Förebygger reader moved to a later MVP.

  Add "Aktivitet Förebygger reader (table format, voucher series)" to the roadmap. *Verify:*
  every change traces to §0; the acceptance criteria still say the same about
  Helsingborgs Judoklubb.
  Result: the MVP has a dated correction note at the top; scope, out-of-scope and the
  Aktivitet Förebygger criterion were adjusted. The roadmap gets "Aktivitet Förebygger
  reader" under R2.
- [x] 1.2 Write **ADR-006 — core book model**: double-entry vouchers with optional series
  and N lines; organisation file formats read by format-specific readers; amounts are
  `Decimal`, never floats. It references ADR-004 (files, no database); ADR-004 itself is
  accepted and is not edited. Add the index row. *Verify:* Nygard sections present; index
  row added.
- [x] 1.3 Write `docs/architecture/glossary.md`: verifikation → voucher, kontoplan → chart
  of accounts, ingående balans → opening balance, konto → account, debet/kredit →
  debit/credit, verifikationsserie → voucher series, underlag → supporting document,
  räkenskapsår → fiscal year, saldo → balance. Link it from `overview.md`. *Verify:* every
  English model name used in §1 is in the glossary.
  Result: all model names (`Books`, `Account`, `OpeningBalance`, `PostingLine`, `Voucher`,
  `Finding`) and the severities are in the glossary; checked with a script.

Commit: `docs(mvp-002): correct the book-model premise and record ADR-006`

### Phase 2 — Profile: the `books` section

- [x] 2.1 **Tests first.**
  - A valid `books` section loads: `path` resolved relative to the config directory;
    `format: front-matter`; `fiscal_year` an integer; `bank_account` accepted as `1930`
    or `"1930"` and normalised to the string `"1930"`.
  - Errors: missing sub-key; unknown format; non-4-digit bank account; non-integer year;
    `path` not a directory.
  - A profile without `books` still loads, since `run` doesn't need it; `validate`
    requires it.
  - Synthetic fixture `tests/fixtures/example/organisation.yaml` gets a `books` section.

  *Verify:* the new tests fail with `AttributeError`/`ProfileError` for the right reason.
  Result: `tests/test_profile_books.py`, 21 tests. All fail for the right reason:
  - 5 × `AttributeError: 'OrganisationProfile' object has no attribute 'books'`;
  - 16 × `DID NOT RAISE ProfileError`.

  Also covered, beyond the list above:
  - an unknown `books` sub-key gives a warning, not an error (forward compatibility, as
    for top-level keys);
  - `books` must be a mapping;
  - `bank_account: true` and an empty string are rejected.

  **Deviation:** the example fixture's `books` section moves to 4.1, because it must point
  at the synthetic books that 4.1 creates. These tests use temporary directories instead.
- [x] 2.2 **STOP — the owner reviews the tests from 2.1.** Result: approved 2026-09-25.
- [x] 2.3 Implement `BooksConfig` in `profile.py` and add `books` to `KNOWN_KEYS`.
  *Verify:* all tests pass; Ruff is clean.
  Result: all 50 tests pass; coverage 96.67 %; Ruff is clean. `current-state.md` updated
  (test count, capability).

Commit: `feat(profile): add books section to organisation profiles`

### Phase 3 — Domain model and balances (`accounting_agent.books`)

- [x] 3.1 **Tests first**, with objects built in code, no files:
  - `Voucher` with series `None`, two lines;
  - `Voucher` with series `"B"`, three lines;
  - a line has either debit or credit;
  - `compute_balances()` = opening balance + debit − credit, in `Decimal`, including an
    account with only an opening balance and an account used only in vouchers;
  - `Finding` ordering and rendering (`ERROR [rule] location: message`);
  - `mask_personal_numbers()` masks the same two patterns as `kontroll.py` (with and
    without a separator) and leaves dates and amounts alone.

  *Verify:* the tests fail with `ModuleNotFoundError`.
  Result: 33 tests in `test_books_model.py` (12), `test_books_balances.py` (5),
  `test_findings.py` (4) and `test_masking.py` (12). All fail at collection with
  `ModuleNotFoundError: No module named 'accounting_agent.books'`. The masking tests use only
  Skatteverket's public test number (19)121212-1212, never numbers from real books.

  Also locked by the tests:
  - negative line amounts are rejected;
  - float amounts are rejected (`TypeError`);
  - a zero line is allowed, so that the checks can report a zero amount;
  - duplicates are kept in the model, so that the checks can report them;
  - `Voucher.id` is `"B12"` with a series and `"12"` without.
- [x] 3.2 **STOP — the owner reviews the tests from 3.1.** Result: approved 2026-09-25.
- [x] 3.3 Implement `books/model.py`, `books/balances.py`, `books/findings.py` and
  `books/masking.py`. *Verify:* tests pass; type hints on all signatures (coding.md); Ruff
  clean.
  Result:
  - All 83 tests pass; coverage is 97.95 %; Ruff is clean.
  - One test failed on the first run: the error message said "a debit or a credit",
    where the reviewed test expects "debit or credit". The implementation's message was
    changed, not the test.
  - `books/__init__.py` declares the public API (`__all__`), a first step on
    `GAP-B3-BOUNDARIES`.

Commit: `feat(books): add double-entry book model, balances and findings`

### Phase 4 — Reader for the `front-matter` format

- [x] 4.1 **Synthetic fixtures:** `tests/fixtures/books/valid/`, a small, consistent set:
  - about 6 accounts;
  - an opening balance that sums to 0;
  - 5 vouchers, covering money in, money out, a transfer with no bank involved, and one
    with supporting documents and a note;
  - invented names only.

  Also one broken variant **per parse-level and format-level rule**, built from `valid/`
  by the test helpers (factory), not as copied folders:
  - BOM, invalid UTF-8, CRLF;
  - wrong header, wrong column count, empty row;
  - bad file name, missing `---`, unknown field, duplicate field, missing field, bad
    quotes;
  - file-name number or date mismatch;
  - invalid amount, invalid date;
  - bank-sign violation (all three branches).

  *Verify:* `kontroll.py`'s rule semantics from §0.3 are each represented once.
  Result: `tests/fixtures/books/valid/` has 6 accounts, 3 opening balances that sum to 0,
  and 5 vouchers:
  - 0001: money out, a bank fee;
  - 0002: money in, a membership fee;
  - 0003: rent, with a supporting document and a note;
  - 0004: a transfer with no bank involved;
  - 0005: a quoted text with a colon and escaped quotes, and two documents.

  All texts are invented, with no names. `.gitattributes` already forces LF for `*.csv`
  and `*.md`, so a Windows checkout cannot turn the valid fixture into a CRLF variant.
  Deferred from 2.1: the example fixture's `organisation.yaml` now has a `books` section
  pointing at `../books/valid`.
- [x] 4.2 **Tests first:** `read_books(config) -> tuple[Books, list[Finding]]` on `valid/`
  gives the expected objects and no findings. Each broken variant gives exactly the
  expected finding, with its severity. **No finding message contains the voucher text.**
  *Verify:* the tests fail for the right reason.
  Result: `tests/test_front_matter.py`, 42 tests, every one of them a single rule:
  - the valid books (5 tests);
  - files and CSV (10);
  - voucher files (19);
  - the bank-sign rule, all three branches, plus the bank account coming from the caller
    (4);
  - 4 tests showing that no finding message quotes the voucher text, using a text with
    the public test number and an invented name.

  All fail with `ModuleNotFoundError: No module named 'accounting_agent.formats'`.

  API locked by the tests: `read_books(path, bank_account) -> (Books | None,
  list[Finding])`. `None` means the books could not be read: a missing file or
  directory, invalid UTF-8, or a wrong header — the same cases where `kontroll.py` stops.
- [x] 4.3 **STOP — the owner reviews the fixtures and tests from 4.1–4.2.** Result: approved
  2026-09-25.
- [x] 4.4 Implement `formats/front_matter.py`:
  - the line-based front-matter parser with JSON-quoted values;
  - the CSV reader;
  - the file-name pattern;
  - the bank-sign rule, using `bank_account` from configuration;
  - mapping to two-line vouchers.

  *Verify:* tests pass; Ruff clean.
  Result:
  - All 125 tests pass on the first run; coverage is 98.31%; Ruff is clean.
  - A dead branch was removed: `InvalidOperation` can never occur after the amount
    pattern has matched, although `kontroll.py` has the same unreachable branch.
  - Two real branches have no dedicated test yet: invalid UTF-8 in a *voucher* file (the
    CSV case is tested), and a blank line inside front matter. They are left for review
    rather than covered by unreviewed tests.
  - Rule ids are English and kebab-case. Findings for voucher files are located by file
    name.
  - The first commit attempt was stopped by the detect-secrets pre-commit hook: the test
    constant `SECRET_TEXT` matched its keyword rule. It was renamed to `SENSITIVE_TEXT`
    rather than allow-listed.

Commit: `feat(formats): read front-matter books into the core model`

### Phase 5 — General checks

- [x] 5.1 **Tests first**, one test per rule on model objects, with severities as in
  `kontroll.py`:
  - opening balance: sum ≠ 0; unknown account; not a balance account; duplicate;
  - chart of accounts: account not four digits;
  - vouchers: numbering gap or duplicate, per series; unknown account; same account debited
    and credited; lines not balancing; zero amount; missing text; date outside the fiscal
    year; personal identity number in text (warning, message masked).

  The `valid/` fixture gives no findings. *Verify:* the tests fail for the right reason.
  Result: `tests/test_checks.py`, 25 tests: clean books (2, one of them reading the
  synthetic fixture), opening balance (4), chart of accounts (4), voucher numbering (5, two
  of them on series), voucher contents (8) and personal numbers (2). They fail at
  collection with `ImportError: cannot import name 'check_books'`.

  Locked semantics:
  - rule ids and locations are `opening balance [account]`, `account N` and
    `voucher <id>`;
  - numbering is checked the way `kontroll.py` does it, in file order, and each series
    separately.
- [x] 5.2 **STOP — the owner reviews the tests from 5.1.** Result: approved 2026-09-25.
- [x] 5.3 Implement `books/checks.py` as a list of small check functions
  (`check_books(books, fiscal_year) -> list[Finding]`), each within the complexity
  threshold. *Verify:* tests pass; Ruff, including C90, clean.
  Result:
  - All 150 tests pass on the first run; coverage is 98.59%; `checks.py` is 100 % covered.
  - Every check function has cyclomatic complexity ≤ 7, measured with
    `max-complexity = 7`, below the advisory 10.
  - The only function in the package at the advisory value 10 is the reader's
    `_read_front_matter` (phase 4). Review it for extraction; it is not blocking.

Commit: `feat(books): add general book checks`

### Phase 6 — `validate` command, masking and module boundary

- [ ] 6.1 **Tests first** (CLI, end to end):
  - `validate example --config-dir tests/fixtures/example` → exit 0 and "OK";
  - a broken fixture → exit 1, findings grouped by severity with counts;
  - `--balances` prints `account;balance` lines, sorted;
  - output containing a personal identity number shows `[personal number]`;
  - organisation mismatch → exit 1;
  - missing `books` section → exit 1 with a clear message;
  - `python -m accounting_agent validate …` works.

  *Verify:* the tests fail for the right reason.
- [ ] 6.2 **STOP — the owner reviews the tests from 6.1.**
- [ ] 6.3 Implement `validate` in `cli.py`. Every printed line passes through
  `mask_personal_numbers()`. *Verify:* tests pass.
- [ ] 6.4 Enforce the module boundary: a Ruff `banned-api` for `csv`, `pathlib`, `io`,
  `accounting_agent.formats` and `accounting_agent.cli`, with `per-file-ignores` for
  `formats/**`, `cli.py`, `profile.py` and `tests/**`. *Verify:* `ruff check` is clean; a temporary
  `import csv` in `books/model.py` is reported as TID251, then removed. Record the rule in
  interpretations §3.
- [ ] 6.5 Update `README.md` (validate usage, the `books` example), `AGENTS.md` (structure
  table), `docs/architecture/overview.md` and `current-state.md` (modules, test counts).
  *Verify:* the documented commands run as written.

Commit: `feat(cli): add validate command with masked output and enforce the domain boundary`

### Phase 7 — Pilot: Helsingborgs Judoklubb through the core

- [ ] 7.1 Write `HJK - Ekonomi/2026/organisation.yaml` (configuration only), in the
  owner's HJK project: `organisation: hbg-judo`, features, and `books:` with `path:
  Bokföring`, `format: front-matter`, `fiscal_year: 2026`, `bank_account: "1930"`.
  *Verify:* the owner commits it in the HJK repository; nothing is added to this
  repository.
- [ ] 7.2 Run `accounting-agent validate hbg-judo --config-dir "…/2026"` and extract only the
  result line, the counts per severity and the counts per rule. The output goes to a
  temporary file, which is deleted afterwards. *Verify:* 0 errors and 4
  personal-identity-number warnings, as in §0.4. Any difference is investigated using
  rule names and voucher numbers only.
- [ ] 7.3 Compare the balances with a throwaway script in the scratchpad (not committed). It
  imports `kontroll.ladda()` and the core's `compute_balances()`, and prints only "N of M
  accounts equal" plus the account numbers that differ. *Verify:* 33 of 33 equal, or every
  difference explained. Record the result in this plan.

Commit: `docs(mvp-002): record the Helsingborgs Judoklubb pilot result`

### Phase 8 — Aktivitet Förebygger comparison and close

- [ ] 8.1 Write the comparison as a "Book formats" section in
  `docs/architecture/overview.md`. It covers what fits the model
  (lines, series, chart, opening balance) and what a table-format reader must do (key/value
  table, line table, debit/credit opening balance, `utf-8-sig`). It is based on code only.
  *Verify:* every row of the §0.1 table is addressed.
- [ ] 8.2 Re-measure coverage and raise `fail_under` to just below the new baseline. Update
  interpretations §1. *Verify:* `pytest --cov` passes at the new floor.
- [ ] 8.3 Update the gap register: close `GAP-E4-MASKING` and `GAP-B3-BOUNDARIES`, and note
  the §9 reading rule applied in `GAP-F2-CONFIDENTIAL`. Add a changelog entry. *Verify:*
  the rows reference this plan.
- [ ] 8.4 Verify each acceptance criterion against the real system:
  - fixtures pass/fail per rule (test run);
  - pilot outcome and balances (7.2–7.3);
  - `git grep` for organisation-specific values in `src/` (organisation names, `1930`,
    `2026`, `Bokföring`), expecting none;
  - the Aktivitet Förebygger comparison exists;
  - the MVP-001 gates are still green (local CI run plus PR);
  - `git ls-files docs/reference` is empty.

  Fill in "Outcome at close".

Commit: `docs(mvp-002): compare Aktivitet Förebygger's format and close MVP-002`

## 5. Risks / open questions

- **Output leaking Confidential data (highest risk).** Voucher texts contain names and
  personal identity numbers. Mitigations:
  - finding messages never contain voucher text;
  - every printed line is masked;
  - `--balances` prints amounts and account numbers only;
  - the pilot extracts counts only and deletes raw output.

  A masking miss (an unusual number format) is possible. The pattern equals
  `kontroll.py`'s, which the organisation already relies on.
- **"Same outcome" is a comparison of counts, not of messages.** `kontroll.py` lumps many
  rules under `verifikation`, so a per-rule mapping is needed in 7.2. If the real books
  are clean (0 errors, as the baseline shows), most error rules are only proven on
  synthetic fixtures, not on the real books.
- **Front-matter parser edge cases:** JSON escapes in quoted text, and colons in unquoted
  values (`partition(":")` takes the first). The parser copies `kontroll.py`'s behaviour
  exactly rather than improving it, so the comparison stays meaningful.
- **Python 3.14 for the pilot:** the core runs from the `accounting-agent` Conda
  environment against the HJK folder. The HJK project itself is unchanged and stays on its
  own Python.
- **Deferred on purpose:** the Aktivitet Förebygger reader, BAS validation,
  revenue/cost/duplicate/date-order warnings, parking accounts and supporting documents —
  see §0.5.

### STRIDE (C1 SKA 4) — new flow: the core reads books containing personal data

| Threat | Relevance | Mitigation |
|---|---|---|
| **S**poofing | Running one organisation's command against another's data | Existing organisation-id check in the profile; `validate` reuses it |
| **T**ampering | The core could corrupt books | Read-only in this MVP; no write paths exist |
| **R**epudiation | — | Nothing is written or decided yet (audit trail is R3) |
| **I**nformation disclosure | Names and personal identity numbers reaching the terminal, logs, CI output or AI context | No voucher text in findings; all output masked; synthetic fixtures only; pilot output reduced to counts; `docs/reference/` git-ignored |
| **D**enial of service | Very large or malformed files | Local, owner-controlled input; per-file errors instead of crashes (tested) |
| **E**levation of privilege | `books.path` pointing outside the organisation folder | Local and owner-controlled; accepted. Revisit if the core ever runs on untrusted configuration |
