"""Tests for reconciling the books against the bank statement, on model objects.

The rules follow Helsingborgs Judoklubb's `kontroll.py` (MVP-003 plan §0.3). A bank
transaction in the core has no counterparty name or message (ADR-007), so no finding can
quote one.
"""

from dataclasses import fields
from datetime import date
from decimal import Decimal

from accounting_agent.books import (
    Account,
    BankTransaction,
    Books,
    Finding,
    OpeningBalance,
    PostingLine,
    Severity,
    Voucher,
    reconcile,
)

BANK = "1930"
ACCOUNTS = (
    Account(BANK, "Bank"),
    Account("2010", "Equity"),
    Account("2890", "Liabilities"),
    Account("3001", "Training fees"),
    Account("3002", "Membership fees"),
    Account("6570", "Bank charges"),
)


def d(text: str) -> date:
    return date.fromisoformat(text)


def money_out(number: int, day: str, amount: str, account: str = "6570") -> Voucher:
    value = Decimal(amount)
    return Voucher(
        series=None,
        number=number,
        date=d(day),
        text="Payment",
        lines=(PostingLine(account, debit=value), PostingLine(BANK, credit=value)),
    )


def money_in(number: int, day: str, amount: str, account: str = "3002") -> Voucher:
    value = Decimal(amount)
    return Voucher(
        series=None,
        number=number,
        date=d(day),
        text="Income",
        lines=(PostingLine(BANK, debit=value), PostingLine(account, credit=value)),
    )


def transfer(number: int, day: str) -> Voucher:
    """A voucher that does not touch the bank."""
    value = Decimal("50.00")
    return Voucher(
        series=None,
        number=number,
        date=d(day),
        text="Transfer",
        lines=(PostingLine("2890", debit=value), PostingLine("2010", credit=value)),
    )


def books(*vouchers: Voucher, opening_bank: str = "1000.00") -> Books:
    return Books(
        accounts=ACCOUNTS,
        opening_balances=(
            OpeningBalance(BANK, Decimal(opening_bank)),
            OpeningBalance("2010", -Decimal(opening_bank)),
        ),
        vouchers=vouchers,
    )


def tx(row: int, day: str, amount: str, balance: str | None) -> BankTransaction:
    return BankTransaction(
        date=d(day),
        amount=Decimal(amount),
        balance=None if balance is None else Decimal(balance),
        row=row,
    )


# The clean case: opening balance 1000.00, two bank transactions, both booked, and a
# voucher that does not touch the bank.
BOOKED = (
    money_out(1, "2026-01-07", "130.00"),
    money_in(2, "2026-01-15", "200.00"),
    transfer(3, "2026-02-10"),
)
STATEMENT = (
    tx(2, "2026-01-07", "-130.00", "870.00"),
    tx(3, "2026-01-15", "200.00", "1070.00"),
)
SUMMARY = Finding(
    Severity.INFO,
    "bank-summary",
    "bank statement",
    "2 transactions 2026-01-07 to 2026-01-15, "
    "the bank's latest balance 1070.00 (2026-01-15)",
)


def rules(findings: list[Finding]) -> list[str]:
    return [f.rule for f in findings]


def test_bank_transaction_holds_no_name_or_message() -> None:
    # Structural: nothing built on the model can quote a counterparty (ADR-007).
    assert {f.name for f in fields(BankTransaction)} == {
        "date",
        "amount",
        "balance",
        "row",
    }


def test_books_that_match_the_bank_give_only_the_summary() -> None:
    assert reconcile(books(*BOOKED), STATEMENT, BANK) == [SUMMARY]


def test_no_transactions_give_no_findings() -> None:
    assert reconcile(books(*BOOKED), (), BANK) == []


# --- The bank's own arithmetic ----------------------------------------------------------


def test_balance_that_does_not_follow_from_the_movements_is_an_error() -> None:
    statement = (STATEMENT[0], tx(3, "2026-01-15", "200.00", "1071.00"))

    findings = reconcile(books(*BOOKED), statement, BANK)

    assert findings[0] == Finding(
        Severity.ERROR,
        "bank-balance",
        "bank statement 2026-01-15",
        "balance 1071.00 does not follow from the earlier balance and movements "
        "(expected 1070.00)",
    )


def test_transactions_without_a_balance_are_counted_but_not_checked() -> None:
    statement = (STATEMENT[0], tx(3, "2026-01-15", "200.00", None))

    findings = reconcile(books(*BOOKED), statement, BANK)

    assert rules(findings) == ["bank-summary"]
    assert "latest balance 870.00 (2026-01-07)" in findings[0].message


def test_several_transactions_on_one_day_use_the_day_end_balance() -> None:
    vouchers = (*BOOKED, money_in(4, "2026-01-15", "30.00"))
    statement = (*STATEMENT, tx(4, "2026-01-15", "30.00", "1100.00"))

    assert rules(reconcile(books(*vouchers), statement, BANK)) == ["bank-summary"]


# --- Opening balance against the bank ---------------------------------------------------


def test_opening_balance_must_equal_the_bank_balance_before_the_year() -> None:
    findings = reconcile(books(*BOOKED, opening_bank="900.00"), STATEMENT, BANK)

    assert (
        Finding(
            Severity.ERROR,
            "bank-opening-balance",
            f"opening balance {BANK}",
            "opening balance is 900.00 but the bank's balance before 2026-01-07 was "
            "1000.00 (difference -100.00)",
        )
        in findings
    )


def test_no_bank_opening_balance_means_no_opening_check() -> None:
    no_opening = Books(accounts=ACCOUNTS, opening_balances=(), vouchers=BOOKED)

    assert rules(reconcile(no_opening, STATEMENT, BANK)) == ["bank-summary"]


# --- Every bank voucher in the statement ------------------------------------------------


def test_booked_bank_voucher_missing_from_the_statement_is_an_error() -> None:
    vouchers = (*BOOKED, money_out(4, "2026-02-20", "50.00"))

    findings = reconcile(books(*vouchers), STATEMENT, BANK)

    assert (
        Finding(
            Severity.ERROR,
            "bank-missing-transaction",
            "voucher 4",
            "2026-02-20, -50.00 is in the books but not in the bank statement",
        )
        in findings
    )


def test_the_bank_amount_is_the_net_of_the_bank_lines() -> None:
    # A general voucher: one bank line against two revenue lines.
    split = Voucher(
        series=None,
        number=2,
        date=d("2026-01-15"),
        text="Fees",
        lines=(
            PostingLine(BANK, debit=Decimal("200.00")),
            PostingLine("3002", credit=Decimal("150.00")),
            PostingLine("3001", credit=Decimal("50.00")),
        ),
    )
    vouchers = (BOOKED[0], split, BOOKED[2])

    assert rules(reconcile(books(*vouchers), STATEMENT, BANK)) == ["bank-summary"]


# --- Every bank transaction booked ------------------------------------------------------


def test_unbooked_transaction_before_the_last_voucher_is_an_error() -> None:
    statement = (
        STATEMENT[0],
        tx(3, "2026-01-10", "-20.00", "850.00"),
        tx(4, "2026-01-15", "200.00", "1050.00"),
    )

    findings = reconcile(books(*BOOKED), statement, BANK)

    assert (
        Finding(
            Severity.ERROR,
            "bank-unbooked",
            "bank statement row 3",
            "2026-01-10, -20.00 has no voucher, although later transactions are booked",
        )
        in findings
    )


def test_unbooked_transactions_after_the_last_voucher_are_one_warning() -> None:
    statement = (
        *STATEMENT,
        tx(4, "2026-03-01", "250.00", "1320.00"),
        tx(5, "2026-03-02", "-20.50", "1299.50"),
    )

    findings = reconcile(books(*BOOKED), statement, BANK)

    assert (
        Finding(
            Severity.WARNING,
            "bank-unbooked-recent",
            "bank statement",
            "2 unbooked transactions after 2026-02-10 "
            "(2026-03-01 to 2026-03-02, net 229.50)",
        )
        in findings
    )
    assert "unbooked" not in rules(findings)


def test_unbooked_transactions_are_listed_on_request() -> None:
    statement = (*STATEMENT, tx(4, "2026-03-01", "250.00", "1320.00"))

    findings = reconcile(books(*BOOKED), statement, BANK, list_unbooked=True)

    assert (
        Finding(Severity.INFO, "unbooked", "bank statement row 4", "2026-03-01, 250.00")
        in findings
    )


def test_identical_transactions_are_matched_one_to_one() -> None:
    # Two equal bank rows, one voucher: exactly one is unbooked.
    statement = (*STATEMENT, tx(4, "2026-01-15", "200.00", "1270.00"))

    findings = reconcile(books(*BOOKED), statement, BANK)

    assert rules(findings).count("bank-unbooked") == 1


def test_summary_is_last_and_counts_every_transaction() -> None:
    statement = (*STATEMENT, tx(4, "2026-03-01", "250.00", "1320.00"))

    findings = reconcile(books(*BOOKED), statement, BANK)

    assert findings[-1].rule == "bank-summary"
    assert findings[-1].message.startswith("3 transactions 2026-01-07 to 2026-03-01")
