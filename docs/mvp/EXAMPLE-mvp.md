# MVP-EXAMPLE – Test methodology (worked example)

> This is a genericised worked example from the project this reference kit was drawn from,
> kept to show what a good MVP + plan pair (see `EXAMPLE-plan.md` alongside it) and an
> honest "Outcome at close" actually look like. Delete both once you have real ones.

## Purpose

Put the project's test-quality guarantees in place: a coverage floor that's actually
enforced, a policy for flaky tests, and a rule for how AI-written code gets tested — not
because a document somewhere says to, but because none of the three existed yet and each
had already caused a real problem (an untested regression, a flaky test nobody owned, an
AI-written function with no test at all).

## Goals

- Coverage can't silently regress — a real, measured floor, enforced in CI, that may only
  be raised deliberately.
- A flaky test gets quarantined with an owner and a deadline, not left failing CI
  intermittently or silently deleted.
- When an AI tool writes production code, a human-defined or human-reviewed test exists
  first.

## Context

No coverage measurement existed in CI at all — it ran tests, but nothing checked how much
of the code they actually exercised. No flaky-test policy existed. No AI-TDD rule was
written down anywhere, even though it was already being practised informally.

## Scope

Coverage floor + ratchet, wired into the existing CI test job. A `quarantine` test marker
with a documented owner/deadline convention. The AI-TDD rule written into the project's
instruction files and testing standard.

## Out of Scope

Writing new tests to *raise* coverage toward some higher target — that's ongoing work, not
this MVP. Mutation testing. A retry plugin for flaky tests (the retry *cap* is documented;
actually adding a plugin is a follow-up if flakiness shows up in practice).

## Acceptance Criteria

- CI fails if coverage drops below a floor recorded in the repo config.
- The floor reflects a real, measured baseline — not a guessed placeholder.
- A documented process exists for quarantining a flaky test.
- The AI-TDD rule is written into the project's instruction files.

## Outcome at close (2026-09-15)

Closed as **delivered**, against the criteria above:

- Coverage floor: **met**, but not at the number originally planned. The plan assumed
  "start at the methodology's suggested 50%, raise later" — before implementing, a real
  measurement showed the codebase was already at 78% coverage. A 50% floor would never
  have functioned as a ratchet (coverage would need to regress 28 points to ever trigger
  it), so the floor was set to 70% instead — just below the real baseline, not the
  originally planned placeholder. **This is the actual lesson this example is here to
  show: measure before you commit a number to a plan, even when the methodology suggests
  a specific starting value.**
- Flaky-test quarantine: **met** — a marker, a policy, and CI wiring that runs quarantined
  tests non-blocking rather than skipping them silently (so they stay visible).
- AI-TDD rule: **met** — written into the instruction files and the testing standard, with
  a cross-reference from the AI action rules so it's found from either direction.
