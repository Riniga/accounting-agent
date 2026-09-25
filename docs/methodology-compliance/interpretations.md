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

### 1. *(Next decision — name the chapter, e.g. "Formatter & linter (B2)")*

**Chapter:** *(link)*.

**Decision:** *(what was chosen, and why — the reasoning matters more than the choice)*.

**Follow-up:** *(the plan that implements it)*.
