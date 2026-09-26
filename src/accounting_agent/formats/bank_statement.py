"""The organisation's bank statement file and fund-value file (ADR-007, ADR-008).

Both are semicolon-separated UTF-8 without BOM, with LF line endings:

- the statement file, ``datum;belopp;namn;meddelande;anteckning;saldo``, oldest first;
- the fund-value file, ``datum;värde``, sorted by date.

This module holds the core's first write paths. It writes only these two files, and
always through a temporary file that replaces the target, so that an interrupted run
never leaves half a file.
"""

import csv
import io
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from accounting_agent.formats.nordea_csv import StatementRow

STATEMENT_HEADER = ["datum", "belopp", "namn", "meddelande", "anteckning", "saldo"]
FUND_HEADER = ["datum", "värde"]


class StatementRefusedError(Exception):
    """Writing the export would drop transactions that the existing file holds."""


@dataclass(frozen=True)
class StatementWrite:
    """What ``write_statement`` wrote."""

    rows: int
    first_date: str
    last_date: str
    replaced_rows: int | None


@dataclass(frozen=True)
class FundWrite:
    """What ``write_fund_values`` wrote."""

    values: int
    latest_date: str


def write_statement(path: Path, rows: Sequence[StatementRow]) -> StatementWrite:
    """Replace the statement file at ``path`` with ``rows`` (oldest first).

    Raises:
        StatementRefusedError: if the export starts later than the existing file, which
            would silently drop the transactions before it.
    """
    existing = _read_rows(path)
    if existing and rows[0].date > existing[0][0]:
        raise StatementRefusedError(
            f"the export starts {rows[0].date} but {path.name} starts "
            f"{existing[0][0]}; fetch the whole year from 1 January."
        )
    _write_atomically(
        path,
        [STATEMENT_HEADER]
        + [
            [row.date, row.amount, row.name, row.message, row.note, row.balance]
            for row in rows
        ],
    )
    return StatementWrite(
        rows=len(rows),
        first_date=rows[0].date,
        last_date=rows[-1].date,
        replaced_rows=None if existing is None else len(existing),
    )


def write_fund_values(path: Path, values: dict[str, str]) -> FundWrite:
    """Merge ``values`` (date → value) into the fund-value file at ``path``."""
    merged = {row[0]: row[1] for row in _read_rows(path) or []}
    merged.update(values)
    dates = sorted(merged)
    _write_atomically(path, [FUND_HEADER] + [[d, merged[d]] for d in dates])
    return FundWrite(values=len(dates), latest_date=dates[-1])


def _read_rows(path: Path) -> list[list[str]] | None:
    """The data rows of an existing file, or ``None`` if there is no file yet."""
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    return list(csv.reader(io.StringIO(text, newline=""), delimiter=";"))[1:]


def _write_atomically(path: Path, rows: Iterable[list[str]]) -> None:
    buffer = io.StringIO(newline="")
    csv.writer(buffer, delimiter=";", lineterminator="\n").writerows(rows)
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_bytes(buffer.getvalue().encode("utf-8"))
        temporary.replace(path)
    finally:
        # Only left behind if the replace failed.
        temporary.unlink(missing_ok=True)
