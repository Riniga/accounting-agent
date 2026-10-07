"""Tests for building vouchers with several lines, and without a bank transaction, on
model objects (MVP-005).

`build_voucher()` gets two more uses besides one account against the bank account:

- a bank transaction against several lines: the caller gives the other side, the bank
  line comes from the transaction, and the two must add up;
- a voucher without a bank transaction: the caller gives the date, the text and every
  line, and the bank account may not be among them.

The tests for one account against the bank account are in `test_posting.py`.
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
YEAR = 2026
MARKER = "Gissad kontering"
ACCOUNTS = (
    Account("1510", "Receivables"),
    Account(BANK, "Bank"),
    Account("2010", "Equity"),
    Account("2710", "Tax withheld"),
    Account("2731", "Employer's contribution, payable"),
    Account("2821", "Salaries payable"),
    Account("3010", "Invoiced services"),
    Account("7010", "Salaries"),
    Account("7510", "Employer's contribution"),
)
DOCUMENTS = frozenset({"payslip.md", "invoice-1.md"})
STATEMENT = (
    BankTransaction(date(2026, 1, 25), Decimal("-21000.00"), None, 2),
    BankTransaction(date(2026, 2, 10), Decimal("12500"), None, 3),
)
TEXTS = {2: "Salary payment", 3: "Customer(Invoice 1)"}


def d(text: str) -> date:
    return date.fromisoformat(text)


def debit(account: str, amount: str) -> PostingLine:
    return PostingLine(account, debit=Decimal(amount))


def credit(account: str, amount: str) -> PostingLine:
    return PostingLine(account, credit=Decimal(amount))


EXISTING = Voucher(
    series=None,
    number=3,
    date=d("2026-01-10"),
    text="Opening adjustment",
    lines=(debit("2010", "100"), credit("2821", "100")),
)


def build(request: VoucherRequest, *vouchers: Voucher) -> Voucher:
    books = Books(
        accounts=ACCOUNTS,
        opening_balances=(OpeningBalance(BANK, Decimal(0)),),
        vouchers=(EXISTING, *vouchers),
    )
    return build_voucher(
        books,
        STATEMENT,
        TEXTS,
        BANK,
        request,
        documents=DOCUMENTS,
        guessed_posting_marker=MARKER,
        fiscal_year=YEAR,
    )


def refusal(request: VoucherRequest, *vouchers: Voucher) -> str:
    """The rule of the refusal that ``request`` gives."""
    with pytest.raises(VoucherRefusedError) as raised:
        build(request, *vouchers)
    return raised.value.rule


def salary(*lines: PostingLine, **changes: object) -> VoucherRequest:
    """The bank transaction 2026-01-25, -21000, against ``lines``."""
    values: dict[str, object] = {
        "date": d("2026-01-25"),
        "amount": Decimal("-21000"),
        "lines": lines,
    }
    return VoucherRequest(**{**values, **changes})  # type: ignore[arg-type]


def journal(*lines: PostingLine, **changes: object) -> VoucherRequest:
    """A voucher without a bank transaction, dated 2026-01-31."""
    values: dict[str, object] = {
        "date": d("2026-01-31"),
        "text": "Invoice 1",
        "lines": lines,
    }
    return VoucherRequest(**{**values, **changes})  # type: ignore[arg-type]


GROSS_AND_TAX = (debit("7010", "30000"), credit("2710", "9000"))
INVOICE = (debit("1510", "12500"), credit("3010", "12500"))


# --- A bank transaction against several lines ------------------------------------


def test_money_out_gets_the_bank_line_last() -> None:
    voucher = build(salary(*GROSS_AND_TAX))

    assert voucher.lines == (
        debit("7010", "30000"),
        credit("2710", "9000"),
        credit(BANK, "21000.00"),
    )
    assert voucher.is_balanced


def test_money_in_gets_the_bank_line_first() -> None:
    request = VoucherRequest(
        date=d("2026-02-10"),
        amount=Decimal("12500"),
        lines=(credit("1510", "12000"), credit("3010", "500")),
    )

    assert build(request).lines == (
        debit(BANK, "12500"),
        credit("1510", "12000"),
        credit("3010", "500"),
    )


def test_date_text_and_number_still_come_from_the_files() -> None:
    voucher = build(salary(*GROSS_AND_TAX, documents=("payslip.md",), note="Paid."))

    assert voucher.date == d("2026-01-25")
    assert voucher.text == "Salary payment"
    assert voucher.number == 4
    assert voucher.documents == ("payslip.md",)
    assert voucher.note == "Paid."


def test_two_lines_on_the_same_account_are_kept() -> None:
    lines = (debit("7010", "20000"), debit("7010", "10000"), credit("2710", "9000"))

    assert build(salary(*lines)).lines[:2] == (
        debit("7010", "20000"),
        debit("7010", "10000"),
    )


@pytest.mark.parametrize(
    "lines",
    [
        (debit("7010", "30000"), credit("2710", "8000")),  # 22000, the bank says 21000
        (credit("7010", "30000"), debit("2710", "9000")),  # the sides are swapped
        (debit("7010", "21000.01"),),
    ],
    ids=["too-much", "swapped", "one-cent"],
)
def test_lines_must_add_up_to_the_bank_amount(lines: tuple[PostingLine, ...]) -> None:
    assert refusal(salary(*lines)) == "lines-unbalanced"


def test_one_line_against_the_bank_is_allowed() -> None:
    # The same voucher as --account 7010 would give.
    assert build(salary(debit("7010", "21000"))).lines == (
        debit("7010", "21000"),
        credit(BANK, "21000.00"),
    )


def test_bank_account_among_the_lines_is_refused() -> None:
    lines = (debit("7010", "30000"), credit("2710", "9000"), credit(BANK, "21000"))

    assert refusal(salary(*lines)) == "account-is-bank"


def test_unknown_account_on_a_line_is_refused() -> None:
    assert refusal(salary(debit("7999", "30000"), credit("2710", "9000"))) == (
        "account-unknown"
    )


def test_line_without_an_amount_is_refused() -> None:
    assert refusal(salary(debit("7010", "21000"), PostingLine("2710"))) == "line-amount"


def test_account_on_both_sides_is_refused() -> None:
    lines = (debit("7010", "30000"), credit("7010", "9000"))

    assert refusal(salary(*lines)) == "account-on-both-sides"


def test_account_and_lines_together_are_refused() -> None:
    assert refusal(salary(*GROSS_AND_TAX, account="7010")) == "account-and-lines"


def test_neither_account_nor_lines_is_refused() -> None:
    assert refusal(salary()) == "account-missing"


def test_text_cannot_be_given_for_a_bank_transaction() -> None:
    # The text comes from the bank statement.
    assert refusal(salary(*GROSS_AND_TAX, text="My own text")) == (
        "text-with-transaction"
    )


def test_bank_transaction_with_lines_can_be_booked_once() -> None:
    first = build(salary(*GROSS_AND_TAX))

    assert refusal(salary(*GROSS_AND_TAX), first) == "already-booked"


def test_guess_works_with_lines() -> None:
    voucher = build(salary(*GROSS_AND_TAX, note="the tax is unclear", guess=True))

    assert voucher.note == "Gissad kontering: the tax is unclear"


# --- A voucher without a bank transaction ----------------------------------------


def test_voucher_without_a_bank_transaction_is_the_callers() -> None:
    voucher = build(journal(*INVOICE, documents=("invoice-1.md",), note="Sent."))

    assert voucher.date == d("2026-01-31")
    assert voucher.text == "Invoice 1"
    assert voucher.lines == INVOICE
    assert voucher.number == 4
    assert voucher.documents == ("invoice-1.md",)
    assert voucher.note == "Sent."


def test_many_lines_are_kept_in_the_callers_order() -> None:
    lines = (
        credit("2710", "16500"),
        debit("7010", "30000.50"),
        debit("7010", "25000"),
        debit("7510", "17281.66"),
        credit("2731", "17281.66"),
        credit("2821", "38500.50"),
    )

    assert build(journal(*lines, text="Salaries January")).lines == lines


def test_text_and_note_are_masked() -> None:
    request = journal(
        *INVOICE, text="Invoice to 19121212-1212", note="See 191212121212."
    )

    voucher = build(request)

    assert voucher.text == "Invoice to [personnummer]"
    assert voucher.note == "See [personnummer]."


@pytest.mark.parametrize("text", ["", "   "])
def test_text_is_required(text: str) -> None:
    assert refusal(journal(*INVOICE, text=text)) == "text-missing"


@pytest.mark.parametrize(
    "lines",
    [(), (debit("1510", "12500"),)],
    ids=["none", "one"],
)
def test_at_least_two_lines_are_required(lines: tuple[PostingLine, ...]) -> None:
    assert refusal(journal(*lines)) == "lines-missing"


def test_lines_must_balance() -> None:
    lines = (debit("1510", "12500"), credit("3010", "12000"))

    assert refusal(journal(*lines)) == "lines-unbalanced"


def test_bank_account_needs_a_bank_transaction() -> None:
    # Otherwise the bank's balance could be changed without the bank agreeing.
    lines = (debit(BANK, "12500"), credit("3010", "12500"))

    assert refusal(journal(*lines)) == "bank-without-transaction"


def test_unknown_account_is_refused() -> None:
    lines = (debit("1599", "12500"), credit("3010", "12500"))

    assert refusal(journal(*lines)) == "account-unknown"


def test_line_of_zero_is_refused() -> None:
    lines = (debit("1510", "12500"), credit("3010", "12500"), PostingLine("2821"))

    assert refusal(journal(*lines)) == "line-amount"


def test_same_account_on_both_sides_is_refused() -> None:
    lines = (debit("1510", "12500"), credit("1510", "12500"))

    assert refusal(journal(*lines)) == "account-on-both-sides"


@pytest.mark.parametrize("day", ["2025-12-31", "2027-01-01"])
def test_date_must_be_in_the_fiscal_year(day: str) -> None:
    assert refusal(journal(*INVOICE, date=d(day))) == "date-outside-year"


def test_account_or_row_needs_a_bank_transaction() -> None:
    assert refusal(journal(*INVOICE, account="3010")) == "amount-missing"
    assert refusal(journal(*INVOICE, row=3)) == "amount-missing"


def test_documents_and_guess_follow_the_same_rules() -> None:
    assert refusal(journal(*INVOICE, documents=("missing.md",))) == "document-missing"
    assert refusal(journal(*INVOICE, guess=True)) == "guess-without-reason"


# --- The same voucher twice ------------------------------------------------------


def test_same_date_text_and_lines_is_refused() -> None:
    first = build(journal(*INVOICE))

    assert refusal(journal(*INVOICE), first) == "duplicate"


def test_lines_in_another_order_are_the_same_voucher() -> None:
    first = build(journal(*INVOICE))

    assert refusal(journal(INVOICE[1], INVOICE[0]), first) == "duplicate"


@pytest.mark.parametrize(
    "changes",
    [
        {"date": d("2026-02-01")},
        {"text": "Invoice 2"},
        {"lines": (debit("1510", "12501"), credit("3010", "12501"))},
    ],
    ids=["date", "text", "amount"],
)
def test_another_date_text_or_amount_is_another_voucher(
    changes: dict[str, object],
) -> None:
    first = build(journal(*INVOICE))
    other = {key: value for key, value in changes.items() if key != "lines"}
    lines = changes.get("lines", INVOICE)

    request = journal(*lines, **other)  # type: ignore[misc]

    assert build(request, first).number == 5


# --- Refusals never quote texts or names -----------------------------------------


@pytest.mark.parametrize(
    "request_",
    [
        journal(*INVOICE, text="Secret Person", date=d("2027-01-01")),
        journal(debit("1510", "1"), credit("3010", "2"), text="Secret Person"),
        journal(debit(BANK, "1"), credit("3010", "1"), text="Secret Person"),
        salary(debit("7010", "1"), note="Secret Person"),
    ],
    ids=["date", "unbalanced", "bank", "bank-amount"],
)
def test_refusal_message_quotes_no_text_or_note(request_: VoucherRequest) -> None:
    with pytest.raises(VoucherRefusedError) as raised:
        build(request_)

    assert str(raised.value)
    assert "Secret" not in str(raised.value)


def test_duplicate_refusal_names_the_voucher_number_only() -> None:
    first = build(journal(*INVOICE, text="Secret Person"))

    with pytest.raises(VoucherRefusedError) as raised:
        build(journal(*INVOICE, text="Secret Person"), first)

    assert "Secret" not in str(raised.value)
    assert "voucher 4" in str(raised.value)
