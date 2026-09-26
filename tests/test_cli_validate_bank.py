"""Tests for `accounting-agent validate` with a `bank` section: reconciliation and
`--unbooked`, on the synthetic `example-full` organisation.

`example-full` shares the `valid/` books with `example`. Its statement matches every bank
voucher and has one transaction after the last voucher (2026-03-10, -45.50).
"""

import shutil
from pathlib import Path

import pytest

from accounting_agent.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
FULL = FIXTURES / "example-full"
# Names and messages in the fixture statement; they must never be printed.
STATEMENT_TEXTS = (
    "Exempelbanken",
    "Testa Testsson",
    "Lokalföreningen",
    "Exempel Exempelsson",
    "Exempelbolaget",
    "Medlemsavgift",
    "Hyra februari",
    "Egen anteckning",
)


@pytest.fixture
def fixtures(tmp_path: Path) -> Path:
    """A private copy of all fixtures, so a test can break the statement."""
    target = tmp_path / "fixtures"
    shutil.copytree(FIXTURES, target)
    return target


def validate(config_dir: Path, *extra: str) -> int:
    return main(["validate", "example", "--config-dir", str(config_dir), *extra])


def test_validate_reconciles_against_the_bank(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = validate(FULL)

    out = capsys.readouterr().out
    assert exit_code == 0
    assert (
        "WARNING [bank-unbooked-recent] bank statement: 1 unbooked transactions after "
        "2026-03-01 (2026-03-10 to 2026-03-10, net -45.50)"
    ) in out
    assert (
        "INFO [bank-summary] bank statement: 5 transactions 2026-01-07 to 2026-03-10, "
        "the bank's latest balance 816.50 (2026-03-10)"
    ) in out
    assert "RESULT: OK (errors: 0, warnings: 1, info: 1)" in out


def test_unbooked_lists_date_amount_and_row_only(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = validate(FULL, "--unbooked")

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "INFO [unbooked] bank statement row 6: 2026-03-10, -45.50" in out
    assert "RESULT: OK (errors: 0, warnings: 1, info: 2)" in out


def test_no_name_or_message_from_the_statement_is_printed(
    capsys: pytest.CaptureFixture[str],
) -> None:
    validate(FULL, "--unbooked", "--balances")

    captured = capsys.readouterr()
    for text in STATEMENT_TEXTS:
        assert text not in captured.out + captured.err


def test_missing_statement_file_is_info_and_not_an_error(
    fixtures: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (fixtures / "example-full" / "statement.csv").unlink()

    exit_code = validate(fixtures / "example-full")

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "INFO [bank-statement-missing] statement.csv:" in out


def test_broken_bank_balance_exits_1(
    fixtures: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    statement = fixtures / "example-full" / "statement.csv"
    statement.write_bytes(statement.read_bytes().replace(b";1070.00\n", b";1071.00\n"))

    exit_code = validate(fixtures / "example-full")

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "ERROR [bank-balance] bank statement 2026-01-15:" in out


def test_without_a_bank_section_nothing_is_reconciled(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The MVP-002 example has no `bank` section; its report is unchanged.
    exit_code = validate(FIXTURES / "example", "--unbooked")

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "bank-" not in out
    assert "RESULT: OK (errors: 0, warnings: 0, info: 0)" in out
