"""Tests for `accounting-agent new-voucher` (ADR-009), on a private copy of the
synthetic `example-full` organisation.

Its statement has one transaction without a voucher: row 6, 2026-03-10, -45.50. The
command creates the voucher from that row; the caller gives only the account, the
documents and a note. Whatever is refused must leave every file as it was.
"""

import shutil
from pathlib import Path

import pytest

from accounting_agent import cli
from accounting_agent.books import Books, Finding, Severity
from accounting_agent.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
NEW_FILE = "0006_2026-03-10.md"
# The row's name, and the other names and messages in the statement: never printed.
STATEMENT_TEXTS = (
    "Exempelbolaget",
    "Exempelbanken",
    "Testa Testsson",
    "Lokalföreningen",
    "Exempel Exempelsson",
    "Medlemsavgift",
    "Hyra februari",
)
DOCUMENT = "20260301-kvitto.pdf"
ROW_6 = ("--date", "2026-03-10", "--amount", "-45.50")


@pytest.fixture
def fixtures(tmp_path: Path) -> Path:
    """A private copy of all fixtures, so that a test can write to the books."""
    target = tmp_path / "fixtures"
    shutil.copytree(FIXTURES, target)
    return target


@pytest.fixture
def full(fixtures: Path) -> Path:
    return fixtures / "example-full"


def vouchers(fixtures: Path) -> Path:
    return fixtures / "books" / "valid" / "verifikationer"


def snapshot(fixtures: Path) -> dict[str, bytes]:
    """Every file under the fixtures, to prove that nothing was written or changed."""
    return {
        path.relative_to(fixtures).as_posix(): path.read_bytes()
        for path in sorted(fixtures.rglob("*"))
        if path.is_file()
    }


def new_voucher(config_dir: Path, *arguments: str) -> int:
    return main(["new-voucher", "example", "--config-dir", str(config_dir), *arguments])


def validate(config_dir: Path, *extra: str) -> int:
    return main(["validate", "example", "--config-dir", str(config_dir), *extra])


def replace_in(path: Path, old: str, new: str) -> None:
    content = path.read_bytes().decode("utf-8")
    assert old in content, f"{old!r} not in {path.name}"
    path.write_bytes(content.replace(old, new).encode("utf-8"))


# --- A voucher is created --------------------------------------------------------


def test_voucher_is_created_from_the_statement_row(fixtures: Path, full: Path) -> None:
    before = snapshot(fixtures)

    exit_code = new_voucher(full, *ROW_6, "--account", "6570")

    assert exit_code == 0
    after = snapshot(fixtures)
    created = set(after) - set(before)
    assert created == {f"books/valid/verifikationer/{NEW_FILE}"}
    assert {name: after[name] for name in before} == before  # nothing else changed
    assert (vouchers(fixtures) / NEW_FILE).read_bytes().decode("utf-8") == (
        "---\n"
        "verifikation: 6\n"
        "datum: 2026-03-10\n"
        'text: "Exempelbolaget AB(456)"\n'
        "belopp: -45.50\n"
        "debet: 6570\n"
        "kredit: 1930\n"
        "underlag:\n"
        "---\n"
        "\n"
        "Debet 6570 Bankkostnader · Kredit 1930 Bankkontot\n"
    )


def test_output_names_number_date_amount_and_accounts_only(
    full: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = new_voucher(
        full, *ROW_6, "--account", "6570", "--document", DOCUMENT, "--note", "Hemlig"
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert f"Created voucher 6 ({NEW_FILE})" in out
    assert "2026-03-10, -45.50, debit 6570, credit 1930, 1 supporting document" in out
    for secret in (*STATEMENT_TEXTS, DOCUMENT, "kvitto", "Hemlig", "Bankkostnader"):
        assert secret not in out


def test_books_are_valid_and_the_transaction_is_booked_afterwards(
    full: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    new_voucher(full, *ROW_6, "--account", "6570")
    capsys.readouterr()

    exit_code = validate(full, "--unbooked")

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "6 vouchers" in out
    assert "unbooked" not in out
    assert "(errors: 0, warnings: 0," in out


def test_documents_and_note_are_written(fixtures: Path, full: Path) -> None:
    exit_code = new_voucher(
        full,
        *ROW_6,
        "--account",
        "6570",
        "--document",
        DOCUMENT,
        "--document",
        "20260201-faktura-lokal-1001.pdf",
        "--note",
        "Avgift för mars.",
    )

    assert exit_code == 0
    content = (vouchers(fixtures) / NEW_FILE).read_bytes().decode("utf-8")
    assert f"\nunderlag: {DOCUMENT}; 20260201-faktura-lokal-1001.pdf\n" in content
    assert content.endswith(
        "\n"
        "Debet 6570 Bankkostnader · Kredit 1930 Bankkontot\n"
        f"Underlag: [{DOCUMENT}](<../../../example-full/documents/{DOCUMENT}>)\n"
        "Underlag: [20260201-faktura-lokal-1001.pdf]"
        "(<../../../example-full/documents/20260201-faktura-lokal-1001.pdf>)\n"
        "\n"
        "Avgift för mars.\n"
    )
    assert validate(full) == 0


def test_guess_is_marked_with_the_organisations_marker(
    fixtures: Path, full: Path
) -> None:
    replace_in(
        full / "organisation.yaml",
        'parking_accounts: ["2890"]\n',
        'parking_accounts: ["2890"]\n  guessed_posting_marker: Gissad kontering\n',
    )

    exit_code = new_voucher(
        full, *ROW_6, "--account", "6570", "--guess", "--note", "bara ett nummer"
    )

    assert exit_code == 0
    content = (vouchers(fixtures) / NEW_FILE).read_bytes().decode("utf-8")
    assert content.endswith("\n\nGissad kontering: bara ett nummer\n")


def test_row_can_be_given_and_must_match(fixtures: Path, full: Path) -> None:
    before = snapshot(fixtures)

    assert new_voucher(full, *ROW_6, "--row", "5", "--account", "6570") == 1
    assert snapshot(fixtures) == before

    assert new_voucher(full, *ROW_6, "--row", "6", "--account", "6570") == 0


def test_running_twice_creates_one_voucher(
    fixtures: Path, full: Path, caplog: pytest.LogCaptureFixture
) -> None:
    assert new_voucher(full, *ROW_6, "--account", "6570") == 0
    after_first = snapshot(fixtures)

    assert new_voucher(full, *ROW_6, "--account", "6570") == 1

    assert snapshot(fixtures) == after_first
    assert "already-booked" in caplog.text


def test_new_warnings_from_the_voucher_are_printed(
    full: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Money out posted against a revenue account: allowed, but worth a look.
    exit_code = new_voucher(full, *ROW_6, "--account", "3002")

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "WARNING [revenue-account-debited] voucher 6:" in out
    # Warnings the books already had are not repeated.
    assert "bank-unbooked-recent" not in out


# --- Refusals leave every file as it was -----------------------------------------


@pytest.mark.parametrize(
    ("arguments", "rule"),
    [
        ((*ROW_6, "--account", "5999"), "account-unknown"),
        ((*ROW_6, "--account", "1930"), "account-is-bank"),
        (
            ("--date", "2026-03-10", "--amount", "-45", "--account", "6570"),
            "transaction-missing",
        ),
        (
            ("--date", "2026-01-07", "--amount", "-130", "--account", "6570"),
            "already-booked",
        ),
        ((*ROW_6, "--account", "6570", "--document", "saknas.pdf"), "document-missing"),
        (
            (*ROW_6, "--account", "6570", "--document", "../statement.csv"),
            "document-missing",
        ),
        ((*ROW_6, "--account", "6570", "--guess"), "guess-marker-missing"),
    ],
    ids=[
        "unknown-account",
        "bank-account",
        "no-such-transaction",
        "already-booked",
        "missing-document",
        "document-outside-the-folder",
        "guess-without-marker",
    ],
)
def test_refused_request_writes_nothing(
    fixtures: Path,
    full: Path,
    caplog: pytest.LogCaptureFixture,
    arguments: tuple[str, ...],
    rule: str,
) -> None:
    before = snapshot(fixtures)

    exit_code = new_voucher(full, *arguments)

    assert exit_code == 1
    assert snapshot(fixtures) == before
    assert f"[{rule}]" in caplog.text
    for secret in (*STATEMENT_TEXTS, "saknas.pdf"):
        assert secret not in caplog.text


def test_books_with_an_error_are_refused(
    fixtures: Path, full: Path, caplog: pytest.LogCaptureFixture
) -> None:
    (path,) = vouchers(fixtures).glob("0002_*.md")
    replace_in(path, "belopp: 200\n", "belopp: -200\n")  # the wrong sign: an error
    before = snapshot(fixtures)

    exit_code = new_voucher(full, *ROW_6, "--account", "6570")

    assert exit_code == 1
    assert snapshot(fixtures) == before
    assert "the books have 1 error" in caplog.text


def test_unreadable_books_are_refused(
    fixtures: Path, full: Path, caplog: pytest.LogCaptureFixture
) -> None:
    (fixtures / "books" / "valid" / "kontoplan.csv").unlink()
    before = snapshot(fixtures)

    assert new_voucher(full, *ROW_6, "--account", "6570") == 1
    assert snapshot(fixtures) == before
    assert "could not be read" in caplog.text


def test_missing_statement_file_is_refused(
    fixtures: Path, full: Path, caplog: pytest.LogCaptureFixture
) -> None:
    (full / "statement.csv").unlink()
    before = snapshot(fixtures)

    assert new_voucher(full, *ROW_6, "--account", "6570") == 1
    assert snapshot(fixtures) == before
    assert "bank statement" in caplog.text


def test_profile_without_a_bank_section_is_refused(
    fixtures: Path, caplog: pytest.LogCaptureFixture
) -> None:
    before = snapshot(fixtures)

    assert new_voucher(fixtures / "example", *ROW_6, "--account", "6570") == 1
    assert snapshot(fixtures) == before
    assert "no 'bank' section" in caplog.text


def test_profile_without_a_books_section_is_refused(
    fixtures: Path, caplog: pytest.LogCaptureFixture
) -> None:
    config = fixtures / "example" / "organisation.yaml"
    content = config.read_bytes().decode("utf-8")
    config.write_bytes(content[: content.index("books:")].encode("utf-8"))

    assert new_voucher(fixtures / "example", *ROW_6, "--account", "6570") == 1
    assert "no 'books' section" in caplog.text


def test_another_organisations_folder_is_refused(fixtures: Path, full: Path) -> None:
    before = snapshot(fixtures)

    exit_code = main(
        ["new-voucher", "other", "--config-dir", str(full), *ROW_6, "--account", "6570"]
    )

    assert exit_code == 1
    assert snapshot(fixtures) == before


def test_document_without_a_documents_folder_is_refused(
    fixtures: Path, full: Path, caplog: pytest.LogCaptureFixture
) -> None:
    replace_in(full / "organisation.yaml", "  documents: documents\n", "")
    before = snapshot(fixtures)

    exit_code = new_voucher(full, *ROW_6, "--account", "6570", "--document", DOCUMENT)

    assert exit_code == 1
    assert snapshot(fixtures) == before
    assert "[documents-not-configured]" in caplog.text


@pytest.mark.parametrize(
    "arguments",
    [
        ("--date", "10/3 2026", "--amount", "-45.50", "--account", "6570"),
        ("--date", "2026-03-10", "--amount", "-45,50", "--account", "6570"),
        ("--date", "2026-03-10", "--amount", "-45.50", "--account", "657"),
        ("--amount", "-45.50", "--account", "6570"),
    ],
    # Until MVP-005 a missing --account was rejected here too. It is now a refusal,
    # `account-missing`, since the lines can be given instead
    # (test_cli_new_voucher_lines.py).
    ids=["date", "amount", "account", "no-date"],
)
def test_malformed_arguments_are_rejected_before_anything_is_read(
    fixtures: Path, full: Path, arguments: tuple[str, ...]
) -> None:
    before = snapshot(fixtures)

    with pytest.raises(SystemExit) as raised:
        new_voucher(full, *arguments)

    assert raised.value.code == 2
    assert snapshot(fixtures) == before


# --- Errors stop, with one exception ---------------------------------------------


def with_an_older_unbooked_transaction(full: Path) -> None:
    """Add a transaction on 2026-02-15, before the last voucher (2026-03-01)."""
    replace_in(
        full / "statement.csv",
        "2026-03-01;250.00;Exempel Exempelsson;Medlemsavgift [personnummer];;862.00\n"
        "2026-03-10;-45.50;Exempelbolaget AB;456;;816.50\n",
        "2026-02-15;-100.00;Lokalföreningen;Hyra förråd;;512.00\n"
        "2026-03-01;250.00;Exempel Exempelsson;Medlemsavgift [personnummer];;762.00\n"
        "2026-03-10;-45.50;Exempelbolaget AB;456;;716.50\n",
    )


def test_transaction_skipped_earlier_is_an_error_that_the_command_fixes(
    fixtures: Path, full: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with_an_older_unbooked_transaction(full)
    assert validate(full) == 1
    assert "ERROR [bank-unbooked] bank statement row 5:" in capsys.readouterr().out

    exit_code = new_voucher(
        full, "--date", "2026-02-15", "--amount", "-100", "--account", "5010"
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Created voucher 6 (0006_2026-02-15.md)" in out
    # The new voucher is dated before voucher 5: said, but not refused.
    assert "WARNING [voucher-date-order] voucher 6:" in out
    assert validate(full) == 0
    assert "bank-unbooked]" not in capsys.readouterr().out


def test_other_vouchers_can_be_created_while_one_is_skipped(
    fixtures: Path, full: Path
) -> None:
    # The books' only error is bank-unbooked; it does not block the newer row either.
    with_an_older_unbooked_transaction(full)

    assert new_voucher(full, *ROW_6, "--account", "6570") == 0


def test_voucher_that_would_add_an_error_is_refused(
    fixtures: Path,
    full: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # No request can reach this today — every known cause is refused earlier — so the
    # safety net is tested by letting a check object to voucher 6.
    real = cli.check_books
    before_vouchers = list(vouchers(fixtures).iterdir())

    def objecting(books: Books, fiscal_year: int) -> list[Finding]:
        findings = real(books, fiscal_year)
        if len(books.vouchers) == len(before_vouchers) + 1:
            findings.append(
                Finding(Severity.ERROR, "made-up", "voucher 6", "objection")
            )
        return findings

    monkeypatch.setattr(cli, "check_books", objecting)
    before = snapshot(fixtures)

    exit_code = new_voucher(full, *ROW_6, "--account", "6570")

    assert exit_code == 1
    assert snapshot(fixtures) == before
    assert "would add 1 error" in caplog.text
    assert "[made-up] voucher 6: objection" in caplog.text


def test_file_that_appears_before_the_write_is_never_replaced(
    fixtures: Path,
    full: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Another run takes number 6 after the books were read, with a text of its own.
    real = cli.front_matter.render_voucher
    other = vouchers(fixtures) / "0006_2026-03-05.md"

    def render_after_the_other_run(*arguments: object) -> str:
        other.write_bytes(b"the other run's voucher")
        return real(*arguments)  # type: ignore[arg-type]

    monkeypatch.setattr(cli.front_matter, "render_voucher", render_after_the_other_run)

    exit_code = new_voucher(full, *ROW_6, "--account", "6570")

    assert exit_code == 1
    assert other.read_bytes() == b"the other run's voucher"
    assert not (vouchers(fixtures) / NEW_FILE).exists()
    assert "voucher 6 already has a file" in caplog.text


# --- Without a documents folder --------------------------------------------------


def test_command_works_without_a_checks_section(fixtures: Path, full: Path) -> None:
    config = full / "organisation.yaml"
    content = config.read_bytes().decode("utf-8")
    start, end = content.index("checks:"), content.index("conventions:")
    config.write_bytes((content[:start] + content[end:]).encode("utf-8"))

    exit_code = new_voucher(full, *ROW_6, "--account", "6570")

    assert exit_code == 0
    assert (vouchers(fixtures) / NEW_FILE).is_file()


def test_link_is_the_name_alone_when_the_folders_are_on_different_drives(
    fixtures: Path, full: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_relative_path(path: object, start: object) -> str:
        raise ValueError("path is on mount 'D:', start on mount 'C:'")

    monkeypatch.setattr(cli.os.path, "relpath", no_relative_path)

    exit_code = new_voucher(full, *ROW_6, "--account", "6570", "--document", DOCUMENT)

    assert exit_code == 0
    content = (vouchers(fixtures) / NEW_FILE).read_bytes().decode("utf-8")
    assert content.endswith(f"\nUnderlag: [{DOCUMENT}](<{DOCUMENT}>)\n")
