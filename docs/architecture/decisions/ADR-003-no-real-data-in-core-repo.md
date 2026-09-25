# ADR-003: The core repository holds no real organisation data

**Status:** Accepted
**Date:** 2026-09-25

## Context

The system handles bank statements, receipts, invoices, e-mail, member registers and — for
Aktivitet Förebygger — payroll data with personal identity numbers and salaries. This
repository is public. The first principle of the initial idea is that organisations'
financial data is never mixed.

To extract functionality, the existing organisation projects are copied locally into
`docs/reference/` as reference material. That copy contains real financial and personal
data. The methodology (area F) also restricts what data may be given to an AI tool: only
low-confidentiality data, with dev/test data anonymised or synthetic.

## Decision

This repository contains **only code, models, documentation and synthetic test data**. Real
organisation data lives exclusively in each organisation's own private repository.

- `docs/reference/` is listed in `.gitignore` and is never committed.
- When the reference projects are analysed with an AI tool, only code, instructions,
  configuration, chart of accounts and rules are read — not books, bank files, receipts,
  payroll, personnel or member data.
- Test fixtures are synthetic and must not be derived by copying and lightly editing real
  records.

## Consequences

**Benefits:**

- The repository can be public and shared with other associations without data-protection
  risk.
- A clear rule for AI tools about what they may read while working in this repository.

**Trade-offs:**

- Realistic edge cases have to be reproduced synthetically, which takes effort and can miss
  quirks in real data; end-to-end verification against real data happens in the
  organisation projects, not here.
- A git-ignore rule is a single line of defence; a mistaken `git add -f` would bypass it.
  Secret scanning does not detect personal data.

## Alternatives considered

- **Anonymised copies of real data as fixtures**: rejected for now — anonymising financial
  and payroll data reliably is hard, and a partial job would still leak information in a
  public repository.
- **Keep the reference projects outside the repository folder altogether**: a valid and
  safer option; not chosen only because the owner wants them next to the code while
  extracting. Can be adopted at any time without changing this decision.
