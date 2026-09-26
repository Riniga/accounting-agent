"""Reader for the `nordea-csv` bank export format (ADR-008).

The bank exports either an account statement (a header with ``Datum``, ``Belopp`` and
``Saldo``) or a fund's market values (exactly ``Datum;Belopp``). Both are
semicolon-separated UTF-8, possibly with a BOM, newest first. The reader reproduces the
organisation's own import script (MVP-003 plan §0.3): rows come out oldest first, with
dates and amounts normalised and personal identity numbers masked, ready to be written to
the organisation's statement file. The export itself is only read.
"""

import csv
import io
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from accounting_agent.books.masking import FILE_MASK, mask_personal_numbers

STATEMENT_COLUMNS = frozenset({"Datum", "Belopp", "Saldo"})
FUND_COLUMNS = ["Datum", "Belopp"]


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


def read_export(path: Path) -> StatementExport | FundExport:
    """Read a bank export and tell its kind by the header row.

    Raises:
        ExportFormatError: if the header is not recognised, or a statement export has no
            transactions.
    """
    text = path.read_bytes().decode("utf-8-sig")
    rows = [
        row
        for row in csv.reader(io.StringIO(text, newline=""), delimiter=";")
        if any(cell.strip() for cell in row)
    ]
    if not rows:
        raise ExportFormatError(f"{path.name} is empty; expected a header row.")

    header = [cell.strip() for cell in rows[0]]
    named = [cell for cell in header if cell]
    if STATEMENT_COLUMNS <= set(named):
        return _statement(path, header, rows[1:])
    if named == FUND_COLUMNS:
        if not rows[1:]:
            raise ExportFormatError(f"{path.name} has no values.")
        return FundExport({_date(row[0]): _amount(row[1]) for row in rows[1:]})
    raise ExportFormatError(
        f"{path.name} has an unknown header; expected a statement "
        f"({', '.join(sorted(STATEMENT_COLUMNS))}) or a fund value "
        f"({';'.join(FUND_COLUMNS)})."
    )


def _statement(path: Path, header: list[str], rows: list[list[str]]) -> StatementExport:
    if not rows:
        raise ExportFormatError(f"{path.name} has no transactions.")
    columns = {name: index for index, name in enumerate(header) if name}

    def field(row: list[str], name: str) -> str:
        # The bank may leave out columns, or trailing empty cells in a row.
        index = columns.get(name)
        return row[index].strip() if index is not None and index < len(row) else ""

    result: list[StatementRow] = []
    # The bank lists newest first; the statement file is oldest first, as events happened.
    for row in reversed(rows):
        # "Ytterligare detaljer" says who, where "Namn" is often only the sender's bank.
        name = field(row, "Ytterligare detaljer") or field(row, "Namn")
        message = field(row, "Meddelande")
        if message.isdigit():
            message = message.lstrip("0")
        result.append(
            StatementRow(
                date=_date(field(row, "Datum")),
                amount=_amount(field(row, "Belopp")),
                name=_mask(name),
                message=_mask(message),
                note=_mask(field(row, "Egna anteckningar")),
                balance=_amount(field(row, "Saldo")),
            )
        )
    return StatementExport(tuple(result))


def _mask(text: str) -> str:
    # Personal identity numbers must never reach the books (ADR-008).
    return mask_personal_numbers(text, mask=FILE_MASK)


def _date(text: str) -> str:
    return text.strip().replace("/", "-")


def _amount(text: str) -> str:
    """``'1 234,50'`` → ``'1234.50'``; empty stays empty."""
    cleaned = text.replace("\xa0", "").replace(" ", "").replace(",", ".")
    if not cleaned:
        return ""
    try:
        return str(Decimal(cleaned))
    except InvalidOperation as error:
        # The value is not quoted: in a malformed row it could be a name.
        raise ExportFormatError(
            "the export has an amount that is not a number."
        ) from error
