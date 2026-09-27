"""Tests for `accounting-agent validate` with a `checks` section: the detail checks run,
with the documents folder listed by the CLI and the conventions from the profile.

`example-full` has every supporting document its vouchers name, and treats 2890 as a
parking account.
"""

import shutil
from pathlib import Path

import pytest

from accounting_agent.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
FULL = FIXTURES / "example-full"
DOCUMENT_NAMES = (
    "20260201-faktura-lokal-1001.pdf",
    "20260301-transaktion-in-250.pdf",
    "20260301-kvitto.pdf",
)


@pytest.fixture
def fixtures(tmp_path: Path) -> Path:
    """A private copy of all fixtures, so a test can remove a document."""
    target = tmp_path / "fixtures"
    shutil.copytree(FIXTURES, target)
    return target


def validate(config_dir: Path, *extra: str) -> int:
    return main(["validate", "example", "--config-dir", str(config_dir), *extra])


def test_detail_checks_run_with_a_checks_section(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = validate(FULL)

    out = capsys.readouterr().out
    assert exit_code == 0
    assert (
        "INFO [documents-summary] vouchers: 3 of 5 vouchers have no supporting "
        "document (of which 1 costs)"
    ) in out
    assert (
        "INFO [parking-summary] account 2890: 1 postings, net -50.00 to distribute "
        "(should be 0 at closing)"
    ) in out
    assert "RESULT: OK (errors: 0, warnings: 1, info: 4)" in out


def test_chart_is_checked_against_the_reference_chart(
    capsys: pytest.CaptureFixture[str],
) -> None:
    validate(FULL)

    out = capsys.readouterr().out
    # 3002 has an empty BAS description in the chart: an own meaning.
    assert (
        "INFO [reference-other-meaning] account 3002: used with its own meaning; "
        "the reference chart means something else"
    ) in out
    assert "Medlemsavgifter" not in out  # the account's local name


def test_missing_document_is_an_error_without_its_file_name(
    fixtures: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (fixtures / "example-full" / "documents" / "20260301-kvitto.pdf").unlink()

    exit_code = validate(fixtures / "example-full")

    out = capsys.readouterr().out
    assert exit_code == 1
    assert (
        "ERROR [document-missing] voucher 5: supporting document 2 of 2 is not in the "
        "documents folder"
    ) in out
    for name in DOCUMENT_NAMES:
        assert name not in out


def test_without_a_checks_section_the_detail_checks_do_not_run(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The MVP-002 example: its vouchers lack documents, but nothing is reported.
    validate(FIXTURES / "example")

    out = capsys.readouterr().out
    assert "documents-summary" not in out
    assert "RESULT: OK (errors: 0, warnings: 0, info: 0)" in out
