# Coding Standard

This is the primary development guideline for coding conventions used across the workspace.

Correctness is mandatory. Clarity, structure, and maintainability take priority over speed and cleverness.
Unnecessary complexity is never acceptable.

> **Relation to the development methodology.** This standard is this project's concrete,
> day-to-day elaboration of methodology area **B (Skriva kod)** — chiefly
> [B1 – Kodkvalitet & clean code](../methodology/b-skriva-kod/kodkvalitet-och-clean-code.md),
> [B2 – Kodstandard & stil](../methodology/b-skriva-kod/kodstandard-och-stil.md) and
> [C1 – Secure coding-principer](../methodology/c-sakerhet/secure-coding-principer.md).
> Where this file is stricter or more specific, follow it; where the two differ on
> principle, the methodology governs. The platform's standing against B/C and the
> project-level choices (formatter, complexity thresholds) are in
> [`docs/methodology-compliance/`](../methodology-compliance/).

## Language

- English for all code: variable names, function names, class names, comments, documentation, and commit messages.

## Naming

- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Files: `snake_case.py`
- Constants: `UPPER_SNAKE_CASE`

## Core Principles

- Follow the **SOLID** principles whenever they improve maintainability (methodology B1
  SKA 2 / BÖR 3 — apply them for a real, current need, not speculatively):
  - **S** – Single Responsibility: one class, one module, one function, one purpose.
  - **O** – Open/Closed: extend existing code rather than modifying stable behavior.
  - **L** – Liskov Substitution: derived implementations must behave as their base contracts.
  - **I** – Interface Segregation: prefer small, focused interfaces over large, general ones.
  - **D** – Dependency Inversion: depend on abstractions, not concrete implementations.
- Prefer simple, readable and maintainable code over clever solutions.
- Separate logic that can be independently understood, tested or reused.
- Eliminate duplication only when it is real, recurring and improves maintainability.
- Write unit tests for reusable logic and non-trivial business rules.
- Do not introduce abstractions or complexity before they are needed.
- Refactor opportunistically: leave the code cleaner than you found it.
- Every public class and function must include a concise docstring.
- Write comments to explain **why**, never **what** the code does.
- Do not leave `TODO` comments without a corresponding MVP or implementation plan.

## Typing

- Type hints are required for all function signatures.
- Use `T | None` instead of `Optional[T]` where appropriate.
- Always declare a return type, including `-> None`.

## Imports

- Import order: standard library → third-party → local modules.
- Remove unused imports.

## Error Handling

- Never use `except: pass` or silently ignore exceptions.
- Log unexpected exceptions with sufficient context.
- Protect all division operations against zero denominators.
- Domain-specific errors should be implemented as custom exception classes.

## Project Structure

Each domain should follow a consistent structure where applicable:

```text
<domain>/
    service.py
    repository.py
    schemas.py
    exceptions.py
```

- Business logic belongs in `service.py`.
- Data access belongs in `repository.py`.

## Security

- Never log passwords, API keys, tokens, cookies, or secrets.
- Validate and authorize all external requests.
- Protect all state-changing web endpoints against CSRF where applicable.
- Have a basic working knowledge of the OWASP Top 10 (2025) and CWE Top 25 categories
  relevant to Python web/CLI code (methodology
  [C1](../methodology/c-sakerhet/secure-coding-principer.md) SKA 1). Automated SAST and a lightweight
  threat-modelling step are recommended once tooling is added — see
  `docs/standards/threat-modeling.md`.

## Complexity

- **Cyclomatic complexity** is gated by Ruff: `mccabe.max-complexity = 20` blocks a pull
  request (the `Ruff` CI check and the pre-commit hook). The advisory value is **10** —
  a function at or above it should be reviewed for extraction, but nothing fails.
  **Cognitive complexity is advisory-only** — no clean tooling yet; revisit when it exists
  (methodology [B1](../methodology/b-skriva-kod/kodkvalitet-och-clean-code.md) BÖR 2,
  record the chosen thresholds in [`interpretations.md`](../methodology-compliance/interpretations.md)).
- A pre-existing function may carry a `# noqa: C901` with a one-line reason where a safe
  refactor is out of scope for the current change (methodology B1 "Undantag").

## Formatting

- Formatting is mechanical and tool-enforced, never a review discussion. `.editorconfig` at
  the repo root sets the baseline; **Ruff** is the designated formatter and linter
  (record the tool choice as an ADR; methodology
  [B2](../methodology/b-skriva-kod/kodstandard-och-stil.md);
  record the decision in [`interpretations.md`](../methodology-compliance/interpretations.md)).
  Config: root `pyproject.toml` `[tool.ruff]`. Enforced by the pre-commit hook
  (`pre-commit install`) and the `Ruff` CI check. Run `ruff format .` and `ruff check --fix .`
  locally.

## Dependencies

- Manage dependencies through `pyproject.toml`.
- Pin compatible version ranges in `pyproject.toml`/`requirements.in`; the actual installed
  versions are hash-locked in `requirements-lock.txt` (`pip-compile`) — see
  [`docs/standards/dependencies.md`](dependencies.md) for the update process, SBOM, SCA, and
  licence-scanning rules (methodology [C2](../methodology/c-sakerhet/beroendehantering-paketkallor-och-signering.md)).
- Document significant new dependencies in an ADR.

## Testing

- New functionality should include automated tests.
- Bug fixes should include a regression test whenever practical.

## General Principles

- Keep functions small and focused.
- Prefer composition over duplication.
- Favor readability over cleverness.
- Refactor before complexity grows.
- Leave the codebase cleaner than you found it.
