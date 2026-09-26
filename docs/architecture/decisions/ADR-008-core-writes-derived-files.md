# ADR-008: The core writes derived files — bank statements and reports — never vouchers

**Status:** Accepted
**Date:** 2026-09-26

## Context

Until MVP-003 the core only read an organisation's books. MVP-003 adds the first writes:

- **bank import** turns the bank's export into the organisation's bank statement file and
  fund-value file, masking personal identity numbers;
- **reports** — the accounts, in Markdown — written to an output folder.

Both files are derived: they can be recreated from their sources at any time. Vouchers
are not derived; they record the treasurer's decisions. Creating and changing vouchers is
R3, with confidence levels and approval policies.

Helsingborgs Judoklubb's own scripts already follow these rules: the import refuses an
export that starts later than the existing file, never changes the export, and masks
personal identity numbers as `[personnummer]`. The reports are refused when the checks
give errors, unless forced, and they are in Swedish, since they are the association's
accounts. The core's terminal output masks as `[personal number]` (MVP-002).

## Decision

**The core writes only derived files — the bank statement file, the fund-value file and
the reports — and only to paths configured in `organisation.yaml`. It never writes
vouchers or other books.**

- **Where:** only the configured statement file, fund-value file and report output folder.
  Paths resolve relative to the configuration directory, like `books.path`.
- **How:** a file is written to a temporary file next to it and then replaced, so an
  interrupted run never leaves half a file. UTF-8 without BOM, LF line endings.
- **The source is never changed:** the bank export is only read.
- **A partial export is refused:** an export whose first date is later than the existing
  statement file's first date would silently drop transactions, so it is refused.
- **Masking:** files the core writes mask personal identity numbers as `[personnummer]`,
  the same text as the organisation's scripts; terminal output keeps
  `[personal number]`.
- **Reports are in Swedish.** Code, findings, terminal output and documentation stay in
  English (documentation.md).
- **No reports from broken books:** when the checks give errors, no report is written
  unless the user forces it.

## Consequences

**Benefits:**

- An organisation can replace its import and report scripts with the core without its
  files changing.
- A write can only reach a derived file, so the worst case is a file that is recreated
  by running the command again.
- Writes are visible in the organisation project's git history.

**Trade-offs:**

- Two mask texts exist, one for files and one for the terminal.
- The reports contain voucher texts, because the voucher list and the general ledger are
  the accounts. They are masked, but names remain. They must stay in the organisation's
  own project; the core never prints them.
- Swedish report texts live in the code, next to English code. A second language would
  need a translation layer; none is planned.
- Configured paths are trusted: the core does not stop a path that points outside the
  organisation folder (accepted, as in MVP-002's STRIDE pass).

## Alternatives considered

- **Keep the core read-only and leave import and reports to the organisations:**
  rejected — it contradicts MVP-003's goal of replacing the organisation's scripts.
- **Write reports in English:** rejected by the owner (2026-09-26) — the reports are a
  Swedish association's accounts, read by its treasurer, board and auditor.
- **Let the core write vouchers now:** rejected — that needs confidence levels,
  approvals and an audit trail (R3).
