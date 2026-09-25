# ADR-006: The core models books as double-entry vouchers with posting lines; each file format has its own reader

**Status:** Accepted
**Date:** 2026-09-25

## Context

MVP-002 moves the first functionality into the core: a shared model of an organisation's
books, and checks that the books are consistent. The MVP assumed Helsingborgs Judoklubb and
Aktivitet Förebygger keep their books in the same way. The plan's investigation (MVP-002
plan §0.1) read both projects' code and found they share the concept — chart of accounts
and opening balance as CSV, one Markdown file per voucher (ADR-004) — but not the format
or the voucher model:

- **Helsingborgs Judoklubb** writes each voucher as front matter with a single debit/credit
  pair and an amount signed "as the bank shows it". Vouchers are numbered 1..N, and the
  file name encodes the number and the date.
- **Aktivitet Förebygger** writes each voucher as a Markdown table with several posting
  lines (account, debit, credit), numbered per voucher series (for example K, B). The
  chart of accounts and the opening balance have other columns.

The front matter is not YAML. It is a line-based `key: value` format where quoted values
are JSON strings. Parsing it as YAML would turn amounts into floating-point numbers.

## Decision

The core has **one general double-entry model**, and **a reader per file format** that
maps an organisation's files into it.

- **Model:**
  - `Account` (number, name);
  - `OpeningBalance` (account, amount, debit positive);
  - `Voucher` — optional series, number, date, text, supporting documents, note, and
    **N `PostingLine`s** (account, debit, credit).

  A voucher balances when its debits equal its credits. A single debit/credit pair is
  simply a voucher with two lines.
- **Amounts** are `decimal.Decimal`, parsed from the file's text, **never floats**.
- **Readers** live outside the domain package (`accounting_agent.formats`). Each reader
  owns its format's rules — file names, column headers, quoting, and the
  `front-matter` format's "amount as the bank shows it" sign rule. It reports problems as
  findings rather than raising.
- **Formats are named neutrally** (`front-matter`), never after an organisation. An
  organisation selects its format in `organisation.yaml`.
- The **domain package** (`accounting_agent.books`) — model, balances, checks, findings,
  masking — does no file I/O. The boundary is enforced by Ruff's `banned-api` rule
  (MVP-002, TODO 6.4).

The storage decision itself — files, not a database — stays as recorded in
[ADR-004](ADR-004-csv-and-markdown-storage.md).

## Consequences

**Benefits:**

- Aktivitet Förebygger's multi-line, per-series vouchers fit without changing the model;
  only a new reader is needed.
- The general checks (numbering, balancing, known accounts, fiscal year) are written
  once, against the model, and apply to every format.
- Exact decimal arithmetic, so balances can match the organisations' own tools to the
  öre.
- The domain can be tested with objects built in code, without files.

**Trade-offs:**

- Each new format costs a reader, with its own parsing rules and tests. The
  `front-matter` reader deliberately copies the organisation's existing parser's quirks
  (for example JSON-quoted values, and `key: value` split at the first colon) instead of
  "fixing" them, so that results stay comparable.
- A general model is slightly heavier than the two-line vouchers Helsingborgs Judoklubb
  needs today.
- Format-specific rules (like the bank-sign rule) are not visible among the general
  checks. They must be looked for in the reader.

## Alternatives considered

- **Model Helsingborgs Judoklubb's voucher (one debit/credit pair) directly:** rejected —
  it would have to be redesigned as soon as Aktivitet Förebygger's multi-line vouchers
  arrive (R5).
- **Convert every organisation to one common file format first:** rejected — it
  contradicts "extract, don't rewrite" (initial idea) and would mean rewriting real books.
- **Parse the front matter with YAML (PyYAML is already a dependency):** rejected — YAML
  types would turn amounts into floats and dates into date objects, which silently
  changes values compared with the organisation's own tool.
