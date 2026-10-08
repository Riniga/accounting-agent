"""What every bank export reader gives (ADR-008, ADR-010).

A bank's export has the bank's own format, and the core has one reader per bank. They all
give the same thing: statement rows as text, oldest first, ready to be written to the
organisation's statement file — or, where a bank has one, a fund's market values.
"""

from dataclasses import dataclass


class ExportFormatError(Exception):
    """The file is not a bank export the core can read."""


@dataclass(frozen=True)
class StatementRow:
    """One statement transaction, as text ready for the statement file."""

    date: str
    amount: str
    name: str
    message: str
    note: str
    balance: str


@dataclass(frozen=True)
class StatementExport:
    """An account statement export, oldest transaction first."""

    rows: tuple[StatementRow, ...]


@dataclass(frozen=True)
class FundExport:
    """A fund-value export: market value per date."""

    values: dict[str, str]
