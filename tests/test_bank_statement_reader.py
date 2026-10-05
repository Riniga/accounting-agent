"""Tests for reading the organisation's bank statement file into the core model.

The statement file is the one `import-bank` writes (ADR-008). Its names and messages are
not read into the model (ADR-007), and no finding quotes them.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from accounting_agent.books import BankTransaction, Finding, Severity
from accounting_agent.formats.bank_statement import read_statement

FIXTURE = Path(__file__).parent / "fixtures" / "example-full" / "statement.csv"
HEADER = "datum;belopp;namn;meddelande;anteckning;saldo"
YEAR = 2026
# A name and a message that must never appear in a finding.
SENSITIVE_NAME = "Hemlig Exempelperson"
SENSITIVE_MESSAGE = "Hemligt meddelande"


def write(tmp_path: Path, *rows: str, header: str = HEADER) -> Path:
    path = tmp_path / "statement.csv"
    path.write_bytes(("\n".join([header, *rows]) + "\n").encode("utf-8"))
    return path


def read(path: Path) -> tuple[tuple[BankTransaction, ...] | None, list[Finding]]:
    return read_statement(path, YEAR)


def test_valid_statement_file_is_read_without_findings() -> None:
    transactions, findings = read(FIXTURE)

    assert findings == []
    assert transactions is not None
    assert len(transactions) == 5
    assert transactions[0] == BankTransaction(
        date=date(2026, 1, 7),
        amount=Decimal("-130.00"),
        balance=Decimal("870.00"),
        row=2,
    )
    assert transactions[-1].row == 6


def test_missing_statement_file_is_info_and_skips_reconciliation(
    tmp_path: Path,
) -> None:
    transactions, findings = read(tmp_path / "statement.csv")

    assert transactions is None
    assert findings == [
        Finding(
            Severity.INFO,
            "bank-statement-missing",
            "statement.csv",
            "file is missing; no reconciliation against the bank",
        )
    ]


def test_wrong_header_is_an_error_and_nothing_is_read(tmp_path: Path) -> None:
    path = write(tmp_path, "2026-01-07;-130.00;A;B;;870.00", header="date;amount")

    transactions, findings = read(path)

    assert transactions is None
    assert [(f.severity, f.rule) for f in findings] == [(Severity.ERROR, "header")]


def test_bom_is_an_error_but_the_file_is_read(tmp_path: Path) -> None:
    path = tmp_path / "statement.csv"
    path.write_bytes(
        ("﻿" + HEADER + "\n2026-01-07;-130.00;A;B;;870.00\n").encode("utf-8")
    )

    transactions, findings = read(path)

    assert transactions is not None
    assert len(transactions) == 1
    assert [f.rule for f in findings] == ["encoding"]


def test_wrong_column_count_is_an_error_and_the_row_is_skipped(tmp_path: Path) -> None:
    path = write(
        tmp_path, "2026-01-07;-130.00;870.00", "2026-01-15;200.00;A;B;;1070.00"
    )

    transactions, findings = read(path)

    assert transactions is not None
    assert [t.row for t in transactions] == [3]
    assert [(f.rule, f.location) for f in findings] == [("columns", "statement.csv:2")]


def test_invalid_date_is_an_error_and_the_row_is_skipped(tmp_path: Path) -> None:
    path = write(tmp_path, f"2026-13-07;-130.00;{SENSITIVE_NAME};B;;870.00")

    transactions, findings = read(path)

    assert transactions == ()
    assert [(f.severity, f.rule, f.location) for f in findings] == [
        (Severity.ERROR, "bank-statement-date", "statement.csv:2")
    ]


@pytest.mark.parametrize(
    "row",
    [
        "2026-01-07;-130,00;A;B;;870.00",  # decimal comma
        "2026-01-07;-1 130.00;A;B;;870.00",  # space
        "2026-01-07;-130.00;A;B;;870.0.0",  # invalid balance
    ],
)
def test_invalid_amount_or_balance_is_an_error_and_the_row_is_skipped(
    tmp_path: Path, row: str
) -> None:
    transactions, findings = read(write(tmp_path, row))

    assert transactions == ()
    assert [f.rule for f in findings] == ["bank-statement-amount"]


def test_empty_balance_is_allowed(tmp_path: Path) -> None:
    transactions, findings = read(write(tmp_path, "2026-01-07;-130.00;A;B;;"))

    assert findings == []
    assert transactions is not None
    assert transactions[0].balance is None


def test_date_outside_the_fiscal_year_is_an_error_but_the_row_is_kept(
    tmp_path: Path,
) -> None:
    transactions, findings = read(write(tmp_path, "2025-12-31;-130.00;A;B;;870.00"))

    assert transactions is not None
    assert len(transactions) == 1
    assert [(f.severity, f.rule) for f in findings] == [
        (Severity.ERROR, "bank-statement-year")
    ]


def test_rows_not_oldest_first_are_an_error_but_are_kept(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "2026-01-15;200.00;A;B;;1070.00",
        "2026-01-07;-130.00;A;B;;870.00",
    )

    transactions, findings = read(path)

    assert transactions is not None
    assert len(transactions) == 2
    assert [(f.rule, f.location) for f in findings] == [
        ("bank-statement-order", "statement.csv:3")
    ]


def test_no_finding_quotes_a_name_or_a_message(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        f"2026-13-01;-1.00;{SENSITIVE_NAME};{SENSITIVE_MESSAGE};;1.00",
        f"2026-01-02;x;{SENSITIVE_NAME};{SENSITIVE_MESSAGE};;1.00",
        f"2025-01-03;-1.00;{SENSITIVE_NAME};{SENSITIVE_MESSAGE};;1.00",
        f"2026-01-01;-1.00;{SENSITIVE_NAME};{SENSITIVE_MESSAGE};;1.00",
    )

    _, findings = read(path)

    assert len(findings) >= 3
    for finding in findings:
        assert SENSITIVE_NAME not in finding.render()
        assert SENSITIVE_MESSAGE not in finding.render()
