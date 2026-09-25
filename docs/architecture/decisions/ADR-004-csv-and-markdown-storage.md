# ADR-004: Books are stored as CSV and Markdown files — no database

**Status:** Accepted
**Date:** 2026-09-25

## Context

The existing organisation projects store their books mainly as CSV and Markdown (for
example `books/<year>/transactions.csv`, `vouchers/`, `journal.md`), with configuration in
YAML. The owner finds this works well. The initial idea keeps the same file-based layout for
the organisation projects and runs the agent locally.

## Decision

The core reads and writes organisation data as plain files — CSV for tabular data such as
transactions, Markdown for human-readable records such as journals and reports, YAML for
configuration and rules. No database is introduced.

The exact file layout and schemas are defined MVP by MVP, starting with the common
transaction model in MVP-002.

## Consequences

**Benefits:**

- Data stays readable and editable by humans and by Claude Code without extra tooling.
- Every change to the books is visible in the organisation project's git history, which
  supports the audit trail and the annual audit.
- No database server to install, back up or secure on a local machine.

**Trade-offs:**

- No transactions, constraints or concurrent-writer protection from a database; integrity
  has to be enforced by the core's validation code and by avoiding parallel runs against the
  same organisation.
- Performance and querying are limited — acceptable at the volume of a small association.
- Schema changes to CSV files need explicit, careful migration code.

## Alternatives considered

- **SQLite**: rejected for now — adds a binary file that is opaque in git diffs and to the
  agent, without a current need.
- **A hosted database**: rejected — no hosting environment exists and it would move
  organisation data off the owner's machine.
