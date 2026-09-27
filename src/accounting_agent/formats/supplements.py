"""Readers for the supplementary CSV files (ADR-007): budget, closing comments and
to-do list, in the core-owned formats Helsingborgs Judoklubb uses.

A missing file is not a finding — its check is skipped, as in `kontroll.py`. The files
follow the shared CSV rules (`formats.common`). A cell that cannot be parsed is an error
at ``<file>:<row>``, and the message never quotes it.
"""

from datetime import date
from pathlib import Path

from accounting_agent.books import (
    BudgetItem,
    ClosingComment,
    Finding,
    Severity,
    TodoItem,
)
from accounting_agent.formats.common import Findings, Row, parse_amount, read_csv

BUDGET_HEADER = ["typ", "post", "konton", "budget", "anteckning"]
COMMENTS_HEADER = ["id", "datum", "typ", "konto", "verifikation", "kommentar"]
TODO_HEADER = [
    "id",
    "ägare",
    "när",
    "område",
    "uppgift",
    "klart_när",
    "status",
    "beroende",
]


def read_budget(path: Path) -> tuple[tuple[BudgetItem, ...] | None, list[Finding]]:
    """Read the budget; accounts are separated by spaces."""
    rows, findings = _read(path, BUDGET_HEADER)
    if rows is None:
        return None, findings.items
    items: list[BudgetItem] = []
    for row in rows:
        amount = parse_amount(row["budget"])
        if amount is None:
            findings.add(
                Severity.ERROR,
                "budget-amount",
                f"{path.name}:{row['_line']}",
                "budget is not a valid amount (decimal point, no spaces)",
            )
        items.append(
            BudgetItem(
                kind=row["typ"],
                name=row["post"],
                accounts=tuple(row["konton"].split()),
                amount=amount,
                note=row["anteckning"],
                row=int(row["_line"]),
            )
        )
    return tuple(items), findings.items


def read_comments(
    path: Path,
) -> tuple[tuple[ClosingComment, ...] | None, list[Finding]]:
    """Read the closing comments; accounts and vouchers are separated by spaces."""
    rows, findings = _read(path, COMMENTS_HEADER)
    if rows is None:
        return None, findings.items
    comments: list[ClosingComment] = []
    for row in rows:
        try:
            day: date | None = date.fromisoformat(row["datum"])
        except ValueError:
            day = None
            findings.add(
                Severity.ERROR,
                "comment-date",
                f"{path.name}:{row['_line']}",
                "datum is not a valid date (YYYY-MM-DD)",
            )
        comments.append(
            ClosingComment(
                id=row["id"],
                date=day,
                kind=row["typ"],
                accounts=tuple(row["konto"].split()),
                vouchers=tuple(row["verifikation"].split()),
                text=row["kommentar"],
                row=int(row["_line"]),
            )
        )
    return tuple(comments), findings.items


def read_todo(path: Path) -> tuple[tuple[TodoItem, ...] | None, list[Finding]]:
    """Read the to-do list."""
    rows, findings = _read(path, TODO_HEADER)
    if rows is None:
        return None, findings.items
    items = tuple(
        TodoItem(
            id=row["id"],
            owner=row["ägare"],
            when=row["när"],
            area=row["område"],
            task=row["uppgift"],
            done_when=row["klart_när"],
            status=row["status"],
            depends_on=row["beroende"],
            row=int(row["_line"]),
        )
        for row in rows
    )
    return items, findings.items


def _read(path: Path, header: list[str]) -> tuple[list[Row] | None, Findings]:
    findings = Findings()
    if not path.is_file():
        return None, findings
    return read_csv(path, header, findings), findings
