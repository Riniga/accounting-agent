# Plan: MVP-001 – Walking skeleton & baseline analysis

Reference: [`docs/mvp/MVP-001-walking-skeleton.md`](../mvp/MVP-001-walking-skeleton.md)

**Status:** Not started — plan written, awaiting review.

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

- [ ] 1.1 Toolchain: Python version, tool and action versions, Conda vs. `uv`. Record in §0.
- [ ] 1.2 GitHub-native security features for the repository, and Semgrep vs. CodeQL.
      Record in §0.
- [ ] 1.3 Baseline analysis of `HJK - Ekonomi` (the seven questions) plus the lighter pass
      over JudoSyd and Aktivitet Förebygger. Record in §0.

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
- [ ] 6.2 Write `docs/mvp/MVP-002-*.md` from the §0 analysis, and link it from the roadmap.
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
