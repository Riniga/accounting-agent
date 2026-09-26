# Methodology compliance

Internal record of how this project meets
[the development methodology](../methodology/index.md) (or your own organisation's
equivalent), which project-level interpretations were made where the methodology leaves a
choice, and what is still open.

**This area is internal.** If you publish a documentation portal from this repo, make sure
its build points at `docs/methodology/` by exact path (or an equivalent explicit list) and
never globs this directory in — this compliance record is not meant to be published.

Adoption decision: [ADR-001](../architecture/decisions/ADR-001-adopt-development-methodology.md).
Baseline established by [MVP-001](../mvp/MVP-001-walking-skeleton.md) on 2026-09-25.

**Standing at a glance (2026-09-25):**

| Area | Standing | Highest open gap |
|---|---|---|
| [A](a-grundforutsattningar.md) | partially met | M — individual AI plan, no organisation agreement (training off since 2026-09-25) |
| [B](b-skriva-kod.md) | mostly met (B4 n/a) | L |
| [C](c-sakerhet.md) | partially met | M — no vulnerability prioritisation |
| [D](d-kvalitetssakring.md) | partially met | **H — no non-author review (EX-001)** |
| [E](e-leverans.md) | met / n/a (E1 partial) | M — AI trailers in history |
| [F](f-ai-samarbete.md) | **not met (F2)** | **H — personal data reached AI context; AI can self-merge** |

## What establishing this baseline does and does not do

Establishing the baseline sets the **preconditions** for following the methodology — the
assessment, the interpretations, and the low-cost guardrails. It does **not** make every
requirement pass on day one. Closing the remaining gaps is the job of follow-up plans,
each tracked in the gap register.

## Files

| File | What it holds |
|------|---------------|
| [`gap-register.md`](gap-register.md) | Every open gap: chapter, gap, severity, owner, follow-up plan, status. |
| [`interpretations.md`](interpretations.md) | The project-level decisions the methodology invites — tool choices, thresholds, branch model, CODEOWNERS, SBOM format, instruction-file structure. Each section cites the chapter it answers. |
| [`exceptions.md`](exceptions.md) | Documented, time-boxed deviations allowed by a chapter's own "Undantag" (exception) section. |
| `a-grundforutsattningar.md` … `f-ai-samarbete.md` | One assessment file per methodology area, created as you assess it, using `_template.md` as the structure. |
| [`_template.md`](_template.md) | The fixed structure each chapter assessment follows |

## How to read (or write) a chapter assessment

Each chapter is assessed with the fields in [`_template.md`](_template.md):

- **Methodology status** — is the methodology chapter itself `fastställd` or `utkast`
  (and if `utkast`, what expert point is pending).
- **Platform standing** — one of: `met`, `partially met`, `not met`,
  `not applicable yet`, `external dependency`.
- **SKA points** — a row per SKA requirement with its standing and a short note.
- **BÖR points we adopt** — the recommendations you commit to.
- **Project interpretation** — what was chosen where the chapter leaves a choice, linking
  the relevant section of [`interpretations.md`](interpretations.md).
- **External dependency** — a central/organisation-owned item this project cannot close
  itself, with the owner to confirm it.
- **Follow-up plan** — the plan that will close the gap, or "none needed".

A chapter marked **`external dependency`** is not a project failure — it is blocked on a
central organisational decision (developer-workstation isolation, SSO, a central secrets
vault, a procured SAST tool, a CVD policy text, a vendor DPA, …). Reference and track those;
don't invent them.
