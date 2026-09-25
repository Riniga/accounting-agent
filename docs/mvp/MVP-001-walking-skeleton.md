# MVP-001 – Walking skeleton & baseline analysis

Roadmap: [R1 – Foundation](../roadmap.md#r1--foundation-done--pending-merge-of-pr-5) ·
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

## Outcome at close (YYYY-MM-DD)

<!-- Fill in when the MVP is actually closed. -->
