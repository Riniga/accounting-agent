# Development Methodology

> **Scope of this document.** This is the lightweight **project process** — how work flows
> from Vision through Roadmap, MVP, Plan, Implementation and Pull Request. It is **not** the
> complete engineering standard. The organisation-wide engineering requirements are defined
> in **[the development methodology](../methodology/index.md)** (areas A–F: developer
> environment, writing code, security, quality assurance, delivery, AI collaboration), and
> this platform's standing against them — plus the project-level choices — is tracked in
> **[`docs/methodology-compliance/`](../methodology-compliance/)**. This document does not
> override the methodology; where this document is silent, the methodology applies.

## Purpose

This document defines the development process for this workspace.

The goal is to keep the process simple, useful and sustainable. Documentation should support thinking, planning and implementation — not become a burden.

The process is designed to work well with both human developers and AI coding assistants such as Claude Code and GitHub Copilot.

The methodology itself should evolve as the platform grows. Improvements should remain incremental and preserve the lightweight nature of the process.

---

## Core Idea

Development follows a lightweight document-driven flow:

```text
Vision
    ↓
Roadmap
    ↓
MVP
    ↓
Implementation Plan
    ↓
Plan Review
    ↓
Implementation
    ↓
MVP Review
    ↓
Pull Request
    ↓
Continuous Improvement
```

Each document type has a clear purpose.

| Document | Purpose                                   |
| -------- | ----------------------------------------- |
| Vision   | Defines the long-term direction           |
| Roadmap  | Describes where the project is going      |
| MVP      | Defines a valuable increment to build     |
| Plan     | Describes how the MVP will be implemented |
| Code     | Contains the actual implementation        |
| ADR      | Records important architectural decisions |

Implementation details should primarily live in the source code, not in duplicated documentation.

---

## Roles

Development is a collaboration between two complementary teams.

### Product Team

Responsible for deciding **what** should be built.

Responsibilities include:

* maintaining the Vision
* maintaining the Roadmap
* defining MVPs
* reviewing architecture
* reviewing implementation plans
* approving MVP completion

### Engineering Team

Responsible for deciding **how** the approved MVP is implemented.

Responsibilities include:

* creating implementation plans
* implementing approved plans
* keeping plans up to date during implementation
* testing and verifying changes
* preparing Pull Requests

AI assistants support both teams but do not replace human judgement.

---

## Directory Structure

```text
docs/
│
├── vision.md
├── roadmap.md
│
├── mvp/
│   └── README.md
│
├── plans/
│   └── README.md
│
├── architecture/
│   ├── overview.md
│   └── decisions/
│       └── README.md
│
├── development/
│   ├── setup.md
│   ├── environment.md
│   ├── tools.md
│   └── methodology.md
│
└── standards/
    ├── coding.md
    ├── git.md
    ├── testing.md
    └── documentation.md
```

Keep this structure small. Add new folders only when there is a clear and recurring need.

---

## Roadmap

The roadmap describes the major capabilities and milestones planned for the platform.

It bridges the gap between the long-term vision and the individual MVPs.

Location:

```text
docs/roadmap.md
```

The roadmap should be lightweight and easy to update.

---

## MVP

An MVP is a clear and valuable delivery increment.

An MVP should answer:

* Why are we building this?
* What value does it create?
* What is included?
* What is not included?
* What are the acceptance criteria?

Location:

```text
docs/mvp/
```

Suggested naming:

```text
MVP-001-short-name.md
MVP-002-short-name.md
```

An MVP should describe the desired outcome, not the detailed implementation.

---

## Implementation Plan

Before implementation starts, create an implementation plan.

The plan should answer:

* How will this be implemented?
* Which modules or files are likely affected?
* What are the implementation steps?
* How will the change be verified?
* Are there any risks or open questions?
* Does this change have significant security impact (new auth/authz, a new external-facing
  surface, a new sensitive-data flow, a changed trust boundary)? If so, include a short
  STRIDE pass in "Risks / open questions" — see
  [`docs/standards/threat-modeling.md`](../standards/threat-modeling.md).

Location:

```text
docs/plans/
```

Suggested naming:

```text
MVP-001.plan.md
MVP-002.plan.md
```

Plans should be practical and action-oriented.

A plan should be broken down into small numbered tasks that can be implemented one at a time.

Before implementation begins, the Product Team reviews the plan to ensure it aligns with the MVP, architecture and long-term direction.

---

## Implementation

Implementation should follow the approved plan.

General rules:

* Implement one plan item at a time.
* Keep changes small and reviewable.
* Update the plan when work is completed or when the approach changes.
* Run relevant tests before committing.
* Do not implement outside the agreed scope without updating the MVP or implementation plan.
* Every implementation should remain traceable to an MVP.

### Found during an MVP

Testing and reviewing an MVP turns up things outside its plan. They are handled on the
MVP's own branch rather than on separate fix branches:

* **Fixes and small changes** — even unrelated ones — are made on the MVP branch:
  * each one in its **own commit** with its own type (`fix:`, `docs:`, `chore:`), never
    mixed into a feature commit, so it can be reviewed and reverted on its own;
  * each recorded as one line in the plan's **"6. Found during this MVP"** (what and why);
  * listed in the pull request's "Notes for the reviewer";
  * a behaviour fix gets a regression test, and AI-written production code still follows
    AI-TDD ([`docs/standards/testing.md`](../standards/testing.md)).
* **Ideas** go to the "Backlog of ideas" in `docs/roadmap.md`, dated and marked with the
  MVP they came from. They are not implemented in the current MVP.
* **Large, risky or decision-worthy items** — a new dependency, an ADR, a security change,
  anything that would change the MVP's goal — become a backlog item or their own MVP. The
  owner decides.
* Keep the MVP short: collecting fixes must not keep a branch open for weeks
  (methodology E1 SKA 1).

The source code is the primary source of truth for how the system works.

---

## MVP Review

Before considering an MVP complete:

* All relevant plan items should be completed.
* Acceptance criteria should be verified.
* Tests should pass.
* Documentation should be updated if needed.
* Important decisions should be recorded as ADRs.
* The implementation should still align with the Vision, Roadmap and architecture.
* The implementation should be considered ready for Pull Request.

An MVP is complete only after both the Product Team and Engineering Team agree that it satisfies the intended outcome.

---

## Architecture

Architecture documentation should describe the system at a level that helps future development.

Recommended starting point:

```text
docs/architecture/overview.md
```

The overview should describe:

* system purpose
* main modules
* important data flows
* important dependencies
* workspace structure

Do not document every implementation detail in the architecture documentation.

---

## Architecture Decision Records

Architectural decisions are documented as ADRs.

Location:

```text
docs/architecture/decisions/
```

Create an ADR when a decision has long-term impact.

Examples:

* choosing a new framework
* changing the workspace structure
* introducing a new external service
* changing the data model
* changing the deployment approach
* adding an important dependency

Suggested naming:

```text
ADR-001-use-conda.md
ADR-002-workspace-structure.md
ADR-003-shared-package-structure.md
```

Small implementation decisions do not need ADRs.

---

## AI-Assisted Development Workflow

When using Claude Code or GitHub Copilot, follow this workflow:

1. Read the Vision.
2. Read the Roadmap.
3. Read the selected MVP.
4. Read relevant architecture and standards.
5. Create or update the implementation plan.
6. Review and approve the plan before implementation.
7. Implement one plan item at a time.
8. Run relevant tests.
9. Update the plan continuously.
10. Perform an MVP Review before creating a Pull Request.

The AI assistant may help create both MVP documents and implementation plans, but implementation should always follow an approved plan.

---

## Document Types We Avoid by Default

To keep the process simple, avoid adding separate document types unless there is a clear need.

Do not create separate documents for every:

* function
* requirement
* technical idea
* implementation detail
* minor design choice

Most of this should be covered by MVPs, plans, code and ADRs.

If a document is not actively used during development, it probably should not exist.

---

## Optional Idea Capture

If many ideas appear before they are ready for the roadmap, an ideas folder may be added later:

```text
docs/ideas/
```

Use this only if needed.

Ideas should eventually be refined into roadmap items or MVPs.

---

## Continuous Improvement

Each completed MVP is an opportunity to improve both the platform and the development process.

When appropriate:

* refine the Vision
* update the Roadmap
* improve this methodology
* improve standards and templates
* record new architectural decisions

The process should evolve incrementally in the same way as the platform itself.

---

## Guiding Principles

* Keep the process simple.
* Build one MVP at a time.
* Prefer working software over excessive documentation.
* Let Vision define direction.
* Let the Roadmap define priorities.
* Let MVPs define what to build.
* Let plans define how to build it.
* Let code define the implementation.
* Let ADRs explain important architectural decisions.
* Avoid duplicate documentation.
* Improve both the platform and the process continuously.
* Update documentation when it helps future development.
