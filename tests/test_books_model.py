"""Tests for the core book model (ADR-006): accounts, opening balances and vouchers."""

from datetime import date
from decimal import Decimal

import pytest

from accounting_agent.books import (
    Account,
    Books,
    OpeningBalance,
    PostingLine,
    Voucher,
)


def two_line_voucher(number: int = 1, amount: str = "200") -> Voucher:
    """Money in: debit the bank, credit a revenue account (a front-matter voucher)."""
    return Voucher(
        series=None,
        number=number,
        date=date(2026, 3, 5),
        text="Membership fee",
        lines=(
            PostingLine(account="1930", debit=Decimal(amount)),
            PostingLine(account="3002", credit=Decimal(amount)),
        ),
    )


def test_voucher_without_series_has_two_lines() -> None:
    voucher = two_line_voucher()

    assert voucher.series is None
    assert voucher.id == "1"
    assert len(voucher.lines) == 2
    assert voucher.total_debit == Decimal("200")
    assert voucher.total_credit == Decimal("200")
    assert voucher.is_balanced


def test_voucher_with_series_and_three_lines() -> None:
    voucher = Voucher(
        series="B",
        number=12,
        date=date(2026, 4, 1),
        text="Invoice paid, split over two cost accounts",
        lines=(
            PostingLine(account="5010", debit=Decimal("300.00")),
            PostingLine(account="6570", debit=Decimal("20.50")),
            PostingLine(account="1930", credit=Decimal("320.50")),
        ),
    )

    assert voucher.id == "B12"
    assert voucher.total_debit == voucher.total_credit == Decimal("320.50")
    assert voucher.is_balanced


def test_unbalanced_voucher_is_reported_as_unbalanced() -> None:
    voucher = Voucher(
        series=None,
        number=1,
        date=date(2026, 1, 2),
        text="Broken",
        lines=(
            PostingLine(account="1930", debit=Decimal("100")),
            PostingLine(account="3002", credit=Decimal("90")),
        ),
    )

    assert not voucher.is_balanced


def test_voucher_defaults_for_documents_note_and_source() -> None:
    voucher = two_line_voucher()

    assert voucher.documents == ()
    assert voucher.note == ""
    assert voucher.source == ""


def test_posting_line_defaults_to_zero_on_the_other_side() -> None:
    line = PostingLine(account="1930", debit=Decimal("5"))

    assert line.credit == Decimal("0")


def test_posting_line_cannot_have_both_debit_and_credit() -> None:
    with pytest.raises(ValueError, match="debit or credit"):
        PostingLine(account="1930", debit=Decimal("1"), credit=Decimal("1"))


@pytest.mark.parametrize("side", ["debit", "credit"])
def test_posting_line_amounts_cannot_be_negative(side: str) -> None:
    with pytest.raises(ValueError, match="negative"):
        PostingLine(account="1930", **{side: Decimal("-1")})


def test_posting_line_may_be_zero_so_a_zero_amount_can_be_reported() -> None:
    # A voucher with amount 0 must be representable; the checks report it (not the model).
    line = PostingLine(account="1930")

    assert line.debit == line.credit == Decimal("0")


def test_posting_line_rejects_floats() -> None:
    # Amounts are Decimal, never float (ADR-006).
    with pytest.raises(TypeError, match="Decimal"):
        PostingLine(account="1930", debit=200.0)  # type: ignore[arg-type]


def test_books_hold_duplicates_so_checks_can_report_them() -> None:
    # The model keeps what the files say; finding duplicates is the checks' job.
    books = Books(
        accounts=(Account("1930", "Bank"), Account("1930", "Bank again")),
        opening_balances=(
            OpeningBalance("1930", Decimal("100")),
            OpeningBalance("1930", Decimal("-100")),
        ),
        vouchers=(two_line_voucher(1), two_line_voucher(1)),
    )

    assert len(books.accounts) == 2
    assert len(books.opening_balances) == 2
    assert len(books.vouchers) == 2


def test_model_objects_are_immutable() -> None:
    voucher = two_line_voucher()

    with pytest.raises(AttributeError):
        voucher.number = 2  # type: ignore[misc]
