# Project-level interpretations

Where [the methodology](../methodology/index.md) deliberately leaves a choice to the
project — a tool, a threshold, a branch model — this file records the choice **once**. The
area files (`a-…` through `f-…`) and the follow-up plans link here instead of repeating the
decision.

Each section names the methodology chapter it answers. A decision here is a *decision*, not
an implementation — the follow-up plan named in each section does the work.

Established by [MVP-001](../mvp/MVP-001-walking-skeleton.md); the adoption decision is
[ADR-001](../architecture/decisions/ADR-001-adopt-development-methodology.md).

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

---

### 3. Formatter, linter and complexity (B1, B2)

**Chapter:** [B1](../methodology/b-skriva-kod/kodkvalitet-och-clean-code.md) BÖR 2,
[B2](../methodology/b-skriva-kod/kodstandard-och-stil.md) SKA 2–4.

**Decision:** **Ruff** is both the formatter and the linter, with default formatting and a
small rule set (`E4`, `E7`, `E9`, `F`, `W`, `I`, `UP`, `B`, `C4`, `C90`), configured in
`pyproject.toml`. The same pinned version runs in pre-commit and in the required `Ruff` CI
check. Cyclomatic complexity **blocks at 20** (`mccabe.max-complexity`). The advisory value
is **10** (`docs/standards/coding.md`). Cognitive complexity is advisory only, because
there is no suitable tool for it yet. The values are inherited from the template and are
generous for a new codebase. Revisit them in MVP-002, once real domain code exists.

**Module boundary (B3, added in MVP-002):** `TID251` (`flake8-tidy-imports.banned-api`)
bans `csv`, `io`, `pathlib`, `accounting_agent.formats` and `accounting_agent.cli`
everywhere. `per-file-ignores` allows them only in `formats/**`, `cli.py`, `__main__.py`,
`profile.py`, `tests/**` and `scripts/**`. This keeps the book domain
(`accounting_agent.books`) free of file I/O without a new dependency (ADR-006). It checks
imports only; a bare built-in `open()` is left to review. It was verified by adding
`import csv` to `books/model.py`, which Ruff reported as TID251.

**Follow-up:** none.

---

### 4. Test strategy (D1)

**Chapter:** [D1 – Testning](../methodology/d-kvalitetssakring/testning.md) SKA 1.

**Decision:** **Mostly unit tests, plus thin end-to-end tests through the command line.**
The risk in this project is in deterministic domain rules — book validation, balances,
matching, posting — where a wrong result is silent and costly. That logic is tested
directly, against small synthetic fixtures. Each command gets at least one end-to-end test
through `python -m accounting_agent`, so that the wiring is covered too. There are no
external services to integration-test yet. Revisit when R3/R4 add Claude, Gmail or Discord
integrations; those are mocked in tests (`docs/standards/testing.md`).

**Follow-up:** none.

---

### 5. Dependency tooling (C2)

**Chapter:** [C2](../methodology/c-sakerhet/beroendehantering-paketkallor-och-signering.md) SKA 1–5.

**Decision:**
- **Lock:** `pip-compile --generate-hashes` → `requirements-lock.txt`. Conda supplies only
  Python.
- **SCA:** `pip-audit` on every PR (the `Dependencies` check), plus Dependabot alerts on
  `main`.
- **Licences:** `pip-licenses` against the allowlist in `docs/standards/dependencies.md`.
  With no organisation legal function, **the owner approves any licence outside the
  allowlist**, recorded in the PR that adds it.
- **Updates:** Dependabot version updates, weekly, for pip and GitHub Actions.
- **SBOM:** not automated yet. GitHub's dependency graph export (SPDX) is available on
  demand. Automate when releases exist.

**Follow-up:** gap rows `GAP-C2-*`.

---

### 6. Secret scanning layers (C4, F2)

**Chapter:** [C4](../methodology/c-sakerhet/hantering-av-hemligheter.md) SKA 1,
[F2](../methodology/f-ai-samarbete/sekretess-och-dataskydd-vid-ai-anvandning.md) SKA 5–7.

**Decision:** three independent layers:
1. **detect-secrets** as a pre-commit hook, against `.secrets.baseline`.
2. **detect-secrets** as the required `Secret scan` CI check.
3. **GitHub secret scanning with push protection** on the repository.

A genuine false positive gets an inline `# pragma: allowlist secret`, not a weaker check.
Scanning at write time and before context reaches the model is not in place (F2 SKA 6,
partial).

**Follow-up:** none now.

---

### 7. AI-assistance marking (E1, F1)

**Chapter:** [E1](../methodology/e-leverans/versionshantering-och-branchstrategi.md) SKA 5.

**Decision:** **No AI trailer in commit messages.** AI assistance is marked per pull
request, with the PR template's "AI assistance" checkbox and the tool's name. That is
where review happens.

**History:** the commits made on 2026-09-25 during initialisation and MVP-001 phases 1–4
carry a `Co-Authored-By: Claude …` trailer. The AI tool added it against `AGENTS.md`. Those
commits are already on `main` or on the published MVP-001 branch. Rewriting them would
require force-pushing published history, a larger risk than the non-compliance itself. They
are left as they are, and this entry is the record. From phase 5 onwards no trailer is
added.

**Follow-up:** `GAP-E1-AITRAILER` (closed once no new trailers appear).

---

### 8. Branch model and versioning (E1)

**Chapter:** [E1](../methodology/e-leverans/versionshantering-och-branchstrategi.md) SKA 1–4, 6.

**Decision:** **One short-lived feature branch per MVP** off `main`
(`feature/mvp-NNN-slug`; `fix/`, `docs/`, `ci/` for smaller work), merged through a pull
request that links the MVP and its plan. This is not trunk-based development and is not
called that. **Semantic Versioning** for the package (`accounting_agent.__version__`),
starting at `0.1.0`. It stays below 1.0.0 until the core's API is stable enough for the
organisation projects to depend on.

**Follow-up:** none.

---

### 9. Data classification for AI use (F2)

**Chapter:** [F2](../methodology/f-ai-samarbete/sekretess-och-dataskydd-vid-ai-anvandning.md) SKA 1–2, 8.

**Decision:** three levels for material this project handles, and what an AI tool may read
while working **in this repository**:

| Level | Examples | May enter AI context here |
|---|---|---|
| Public | This repository: code, docs, synthetic fixtures | Yes |
| Internal | Organisation projects' code, AI instructions, configuration, chart of accounts, rule descriptions | Yes, read from `docs/reference/` for extraction work |
| Confidential | Books, vouchers, bank files, receipts, invoices, payroll, personnel and member data, personal identity numbers, names tied to amounts | **No** |

**Reading rule for `docs/reference/`:**
- Before opening a file there, check by name and location that it is Internal.
- If an Internal file turns out to contain Confidential content (as happened on
  2026-09-25), stop, record that it happened without copying the content, and continue
  only with material known to be clean.
- Organisation projects are encouraged to keep rules and decision logs apart, so that
  rules can be read without personal data.

How each organisation project uses Claude Code on its own books is governed in that
project, not here.

**Follow-up:** `GAP-F2-CONFIDENTIAL`, `GAP-F2-CLASSIFICATION`.
