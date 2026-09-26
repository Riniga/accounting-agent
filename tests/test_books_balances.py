"""Tests for account balances: opening balance plus postings (debit +, credit −)."""

from datetime import date
from decimal import Decimal

from accounting_agent.books import (
    Account,
    Books,
    OpeningBalance,
    PostingLine,
    Voucher,
    compute_balances,
)


def voucher(number: int, *lines: PostingLine) -> Voucher:
    return Voucher(
        series=None, number=number, date=date(2026, 5, 1), text="x", lines=lines
    )


def test_balances_add_postings_to_opening_balances() -> None:
    books = Books(
        accounts=(
            Account("1930", "Bank"),
            Account("2010", "Equity"),
            Account("3002", "Fees"),
            Account("6570", "Bank charges"),
        ),
        opening_balances=(
            OpeningBalance("1930", Decimal("1000.00")),
            OpeningBalance("2010", Decimal("-1000.00")),
        ),
        vouchers=(
            voucher(
                1,
                PostingLine("1930", debit=Decimal("200")),
                PostingLine("3002", credit=Decimal("200")),
            ),
            voucher(
                2,
                PostingLine("6570", debit=Decimal("12.50")),
                PostingLine("1930", credit=Decimal("12.50")),
            ),
        ),
    )

    balances = compute_balances(books)

    assert balances == {
        "1930": Decimal("1187.50"),
        "2010": Decimal("-1000.00"),
        "3002": Decimal("-200"),
        "6570": Decimal("12.50"),
    }


def test_account_with_only_an_opening_balance_keeps_it() -> None:
    books = Books(
        accounts=(Account("1350", "Fund"),),
        opening_balances=(OpeningBalance("1350", Decimal("5000")),),
        vouchers=(),
    )

    assert compute_balances(books) == {"1350": Decimal("5000")}


def test_account_used_only_in_vouchers_starts_from_zero() -> None:
    books = Books(
        accounts=(),
        opening_balances=(),
        vouchers=(
            voucher(
                1,
                PostingLine("4010", debit=Decimal("99.90")),
                PostingLine("1930", credit=Decimal("99.90")),
            ),
        ),
    )

    assert compute_balances(books) == {
        "4010": Decimal("99.90"),
        "1930": Decimal("-99.90"),
    }


def test_balances_are_exact_decimals() -> None:
    # 0.1 + 0.2 must be exactly 0.3 — the reason amounts are never floats.
    books = Books(
        accounts=(),
        opening_balances=(),
        vouchers=(
            voucher(
                1,
                PostingLine("6570", debit=Decimal("0.1")),
                PostingLine("1930", credit=Decimal("0.1")),
            ),
            voucher(
                2,
                PostingLine("6570", debit=Decimal("0.2")),
                PostingLine("1930", credit=Decimal("0.2")),
            ),
        ),
    )

    assert compute_balances(books)["6570"] == Decimal("0.3")


def test_empty_books_have_no_balances() -> None:
    assert compute_balances(Books(accounts=(), opening_balances=(), vouchers=())) == {}
