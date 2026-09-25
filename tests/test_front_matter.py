"""Tests for the `front-matter` book format reader (ADR-006).

The broken variants are built from the synthetic `valid` books by small helpers, one
variant per rule, instead of being kept as copied folders.
"""

import shutil
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from accounting_agent.books import Finding, PostingLine, Severity
from accounting_agent.formats.front_matter import read_books

VALID = Path(__file__).parent / "fixtures" / "books" / "valid"
BANK = "1930"
CHART = "kontoplan.csv"
OPENING = "ingående-balans.csv"
VOUCHERS = "verifikationer"


@pytest.fixture
def books_dir(tmp_path: Path) -> Path:
    """A private copy of the valid books that a test may break."""
    target = tmp_path / "books"
    shutil.copytree(VALID, target)
    return target


def replace_in(path: Path, old: str, new: str) -> None:
    """Replace text in a file, byte-exactly (no newline translation)."""
    content = path.read_bytes().decode("utf-8")
    assert old in content, f"{old!r} not in {path.name}"
    path.write_bytes(content.replace(old, new).encode("utf-8"))


def voucher_file(books_dir: Path, number: int) -> Path:
    (path,) = (books_dir / VOUCHERS).glob(f"{number:04d}_*.md")
    return path


def rules(findings: list[Finding]) -> list[tuple[Severity, str]]:
    return sorted((f.severity, f.rule) for f in findings)


# --- The valid books -------------------------------------------------------------


def test_valid_books_are_read_without_findings() -> None:
    books, findings = read_books(VALID, BANK)

    assert findings == []
    assert books is not None
    assert [a.number for a in books.accounts] == [
        "1930",
        "2010",
        "2890",
        "3002",
        "5010",
        "6570",
    ]
    assert books.accounts[0].name == "Bankkontot"  # the local name is used
    assert [(o.account, o.amount) for o in books.opening_balances] == [
        ("1930", Decimal("1000.00")),
        ("2010", Decimal("-800.00")),
        ("2890", Decimal("-200.00")),
    ]
    assert [v.number for v in books.vouchers] == [1, 2, 3, 4, 5]


def test_money_out_becomes_two_lines_with_absolute_amounts() -> None:
    books, _ = read_books(VALID, BANK)
    assert books is not None

    first = books.vouchers[0]

    assert first.series is None
    assert first.date == date(2026, 1, 7)
    assert first.text == "Bankens årsavgift"
    assert first.lines == (
        PostingLine("6570", debit=Decimal("130.00")),
        PostingLine("1930", credit=Decimal("130.00")),
    )
    assert first.source == "0001_2026-01-07.md"


def test_documents_and_note_are_read() -> None:
    books, _ = read_books(VALID, BANK)
    assert books is not None

    third = books.vouchers[2]

    assert third.documents == ("20260201-faktura-lokal-1001.pdf",)
    assert third.note == "Hyra för februari. Fakturan betalades via bankgiro."


def test_quoted_text_is_decoded_as_a_json_string() -> None:
    # Same semantics as the organisation's own parser: colons and escaped quotes survive.
    books, _ = read_books(VALID, BANK)
    assert books is not None

    fifth = books.vouchers[4]

    assert fifth.text == 'Swish: medlemsavgift "VT26"'
    assert fifth.documents == (
        "20260301-transaktion-in-250.pdf",
        "20260301-kvitto.pdf",
    )


def test_amounts_are_exact_decimals() -> None:
    books, _ = read_books(VALID, BANK)
    assert books is not None

    assert all(
        isinstance(line.debit, Decimal) and isinstance(line.credit, Decimal)
        for voucher in books.vouchers
        for line in voucher.lines
    )


# --- Files and CSV -------------------------------------------------------------------


@pytest.mark.parametrize("name", [CHART, OPENING])
def test_missing_csv_file_makes_the_books_unreadable(
    books_dir: Path, name: str
) -> None:
    (books_dir / name).unlink()

    books, findings = read_books(books_dir, BANK)

    assert books is None
    assert rules(findings) == [(Severity.ERROR, "file-missing")]
    assert findings[0].location == name


def test_missing_voucher_directory_makes_the_books_unreadable(books_dir: Path) -> None:
    shutil.rmtree(books_dir / VOUCHERS)

    books, findings = read_books(books_dir, BANK)

    assert books is None
    assert rules(findings) == [(Severity.ERROR, "directory-missing")]


def test_bom_is_an_error_but_the_file_is_still_read(books_dir: Path) -> None:
    path = books_dir / CHART
    path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert len(books.accounts) == 6
    assert rules(findings) == [(Severity.ERROR, "encoding")]


def test_invalid_utf8_makes_the_books_unreadable(books_dir: Path) -> None:
    path = books_dir / OPENING
    path.write_bytes(path.read_bytes() + b"\xff\xfe\n")

    books, findings = read_books(books_dir, BANK)

    assert books is None
    assert rules(findings) == [(Severity.ERROR, "encoding")]


def test_crlf_line_endings_are_a_warning(books_dir: Path) -> None:
    path = books_dir / CHART
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert rules(findings) == [(Severity.WARNING, "line-endings")]


def test_wrong_header_makes_the_books_unreadable(books_dir: Path) -> None:
    replace_in(books_dir / CHART, "lokal_benämning", "namn")

    books, findings = read_books(books_dir, BANK)

    assert books is None
    assert rules(findings) == [(Severity.ERROR, "header")]


def test_wrong_column_count_skips_the_row(books_dir: Path) -> None:
    replace_in(
        books_dir / CHART, "6570;Bankkostnader;Bankkostnader", "6570;Bankkostnader"
    )

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert "6570" not in [a.number for a in books.accounts]
    assert rules(findings) == [(Severity.ERROR, "columns")]
    assert findings[0].location == f"{CHART}:7"


def test_empty_row_is_a_warning(books_dir: Path) -> None:
    replace_in(
        books_dir / OPENING, "1930;Bankkontot;1000.00\n", "1930;Bankkontot;1000.00\n\n"
    )

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert rules(findings) == [(Severity.WARNING, "empty-row")]


def test_invalid_opening_balance_amount_skips_the_row(books_dir: Path) -> None:
    replace_in(books_dir / OPENING, "1000.00", "1 000,00")

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert "1930" not in [o.account for o in books.opening_balances]
    assert rules(findings) == [(Severity.ERROR, "invalid-amount")]


# --- Voucher files ---------------------------------------------------------------------


def test_file_with_unexpected_name_is_an_error(books_dir: Path) -> None:
    (books_dir / VOUCHERS / "anteckningar.txt").write_text("x\n", encoding="utf-8")

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert len(books.vouchers) == 5
    assert rules(findings) == [(Severity.ERROR, "file-name")]
    assert findings[0].location == "anteckningar.txt"


def test_missing_front_matter_skips_the_voucher(books_dir: Path) -> None:
    path = voucher_file(books_dir, 2)
    path.write_bytes(path.read_bytes().replace(b"---\n", b"", 1))

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert [v.number for v in books.vouchers] == [1, 3, 4, 5]
    assert rules(findings) == [(Severity.ERROR, "front-matter")]


def test_unknown_field_is_an_error(books_dir: Path) -> None:
    replace_in(
        voucher_file(books_dir, 2), "debet: 1930\n", "debet: 1930\nkonto: 1930\n"
    )

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert len(books.vouchers) == 5  # the known fields are still complete
    assert rules(findings) == [(Severity.ERROR, "unknown-field")]


def test_duplicate_field_is_an_error(books_dir: Path) -> None:
    replace_in(
        voucher_file(books_dir, 2), "belopp: 200\n", "belopp: 200\nbelopp: 300\n"
    )

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert books.vouchers[1].lines[0].debit == Decimal("200")  # the first value wins
    assert rules(findings) == [(Severity.ERROR, "duplicate-field")]


@pytest.mark.parametrize(
    "field", ["verifikation", "datum", "text", "belopp", "debet", "kredit"]
)
def test_missing_required_field_skips_the_voucher(books_dir: Path, field: str) -> None:
    path = voucher_file(books_dir, 2)
    lines = path.read_bytes().decode("utf-8").split("\n")
    path.write_bytes(
        "\n".join(line for line in lines if not line.startswith(f"{field}:")).encode()
    )

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert 2 not in [v.number for v in books.vouchers]
    assert rules(findings) == [(Severity.ERROR, "missing-field")]
    assert field in findings[0].message


def test_bad_quotes_are_an_error_and_the_field_counts_as_missing(
    books_dir: Path,
) -> None:
    replace_in(
        voucher_file(books_dir, 2), 'text: "Medlemsavgift 2026"', 'text: "Medlemsavgift'
    )

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert 2 not in [v.number for v in books.vouchers]
    assert rules(findings) == [
        (Severity.ERROR, "missing-field"),
        (Severity.ERROR, "quoting"),
    ]


def test_number_in_file_name_must_match_the_field(books_dir: Path) -> None:
    replace_in(voucher_file(books_dir, 2), "verifikation: 2", "verifikation: 7")

    _, findings = read_books(books_dir, BANK)

    assert rules(findings) == [(Severity.ERROR, "number-mismatch")]


def test_date_in_file_name_must_match_the_field(books_dir: Path) -> None:
    replace_in(voucher_file(books_dir, 2), "datum: 2026-01-15", "datum: 2026-01-16")

    _, findings = read_books(books_dir, BANK)

    assert rules(findings) == [(Severity.ERROR, "date-mismatch")]


def test_invalid_date_skips_the_voucher(books_dir: Path) -> None:
    path = voucher_file(books_dir, 2)
    replace_in(path, "datum: 2026-01-15", "datum: 2026-02-30")
    path.rename(path.with_name("0002_2026-02-30.md"))

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert 2 not in [v.number for v in books.vouchers]
    assert rules(findings) == [(Severity.ERROR, "invalid-date")]


@pytest.mark.parametrize("amount", ["200,00", "2 00", "abc", "200.123", ""])
def test_invalid_voucher_amount_skips_the_voucher(books_dir: Path, amount: str) -> None:
    replace_in(voucher_file(books_dir, 2), "belopp: 200\n", f"belopp: {amount}\n")

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert 2 not in [v.number for v in books.vouchers]
    assert rules(findings) == [(Severity.ERROR, "invalid-amount")]


# --- The bank-sign rule (a rule of this format, ADR-006) ---------------------------------


@pytest.mark.parametrize(
    ("number", "old", "new"),
    [
        (2, "belopp: 200\n", "belopp: -200\n"),  # debit bank (money in) but negative
        (
            1,
            "belopp: -130.00\n",
            "belopp: 130.00\n",
        ),  # credit bank (money out) but positive
        (4, "belopp: 50.00\n", "belopp: -50.00\n"),  # bank not involved but negative
    ],
)
def test_amount_sign_must_match_the_bank_side(
    books_dir: Path, number: int, old: str, new: str
) -> None:
    replace_in(voucher_file(books_dir, number), old, new)

    books, findings = read_books(books_dir, BANK)

    assert books is not None
    assert rules(findings) == [(Severity.ERROR, "bank-sign")]
    assert findings[0].location == voucher_file(books_dir, number).name


def test_bank_account_comes_from_the_caller(books_dir: Path) -> None:
    # With another bank account, voucher 1's negative amount is "not involving the bank".
    _, findings = read_books(books_dir, "1910")

    assert (Severity.ERROR, "bank-sign") in rules(findings)


# --- No voucher text in any finding (STRIDE: information disclosure) ----------------------

SENSITIVE_TEXT = "Swish from 191212121212 Anna Exempel"


@pytest.mark.parametrize(
    "break_voucher",
    [
        lambda p: replace_in(p, "belopp: 200\n", "belopp: -200\n"),
        lambda p: replace_in(p, "debet: 1930\n", "debet: 1930\nokänt: 1\n"),
        lambda p: replace_in(p, "belopp: 200\n", "belopp: x\n"),
        lambda p: replace_in(p, "verifikation: 2", "verifikation: 9"),
    ],
)
def test_findings_never_quote_the_voucher_text(
    books_dir: Path, break_voucher: Callable[[Path], None]
) -> None:
    path = voucher_file(books_dir, 2)
    replace_in(path, "Medlemsavgift 2026", SENSITIVE_TEXT)
    break_voucher(path)

    _, findings = read_books(books_dir, BANK)

    assert findings
    for finding in findings:
        assert "191212121212" not in finding.render()
        assert "Anna" not in finding.render()
