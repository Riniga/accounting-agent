# ADR-002: This repository is a single Python package — the core; organisation projects are separate repositories

**Status:** Accepted (the Python version, tool versions and how organisation projects
consume the core are deliberately left open — see below)
**Date:** 2026-09-25

## Context

The [initial idea](../../initial-idea.md) describes a shared core, `accounting-agent-core`,
that must not know about any specific organisation, plus one project per organisation
(JudoSyd, Helsingborgs Judoklubb, Aktivitet Förebygger) holding data, chart of accounts,
rules, instructions and configuration, with as little code of their own as possible. The
three existing projects are Python-based and run through Claude Code in VS Code. The idea
states that deterministic Python does file operations, bookkeeping, validation, calculations
and integrations.

The project template assumes a monorepo (`apps/<app>/` plus `packages/<shared>/`) and a
Python toolchain: Conda, pip-tools lock files, Ruff, pytest, Semgrep and detect-secrets on
GitHub Actions.

Nothing has been installed or measured yet; tool versions are verified in MVP-001's
investigation step rather than assumed here.

## Decision

This repository **is the core**. It holds one installable Python package — distribution
name `accounting-agent`, import name `accounting_agent`, console command `accounting-agent`
— in a `src/` layout, with tests under `tests/`. The organisation projects remain
**separate, private repositories** that consume the core; they are not part of this
repository.

The template's toolchain is kept: Conda + pip-tools, Ruff, pytest, pre-commit, GitHub
Actions for CI on pull requests (no CD). The Python version and every tool version are
chosen in MVP-001 as the newest version the whole toolchain supports, after verification.

The template's `apps/` + `packages/` layout is not used. Its rule that code moves to a
shared package only when reused by at least two apps has no direct counterpart here, because
the core *is* the product. The equivalent rule for this repository comes from the initial
idea: **functionality is extracted into the core only when there is a working, concrete
function in an organisation project to generalise.**

**Left open, to be decided in R3 with its own ADR:** how organisation projects consume the
core (installed Python package, scripts, an MCP server, or a combination) and how the agent
runs. The current expectation is that Claude Code acts as the agent inside each organisation
project, running locally with a scheduler.

## Consequences

**Benefits:**

- One small, conventional package that is easy to install, test and eventually publish.
- A hard physical boundary between shared code (public) and organisation data (private).
- The template's CI gates can be reused almost unchanged.

**Trade-offs:**

- Changes that span the core and an organisation project need two pull requests in two
  repositories, and a way to pin which core version each project uses.
- Conda is heavier than a plain virtual environment for a pure-Python package; kept for
  consistency with the template and the existing projects, and revisited in MVP-001.
- Deferring the consumption mechanism means early core APIs may need to change once it is
  decided.

## Alternatives considered

- **Monorepo containing the core and all organisation projects**: rejected — organisation
  data is private and must never be in this public repository (ADR-003).
- **Keep the template's `apps/` + `packages/` layout**: rejected — there is only one
  deliverable here; the extra level adds structure without a use.
- **A different language or stack**: rejected — the existing projects and the idea are
  Python-based, and extraction without rewriting is a core principle.
