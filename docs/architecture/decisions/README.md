# ADR

Architecture Decision Records.

## Namnstandard

`ADR-001-kort-beslut.md`

Nygard-format: titel, status, kontext, beslut, konsekvenser. En godkänd ADR redigeras
aldrig i efterhand — om beslutet ändras skrivs en ny ADR som ersätter den, med en länk
mellan dem. Se [`docs/standards/documentation.md`](../../standards/documentation.md) and
`ADR-TEMPLATE.md` in this directory for the exact section structure.

## Index

| ADR | Beslut |
|-----|--------|
| [ADR-001](ADR-001-adopt-development-methodology.md) | Follow the development methodology, with single-maintainer exceptions documented |
| [ADR-002](ADR-002-python-core-repository.md) | This repository is a single Python package — the core; organisation projects are separate repositories |
| [ADR-003](ADR-003-no-real-data-in-core-repo.md) | The core repository holds no real organisation data |
| [ADR-004](ADR-004-csv-and-markdown-storage.md) | Books are stored as CSV and Markdown files — no database |
| [ADR-005](ADR-005-noncommercial-licence.md) | License the code under the PolyForm Noncommercial License 1.0.0 |
| [ADR-006](ADR-006-core-book-model.md) | The core models books as double-entry vouchers with posting lines; each file format has its own reader |
| [ADR-007](ADR-007-supplementary-book-files.md) | Supplementary book files get core models and core-owned formats; accounts get an optional group |
| [ADR-008](ADR-008-core-writes-derived-files.md) | The core writes derived files — bank statements and reports — never vouchers |
