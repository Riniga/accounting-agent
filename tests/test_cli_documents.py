"""Tests for the document checks through the commands (MVP-004), on a private copy of
the synthetic `example-full` organisation.

`validate` names payments without a supporting document and counts the files no voucher
refers to. The names of those files appear only in the to-do report, which stays in the
organisation's own project — never in the terminal.
"""

import shutil
from pathlib import Path

import pytest

from accounting_agent.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
UNUSED = "20260105-kvitto (Exempel).jpg"


@pytest.fixture
def full(tmp_path: Path) -> Path:
    target = tmp_path / "fixtures"
    shutil.copytree(FIXTURES, target)
    return target / "example-full"


def run(command: str, config_dir: Path, *extra: str) -> int:
    return main([command, "example", "--config-dir", str(config_dir), *extra])


def remove_document_from_voucher_3(full: Path) -> None:
    path = full.parent / "books" / "valid" / "verifikationer" / "0003_2026-02-01.md"
    content = path.read_bytes().decode("utf-8")
    line = "underlag: 20260201-faktura-lokal-1001.pdf\n"
    assert line in content
    path.write_bytes(content.replace(line, "").encode("utf-8"))


def test_example_books_have_nothing_to_report(
    full: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Every payment has a document or is on an account that needs none, and every file
    # in the documents folder is referred to.
    exit_code = run("validate", full)

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "documents-expected" not in out
    assert "documents-unused" not in out


def test_validate_names_a_payment_without_a_document(
    full: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    remove_document_from_voucher_3(full)

    exit_code = run("validate", full)

    out = capsys.readouterr().out
    assert exit_code == 0  # a warning, not an error
    assert (
        "WARNING [documents-expected] voucher 3: money out of the bank without a "
        "supporting document"
    ) in out
    # Voucher 1 is a bank charge, on the account configured as needing no document.
    assert "[documents-expected] voucher 1" not in out


def test_validate_counts_unused_documents_without_naming_them(
    full: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (full / "documents" / UNUSED).write_bytes(b"")

    exit_code = run("validate", full)

    out = capsys.readouterr().out
    assert exit_code == 0
    assert (
        "INFO [documents-unused] documents folder: 1 of 4 files are not referred to "
        "by any voucher"
    ) in out
    assert "kvitto" not in out
    assert "Exempel)" not in out


def test_report_lists_the_unused_documents_by_name(
    full: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (full / "documents" / UNUSED).write_bytes(b"")

    exit_code = run("report", full)

    assert exit_code == 0
    todo = (full / "reports" / "att-göra.md").read_bytes().decode("utf-8")
    assert (
        f"### Underlag som ingen verifikation hänvisar till (1)\n\n"
        f"Koppla dem till en verifikation, eller ta bort dem om de inte behövs.\n\n"
        f"- {UNUSED}\n"
    ) in todo
    assert "kvitto" not in capsys.readouterr().out


def test_report_says_when_no_document_is_unused(full: Path) -> None:
    assert run("report", full) == 0

    todo = (full / "reports" / "att-göra.md").read_bytes().decode("utf-8")
    assert "### Underlag som ingen verifikation hänvisar till (0)\n\nInga.\n" in todo


def test_report_has_no_document_list_without_a_documents_folder(full: Path) -> None:
    config = full / "organisation.yaml"
    content = config.read_bytes().decode("utf-8")
    assert "  documents: documents\n" in content
    config.write_bytes(content.replace("  documents: documents\n", "").encode("utf-8"))

    assert run("report", full) == 0

    todo = (full / "reports" / "att-göra.md").read_bytes().decode("utf-8")
    assert "ingen verifikation hänvisar till" not in todo


def test_new_voucher_says_when_the_new_payment_has_no_document(
    full: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = run(
        "new-voucher",
        full,
        "--date",
        "2026-03-10",
        "--amount",
        "-45.50",
        "--account",
        "5010",
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "WARNING [documents-expected] voucher 6:" in out
