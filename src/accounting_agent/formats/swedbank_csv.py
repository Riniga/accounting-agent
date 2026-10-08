"""Reader for the `swedbank-csv` bank export format (MVP-006).

The export is comma-separated, in Windows-1252 with CRLF line endings, newest first. A
line that starts with ``*`` says what the file is; then come a header row and one row per
transaction, with the bank's row number, the account, three dates, a reference, a text,
the amount and the balance after the transaction.

The reader refuses whatever does not fit, naming the file and the row — never what the row
holds. Rows come out oldest first, dated by the bank's booking date, with the text as the
name and the reference as the message, personal identity numbers masked, ready to be
written to the organisation's statement file. The export itself is only read.
"""

import csv
import io
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
from accounting_agent.formats.common import parse_amount

HEADER = [
    "Radnr",
    "Clnr",
    "Kontonr",
    "Produkt",
    "Valuta",
    "Bokfdag",
    "Transdag",
    "Valutadag",
    "Referens",
    "Text",
    "Belopp",
    "Saldo",
]
TITLE_MARK = "*"
CURRENCY = "SEK"
# The bank saves the file in Windows-1252; a file saved again as UTF-8 is read too.
ENCODINGS = ("utf-8-sig", "cp1252")


def read_export(path: Path) -> StatementExport:
    """Read a statement export.

    Raises:
        ExportFormatError: if the file is empty, has another header, or a row does not
            fit the format.
    """
    text = decode_export(path, ENCODINGS)
    rows = [
        (number, [cell.strip() for cell in row])
        for number, row in enumerate(
            csv.reader(io.StringIO(text, newline=""), delimiter=","), start=1
        )
        if any(cell.strip() for cell in row)
    ]
    if rows and rows[0][1][0].startswith(TITLE_MARK):
        rows = rows[1:]
    if not rows:
        raise ExportFormatError(f"{path.name} is empty; expected a Swedbank export.")
    if rows[0][1] != HEADER:
        raise ExportFormatError(
            f"{path.name} does not have the header {','.join(HEADER)}."
        )
    if not rows[1:]:
        raise ExportFormatError(f"{path.name} has no transactions.")

    result: list[StatementRow] = []
    accounts: set[tuple[str, str]] = set()
    for expected, (number, cells) in enumerate(rows[1:], start=1):
        where = f"{path.name} row {number}"
        if len(cells) != len(HEADER):
            raise ExportFormatError(f"{where} does not have {len(HEADER)} fields.")
        field = dict(zip(HEADER, cells, strict=True))
        # The bank numbers its rows from 1; a gap means that rows are missing.
        if field["Radnr"] != str(expected):
            raise ExportFormatError(
                f"{where} does not have the bank's row number {expected}; the file "
                f"must be the bank's export as it was downloaded."
            )
        if field["Valuta"] != CURRENCY:
            raise ExportFormatError(f"{where} is not in {CURRENCY}.")
        accounts.add((field["Clnr"], field["Kontonr"]))
        result.append(
            StatementRow(
                date=_date(field["Bokfdag"], where),
                amount=_amount(field["Belopp"], where, required=True),
                # Personal identity numbers must never reach the books (ADR-008).
                name=mask_personal_numbers(field["Text"], mask=FILE_MASK),
                message=mask_personal_numbers(field["Referens"], mask=FILE_MASK),
                note="",
                balance=_amount(field["Saldo"], where, required=False),
            )
        )
    if len(accounts) > 1:
        # The account numbers are not quoted: the message is shown to AI tools too.
        raise ExportFormatError(
            f"{path.name} holds transactions of {len(accounts)} accounts; export one "
            f"account at a time."
        )

    # The statement file is oldest first, as events happened; the bank lists newest
    # first. An export in the other order is kept as it is.
    days = [row.date for row in result]
    if days == sorted(days, reverse=True):
        return StatementExport(tuple(reversed(result)))
    if days == sorted(days):
        return StatementExport(tuple(result))
    raise ExportFormatError(
        f"{path.name} has its dates in no order; the rows must be in the bank's order."
    )


def _date(text: str, where: str) -> str:
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        raise ExportFormatError(f"{where} has a date that is not YYYY-MM-DD.") from None


def _amount(text: str, where: str, required: bool) -> str:
    """A plain decimal amount, as the bank writes it; an empty balance stays empty."""
    if not text and not required:
        return ""
    if parse_amount(text) is None:
        raise ExportFormatError(f"{where} has an amount that cannot be read.")
    return str(Decimal(text))
