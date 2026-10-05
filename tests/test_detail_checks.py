"""Tests for the detail checks from `kontroll.py` that MVP-002 deferred, on model objects.

They are the MVP-003 plan's phase 5: duplicates, date order, revenue/cost-account sides,
supporting documents, parking accounts, unused accounts and the chart's own rules. No
message quotes a voucher's text, an account's name or a document's file name.
"""

from datetime import date
from decimal import Decimal

from accounting_agent.books import (
    Account,
    Books,
    Finding,
    OpeningBalance,
    PostingLine,
    Severity,
    Voucher,
    check_details,
)

BANK = "1930"
ACCOUNTS = (
    Account(BANK, "Bank"),
    Account("2010", "Equity"),
    Account("3002", "Membership fees"),
    Account("3008", "Unspecified income"),
    Account("5010", "Rent"),
    Account("6570", "Bank charges"),
)
OPENING = (
    OpeningBalance(BANK, Decimal("100.00")),
    OpeningBalance("2010", Decimal("-100.00")),
)
SENSITIVE_TEXT = "Swish Hemlig Exempelperson"
SENSITIVE_DOCUMENT = "kvitto-hemlig-exempelperson.pdf"


def voucher(
    number: int,
    *,
    debit: str = BANK,
    credit: str = "3002",
    amount: str = "200.00",
    text: str = "Membership fee",
    on: str = "2026-03-10",
    documents: tuple[str, ...] = ("receipt.pdf",),
) -> Voucher:
    value = Decimal(amount)
    return Voucher(
        series=None,
        number=number,
        date=date.fromisoformat(on),
        text=text,
        lines=(PostingLine(debit, debit=value), PostingLine(credit, credit=value)),
        documents=documents,
    )


# Every account used, dates in order, every voucher with a document that exists.
CLEAN = (
    voucher(1, on="2026-01-10"),
    voucher(
        2, debit="5010", credit=BANK, amount="500.00", text="Rent", on="2026-03-01"
    ),
    voucher(3, debit="6570", credit=BANK, amount="10.00", text="Fee", on="2026-03-01"),
    voucher(4, credit="3008", amount="75.00", text="Unknown payment", on="2026-03-02"),
)
DOCUMENTS = frozenset({"receipt.pdf"})


def books(*vouchers: Voucher, accounts: tuple[Account, ...] = ACCOUNTS) -> Books:
    return Books(accounts=accounts, opening_balances=OPENING, vouchers=vouchers)


def check(
    b: Books,
    parking: tuple[str, ...] = (),
    documents: frozenset[str] | None = DOCUMENTS,
) -> list[Finding]:
    return check_details(b, BANK, parking_accounts=parking, documents=documents)


def rules(findings: list[Finding]) -> list[str]:
    return sorted(f.rule for f in findings)


def test_clean_books_give_no_findings() -> None:
    assert check(books(*CLEAN)) == []


# --- Duplicates -------------------------------------------------------------------------


def test_same_date_text_and_bank_amount_is_a_duplicate_warning() -> None:
    duplicate = voucher(5, text=SENSITIVE_TEXT)
    original = voucher(6, text=SENSITIVE_TEXT)

    findings = check(books(*CLEAN, duplicate, original))

    assert findings == [
        Finding(
            Severity.WARNING,
            "voucher-duplicate",
            "voucher 5, 6",
            "same date, amount and text (2026-03-10, 200.00)",
        )
    ]


def test_money_in_and_money_out_of_the_same_size_are_not_duplicates() -> None:
    # The amount is signed as the bank shows it, as in kontroll.py.
    money_in = voucher(5, text="Correction")
    money_out = voucher(6, debit="3002", credit=BANK, text="Correction")

    assert "voucher-duplicate" not in rules(check(books(*CLEAN, money_in, money_out)))


def test_different_text_is_not_a_duplicate() -> None:
    findings = check(books(*CLEAN, voucher(5, text="A"), voucher(6, text="B")))

    assert "voucher-duplicate" not in rules(findings)


# --- Date order -------------------------------------------------------------------------


def test_voucher_dated_before_the_previous_one_is_a_warning() -> None:
    late = voucher(5, on="2026-02-01", text="Late entry")

    findings = check(books(*CLEAN, late))

    assert findings == [
        Finding(
            Severity.WARNING,
            "voucher-date-order",
            "voucher 5",
            "date 2026-02-01 is earlier than the previous voucher (2026-03-02)",
        )
    ]


# --- Revenue and cost accounts on the unexpected side -----------------------------------


def test_revenue_account_debited_is_a_warning() -> None:
    refund = voucher(5, debit="3002", credit=BANK, amount="50.00", text="Refund")

    findings = check(books(*CLEAN, refund))

    assert findings == [
        Finding(
            Severity.WARNING,
            "revenue-account-debited",
            "voucher 5",
            "revenue account 3002 is debited (50.00); is that right?",
        )
    ]


def test_cost_account_credited_is_a_warning() -> None:
    credit_note = voucher(5, debit=BANK, credit="5010", amount="80.00", text="Credit")

    findings = check(books(*CLEAN, credit_note))

    assert findings == [
        Finding(
            Severity.WARNING,
            "cost-account-credited",
            "voucher 5",
            "cost account 5010 is credited (80.00); is that right?",
        )
    ]


# --- Supporting documents ---------------------------------------------------------------


def test_missing_supporting_document_is_an_error_without_its_name() -> None:
    v = voucher(5, text="Hall", documents=("receipt.pdf", SENSITIVE_DOCUMENT))

    findings = check(books(*CLEAN, v))

    assert findings == [
        Finding(
            Severity.ERROR,
            "document-missing",
            "voucher 5",
            "supporting document 2 of 2 is not in the documents folder",
        )
    ]


def test_documents_in_a_subfolder_are_found_by_relative_path() -> None:
    v = voucher(5, text="Hall", documents=("2026/receipt.pdf",))

    assert check(books(*CLEAN, v), documents=DOCUMENTS | {"2026/receipt.pdf"}) == []


def test_without_a_documents_folder_existence_is_not_checked() -> None:
    v = voucher(5, text="Hall", documents=(SENSITIVE_DOCUMENT,))

    assert "document-missing" not in rules(check(books(*CLEAN, v), documents=None))


def test_vouchers_without_documents_are_summarised() -> None:
    no_document_income = voucher(5, text="Fee", documents=())
    no_document_cost = voucher(6, debit="5010", credit=BANK, text="Rent", documents=())

    findings = check(books(*CLEAN, no_document_income, no_document_cost))

    # The payment is also named on its own since MVP-004 (test_document_checks.py).
    assert findings == [
        Finding(
            Severity.WARNING,
            "documents-expected",
            "voucher 6",
            "money out of the bank without a supporting document",
        ),
        Finding(
            Severity.INFO,
            "documents-summary",
            "vouchers",
            "2 of 6 vouchers have no supporting document (of which 1 costs)",
        ),
    ]


# --- Parking accounts -------------------------------------------------------------------


def test_postings_on_a_parking_account_are_summarised() -> None:
    parked_again = voucher(5, credit="3008", amount="25.00", text="Unknown 2")

    findings = check(books(*CLEAN, parked_again), parking=("3008",))

    assert findings == [
        Finding(
            Severity.INFO,
            "parking-summary",
            "account 3008",
            "2 postings, net 100.00 to distribute (should be 0 at closing)",
        )
    ]


def test_unused_parking_account_gives_no_summary() -> None:
    assert check(books(*CLEAN), parking=("2010",)) == []


# --- Unused accounts --------------------------------------------------------------------


def test_unused_accounts_are_listed() -> None:
    accounts = (*ACCOUNTS, Account("4010", "Goods"), Account("1910", "Cash"))

    findings = check(books(*CLEAN, accounts=accounts))

    assert findings == [
        Finding(
            Severity.INFO,
            "unused-accounts",
            "chart of accounts",
            "unused accounts: 1910, 4010",
        )
    ]


def test_an_account_with_only_an_opening_balance_is_used() -> None:
    # 2010 has an opening balance but no postings in CLEAN.
    assert "unused-accounts" not in rules(check(books(*CLEAN)))


# --- The chart's own rules --------------------------------------------------------------


def test_account_twice_in_the_chart_is_a_warning() -> None:
    accounts = (*ACCOUNTS, Account("5010", "Another name"))

    findings = check(books(*CLEAN, accounts=accounts))

    assert findings == [
        Finding(
            Severity.WARNING,
            "account-duplicate",
            "account 5010",
            "appears more than once in the chart of accounts",
        )
    ]


def test_account_without_a_name_is_an_error() -> None:
    accounts = tuple(
        Account(a.number, "  ") if a.number == "6570" else a for a in ACCOUNTS
    )

    findings = check(books(*CLEAN, accounts=accounts))

    assert findings == [
        Finding(Severity.ERROR, "account-missing-name", "account 6570", "has no name")
    ]


# --- No message quotes data -------------------------------------------------------------


def test_no_message_quotes_a_text_a_name_or_a_document() -> None:
    accounts = (*ACCOUNTS, Account("5010", SENSITIVE_TEXT))
    vouchers = (
        *CLEAN,
        voucher(5, text=SENSITIVE_TEXT, documents=(SENSITIVE_DOCUMENT,)),
        voucher(6, text=SENSITIVE_TEXT, documents=(SENSITIVE_DOCUMENT,)),
        voucher(7, debit="3002", credit=BANK, text=SENSITIVE_TEXT, on="2026-01-01"),
    )

    findings = check(books(*vouchers, accounts=accounts), parking=("3008",))

    assert len(findings) >= 6
    for finding in findings:
        assert SENSITIVE_TEXT not in finding.render()
        assert SENSITIVE_DOCUMENT not in finding.render()
