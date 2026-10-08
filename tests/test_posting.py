"""Tests for building a new voucher from a bank transaction, on model objects (ADR-009).

The caller supplies decisions only: which bank transaction, the counter account, the
supporting documents, a note and whether the posting is a guess. The date, the amount,
the text and the number come from the books and the bank statement. A request that
cannot give a right voucher is refused, and a refusal never quotes a text or a name.
"""

from datetime import date
from decimal import Decimal

import pytest

from accounting_agent.books import (
    Account,
    BankTransaction,
    Books,
    OpeningBalance,
    PostingLine,
    Voucher,
    VoucherRefusedError,
    VoucherRequest,
    build_voucher,
)

BANK = "1930"
MARKER = "Gissad kontering"
ACCOUNTS = (
    Account(BANK, "Bank"),
    Account("2010", "Equity"),
    Account("3001", "Training fees"),
    Account("3002", "Membership fees"),
    Account("5010", "Rent"),
    Account("6570", "Bank charges"),
)
DOCUMENTS = frozenset({"20260301-invoice.pdf", "20260301-receipt (Anna).jpg"})


def d(text: str) -> date:
    return date.fromisoformat(text)


def transaction(row: int, day: str, amount: str) -> BankTransaction:
    return BankTransaction(date=d(day), amount=Decimal(amount), balance=None, row=row)


def booked(number: int, day: str, amount: str, account: str, text: str) -> Voucher:
    """An existing voucher on the bank account, signed as the bank shows it."""
    value = Decimal(amount)
    if value > 0:
        lines = (PostingLine(BANK, debit=value), PostingLine(account, credit=value))
    else:
        lines = (PostingLine(account, debit=-value), PostingLine(BANK, credit=-value))
    return Voucher(series=None, number=number, date=d(day), text=text, lines=lines)


def books(*vouchers: Voucher) -> Books:
    return Books(
        accounts=ACCOUNTS,
        opening_balances=(OpeningBalance(BANK, Decimal(0)),),
        vouchers=vouchers,
    )


# Rows 2–4 are the statement's data rows; row 1 is the header.
STATEMENT = (
    transaction(2, "2026-03-01", "-458.00"),
    transaction(3, "2026-03-02", "600"),
    transaction(4, "2026-03-02", "600"),
    transaction(5, "2026-03-02", "600"),
)
TEXTS = {
    2: "Landlord(Rent March)",
    3: "Payer One(Child A)",
    4: "Payer Two(Child B)",
    5: "Payer One(Child A)",
}
EXISTING = booked(7, "2026-02-01", "-130", "6570", "Bank(Fee)")


def build(
    request: VoucherRequest,
    *vouchers: Voucher,
    documents: frozenset[str] | None = DOCUMENTS,
    marker: str | None = MARKER,
) -> Voucher:
    return build_voucher(
        books(EXISTING, *vouchers),
        STATEMENT,
        TEXTS,
        BANK,
        request,
        documents=documents,
        guessed_posting_marker=marker,
    )


def refusal(
    request: VoucherRequest,
    *vouchers: Voucher,
    documents: frozenset[str] | None = DOCUMENTS,
    marker: str | None = MARKER,
) -> str:
    """The rule of the refusal that ``request`` gives."""
    with pytest.raises(VoucherRefusedError) as raised:
        build(request, *vouchers, documents=documents, marker=marker)
    return raised.value.rule


RENT = VoucherRequest(date=d("2026-03-01"), amount=Decimal("-458"), account="5010")
FEE = VoucherRequest(date=d("2026-03-02"), amount=Decimal("600"), account="3001")


def fee(row: int | None) -> VoucherRequest:
    return VoucherRequest(
        date=FEE.date, amount=FEE.amount, account=FEE.account, row=row
    )


# --- What the voucher gets from the files ----------------------------------------


def test_money_out_debits_the_account_and_credits_the_bank() -> None:
    voucher = build(RENT)

    assert voucher.lines == (
        PostingLine("5010", debit=Decimal("458.00")),
        PostingLine(BANK, credit=Decimal("458.00")),
    )


def test_money_in_debits_the_bank_and_credits_the_account() -> None:
    voucher = build(fee(3))

    assert voucher.lines == (
        PostingLine(BANK, debit=Decimal("600")),
        PostingLine("3001", credit=Decimal("600")),
    )


def test_date_text_and_number_come_from_the_files() -> None:
    voucher = build(RENT)

    assert voucher.date == d("2026-03-01")
    assert voucher.text == "Landlord(Rent March)"
    assert voucher.number == 8  # the highest number plus one
    assert voucher.series is None
    assert voucher.documents == ()
    assert voucher.note == ""


def test_first_voucher_of_the_year_gets_number_one() -> None:
    voucher = build_voucher(
        Books(accounts=ACCOUNTS, opening_balances=(), vouchers=()),
        STATEMENT,
        TEXTS,
        BANK,
        RENT,
    )

    assert voucher.number == 1


def test_amount_is_matched_by_value_not_by_how_it_is_written() -> None:
    # The statement says -458.00; the caller wrote -458.
    assert build(RENT).total_debit == Decimal("458.00")


def test_documents_and_note_are_the_callers() -> None:
    request = VoucherRequest(
        date=RENT.date,
        amount=RENT.amount,
        account="5010",
        documents=("20260301-invoice.pdf", "20260301-receipt (Anna).jpg"),
        note="Rent for March.",
    )

    voucher = build(request)

    assert voucher.documents == ("20260301-invoice.pdf", "20260301-receipt (Anna).jpg")
    assert voucher.note == "Rent for March."


def test_personal_numbers_are_masked_in_text_and_note() -> None:
    request = VoucherRequest(
        date=RENT.date,
        amount=RENT.amount,
        account="5010",
        note="Paid by 19121212-1212.",
    )

    voucher = build_voucher(
        books(), STATEMENT, {2: "Landlord(191212121212)"}, BANK, request
    )

    assert voucher.text == "Landlord([personnummer])"
    assert voucher.note == "Paid by [personnummer]."


# --- A guess stays a guess -------------------------------------------------------


def test_guess_puts_the_marker_before_the_reason() -> None:
    request = VoucherRequest(
        date=RENT.date,
        amount=RENT.amount,
        account="5010",
        note="the landlord's name only",
        guess=True,
    )

    assert build(request).note == "Gissad kontering: the landlord's name only"


def test_guess_needs_a_reason() -> None:
    request = VoucherRequest(
        date=RENT.date, amount=RENT.amount, account="5010", guess=True
    )

    assert refusal(request) == "guess-without-reason"


def test_guess_needs_a_configured_marker() -> None:
    request = VoucherRequest(
        date=RENT.date, amount=RENT.amount, account="5010", note="why", guess=True
    )

    assert refusal(request, marker=None) == "guess-marker-missing"


# --- Which bank transaction ------------------------------------------------------


def test_no_transaction_with_that_date_and_amount_is_refused() -> None:
    request = VoucherRequest(
        date=d("2026-03-01"), amount=Decimal("-459"), account="5010"
    )

    assert refusal(request) == "transaction-missing"


def test_already_booked_transaction_is_refused() -> None:
    existing = booked(8, "2026-03-01", "-458", "5010", "Landlord(Rent March)")

    assert refusal(RENT, existing) == "already-booked"


def test_several_equal_transactions_need_the_row() -> None:
    assert refusal(fee(None)) == "transaction-ambiguous"


def test_row_selects_among_equal_transactions() -> None:
    assert build(fee(4)).text == "Payer Two(Child B)"


def test_row_with_another_date_or_amount_is_refused() -> None:
    assert refusal(fee(2)) == "row-mismatch"
    assert refusal(fee(99)) == "row-mismatch"


def test_row_is_checked_also_when_only_one_transaction_matches() -> None:
    request = VoucherRequest(date=RENT.date, amount=RENT.amount, account="5010", row=3)

    assert refusal(request) == "row-mismatch"


def test_row_that_already_has_a_voucher_is_refused() -> None:
    # Row 4 is booked; rows 3 and 5 are not.
    existing = booked(8, "2026-03-02", "600", "3001", "Payer Two(Child B)")

    assert refusal(fee(4), existing) == "already-booked"
    assert build(fee(3), existing).text == "Payer One(Child A)"


def test_equal_transactions_with_equal_texts_are_booked_one_by_one() -> None:
    # Rows 3 and 5 have the same date, amount and text: the same payer paid twice.
    first = booked(8, "2026-03-02", "600", "3001", "Payer One(Child A)")
    second = booked(9, "2026-03-02", "600", "3001", "Payer One(Child A)")

    assert build(fee(5), first).number == 9
    assert refusal(fee(5), first, second) == "already-booked"


def test_all_equal_transactions_booked_is_refused_whatever_their_texts() -> None:
    # The texts were edited by hand, but three vouchers cover the three transactions.
    edited = [
        booked(8 + i, "2026-03-02", "600", "3001", f"Edited {i}") for i in range(3)
    ]

    assert refusal(fee(3), *edited) == "already-booked"


def test_voucher_that_is_not_on_the_bank_account_does_not_count_as_booked() -> None:
    # Same date and amount, but it moves money between two other accounts.
    transfer = Voucher(
        series=None,
        number=8,
        date=d("2026-03-01"),
        text="Transfer",
        lines=(
            PostingLine("5010", debit=Decimal("458")),
            PostingLine("2010", credit=Decimal("458")),
        ),
    )

    assert build(RENT, transfer).number == 9


# --- The account -----------------------------------------------------------------


def test_account_must_be_in_the_chart() -> None:
    request = VoucherRequest(date=RENT.date, amount=RENT.amount, account="5999")

    assert refusal(request) == "account-unknown"


def test_account_cannot_be_the_bank_account() -> None:
    request = VoucherRequest(date=RENT.date, amount=RENT.amount, account=BANK)

    assert refusal(request) == "account-is-bank"


# --- Supporting documents --------------------------------------------------------


def test_document_must_be_in_the_documents_folder() -> None:
    request = VoucherRequest(
        date=RENT.date,
        amount=RENT.amount,
        account="5010",
        documents=("20260301-invoice.pdf", "missing.pdf"),
    )

    assert refusal(request) == "document-missing"


@pytest.mark.parametrize("name", ["../secret.pdf", "/etc/passwd", "C:\\secret.pdf"])
def test_document_outside_the_folder_is_refused(name: str) -> None:
    request = VoucherRequest(
        date=RENT.date, amount=RENT.amount, account="5010", documents=(name,)
    )

    assert refusal(request) == "document-missing"


def test_document_without_a_configured_folder_is_refused() -> None:
    request = VoucherRequest(
        date=RENT.date,
        amount=RENT.amount,
        account="5010",
        documents=("20260301-invoice.pdf",),
    )

    assert refusal(request, documents=None) == "documents-not-configured"


def test_document_name_with_the_field_separator_is_refused() -> None:
    # The field separates documents with a semicolon; such a name cannot be written.
    request = VoucherRequest(
        date=RENT.date, amount=RENT.amount, account="5010", documents=("a;b.pdf",)
    )

    assert refusal(request, documents=frozenset({"a;b.pdf"})) == "document-name"


def test_same_document_twice_is_refused() -> None:
    request = VoucherRequest(
        date=RENT.date,
        amount=RENT.amount,
        account="5010",
        documents=("20260301-invoice.pdf", "20260301-invoice.pdf"),
    )

    assert refusal(request) == "document-twice"


def test_no_folder_is_needed_without_documents() -> None:
    assert build(RENT, documents=None).documents == ()


# --- Refusals never quote texts or names -----------------------------------------


@pytest.mark.parametrize(
    "request_",
    [
        VoucherRequest(date=d("2026-03-01"), amount=Decimal("-459"), account="5010"),
        fee(None),
        fee(2),
        VoucherRequest(date=RENT.date, amount=RENT.amount, account="5999"),
        VoucherRequest(
            date=RENT.date,
            amount=RENT.amount,
            account="5010",
            documents=("20260301-receipt (Bertil).jpg",),
            note="Secret note",
        ),
    ],
    ids=["missing", "ambiguous", "row", "account", "document"],
)
def test_refusal_message_quotes_no_text_name_or_file_name(
    request_: VoucherRequest,
) -> None:
    with pytest.raises(VoucherRefusedError) as raised:
        build(request_)

    message = str(raised.value)
    assert message
    for secret in ("Payer", "Child", "Landlord", "Bertil", "Secret", ".jpg", "Rent"):
        assert secret not in message
