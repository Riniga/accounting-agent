# Current Architecture State

Short reference for the current state of the workspace. For full context see
[`overview.md`](overview.md). Keep this current — it's the quick-scan version; update it
in the same PR as any change to an app's status, test count, or key capabilities.

## Applications

| App | Status | Tests | Key capabilities |
|-----|--------|-------|-------------------|
| `<app-1>` | *(Planned / In progress / Implemented)* | *(count)* | *(a terse, comma-separated list — not prose)* |

## Shared package — \<shared-package-name\>

<!-- What's actually in it, and why it earned the "reused by ≥2 apps" bar — link the ADR
     that recorded that boundary decision. -->

## Conventions

<!-- Point at docs/standards/*.md rather than restating them; note anything genuinely
     unusual or project-specific here. -->

## Dependencies

<!-- A short table or list of the notable runtime dependencies and why each is there — not
     a dump of requirements.in. -->

## Test counts

<!-- Aggregate test counts per app/package, kept current — a quick "is this still tested"
     signal for anyone (human or AI) about to touch a given area. -->

## Methodology compliance

See [`docs/methodology-compliance/`](../methodology-compliance/) — this section is a
one-line pointer, not a duplicate of the gap register.
