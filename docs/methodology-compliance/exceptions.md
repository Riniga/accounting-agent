# Documented exceptions

Recorded deviations from [the methodology](../methodology/index.md). Two kinds:

1. **Undantag-allowed** — permitted by a chapter's own "Undantag" (exception) section and
   recorded here per that section's requirement (the exception and its reason are
   documented in the actual work's own record).
2. **Forced by circumstance** — a requirement the methodology does *not* permit an
   exception from, but which is physically impossible to meet right now (e.g. non-author
   review with a single maintainer). Accepted by whoever owns the methodology adoption as a
   temporary, visible non-compliance with a concrete close condition, **and also kept as an
   open row in the gap register**.

Every entry is time-boxed, has a named responsible person, and a review trigger. An
exception is never a permanent waiver. Related: [`gap-register.md`](gap-register.md).

---

## EX-001 — No non-author review (single maintainer)

| | |
|---|---|
| **Methodology basis** | Kind 2, forced by circumstance. [D2](../methodology/d-kvalitetssakring/kodgranskning.md) SKA 2–3, [F1](../methodology/f-ai-samarbete/riktlinjer-for-ai-assisterade-verktyg.md) SKA 1, [D3](../methodology/d-kvalitetssakring/definition-of-done.md) SKA 3. D2's own Undantag only allows postponing review during an incident, so this is not an Undantag. |
| **Status** | Active |
| **Granted** | 2026-09-25 |
| **Responsible** | Rickard Nisses-Gagnér (owner, sole maintainer) |
| **Review** | When a second person can review — then raise required approvals to 1 and add `CODEOWNERS` ([`repo-settings.md`](../development/repo-settings.md) §3). Otherwise re-confirmed at every MVP close. |
| **Gap-register link** | `GAP-D2-REVIEW`, `GAP-F1-SELFMERGE` |

The project has one person in every role. A required non-author approval would make merging
impossible, so the "Protect main" ruleset requires a pull request and all six CI checks, but
**0 approvals**.

**Compensating controls:**
- No one can push to `main` directly, the owner included (empty bypass list).
- Every change passes Ruff, dependency, SAST, secret, instruction-file and test gates.
- The owner reviews every AI-assisted diff before commit and before merge.
- The AI tool asks before `git commit` and `git push` (`.claude/settings.json`), and does
  not merge pull requests itself.

**What it does not cover:** a second pair of eyes on design and correctness, which no
automated gate replaces.

---

## EX-002 — AI-written tests not reviewed before implementation (MVP-001 phase 2)

| | |
|---|---|
| **Methodology basis** | Kind 2, forced by the owner's decision. [D1](../methodology/d-kvalitetssakring/testning.md) SKA 5 (AI-TDD). D1's Undantag does not cover it. |
| **Status** | Closed (one-off) |
| **Granted** | 2026-09-25 |
| **Responsible** | Rickard Nisses-Gagnér |
| **Review** | Closed when PR #5 is reviewed, since the tests are reviewed together with the code there. |
| **Gap-register link** | `GAP-D1-AITDD` |

For MVP-001 phase 2, the owner explicitly chose to skip reviewing the AI-written tests
before the AI wrote the implementation. The tests were still written first and shown to fail
for the right reason (`ModuleNotFoundError`) before any implementation existed. They cover
the profile validation and the `run` command (27 tests).

This is **not a standing waiver**. Future MVPs follow D1 SKA 5, unless the owner records a new
exception.

---

## EX-003 — AI tool on a personal plan, with model-training opt-in on

| | |
|---|---|
| **Methodology basis** | Kind 2, forced by circumstance. [A2](../methodology/a-grundforutsattningar/verktyg-for-ai-assisterad-utveckling.md) SKA 1–2, [F2](../methodology/f-ai-samarbete/sekretess-och-dataskydd-vid-ai-anvandning.md) SKA 3. A2 has no Undantag that allows it. |
| **Status** | **Closed 2026-09-25** — the owner turned the model-training setting off the same day (owner's statement) |
| **Granted** | 2026-09-25 |
| **Responsible** | Rickard Nisses-Gagnér |
| **Review** | **2026-10-02** — the setting must be off by then; re-checked at MVP-001 close review and at every MVP start until done. |
| **Gap-register link** | `GAP-A2-AGREEMENT`, `GAP-F2-DPA` |

Claude Code runs on the owner's **individual Pro plan**, confirmed on 2026-09-25. On that plan
the privacy setting *"Help improve our AI models"* is **on**, which lets the provider use
conversations and code for model training. There is no organisation agreement and no data
processing agreement. The project has no organisation to hold one.

**Why this is the most urgent item:** on 2026-09-25 personal data from an organisation
project reached the AI tool's context (`GAP-F2-CONFIDENTIAL`). With training on, such data
may also be used for training.

**Fix (owner, about one minute):** claude.ai → *Settings* → *Privacy* → turn off the
model-improvement setting. Then update this entry to *Closed*, and `GAP-A2-AGREEMENT` to
"partially met": individual plan, training off, still no DPA.

**Until fixed:** no material classed Confidential (interpretations §9) may be given to the
AI tool — including from `docs/reference/`.

**Closed 2026-09-25:** the owner reports the setting is now off. What remains is not an
exception but open gaps: an individual plan instead of an organisation agreement
(`GAP-A2-AGREEMENT`), and no DPA (`GAP-F2-DPA`). The rule in interpretations §9 —
no Confidential material in AI context — still applies regardless.
