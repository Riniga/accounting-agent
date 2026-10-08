"""Tests for writing a new voucher in the `front-matter` format (ADR-009).

Three parts: the voucher text composed from a bank statement row, rendering a voucher as
the format's file content with its generated lines, and writing the file. The writer and
the reader must agree, so every rendered voucher is also read back.
"""

import shutil
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from accounting_agent.books import PostingLine, Voucher
from accounting_agent.formats.bank_statement import read_voucher_texts
from accounting_agent.formats.front_matter import (
    VoucherExistsError,
    read_books,
    render_voucher,
    voucher_file_name,
    write_voucher,
)

FIXTURES = Path(__file__).parent / "fixtures"
VALID = FIXTURES / "books" / "valid"
STATEMENT = FIXTURES / "example-full" / "statement.csv"
HEADER = "datum;belopp;namn;meddelande;anteckning;saldo"
BANK = "1930"
VOUCHERS = "verifikationer"
NAMES = {"1930": "Bankkontot", "3002": "Medlemsavgifter", "5010": "Hyra"}
LINK_PATH = "../../underlag"


def money_out(**changes: object) -> Voucher:
    voucher = Voucher(
        series=None,
        number=6,
        date=date(2026, 3, 10),
        text="Lokalföreningen(Hyra mars)",
        lines=(
            PostingLine("5010", debit=Decimal("458.00")),
            PostingLine(BANK, credit=Decimal("458.00")),
        ),
    )
    return replace(voucher, **changes)  # type: ignore[arg-type]


def money_in(**changes: object) -> Voucher:
    voucher = Voucher(
        series=None,
        number=6,
        date=date(2026, 3, 10),
        text="Testa Testsson(Medlemsavgift)",
        lines=(
            PostingLine(BANK, debit=Decimal("200.00")),
            PostingLine("3002", credit=Decimal("200.00")),
        ),
    )
    return replace(voucher, **changes)  # type: ignore[arg-type]


def render(voucher: Voucher, link_path: str | None = LINK_PATH) -> str:
    return render_voucher(voucher, NAMES, BANK, link_path)


@pytest.fixture
def books_dir(tmp_path: Path) -> Path:
    """A private copy of the valid books (vouchers 1–5) that a test may write to."""
    target = tmp_path / "books"
    shutil.copytree(VALID, target)
    return target


def folder_content(directory: Path) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(directory.iterdir())}


# --- The voucher text of a statement row -----------------------------------------


def test_text_is_the_name_with_the_message_in_parentheses() -> None:
    texts = read_voucher_texts(STATEMENT)

    # Keyed by the row in the file, as BankTransaction.row; row 1 is the header.
    assert texts[2] == "Exempelbanken(Avgift)"
    assert texts[4] == "Lokalföreningen(Hyra februari)"
    assert sorted(texts) == [2, 3, 4, 5, 6]


def test_text_is_the_name_alone_when_there_is_no_message(tmp_path: Path) -> None:
    path = tmp_path / "statement.csv"
    rows = [HEADER, "2026-01-07;-130.00;Exempelbanken;;Egen anteckning;870.00"]
    path.write_bytes(("\n".join(rows) + "\n").encode("utf-8"))

    assert read_voucher_texts(path) == {2: "Exempelbanken"}


def test_personal_numbers_in_the_text_are_masked(tmp_path: Path) -> None:
    path = tmp_path / "statement.csv"
    rows = [HEADER, "2026-01-07;200.00;Testa Testsson;191212121212;;870.00"]
    path.write_bytes(("\n".join(rows) + "\n").encode("utf-8"))

    assert read_voucher_texts(path) == {2: "Testa Testsson([personnummer])"}


def test_missing_or_unreadable_statement_gives_no_texts(tmp_path: Path) -> None:
    assert read_voucher_texts(tmp_path / "missing.csv") == {}
    wrong = tmp_path / "wrong.csv"
    wrong.write_bytes(b"a;b\n1;2\n")
    assert read_voucher_texts(wrong) == {}


# --- Rendering -------------------------------------------------------------------


def test_money_out_is_rendered_with_a_negative_amount() -> None:
    assert render(money_out()) == (
        "---\n"
        "verifikation: 6\n"
        "datum: 2026-03-10\n"
        'text: "Lokalföreningen(Hyra mars)"\n'
        "belopp: -458\n"
        "debet: 5010\n"
        "kredit: 1930\n"
        "underlag:\n"
        "---\n"
        "\n"
        "Debet 5010 Hyra · Kredit 1930 Bankkontot\n"
    )


def test_money_in_is_rendered_with_a_positive_amount() -> None:
    assert render(money_in()) == (
        "---\n"
        "verifikation: 6\n"
        "datum: 2026-03-10\n"
        'text: "Testa Testsson(Medlemsavgift)"\n'
        "belopp: 200\n"
        "debet: 1930\n"
        "kredit: 3002\n"
        "underlag:\n"
        "---\n"
        "\n"
        "Debet 1930 Bankkontot · Kredit 3002 Medlemsavgifter\n"
    )


@pytest.mark.parametrize(
    ("amount", "written"),
    [("458.00", "-458"), ("458", "-458"), ("45.50", "-45.50"), ("1305.55", "-1305.55")],
)
def test_whole_amounts_have_no_decimals_and_others_have_two(
    amount: str, written: str
) -> None:
    voucher = money_out(
        lines=(
            PostingLine("5010", debit=Decimal(amount)),
            PostingLine(BANK, credit=Decimal(amount)),
        )
    )

    assert f"\nbelopp: {written}\n" in render(voucher)


def test_documents_get_a_field_and_a_link_each() -> None:
    voucher = money_out(
        documents=("20260310-faktura-1002.pdf", "20260310-kvitto (Exempel).jpg")
    )

    text = render(voucher)

    assert (
        "\nunderlag: 20260310-faktura-1002.pdf; 20260310-kvitto (Exempel).jpg\n" in text
    )
    assert text.endswith(
        "\n"
        "Debet 5010 Hyra · Kredit 1930 Bankkontot\n"
        "Underlag: [20260310-faktura-1002.pdf]"
        "(<../../underlag/20260310-faktura-1002.pdf>)\n"
        "Underlag: [20260310-kvitto (Exempel).jpg]"
        "(<../../underlag/20260310-kvitto (Exempel).jpg>)\n"
    )


def test_link_is_the_name_alone_without_a_path_to_the_documents() -> None:
    # No relative path exists when the folders are on different drives.
    voucher = money_out(documents=("20260310-faktura-1002.pdf",))

    assert render(voucher, link_path=None).endswith(
        "Underlag: [20260310-faktura-1002.pdf](<20260310-faktura-1002.pdf>)\n"
    )


def test_note_follows_the_generated_lines_after_a_blank_line() -> None:
    voucher = money_out(note="Gissad kontering: bara namnet framgår.")

    assert render(voucher).endswith(
        "\nDebet 5010 Hyra · Kredit 1930 Bankkontot\n"
        "\n"
        "Gissad kontering: bara namnet framgår.\n"
    )


def test_text_is_written_as_one_quoted_line() -> None:
    voucher = money_out(text='Swish: "VT26"\nandra raden\n---')

    lines = render(voucher).split("\n")

    assert lines[3] == r'text: "Swish: \"VT26\"\nandra raden\n---"'
    assert lines[4] == "belopp: -458"


def test_voucher_between_two_other_accounts_is_rendered_positive() -> None:
    voucher = money_out(
        lines=(
            PostingLine("5010", debit=Decimal("50")),
            PostingLine("3002", credit=Decimal("50")),
        )
    )

    text = render(voucher)

    assert "\nbelopp: 50\ndebet: 5010\nkredit: 3002\n" in text


@pytest.mark.parametrize(
    "lines",
    [
        (PostingLine("5010", debit=Decimal("458")),),
        (
            PostingLine("5010", debit=Decimal("458")),
            PostingLine(BANK, credit=Decimal("400")),
        ),
    ],
    ids=["one-line", "unbalanced"],
)
def test_voucher_that_does_not_balance_cannot_be_rendered(
    lines: tuple[PostingLine, ...],
) -> None:
    # Until MVP-005 three lines, or the credit line first, could not be rendered either;
    # they are now written in the lines form (test_voucher_writer_lines.py).
    with pytest.raises(ValueError, match="balance"):
        render(money_out(lines=lines))


def test_account_that_is_not_in_the_chart_cannot_be_rendered() -> None:
    voucher = money_out(
        lines=(
            PostingLine("5999", debit=Decimal("458")),
            PostingLine(BANK, credit=Decimal("458")),
        )
    )

    with pytest.raises(ValueError, match="5999"):
        render(voucher)


# --- The file name ---------------------------------------------------------------


def test_file_name_is_the_number_and_the_date() -> None:
    assert voucher_file_name(money_out()) == "0006_2026-03-10.md"
    assert voucher_file_name(money_out(number=1234)) == "1234_2026-03-10.md"


@pytest.mark.parametrize("number", [0, -1, 10000])
def test_number_must_fit_the_file_name(number: int) -> None:
    with pytest.raises(ValueError, match="1 to 9999"):
        voucher_file_name(money_out(number=number))


# --- Round trip: what is rendered is read back -----------------------------------


@pytest.mark.parametrize(
    "voucher",
    [
        money_out(),
        money_in(),
        money_out(documents=("20260310-faktura-1002.pdf",), note="Hyra för mars."),
        money_in(
            documents=("20260310-kvitto (Exempel).jpg", "20260310-faktura.pdf"),
            note="Gissad kontering: skäl.\n\nAndra stycket.\n---\ntext: inte ett fält",
        ),
        money_out(text='Swish: "VT26"\nandra raden\n---'),
        money_out(text="Åäö é – (parentes) [hake] ; semikolon"),
        money_out(
            lines=(
                PostingLine("5010", debit=Decimal("45.50")),
                PostingLine(BANK, credit=Decimal("45.50")),
            )
        ),
        money_out(note="Debet 3002 Fel namn · Kredit 5010 Fel namn"),
    ],
    ids=[
        "money-out",
        "money-in",
        "document-and-note",
        "two-documents-long-note",
        "text-with-quotes-and-line-breaks",
        "text-with-swedish-letters",
        "decimals",
        "note-shaped-like-a-generated-line",
    ],
)
def test_rendered_voucher_is_read_back_as_the_same_voucher(
    books_dir: Path, voucher: Voucher
) -> None:
    path = write_voucher(books_dir / VOUCHERS, voucher, render(voucher))

    books, findings = read_books(books_dir, BANK)

    assert findings == []
    assert books is not None
    assert books.vouchers[-1] == replace(voucher, source=path.name)


# --- Writing ---------------------------------------------------------------------


def test_file_is_created_as_utf8_without_bom_and_with_lf(books_dir: Path) -> None:
    voucher = money_out(text="Åäö")

    path = write_voucher(books_dir / VOUCHERS, voucher, render(voucher))

    assert path == books_dir / VOUCHERS / "0006_2026-03-10.md"
    raw = path.read_bytes()
    assert raw == render(voucher).encode("utf-8")
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in raw


def test_existing_file_is_never_replaced(books_dir: Path) -> None:
    voucher = money_out(number=5, date=date(2026, 3, 1))
    before = folder_content(books_dir / VOUCHERS)

    with pytest.raises(VoucherExistsError):
        write_voucher(books_dir / VOUCHERS, voucher, render(voucher))

    assert folder_content(books_dir / VOUCHERS) == before


def test_number_that_another_file_has_is_refused(books_dir: Path) -> None:
    # Voucher 5 exists with another date; the number is the identity.
    voucher = money_out(number=5)
    before = folder_content(books_dir / VOUCHERS)

    with pytest.raises(VoucherExistsError):
        write_voucher(books_dir / VOUCHERS, voucher, render(voucher))

    assert folder_content(books_dir / VOUCHERS) == before


def test_missing_voucher_folder_is_not_created(tmp_path: Path) -> None:
    voucher = money_out()

    with pytest.raises(FileNotFoundError):
        write_voucher(tmp_path / "saknas", voucher, render(voucher))

    assert not (tmp_path / "saknas").exists()


def test_refusal_does_not_quote_the_voucher_text(books_dir: Path) -> None:
    voucher = money_out(number=5, text="Hemlig Exempelperson")

    with pytest.raises(VoucherExistsError) as raised:
        write_voucher(books_dir / VOUCHERS, voucher, render(voucher))

    assert "Hemlig" not in str(raised.value)
