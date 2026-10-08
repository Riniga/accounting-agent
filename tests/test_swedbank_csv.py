"""Tests for the `swedbank-csv` bank export (MVP-006).

The export is comma-separated, in Windows-1252, newest first. A line that starts with `*`
says what the file is; then comes a header row with twelve columns, and one row per
transaction with the bank's row number, the account, three dates, a reference, a text, the
amount and the balance after the transaction. The export is synthetic
(`tests/fixtures/bank/`), with invented names and Skatteverket's public test number.
"""

import shutil
from decimal import Decimal
from pathlib import Path

import pytest

from accounting_agent.cli import main
from accounting_agent.formats.bank_export import ExportFormatError, StatementExport
from accounting_agent.formats.bank_statement import (
    read_statement,
    read_voucher_texts,
    write_statement,
)
from accounting_agent.formats.swedbank_csv import read_export
from accounting_agent.profile import load_profile

BANK_FIXTURES = Path(__file__).parent / "fixtures" / "bank"
EXPORT = BANK_FIXTURES / "swedbank-statement.csv"
NORDEA_EXPORT = BANK_FIXTURES / "nordea-statement.csv"
SPARBANKEN_EXPORT = BANK_FIXTURES / "sparbanken-syd-statement.csv"

TITLE = "* Transaktioner Period 2026-01-01 – 2026-03-10 Skapad 2026-03-11 09:15 CET"
HEADER = (
    "Radnr,Clnr,Kontonr,Produkt,Valuta,Bokfdag,Transdag,Valutadag,Referens,Text,"
    "Belopp,Saldo"
)
ACCOUNT = '81234,1234567890,"Föreningskonto",SEK'

# The statement file the fixture export must become: oldest first, the text as the name
# and the reference as the message, personal identity numbers masked, the balance kept.
EXPECTED_STATEMENT = (
    "datum;belopp;namn;meddelande;anteckning;saldo\n"
    "2026-01-07;-130.00;Avgift;;;870.00\n"
    "2026-01-15;200.00;Testa Testsson;Medlemsavgift;;1070.00\n"
    "2026-02-01;-458.00;Lokalföreningen;Faktura 1001;;612.00\n"
    "2026-03-01;250.00;Exempel Exempelsson;[personnummer];;862.00\n"
    "2026-03-10;-45.50;Kortköp, Exempelbutiken;;;816.50\n"
).encode()
FIXTURE_NAMES = ("Exempelbutiken", "Exempel Exempelsson", "Testa Testsson", "Lokalf")

PROFILE = """\
organisation: example
features:
  accounting: true
bank:
  export_format: {format}
  statement_file: books/statement.csv
"""


def row(number: int, day: str, text: str, amount: str, balance: str = "100.00") -> str:
    return f'{number},{ACCOUNT},{day},{day},{day},"","{text}",{amount},{balance}'


def write_export(tmp_path: Path, *lines: str, encoding: str = "cp1252") -> Path:
    path = tmp_path / "export.csv"
    path.write_bytes("".join(f"{line}\r\n" for line in lines).encode(encoding))
    return path


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "config"
    (directory / "books").mkdir(parents=True)
    (directory / "organisation.yaml").write_text(
        PROFILE.format(format="swedbank-csv"), encoding="utf-8"
    )
    return directory


def import_bank(config_dir: Path, export: Path) -> int:
    return main(
        ["import-bank", "example", "--config-dir", str(config_dir), str(export)]
    )


# --- The reader ------------------------------------------------------------------


def test_export_is_read_oldest_first_with_balances_and_masked() -> None:
    export = read_export(EXPORT)

    assert isinstance(export, StatementExport)
    assert [(r.date, r.amount, r.balance) for r in export.rows] == [
        ("2026-01-07", "-130.00", "870.00"),
        ("2026-01-15", "200.00", "1070.00"),
        ("2026-02-01", "-458.00", "612.00"),
        ("2026-03-01", "250.00", "862.00"),
        ("2026-03-10", "-45.50", "816.50"),
    ]
    assert [(r.name, r.message) for r in export.rows[:3]] == [
        ("Avgift", ""),
        ("Testa Testsson", "Medlemsavgift"),
        ("Lokalföreningen", "Faktura 1001"),
    ]
    assert export.rows[3].message == "[personnummer]"
    assert all(r.note == "" for r in export.rows)


def test_text_with_a_comma_is_one_field() -> None:
    assert read_export(EXPORT).rows[4].name == "Kortköp, Exempelbutiken"


def test_date_is_the_banks_booking_date(tmp_path: Path) -> None:
    # Bokfdag, not the transaction date or the value date: the balance follows it.
    line = f'1,{ACCOUNT},2026-03-10,2026-03-08,2026-03-11,"","Kortköp",-1.00,99.00'

    export = read_export(write_export(tmp_path, TITLE, HEADER, line))

    assert export.rows[0].date == "2026-03-10"


def test_rows_of_the_same_day_are_turned_around_with_the_rest(tmp_path: Path) -> None:
    # Row 1 is the newest; the statement file is oldest first.
    export = read_export(
        write_export(
            tmp_path,
            TITLE,
            HEADER,
            row(1, "2026-01-08", "Fourth", "-4.00", "90.00"),
            row(2, "2026-01-08", "Third", "-3.00", "94.00"),
            row(3, "2026-01-07", "Second", "-2.00", "97.00"),
            row(4, "2026-01-07", "First", "-1.00", "99.00"),
        )
    )

    assert [r.name for r in export.rows] == ["First", "Second", "Third", "Fourth"]
    assert [r.balance for r in export.rows] == ["99.00", "97.00", "94.00", "90.00"]


def test_export_that_is_oldest_first_is_kept_in_that_order(tmp_path: Path) -> None:
    # Not seen from this bank, but harmless to accept: the order is unambiguous.
    export = read_export(
        write_export(
            tmp_path,
            TITLE,
            HEADER,
            row(1, "2026-01-07", "First", "-1.00"),
            row(2, "2026-01-08", "Second", "-2.00"),
        )
    )

    assert [r.name for r in export.rows] == ["First", "Second"]


def test_export_without_the_title_line_is_accepted(tmp_path: Path) -> None:
    export = read_export(
        write_export(tmp_path, HEADER, row(1, "2026-01-07", "A", "1.00"))
    )

    assert len(export.rows) == 1


def test_export_saved_as_utf8_is_accepted(tmp_path: Path) -> None:
    path = write_export(
        tmp_path,
        TITLE,
        HEADER,
        row(1, "2026-01-07", "Kortköp", "1.00"),
        encoding="utf-8",
    )

    assert read_export(path).rows[0].name == "Kortköp"


@pytest.mark.parametrize(
    ("raw", "expected"), [("1250.00", "1250.00"), ("-0.50", "-0.50"), ("100", "100")]
)
def test_amounts_are_kept_with_a_decimal_point(
    tmp_path: Path, raw: str, expected: str
) -> None:
    export = read_export(
        write_export(tmp_path, TITLE, HEADER, row(1, "2026-01-07", "A", raw))
    )

    assert export.rows[0].amount == expected


def test_row_without_a_balance_gives_an_empty_balance(tmp_path: Path) -> None:
    export = read_export(
        write_export(tmp_path, TITLE, HEADER, row(1, "2026-01-07", "A", "1.00", ""))
    )

    assert export.rows[0].balance == ""


# --- Whatever does not fit is refused --------------------------------------------

ROW_TEXT = "Hemlig text"
OTHER_ACCOUNT = f'2,81234,9999999999,"Sparkonto",SEK,2026-01-07,2026-01-07,2026-01-07,"","{ROW_TEXT}",1.00,1.00'


@pytest.mark.parametrize(
    "lines",
    [
        (),
        (TITLE,),
        (TITLE, HEADER),
        (
            TITLE,
            HEADER.replace("Saldo", "Balans"),
            row(1, "2026-01-07", ROW_TEXT, "1.00"),
        ),
        (TITLE, HEADER, row(1, "2026-01-07", ROW_TEXT, "1.00") + ",extra"),
        (TITLE, HEADER, f'1,{ACCOUNT},2026-01-07,2026-01-07,"","{ROW_TEXT}",1.00,1.00'),
        (TITLE, HEADER, row(1, "07/01/2026", ROW_TEXT, "1.00")),
        (TITLE, HEADER, row(1, "2026-01-07", ROW_TEXT, "1,00")),
        (TITLE, HEADER, row(1, "2026-01-07", ROW_TEXT, "1 000.00")),
        (TITLE, HEADER, row(1, "2026-01-07", ROW_TEXT, "")),
        (TITLE, HEADER, row(1, "2026-01-07", ROW_TEXT, "1.00", "abc")),
        (
            TITLE,
            HEADER,
            row(1, "2026-01-07", ROW_TEXT, "1.00").replace(",SEK,", ",EUR,"),
        ),
        (TITLE, HEADER, row(1, "2026-01-08", ROW_TEXT, "1.00"), OTHER_ACCOUNT),
        (TITLE, HEADER, row(2, "2026-01-07", ROW_TEXT, "1.00")),
        (
            TITLE,
            HEADER,
            row(1, "2026-01-08", ROW_TEXT, "1.00"),
            row(3, "2026-01-07", ROW_TEXT, "1.00"),
        ),
        (
            TITLE,
            HEADER,
            row(1, "2026-01-07", ROW_TEXT, "1.00").replace("1,81234", "x,81234"),
        ),
        (
            TITLE,
            HEADER,
            row(1, "2026-01-07", ROW_TEXT, "1.00"),
            row(2, "2026-01-09", ROW_TEXT, "1.00"),
            row(3, "2026-01-08", ROW_TEXT, "1.00"),
        ),
    ],
    ids=[
        "empty",
        "title-only",
        "no-transactions",
        "another-header",
        "thirteen-fields",
        "eleven-fields",
        "date",
        "decimal-comma",
        "thousands-space",
        "no-amount",
        "balance",
        "currency",
        "two-accounts",
        "row-numbers-not-from-one",
        "row-number-missing",
        "row-number-not-a-number",
        "dates-in-no-order",
    ],
)
def test_export_that_does_not_fit_is_refused(
    tmp_path: Path, lines: tuple[str, ...]
) -> None:
    with pytest.raises(ExportFormatError) as raised:
        read_export(write_export(tmp_path, *lines))

    # The message names the file and the row, never what the row holds.
    assert "export.csv" in str(raised.value)
    assert "Hemlig" not in str(raised.value)
    assert "9999999999" not in str(raised.value)


@pytest.mark.parametrize(
    "other", [NORDEA_EXPORT, SPARBANKEN_EXPORT], ids=["nordea", "sparbanken"]
)
def test_another_banks_export_is_refused(other: Path) -> None:
    with pytest.raises(ExportFormatError):
        read_export(other)


# --- The statement file ----------------------------------------------------------


def test_statement_file_is_written_exactly(tmp_path: Path) -> None:
    path = tmp_path / "statement.csv"

    written = write_statement(path, read_export(EXPORT).rows)

    assert path.read_bytes() == EXPECTED_STATEMENT
    assert (written.rows, written.first_date, written.last_date) == (
        5,
        "2026-01-07",
        "2026-03-10",
    )


def test_written_statement_is_read_with_its_balances(tmp_path: Path) -> None:
    path = tmp_path / "statement.csv"
    write_statement(path, read_export(EXPORT).rows)

    transactions, findings = read_statement(path, 2026)

    assert findings == []
    assert transactions is not None
    assert [t.balance for t in transactions] == [
        Decimal("870.00"),
        Decimal("1070.00"),
        Decimal("612.00"),
        Decimal("862.00"),
        Decimal("816.50"),
    ]


def test_voucher_text_is_the_text_with_the_reference(tmp_path: Path) -> None:
    path = tmp_path / "statement.csv"
    write_statement(path, read_export(EXPORT).rows)

    texts = read_voucher_texts(path)

    assert texts[2] == "Avgift"
    assert texts[3] == "Testa Testsson(Medlemsavgift)"
    assert texts[5] == "Exempel Exempelsson([personnummer])"


# --- The command selects the reader from the profile -----------------------------


def test_profile_accepts_the_export_format(config_dir: Path) -> None:
    profile = load_profile(config_dir)

    assert profile.bank is not None
    assert profile.bank.export_format == "swedbank-csv"


def test_import_bank_writes_the_statement_file(
    config_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    export = tmp_path / "export.csv"
    shutil.copyfile(EXPORT, export)

    exit_code = import_bank(config_dir, export)

    out = capsys.readouterr().out
    assert exit_code == 0
    assert (config_dir / "books" / "statement.csv").read_bytes() == EXPECTED_STATEMENT
    assert export.read_bytes() == EXPORT.read_bytes()  # the export is never changed
    assert "Wrote statement.csv: 5 rows, 2026-01-07 to 2026-03-10." in out
    for name in FIXTURE_NAMES:
        assert name not in out


@pytest.mark.parametrize(
    "other", [NORDEA_EXPORT, SPARBANKEN_EXPORT], ids=["nordea", "sparbanken"]
)
def test_import_bank_refuses_another_banks_export(
    config_dir: Path, other: Path, caplog: pytest.LogCaptureFixture
) -> None:
    exit_code = import_bank(config_dir, other)

    assert exit_code == 1
    assert not (config_dir / "books" / "statement.csv").exists()
    for name in FIXTURE_NAMES:
        assert name not in caplog.text


@pytest.mark.parametrize("other", ["nordea-csv", "sparbanken-syd-csv"])
def test_other_formats_refuse_this_export(
    config_dir: Path, other: str, caplog: pytest.LogCaptureFixture
) -> None:
    (config_dir / "organisation.yaml").write_text(
        PROFILE.format(format=other), encoding="utf-8"
    )

    exit_code = import_bank(config_dir, EXPORT)

    assert exit_code == 1
    assert not (config_dir / "books" / "statement.csv").exists()
    for name in FIXTURE_NAMES:
        assert name not in caplog.text


def test_export_of_another_period_that_starts_later_is_refused(
    config_dir: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    statement = config_dir / "books" / "statement.csv"
    statement.write_bytes(EXPECTED_STATEMENT)
    later = write_export(
        tmp_path, TITLE, HEADER, row(1, "2026-03-10", "Kortköp", "-45.50")
    )

    exit_code = import_bank(config_dir, later)

    assert exit_code == 1
    assert statement.read_bytes() == EXPECTED_STATEMENT
    assert "fetch the whole year" in caplog.text
