"""Tests for the document checks that MVP-004 adds, on model objects.

`documents-expected` names each payment out of the bank that has no supporting document,
by the same rule as the to-do report: the accounts that need none are left out.
`documents-unused` counts the files in the documents folder that no voucher refers to.
No message quotes a voucher's text or a document's file name.
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
    Account("1410", "Stock"),
    Account("2010", "Equity"),
    Account("3002", "Membership fees"),
    Account("5010", "Rent"),
    Account("6570", "Bank charges"),
)
OPENING = (
    OpeningBalance(BANK, Decimal("100.00")),
    OpeningBalance("2010", Decimal("-100.00")),
)
SENSITIVE_TEXT = "Utlägg Hemlig Exempelperson"
SENSITIVE_DOCUMENT = "kvitto (Hemlig Exempelperson).jpg"


def voucher(
    number: int,
    *,
    debit: str = "5010",
    credit: str = BANK,
    documents: tuple[str, ...] = (),
    text: str = "Payment",
) -> Voucher:
    value = Decimal("100.00")
    return Voucher(
        series=None,
        number=number,
        date=date(2026, 3, number),
        text=text,
        lines=(PostingLine(debit, debit=value), PostingLine(credit, credit=value)),
        documents=documents,
    )


def check(
    *vouchers: Voucher,
    documents: frozenset[str] | None = None,
    no_document_accounts: tuple[str, ...] = (),
) -> list[Finding]:
    books = Books(accounts=ACCOUNTS, opening_balances=OPENING, vouchers=vouchers)
    return check_details(
        books, BANK, documents=documents, no_document_accounts=no_document_accounts
    )


def expected(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings if f.rule == "documents-expected"]


def unused(findings: list[Finding]) -> list[Finding]:
    return [f for f in findings if f.rule == "documents-unused"]


# --- documents-expected ----------------------------------------------------------


def test_payment_without_a_document_is_named() -> None:
    findings = expected(check(voucher(1), voucher(2)))

    assert findings == [
        Finding(
            Severity.WARNING,
            "documents-expected",
            "voucher 1",
            "money out of the bank without a supporting document",
        ),
        Finding(
            Severity.WARNING,
            "documents-expected",
            "voucher 2",
            "money out of the bank without a supporting document",
        ),
    ]


def test_payment_with_a_document_is_not_named() -> None:
    assert expected(check(voucher(1, documents=("invoice.pdf",)))) == []


def test_money_in_needs_no_document() -> None:
    assert expected(check(voucher(1, debit=BANK, credit="3002"))) == []


# --- documents-expected for vouchers without a bank transaction (MVP-005) --------
#
# Until MVP-005 a voucher that is not on the bank account needed no document. Such a
# voucher has no bank transaction behind it, so its document is all that backs it.


def test_voucher_without_a_bank_line_and_without_a_document_is_named() -> None:
    findings = expected(check(voucher(1, debit="5010", credit="2010")))

    assert findings == [
        Finding(
            Severity.WARNING,
            "documents-expected",
            "voucher 1",
            "no bank transaction and no supporting document",
        )
    ]


def test_voucher_without_a_bank_line_but_with_a_document_is_not_named() -> None:
    journal = voucher(1, debit="5010", credit="2010", documents=("basis.md",))

    assert expected(check(journal)) == []


def test_exempt_accounts_are_left_out_without_a_bank_line_too() -> None:
    findings = check(
        voucher(1, debit="6570", credit="2010"),
        voucher(2, debit="5010", credit="2010"),
        no_document_accounts=("6570",),
    )

    assert [f.location for f in expected(findings)] == ["voucher 2"]


def test_voucher_with_several_lines_and_no_bank_line_is_named_once() -> None:
    value = Decimal("50.00")
    journal = Voucher(
        series=None,
        number=1,
        date=date(2026, 3, 1),
        text="Salaries",
        lines=(
            PostingLine("5010", debit=value),
            PostingLine("6570", debit=value),
            PostingLine("2010", credit=value * 2),
        ),
    )

    assert [f.location for f in expected(check(journal))] == ["voucher 1"]


def test_money_out_with_several_lines_is_named_as_a_payment() -> None:
    value = Decimal("50.00")
    payment = Voucher(
        series=None,
        number=1,
        date=date(2026, 3, 1),
        text="Salary",
        lines=(
            PostingLine("5010", debit=value * 2),
            PostingLine("2010", credit=value),
            PostingLine(BANK, credit=value),
        ),
    )

    assert [f.message for f in expected(check(payment))] == [
        "money out of the bank without a supporting document"
    ]


def test_accounts_that_need_no_document_are_left_out() -> None:
    findings = check(
        voucher(1, debit="6570"),
        voucher(2, debit="5010"),
        no_document_accounts=("6570",),
    )

    assert [f.location for f in expected(findings)] == ["voucher 2"]


def test_purchase_for_stock_needs_a_document_too() -> None:
    # Not a cost account, but money out of the bank — the same rule as the to-do report.
    assert [f.location for f in expected(check(voucher(1, debit="1410")))] == [
        "voucher 1"
    ]


def test_expected_documents_do_not_depend_on_a_documents_folder() -> None:
    with_folder = check(voucher(1), documents=frozenset())
    without_folder = check(voucher(1), documents=None)

    assert expected(with_folder) == expected(without_folder) != []


# --- documents-unused ------------------------------------------------------------


def test_files_no_voucher_refers_to_are_counted() -> None:
    findings = check(
        voucher(1, documents=("invoice.pdf",)),
        documents=frozenset({"invoice.pdf", "old-receipt.jpg", "notes.md"}),
    )

    assert unused(findings) == [
        Finding(
            Severity.INFO,
            "documents-unused",
            "documents folder",
            "2 of 3 files are not referred to by any voucher",
        )
    ]


def test_no_finding_when_every_file_is_referred_to() -> None:
    findings = check(
        voucher(1, documents=("invoice.pdf", "receipt.jpg")),
        voucher(2, documents=("invoice.pdf",)),
        documents=frozenset({"invoice.pdf", "receipt.jpg"}),
    )

    assert unused(findings) == []


def test_no_finding_without_a_documents_folder() -> None:
    assert unused(check(voucher(1), documents=None)) == []


def test_empty_documents_folder_gives_no_finding() -> None:
    assert unused(check(voucher(1), documents=frozenset())) == []


# --- The existing summary is unchanged -------------------------------------------


def test_the_summary_of_vouchers_without_documents_is_unchanged() -> None:
    findings = check(voucher(1), voucher(2, debit=BANK, credit="3002"))

    assert [f for f in findings if f.rule == "documents-summary"] == [
        Finding(
            Severity.INFO,
            "documents-summary",
            "vouchers",
            "2 of 2 vouchers have no supporting document (of which 1 costs)",
        )
    ]


# --- Nothing is quoted -----------------------------------------------------------


def test_findings_quote_no_text_or_file_name() -> None:
    findings = check(
        voucher(1, text=SENSITIVE_TEXT),
        documents=frozenset({SENSITIVE_DOCUMENT}),
    )

    assert expected(findings)
    assert unused(findings)
    for finding in findings:
        assert "Hemlig" not in finding.render()
        assert "kvitto" not in finding.render()
