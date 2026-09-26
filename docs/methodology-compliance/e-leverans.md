# E — Leverans

First assessment: 2026-09-25 (MVP-001). There is no CD and no hosted service; the core is a
package run locally. Several E requirements are written for services and are
`not applicable yet`.

---

### `E1` — `Versionshantering & branchstrategi`

Methodology chapter: [`versionshantering-och-branchstrategi`](../methodology/e-leverans/versionshantering-och-branchstrategi.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `partially met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Short-lived feature branches | met | One branch per MVP, merged when the MVP closes (days). |
| 2 | Only call it trunk-based if CI, flags and a merge queue exist | met | It is not called trunk-based. |
| 3 | Commit messages say what and why | met | Conventional-style messages with a body. |
| 4 | Semantic Versioning | met | `0.1.0` in `accounting_agent.__version__`. |
| 5 | No AI-specific marking in commits | **not met** | Commits from 2026-09-25 carry a `Co-Authored-By: Claude …` trailer, added by the AI tool against `AGENTS.md`. Stopped from MVP-001 phase 5 onwards. Rewriting the already-published history is not worth the risk — see interpretations §7. |
| 6 | PR linked to a work item, technically enforced | partial | The PR template asks for the MVP/plan link. GitHub has no built-in enforcement. |

**Project interpretation:** branch model and versioning — [`interpretations.md#8-branch-model-and-versioning-e1`](interpretations.md#8-branch-model-and-versioning-e1);
AI trailers — [`interpretations.md#7-ai-assistance-marking-e1-f1`](interpretations.md#7-ai-assistance-marking-e1-f1).

**Gap-register rows:** `GAP-E1-AITRAILER`, `GAP-E1-WORKITEM`

---

### `E2` — `CI/CD & automatisering`

Methodology chapter: [`ci-cd-och-automatisering`](../methodology/e-leverans/ci-cd-och-automatisering.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Full automated check chain on every PR before merge | met | Six required checks. |
| 2 | Fail-fast ordering | met | `Ruff` first; everything else `needs: lint`. |
| 3 | Feature flags categorised, owned, removed | n/a | No feature flags. |
| 4 | Main branch stays green | met | Strict required checks (branch must be up to date) plus CI on push to `main`. |

**Gap-register rows:** none.

---

### `E3` — `Miljöhantering & konfiguration`

Methodology chapter: [`miljohantering-och-konfiguration`](../methodology/e-leverans/miljohantering-och-konfiguration.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Environment-specific config outside the code | met | None needed yet. Organisation settings come from each organisation's own `organisation.yaml`. |
| 2 | Checked-in example file (`.env.example`), no real values | met | |
| 3 | Environments codified, not hand-configured | met | The development environment is `environment.yml`. There are no deployed environments. |
| 4 | Ephemeral preview environments get no production secrets/data | n/a | None exist. |

**Gap-register rows:** none.

---

### `E4` — `Observability`

Methodology chapter: [`observability`](../methodology/e-leverans/observability.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `not applicable yet` (except SKA 3)

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Instrumentation via OpenTelemetry | n/a | Local CLI, not a service. |
| 2 | Structured JSON logs with trace id | n/a (yet) | Plain-text logging to stderr. Revisit in R3, where the agent's audit trail and scheduled runs make structured logs useful. |
| 3 | No personal data, credentials or secrets in logs; automated masking | met | Every line `validate` prints passes `mask_personal_numbers()`; findings never quote voucher text; tested, including a deliberately leaky finding (MVP-002). |
| 4 | Health endpoints (liveness/readiness) | n/a | No service. |
| 5 | RED metrics per endpoint | n/a | No service. |

**Follow-up plan:** none needed for SKA 3; revisit SKA 2 (structured logs) in R3.
**Gap-register rows:** ~~`GAP-E4-MASKING`~~ (closed by MVP-002)
