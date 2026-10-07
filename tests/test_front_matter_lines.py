"""Tests for vouchers with several posting lines in the book format (MVP-005, ADR-010).

A voucher file is in one of two forms, never mixed:

- the *simple* form: one `debet` and one `kredit` with an account only, and `belopp`;
- the *lines* form: any number of `debet` and `kredit` fields, each `<account> <amount>`.

The synthetic `lines` books hold both: a salary paid from the bank (three lines), the
employer's contribution (two lines, in the lines form), an invoice and its payment (the
simple form), and a salary run for two employees without the bank account (four lines,
two of them on the same account).
"""

import shutil
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from accounting_agent.books import (
    Finding,
    PostingLine,
    Severity,
    check_books,
    compute_balances,
)
from accounting_agent.formats.front_matter import read_books

FIXTURES = Path(__file__).parent / "fixtures" / "books"
LINES = FIXTURES / "lines"
VALID = FIXTURES / "valid"
BANK = "1930"
VOUCHERS = "verifikationer"
YEAR = 2026
SALARY = "0001_2026-01-25.md"  # debet 7010 30000; kredit 2710 9000; kredit 1930 21000
SALARY_RUN = "0005_2026-02-25.md"  # four lines, no bank account
INVOICE = "0003_2026-01-31.md"  # the simple form


@pytest.fixture
def books_dir(tmp_path: Path) -> Path:
    """A private copy of the `lines` books that a test may break."""
    target = tmp_path / "books"
    shutil.copytree(LINES, target)
    return target


def replace_in(books_dir: Path, name: str, old: str, new: str) -> None:
    path = books_dir / VOUCHERS / name
    content = path.read_bytes().decode("utf-8")
    assert old in content, f"{old!r} not in {name}"
    path.write_bytes(content.replace(old, new).encode("utf-8"))


def rules(findings: list[Finding]) -> list[tuple[Severity, str]]:
    return sorted((f.severity, f.rule) for f in findings)


# --- The lines form is read ------------------------------------------------------


def test_books_with_both_forms_are_read_without_findings() -> None:
    books, findings = read_books(LINES, BANK)

    assert findings == []
    assert books is not None
    assert [v.number for v in books.vouchers] == [1, 2, 3, 4, 5]
    assert check_books(books, YEAR) == []


def test_voucher_with_three_lines_is_read() -> None:
    books, _ = read_books(LINES, BANK)
    assert books is not None

    salary = books.vouchers[0]

    assert salary.lines == (
        PostingLine("7010", debit=Decimal("30000")),
        PostingLine("2710", credit=Decimal("9000")),
        PostingLine(BANK, credit=Decimal("21000")),
    )
    assert salary.date == date(2026, 1, 25)
    assert salary.text == "Lön januari"
    assert salary.documents == ("20260125-lonespecifikation.md",)
    assert salary.note == "Utbetald via banken."
    assert salary.source == SALARY
    assert salary.is_balanced


def test_lines_keep_the_order_they_are_written_in() -> None:
    # The file lists a credit first, then two debits, then a credit.
    books, _ = read_books(LINES, BANK)
    assert books is not None

    assert books.vouchers[4].lines == (
        PostingLine("2710", credit=Decimal("16500")),
        PostingLine("7010", debit=Decimal("30000.50")),
        PostingLine("7010", debit=Decimal("25000")),
        PostingLine("2821", credit=Decimal("38500.50")),
    )


def test_two_lines_on_the_same_account_are_two_lines() -> None:
    books, _ = read_books(LINES, BANK)
    assert books is not None

    salaries = [line for line in books.vouchers[4].lines if line.account == "7010"]

    assert [line.debit for line in salaries] == [Decimal("30000.50"), Decimal("25000")]


def test_two_lines_can_be_written_in_the_lines_form() -> None:
    books, _ = read_books(LINES, BANK)
    assert books is not None

    assert books.vouchers[1].lines == (
        PostingLine("7510", debit=Decimal("9426")),
        PostingLine("2731", credit=Decimal("9426")),
    )


def test_balances_follow_every_line() -> None:
    books, _ = read_books(LINES, BANK)
    assert books is not None

    balances = compute_balances(books)

    assert balances[BANK] == Decimal("41500")  # 50000 - 21000 + 12500
    assert balances["7010"] == Decimal("85000.50")
    assert balances["2710"] == Decimal("-25500")
    assert balances["1510"] == Decimal("0")


# --- The simple form is read as before -------------------------------------------


def test_simple_form_is_read_as_before() -> None:
    books, _ = read_books(LINES, BANK)
    assert books is not None

    assert books.vouchers[2].lines == (
        PostingLine("1510", debit=Decimal("12500")),
        PostingLine("3010", credit=Decimal("12500")),
    )


def test_the_valid_books_are_unchanged() -> None:
    books, findings = read_books(VALID, BANK)

    assert findings == []
    assert books is not None
    assert [len(v.lines) for v in books.vouchers] == [2, 2, 2, 2, 2]


# --- belopp must agree with the lines --------------------------------------------


@pytest.mark.parametrize(
    ("name", "old", "new"),
    [
        (SALARY, "belopp: -21000\n", "belopp: 21000\n"),  # the bank shows money out
        (SALARY, "belopp: -21000\n", "belopp: -30000\n"),  # the total, not the bank net
        (SALARY_RUN, "belopp: 55000.50\n", "belopp: 55000\n"),  # not the total
        (SALARY_RUN, "belopp: 55000.50\n", "belopp: -55000.50\n"),  # no bank: positive
    ],
    ids=["bank-sign", "bank-total", "no-bank-total", "no-bank-negative"],
)
def test_amount_that_disagrees_with_the_lines_is_an_error(
    books_dir: Path, name: str, old: str, new: str
) -> None:
    replace_in(books_dir, name, old, new)

    books, findings = read_books(books_dir, BANK)

    assert rules(findings) == [(Severity.ERROR, "amount-mismatch")]
    assert findings[0].location == name
    # The lines are the posting; the voucher is still read from them.
    assert books is not None
    assert len(books.vouchers) == 5


def test_money_into_the_bank_with_several_lines_has_a_positive_amount(
    books_dir: Path,
) -> None:
    replace_in(
        books_dir,
        SALARY,
        "belopp: -21000\ndebet: 7010 30000\nkredit: 2710 9000\nkredit: 1930 21000\n",
        "belopp: 500\ndebet: 1930 500\nkredit: 3010 300\nkredit: 1510 200\n",
    )

    books, findings = read_books(books_dir, BANK)

    assert findings == []
    assert books is not None
    assert books.vouchers[0].lines[0] == PostingLine(BANK, debit=Decimal("500"))


def test_simple_form_keeps_the_bank_sign_rule(books_dir: Path) -> None:
    replace_in(books_dir, "0004_2026-02-10.md", "belopp: 12500\n", "belopp: -12500\n")

    _, findings = read_books(books_dir, BANK)

    assert rules(findings) == [(Severity.ERROR, "bank-sign")]


# --- Balance is the general check's rule, not the format's -----------------------


def test_unbalanced_voucher_is_read_and_reported_by_the_general_check(
    books_dir: Path,
) -> None:
    replace_in(books_dir, SALARY, "kredit: 2710 9000\n", "kredit: 2710 8000\n")

    books, findings = read_books(books_dir, BANK)

    assert findings == []  # belopp still equals the bank net
    assert books is not None
    assert not books.vouchers[0].is_balanced
    assert rules(check_books(books, YEAR)) == [(Severity.ERROR, "voucher-unbalanced")]


def test_account_both_debited_and_credited_is_still_an_error(books_dir: Path) -> None:
    replace_in(books_dir, SALARY_RUN, "kredit: 2710 16500\n", "kredit: 7010 16500\n")

    books, _ = read_books(books_dir, BANK)

    assert books is not None
    assert rules(check_books(books, YEAR)) == [(Severity.ERROR, "voucher-same-account")]


# --- A line must be an account and a positive amount -----------------------------


@pytest.mark.parametrize(
    "line",
    [
        "debet: 7010 abc",
        "debet: 7010 30 000",
        "debet: 7010 30000,50",
        "debet: 7010 -30000",
        "debet: 7010 0",
        "debet: 7010 30000.505",
    ],
    ids=["letters", "space", "comma", "negative", "zero", "three-decimals"],
)
def test_line_that_is_not_an_account_and_an_amount_skips_the_voucher(
    books_dir: Path, line: str
) -> None:
    replace_in(books_dir, SALARY, "debet: 7010 30000\n", f"{line}\n")

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert [v.number for v in books.vouchers] == [2, 3, 4, 5]
    assert rules(findings) == [(Severity.ERROR, "invalid-line")]
    assert findings[0].location == SALARY


def test_unknown_account_on_a_line_is_the_general_checks_rule(books_dir: Path) -> None:
    replace_in(books_dir, SALARY, "debet: 7010 30000\n", "debet: 7999 30000\n")

    books, findings = read_books(books_dir, BANK)

    assert findings == []
    assert books is not None
    assert rules(check_books(books, YEAR)) == [
        (Severity.ERROR, "voucher-unknown-account")
    ]


# --- The two forms never mix -----------------------------------------------------


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("kredit: 2710 9000\n", "kredit: 2710\n"),  # one line without an amount
        (
            "debet: 7010 30000\nkredit: 2710 9000\nkredit: 1930 21000\n",
            "debet: 7010\nkredit: 2710\nkredit: 1930\n",  # several lines, no amounts
        ),
        (
            "debet: 7010 30000\nkredit: 2710 9000\nkredit: 1930 21000\n",
            "debet: 7010 21000\nkredit: 1930\n",  # one of two has an amount
        ),
    ],
    ids=["one-without", "repeated-without", "one-of-two"],
)
def test_mixed_forms_skip_the_voucher(books_dir: Path, old: str, new: str) -> None:
    replace_in(books_dir, SALARY, old, new)

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert [v.number for v in books.vouchers] == [2, 3, 4, 5]
    assert rules(findings) == [(Severity.ERROR, "lines-mixed")]
    assert findings[0].location == SALARY


@pytest.mark.parametrize(
    ("old", "new", "missing"),
    [
        ("kredit: 2710 9000\nkredit: 1930 21000\n", "", "kredit"),
        ("debet: 7010 30000\n", "", "debet"),
    ],
    ids=["only-debit", "only-credit"],
)
def test_voucher_needs_a_debit_and_a_credit_line(
    books_dir: Path, old: str, new: str, missing: str
) -> None:
    replace_in(books_dir, SALARY, old, new)

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert [v.number for v in books.vouchers] == [2, 3, 4, 5]
    assert rules(findings) == [(Severity.ERROR, "missing-field")]
    assert missing in findings[0].message


def test_other_fields_may_still_not_be_repeated(books_dir: Path) -> None:
    replace_in(books_dir, SALARY, "belopp: -21000\n", "belopp: -21000\nbelopp: -1\n")

    _, findings = read_books(books_dir, BANK)

    assert rules(findings) == [(Severity.ERROR, "duplicate-field")]


# --- Findings never quote the text -----------------------------------------------


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("belopp: -21000\n", "belopp: 21000\n"),
        ("debet: 7010 30000\n", "debet: 7010 abc\n"),
        ("kredit: 2710 9000\n", "kredit: 2710\n"),
    ],
    ids=["amount-mismatch", "invalid-line", "lines-mixed"],
)
def test_findings_quote_no_text_or_line_value(
    books_dir: Path, old: str, new: str
) -> None:
    replace_in(books_dir, SALARY, "Lön januari", "Lön Hemlig Exempelperson")
    replace_in(books_dir, SALARY, old, new)

    _, findings = read_books(books_dir, BANK)

    assert findings
    for finding in findings:
        assert "Hemlig" not in finding.render()
        assert "abc" not in finding.render()
