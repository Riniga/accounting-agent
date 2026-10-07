"""Tests for writing vouchers with several posting lines, and for their generated lines
(MVP-005).

The writer chooses the form: one debit and one credit line of the same amount is written
in the simple form, exactly as before; anything else in the lines form. In the lines form
there is one generated line per posting, with the amount. Whatever is rendered must be
read back as the same voucher.
"""

import shutil
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from accounting_agent.books import Finding, PostingLine, Severity, Voucher
from accounting_agent.formats.front_matter import (
    read_books,
    render_voucher,
    write_voucher,
)

LINES = Path(__file__).parent / "fixtures" / "books" / "lines"
BANK = "1930"
VOUCHERS = "verifikationer"
NAMES = {
    "1510": "Kundfordringar",
    "1930": "Bankkontot",
    "2710": "Personalskatt",
    "2731": "Arbetsgivaravgifter att betala",
    "2821": "Löneskulder",
    "3010": "Fakturerade tjänster",
    "7010": "Löner",
    "7510": "Arbetsgivaravgifter",
}
SALARY_FILE = "0001_2026-01-25.md"
SALARY_GENERATED = (
    "Debet 7010 Löner 30000\n"
    "Kredit 2710 Personalskatt 9000\n"
    "Kredit 1930 Bankkontot 21000\n"
)
SALARY_LINK = (
    "Underlag: [20260125-lonespecifikation.md]"
    "(<../../underlag/20260125-lonespecifikation.md>)\n"
)


def debit(account: str, amount: str) -> PostingLine:
    return PostingLine(account, debit=Decimal(amount))


def credit(account: str, amount: str) -> PostingLine:
    return PostingLine(account, credit=Decimal(amount))


def voucher(*lines: PostingLine, **changes: object) -> Voucher:
    base = Voucher(
        series=None,
        number=6,
        date=date(2026, 3, 25),
        text="Lön mars",
        lines=lines,
    )
    return replace(base, **changes)  # type: ignore[arg-type]


SALARY = (debit("7010", "30000"), credit("2710", "9000"), credit(BANK, "21000"))


def render(v: Voucher) -> str:
    return render_voucher(v, NAMES, BANK, "../../underlag")


@pytest.fixture
def books_dir(tmp_path: Path) -> Path:
    """A private copy of the `lines` books (vouchers 1–5) that a test may change."""
    target = tmp_path / "books"
    shutil.copytree(LINES, target)
    return target


def set_body(books_dir: Path, name: str, body: str) -> None:
    """Replace everything below a voucher's fields with ``body``."""
    path = books_dir / VOUCHERS / name
    content = path.read_bytes().decode("utf-8")
    end = content.index("\n---\n", 3) + len("\n---\n")
    path.write_bytes((content[:end] + body).encode("utf-8"))


def read_voucher(books_dir: Path, number: int) -> tuple[Voucher, list[Finding]]:
    books, findings = read_books(books_dir, BANK)
    assert books is not None
    return books.vouchers[number - 1], findings


def rules(findings: list[Finding]) -> list[tuple[Severity, str]]:
    return sorted((f.severity, f.rule) for f in findings)


# --- Rendering the lines form ----------------------------------------------------


def test_three_lines_are_rendered_in_the_lines_form() -> None:
    v = voucher(*SALARY, documents=("20260325-lonespecifikation.md",), note="Utbetald.")

    assert render(v) == (
        "---\n"
        "verifikation: 6\n"
        "datum: 2026-03-25\n"
        'text: "Lön mars"\n'
        "belopp: -21000\n"
        "debet: 7010 30000\n"
        "kredit: 2710 9000\n"
        "kredit: 1930 21000\n"
        "underlag: 20260325-lonespecifikation.md\n"
        "---\n"
        "\n"
        "Debet 7010 Löner 30000\n"
        "Kredit 2710 Personalskatt 9000\n"
        "Kredit 1930 Bankkontot 21000\n"
        "Underlag: [20260325-lonespecifikation.md]"
        "(<../../underlag/20260325-lonespecifikation.md>)\n"
        "\n"
        "Utbetald.\n"
    )


def test_lines_keep_their_order() -> None:
    v = voucher(
        credit("2710", "16500"),
        debit("7010", "30000.50"),
        debit("7010", "25000"),
        credit("2821", "38500.50"),
    )

    text = render(v)

    assert (
        "belopp: 55000.50\n"
        "kredit: 2710 16500\n"
        "debet: 7010 30000.50\n"
        "debet: 7010 25000\n"
        "kredit: 2821 38500.50\n"
    ) in text
    assert text.endswith(
        "\n"
        "Kredit 2710 Personalskatt 16500\n"
        "Debet 7010 Löner 30000.50\n"
        "Debet 7010 Löner 25000\n"
        "Kredit 2821 Löneskulder 38500.50\n"
    )


@pytest.mark.parametrize(
    ("lines", "amount"),
    [
        (SALARY, "-21000"),  # the bank is credited: money out
        (
            (debit(BANK, "500"), credit("3010", "300"), credit("1510", "200")),
            "500",  # the bank is debited: money in
        ),
        (
            (debit("7010", "30000"), credit("2710", "9000"), credit("2821", "21000")),
            "30000",  # no bank account: the total
        ),
    ],
    ids=["money-out", "money-in", "no-bank"],
)
def test_belopp_is_the_bank_net_or_the_total(
    lines: tuple[PostingLine, ...], amount: str
) -> None:
    assert f"\nbelopp: {amount}\n" in render(voucher(*lines))


def test_whole_amounts_have_no_decimals_and_others_have_two() -> None:
    v = voucher(
        debit("7010", "100.00"), debit("7510", "31.4"), credit("2821", "131.40")
    )

    text = render(v)

    assert "debet: 7010 100\ndebet: 7510 31.40\nkredit: 2821 131.40\n" in text
    assert "Debet 7010 Löner 100\nDebet 7510 Arbetsgivaravgifter 31.40\n" in text


# --- The simple form is chosen when it fits --------------------------------------


def test_one_debit_and_one_credit_line_are_rendered_in_the_simple_form() -> None:
    v = voucher(debit("7510", "9426"), credit("2731", "9426"))

    assert render(v) == (
        "---\n"
        "verifikation: 6\n"
        "datum: 2026-03-25\n"
        'text: "Lön mars"\n'
        "belopp: 9426\n"
        "debet: 7510\n"
        "kredit: 2731\n"
        "underlag:\n"
        "---\n"
        "\n"
        "Debet 7510 Arbetsgivaravgifter · Kredit 2731 Arbetsgivaravgifter att betala\n"
    )


def test_credit_line_first_is_rendered_in_the_lines_form() -> None:
    # The simple form always reads the debit line first; this order needs the lines form.
    v = voucher(credit("2731", "9426"), debit("7510", "9426"))

    assert "kredit: 2731 9426\ndebet: 7510 9426\n" in render(v)


# --- What cannot be rendered -----------------------------------------------------


@pytest.mark.parametrize(
    "lines",
    [
        (debit("7010", "30000"),),
        (debit("7010", "30000"), credit("2710", "9000"), credit(BANK, "20000")),
        (debit("7010", "30000"), PostingLine("2710"), credit(BANK, "30000")),
        (),
    ],
    ids=["one-line", "unbalanced", "line-of-zero", "no-lines"],
)
def test_voucher_that_does_not_balance_cannot_be_rendered(
    lines: tuple[PostingLine, ...],
) -> None:
    with pytest.raises(ValueError, match="balance"):
        render(voucher(*lines))


def test_account_that_is_not_in_the_chart_cannot_be_rendered() -> None:
    v = voucher(debit("7999", "30000"), credit("2710", "9000"), credit(BANK, "21000"))

    with pytest.raises(ValueError, match="7999"):
        render(v)


# --- Round trip: what is rendered is read back -----------------------------------


@pytest.mark.parametrize(
    "v",
    [
        voucher(*SALARY),
        voucher(
            *SALARY, documents=("a.md", "b (kopia).md"), note="Rad ett.\n\nRad två."
        ),
        voucher(
            debit("7010", "30000.50"),
            debit("7010", "25000"),
            debit("7510", "17281.66"),
            credit("2710", "16500"),
            credit("2731", "17281.66"),
            credit("2821", "38500.50"),
        ),
        voucher(debit(BANK, "500"), credit("3010", "300"), credit("1510", "200")),
        voucher(credit("2731", "9426"), debit("7510", "9426")),
        voucher(debit("7510", "9426"), credit("2731", "9426")),
        voucher(*SALARY, note="Debet 7010 Löner 1\nKredit 1930 Bankkontot 1"),
    ],
    ids=[
        "three-lines",
        "documents-and-note",
        "six-lines-two-on-one-account",
        "money-in",
        "credit-first",
        "simple-form",
        "note-shaped-like-generated-lines",
    ],
)
def test_rendered_voucher_is_read_back_as_the_same_voucher(
    books_dir: Path, v: Voucher
) -> None:
    path = write_voucher(books_dir / VOUCHERS, v, render(v))

    books, findings = read_books(books_dir, BANK)

    assert findings == []
    assert books is not None
    assert books.vouchers[-1] == replace(v, source=path.name)


# --- The reader: generated lines of the lines form -------------------------------


def test_generated_lines_per_posting_are_kept_out_of_the_note(books_dir: Path) -> None:
    set_body(books_dir, SALARY_FILE, f"\n{SALARY_GENERATED}{SALARY_LINK}\nUtbetald.\n")

    v, findings = read_voucher(books_dir, 1)

    assert findings == []
    assert v.note == "Utbetald."


def test_same_shape_below_the_note_stays_in_the_note(books_dir: Path) -> None:
    set_body(books_dir, SALARY_FILE, "\nEgen anteckning.\nDebet 7010 Löner 1\n")

    v, findings = read_voucher(books_dir, 1)

    assert findings == []
    assert v.note == "Egen anteckning.\nDebet 7010 Löner 1"


@pytest.mark.parametrize(
    "generated",
    [
        "Debet 7010 Löner 30001\nKredit 2710 Personalskatt 9000\n"
        "Kredit 1930 Bankkontot 21000\n",
        "Debet 7510 Arbetsgivaravgifter 30000\nKredit 2710 Personalskatt 9000\n"
        "Kredit 1930 Bankkontot 21000\n",
        "Kredit 7010 Löner 30000\nKredit 2710 Personalskatt 9000\n"
        "Kredit 1930 Bankkontot 21000\n",
        "Debet 7010 Löner 30000\nKredit 2710 Personalskatt 9000\n",
        "Debet 7010 Löner 30000\nKredit 2710 Personalskatt 9000\n"
        "Kredit 1930 Bankkontot 21000\nKredit 2821 Löneskulder 1\n",
        "Debet 7010 Löner 30000\nKredit 1930 Bankkontot 21000\n"
        "Kredit 2710 Personalskatt 9000\n",
        "Debet 7010 Löner · Kredit 1930 Bankkontot\n",
    ],
    ids=[
        "amount",
        "account",
        "side",
        "line-missing",
        "line-too-many",
        "order",
        "single-line-of-the-simple-form",
    ],
)
def test_generated_lines_must_match_the_posting_lines(
    books_dir: Path, generated: str
) -> None:
    set_body(books_dir, SALARY_FILE, f"\n{generated}{SALARY_LINK}")

    v, findings = read_voucher(books_dir, 1)

    assert rules(findings) == [(Severity.ERROR, "generated-accounts")]
    assert findings[0].location == SALARY_FILE
    assert len(v.lines) == 3  # the fields are the single source
    assert v.note == ""


def test_generated_name_that_differs_from_the_chart_is_a_warning(
    books_dir: Path,
) -> None:
    generated = SALARY_GENERATED.replace("7010 Löner", "7010 Lön")
    set_body(books_dir, SALARY_FILE, f"\n{generated}{SALARY_LINK}")

    _, findings = read_voucher(books_dir, 1)

    assert rules(findings) == [(Severity.WARNING, "generated-account-name")]


def test_wrong_name_on_two_lines_of_one_account_is_one_warning(
    books_dir: Path,
) -> None:
    generated = (
        "Kredit 2710 Personalskatt 16500\n"
        "Debet 7010 Lön 30000.50\n"
        "Debet 7010 Lön 25000\n"
        "Kredit 2821 Löneskulder 38500.50\n"
    )
    links = (
        "Underlag: [20260225-lonespecifikation-1.md]"
        "(<../../underlag/20260225-lonespecifikation-1.md>)\n"
        "Underlag: [20260225-lonespecifikation-2.md]"
        "(<../../underlag/20260225-lonespecifikation-2.md>)\n"
    )
    set_body(books_dir, "0005_2026-02-25.md", f"\n{generated}{links}")

    _, findings = read_voucher(books_dir, 5)

    assert rules(findings) == [(Severity.WARNING, "generated-account-name")]


def test_generated_documents_are_checked_in_the_lines_form_too(
    books_dir: Path,
) -> None:
    set_body(books_dir, SALARY_FILE, f"\n{SALARY_GENERATED}")  # the link is missing

    _, findings = read_voucher(books_dir, 1)

    assert rules(findings) == [(Severity.ERROR, "generated-documents")]


def test_lines_written_per_posting_on_a_simple_voucher_are_accepted(
    books_dir: Path,
) -> None:
    # Voucher 4 is in the simple form: debet 1930, kredit 1510, belopp 12500.
    body = "\nDebet 1930 Bankkontot 12500\nKredit 1510 Kundfordringar 12500\n"
    set_body(books_dir, "0004_2026-02-10.md", body)

    v, findings = read_voucher(books_dir, 4)

    assert findings == []
    assert v.note == ""


def test_findings_quote_no_name_or_text(books_dir: Path) -> None:
    generated = SALARY_GENERATED.replace("7010 Löner 30000", "7510 Hemligt Namn 1")
    set_body(
        books_dir, SALARY_FILE, f"\n{generated}{SALARY_LINK}\nHemlig anteckning.\n"
    )

    _, findings = read_voucher(books_dir, 1)

    assert findings
    for finding in findings:
        assert "Hemlig" not in finding.render()
        assert "Lön januari" not in finding.render()
