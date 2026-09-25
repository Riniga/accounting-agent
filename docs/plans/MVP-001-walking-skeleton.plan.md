# Plan: MVP-001 – Walking skeleton & baseline analysis

Reference: [`docs/mvp/MVP-001-walking-skeleton.md`](../mvp/MVP-001-walking-skeleton.md)

**Status:** In progress — phase 1 (investigation) done, phase 2 next.

## 0. Investigation

Nothing below is decided until it has been checked for real. Record each finding here
(dated), including anything that overturns an assumption in the MVP or ADR-002.

**Toolchain and versions** — the aim is the newest version the whole chain supports:

- **Python version:** check that 3.14 is available on conda-forge and supported by Ruff's
  `target-version`, Semgrep, detect-secrets, pip-tools and `actions/setup-python`. Fall back
  to 3.13 if any gate does not support it. Record the result.
- **Tool versions:** look up the current releases of Ruff, pre-commit, the
  `pre-commit-hooks` / `detect-secrets` hook revisions and the GitHub Actions the workflow
  uses (`actions/checkout`, `actions/setup-python`, `actions/cache`,
  `conda-incubator/setup-miniconda`). Do not copy the template's pinned numbers without
  checking them.
- **Conda + pip-tools vs. `uv`:** ADR-002 keeps Conda + pip-tools. Try both briefly on this
  package: time to create the environment locally and in CI, and lock-file drift between
  Windows and Linux. Stay with Conda unless the difference is clear; if switching, write a
  superseding ADR.

**Gates available for a public GitHub repository:**

- Check whether GitHub's native **secret scanning** and **push protection** are available
  and enabled for this repository. Keep detect-secrets in any case, because it also runs as
  a pre-commit hook.
- Check **Dependabot alerts** / automated security fixes, and whether a CI
  vulnerability check (for example `pip-audit`) adds anything on top of them.
- Compare **Semgrep** (template) and **CodeQL** for SAST on this codebase: run both once,
  and compare signal against noise and run time. Choose one, or both, and record it in
  `interpretations.md`.

**Coverage floor:** do not set it in advance. Measure coverage once the skeleton and its
tests exist, and set the floor just below the measured value (see the example in the
testing standard).

**Baseline analysis of the existing projects** (`docs/reference/`, git-ignored). Read only
code, AI instructions (`CLAUDE.md` and similar), configuration, chart of accounts and rules.
Do **not** read bank files, books, receipts, payroll, personnel or member data (ADR-003). For
Helsingborgs Judoklubb (`HJK - Ekonomi`), answer the initial idea's questions:

1. Which scripts exist today?
2. Which data models are used (CSV columns, file layout)?
3. Which parts are specific to Helsingborgs Judoklubb?
4. Which parts are general?
5. Which rules live implicitly in prompts or Python?
6. Which functions should become agent tools?
7. Which operations require human approval?

Do a lighter pass over `Judosyd - Kassör` and `AF - Ekonomi`, focused on overlap with
Helsingborgs Judoklubb and on what they add (PDF, Gmail, Discord, the accounting system,
payroll).

Record the findings as a table or short bullets under this section, not as a copy of code
or data.

### Findings (2026-09-25)

#### Toolchain and versions

| Item | Found | Decision |
|---|---|---|
| Python | 3.14.7 is the latest stable version (3.15 is at rc2). It is on conda-forge for both `win-64` and `linux-64`. Ruff, pip-tools, Semgrep, pytest, pytest-cov, PyYAML, pip-licenses and pip-audit all declare 3.14 support. pre-commit and detect-secrets do not declare it, but are pure Python. | **Python 3.14.** Phase 3 verifies that pre-commit and detect-secrets actually run on it; fall back to 3.13 if they don't. |
| Ruff | 0.16.9 (the template pinned 0.16.6) | Pin `ruff==0.16.9` and pre-commit `rev: v0.16.9` |
| pre-commit / hooks | pre-commit 4.6.2; `pre-commit-hooks` v6.0.0; `detect-secrets` v1.5.0 | Update the ranges and revisions |
| pip-tools | 7.6.1 | Unpinned in CI, as in the template |
| pytest / pytest-cov / PyYAML | 9.1.1 / 7.1.0 / 6.0.3 | `pytest-cov` is added (coverage gate). PyYAML is the only runtime dependency — the YAML parser for `organisation.yaml`. The standard library has none |
| GitHub Actions | `actions/checkout` v7.0.1, `actions/setup-python` v7.0.0, `actions/cache` v6.1.0, `conda-incubator/setup-miniconda` v4.1.0, `github/codeql-action` v4.38.2 | Update the tags that are behind (`setup-miniconda`) |
| Conda | Conda 26.5.3 is installed locally (`~/anaconda3`), but not on the Git Bash PATH | Keep Conda (ADR-002). |
| `uv` | Not installed | **Not trialled** — deviation from this section's plan. For one small, pure-Python package the expected benefit (faster environment setup) doesn't justify introducing and comparing a second toolchain now. Revisit if the CI environment step becomes a real bottleneck — measure its duration in phase 4. |

#### GitHub security features (public repository)

| Setting | State 2026-09-25 | Action |
|---|---|---|
| Secret scanning | enabled | Keep. Complements detect-secrets, which also runs as a pre-commit hook |
| Push protection | enabled | Keep |
| Dependabot alerts | **disabled** | Enable (4.3) |
| Dependabot security updates | **disabled** | Enable (4.3) |
| Private vulnerability reporting | **disabled** | Enable (4.3). `SECURITY.md` depends on it |
| Branch protection / rulesets on `main` | **none** | Apply (4.3) |

- **Vulnerability check in CI:** Dependabot alerts only watch the default branch after
  merge. `pip-audit` against `requirements-lock.txt` checks the pull request *before*
  merge. **Add `pip-audit` to the Dependencies job.**
- **SAST:** CodeQL is free for public repositories. Semgrep does not run natively on
  Windows, which doesn't matter because it only runs in CI. **Run both on the first pull
  request in phase 4**, then keep the one with the better signal-to-noise ratio and run
  time, and record the choice in `interpretations.md`.

#### Baseline analysis — Helsingborgs Judoklubb (`HJK - Ekonomi`)

Read: `2026/agent/*.py` (structure, plus the importer in full), `2026/agent/README.md`,
`2026/Bokföring/README.md`. Not read: books, bank files, receipts, personnel and member
data.

> **Finding — personal data in the rules file.** `2026/Bokföring/README.md` combines the
> rules with a running log, "Rättelser och beslut" (corrections and decisions), that names
> members, parents and children next to amounts. Reading the rules therefore exposed real
> personal data to the AI tool. Nothing from it has been copied here. **Recommendation for
> the HJK project:** move the decision log out of `README.md` into its own file. The
> extraction work can then read the rules without reading personal data.

1. **Which scripts exist today?** Four standard-library-only Python scripts (about 2,200
   lines) in `2026/agent/`:
   - `importera_kontoutdrag.py` — bank CSV import with personal-identity-number masking.
   - `kontroll.py` — read-only validation, with FEL (error), VARNING (warning) and INFO
     levels and an exit code.
   - `generera_redovisning.py` — ten Markdown reports. It refuses to run when the checks fail.
   - `medlemskontroll.py` — member registers compared against attendance and payments.

   A step-by-step routine for people and agents is in `Bokföring/SOP.md`.
2. **Which data models are used?** Semicolon-separated UTF-8 CSV files with a decimal
   point and ISO dates: chart of accounts (a BAS subset), opening balance, budget, members,
   member payments, to-do list, comments and bank statement. **One Markdown file per
   voucher**, with YAML-like front matter (`verifikation`, `datum`, `text`, `belopp`,
   `debet`, `kredit`, `underlag`) and free text below. The whole BAS chart of accounts is
   kept as reference in `kontobas/`.
3. **Which parts are specific to Helsingborgs Judoklubb?**
   - The organisation name and number, which are hard-coded.
   - The Nordea export format.
   - The member categories and fees.
   - The Swedish sports-club registers (Svenska Lag, IdrottOnline) and attendance.
   - The posting rules table (which counterparty maps to which account).
   - The park accounts 3008/6990 as numbers.
   - The hard-coded paths relative to the script.
4. **Which parts are general?**
   - The voucher model (one file per voucher, sequence without gaps, never deleted,
     corrected by a reversing voucher).
   - Chart of accounts and opening-balance validation.
   - Double-entry checks.
   - Bank-statement ↔ voucher reconciliation.
   - Sign conventions.
   - The FEL/VARNING/INFO check framework.
   - Personal-identity-number masking.
   - Balances.
   - Reports: income statement, balance sheet, general ledger, voucher list, monthly
     overview, budget follow-up.
   - The "don't guess — park and flag" principle.
5. **Which rules live implicitly in prompts or Python?**
   - The posting rules are documented in the README, but applied by the agent following
     prose rather than by code.
   - Age and fee rules are constants in `medlemskontroll.py`.
   - Report sign conventions (income statement: credit − debit; balance sheet: debit −
     credit) are in code comments and the README.
   - The "confidence" of a member link (`säker`/`trolig`/`gissad`) is an early form of the
     idea's confidence value.
6. **Which functions should become agent tools?**
   - `kontroll` → `validate_books()`.
   - The obokförda (unbooked transactions) list → `get_unprocessed_transactions()`.
   - Voucher creation with the next number → `post_transaction()`.
   - Report generation → `generate_report()`.
   - Bank import → an importer.
   - The planned "agent proposes new vouchers from new statements and receipts" →
     `suggest_posting()`.
7. **Which operations require human approval?** Per the README:
   - Changing an existing voucher requires an explicit decision by the treasurer (kassör).
   - Scripts and agents may only create new vouchers.
   - Uncertain postings are parked and flagged to the treasurer.
   - Decisions are logged.

#### Lighter pass — JudoSyd and Aktivitet Förebygger

- **JudoSyd (`Kassörsassitenten`):**
  - Already runs **Claude Code headless (`claude -p`) from a scheduled PowerShell script**
    (`scripts/kassor-run.ps1`), with an allowed-tools list and a log directory.
  - Two home-built **MCP servers**:
    - Gmail/Calendar: search, fetch, download attachment, archive, plus calendar events.
    - Discord: DM and channel message.
  - Design docs in `docs/` (assignment, technology, plans).
  - No bookkeeping scripts; the books are mostly PDF/Excel.
  - This is a working example of the pattern R3 has to decide on: Claude Code as the agent
    in the organisation project, with tools as MCP servers.
- **Aktivitet Förebygger:**
  - One script, `Bokföring/bygg-redovisning.py` (about 620 lines), that builds reports from
    **Markdown voucher files** (with voucher series: customer invoices, bank, …) plus CSV
    chart of accounts, opening balance and budget.
  - Also covers accounts receivable and taxes/fees (payroll-related).
  - Hard-codes the organisation name and number.

#### Conclusions for MVP-002 and the core

- **The strongest overlap is not bank import but the book model.** Both Helsingborgs
  Judoklubb and Aktivitet Förebygger have the same model: chart of accounts CSV, opening
  balance CSV, and one Markdown file per voucher. Both also generate largely the same
  reports (income statement, balance sheet, general ledger, voucher list, monthly
  overview, budget) with separate, duplicated code. The bank import is Nordea-specific and
  used only by Helsingborgs Judoklubb.
- **Decided 2026-09-25 (owner):** MVP-002 is changed from "bank statement import and
  matching" to **"common book model and validation via core"**. It reads the chart of
  accounts, opening balance and voucher files into core models, and runs the general
  checks from `kontroll.py`. It is proven on Helsingborgs Judoklubb and checked against
  Aktivitet Förebygger's format. Written early, straight after the investigation:
  [`MVP-002-common-book-model.md`](../mvp/MVP-002-common-book-model.md). Bank import and
  reconciliation follow as MVP-003, and reports as MVP-004 (roadmap headings only).
- Existing code is in Swedish (identifiers and messages). The core follows
  `docs/standards/coding.md` (English code). Domain terms (verifikation, kontoplan) need a
  small glossary when extracting.
- The organisation projects hard-code paths relative to the script. The core's
  `--config-dir` approach replaces this.

## 1. Goal

When this plan is done:

- `pip install -e .` gives a working `accounting-agent` command that loads and validates an
  organisation profile, with tests.
- CI on pull requests runs lint/format, tests with coverage, secret scan, dependency scan,
  SAST and the instruction-file scan, all green, and `main` is protected.
- The methodology baseline is written.
- The analysis above is recorded, and MVP-002 is written from it.

## 2. Scope boundary

- **In:** `src/accounting_agent/` (CLI and profile loading only), `tests/`,
  `tests/fixtures/`, `pyproject.toml`, `pytest.ini`, `environment.yml`, `requirements.in`,
  `requirements-lock.txt`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`,
  `.secrets.baseline`, `LICENSE`, `docs/development/*` (commands and environment name),
  `docs/methodology-compliance/*`, `docs/development/repo-settings.md` (record what was
  applied), `docs/architecture/overview.md` + `current-state.md`, `README.md` quick start,
  and `docs/mvp/MVP-002-*.md`.
- **Out:** any accounting logic, a data model beyond the profile, LLM calls, changes to the
  organisation projects, CD, a scheduler, publishing to PyPI.

## 3. Chapters addressed

- A1 / A2 – developer environment and AI tools (setup docs, Claude Code as the approved tool)
- B2 – Kodstandard & stil (Ruff, EditorConfig)
- B5 – Dokumentation av kod (README with install/run/test and an owner line)
- C1 – Secure coding (SAST gate)
- C2 – Beroendehantering (lock file, licence scan, Dependabot)
- C4 – Hantering av hemligheter (detect-secrets, push protection)
- D1 – Testning (tests, coverage floor)
- D2 – Kodgranskning (branch protection; the single-maintainer exception)
- E1 / E2 – branch strategy and CI
- F1–F3 – AI action rules, data restrictions (ADR-003), instruction-file scan
- The full A–F assessment and gap register

## 4. TODOs

### Phase 1 — Investigation

- [x] 1.1 Toolchain: Python version, tool and action versions, Conda vs. `uv`. Record in §0.
      Result: Python 3.14, versions updated. `uv` was not trialled (see §0).
- [x] 1.2 GitHub-native security features for the repository, and Semgrep vs. CodeQL.
      Record in §0. Result: secret scanning and push protection are already on; the other
      settings go to 4.3. `pip-audit` is added. The SAST choice is deferred to phase 4, after
      running both tools.
- [x] 1.3 Baseline analysis of `HJK - Ekonomi` (the seven questions) plus the lighter pass
      over JudoSyd and Aktivitet Förebygger. Record in §0. Result: done. Personal data was
      found in the HJK rules file (not copied). Proposal: MVP-002 becomes "common book
      model and validation".

Commit: `docs(mvp-001): record investigation findings for toolchain and baseline analysis`

### Phase 2 — Package skeleton (test first)

- [ ] 2.1 Write the tests first and have them reviewed: valid profile → features logged,
      exit 0; missing file, invalid YAML, missing `organisation`, non-boolean feature →
      clear error, non-zero exit. Synthetic fixture `tests/fixtures/example/organisation.yaml`.
- [ ] 2.2 Implement `src/accounting_agent/` (profile loading + `run` CLI) until the tests
      pass. Add `[project]` and `[build-system]` to `pyproject.toml` with the console script
      entry.
- [ ] 2.3 Adapt `pytest.ini` (`testpaths = tests`) and the Ruff/coverage sections of
      `pyproject.toml` (`src`, `known-first-party`, coverage source) — no placeholders left.

Commit: `feat(core): add accounting-agent package skeleton with run command and profile validation`

### Phase 3 — Environment and dependencies

- [ ] 3.1 Set the environment name (`accounting-agent`) and the Python version from §0 in
      `environment.yml`. Add the YAML parser to `requirements.in` (justify it in the PR),
      update tool pins, and generate `requirements-lock.txt`.
- [ ] 3.2 Update `.pre-commit-config.yaml` revisions and regenerate `.secrets.baseline`
      with forward-slash paths.
- [ ] 3.3 Update `docs/development/setup.md`, `environment.md` and `tools.md` and the
      `AGENTS.md` "Local commands" block to the real commands. Verify them in a fresh clone.

Commit: `build: pin Python toolchain, lock dependencies and document local setup`

### Phase 4 — CI gates

- [ ] 4.1 Adapt `.github/workflows/ci.yml`: Python version, environment name, install step
      for the package, SAST scope `src`, licence-scan ignore list, and the SAST tool chosen
      in §0. Add a vulnerability check if §0 found it useful.
- [ ] 4.2 Open a PR and get every job green. Then show that each gate fails at least once
      on a deliberately broken commit (formatting error, failing test, fake secret, lock
      drift, SAST finding). Revert, and record the result under this TODO.
- [ ] 4.3 Apply branch protection and the security settings per
      `docs/development/repo-settings.md`, with required approvals at 0 under the documented
      exception. Record the ruleset id and date there.
- [ ] 4.4 Measure coverage and set `fail_under` just below the baseline. Record it in
      `interpretations.md`.

Commit: `ci: adapt quality gates to the core package and enforce them on main`

### Phase 5 — Licence and methodology baseline

- [ ] 5.1 Add `LICENSE` with the PolyForm Noncommercial 1.0.0 text, copied verbatim from
      the official source. Add a licence line to `README.md`.
- [ ] 5.2 Assess areas A–F using `_template.md`. Fill in the gap register,
      `interpretations.md` (formatter, complexity threshold, SAST/secret/SCA tools, coverage
      floor, branch model, AI trailer policy) and `exceptions.md` (EX-001: no non-author
      review, single maintainer).

Commit: `docs(methodology): add PolyForm Noncommercial licence and first methodology baseline`

### Phase 6 — Close

- [ ] 6.1 Update `docs/architecture/overview.md`, `current-state.md` and `README.md` to
      describe what now exists.
- [x] 6.2 Write `docs/mvp/MVP-002-*.md` from the §0 analysis, and link it from the roadmap.
      Result: done early (2026-09-25), right after phase 1, at the owner's request. At close,
      only check that MVP-002 still matches what MVP-001 actually delivered.
- [ ] 6.3 Verify each acceptance criterion for real, including a `git ls-files` check that
      nothing from `docs/reference/` is tracked. Fill in "Outcome at close".

Commit: `docs(mvp-001): close MVP-001 and define MVP-002`

## 5. Risks / open questions

- **Real data leaking into the public repository** is the largest risk. Mitigations:
  `docs/reference/` is git-ignored; the analysis reads only code, instructions and
  configuration; fixtures are synthetic; each PR diff is reviewed before commit. Secret
  scanning does not detect personal data. Consider moving the reference copies outside the
  repository folder (ADR-003, alternatives).
- **The analysis exposes real content to the AI tool.** Instructions and scripts can
  contain names, account numbers or example transactions. If something like that turns up,
  stop, note that it was found (without copying it), and continue only on the code.
- **Single maintainer:** no second human reviews AI-written code. CI gates and the owner's
  own review of every diff are the compensation. This is recorded as EX-001 and a gap-register
  row.
- **Windows vs. Linux lock drift** (known from the template). Trust CI's compile and pin
  platform-conditional packages explicitly.
- **Threat modelling (STRIDE):** not needed for this plan. The skeleton only reads a local
  YAML file and has no network, authentication or sensitive-data flow. A STRIDE pass becomes
  relevant in R3 (agent tools, e-mail, Discord) and R5 (payroll).
- **The consumption mechanism is open (R3).** Keep the public API of the skeleton minimal,
  so that it does not lock in a choice.
