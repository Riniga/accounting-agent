# Project-level interpretations

Where [the methodology](../methodology/index.md) deliberately leaves a choice to the
project — a tool, a threshold, a branch model — this file records the choice **once**. The
area files (`a-…` through `f-…`) and the follow-up plans link here instead of repeating the
decision.

Each section names the methodology chapter it answers. A decision here is a *decision*, not
an implementation — the follow-up plan named in each section does the work.

Established by the MVP that adopted the methodology; record that adoption as an ADR and
link it here.

---

### Example: Test-strategy shape (D1)

<!-- This is a worked example from the project this reference was drawn from, kept to show
     the expected shape and rigour of an entry — measure the real baseline before deciding
     a number, don't guess one. Replace with your own project's actual chapters and
     decisions; delete this example once you have real entries. -->

**Chapter:** [D1 – Testning](../methodology/d-kvalitetssakring/testning.md) (SKA 1–2, BÖR 1).

**Decision:** **Classic test pyramid.** State *why* — where does this project's risk
actually live (heavy domain logic? thin CRUD? something else)? Pick the shape the
methodology chapter recommends for that profile, don't default to whatever's familiar.

**Coverage:**

- Measure the real baseline (`pytest-cov`, dated) before setting a floor number — a floor
  set as a generic placeholder (e.g. "50%, the chapter's suggested adoption-friendly
  starting point") can end up meaningless if the real baseline is already well above it,
  as happened in this worked example.
- **Floor:** set just below the measured baseline, enforced as a **ratchet** (CI fails if
  coverage drops below it — never a rising target chased toward 100%).
- Decide **repo-wide vs. per-package** deliberately and record the trade-off, not just the
  choice.
- The floor is raised in steps as the codebase matures, each raise a deliberate PR that
  also records the new floor and updates this section.

**Follow-up:** *(the plan that implements this decision)*.

---

### 1. Coverage floor (D1)

**Chapter:** [D1 – Testning](../methodology/d-kvalitetssakring/testning.md) (SKA 2).

**Measured baseline:** 96.47 % (82 of 85 statements), `pytest-cov` in CI on
2026-09-25, PR #5. The only uncovered file is `__main__.py`, which the tests run in a
subprocess, where coverage doesn't measure it.

**Decision:** **`fail_under = 90`**, repo-wide, enforced as a ratchet in `pyproject.toml`.
It is set a few points below the baseline rather than right at it, because the codebase is
tiny: one new, partly tested module could move the total several points, and a floor at
96 % would turn normal growth into build failures instead of catching regressions. A
per-package floor isn't relevant — there is only one package. Raise the floor in a
deliberate PR once the codebase has grown and its coverage is stable (MVP-002 is the
first natural review point).

**Follow-up:** [MVP-001 plan](../plans/MVP-001-walking-skeleton.plan.md), step 4.4.

---

### 2. SAST tool (C1)

**Chapter:** [C1 – Secure coding-principer](../methodology/c-sakerhet/secure-coding-principer.md)
(SKA 2). The chapter names Semgrep and CodeQL as examples and leaves the choice to the
project.

**Investigated (2026-09-25):** both tools ran in CI side by side, first on clean code
(PR #5: both 0 findings; Semgrep 27 s, CodeQL 57 s), then on deliberately insecure code
(throwaway PR #6: `subprocess.call(..., shell=True)`, `yaml.load(..., Loader=yaml.Loader)`
and `eval()`).
- **Semgrep** (`p/security-audit` + `p/owasp-top-ten`, 201 rules) flagged all three as
  blocking.
- **CodeQL** (`security-extended`) flagged none. Its Python queries report only when data
  flows from a recognised remote source, such as a web request, and a local CLI has none.

**Decision:** **Semgrep is the blocking SAST gate (`SAST` job); CodeQL is removed.** For
this codebase, CodeQL doubled the run time without adding signal.

**Revisit:** when the core starts handling external input — e-mail, Discord or network
APIs (R4) — CodeQL's data-flow analysis becomes relevant. Re-evaluate adding it then.

**Follow-up:** [MVP-001 plan](../plans/MVP-001-walking-skeleton.plan.md), step 4.2.
