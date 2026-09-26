# ADR-007: Supplementary book files get core models and core-owned formats; accounts get an optional group

**Status:** Accepted
**Date:** 2026-09-26

## Context

MVP-003 moves the rest of Helsingborgs Judoklubb's bookkeeping tooling into the core:
bank reconciliation, the remaining checks and the reports. That tooling reads more than
the books that ADR-006 models:

- a bank statement file and a fund-value file;
- a budget, closing comments and a to-do list (CSV files next to the books);
- a reference chart of accounts (the BAS chart, in four CSV files);
- the supporting-documents folder.

The MVP-003 plan's investigation (§0.2) found that the model from ADR-006 cannot carry
the reports or the chart check:

- `Account` holds a number and a name only. The organisation's reports group accounts by
  the chart's `kontogrupp` column and find equity by its group name, and the chart check
  compares the chart's `bas_beskrivning` with the reference chart.
- Aktivitet Förebygger's chart has no group column (MVP-002, "Book formats"), so a group
  cannot be required.
- `kontroll.py`'s bank findings quote counterparties' names. The MVP forbids that.

ADR-006 is accepted and is not edited; this ADR extends it.

## Decision

**The supplementary files get domain models in `accounting_agent.books`, their formats
are owned by the core and read in `accounting_agent.formats`, and `Account` gets an
optional group and reference description.**

- **`Account`** gains two optional fields: its group (the chart's group name) and its
  reference description (the chart's copy of the reference-chart description). A format
  without them leaves them empty. Reports then fall back to the two-digit BAS group.
- **New domain models**, with no file I/O, as in ADR-006:
  - bank transactions — date, amount, balance and statement row, but **no counterparty
    name or message**, so that no check or report built on them can quote one;
  - fund values; budget items; closing comments; to-do items; the reference chart.
- **Formats are owned by the core.** Each file has one neutrally named format with a
  fixed header and fixed allowed values — for example the closing-comment types and the
  to-do owners, statuses and "when" values — as the `front-matter` reader owns its files.
  The first formats are the ones Helsingborgs Judoklubb uses today.
- **Configuration gives paths and organisation-specific values only:** where each file
  is, the fund and parking accounts, and conventions such as the accounts that need no
  supporting document. Every supplementary file is optional; its checks run only when it
  is configured.
- **Checks that need the file system** — whether a supporting document exists — get
  their input from the CLI (the set of file names), so the domain stays free of I/O.

## Consequences

**Benefits:**

- Reconciliation, the remaining checks and the reports are written once, against the
  model, and apply to any organisation whose files can be read into it.
- A bank transaction cannot leak a name into a finding, because the model has no field
  for it.
- Aktivitet Förebygger can use the reports without a group column.

**Trade-offs:**

- The core now dictates the format of files an organisation writes by hand (budget,
  comments, to-do). Another organisation must use the same headers and values, or a new
  reader is needed.
- The allowed values are Swedish words (`kassör`, `princip`, `öppen`), fixed in code.
  Changing them is a core change, not a configuration change.
- More models and readers to maintain, each with its own tests.

## Alternatives considered

- **Keep supplementary files outside the model and read them in the report code:**
  rejected — the checks and the reports would each parse the files, and the domain
  boundary (ADR-006) would be broken.
- **Allowed values in configuration:** rejected by the owner (2026-09-26) — the formats
  are the core's, and one organisation's words in configuration would still be the same
  words; only real conventions (accounts, markers) are configured.
- **Carry the counterparty name in the bank-transaction model and rely on the checks not
  to print it:** rejected — a model field invites use; leaving it out makes the rule
  structural.
