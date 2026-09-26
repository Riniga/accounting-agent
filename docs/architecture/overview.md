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

**Current state (MVP-002 in progress):** one installable package, behind the CI quality
gates from MVP-001, containing:
- an organisation-profile loader;
- a general double-entry book model (ADR-006);
- a reader for the `front-matter` book format;
- the general book checks;
- `accounting-agent run` and `accounting-agent validate`.

The Helsingborgs Judoklubb pilot ([MVP-002](../mvp/MVP-002-common-book-model.md), phase 7)
is next.

## Current Workspace Structure

```text
src/accounting_agent/   The core package (ADR-002)
    __init__.py         Package version
    __main__.py         `python -m accounting_agent`
    cli.py              `accounting-agent` command line: run, validate (argparse)
    profile.py          Organisation profile: organisation.yaml → OrganisationProfile (+ books)
    books/              The book domain — no file I/O (ADR-006; Ruff TID251)
        model.py        Account, OpeningBalance, PostingLine, Voucher, Books
        balances.py     compute_balances()
        checks.py       check_books() — the general checks
        findings.py     Finding, Severity
        masking.py      Personal identity number masking
    formats/            One reader per book file format (ADR-006)
        front_matter.py read_books() for the `front-matter` format
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
- **`cli.py`** provides two commands. Both load the profile, and both refuse if
  `<organisation>` doesn't match it.
  - `run <organisation> --config-dir <path>` logs the enabled features.
  - `validate <organisation> --config-dir <path> [--balances]` prints a masked report to
    stdout and exits 1 on errors.

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

`pytest -q` from the repository root. The coverage floor is 90 % (`pyproject.toml`);
coverage is currently 98.76%. The floor is re-measured and raised at the close of MVP-002.

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

The core reads each organisation's books through a reader for its file format, into one
general model (ADR-006). The comparison below is based on the two projects' code and CSV
header rows only (MVP-002 plan §0.1 and TODO 8.1), never on their books.

| | `front-matter` (Helsingborgs Judoklubb) — **reader exists** | Table format (Aktivitet Förebygger) — **no reader yet** |
|---|---|---|
| Chart of accounts | `kontoplan.csv`: `kontoklass;kontogrupp;konto;bas_beskrivning;lokal_benämning` | `kontoplan.csv`: `nummer;beskrivning;typ;användning` |
| Opening balance | `ingående-balans.csv`: `konto;lokal_benämning;ingående_balans` — one signed column | `ingående-balans.csv`: `nummer;beskrivning;debet;kredit` — amount = debit − credit |
| Encoding | UTF-8 **without** BOM (a BOM is an error), LF | UTF-8 **with** BOM, read tolerantly |
| Voucher folder | `verifikationer/` | `Verifikationer/` |
| Voucher file name | `NNNN_YYYY-MM-DD.md`, checked against the fields | `<series><number> <date> <description>.md` — free text, not checked |
| Voucher fields | Front matter `key: value` between `---` lines; quoted values are JSON strings | Markdown key/value table rows `\| **Key** \| value \|` (Verifikation, Datum, Text, …) |
| Posting lines | Implicit: one `debet`/`kredit` pair and one `belopp` | Explicit table rows `\| account \| name \| debit \| credit \|`, **several per voucher** |
| Numbering | 1..N across the year | **Per series** (letters in the voucher id, e.g. B, K), 1..N in each |
| Amounts | `-?\d+(\.\d{1,2})?` — decimal point only | Tolerant: spaces, non-breaking spaces, `−`, comma decimal, `*` marks |
| Format rule | Amount signed as the bank shows it (the bank-sign rule) | None — debit and credit columns carry the sign |

**What already fits the model:**
- voucher series and N posting lines;
- the per-series numbering check;
- the balanced-voucher check (which the `front-matter` format can never fail);
- the unknown-account, zero-amount, text and fiscal-year checks;
- balances.

**What an Aktivitet Förebygger reader must do** (roadmap: "Aktivitet Förebygger reader"):
- parse the key/value table and the posting-line table;
- derive the series and number from the voucher id;
- read the four-column chart of accounts and the debit/credit opening balance;
- decide how strict to be about BOMs and the tolerant amount format — likely accept what
  the organisation writes today, and report it as a warning rather than an error;
- ignore free-text file names.

Its own tool also checks that debits equal credits and that numbering is contiguous per
series, and the core's general checks already cover both.

**Open for that MVP:**
- what the chart's `typ` and `användning` columns mean for the model;
- whether Aktivitet Förebygger's balance sheet uses BAS classes 1–2 the same way.

## Planned Evolution of the Workspace

*Everything in this section is planned, not existing.*

- **MVP-002 (remaining):** the Helsingborgs Judoklubb pilot, and a written comparison
  with Aktivitet Förebygger's table format (a "Book formats" section here).
- **Aktivitet Förebygger reader:** a second reader for the table format (multi-line
  vouchers, series) into the same model.
- **Later module areas** (from the initial idea, added only as extraction justifies them):
  bank import and reconciliation (MVP-003), reports (MVP-004), agent tools, confidence
  and approval policies, and the audit trail (R3), integrations (R4), payroll (R5).
- **Consumption by organisation projects (undecided, R3):** Claude Code acts as the agent
  in each organisation project, locally and on a schedule. JudoSyd already does this with
  `claude -p` and its own MCP servers. Whether the core is reached as an installed
  package, through scripts or through an MCP server is decided in R3.

## Open Questions and Areas Not Yet Implemented

- How organisation projects consume the core (package / scripts / MCP) — Unknown – to be
  decided (R3).
- The data model's file schemas beyond the book model — MVP-002 onward.
- Confidence thresholds and approval levels per operation — Unknown – to be decided (R3).
- Local scheduler mechanism — Unknown – to be decided.
- Relation to the Swedish Bookkeeping Act (archiving, verification) — backlog.
- Methodology gaps and exceptions — see
  [`docs/methodology-compliance/`](../methodology-compliance/README.md), notably EX-001
  (no second reviewer).
