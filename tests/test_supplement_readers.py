"""Tests for reading the supplementary files into the core model (ADR-007): fund value,
budget, closing comments and to-do list, in the core-owned formats.

A missing file is not a finding: its check is skipped, as in `kontroll.py`. No finding
quotes a cell's content.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

from accounting_agent.books import (
    BudgetItem,
    ClosingComment,
    FundValue,
    Severity,
    TodoItem,
)
from accounting_agent.formats.bank_statement import read_fund_values
from accounting_agent.formats.supplements import read_budget, read_comments, read_todo

FULL = Path(__file__).parent / "fixtures" / "example-full"
SENSITIVE = "Hemlig Exempelperson"


def write(tmp_path: Path, name: str, *lines: str) -> Path:
    path = tmp_path / name
    path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    return path


# --- Fund value -------------------------------------------------------------------------


def test_fund_values_are_read() -> None:
    values, findings = read_fund_values(FULL / "fund-value.csv")

    assert findings == []
    assert values == (
        FundValue(date=date(2026, 8, 31), value=Decimal("12345.67")),
        FundValue(date=date(2026, 9, 19), value=Decimal("12500.00")),
    )


def test_missing_fund_value_file_skips_the_check(tmp_path: Path) -> None:
    assert read_fund_values(tmp_path / "fund-value.csv") == (None, [])


def test_invalid_fund_value_is_an_error_and_the_row_is_skipped(
    tmp_path: Path,
) -> None:
    path = write(
        tmp_path,
        "fund-value.csv",
        "datum;värde",
        "2026-08-31;12 345,67",
        "2026-13-01;1.00",
        "2026-09-19;12500.00",
    )

    values, findings = read_fund_values(path)

    assert values is not None
    assert len(values) == 1
    assert [(f.severity, f.rule, f.location) for f in findings] == [
        (Severity.ERROR, "fund-value-invalid", "fund-value.csv:2"),
        (Severity.ERROR, "fund-value-invalid", "fund-value.csv:3"),
    ]


# --- Budget -----------------------------------------------------------------------------


def test_budget_is_read() -> None:
    items, findings = read_budget(FULL / "budget.csv")

    assert findings == []
    assert items is not None
    assert items[1] == BudgetItem(
        kind="kostnad",
        name="Lokal",
        accounts=("5010",),
        amount=Decimal("6000"),
        note="Hyra för träningslokalen",
        row=3,
    )


def test_budget_accounts_are_separated_by_spaces(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "budget.csv",
        "typ;post;konton;budget;anteckning",
        "intäkt;Avgifter;3001  3002;100;",
    )

    items, _ = read_budget(path)

    assert items is not None
    assert items[0].accounts == ("3001", "3002")


def test_invalid_budget_amount_is_an_error_and_the_item_is_kept(
    tmp_path: Path,
) -> None:
    path = write(
        tmp_path,
        "budget.csv",
        "typ;post;konton;budget;anteckning",
        f"kostnad;{SENSITIVE};5010;6 000;",
    )

    items, findings = read_budget(path)

    assert items is not None
    assert items[0].amount is None
    assert [(f.rule, f.location) for f in findings] == [
        ("budget-amount", "budget.csv:2")
    ]
    assert SENSITIVE not in findings[0].render()


def test_missing_budget_file_skips_the_check(tmp_path: Path) -> None:
    assert read_budget(tmp_path / "budget.csv") == (None, [])


def test_budget_with_a_wrong_header_is_not_read(tmp_path: Path) -> None:
    path = write(tmp_path, "budget.csv", "type;item;amount", "income;Fees;100")

    items, findings = read_budget(path)

    assert items is None
    assert [f.rule for f in findings] == ["header"]


# --- Closing comments -------------------------------------------------------------------


def test_closing_comments_are_read() -> None:
    comments, findings = read_comments(FULL / "comments.csv")

    assert findings == []
    assert comments is not None
    assert comments[1] == ClosingComment(
        id="2",
        date=date(2026, 3, 1),
        kind="händelse",
        accounts=("3002",),
        vouchers=("2", "5"),
        text="Medlemsavgifterna betalas via Swish.",
        row=3,
    )


def test_invalid_comment_date_is_an_error_and_the_comment_is_kept(
    tmp_path: Path,
) -> None:
    path = write(
        tmp_path,
        "comments.csv",
        "id;datum;typ;konto;verifikation;kommentar",
        f"1;1 mars;princip;;;{SENSITIVE}",
    )

    comments, findings = read_comments(path)

    assert comments is not None
    assert comments[0].date is None
    assert [(f.rule, f.location) for f in findings] == [
        ("comment-date", "comments.csv:2")
    ]
    assert SENSITIVE not in findings[0].render()


def test_missing_comments_file_skips_the_check(tmp_path: Path) -> None:
    assert read_comments(tmp_path / "comments.csv") == (None, [])


# --- To-do list -------------------------------------------------------------------------


def test_todo_list_is_read() -> None:
    items, findings = read_todo(FULL / "todo.csv")

    assert findings == []
    assert items is not None
    assert [i.id for i in items] == ["T1", "T2", "T3"]
    assert items[2] == TodoItem(
        id="T3",
        owner="vi",
        when="bokslut",
        area="fond",
        task="Bokför fondens värdeförändring",
        done_when="Värdeförändringen är bokförd",
        status="väntar",
        depends_on="T1",
        row=4,
    )


def test_missing_todo_file_skips_the_check(tmp_path: Path) -> None:
    assert read_todo(tmp_path / "todo.csv") == (None, [])
