# A — Grundförutsättningar

First assessment: 2026-09-25 (MVP-001). Context: a public repository with a single
maintainer, developed on a personal computer, with no organisation behind it. Many A
requirements assume a central IT function; where none exists, this is stated rather than
counted as met.

---

### `A1` — `Utvecklingsmiljö & verktyg`

Methodology chapter: [`utvecklingsmiljo-och-verktyg`](../methodology/a-grundforutsattningar/utvecklingsmiljo-och-verktyg.md)

- **Methodology status:** `utkast` (pending: IT security/IAM verification of two points)
- **Platform standing:** `partially met`

**SKA points**

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Isolated, managed, traceable workstation | not met | Personal Windows computer, not centrally managed. The same machine holds the organisation projects' real data (`docs/reference/`, git-ignored). |
| 2 | Identity-based network access (ZTNA) | n/a | No organisation network or resources to protect. |
| 3 | Admin identity per the Enterprise Access model | n/a | No separate admin identity environment. |
| 4 | Least privilege, just-in-time elevation | not assessed | Owner to confirm whether day-to-day work runs as a local administrator. |
| 5 | Project environment declarative and versioned | met | `environment.yml` + hash-locked `requirements-lock.txt`, verified from scratch in MVP-001. |
| 6 | Base image from a shared, maintained image | n/a | No organisation base image. |
| 7 | Application control on the workstation | not met | Personal computer; no allow-listing. |

**BÖR points we adopt:** none yet.

**Project interpretation:** none — chapter leaves no open choice.

**External dependency:** none — there is no organisation IT function to depend on; the
gaps are owner decisions.

**Follow-up plan:** none needed now.

**Gap-register rows:** `GAP-A1-WORKSTATION`, `GAP-A1-PRIVILEGE`

---

### `A2` — `Verktyg för AI-assisterad utveckling`

Methodology chapter: [`verktyg-for-ai-assisterad-utveckling`](../methodology/a-grundforutsattningar/verktyg-for-ai-assisterad-utveckling.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `partially met`

**SKA points**

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Only via an organisation (business/enterprise) agreement | not assessed | Owner to confirm which Claude plan is used. |
| 2 | Agreement guarantees no training on inputs + short retention | not assessed | Depends on the plan and its settings. |
| 3 | Approved through the organisation's tool-approval process | n/a | No such process; the owner approves tools, recorded in `docs/development/tools.md`. |
| 4 | Up-to-date list of approved AI tools | met | `docs/development/tools.md`: Claude Code (primary), GitHub Copilot (optional). |
| 5 | Access through organisation SSO | n/a | Single person, no identity provider. |
| 6 | Tool can be technically restricted to branches/PRs | met | The ruleset on `main` has an empty bypass list; Claude Code works through branches and PRs. See F1 for the remaining gap (0 approvals). |

**BÖR points we adopt:** review MCP integrations separately (BÖR 1) — relevant when R3/R4
add Gmail and Discord MCP servers.

**Project interpretation:** none — chapter leaves no open choice.

**External dependency:** none.

**Follow-up plan:** none needed now.

**Gap-register rows:** `GAP-A2-AGREEMENT`
