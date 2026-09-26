# MVP-001 – Walking skeleton & baseline analysis

Roadmap: [R1 – Foundation](../roadmap.md#r1--foundation-done) ·
Plan: [`MVP-001-walking-skeleton.plan.md`](../plans/MVP-001-walking-skeleton.plan.md)

## Purpose

Most of this project's code will be written with AI assistance, and it is financial
software. Before any real accounting logic is extracted into the core, the quality and
security gates must exist and be proven to work end to end: a package that installs, a
command that runs, a test that passes, and CI that blocks a pull request when something is
wrong.

At the same time, we do not yet know what to extract first. The initial idea asks seven
concrete questions about the existing Helsingborgs Judoklubb project; answering them is what
turns MVP-002 from a heading into a concrete increment.

## Goals

- A change to this repository can only reach `main` through a pull request whose CI gates
  (lint/format, tests with a coverage floor, secret scan, dependency scan, SAST,
  instruction-file scan) are green.
- The thinnest possible end-to-end path exists: install the package, run
  `accounting-agent run <org>` against a configuration directory, and get a validated
  result — proven by a test.
- The project's standing against the development methodology is known and written down,
  including the single-maintainer exception.
- We know, based on the actual code rather than assumptions, which parts of the Helsingborgs
  Judoklubb project are general and should move to the core first.

## Context

The repository was initialised from a template on 2026-09-25: vision, roadmap and ADR-001–005
are written, but there is no code. The template's CI workflow and Python tool configuration
still contain placeholders and have never run. The three existing organisation projects are
available locally in the git-ignored `docs/reference/` folder
([ADR-003](../architecture/decisions/ADR-003-no-real-data-in-core-repo.md)).

See [`docs/architecture/overview.md`](../architecture/overview.md) and
[ADR-002](../architecture/decisions/ADR-002-python-core-repository.md) for the chosen
structure.

## Scope

- An installable Python package `accounting-agent` (`src/accounting_agent/`) with a console
  command `accounting-agent run <org> --config-dir <path>` that loads `organisation.yaml`,
  validates it (organisation id and a `features` map of booleans), logs which features are
  enabled, and exits with a non-zero code and a clear message on invalid input.
- A synthetic example organisation under `tests/fixtures/` and tests for the valid and
  invalid cases.
- The template's tool configuration adapted to the package: `pyproject.toml`, `pytest.ini`,
  `environment.yml`, `requirements.in` + a generated `requirements-lock.txt`,
  `.pre-commit-config.yaml`.
- CI running on pull requests to `main`, all gates green; `main` protected so that a pull
  request with green CI is required.
- `LICENSE` with the PolyForm Noncommercial 1.0.0 text
  ([ADR-005](../architecture/decisions/ADR-005-noncommercial-licence.md)).
- First methodology assessment in `docs/methodology-compliance/`: one file per area A–F,
  the gap register, `interpretations.md` for the choices made, and the single-maintainer
  review exception in `exceptions.md`.
- An analysis of the Helsingborgs Judoklubb project answering the initial idea's seven
  questions, plus a lighter pass over JudoSyd and Aktivitet Förebygger, reading only code,
  instructions, configuration, chart of accounts and rules.

## Out of Scope

- Any real accounting logic — import, matching, posting, validation, reporting. That starts
  in MVP-002, informed by this MVP's analysis.
- A data model beyond the organisation profile.
- Calling an LLM, agent tools, confidence levels, approval policies, audit trail (R3).
- Deciding how organisation projects consume the core (R3).
- Changing any organisation project.
- CD, deployment, publishing the package.
- A scheduler.

## Acceptance Criteria

- In a fresh clone, following `docs/development/setup.md` and `environment.md` gives a
  working environment, and `accounting-agent run example --config-dir tests/fixtures/...`
  prints the enabled features and exits 0.
- `pytest` passes locally and in CI, with the coverage floor set just below the measured
  baseline.
- A pull request to `main` runs every gate listed in Goals, and each gate has been shown to
  fail on a deliberately broken commit at least once (then reverted).
- `main` cannot be pushed to directly; merging requires the CI checks to pass. The
  required-approval exception is documented in `exceptions.md` and the gap register.
- `docs/methodology-compliance/` has an assessment for each area A–F, and every open gap
  has a row in the gap register.
- The analysis answers the seven questions for Helsingborgs Judoklubb, and MVP-002 is
  detailed from it.
- No file under `docs/reference/` is tracked by git, and no real organisation data appears
  in any committed file.

## Outcome at close (2026-09-25)

Closed as **delivered**, pending the merge of PR #5. Re-verified in the MVP close review on
the same day. Against the criteria above:

- **Fresh clone → working environment → `run` exits 0: met.** Verified from a fresh clone
  of the pushed branch (`972481e`): environment in 30 s, all tests passing, the example
  run exiting 0.
- **`pytest` passes locally and in CI, with the coverage floor below the measured baseline:
  met, with a deliberate margin.**
  - 29 tests pass locally. The close review added 2 tests for behaviour that already
    existed: `--version`, and the output when no feature is enabled. CI was green with 27
    tests on every earlier push.
  - Coverage is 96.47 %. The floor is 90 %, not "just below", because a codebase of 85
    statements swings several points with one new module. It is to be raised in MVP-002
    (interpretations §1). The owner accepted this margin when it was reported in phase 4.
- **Every gate runs on the PR and was shown to fail at least once: met, with two
  adjustments the owner accepted.**
  - Six required checks run on every PR, and each was shown to fail on throwaway PR #6.
  - `pip-audit` and the licence scan were shown to fail locally, not on a PR commit,
    because they run after the lock-drift step in the same job.
  - CodeQL was removed after it let `shell=True`, `eval` and `yaml.load` through while
    Semgrep blocked all three (interpretations §2).
- **`main` protected, merge requires CI, approval exception documented: met.** Ruleset
  "Protect main" has no bypass, the owner included. There are 0 required approvals, under
  EX-001.
- **Methodology assessment A–F plus gap register: met.** 21 chapters assessed, 22 gap rows,
  9 interpretations, 3 exceptions. EX-003 (AI-tool training setting on) was **closed the
  same day** after the owner turned the setting off. The honest headline remains that
  **F2 is not met**: personal data reached the AI tool's context during the analysis
  (`GAP-F2-CONFIDENTIAL`), and there is no DPA with the provider (`GAP-F2-DPA`).
- **Analysis answers the seven questions; MVP-002 defined from it: met.** The analysis
  moved MVP-002's focus from bank import to the book model that Helsingborgs Judoklubb and
  Aktivitet Förebygger already share.
- **Nothing from `docs/reference/` tracked, no real data committed: met.** Verified with
  `git ls-files`, the branch history and pattern searches.

**Deviations from the plan, all recorded where they happened:**
- `uv` was not trialled (§0); the CI timings later showed Conda is fast enough.
- The owner waived reviewing the tests before implementation in phase 2 (EX-002). The tests
  are therefore reviewed in PR #5 — that review is still outstanding.
- The AI tool added `Co-Authored-By` trailers against `AGENTS.md` until phase 5
  (`GAP-E1-AITRAILER`).
- MVP-002 was written right after phase 1, at the owner's request.
- `.claude/settings.json` was changed (`gh pr merge` made an ask-first action). It lies
  outside the plan's scope boundary, but is a direct mitigation of `GAP-F1-SELFMERGE`,
  found in the phase-5 assessment.
- The close review corrected template leftovers that were wrong for this project, in
  `git.md`, `dependencies.md`, `testing.md`, the PR template and `AGENTS.md`.
