"""Reader for the `sparbanken-syd-csv` bank export format (MVP-005).

The export has no header row. Every row is ``date;text;amount;currency;``: semicolon
separated UTF-8 with a BOM, oldest first, the amount with a thousands point and a decimal
comma, and no balance. Since nothing but the shape of its rows tells that a file is this
export, the reader refuses whatever does not fit exactly, naming the file and the row —
never what the row holds, which can be a person's name.

Rows come out oldest first, with amounts normalised and personal identity numbers masked,
ready to be written to the organisation's statement file. The export itself is only read.
"""

import csv
import io
import re
from datetime import date
from decimal import Decimal
from pathlib import Path

from accounting_agent.books.masking import FILE_MASK, mask_personal_numbers
from accounting_agent.formats.bank_export import (
    ExportFormatError,
    StatementExport,
    StatementRow,
    decode_export,
)

FIELDS = "date;text;amount;currency"
FIELD_COUNT = 4
CURRENCY = "SEK"
# Digits, grouped by thousands points or not at all, then an optional decimal comma.
AMOUNT = re.compile(r"-?(\d{1,3}(\.\d{3})+|\d+)(,\d{1,2})?")


def read_export(path: Path) -> StatementExport:
    """Read a statement export.

    Raises:
        ExportFormatError: if the file is empty, or a row does not fit the format.
    """
    text = decode_export(path)
    rows = [
        (number, row)
        for number, row in enumerate(
            csv.reader(io.StringIO(text, newline=""), delimiter=";"), start=1
        )
        if any(cell.strip() for cell in row)
    ]
    if not rows:
        raise ExportFormatError(f"{path.name} is empty; expected rows of {FIELDS}.")

    result: list[StatementRow] = []
    for number, row in rows:
        where = f"{path.name} row {number}"
        # The bank ends each row with a separator, which gives one empty field more.
        if len(row) == FIELD_COUNT + 1 and not row[-1].strip():
            row = row[:FIELD_COUNT]
        if len(row) != FIELD_COUNT:
            raise ExportFormatError(f"{where} does not have the fields {FIELDS}.")
        day, name, amount, currency = (cell.strip() for cell in row)
        if currency != CURRENCY:
            raise ExportFormatError(f"{where} is not in {CURRENCY}.")
        result.append(
            StatementRow(
                date=_date(day, where),
                amount=_amount(amount, where),
                # Personal identity numbers must never reach the books (ADR-008).
                name=mask_personal_numbers(name, mask=FILE_MASK),
                message="",
                note="",
                balance="",
            )
        )

    # The statement file is oldest first, as events happened, and so is this bank's
    # export. An export that is newest first is turned around; one in no order at all
    # is not the bank's file as it was downloaded.
    days = [row.date for row in result]
    if days == sorted(days):
        return StatementExport(tuple(result))
    if days == sorted(days, reverse=True):
        return StatementExport(tuple(reversed(result)))
    raise ExportFormatError(
        f"{path.name} has its dates in no order; the rows must be in the bank's order."
    )


def _date(text: str, where: str) -> str:
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise ExportFormatError(f"{where} has a date that is not YYYY-MM-DD.") from None


def _amount(text: str, where: str) -> str:
    """``'-12.458,00'`` → ``'-12458.00'``: no thousands separators, a decimal point."""
    compact = text.replace("\xa0", "").replace(" ", "")
    # A point is only ever a thousands separator here. Without this check an amount
    # written with a decimal point, such as 12.50, would silently become 1250.
    if not AMOUNT.fullmatch(compact):
        raise ExportFormatError(f"{where} has an amount that cannot be read.")
    return str(Decimal(compact.replace(".", "").replace(",", ".")))
