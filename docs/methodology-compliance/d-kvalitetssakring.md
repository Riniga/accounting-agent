# D — Kvalitetssäkring

First assessment: 2026-09-25 (MVP-001).

---

### `D1` — `Testning`

Methodology chapter: [`testning`](../methodology/d-kvalitetssakring/testning.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `partially met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Test distribution chosen by where the risk is | met | Decided in interpretations §4. |
| 2 | Coverage floor enforced as a ratchet | met | `fail_under = 90`, measured baseline 96.47 % — see interpretations §1. |
| 3 | Flaky tests quarantined, with owner and deadline | met | `quarantine` marker, run non-blocking in CI. |
| 4 | Automatic CI retries capped (≤ 2) | met | CI does not retry at all. |
| 5 | AI-TDD: human-defined/reviewed test before AI implementation | partial | Tests were written first and failed for the right reason. The owner waived reviewing them before implementation for MVP-001 phase 2 — exception EX-002. |

**Project interpretation:** coverage floor — [`interpretations.md#1-coverage-floor-d1`](interpretations.md#1-coverage-floor-d1);
test strategy — [`interpretations.md#4-test-strategy-d1`](interpretations.md#4-test-strategy-d1).

**External dependency:** none. **Follow-up plan:** none needed.
**Gap-register rows:** `GAP-D1-AITDD`

---

### `D2` — `Kodgranskning`

Methodology chapter: [`kodgranskning`](../methodology/d-kvalitetssakring/kodgranskning.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `partially met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | PR mandatory for protected branches, enforced technically | met | Ruleset "Protect main", no bypass. |
| 2 | At least one non-author human approves | **not met** | Single maintainer; required approvals is 0 — exception EX-001. |
| 3 | Approval routed to the right expert (CODEOWNERS) | not met | Single maintainer — part of EX-001. |
| 4 | Earlier approval dismissed on new commits | met | Configured in the ruleset. Moot while approvals are 0. |
| 5 | Review bar: improves code health, not perfection | met (process) | |

**Undantag:** the chapter allows only postponing review in an incident, never dropping
it. EX-001 is therefore a forced-by-circumstance exception, not an Undantag.

**External dependency:** none — a second reviewer is the only fix.
**Follow-up plan:** when a second reviewer joins, see `docs/development/repo-settings.md` §3.
**Gap-register rows:** `GAP-D2-REVIEW`

---

### `D3` — `Definition of Done`

Methodology chapter: [`definition-of-done`](../methodology/d-kvalitetssakring/definition-of-done.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `partially met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Code quality and standard | met | Ruff check. |
| 2 | Tests, coverage floor, no unmanaged flaky tests | met | |
| 3 | PR approved by another human, linked to a work item | not met | EX-001. The link to a work item (MVP) is by convention only. |
| 4 | SAST and dependency scanning, no open critical findings | met | |
| 5 | No secrets in code or history | met | |
| 6 | Backward-compatible migrations | n/a | No database. |
| 7 | Documentation updated in the same PR | met | |
| 8 | Operable (logging, metrics) | partial | Logging to stderr; no metrics (see E4). |
| 9 | CI green | met | Required checks. |
| 10 | AI-assisted code meets F1/F2 | partial | See the F-area gaps. |
| 11 | Production deployment linked to a change request | n/a | Nothing is deployed; the core runs locally. |

The PR template's DoD checklist mirrors this chapter.

**Gap-register rows:** `GAP-D2-REVIEW`, `GAP-E1-WORKITEM` (see those areas).
