"""Tests for `accounting-agent report` (ADR-008): the reports are written to the
configured folder, only from books without errors unless forced, masked, and with the
terminal showing file names and counts only.

Every test works on a private copy of the fixtures, since the command writes files.
"""

import logging
import shutil
from pathlib import Path

import pytest

from accounting_agent.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
ACCOUNTS_REPORTS = (
    "resultatrapport.md",
    "balansrapport.md",
    "huvudbok.md",
    "verifikationslista.md",
    "månadsöversikt.md",
)


@pytest.fixture
def fixtures(tmp_path: Path) -> Path:
    target = tmp_path / "fixtures"
    shutil.copytree(FIXTURES, target)
    return target


def report(config_dir: Path, *extra: str, organisation: str = "example") -> int:
    return main(["report", organisation, "--config-dir", str(config_dir), *extra])


def set_voucher_text(fixtures: Path, old: bytes, new: bytes) -> None:
    path = fixtures / "books" / "valid" / "verifikationer" / "0002_2026-01-15.md"
    path.write_bytes(path.read_bytes().replace(old, new))


def test_report_writes_the_accounts_reports(
    fixtures: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = report(fixtures / "example-full")

    out = capsys.readouterr().out
    output = fixtures / "example-full" / "reports"
    assert exit_code == 0
    for name in ACCOUNTS_REPORTS:
        assert (output / name).is_file()
        assert f"  {name}" in out.splitlines()
    # example-full has a budget, so all nine reports are written.
    assert "Wrote 9 reports to reports, up to 2026-03-01." in out


def test_summary_uses_the_checks_budget_and_to_do_list(fixtures: Path) -> None:
    report(fixtures / "example-full")

    summary = (fixtures / "example-full" / "reports" / "sammanfattning.md").read_text(
        encoding="utf-8"
    )
    assert "| Banksaldo (1930) | 862,00 | Stämmer mot bankens kontoutdrag |" in summary
    assert "## Mot budget" in summary
    assert "- **T1** (underlag): Lämna kvitton för februari" in summary
    assert "Kontrollen ger **OK** (0 fel, 1 varningar)." in summary
    todo = (fixtures / "example-full" / "reports" / "att-göra.md").read_text(
        encoding="utf-8"
    )
    # The unbooked transaction after the last voucher is counted.
    assert "| Alla banktransaktioner är bokförda | 1 obokförda |" in todo


def test_report_prints_no_voucher_text(
    fixtures: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report(fixtures / "example-full")

    out = capsys.readouterr().out
    assert "Bankens årsavgift" not in out
    assert "Medlemsavgift" not in out


def test_reports_link_to_the_voucher_files(fixtures: Path) -> None:
    report(fixtures / "example-full")

    ledger = (fixtures / "example-full" / "reports" / "huvudbok.md").read_text(
        encoding="utf-8"
    )
    assert "[0001](../../books/valid/verifikationer/0001_2026-01-07.md)" in ledger


def test_personal_numbers_are_masked_in_the_written_reports(
    fixtures: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A personal number in a voucher text is a warning, so the reports are written.
    set_voucher_text(
        fixtures, b'"Medlemsavgift 2026"', b'"Medlemsavgift 19121212-1212"'
    )

    exit_code = report(fixtures / "example-full")

    output = fixtures / "example-full" / "reports"
    assert exit_code == 0
    for name in ACCOUNTS_REPORTS:
        text = (output / name).read_text(encoding="utf-8")
        assert "19121212-1212" not in text
    assert "Medlemsavgift [personnummer]" in (output / "huvudbok.md").read_text(
        encoding="utf-8"
    )
    assert "19121212-1212" not in capsys.readouterr().out


def test_books_with_errors_give_no_reports(
    fixtures: Path, caplog: pytest.LogCaptureFixture
) -> None:
    set_voucher_text(fixtures, b"belopp: 200\n", b"belopp: -200\n")

    with caplog.at_level(logging.ERROR):
        exit_code = report(fixtures / "example-full")

    assert exit_code == 1
    assert not (fixtures / "example-full" / "reports").exists()
    assert "no reports were written" in caplog.text


def test_force_writes_reports_from_books_with_errors(
    fixtures: Path, caplog: pytest.LogCaptureFixture
) -> None:
    set_voucher_text(fixtures, b"belopp: 200\n", b"belopp: -200\n")

    with caplog.at_level(logging.WARNING):
        exit_code = report(fixtures / "example-full", "--force")

    assert exit_code == 0
    assert (fixtures / "example-full" / "reports" / "huvudbok.md").is_file()
    assert "--force" in caplog.text


def test_existing_reports_are_replaced_and_other_files_kept(fixtures: Path) -> None:
    output = fixtures / "example-full" / "reports"
    output.mkdir()
    (output / "huvudbok.md").write_text("old", encoding="utf-8")
    (output / "own-notes.md").write_text("mine", encoding="utf-8")

    report(fixtures / "example-full")

    assert (output / "huvudbok.md").read_text(encoding="utf-8").startswith("# Huvudbok")
    assert (output / "own-notes.md").read_text(encoding="utf-8") == "mine"


def test_report_without_a_reports_section_exits_1(
    caplog: pytest.LogCaptureFixture,
) -> None:
    exit_code = report(FIXTURES / "example")

    assert exit_code == 1
    assert "'reports'" in caplog.text


def test_report_organisation_mismatch_exits_1(fixtures: Path) -> None:
    exit_code = report(fixtures / "example-full", organisation="other")

    assert exit_code == 1
    assert not (fixtures / "example-full" / "reports").exists()
