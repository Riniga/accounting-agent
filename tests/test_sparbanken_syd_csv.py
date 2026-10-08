"""Tests for the `sparbanken-syd-csv` bank export (MVP-005).

The export has no header row: every row is `date;text;amount;currency;`, oldest first,
with a thousands point and a decimal comma in the amount, and no balance. Nothing but the
shape of its rows tells that a file is this export, so the reader refuses whatever does
not fit exactly. The export is synthetic (`tests/fixtures/bank/`), with invented names
and Skatteverket's public test number.
"""

import shutil
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from accounting_agent.books import (
    Account,
    BankTransaction,
    Books,
    OpeningBalance,
    PostingLine,
    Severity,
    Voucher,
    reconcile,
)
from accounting_agent.cli import main
from accounting_agent.formats.bank_statement import (
    read_statement,
    read_voucher_texts,
    write_statement,
)
from accounting_agent.formats.nordea_csv import ExportFormatError, StatementExport
from accounting_agent.formats.sparbanken_syd_csv import read_export
from accounting_agent.profile import load_profile

BANK_FIXTURES = Path(__file__).parent / "fixtures" / "bank"
EXPORT = BANK_FIXTURES / "sparbanken-syd-statement.csv"
NORDEA_EXPORT = BANK_FIXTURES / "nordea-statement.csv"

# The statement file the fixture export must become: oldest first, amounts normalised,
# the text as the name, personal identity numbers masked, no message, note or balance.
EXPECTED_STATEMENT = (
    "datum;belopp;namn;meddelande;anteckning;saldo\n"
    "2026-01-07;-130.00;Avgift;;;\n"
    "2026-01-15;200.00;Swish Testa Testsson;;;\n"
    "2026-02-01;-12458.00;Hyra februari;;;\n"
    "2026-03-01;1250.00;Insättning Exempel Exempelsson [personnummer];;;\n"
    "2026-03-10;-45.50;Kortköp Exempelbutiken;;;\n"
).encode()
FIXTURE_NAMES = ("Exempelbutiken", "Exempel Exempelsson", "Testa Testsson", "Hyra")

PROFILE = """\
organisation: example
features:
  accounting: true
bank:
  export_format: {format}
  statement_file: books/statement.csv
"""


def write_export(tmp_path: Path, *rows: str) -> Path:
    path = tmp_path / "export.csv"
    path.write_bytes(("﻿" + "".join(f"{row}\r\n" for row in rows)).encode("utf-8"))
    return path


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "config"
    (directory / "books").mkdir(parents=True)
    (directory / "organisation.yaml").write_text(
        PROFILE.format(format="sparbanken-syd-csv"), encoding="utf-8"
    )
    return directory


def import_bank(config_dir: Path, export: Path) -> int:
    return main(
        ["import-bank", "example", "--config-dir", str(config_dir), str(export)]
    )


# --- The reader ------------------------------------------------------------------


def test_export_is_read_oldest_first_normalised_and_masked() -> None:
    export = read_export(EXPORT)

    assert isinstance(export, StatementExport)
    assert [(r.date, r.amount) for r in export.rows] == [
        ("2026-01-07", "-130.00"),
        ("2026-01-15", "200.00"),
        ("2026-02-01", "-12458.00"),
        ("2026-03-01", "1250.00"),
        ("2026-03-10", "-45.50"),
    ]
    first = export.rows[0]
    assert (first.name, first.message, first.note, first.balance) == (
        "Avgift",
        "",
        "",
        "",
    )
    assert export.rows[3].name == "Insättning Exempel Exempelsson [personnummer]"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1.234.567,89", "1234567.89"),
        ("-0,50", "-0.50"),
        ("100", "100"),
        ("-631,00", "-631.00"),
        ("1 250,00", "1250.00"),
    ],
)
def test_amounts_are_normalised(tmp_path: Path, raw: str, expected: str) -> None:
    export = read_export(write_export(tmp_path, f"2026-01-07;Text;{raw};SEK;"))

    assert export.rows[0].amount == expected


def test_row_without_the_trailing_separator_is_accepted(tmp_path: Path) -> None:
    export = read_export(write_export(tmp_path, "2026-01-07;Text;-1,00;SEK"))

    assert len(export.rows) == 1


def test_blank_rows_are_skipped(tmp_path: Path) -> None:
    export = read_export(
        write_export(
            tmp_path, "2026-01-08;B;-1,00;SEK;", ";;;;", "2026-01-07;A;-1,00;SEK;"
        )
    )

    assert [row.name for row in export.rows] == ["A", "B"]


def test_rows_of_the_same_day_keep_the_banks_order(tmp_path: Path) -> None:
    # The bank lists oldest first, so the rows of a day are already in order.
    export = read_export(
        write_export(
            tmp_path,
            "2026-01-07;First;-1,00;SEK;",
            "2026-01-07;Second;-2,00;SEK;",
            "2026-01-08;Third;-3,00;SEK;",
            "2026-01-08;Fourth;-4,00;SEK;",
        )
    )

    assert [row.name for row in export.rows] == ["First", "Second", "Third", "Fourth"]


def test_export_with_one_day_only_is_kept_in_the_banks_order(tmp_path: Path) -> None:
    export = read_export(
        write_export(
            tmp_path, "2026-01-07;First;-1,00;SEK;", "2026-01-07;Second;-2,00;SEK;"
        )
    )

    assert [row.name for row in export.rows] == ["First", "Second"]


def test_export_that_is_newest_first_is_turned_around(tmp_path: Path) -> None:
    # Not seen from this bank, but harmless to accept: the order is unambiguous.
    export = read_export(
        write_export(
            tmp_path,
            "2026-01-08;Fourth;-4,00;SEK;",
            "2026-01-08;Third;-3,00;SEK;",
            "2026-01-07;Second;-2,00;SEK;",
            "2026-01-07;First;-1,00;SEK;",
        )
    )

    assert [row.name for row in export.rows] == ["First", "Second", "Third", "Fourth"]


# --- Whatever does not fit is refused --------------------------------------------


@pytest.mark.parametrize(
    "rows",
    [
        (),
        ("2026-01-07;Hemlig text;-1,00",),
        ("2026-01-07;Hemlig text;-1,00;SEK;extra",),
        ("2026-01-07;Hemlig text;-1,00;SEK;;",),
        ("07/01/2026;Hemlig text;-1,00;SEK;",),
        ("2026-01-07;Hemlig text;1,0a;SEK;",),
        ("2026-01-07;Hemlig text;;SEK;",),
        ("2026-01-07;Hemlig text;12.50;SEK;",),
        ("2026-01-07;Hemlig text;1.25,00;SEK;",),
        ("2026-01-07;Hemlig text;-1,00;EUR;",),
        (
            "2026-01-07;Hemlig text;-1,00;SEK;",
            "2026-01-09;Hemlig text;-1,00;SEK;",
            "2026-01-08;Hemlig text;-1,00;SEK;",
        ),
        ("Datum;Text;Belopp;Valuta;", "2026-01-07;Hemlig text;-1,00;SEK;"),
    ],
    ids=[
        "empty",
        "three-fields",
        "fifth-field",
        "six-fields",
        "date",
        "amount",
        "no-amount",
        "decimal-point",
        "wrong-grouping",
        "currency",
        "dates-in-no-order",
        "header-row",
    ],
)
def test_export_that_does_not_fit_is_refused(
    tmp_path: Path, rows: tuple[str, ...]
) -> None:
    with pytest.raises(ExportFormatError) as raised:
        read_export(write_export(tmp_path, *rows))

    # The message names the file and the row, never what the row holds.
    assert "export.csv" in str(raised.value)
    assert "Hemlig" not in str(raised.value)


def test_another_banks_export_is_refused() -> None:
    with pytest.raises(ExportFormatError):
        read_export(NORDEA_EXPORT)


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


def test_written_statement_is_read_without_findings_and_without_balances(
    tmp_path: Path,
) -> None:
    path = tmp_path / "statement.csv"
    write_statement(path, read_export(EXPORT).rows)

    transactions, findings = read_statement(path, 2026)

    assert findings == []
    assert transactions is not None
    assert [t.amount for t in transactions][:2] == [
        Decimal("-130.00"),
        Decimal("200.00"),
    ]
    assert all(t.balance is None for t in transactions)


def test_voucher_text_is_the_banks_text(tmp_path: Path) -> None:
    path = tmp_path / "statement.csv"
    write_statement(path, read_export(EXPORT).rows)

    texts = read_voucher_texts(path)

    assert texts[2] == "Avgift"
    assert texts[5] == "Insättning Exempel Exempelsson [personnummer]"


# --- The command selects the reader from the profile -----------------------------


def test_profile_accepts_the_export_format(config_dir: Path) -> None:
    profile = load_profile(config_dir)

    assert profile.bank is not None
    assert profile.bank.export_format == "sparbanken-syd-csv"


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


def test_import_bank_refuses_another_banks_export(
    config_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    exit_code = import_bank(config_dir, NORDEA_EXPORT)

    assert exit_code == 1
    assert not (config_dir / "books" / "statement.csv").exists()
    assert "nordea-statement.csv" in caplog.text


def test_nordea_profile_refuses_this_export(
    config_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    # Until MVP-005 the Nordea reader was used whatever the profile said; the profile's
    # format now selects the reader, and each reader refuses the other's file.
    (config_dir / "organisation.yaml").write_text(
        PROFILE.format(format="nordea-csv"), encoding="utf-8"
    )

    exit_code = import_bank(config_dir, EXPORT)

    assert exit_code == 1
    assert not (config_dir / "books" / "statement.csv").exists()
    for name in FIXTURE_NAMES:
        assert name not in caplog.text


def test_partial_export_is_refused(
    config_dir: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    statement = config_dir / "books" / "statement.csv"
    statement.write_bytes(EXPECTED_STATEMENT)
    later = write_export(tmp_path, "2026-03-10;Kortköp;-45,50;SEK;")

    exit_code = import_bank(config_dir, later)

    assert exit_code == 1
    assert statement.read_bytes() == EXPECTED_STATEMENT
    assert "fetch the whole year" in caplog.text


# --- Reconciling against a statement without balances ----------------------------


def books_with_bank_voucher() -> Books:
    amount = Decimal("130.00")
    return Books(
        accounts=(
            Account("1930", "Bank"),
            Account("2010", "Equity"),
            Account("6570", "Fees"),
        ),
        opening_balances=(
            OpeningBalance("1930", Decimal("999.00")),  # nothing to check it against
            OpeningBalance("2010", Decimal("-999.00")),
        ),
        vouchers=(
            Voucher(
                series=None,
                number=1,
                date=date(2026, 1, 7),
                text="Fee",
                lines=(
                    PostingLine("6570", debit=amount),
                    PostingLine("1930", credit=amount),
                ),
            ),
        ),
    )


def test_statement_without_balances_says_what_is_not_checked() -> None:
    transactions = (BankTransaction(date(2026, 1, 7), Decimal("-130.00"), None, 2),)

    findings = reconcile(books_with_bank_voucher(), transactions, "1930")

    assert [(f.severity, f.rule) for f in findings] == [
        (Severity.INFO, "bank-no-balances"),
        (Severity.INFO, "bank-summary"),
    ]
    assert findings[0].location == "bank statement"
    assert "opening balance" in findings[0].message


def test_statement_with_a_balance_is_checked_as_before() -> None:
    transactions = (
        BankTransaction(date(2026, 1, 7), Decimal("-130.00"), Decimal("869.00"), 2),
    )

    findings = reconcile(books_with_bank_voucher(), transactions, "1930")

    assert [f.rule for f in findings] == ["bank-summary"]
