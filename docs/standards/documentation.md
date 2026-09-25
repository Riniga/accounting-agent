# Documentation Standard

> **Relation to Skanskas utvecklingsmetodik.** This standard is this project's elaboration
> of methodology [B5 – Dokumentation av kod](../methodology/b-skriva-kod/dokumentation-av-kod.md).
> Adopted from B5: every repo README states its purpose, runnable install/run/test commands,
> and an ownership/status line (B5 SKA 1); documentation is updated in the **same** pull
> request as the change (B5 SKA 2 — already the rule below); ADRs use the Nygard format and
> an approved ADR is superseded, never edited (B5 SKA 3–4, see the ADR section below).
> Automated validation of runnable examples (B5 SKA 5) is a recommended follow-up once the tooling exists.

## Language

All workspace documentation is written in English.

File names and folder names use English and `kebab-case`.

Business source data may be kept in its original language when needed.

## Format

All documentation files use Markdown (`.md`).

## File and folder naming

```text
kebab-case-file-name.md
kebab-case-folder-name/
```

## Length and tone

Keep documentation short and practical. Avoid long theoretical text.

Write for a reader who wants to understand quickly and move on to doing.

## What documentation explains

Documentation explains **why** and **what**:

- Why a decision was made
- What a component does or is for
- What is needed to use or run something

Source code explains **how**.

Do not duplicate in documentation what is already clear from reading the code.

## When to update documentation

Update documentation in the same pull request as the change it describes.

Do not defer documentation to a later pull request.

Changes that require documentation updates:

- Architecture or workspace structure changes
- New or changed development setup steps
- New tools or dependencies
- Changes to coding, testing, or Git standards
- Significant new functionality that is not self-evident from the code

## What not to document

Do not write documentation for:

- Implementation details that are clear from reading the code
- Every function or class (docstrings in code handle this)
- Decisions that have no lasting impact
- Temporary or experimental work

## Architecture Decision Records

Significant architectural decisions are recorded as ADRs in `docs/architecture/decisions/`,
numbered (`ADR-001-...md`, `ADR-002-...md`, …). Each ADR uses the **Nygard format**:

- **Title** — short, descriptive.
- **Status** — proposed, accepted, or superseded by a later ADR.
- **Context** — the situation or problem that required a decision.
- **Decision** — what was decided.
- **Consequences** — the results, positive and negative.

An **accepted ADR is never edited afterwards.** If the decision changes, write a new ADR
that supersedes the old one, with a link between them. The history is itself the
documentation.

Create an ADR for: a new significant dependency, a new external integration, a major folder
structure change, a data-format change, or an authentication/authorization change.

## Document types

| Type | Location | Purpose |
|------|----------|---------|
| Architecture overview | `docs/architecture/overview.md` | System structure and key dependencies |
| ADR | `docs/architecture/decisions/` | Record of significant architectural decisions (Nygard format; superseded, never edited) |
| Vision | `docs/vision.md` | Long-term purpose and principles |
| Roadmap | `docs/roadmap/` | Direction and planned work |
| MVP | `docs/mvp/` | Scoped delivery increments |
| Implementation plan | `docs/plans/` | Step-by-step implementation guide |
| Development setup | `docs/development/` | Environment, tools, and workflow |
| Standards | `docs/standards/` | Coding, testing, Git, and documentation conventions |
