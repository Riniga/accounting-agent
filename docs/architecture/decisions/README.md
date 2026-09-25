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
