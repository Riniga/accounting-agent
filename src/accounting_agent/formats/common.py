"""Shared rules for the semicolon-separated CSV files the formats read.

The rules are those of Helsingborgs Judoklubb's own tool, which every CSV file in its
books follows: UTF-8 without BOM, LF line endings, an exact header row, the same number of
columns on every row. Problems are reported as findings, never raised, and no message
quotes a cell's content.
"""

import csv
import io
import re
from decimal import Decimal
from pathlib import Path

from accounting_agent.books import Finding, Severity

AMOUNT = re.compile(r"-?\d+(\.\d{1,2})?")
BOM = b"\xef\xbb\xbf"

Row = dict[str, str]


class Findings:
    """Collects findings in the order they are found."""

    def __init__(self) -> None:
        self.items: list[Finding] = []

    def add(self, severity: Severity, rule: str, location: str, message: str) -> None:
        """Record one finding."""
        self.items.append(Finding(severity, rule, location, message))


def read_text(path: Path, findings: Findings) -> str | None:
    """Read a UTF-8 file; a BOM is an error and CRLF a warning, invalid UTF-8 → None."""
    raw = path.read_bytes()
    if raw.startswith(BOM):
        findings.add(
            Severity.ERROR,
            "encoding",
            path.name,
            "file has a BOM; must be UTF-8 without BOM",
        )
        raw = raw[len(BOM) :]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        findings.add(Severity.ERROR, "encoding", path.name, "file is not valid UTF-8")
        return None
    if "\r" in text:
        findings.add(
            Severity.WARNING,
            "line-endings",
            path.name,
            "file has CRLF line endings; must be LF",
        )
    return text


def read_csv(path: Path, header: list[str], findings: Findings) -> list[Row] | None:
    """Read a CSV file with an exact header into rows keyed by column, plus ``_line``.

    Returns ``None`` if the file is missing, not UTF-8 or has the wrong header.
    """
    if not path.is_file():
        findings.add(Severity.ERROR, "file-missing", path.name, "file is missing")
        return None
    text = read_text(path, findings)
    if text is None:
        return None
    rows = list(csv.reader(io.StringIO(text, newline=""), delimiter=";"))
    if not rows or rows[0] != header:
        findings.add(
            Severity.ERROR,
            "header",
            path.name,
            f"wrong header row, expected {';'.join(header)}",
        )
        return None

    result: list[Row] = []
    for line_number, row in enumerate(rows[1:], start=2):
        location = f"{path.name}:{line_number}"
        if not row:
            findings.add(Severity.WARNING, "empty-row", location, "empty row")
        elif len(row) != len(header):
            findings.add(
                Severity.ERROR,
                "columns",
                location,
                f"{len(row)} columns, expected {len(header)}",
            )
        else:
            result.append(
                {**dict(zip(header, row, strict=True)), "_line": str(line_number)}
            )
    return result


def parse_amount(text: str) -> Decimal | None:
    """A plain decimal amount (decimal point, no spaces), or ``None``."""
    # The pattern only admits plain decimal numbers, so Decimal() cannot fail here.
    return Decimal(text) if AMOUNT.fullmatch(text) else None
