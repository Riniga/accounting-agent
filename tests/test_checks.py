"""Tests for the general book checks, run on model objects (ADR-006).

Severities follow the organisation's own tool: broken books are errors; a personal
identity number in a voucher text is a warning.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from accounting_agent.books import (
    Account,
    Books,
    Finding,
    OpeningBalance,
    PostingLine,
    Severity,
    Voucher,
    check_books,
)
from accounting_agent.formats.front_matter import read_books

YEAR = 2026
ACCOUNTS = (
    Account("1930", "Bank"),
    Account("2010", "Equity"),
    Account("3002", "Membership fees"),
    Account("6570", "Bank charges"),
)
OPENING = (
    OpeningBalance("1930", Decimal("100.00")),
    OpeningBalance("2010", Decimal("-100.00")),
)


def voucher(
    number: int,
    *,
    series: str | None = None,
    debit: str = "1930",
    credit: str = "3002",
    amount: str = "200",
    text: str = "Membership fee",
    on: date = date(YEAR, 3, 1),
) -> Voucher:
    return Voucher(
        series=series,
        number=number,
        date=on,
        text=text,
        lines=(
            PostingLine(debit, debit=Decimal(amount)),
            PostingLine(credit, credit=Decimal(amount)),
        ),
    )


def books(
    vouchers: tuple[Voucher, ...] = (voucher(1), voucher(2)),
    opening: tuple[OpeningBalance, ...] = OPENING,
    accounts: tuple[Account, ...] = ACCOUNTS,
) -> Books:
    return Books(accounts=accounts, opening_balances=opening, vouchers=vouchers)


def found(findings: list[Finding]) -> list[tuple[Severity, str, str]]:
    return sorted((f.severity, f.rule, f.location) for f in findings)


# --- Clean books -----------------------------------------------------------------------


def test_consistent_books_give_no_findings() -> None:
    assert check_books(books(), YEAR) == []


def test_the_synthetic_valid_books_give_no_findings() -> None:
    valid, read_findings = read_books(
        Path(__file__).parent / "fixtures" / "books" / "valid", "1930"
    )
    assert read_findings == []
    assert valid is not None

    assert check_books(valid, YEAR) == []


# --- Opening balance -------------------------------------------------------------------


def test_opening_balance_must_sum_to_zero() -> None:
    opening = (OpeningBalance("1930", Decimal("100.00")),)

    assert found(check_books(books(opening=opening), YEAR)) == [
        (Severity.ERROR, "opening-balance-sum", "opening balance")
    ]


def test_opening_balance_account_must_be_in_the_chart() -> None:
    opening = (
        OpeningBalance("1910", Decimal("100.00")),
        OpeningBalance("2010", Decimal("-100.00")),
    )

    assert found(check_books(books(opening=opening), YEAR)) == [
        (Severity.ERROR, "opening-balance-unknown-account", "opening balance 1910")
    ]


def test_opening_balance_account_must_be_a_balance_account() -> None:
    opening = (
        OpeningBalance("3002", Decimal("100.00")),
        OpeningBalance("2010", Decimal("-100.00")),
    )

    assert found(check_books(books(opening=opening), YEAR)) == [
        (Severity.ERROR, "opening-balance-not-balance-account", "opening balance 3002")
    ]


def test_opening_balance_account_may_appear_only_once() -> None:
    opening = (
        OpeningBalance("1930", Decimal("60.00")),
        OpeningBalance("1930", Decimal("40.00")),
        OpeningBalance("2010", Decimal("-100.00")),
    )

    assert found(check_books(books(opening=opening), YEAR)) == [
        (Severity.ERROR, "opening-balance-duplicate", "opening balance 1930")
    ]


# --- Chart of accounts -------------------------------------------------------------------


@pytest.mark.parametrize("number", ["193", "19300", "19A0", ""])
def test_account_number_must_have_four_digits(number: str) -> None:
    accounts = (*ACCOUNTS, Account(number, "Broken"))

    assert found(check_books(books(accounts=accounts), YEAR)) == [
        (Severity.ERROR, "account-number", f"account {number}")
    ]


# --- Voucher numbering ---------------------------------------------------------------------


def test_gap_in_voucher_numbers_is_an_error() -> None:
    vouchers = (voucher(1), voucher(2), voucher(4))

    assert found(check_books(books(vouchers=vouchers), YEAR)) == [
        (Severity.ERROR, "voucher-numbering", "voucher 4")
    ]


def test_duplicate_voucher_number_is_an_error() -> None:
    vouchers = (voucher(1), voucher(2), voucher(2))

    assert found(check_books(books(vouchers=vouchers), YEAR)) == [
        (Severity.ERROR, "voucher-numbering", "voucher 2")
    ]


def test_numbering_starts_at_one() -> None:
    vouchers = (voucher(2), voucher(3))

    assert found(check_books(books(vouchers=vouchers), YEAR)) == [
        (Severity.ERROR, "voucher-numbering", "voucher 2")
    ]


def test_each_series_is_numbered_separately() -> None:
    vouchers = (
        voucher(1, series="B"),
        voucher(1, series="K"),
        voucher(2, series="B"),
        voucher(2, series="K"),
    )

    assert check_books(books(vouchers=vouchers), YEAR) == []


def test_gap_within_a_series_is_an_error() -> None:
    vouchers = (voucher(1, series="B"), voucher(3, series="B"), voucher(1, series="K"))

    assert found(check_books(books(vouchers=vouchers), YEAR)) == [
        (Severity.ERROR, "voucher-numbering", "voucher B3")
    ]


# --- Voucher contents ------------------------------------------------------------------------


def test_voucher_account_must_be_in_the_chart() -> None:
    vouchers = (voucher(1), voucher(2, credit="3999"))

    assert found(check_books(books(vouchers=vouchers), YEAR)) == [
        (Severity.ERROR, "voucher-unknown-account", "voucher 2")
    ]


def test_same_account_cannot_be_debited_and_credited() -> None:
    vouchers = (voucher(1), voucher(2, debit="1930", credit="1930"))

    assert found(check_books(books(vouchers=vouchers), YEAR)) == [
        (Severity.ERROR, "voucher-same-account", "voucher 2")
    ]


def test_voucher_lines_must_balance() -> None:
    unbalanced = replace(
        voucher(2),
        lines=(
            PostingLine("6570", debit=Decimal("10")),
            PostingLine("1930", credit=Decimal("9")),
        ),
    )

    assert found(check_books(books(vouchers=(voucher(1), unbalanced)), YEAR)) == [
        (Severity.ERROR, "voucher-unbalanced", "voucher 2")
    ]


def test_zero_amount_is_an_error() -> None:
    vouchers = (voucher(1), voucher(2, amount="0"))

    assert found(check_books(books(vouchers=vouchers), YEAR)) == [
        (Severity.ERROR, "voucher-zero-amount", "voucher 2")
    ]


@pytest.mark.parametrize("text", ["", "   "])
def test_voucher_text_must_not_be_empty(text: str) -> None:
    vouchers = (voucher(1), voucher(2, text=text))

    assert found(check_books(books(vouchers=vouchers), YEAR)) == [
        (Severity.ERROR, "voucher-missing-text", "voucher 2")
    ]


def test_voucher_date_must_be_inside_the_fiscal_year() -> None:
    vouchers = (voucher(1), voucher(2, on=date(YEAR - 1, 12, 31)))

    assert found(check_books(books(vouchers=vouchers), YEAR)) == [
        (Severity.ERROR, "voucher-outside-fiscal-year", "voucher 2")
    ]


def test_fiscal_year_comes_from_the_caller() -> None:
    vouchers = (voucher(1, on=date(2025, 6, 1)), voucher(2, on=date(2025, 6, 2)))

    assert check_books(books(vouchers=vouchers), 2025) == []


# --- Personal identity numbers (warning, never quoted) ------------------------------------------


def test_personal_number_in_voucher_text_is_a_warning() -> None:
    vouchers = (voucher(1), voucher(2, text="Swish from 191212121212 Anna Exempel"))

    findings = check_books(books(vouchers=vouchers), YEAR)

    assert found(findings) == [(Severity.WARNING, "personal-number", "voucher 2")]
    rendered = findings[0].render()
    assert "191212121212" not in rendered
    assert "Anna" not in rendered


def test_no_finding_quotes_the_voucher_text() -> None:
    text = "Swish 121212-1212 Anna Exempel"
    vouchers = (
        voucher(1, text=text),
        voucher(3, text=text, amount="0"),
        voucher(4, text=text, on=date(YEAR + 1, 1, 1)),
        voucher(5, text=text, credit="3999"),
    )

    findings = check_books(books(vouchers=vouchers), YEAR)

    assert findings
    for finding in findings:
        assert "Anna" not in finding.render()
        assert "1212" not in finding.message
