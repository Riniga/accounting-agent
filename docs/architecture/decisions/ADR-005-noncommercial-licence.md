# ADR-005: License the code under the PolyForm Noncommercial License 1.0.0

**Status:** Accepted
**Date:** 2026-09-25

## Context

The repository is public, and other associations may want to use the core for their own
bookkeeping. The owner's requirement: anyone may use the code for their own projects, but
not commercially — for example as the base of a product that is then distributed or sold.

A standard open-source licence (MIT, Apache-2.0, GPL) cannot express this: the Open Source
Definition does not allow restricting commercial use.

## Decision

The code is licensed under the **PolyForm Noncommercial License 1.0.0**. It permits use,
modification and distribution for any noncommercial purpose, including by charitable and
other non-profit organisations, and does not permit commercial use.

The licence text is added as `LICENSE` in MVP-001, copied verbatim from the official
PolyForm Project source rather than written from memory.

## Consequences

**Benefits:**

- Matches the owner's intent: free to reuse for associations and personal projects,
  protected against commercial exploitation.
- A published, standardised licence rather than a home-written one.

**Trade-offs:**

- The project is **source-available, not open source** in the OSI sense; some people and
  platforms will not treat it as open source, and it cannot be included in projects that
  require an OSI licence.
- Contributions from others are accepted under the same licence; there is no contributor
  agreement, so relicensing later would need every contributor's consent.
- The licence governs this code only; each third-party dependency keeps its own licence
  (checked by the licence scan in CI).

## Alternatives considered

- **MIT or Apache-2.0**: rejected — permit commercial use.
- **Creative Commons BY-NC**: rejected — Creative Commons advise against using their
  licences for software.
- **No licence (all rights reserved)**: rejected — nobody could legally reuse the code,
  which contradicts the goal of letting other associations use it.
