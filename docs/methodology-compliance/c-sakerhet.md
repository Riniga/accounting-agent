# C — Säkerhet

First assessment: 2026-09-25 (MVP-001).

---

### `C1` — `Secure coding-principer`

Methodology chapter: [`secure-coding-principer`](../methodology/c-sakerhet/secure-coding-principer.md)

- **Methodology status:** `utkast` (pending: security architect review)
- **Platform standing:** `met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Working knowledge of OWASP Top 10 / CWE Top 25 | met (self-assessed) | Owner's own assessment; there is no training record. |
| 2 | SAST on every PR, blocking | met | Semgrep, required check `SAST`. Shown to block three insecure patterns in MVP-001 step 4.2. |
| 3 | DAST against staging before production | n/a | No external interface and no deployment. The template's manual `dast.yml` is proposed for removal. |
| 4 | Lightweight threat modelling for security-relevant changes | met (process) | The plan template requires a STRIDE pass. None was needed for MVP-001. Expected in R3 (agent tools) and R4 (e-mail, Discord). |

**Project interpretation:** SAST tool — [`interpretations.md#2-sast-tool-c1`](interpretations.md#2-sast-tool-c1).

**External dependency:** none. **Follow-up plan:** none needed. **Gap-register rows:** none.

---

### `C2` — `Beroendehantering, paketkällor & signering`

Methodology chapter: [`beroendehantering-paketkallor-och-signering`](../methodology/c-sakerhet/beroendehantering-paketkallor-och-signering.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `partially met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | SBOM generated automatically in build/delivery | not met | No build or release pipeline yet. GitHub's dependency graph can export an SPDX SBOM on demand. Automate it when releases exist. |
| 2 | Automatic SCA in the pipeline, reachability as a selection criterion | partial | `pip-audit` on every PR plus Dependabot alerts on `main`. Neither does reachability analysis. |
| 3 | Dependencies locked to verifiable versions | met | `requirements-lock.txt` with hashes, and a CI drift check. |
| 4 | Automated licence scan plus a documented exception process | partial | The scan runs in CI against an allowlist. The exception process refers to an organisation legal function that doesn't exist; the owner decides. |
| 5 | Automated, recurring dependency updates | met | `.github/dependabot.yml`, weekly, for pip and GitHub Actions. |

Also noted: GitHub Actions are pinned to version tags, not commit SHAs.

**Project interpretation:** [`interpretations.md#5-dependency-tooling-c2`](interpretations.md#5-dependency-tooling-c2).

**External dependency:** none.
**Follow-up plan:** none scheduled — see gap rows.
**Gap-register rows:** `GAP-C2-SBOM`, `GAP-C2-REACHABILITY`, `GAP-C2-SHAPIN`, `GAP-C2-DEPENDABOT-LOCK`

---

### `C3` — `Sårbarhetshantering, patchning & CVD`

Methodology chapter: [`sarbarhetshantering-patchning-och-cvd`](../methodology/c-sakerhet/sarbarhetshantering-patchning-och-cvd.md)

- **Methodology status:** `utkast` (pending: legally reviewed safe-harbor text)
- **Platform standing:** `partially met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Published CVD policy; contact via `security.txt` | partial | `SECURITY.md` plus GitHub private vulnerability reporting. `security.txt` is n/a — no website. |
| 2 | Safe-harbor language for good-faith researchers | not met | The methodology's own legally reviewed text is still pending. |
| 3 | Prioritise by CVSS, faster for actively exploited | not met | No written prioritisation or response times. |
| 4 | Severity integrated into service SLA/OLA | n/a | No service with an SLA. |
| 5 | SLA compliance measured | n/a | As above. |

**External dependency:** safe-harbor text from the methodology owner — owner to confirm:
methodology owner.
**Follow-up plan:** none scheduled.
**Gap-register rows:** `GAP-C3-SAFEHARBOR`, `GAP-C3-PRIORITY`

---

### `C4` — `Hantering av hemligheter`

Methodology chapter: [`hantering-av-hemligheter`](../methodology/c-sakerhet/hantering-av-hemligheter.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `met` (for the current scope: the project has no secrets)

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Never in code/config/history; dedicated secret manager | met / n/a | No secrets exist. `.env` is git-ignored, and detect-secrets runs in pre-commit and CI, plus GitHub secret scanning with push protection. A secret manager becomes relevant when an API key appears (R3). |
| 2 | Identity federation instead of stored CI secrets | n/a | CI needs no secrets. |
| 3 | Least privilege for secret access | met | Workflow `permissions: contents: read`. |
| 4 | Exposed secret = compromised, rotate at once | met (process) | `docs/development/secrets-rotation.md`. |
| 5 | History cleanup only after rotation | met (process) | Same runbook. |

**Project interpretation:** [`interpretations.md#6-secret-scanning-layers-c4-f2`](interpretations.md#6-secret-scanning-layers-c4-f2).

**External dependency:** none. **Follow-up plan:** none needed. **Gap-register rows:** none.
