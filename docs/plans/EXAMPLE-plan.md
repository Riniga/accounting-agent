# Plan: MVP-EXAMPLE – Test methodology (worked example)

> Genericised worked example — see `../mvp/EXAMPLE-mvp.md` for the MVP this implements, and
> that file's "Outcome at close" for how this plan's investigation changed the actual
> outcome. Delete both once you have real ones.

Reference: [`docs/mvp/EXAMPLE-mvp.md`](../mvp/EXAMPLE-mvp.md)

**Status:** Implemented — pending PR.

## 0. Investigation

Measured coverage for real before writing a floor number into any config (`pytest-cov`,
run against the actual codebase):

| Package | Coverage |
|---|---|
| `package-a` | 100% |
| `package-b` | 87% |
| `package-c` | 76% |
| **Repo-wide** | **78%** |

The MVP's own plan assumed "start at 50%, the methodology's suggested adoption-friendly
starting point" — written before anyone had actually measured. At this real baseline, 50%
would never function as a ratchet (coverage would need to regress ~28 points before it
ever triggered). **Adjusted floor: 70%** — set just below the measured baseline (closest
package: `package-c` at 76%), enforced in `pyproject.toml`'s `[tool.coverage.report]
fail_under`.

Also checked: repo-wide vs. per-package floor. Coverage varies 76–100% across packages — a
single repo-wide number is simpler to configure and enforce than one per package.
Trade-off, accepted deliberately: a regression in the weakest package could be masked by a
stronger one without moving the repo-wide number for a while. Revisit if that package's
coverage trends down further — this is a decision to record and revisit, not one to
silently make once and forget.

## 1. Goal

A coverage floor enforced as a ratchet in CI (starting at the measured-baseline value
above); a non-blocking `quarantine` test marker with an owner/deadline policy; the AI-TDD
rule written into the project's instruction files.

## 2. Scope boundary

- **In:** `pytest-cov` wired into the existing CI test job; the coverage floor in
  `pyproject.toml`; a `quarantine` marker registered in `pytest.ini`; the AI-TDD paragraph
  in the instruction files and testing standard.
- **Out:** writing new tests to raise coverage toward a higher target (ongoing work, not
  this plan); a retry plugin for flaky tests (documented cap only, for now).

## 3. Chapters addressed

- Methodology D1 – Testning (coverage floor, flaky-test policy, AI-TDD)

## 4. TODOs

- [x] Add `pytest-cov` to the dev dependencies.
- [x] Add `[tool.coverage.run]`/`[tool.coverage.report]` to `pyproject.toml` with
      `fail_under = 70`, with a comment recording that 70% is the measured-baseline floor
      (§0), not an arbitrary number.
- [x] Register the `quarantine` marker in `pytest.ini` with an owner/deadline expectation
      in the marker description.
- [x] Wire the CI test job to run quarantined tests separately and non-blocking, then the
      real gating run with `--cov`.
- [x] Add the AI-TDD paragraph to the testing standard and the instruction files, with a
      cross-reference between the two.
- [x] Ran the full test suite locally with the new coverage gate before proposing the PR:
      passed, coverage at 78% (above the 70% floor).

## 5. Risks / open questions

- Raising the floor from 70% toward a higher target is explicitly out of scope here — a
  deliberate future step, not automatic.
- The retry cap is documented but not technically enforced (no plugin installed). If flaky
  tests start appearing often enough to justify one, that's its own small follow-up.
