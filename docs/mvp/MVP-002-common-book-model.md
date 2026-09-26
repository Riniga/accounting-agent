# MVP-002 – Common book model and validation via core

Roadmap: [R2 – Helsingborgs Judoklubb pilot via core](../roadmap.md#r2--helsingborgs-judoklubb-pilot-via-core-ongoing) ·
Plan: [`MVP-002-common-book-model.plan.md`](../plans/MVP-002-common-book-model.plan.md)

> **Corrected 2026-09-25 (plan §0.1):** the first version of this MVP said Helsingborgs
> Judoklubb and Aktivitet Förebygger keep their books "in the same way". The plan's
> investigation showed that they share the concept but not the format or the voucher model.
> Aktivitet Förebygger uses Markdown-table vouchers with several posting lines and voucher
> series. The scope below was adjusted accordingly, with the owner's approval.

## Purpose

Helsingborgs Judoklubb and Aktivitet Förebygger keep their books in the same kind of way — a
chart of accounts and an opening balance as CSV, plus one Markdown file per voucher — but
in different file formats, and each has its own code to read and check them. That is exactly the duplication the project exists to
remove, and it sits at the bottom of everything else: import, matching, posting, reports
and agent tools all need a correct, shared understanding of "the books".

MVP-001's baseline analysis (see its plan, §0) showed this book model — not bank import,
which is specific to one bank and one organisation — to be the strongest overlap between
the existing projects. It is therefore the first functionality to extract.

## Goals

- The core has one model of the books — accounts, opening balances, vouchers — that is
  independent of any organisation.
- The core can tell whether an organisation's books are internally consistent, with the
  same rigour as Helsingborgs Judoklubb's current checks, and says so in a way both people
  and an agent can act on (error / warning / info, with an exit code).
- Helsingborgs Judoklubb's books are validated through the core instead of through its own
  code for these checks — the first real organisation using the core.
- We know whether Aktivitet Förebygger's books fit the same model, and what is missing if
  not.

## Context

- MVP-001 delivers the package skeleton, the `run` command, organisation profiles
  (`organisation.yaml`) and the CI gates this MVP builds on.
- Helsingborgs Judoklubb's current validation lives in `kontroll.py` in its own project;
  its book format is documented in that project's bookkeeping README. Aktivitet Förebygger
  uses the same kind of voucher files, but also has voucher series (for example customer
  invoices vs. bank).
- Books are files, not a database
  ([ADR-004](../architecture/decisions/ADR-004-csv-and-markdown-storage.md)); the core holds
  no real data, so it is tested with synthetic books
  ([ADR-003](../architecture/decisions/ADR-003-no-real-data-in-core-repo.md)).
- How organisation projects consume the core long-term is still open (R3). For this MVP the
  core is simply installed locally and run as a command against the organisation's folder.

## Scope

- A **general double-entry model**:
  - **account** (chart of accounts);
  - **opening balance**;
  - **voucher**, with an optional series, a number, a date, a text, *N posting lines*
    (account, debit, credit), supporting documents and free text.

  A Helsingborgs Judoklubb voucher is a voucher with two lines. Aktivitet Förebygger's
  multi-line, per-series vouchers fit the same model.
- **One reader**, for the `front-matter` file format that Helsingborgs Judoklubb uses: a
  chart of accounts CSV, an opening balance CSV, and a folder of Markdown voucher files
  with front matter. Where the files are, the file format, the fiscal year and the bank
  account come from the organisation's configuration, not from code.
- The checks — the format's own rules first:
  - Files are readable: UTF-8 without BOM, the expected header and column count, voucher
    file names that follow the format.
  - Required fields are present and unknown fields are flagged; amounts and dates are
    valid.
  - File names match their fields.
  - The sign of the amount is consistent with the bank account's side (a rule of the
    `front-matter` format, whose amounts are "as the bank shows them").

  Then the general checks on the model:
  - The opening balance sums to zero, uses only known balance accounts, and lists each
    account once.
  - Account numbers in the chart of accounts have four digits.
  - Voucher numbers run 1..N per series, without gaps or duplicates.
  - Every account used exists in the chart of accounts.
  - The same account is not both debited and credited; the lines balance.
  - The amount is not zero, the text is not empty, and the date is inside the fiscal year.
  - Personal identity numbers in voucher text are flagged.
- Personal identity numbers are masked in everything the core logs or reports, because
  voucher texts can contain them (methodology E4 SKA 3; gap `GAP-E4-MASKING`).
- Account balances computed from the opening balance plus the vouchers.
- A command, `accounting-agent validate` (or an extension of `run` — decided in the plan),
  that reports findings as error / warning / info and exits non-zero on error.
- Helsingborgs Judoklubb's project gets the organisation configuration it needs and is
  validated through the core.
- A written comparison against Aktivitet Förebygger's file format: what fits the model,
  and what a reader for its table format must handle.
- A short glossary of the Swedish bookkeeping terms (verifikation, kontoplan, ingående
  balans, …) and the English names used in the core.

## Out of Scope

- Bank statement import and bank ↔ voucher reconciliation — MVP-003.
- Reports (income statement, balance sheet, general ledger, …) — a later MVP.
- Creating or changing vouchers. The core only reads in this MVP; the rule that agents may
  only add vouchers, never change existing ones, becomes relevant once writing exists.
- Members, member payments, budget, comments and to-do lists — organisation-specific for
  now.
- Migrating Aktivitet Förebygger or JudoSyd onto the core.
- Agent tools, LLM calls, confidence values, approval policies.
- A reader for Aktivitet Förebygger's table format — a later MVP (roadmap).
- Replacing the whole of Helsingborgs Judoklubb's `kontroll.py` — only the checks listed
  above move. The rest stays in the organisation project until later MVPs. That includes:
  - the BAS chart validation;
  - the revenue/cost-account warnings, the duplicate warning and date order;
  - the existence of supporting documents;
  - the parking-account and unused-account summaries. Parking accounts are not configured
    until a check or report needs them.

## Acceptance Criteria

- Synthetic example books in `tests/fixtures/` pass validation. Deliberately broken
  variants — one per check — produce the expected error or warning.
- Run against Helsingborgs Judoklubb's real books (in its own project, not in this
  repository), the core reports the same outcome for the checks in scope as `kontroll.py`
  does today, and account balances match to the öre.
- No Helsingborgs Judoklubb name, account number or other organisation-specific value is
  hard-coded in the core. It all comes from configuration.
- The Aktivitet Förebygger comparison is written down, and what its reader needs is
  recorded as a follow-up.
- Everything from MVP-001's gates still holds: CI green, coverage floor held, no real data
  committed.

## Outcome at close (2026-09-26)

Closed as **delivered**, pending the pull request. Against the criteria above:

- **Synthetic books pass; one broken variant per check gives the expected finding: met.**
  - The valid books read and check with no findings.
  - Every format rule (42 reader tests) and every general check (25 check tests) has its
    own broken variant with the expected rule and severity.
  - 162 tests in total, coverage 98.76 %.
- **Helsingborgs Judoklubb's real books give the same outcome as `kontroll.py`, and
  balances match to the öre: met.**
  - Run through the core on 2026-09-26 (counts only; no data left the organisation
    project): 33 accounts, 8 opening balances, 163 vouchers, 0 errors, 4
    personal-identity-number warnings — identical to `kontroll.py`.
  - Balances are equal for **25 of 25** accounts that carry a balance. The plan's "33 of
    33" counted the chart of accounts; 8 accounts are unused.
- **No organisation-specific value hard-coded in the core: met.**
  - `git grep` over `src/` for the organisations' names, bank account, year and folder
    names is empty.
  - Three illustrative values in help, error and comment text were made neutral during
    the close.
  - The bank account, fiscal year, book path and format all come from `organisation.yaml`.
- **Aktivitet Förebygger comparison written; what its reader needs recorded: met.** It is
  in `docs/architecture/overview.md` ("Book formats"), and the reader is on the roadmap.
- **MVP-001's gates still hold: met locally; the pull request run is pending.**
  - Every CI check was run locally and is green.
  - The coverage floor was raised from 90 to 95 %.
  - `docs/reference/` is not tracked.

**What turned out differently, recorded where it happened:**
- **The MVP's premise was wrong**: Aktivitet Förebygger's books are not "the same". Caught
  in the plan's investigation, before any code. The model became general double entry
  (ADR-006) and the MVP was corrected with a dated note.
- The front matter turned out not to be YAML. The core reproduces the organisation's own
  parser instead.
- Personal data: the pilot kept to counts only. But listing Aktivitet Förebygger's voucher
  file names exposed counterparty names (`GAP-F2-CONFIDENTIAL`), and the reading rule was
  tightened.
- AI-TDD: each of the five test sets was reviewed by the owner before implementation. One
  test first passed for the wrong reason and was tightened before review.
- The detect-secrets hook stopped one commit (a test constant named `SECRET_TEXT`); it was
  renamed, not allow-listed.
- The scratchpad test environment broke overnight; the work continued in the owner's
  `accounting-agent` environment.

**Still open:**
- the owner commits `organisation.yaml` in the Helsingborgs Judoklubb repository;
- the CI run on the pull request.
