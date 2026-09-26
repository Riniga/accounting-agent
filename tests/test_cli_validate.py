"""Tests for `accounting-agent validate`: findings report, balances and masked output."""

import logging
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import accounting_agent.cli as cli
from accounting_agent.books import Finding, Severity
from accounting_agent.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures(tmp_path: Path) -> Path:
    """A private copy of all fixtures, so a test can break the example's books."""
    target = tmp_path / "fixtures"
    shutil.copytree(FIXTURES, target)
    return target


def break_bank_sign(fixtures: Path) -> None:
    path = fixtures / "books" / "valid" / "verifikationer" / "0002_2026-01-15.md"
    path.write_bytes(path.read_bytes().replace(b"belopp: 200\n", b"belopp: -200\n"))


def validate(config_dir: Path, *extra: str) -> int:
    return main(["validate", "example", "--config-dir", str(config_dir), *extra])


def test_valid_books_report_ok_and_exit_0(
    example_config_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = validate(example_config_dir)

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "fiscal year 2026" in out
    assert "6 accounts, 3 opening balances, 5 vouchers" in out
    assert "RESULT: OK (errors: 0, warnings: 0, info: 0)" in out


def test_errors_are_grouped_counted_and_exit_1(
    fixtures: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    break_bank_sign(fixtures)

    exit_code = validate(fixtures / "example")

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "ERROR (1)" in out
    assert "ERROR [bank-sign] 0002_2026-01-15.md:" in out
    assert "RESULT: ERROR (errors: 1, warnings: 0, info: 0)" in out


def test_warnings_alone_still_exit_0(
    fixtures: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = fixtures / "books" / "valid" / "verifikationer" / "0002_2026-01-15.md"
    path.write_bytes(
        path.read_bytes().replace(b"Medlemsavgift 2026", b"Swish 191212121212")
    )

    exit_code = validate(fixtures / "example")

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "WARNING (1)" in out
    assert "[personal-number] voucher 2" in out
    assert "RESULT: OK (errors: 0, warnings: 1, info: 0)" in out
    assert "191212121212" not in out


def test_unreadable_books_exit_1_with_the_reading_findings(
    fixtures: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (fixtures / "books" / "valid" / "kontoplan.csv").unlink()

    exit_code = validate(fixtures / "example")

    out = capsys.readouterr().out
    assert exit_code == 1
    assert "[file-missing] kontoplan.csv" in out
    assert "RESULT: ERROR (the books could not be read)" in out


def test_balances_are_listed_sorted_by_account(
    example_config_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = validate(example_config_dir, "--balances")

    out = capsys.readouterr().out
    assert exit_code == 0
    balances = out.split("BALANCES (debit +, credit -)\n", 1)[1].split("\n\n", 1)[0]
    assert balances.splitlines() == [
        "1930;862.00",
        "2010;-850.00",
        "2890;-150.00",
        "3002;-450",
        "5010;458",
        "6570;130.00",
    ]


def test_balances_are_not_listed_without_the_option(
    example_config_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    validate(example_config_dir)

    assert "BALANCES" not in capsys.readouterr().out


def test_every_output_line_is_masked(
    example_config_dir: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Defence in depth: even a finding that did contain a personal number is masked.
    leaky = Finding(Severity.WARNING, "test", "voucher 1", "from 121212-1212")
    monkeypatch.setattr(cli, "check_books", lambda books, fiscal_year: [leaky])

    validate(example_config_dir)

    out = capsys.readouterr().out
    assert "121212-1212" not in out
    assert "[personal number]" in out


def test_organisation_must_match_the_profile(
    example_config_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    exit_code = main(["validate", "other-org", "--config-dir", str(example_config_dir)])

    assert exit_code == 1
    assert "other-org" in caplog.text


def test_profile_without_books_section_is_an_error(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    (tmp_path / "organisation.yaml").write_text(
        "organisation: example\nfeatures:\n  accounting: true\n", encoding="utf-8"
    )

    with caplog.at_level(logging.ERROR):
        exit_code = validate(tmp_path)

    assert exit_code == 1
    assert "books" in caplog.text


def test_invalid_profile_is_an_error(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    exit_code = validate(tmp_path / "missing")

    assert exit_code == 1
    assert "does not exist" in caplog.text


def test_validate_requires_config_dir(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["validate", "example"])

    assert excinfo.value.code == 2
    assert "--config-dir" in capsys.readouterr().err


def test_module_entry_point_runs_validate(example_config_dir: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "accounting_agent",
            "validate",
            "example",
            "--config-dir",
            str(example_config_dir),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "RESULT: OK" in result.stdout
