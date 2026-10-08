# ADR-010: The core has one book format; organisations adapt to it

**Status:** Accepted
**Date:** 2026-10-07

Supersedes [ADR-006](ADR-006-core-book-model.md) on one point: "each file format has its
own reader". The book model in ADR-006 still applies.

## Context

ADR-006 gave the core one general book model and a reader per file format, because the
first two organisations kept their books in different formats: Helsingborgs Judoklubb in
`front-matter`, with one debit and one credit account per voucher, and Aktivitet
Förebygger in a table format with several lines per voucher and voucher series. The
roadmap had "Aktivitet Förebygger reader" as a step before that organisation could use
the core.

Since then the core has started to write books, not only read them (ADR-009): it creates
vouchers, and its reports, checks and instructions for AI agents all describe one layout
of files. A second book format would need a second reader, a second writer, a second set
of generated lines and a second routine to teach every agent — for each organisation that
differs.

The owner decided on 2026-10-07: the core is meant for many organisations, not three, and
it has **one** book format. An organisation that wants to use the core adopts the format.
Where the format cannot hold what an organisation needs, that is a fault in the format,
and the one format is extended.

The first such fault is known: the format holds one debit and one credit account per
voucher, and a salary payment or an issued invoice needs more (MVP-005).

## Decision

**The core reads and writes one book format. No reader or writer is added for another
organisation's book format; an organisation adopts the core's format instead.**

- The format is the one called `front-matter` today: a chart of accounts and an opening
  balance as CSV, one Markdown file per voucher, and the supplementary files of ADR-007.
- When the format lacks something an organisation needs, the format is extended for
  everyone, in a way that keeps existing books valid.
- **Formats that belong to someone else are not book formats.** A bank's export has the
  bank's format, and the core reads one per bank. A reference chart, a tax-account
  statement or a payroll file is likewise read as what it is.
- An organisation that already has books in another layout builds them again in the
  core's format, from its bank statements and supporting documents. The core does not
  convert books.
- `books.format` stays in `organisation.yaml` with its one value, so that existing
  configurations keep working.

## Consequences

**Benefits:**

- One routine, one set of checks, one set of reports and one instruction for AI agents,
  whatever the organisation.
- A change to the format reaches every organisation at once.
- A new organisation is set up by configuration and by copying a layout, not by code.

**Trade-offs:**

- An organisation with working books in another layout has to rebuild them, and loses
  whatever its own layout expressed that the format does not, until the format is
  extended.
- The format has to grow to fit the most demanding organisation, and every extension has
  to keep the simplest organisation's files valid and readable in a text editor.
- Voucher series, which Aktivitet Förebygger used, are not in the format. The model
  still has them (ADR-006); they are unused until the format gets them, if it ever does.
- The comparison of the two formats and the plan for a second reader (MVP-002) are no
  longer the way forward. They stay as history.

## Alternatives considered

- **A reader per book format** (ADR-006): rejected by the owner — it grows with the
  number of organisations, and since ADR-009 it would also mean a writer per format.
- **Convert an organisation's existing books into the core's format with a tool:**
  rejected — a converter is a reader by another name, used once. Rebuilding from the
  bank statement and the supporting documents also tests the organisation's routine.
- **A new, richer format for everyone, replacing `front-matter`:** rejected — the
  existing format can be extended without invalidating a single existing voucher.
