# Architecture Overview

<!--
Keep this file current: update it in the same PR as any change to workspace structure,
major components, dependencies, or the build/deploy process (see
docs/standards/documentation.md).
-->

## Project Overview

Accounting Agent is the shared core for AI-assisted bookkeeping in several small non-profit
organisations (JudoSyd, Helsingborgs Judoklubb, Aktivitet Förebygger). Each organisation
keeps its own private project with data, chart of accounts, rules and configuration. This
public repository holds the general functionality they share. See
[`docs/vision.md`](../vision.md) and the [initial idea](../initial-idea.md).
Swedish bookkeeping terms and their English names in the code are in the
[glossary](glossary.md).

**Current state (MVP-005 merged; MVP-006 implemented, pending its pull request):** one
installable
package, behind the CI quality gates from MVP-001, containing:
- an organisation-profile loader;
- a general double-entry book model (ADR-006), with supplementary-file models (ADR-007);
- readers for the `front-matter` book format, the `nordea-csv`,
  `sparbanken-syd-csv` and `swedbank-csv` bank exports, the bank
  statement, the BAS reference chart and the supplementary files;
- the general checks, the detail checks, the reference-chart check and reconciliation
  against the bank;
- Swedish Markdown reports;
- `accounting-agent run`, `validate`, `import-bank`, `report` and `new-voucher`. The
  core writes derived files (`import-bank`, `report` — ADR-008) and new vouchers
  (`new-voucher` — ADR-009); it never changes a voucher.

Helsingborgs Judoklubb runs its bookkeeping tooling through it, except member
management: verified on its 2026 books in the
[MVP-003](../mvp/MVP-003-bank-reconciliation-and-reports.md) pilot.

## Current Workspace Structure

```text
src/accounting_agent/   The core package (ADR-002)
    __init__.py         Package version
    __main__.py         `python -m accounting_agent`
    cli.py              `accounting-agent` command line: run, validate (argparse)
    profile.py          Organisation profile: organisation.yaml → OrganisationProfile (+ books)
    books/              The book domain — no file I/O (ADR-006; Ruff TID251)
        model.py        Account, OpeningBalance, PostingLine, Voucher, Books, BankTransaction,
                        ReferenceChart
        balances.py     compute_balances()
        checks.py       check_books() — the general checks
        details.py      check_details() — the detail checks from kontroll.py, and the document checks
        posting.py      build_voucher() — a new voucher from a bank transaction, or a refusal (ADR-009)
        reference.py    check_reference() — the chart against a reference chart (BAS)
        supplements.py  FundValue, BudgetItem, ClosingComment, TodoItem and their checks
        reconciliation.py  reconcile() — the books against the bank statement
        findings.py     Finding, Severity
        masking.py      Personal identity number masking
    formats/            The book format's reader and writer, and one reader per external format (ADR-007, ADR-010); the only writers (ADR-008, ADR-009)
        common.py       Shared CSV rules (encoding, header, columns, amounts)
        front_matter.py read_books() for the `front-matter` format; render_voucher(), write_voucher()
        reference_chart.py  read_reference_chart() — the four-file BAS reference
        supplements.py  read_budget(), read_comments(), read_todo()
        bank_export.py  What every bank export reader gives: statement rows, fund values; shared decoding
        nordea_csv.py   read_export() for the `nordea-csv` bank export
        sparbanken_syd_csv.py  read_export() for the `sparbanken-syd-csv` bank export
        swedbank_csv.py  read_export() for the `swedbank-csv` bank export
        bank_statement.py  read_statement(), read_fund_values(), read_voucher_texts(); write_statement(), write_fund_values() — atomic writes
    reports/            Swedish Markdown reports, rendered from the model — no file I/O (ADR-008)
        format.py       ReportContext, amounts, tables (masked cells), the report header
        ledger.py       The books worked out per account for the reports
        accounts.py     Income statement, balance sheet, general ledger, voucher list, monthly overview
        overview.py     Budget follow-up, closing comments, to-do report, summary; render_reports()
tests/                  pytest suite; fixtures/ holds synthetic organisations only (ADR-003)
docs/                   Vision, roadmap, architecture + ADRs, MVPs, plans, standards,
                        development setup, methodology + compliance, Claude prompts
docs/reference/         Local, git-ignored copies of the private organisation projects
scripts/                scan_instruction_files.py (hidden-Unicode scan, used by CI)
.github/                CI workflow, Dependabot, PR template, Copilot pointer
.claude/                Claude Code permission settings
pyproject.toml          Package metadata + Ruff/coverage configuration
environment.yml         Conda: Python 3.14 + the pip lock
requirements.in / requirements-lock.txt   Pip sources / hash-pinned lock
LICENSE                 PolyForm Noncommercial 1.0.0 (ADR-005)
```

## Major Components

### `accounting_agent` (package)

- **`profile.py`** reads and validates `organisation.yaml` from an organisation's
  configuration directory:
  - `organisation` must be a lowercase slug;
  - `features` must map names to real booleans;
  - unknown top-level keys produce a warning, not an error;
  - the file is read with `yaml.safe_load`.

  An optional `books` section gives the books' path, file format, fiscal year and bank
  account. The profile is returned as an immutable `OrganisationProfile`, or loading
  raises `ProfileError`. This is the only place organisation-specific settings enter the
  core.
- **`books/`** is the domain. It is pure and does no file I/O; this is enforced by Ruff
  `TID251`.
  - The model is general double entry: a `Voucher` has an optional series and N
    `PostingLine`s, and amounts are always `Decimal` (ADR-006).
  - `check_books(books, fiscal_year)` returns `Finding`s: `ERROR`, `WARNING` or `INFO`,
    with a rule id and a location.
  - No finding quotes a voucher's text, and personal identity numbers are masked in all
    output.
- **`formats/front_matter.py`** reads the `front-matter` format — chart-of-accounts CSV,
  opening-balance CSV and one Markdown voucher file per voucher — with the same field
  semantics as the organisation's own tool. It reports parse- and format-level findings,
  including the bank-sign rule.
- **`books/details.py`** has the detail checks that MVP-002 deferred (duplicates, date
  order, account sides, supporting documents, parking and unused accounts, the chart's
  own rules). `validate` runs them when the profile has a `checks` section; the CLI
  lists the documents folder, so the domain stays free of I/O.
- **`books/reference.py`** checks the chart against a reference chart (BAS) as
  `kontroll.py` does, using the chart's own group and BAS description, which the
  `front-matter` reader now keeps on `Account` (ADR-007). A format without those
  columns leaves them `None`, and the text comparisons are skipped.
- **`books/supplements.py`** models the supplementary files (fund value, budget,
  closing comments, to-do list) and checks them as `kontroll.py` does. Their formats,
  including the allowed values, are the core's own (ADR-007).
- **`books/reconciliation.py`** reconciles the books against the bank statement as
  `kontroll.py` does: the bank's balance arithmetic, the opening balance, and matching on
  (date, amount), where a voucher's amount is the net of its bank lines. A
  `BankTransaction` holds no name or message (ADR-007), so no finding can quote one.
- **`formats/nordea_csv.py`** reads a `nordea-csv` bank export — a statement or fund
  values, told apart by the header — into rows that are normalised, masked with
  `[personnummer]` and oldest first. **`formats/bank_statement.py`** writes the
  organisation's statement and fund-value files. These are the core's write paths for
  derived files (ADR-008): configured paths only, through a temporary file that replaces
  the target.
- **Creating a voucher (ADR-009)** is split over three layers.
  - `books/posting.py` builds the voucher from the caller's decisions and the bank
    transaction, or refuses with a rule. It does no I/O.
  - `formats/bank_statement.py` composes the voucher's text from a statement row, since
    the domain's bank transaction holds no name or message. `formats/front_matter.py`
    renders the file — the fields, then the generated lines with account names and
    document links — and writes it with exclusive creation, so an existing voucher is
    never replaced. The reader keeps the generated lines out of the note and checks them
    against the fields.
  - The CLI checks the books before, checks them again with the new voucher added, and
    writes only if no error was added.
- **`cli.py`** provides five commands. All load the profile, and all refuse if
  `<organisation>` doesn't match it.
  - `run <organisation> --config-dir <path>` logs the enabled features.
  - `validate <organisation> --config-dir <path> [--balances] [--unbooked]` prints a
    masked report to stdout and exits 1 on errors. With a `bank` section it also
    reconciles against the statement file.
  - `import-bank <organisation> --config-dir <path> <export>` writes the statement or
    fund-value file and prints only file names, dates and counts.
  - `report <organisation> --config-dir <path> [--force]` runs the checks, then writes
    the reports to the configured folder; it refuses on errors unless forced.
  - `new-voucher <organisation> --config-dir <path> --date … ` creates one voucher and
    prints its number, date, amount and lines. With `--amount` it is for a bank
    transaction, against `--account` or against lines (`--debit`, `--credit`); without
    `--amount` it has no bank transaction, and `--text` and every line are the caller's
    (MVP-005).
- **`reports/`** renders the reports as Swedish Markdown strings, with the texts and
  figures of Helsingborgs Judoklubb's `generera_redovisning.py`. It does no I/O — the
  `TID251` ban covers it — and the CLI writes the files atomically. Table cells are
  masked as `[personnummer]`; the header is not, since an organisation number has the
  same shape as a personal number.

The first consumer is Helsingborgs Judoklubb's 2026 books, in the MVP-002 pilot.

## Existing Dependencies

### Runtime

- **PyYAML** — parses `organisation.yaml`. The standard library has no YAML parser.

### Development Environment

- **Conda** (conda-forge only) provides **Python 3.14**.
- **pip**, from `requirements-lock.txt` (hash-pinned, compiled with pip-tools), provides
  Ruff, pre-commit, pytest and pytest-cov (plus colorama, pinned for cross-platform lock
  stability).

### Build

- **setuptools** is the build backend. The version comes from
  `accounting_agent.__version__`. There is no published release.

### AI Assistants

- **Claude Code** is the primary assistant; GitHub Copilot is optional. Both follow
  [`AGENTS.md`](../../AGENTS.md).
- `.claude/settings.json` requires in-the-moment approval for commit, push, delete and
  `gh pr merge`.

## Build and Development Process

### Environment Setup

See [`docs/development/setup.md`](../development/setup.md). The commands were verified from
a fresh clone in MVP-001.

### Running Tests

`pytest -q` from the repository root. The coverage floor is 97 % (`pyproject.toml`,
raised at the close of MVP-003); coverage is currently 98.82 %.

### Development Workflow

`Roadmap → MVP → Plan → Implementation → Test → Pull Request` — see
[`docs/development/methodology.md`](../development/methodology.md) and
[`AGENTS.md`](../../AGENTS.md).

### Git Workflow

One feature branch per MVP off `main`, merged through a pull request (see
[`docs/standards/git.md`](../standards/git.md) and interpretations §8).

`main` is protected by the ruleset "Protect main":
- no direct pushes or force pushes, and no deletion — for anyone;
- a pull request is required, with 6 required checks;
- 0 required approvals — single-maintainer exception EX-001.

### CI/CD

`.github/workflows/ci.yml` runs on pull requests to `main` and on pushes to `main`. `Ruff`
runs first; the other checks run after it:
- `Ruff` — format and lint;
- `Dependencies` — lock drift, `pip-audit`, licence allowlist;
- `SAST` — Semgrep;
- `Secret scan` — detect-secrets;
- `Instruction file scan` — hidden Unicode;
- `Run tests` — pytest with the coverage gate, in the Conda environment.

Every gate was shown to fail on deliberately broken code. The same Ruff and detect-secrets
checks run locally as pre-commit hooks. There is no CD.

### Deployment

None. The core is installed locally and run on the owner's machine; the organisation
projects will run it on a local schedule.

## Architectural Observations

- **Two-layer split:** a public, organisation-agnostic core (this repository) and private
  organisation projects that hold data and configuration (ADR-002, ADR-003). The profile's
  organisation check is the first guard against running one organisation's command against
  another's data.
- **AI decides, code executes:** the LLM does understanding and judgement; deterministic
  Python does bookkeeping operations, validation and integrations, exposed to the agent as
  defined tools (R3).
- **Files, not a database:** books as CSV and Markdown, configuration as YAML (ADR-004).
- **Extract, don't design ahead:** functionality moves into the core only once a working
  function exists in an organisation project to generalise. MVP-001's baseline analysis
  found the book model (chart of accounts, opening balance, one Markdown file per voucher)
  to be the strongest overlap, so it is extracted first (MVP-002).

## Book formats

**The core has one book format** ([ADR-010](decisions/ADR-010-one-book-format.md)). An
organisation that uses the core keeps its books in it; the core has no reader or writer
for another layout, and does not convert books.

The format, called `front-matter` in `organisation.yaml`:

| File | Content |
|---|---|
| `kontoplan.csv` | The chart of accounts: `kontoklass;kontogrupp;konto;bas_beskrivning;lokal_benämning` |
| `ingående-balans.csv` | The opening balance: `konto;lokal_benämning;ingående_balans`, one signed column |
| `verifikationer/NNNN_YYYY-MM-DD.md` | One file per voucher: the fields between two `---` lines, then the generated lines (ADR-009) and the note |
| the supplementary files | Bank statement, fund value, budget, closing comments and to-do list (ADR-007) |

All of them are UTF-8 without BOM, with LF line endings; the CSV files are separated by
semicolons. Vouchers are numbered 1..N across the year, without series.

**When the format lacks something an organisation needs, the format is extended** for
everyone, in a way that keeps existing books valid. A voucher has one debit and one
credit account in the *simple form*; MVP-005 added the *lines form*, where `debet` and
`kredit` each list their posting lines as `<account> <amount>`, separated by semicolons
like the documents in `underlag`. The simple form is still what one debit and one credit
line is written in, so no existing voucher changed.

**The fields of a voucher file are valid YAML**, with every field once: Markdown tools
read the top of the file as YAML and fail on a repeated key.

**Formats that belong to someone else are not book formats.** The core reads one export
format per bank (`bank.export_format`), and the BAS reference chart as it is published.

**An organisation adopts the format** by building its books in it: the chart of accounts
and the opening balance as the two CSV files, the bank statement through `import-bank`,
and the vouchers through `new-voucher`, from the bank statement and the supporting
documents.

The comparison with Aktivitet Förebygger's earlier table format, and what a second
reader would have had to do, are history: see the MVP-002 plan (§0.1 and TODO 8.1).

## Planned Evolution of the Workspace

*Everything in this section is planned, not existing.*

- **Member management via core (backlog, high priority):** the member register, member
  payments and the member-fee report, with their own STRIDE pass.
- **Reconciling a second statement**, such as the tax account against its account in
  the books (backlog).
- **Later module areas** (from the initial idea, added only as extraction justifies them):
  member management (backlog), agent tools, confidence
  and approval policies, and the audit trail (R3), integrations (R4), payroll (R5).
- **Consumption by organisation projects (undecided, R3):** Claude Code acts as the agent
  in each organisation project, locally and on a schedule. JudoSyd already does this with
  `claude -p` and its own MCP servers. Whether the core is reached as an installed
  package, through scripts or through an MCP server is decided in R3.

## Open Questions and Areas Not Yet Implemented

- How organisation projects consume the core (package / scripts / MCP) — Unknown – to be
  decided (R3).
- The data model's file schemas beyond the book model — MVP-003 adds the supplementary
  files (ADR-007).
- Confidence thresholds and approval levels per operation — Unknown – to be decided (R3).
- Local scheduler mechanism — Unknown – to be decided.
- Relation to the Swedish Bookkeeping Act (archiving, verification) — backlog.
- Methodology gaps and exceptions — see
  [`docs/methodology-compliance/`](../methodology-compliance/README.md), notably EX-001
  (no second reviewer).
