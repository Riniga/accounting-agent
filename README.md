# <Project Name>

<!-- One or two sentences: what this workspace is for. -->

The workspace is designed to grow over time by adding independent applications that share
a common architecture, development process, coding standards, and reusable components.

## Vision

<!-- One sentence: the outcome this project exists to create. See docs/vision.md for the
     full version. -->

## Workspace Structure

```text
apps/
    <app-1>/           <what it does>
    <app-2>/           <what it does>

packages/
    <shared-package>/  Shared libraries and reusable components

docs/
    Architecture, development process, standards, roadmap, MVPs and implementation plans
```

> **Note**
>
> The workspace is currently being established. Additional applications, shared packages
> and documentation will be introduced incrementally as the project evolves.

## Development Process

Every change follows the same lightweight process:

```text
Roadmap
    ↓
MVP
    ↓
Implementation Plan
    ↓
Implementation
    ↓
Test
    ↓
Pull Request
```

See [`docs/development/methodology.md`](docs/development/methodology.md) for the full
process, and [`AGENTS.md`](AGENTS.md) for how AI tools work within it.

## Getting Started

1. Read [`AGENTS.md`](AGENTS.md) — the canonical instruction file for how work happens
   here (human or AI).
2. Follow [`docs/development/setup.md`](docs/development/setup.md) and
   [`environment.md`](docs/development/environment.md) to set up your local environment.
3. Read [`docs/standards/`](docs/standards/) — coding, testing, git, documentation,
   dependencies.
4. If starting a brand-new project from this template, put the project idea in
   `docs/initial-idea.md` and run
   [`docs/claude-prompts/initialize-project.md`](docs/claude-prompts/initialize-project.md).

## Required GitHub Actions secrets

<!-- List whatever your CI/CD workflows actually need, e.g.: -->

| Secret | Purpose |
|--------|---------|
| `<SECRET_NAME>` | <what it's for> |

## Documentation

| Area | Location |
|------|----------|
| Architecture | [`docs/architecture/`](docs/architecture/) |
| Development process | [`docs/development/methodology.md`](docs/development/methodology.md) |
| Standards | [`docs/standards/`](docs/standards/) |
| Organisation methodology | [`docs/methodology/`](docs/methodology/) |
| Methodology compliance (internal) | [`docs/methodology-compliance/`](docs/methodology-compliance/) |
| Roadmap | [`docs/roadmap.md`](docs/roadmap.md) |
| MVPs | [`docs/mvp/`](docs/mvp/) |
| Implementation plans | [`docs/plans/`](docs/plans/) |
