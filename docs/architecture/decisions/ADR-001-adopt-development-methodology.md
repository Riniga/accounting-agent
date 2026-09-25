# ADR-001: Follow the development methodology, with single-maintainer exceptions documented

**Status:** Accepted
**Date:** 2026-09-25

## Context

The repository was initialised from a project template that ships a complete development
methodology in [`docs/methodology/`](../../methodology/index.md) (21 chapters, areas A–F:
developer environment, writing code, security, quality assurance, delivery, AI
collaboration) and a compliance area in
[`docs/methodology-compliance/`](../../methodology-compliance/README.md).

The methodology was written for a large organisation. This project is a small, public
repository with one person holding every role — product owner, technical owner, developer,
security contact and reviewer. It handles financial software for non-profit organisations,
and most of its code will be written with AI assistance (Claude Code). Quality gates that
catch errors and leaked secrets therefore matter even though there is no organisational
mandate to follow the methodology.

## Decision

The project follows the development methodology voluntarily and tracks its compliance in
`docs/methodology-compliance/`. The methodology text is kept in the repository and
genericised — references to the organisation it originated from are replaced with neutral
wording, without changing any requirement (SKA/BÖR) in substance.

Requirements that cannot be met because there is a single maintainer — above all a
non-author human review of every pull request — are recorded as time-boxed exceptions in
[`exceptions.md`](../../methodology-compliance/exceptions.md) and as open rows in the gap
register, never silently dropped.

## Consequences

**Benefits:**

- Quality and security gates (lint, tests, secret scanning, dependency scanning, SAST) exist
  before AI tools start writing production code.
- A clear, written process that others (for example other associations reusing the code)
  can follow and trust.
- Gaps are visible rather than implicit.

**Trade-offs:**

- Process overhead that is large relative to a one-person project; parts of the methodology
  (central security functions, identity management, change requests) have no counterpart
  here and will show up as "not applicable" or external-dependency rows.
- The core review guarantee (a second human reads every change) is not met. Branch
  protection with required CI partly compensates, but does not replace it.
- Genericising the methodology means it drifts from its upstream source; future upstream
  changes have to be ported by hand.

## Alternatives considered

- **No formal methodology, just a few project rules**: rejected — the owner explicitly wants
  to stay compliant, and the template's gates are already written.
- **Keep the methodology verbatim, including the originating organisation's name**:
  rejected — the repository is public and not owned by that organisation; its name would
  imply an affiliation that does not exist.
