"""What every bank export reader gives (ADR-008, ADR-010).

A bank's export has the bank's own format, and the core has one reader per bank. They all
give the same thing: statement rows as text, oldest first, ready to be written to the
organisation's statement file — or, where a bank has one, a fund's market values.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


class ExportFormatError(Exception):
    """The file is not a bank export the core can read."""


def decode_export(path: Path, encodings: Sequence[str] = ("utf-8-sig",)) -> str:
    """The export's text, in the first of ``encodings`` that fits.

    Raises:
        ExportFormatError: if none fits. Another bank's export, in another encoding, is
            then refused like any other file that is not this bank's.
    """
    raw = path.read_bytes()
    for encoding in encodings:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ExportFormatError(
        f"{path.name} is not in the encoding this bank's export has "
        f"({' or '.join(encodings)})."
    )


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
