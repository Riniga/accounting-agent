# Testing Standard

## Purpose

This document defines the testing standards for all projects in the workspace.

> **Relation to the development methodology.** This standard is this project's elaboration
> of methodology [D1 – Testning](../methodology/d-kvalitetssakring/testning.md). Adopted
> from D1:
>
> - A **code coverage floor**, enforced technically as a ratchet (it may not drop) — set
>   just below a real, measured baseline (`pytest-cov`, dated — not a guessed placeholder;
>   see `docs/methodology-compliance/interpretations.md` for the worked example of why
>   this matters), and raised in steps as the codebase matures. Never a target chased
>   toward 100 % (D1 SKA 2). See "Coverage" below.
> - When an **AI tool writes production code**, a human-defined or human-reviewed test that
>   expresses the desired behaviour must exist **before** the implementation (D1 SKA 5). See
>   "AI-Assisted Test-Driven Development" below.
> - Flaky tests are **quarantined** (a non-blocking suite) with an owner and a fix-or-delete
>   deadline (D1 SKA 3); automatic CI retries are capped at 2 (D1 SKA 4). See "Flaky Test
>   Quarantine" below.
>
> The test-strategy shape for this platform (classic pyramid) and the reasoning behind the
> floor and the repo-wide (not per-package) enforcement choice are recorded in
> [`docs/methodology-compliance/interpretations.md`](../methodology-compliance/interpretations.md).

## Test Framework

- Framework: `pytest`
- Test directory: `tests/`
- Test files: `test_<module>.py`
- Tests must be deterministic and runnable offline.
- Avoid external dependencies whenever possible.

## Test Principles

- Every bug fix should include a regression test.
- Every new feature should include tests.
- Prefer fast unit tests over slow integration tests.
- Keep tests isolated and repeatable.

## Test Levels

### Unit Tests
Test individual functions and classes in isolation.

### Integration Tests
Verify collaboration between modules, services or data sources.

### End-to-End Tests
Verify complete user or business workflows where appropriate.

## Running Tests

```bash
pytest
pytest -q
pytest tests/test_example.py
```

All tests should pass before creating a Pull Request.

## Test Requirements

| Change | Required Tests |
|---------|----------------|
| New module | Happy path and error scenarios |
| Bug fix | Regression test |
| New feature | Unit tests and integration tests where applicable |
| Refactoring | Existing tests must remain green |

## Test Data

- Keep fixtures small and reusable.
- Do not depend on production data.
- Prefer factories or fixtures over hard-coded data.

## CI

- All automated tests must pass before merging.
- New failing tests must be investigated before merge.

## Coverage

- Measured with `pytest-cov` (`pytest -m "not quarantine" --cov`); configured in
  `pyproject.toml` (`[tool.coverage.run]`/`[tool.coverage.report]`).
- Enforced as a **ratchet**: CI fails if coverage drops below the floor recorded in
  `pyproject.toml` (`fail_under`). It is never a target chased toward 100 % — some code
  (CLIs' `__main__` wiring, defensive branches) is reasonably left uncovered.
- The floor may only be **raised**, and only in a deliberate PR that also updates the floor
  value and this document — never lowered to make a failing build pass.
- The floor is repo-wide, not per package (see `interpretations.md` §1 for the trade-off);
  if one package's coverage trends down while others compensate, that's a case for
  revisiting per-package floors, not for this document to solve unilaterally.

## Flaky Test Quarantine

- Mark a flaky test `@pytest.mark.quarantine` (registered in `pytest.ini`) rather than
  deleting it or leaving it to fail CI intermittently.
- A quarantined test still runs in CI (visible in the log) but does not block the build and
  is excluded from the coverage gate.
- Quarantining a test requires, next to the marker, a comment recording an **owner** and a
  **fix-or-delete deadline** — a quarantined test with neither is itself a bug:

  ```python
  @pytest.mark.quarantine  # owner: <name>, fix-or-delete by 2026-XX-XX — <why it's flaky>
  def test_something_flaky():
      ...
  ```

- A test past its deadline should be fixed or deleted, not left quarantined indefinitely.

## Retry Policy

- Automatic CI retries on a test failure are capped at **2** (D1 SKA 4).
- No retry plugin is installed today, so this cap is a documented ceiling, not yet a
  technical control — CI does not currently retry failed tests at all. If flaky tests appear
  often enough in practice to justify automatic retries, add a retry plugin capped at this
  limit as its own small change, rather than raising the cap to fit a specific test.

## AI-Assisted Test-Driven Development

When an AI tool (including Claude Code) writes **production code** — not a prototype,
spike, or throwaway experiment — a human-defined or human-reviewed test that expresses the
desired behaviour must exist **before** the AI writes the implementation (D1 SKA 5):

- The test may be written by a human, or written by the AI and then reviewed and accepted by
  a human, before implementation starts.
- The test must fail for the right reason (the behaviour is missing) before the
  implementation lands, and pass afterwards.
- This does not apply to non-production code an AI tool writes on its own initiative — a
  throwaway debugging script, for example — only to changes that ship.

## Known Limitations

Project-specific limitations (database engines, authentication providers, external services, etc.) belong in the project's architecture or testing documentation—not in this shared standard.
