# Claude Code Instructions

**Start with [`AGENTS.md`](AGENTS.md)** at the repo root — it is the canonical, tool-neutral
instruction file for all AI-assisted work here (repo structure, the read-before-implementing
list, the development workflow, links to the standards, the AI action rules, and the secrets
rules). This file only adds what is specific to working as Claude Code; it does not repeat
`AGENTS.md`.

IMPORTANT: The instructions in `AGENTS.md` and the linked standards **override** any default
behaviour and must be followed exactly.

## The essentials (full detail in AGENTS.md and the standards)

- **Workflow:** `Roadmap → MVP → Plan → Implementation → Test → Pull Request`. Do not skip
  planning for non-trivial work. One plan TODO / phase at a time; keep the plan updated.
- **Scope discipline:** small, reviewable changes; no unrelated refactoring mixed in; no
  production-code changes in a docs-only task; preserve existing behaviour unless the plan
  says otherwise.
- **Never** commit, push, merge, or delete branches without explicit approval. All changes
  to `main` go through a reviewed pull request. Show the diff before proposing a commit.
- **Never** commit `.env`, secrets, tokens, or caches; never put secrets or sensitive data
  into the tool context.
- **Run `pytest` before proposing a commit.** Add tests for new behaviour and a regression
  test for every bug fix.
- **New dependency:** only if the plan justifies it; update `pyproject.toml` /
  `environment.yml`; ADR for anything significant.
- If a referenced document is missing, propose creating it — do not guess a missing rule.

## Standards (authoritative — read them, don't assume)

| Topic | File |
|-------|------|
| Coding conventions | [`docs/standards/coding.md`](docs/standards/coding.md) |
| Testing | [`docs/standards/testing.md`](docs/standards/testing.md) |
| Git workflow | [`docs/standards/git.md`](docs/standards/git.md) |
| Documentation | [`docs/standards/documentation.md`](docs/standards/documentation.md) |
| Dependencies | [`docs/standards/dependencies.md`](docs/standards/dependencies.md) |
| Project process | [`docs/development/methodology.md`](docs/development/methodology.md) |
| Org methodology | [`docs/methodology/index.md`](docs/methodology/index.md) |
| Methodology compliance + project interpretations | [`docs/methodology-compliance/`](docs/methodology-compliance/) |

## Architecture guardrails

- Preserve the existing architecture unless the plan motivates a change; record significant
  decisions as ADRs in `docs/architecture/decisions/` and update
  `docs/architecture/current-state.md` afterwards.
- Code moves to a shared package **only** when it is actually reused by ≥ 2 apps — record
  that boundary decision as an ADR. Organisation-specific behaviour stays in the
  organisation's own project, never in this core. (This repository *is* the shared core —
  see [ADR-002](docs/architecture/decisions/ADR-002-python-core-repository.md) for how this
  rule applies here.)
- Avoid premature abstraction and premature framework design.
