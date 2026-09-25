<!--
  Pull request template.
  The Definition of Done below mirrors the development methodology, chapter D3.
  Items marked (once wired up) describe a gate this checklist expects to exist once the
  corresponding CI check is added — until then they're a manual habit, not yet enforced.
  Track what's automated vs. manual in docs/methodology-compliance/gap-register.md.
-->

## Purpose

<!-- What does this change do, and why? One short paragraph. -->

## Linked work item / MVP / plan

<!-- e.g. MVP-004, docs/plans/004-short-slug.plan.md, or an Azure DevOps / GitHub work item id. -->
-

## AI assistance

- [ ] An AI tool (Claude Code / GitHub Copilot / other) contributed to this change
  - Tool(s): <!-- name them -->
- [ ] No AI tool was used

## Definition of Done

<!-- Tick each item, or strike it through with a one-line reason if genuinely N/A. -->

- [ ] **Code quality & standard** — `Ruff` check green (format + lint + complexity)
  ([B1](../docs/methodology/b-skriva-kod/kodkvalitet-och-clean-code.md),
  [B2](../docs/methodology/b-skriva-kod/kodstandard-och-stil.md))
- [ ] **Tests** — added/updated for the change; a regression test for any bug fix; coverage
  floor held ([D1](../docs/methodology/d-kvalitetssakring/testning.md))
- [ ] **AI-written production code was test-driven** — a human-defined/reviewed test existed
  before the implementation ([D1](../docs/methodology/d-kvalitetssakring/testning.md) SKA 5)
  *(N/A if no AI-written production code)*
- [ ] **Review** — this PR will be approved by at least one non-author human and is linked
  to a work item ([D2](../docs/methodology/d-kvalitetssakring/kodgranskning.md),
  [E1](../docs/methodology/e-leverans/versionshantering-och-branchstrategi.md))
- [ ] **Security checks** — the `SAST` and `Dependencies` CI checks are green, no
  unaddressed findings ([C1](../docs/methodology/c-sakerhet/secure-coding-principer.md),
  [C2](../docs/methodology/c-sakerhet/beroendehantering-paketkallor-och-signering.md))
  *(SAST is Semgrep — see `docs/methodology-compliance/interpretations.md` §2)*
- [ ] **Threat model (STRIDE)** — if this change has significant security impact (new
  auth/authz, a new external-facing surface, a new sensitive-data flow, a changed trust
  boundary), the plan's "Risks / open questions" includes a STRIDE pass
  ([C1](../docs/methodology/c-sakerhet/secure-coding-principer.md) SKA 4,
  [`docs/standards/threat-modeling.md`](../docs/standards/threat-modeling.md))
  *(N/A for most changes — a judgement call, not automated)*
- [ ] **No secrets** in the code or its history; searched AI-generated code for hardcoded
  secrets ([C4](../docs/methodology/c-sakerhet/hantering-av-hemligheter.md),
  [F2](../docs/methodology/f-ai-samarbete/sekretess-och-dataskydd-vid-ai-anvandning.md))
- [ ] **Database migrations** (if any) are backward-compatible with the running version
  ([B4](../docs/methodology/b-skriva-kod/datamodellering-och-databasdesign.md))
  *(N/A if no database)*
- [ ] **Documentation** — README / ADR / architecture docs updated **in this PR**
  ([B5](../docs/methodology/b-skriva-kod/dokumentation-av-kod.md))
- [ ] **Operability** — new functionality exposes the logging / metrics it needs to be run
  and diagnosed ([E4](../docs/methodology/e-leverans/observability.md))
- [ ] **CI is green** ([E2](../docs/methodology/e-leverans/ci-cd-och-automatisering.md))
- [ ] **AI action rules met** — no direct commit/merge to `main`; production-writing actions
  had explicit human approval
  ([F1](../docs/methodology/f-ai-samarbete/riktlinjer-for-ai-assisterade-verktyg.md))
  *(N/A if no AI assistance)*
- [ ] **Production deployment** (if this ships) is linked to an approved change request per
  the organisation's deployment process
  ([D3](../docs/methodology/d-kvalitetssakring/definition-of-done.md) SKA 11)

## Notes for the reviewer

<!-- Anything that needs context: a deliberate deviation, a follow-up left for later, a risk. -->
