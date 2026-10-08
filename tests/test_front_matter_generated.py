"""Tests for the generated lines below a `front-matter` voucher's fields (ADR-009).

The generated lines repeat the fields in a readable form: the accounts with their names,
and a link to each supporting document. The reader keeps them out of the note and reports
lines that disagree with the fields. They are recognised only at the top of the body.
"""

import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from accounting_agent.books import Finding, Severity, Voucher
from accounting_agent.formats.front_matter import read_books

VALID = Path(__file__).parent / "fixtures" / "books" / "valid"
BANK = "1930"
VOUCHERS = "verifikationer"

# Voucher 3 debits 5010 "Hyra", credits 1930 "Bankkontot", and has one document.
ACCOUNTS_3 = "Debet 5010 Hyra · Kredit 1930 Bankkontot"
DOCUMENT_3 = "20260201-faktura-lokal-1001.pdf"
LINK_3 = f"Underlag: [{DOCUMENT_3}](<../../documents/{DOCUMENT_3}>)"
# Voucher 1 debits 6570 "Bankkostnader", credits 1930, and has no document.
ACCOUNTS_1 = "Debet 6570 Bankkostnader · Kredit 1930 Bankkontot"
# Voucher 5 debits 1930, credits 3002 "Medlemsavgifter", and has two documents.
ACCOUNTS_5 = "Debet 1930 Bankkontot · Kredit 3002 Medlemsavgifter"
DOCUMENTS_5 = ("20260301-transaktion-in-250.pdf", "20260301-kvitto.pdf")


def link(name: str) -> str:
    return f"Underlag: [{name}](<../../documents/{name}>)"


@pytest.fixture
def books_dir(tmp_path: Path) -> Path:
    """A private copy of the valid books that a test may change."""
    target = tmp_path / "books"
    shutil.copytree(VALID, target)
    return target


def set_body(books_dir: Path, number: int, body: str) -> None:
    """Replace everything below a voucher's fields with ``body``."""
    (path,) = (books_dir / VOUCHERS).glob(f"{number:04d}_*.md")
    content = path.read_bytes().decode("utf-8")
    end = content.index("\n---\n", 3) + len("\n---\n")
    path.write_bytes((content[:end] + body).encode("utf-8"))


def original(number: int) -> Voucher:
    books, _ = read_books(VALID, BANK)
    assert books is not None
    return books.vouchers[number - 1]


def read_voucher(books_dir: Path, number: int) -> tuple[Voucher, list[Finding]]:
    books, findings = read_books(books_dir, BANK)
    assert books is not None
    return books.vouchers[number - 1], findings


def rules(findings: list[Finding]) -> list[tuple[Severity, str]]:
    return sorted((f.severity, f.rule) for f in findings)


# --- Generated lines are not part of the note ----------------------------------------


def test_generated_lines_are_kept_out_of_the_note(books_dir: Path) -> None:
    set_body(books_dir, 3, f"\n{ACCOUNTS_3}\n{LINK_3}\n\nHyra för februari.\n")

    voucher, findings = read_voucher(books_dir, 3)

    assert findings == []
    assert voucher == replace(original(3), note="Hyra för februari.")


def test_generated_lines_alone_give_an_empty_note(books_dir: Path) -> None:
    set_body(books_dir, 1, f"\n{ACCOUNTS_1}\n")

    voucher, findings = read_voucher(books_dir, 1)

    assert findings == []
    assert voucher == original(1)
    assert voucher.note == ""


def test_generated_lines_directly_below_the_fields_are_recognised(
    books_dir: Path,
) -> None:
    # No blank line between the closing --- and the generated lines.
    set_body(books_dir, 1, f"{ACCOUNTS_1}\nBetald via autogiro.\n")

    voucher, findings = read_voucher(books_dir, 1)

    assert findings == []
    assert voucher.note == "Betald via autogiro."


def test_every_document_gets_a_generated_line(books_dir: Path) -> None:
    body = f"\n{ACCOUNTS_5}\n{link(DOCUMENTS_5[0])}\n{link(DOCUMENTS_5[1])}\n"
    set_body(books_dir, 5, body)

    voucher, findings = read_voucher(books_dir, 5)

    assert findings == []
    assert voucher == original(5)


def test_document_name_with_space_and_parenthesis_is_read(books_dir: Path) -> None:
    name = "20260201-kvitto butik (Exempel).jpg"
    (path,) = (books_dir / VOUCHERS).glob("0003_*.md")
    content = path.read_bytes().decode("utf-8")
    path.write_bytes(content.replace(DOCUMENT_3, name).encode("utf-8"))
    set_body(books_dir, 3, f"\n{ACCOUNTS_3}\n{link(name)}\n")

    voucher, findings = read_voucher(books_dir, 3)

    assert findings == []
    assert voucher.documents == (name,)
    assert voucher.note == ""


def test_note_keeps_its_own_line_breaks(books_dir: Path) -> None:
    set_body(books_dir, 1, f"\n{ACCOUNTS_1}\n\nFörsta raden.\n\nAndra raden.\n")

    voucher, _ = read_voucher(books_dir, 1)

    assert voucher.note == "Första raden.\n\nAndra raden."


# --- Only the top of the body is generated -------------------------------------------


def test_same_shape_further_down_stays_in_the_note(books_dir: Path) -> None:
    # A person may write such a line in a note; it is theirs, and it is not checked.
    body = "\nEgen anteckning.\nDebet 3002 Fel namn · Kredit 5010 Fel namn\n"
    set_body(books_dir, 1, body)

    voucher, findings = read_voucher(books_dir, 1)

    assert findings == []
    assert voucher.note == (
        "Egen anteckning.\nDebet 3002 Fel namn · Kredit 5010 Fel namn"
    )


def test_document_line_without_an_account_line_stays_in_the_note(
    books_dir: Path,
) -> None:
    set_body(books_dir, 3, f"\n{LINK_3}\n")

    voucher, findings = read_voucher(books_dir, 3)

    assert findings == []
    assert voucher.note == LINK_3


def test_document_line_after_the_note_stays_in_the_note(books_dir: Path) -> None:
    set_body(books_dir, 3, f"\n{ACCOUNTS_3}\n{LINK_3}\n\nAnteckning.\n{LINK_3}\n")

    voucher, findings = read_voucher(books_dir, 3)

    assert findings == []
    assert voucher.note == f"Anteckning.\n{LINK_3}"


# --- Generated lines must agree with the fields --------------------------------------


@pytest.mark.parametrize(
    "accounts",
    [
        "Debet 6570 Bankkostnader · Kredit 1930 Bankkontot",  # wrong debit account
        "Debet 5010 Hyra · Kredit 2890 Skulder",  # wrong credit account
        "Debet 1930 Bankkontot · Kredit 5010 Hyra",  # the sides are swapped
    ],
)
def test_generated_accounts_must_match_the_fields(
    books_dir: Path, accounts: str
) -> None:
    set_body(books_dir, 3, f"\n{accounts}\n{LINK_3}\n")

    voucher, findings = read_voucher(books_dir, 3)

    assert rules(findings) == [(Severity.ERROR, "generated-accounts")]
    assert findings[0].location == "0003_2026-02-01.md"
    # The fields are the single source: the voucher itself is read as before.
    assert voucher == replace(original(3), note="")


@pytest.mark.parametrize(
    "accounts",
    [
        "Debet 5010 Lokalhyra · Kredit 1930 Bankkontot",
        "Debet 5010 Hyra · Kredit 1930 Banken",
    ],
)
def test_generated_account_name_that_differs_from_the_chart_is_a_warning(
    books_dir: Path, accounts: str
) -> None:
    set_body(books_dir, 3, f"\n{accounts}\n{LINK_3}\n")

    _, findings = read_voucher(books_dir, 3)

    assert rules(findings) == [(Severity.WARNING, "generated-account-name")]
    assert findings[0].location == "0003_2026-02-01.md"


def test_wrong_number_is_not_also_reported_as_a_wrong_name(books_dir: Path) -> None:
    # The name is not right for 6570 either, but one finding per line is enough.
    set_body(books_dir, 3, f"\nDebet 6570 Hyra · Kredit 1930 Bankkontot\n{LINK_3}\n")

    _, findings = read_voucher(books_dir, 3)

    assert rules(findings) == [(Severity.ERROR, "generated-accounts")]


def test_generated_line_missing_for_a_document_is_an_error(books_dir: Path) -> None:
    set_body(books_dir, 3, f"\n{ACCOUNTS_3}\n")

    _, findings = read_voucher(books_dir, 3)

    assert rules(findings) == [(Severity.ERROR, "generated-documents")]
    assert findings[0].location == "0003_2026-02-01.md"


def test_generated_line_for_a_document_not_in_the_field_is_an_error(
    books_dir: Path,
) -> None:
    set_body(books_dir, 1, f"\n{ACCOUNTS_1}\n{LINK_3}\n")

    _, findings = read_voucher(books_dir, 1)

    assert rules(findings) == [(Severity.ERROR, "generated-documents")]


def test_generated_line_for_another_document_is_an_error(books_dir: Path) -> None:
    set_body(books_dir, 3, f"\n{ACCOUNTS_3}\n{link('20260201-annan-faktura.pdf')}\n")

    _, findings = read_voucher(books_dir, 3)

    assert rules(findings) == [(Severity.ERROR, "generated-documents")]


def test_generated_documents_follow_the_order_of_the_field(books_dir: Path) -> None:
    body = f"\n{ACCOUNTS_5}\n{link(DOCUMENTS_5[1])}\n{link(DOCUMENTS_5[0])}\n"
    set_body(books_dir, 5, body)

    _, findings = read_voucher(books_dir, 5)

    assert rules(findings) == [(Severity.ERROR, "generated-documents")]


def test_link_must_point_at_the_document_it_names(books_dir: Path) -> None:
    body = f"\n{ACCOUNTS_3}\nUnderlag: [{DOCUMENT_3}](<../../documents/annan.pdf>)\n"
    set_body(books_dir, 3, body)

    _, findings = read_voucher(books_dir, 3)

    assert rules(findings) == [(Severity.ERROR, "generated-documents")]


# --- Vouchers without generated lines are read as before -----------------------------


def test_vouchers_without_generated_lines_are_unchanged() -> None:
    books, findings = read_books(VALID, BANK)

    assert findings == []
    assert books is not None
    assert [v.note for v in books.vouchers] == [
        "",
        "",
        "Hyra för februari. Fakturan betalades via bankgiro.",
        "",
        "",
    ]


# --- Findings never quote names, texts or file names ---------------------------------


@pytest.mark.parametrize(
    "body",
    [
        f"\nDebet 6570 Hemligt Kontonamn · Kredit 1930 Bankkontot\n{LINK_3}\n",
        f"\nDebet 5010 Hemligt Kontonamn · Kredit 1930 Bankkontot\n{LINK_3}\n",
        f"\n{ACCOUNTS_3}\n{link('20260201-kvitto (Hemligt Namn).pdf')}\n",
        f"\n{ACCOUNTS_3}\n",
    ],
    ids=["wrong-account", "wrong-name", "wrong-document", "missing-document"],
)
def test_findings_quote_no_name_text_or_file_name(books_dir: Path, body: str) -> None:
    set_body(books_dir, 3, body + "\nHemlig anteckning om Anna.\n")

    _, findings = read_voucher(books_dir, 3)

    assert findings
    for finding in findings:
        rendered = finding.render()
        for secret in (
            "Hemlig",
            "Anna",
            "Lokalhyra februari",  # the voucher's text
            "Hyra",  # an account's name
            "Bankkontot",
            DOCUMENT_3,
            ".pdf",
        ):
            assert secret not in rendered
