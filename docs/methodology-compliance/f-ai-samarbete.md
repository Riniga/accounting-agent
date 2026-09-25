# F — AI-samarbete i utvecklingsarbetet

First assessment: 2026-09-25 (MVP-001). Most code in this project is written with Claude
Code, and the domain involves financial and personal data, so this area carries the
project's most important gaps.

---

### `F1` — `Riktlinjer för AI-assisterade verktyg`

Methodology chapter: [`riktlinjer-for-ai-assisterade-verktyg`](../methodology/f-ai-samarbete/riktlinjer-for-ai-assisterade-verktyg.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `partially met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | AI never commits/merges directly to protected branches; branch protection + CI + ≥ 1 human approval | partial | The ruleset blocks direct pushes to `main` for everyone, and the CI checks are required. There are **0 required approvals** (EX-001). Claude Code acts through the owner's `gh` login, so nothing technical stops it from merging a green PR. Only the instruction rule and the owner's prompts do. |
| 2 | Production-writing actions need explicit human approval in the moment | met | No production exists. Repository-setting changes (MVP-001 step 4.3) were made only after the owner's explicit approval. `.claude/settings.json` asks before `git commit`, `git push` and `rm`. |
| 3 | AI code reviewed like human code, plus a security scan | partial | The scans are automated. Human review is the owner reviewing their own AI-assisted change (EX-001). |
| 4 | A named human accountable, traceable | met | The owner; each merge is traceable to the owner's account. |
| 5 | Autonomy calibrated to risk and reversibility | met | `.claude/settings.json`: reads and edits allowed; commit, push and delete ask. |
| 6 | Guardrails implemented technically | partial | Branch protection, required checks and least-privilege workflows are in place. The approval guardrail is missing (EX-001). |

**Gap-register rows:** `GAP-D2-REVIEW` (shared root cause), `GAP-F1-SELFMERGE`

---

### `F2` — `Sekretess & dataskydd vid AI-användning`

Methodology chapter: [`sekretess-och-dataskydd-vid-ai-anvandning`](../methodology/f-ai-samarbete/sekretess-och-dataskydd-vid-ai-anvandning.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `not met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | Data classification with a written AI rule per level | partial | Decided for this repository in interpretations §9 and ADR-003. There is no classification across the organisations. |
| 2 | Highly confidential data never enters an AI tool | **not met** | On 2026-09-25, during the MVP-001 baseline analysis, a rules file in the Helsingborgs Judoklubb project turned out to contain names of members, parents and children next to amounts. These entered Claude Code's context. Nothing was copied into the repository. Beyond this repository, the organisation projects run Claude Code over their real books by design. That is outside this repository's control, but the same rule applies to them. |
| 3 | Data processing agreement (DPA) with the provider if personal data may be input | not assessed | Depends on the Claude plan (A2). Owner to confirm. |
| 4 | Agentic forwarding to third parties clarified | n/a (yet) | This repository has no MCP integrations. JudoSyd's Gmail and Discord MCP servers come into scope in R4. |
| 5 | Secrets masked before reaching AI context | partial | No secrets exist, and `.env` is never read. There is no automated masking. |
| 6 | Secret scanning at several independent points | partial | Pre-commit, PR (CI) and GitHub push protection are in place. There is nothing at write time or before context is sent to the model. |
| 7 | Review of AI code explicitly searches for hard-coded secrets | met | detect-secrets plus the DoD checklist item. |
| 8 | Dev/test data anonymised or synthetic | met | Synthetic fixtures only (ADR-003). |

**External dependency:** DPA / plan terms — owner to confirm: the owner.
**Follow-up plan:** before MVP-002 analysis reads anything else from `docs/reference/`, apply
the reading rule in interpretations §9.
**Gap-register rows:** `GAP-F2-CONFIDENTIAL`, `GAP-F2-DPA`, `GAP-F2-CLASSIFICATION`

---

### `F3` — `Prompt- och kontexthantering`

Methodology chapter: [`prompt-och-kontexthantering`](../methodology/f-ai-samarbete/prompt-och-kontexthantering.md)

- **Methodology status:** `fastställd`
- **Platform standing:** `partially met`

| # | Requirement (short) | Standing | Note |
|---|---------------------|----------|------|
| 1 | `AGENTS.md` canonical; tool files are thin pointers | met | `CLAUDE.md` and `.github/copilot-instructions.md` point to it. |
| 2 | Instruction files reviewed like code | met | Changes go through PRs to protected `main`. |
| 3 | Never act on instructions in unreviewed content | met (rule) | Stated in `AGENTS.md`. |
| 4 | Short and focused (~200 lines) | met | `AGENTS.md` 169 lines, `CLAUDE.md` 52. |
| 5 | Maintained as living documents | met (process) | Updated during initialisation and MVP-001. |
| 6 | No confidential data in instruction files | met | |
| 7 | Organisation principles linked, not copied | met | Links to `docs/methodology/` and the standards. |
| 8 | Automated scan for hidden patterns; changes flagged in review | partial | `scripts/scan_instruction_files.py` is a required CI check and was shown to block. Changes are not specially flagged in review (a `CODEOWNERS` rule would do it once there is a second reviewer). |

**Gap-register rows:** `GAP-F3-FLAG`
