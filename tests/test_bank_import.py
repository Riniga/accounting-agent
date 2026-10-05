"""Tests for bank import: the `nordea-csv` export reader, the statement and fund-value
writers, and `accounting-agent import-bank` (ADR-008).

The exports are synthetic (`tests/fixtures/bank/`), with invented names only and
Skatteverket's public test number. The expected output follows the organisation's own
import script (MVP-003 plan §0.3).
"""

import logging
import shutil
from pathlib import Path

import pytest

from accounting_agent.cli import main
from accounting_agent.formats.bank_statement import (
    StatementRefusedError,
    write_fund_values,
    write_statement,
)
from accounting_agent.formats.nordea_csv import (
    ExportFormatError,
    FundExport,
    StatementExport,
    read_export,
)

BANK_FIXTURES = Path(__file__).parent / "fixtures" / "bank"
STATEMENT_EXPORT = BANK_FIXTURES / "nordea-statement.csv"
FUND_EXPORT = BANK_FIXTURES / "nordea-fund.csv"

# The statement file the fixture export must become: oldest first, amounts normalised,
# names from "Ytterligare detaljer" when present, leading zeros stripped from an
# all-digit message, personal identity numbers masked, UTF-8 without BOM, LF.
EXPECTED_STATEMENT = (
    "datum;belopp;namn;meddelande;anteckning;saldo\n"
    "2026-01-07;-130.00;Exempelbanken;Avgift;;870.00\n"
    "2026-01-15;200.00;Testa Testsson;Medlemsavgift;;1070.00\n"
    "2026-02-01;-458.00;Lokalföreningen;Hyra februari;Egen anteckning;612.00\n"
    "2026-03-01;250.00;Exempel Exempelsson;Medlemsavgift [personnummer];;862.00\n"
    "2026-03-10;-45.50;Exempelbolaget AB;456;;816.50\n"
).encode()

EXPECTED_FUND = b"datum;v\xc3\xa4rde\n2026-08-31;12345.67\n2026-09-19;12500.00\n"

# Names that appear in the fixture exports; they must never reach the terminal.
FIXTURE_NAMES = ("Exempelbolaget", "Exempel Exempelsson", "Testa Testsson")


def write_export(tmp_path: Path, lines: list[str], name: str = "export.csv") -> Path:
    path = tmp_path / name
    path.write_bytes(("﻿" + "\n".join(lines) + "\n").encode("utf-8"))
    return path


# --- Reading the export -----------------------------------------------------------------


def test_statement_export_is_recognised_by_its_header() -> None:
    export = read_export(STATEMENT_EXPORT)

    assert isinstance(export, StatementExport)
    assert len(export.rows) == 5  # the blank row is skipped


def test_statement_rows_are_oldest_first_normalised_and_masked() -> None:
    export = read_export(STATEMENT_EXPORT)
    assert isinstance(export, StatementExport)

    first, fourth, last = export.rows[0], export.rows[3], export.rows[4]
    assert (first.date, first.amount, first.balance) == (
        "2026-01-07",
        "-130.00",
        "870.00",
    )
    assert export.rows[1].balance == "1070.00"  # non-breaking space removed
    assert fourth.name == "Exempel Exempelsson"  # "Ytterligare detaljer" wins
    assert fourth.message == "Medlemsavgift [personnummer]"
    assert last.message == "456"  # all digits: leading zeros stripped
    assert export.rows[2].note == "Egen anteckning"


def test_fund_export_is_recognised_by_its_header() -> None:
    export = read_export(FUND_EXPORT)

    assert isinstance(export, FundExport)
    assert export.values == {"2026-09-19": "12500.00", "2026-08-31": "12345.67"}


def test_unknown_export_is_refused(tmp_path: Path) -> None:
    path = write_export(tmp_path, ["Date;Amount;Something", "2026-01-01;1;x"])

    with pytest.raises(ExportFormatError, match="header"):
        read_export(path)


def test_statement_export_without_transactions_is_refused(tmp_path: Path) -> None:
    path = write_export(tmp_path, ["Datum;Belopp;Namn;Meddelande;Saldo"])

    with pytest.raises(ExportFormatError, match="no transactions"):
        read_export(path)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("1 234,50", "1234.50"), ("-1 000", "-1000"), ("250", "250"), ("", "")],
)
def test_amounts_are_normalised(tmp_path: Path, raw: str, expected: str) -> None:
    path = write_export(
        tmp_path,
        ["Datum;Belopp;Namn;Meddelande;Saldo", f"2026-01-02;{raw or '0'};A;B;{raw}"],
    )

    export = read_export(path)

    assert isinstance(export, StatementExport)
    assert export.rows[0].balance == expected


def test_short_rows_give_empty_fields(tmp_path: Path) -> None:
    # The bank may leave out trailing empty cells.
    path = write_export(
        tmp_path,
        ["Datum;Belopp;Namn;Meddelande;Egna anteckningar;Saldo", "2026-01-02;5"],
    )

    export = read_export(path)

    assert isinstance(export, StatementExport)
    row = export.rows[0]
    assert (row.name, row.message, row.note, row.balance) == ("", "", "", "")


# --- Writing the statement file ---------------------------------------------------------


def test_statement_file_is_written_exactly(tmp_path: Path) -> None:
    export = read_export(STATEMENT_EXPORT)
    assert isinstance(export, StatementExport)
    target = tmp_path / "statement.csv"

    result = write_statement(target, export.rows)

    assert target.read_bytes() == EXPECTED_STATEMENT
    assert (result.rows, result.first_date, result.last_date) == (
        5,
        "2026-01-07",
        "2026-03-10",
    )
    assert result.replaced_rows is None


def test_existing_statement_file_is_replaced(tmp_path: Path) -> None:
    export = read_export(STATEMENT_EXPORT)
    assert isinstance(export, StatementExport)
    target = tmp_path / "statement.csv"
    target.write_bytes(
        b"datum;belopp;namn;meddelande;anteckning;saldo\n"
        b"2026-01-07;-130.00;X;Y;;870.00\n"
    )

    result = write_statement(target, export.rows)

    assert result.replaced_rows == 1
    assert target.read_bytes() == EXPECTED_STATEMENT


def test_export_starting_later_than_the_existing_file_is_refused(
    tmp_path: Path,
) -> None:
    # An export from February would silently drop January's transactions.
    export = read_export(STATEMENT_EXPORT)
    assert isinstance(export, StatementExport)
    target = tmp_path / "statement.csv"
    existing = (
        b"datum;belopp;namn;meddelande;anteckning;saldo\n2026-01-02;1.00;X;Y;;1.00\n"
    )
    target.write_bytes(existing)

    with pytest.raises(StatementRefusedError, match="2026-01-07.*2026-01-02"):
        write_statement(target, export.rows)

    assert target.read_bytes() == existing


def test_no_temporary_file_is_left_behind(tmp_path: Path) -> None:
    export = read_export(STATEMENT_EXPORT)
    assert isinstance(export, StatementExport)

    write_statement(tmp_path / "statement.csv", export.rows)

    assert [p.name for p in tmp_path.iterdir()] == ["statement.csv"]


# --- Writing the fund-value file --------------------------------------------------------


def test_fund_values_are_written_sorted(tmp_path: Path) -> None:
    export = read_export(FUND_EXPORT)
    assert isinstance(export, FundExport)
    target = tmp_path / "fund-value.csv"

    result = write_fund_values(target, export.values)

    assert target.read_bytes() == EXPECTED_FUND
    assert (result.values, result.latest_date) == (2, "2026-09-19")


def test_fund_values_are_merged_by_date(tmp_path: Path) -> None:
    target = tmp_path / "fund-value.csv"
    target.write_bytes("datum;värde\n2026-06-30;12000.00\n2026-08-31;1.00\n".encode())

    result = write_fund_values(
        target, {"2026-08-31": "12345.67", "2026-09-19": "12500.00"}
    )

    assert (
        target.read_bytes()
        == (
            "datum;värde\n2026-06-30;12000.00\n2026-08-31;12345.67\n2026-09-19;12500.00\n"
        ).encode()
    )
    assert result.values == 3


# --- The command ------------------------------------------------------------------------

BANK_PROFILE = """\
organisation: example
features:
  accounting: true
bank:
  export_format: nordea-csv
  statement_file: books/statement.csv
  fund_account: "1350"
  fund_value_file: books/fund-value.csv
"""


@pytest.fixture
def bank_config_dir(tmp_path: Path) -> Path:
    config_dir = tmp_path / "config"
    (config_dir / "books").mkdir(parents=True)
    (config_dir / "organisation.yaml").write_text(BANK_PROFILE, encoding="utf-8")
    return config_dir


def import_bank(config_dir: Path, export: Path, organisation: str = "example") -> int:
    return main(
        ["import-bank", organisation, "--config-dir", str(config_dir), str(export)]
    )


def test_import_bank_writes_the_statement_file(
    bank_config_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    export = tmp_path / "export.csv"
    shutil.copyfile(STATEMENT_EXPORT, export)

    exit_code = import_bank(bank_config_dir, export)

    out = capsys.readouterr().out
    assert exit_code == 0
    assert (bank_config_dir / "books" / "statement.csv").read_bytes() == (
        EXPECTED_STATEMENT
    )
    assert "Wrote statement.csv: 5 rows, 2026-01-07 to 2026-03-10." in out


def test_import_bank_leaves_the_export_unchanged(
    bank_config_dir: Path, tmp_path: Path
) -> None:
    export = tmp_path / "export.csv"
    shutil.copyfile(STATEMENT_EXPORT, export)
    before = export.read_bytes()

    import_bank(bank_config_dir, export)

    assert export.read_bytes() == before


def test_import_bank_reports_replaced_rows(
    bank_config_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    import_bank(bank_config_dir, STATEMENT_EXPORT)
    capsys.readouterr()

    import_bank(bank_config_dir, STATEMENT_EXPORT)

    assert "Replaced 5 rows with 5." in capsys.readouterr().out


def test_import_bank_writes_the_fund_value_file(
    bank_config_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = import_bank(bank_config_dir, FUND_EXPORT)

    assert exit_code == 0
    assert (bank_config_dir / "books" / "fund-value.csv").read_bytes() == EXPECTED_FUND
    assert "Wrote fund-value.csv: 2 values, latest 2026-09-19." in (
        capsys.readouterr().out
    )


def test_import_bank_never_prints_names_or_messages(
    bank_config_dir: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.DEBUG):
        import_bank(bank_config_dir, STATEMENT_EXPORT)

    captured = capsys.readouterr()
    output = captured.out + captured.err + caplog.text
    for name in FIXTURE_NAMES:
        assert name not in output
    assert "Medlemsavgift" not in output


def test_import_bank_refusal_exits_1_and_keeps_the_file(
    bank_config_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    statement = bank_config_dir / "books" / "statement.csv"
    existing = (
        b"datum;belopp;namn;meddelande;anteckning;saldo\n2026-01-02;1.00;X;Y;;1.00\n"
    )
    statement.write_bytes(existing)

    exit_code = import_bank(bank_config_dir, STATEMENT_EXPORT)

    assert exit_code == 1
    assert statement.read_bytes() == existing
    assert "whole year" in caplog.text


def test_import_bank_unknown_export_exits_1(
    bank_config_dir: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    export = write_export(tmp_path, ["Date;Amount", "2026-01-01;1"], "odd.csv")
    # "Date;Amount" is not the fund header either ("Datum;Belopp").

    exit_code = import_bank(bank_config_dir, export)

    assert exit_code == 1
    assert "header" in caplog.text


def test_import_bank_missing_export_exits_1(
    bank_config_dir: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    exit_code = import_bank(bank_config_dir, tmp_path / "missing.csv")

    assert exit_code == 1
    assert "missing.csv" in caplog.text


def test_import_bank_without_bank_section_exits_1(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    (tmp_path / "organisation.yaml").write_text(
        "organisation: example\nfeatures:\n  accounting: true\n", encoding="utf-8"
    )

    exit_code = import_bank(tmp_path, STATEMENT_EXPORT)

    assert exit_code == 1
    assert "'bank'" in caplog.text


def test_import_bank_fund_export_without_fund_configuration_exits_1(
    bank_config_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    profile = bank_config_dir / "organisation.yaml"
    profile.write_text(
        "\n".join(line for line in BANK_PROFILE.splitlines() if "fund" not in line),
        encoding="utf-8",
    )

    exit_code = import_bank(bank_config_dir, FUND_EXPORT)

    assert exit_code == 1
    assert "fund_value_file" in caplog.text


def test_import_bank_organisation_mismatch_exits_1(bank_config_dir: Path) -> None:
    exit_code = import_bank(bank_config_dir, STATEMENT_EXPORT, organisation="other")

    assert exit_code == 1
    assert not (bank_config_dir / "books" / "statement.csv").exists()
