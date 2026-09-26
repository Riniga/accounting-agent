"""Tests for the MVP-003 sections of an organisation profile (organisation.yaml).

`bank`, `checks`, `conventions` and `reports` are all optional (ADR-007, ADR-008). Paths
resolve relative to the configuration directory, like `books.path`.
"""

import logging
from collections.abc import Callable
from pathlib import Path

import pytest

from accounting_agent.profile import ProfileError, load_profile

HEADER = """\
organisation: example
features:
  accounting: true
"""

BANK = """\
bank:
  export_format: nordea-csv
  statement_file: books/statement.csv
  fund_account: "1350"
  fund_value_file: books/fund-value.csv
"""

CHECKS = """\
checks:
  reference_chart: reference
  documents: documents
  budget_file: books/budget.csv
  comments_file: books/comments.csv
  todo_file: books/todo.csv
"""

CONVENTIONS = """\
conventions:
  parking_accounts: ["3008"]
  no_document_accounts: [6570]
  guessed_posting_marker: Guessed posting
  outlay_prefix: outlay
"""

REPORTS = """\
reports:
  output: reports
  organisation_name: Example Club
  organisation_number: 000000-0000
"""


@pytest.fixture
def config_dir_with_folders(
    write_profile: Callable[[str], Path],
) -> Callable[[str], Path]:
    """Write organisation.yaml and create the folders the sections point at."""

    def _write(content: str) -> Path:
        config_dir = write_profile(content)
        for name in ("books", "reference", "documents"):
            (config_dir / name).mkdir(exist_ok=True)
        return config_dir

    return _write


# --- All sections optional ------------------------------------------------------------


def test_profile_without_the_new_sections_still_loads(
    write_profile: Callable[[str], Path],
) -> None:
    profile = load_profile(write_profile(HEADER))

    assert profile.bank is None
    assert profile.checks is None
    assert profile.reports is None
    # Conventions always exist, empty by default, so checks can read them directly.
    assert profile.conventions.parking_accounts == ()
    assert profile.conventions.no_document_accounts == ()
    assert profile.conventions.guessed_posting_marker is None
    assert profile.conventions.outlay_prefix is None


@pytest.mark.parametrize("section", ["bank", "checks", "conventions", "reports"])
def test_new_sections_are_not_reported_as_unknown_keys(
    config_dir_with_folders: Callable[[str], Path],
    caplog: pytest.LogCaptureFixture,
    section: str,
) -> None:
    config_dir = config_dir_with_folders(HEADER + BANK + CHECKS + CONVENTIONS + REPORTS)

    with caplog.at_level(logging.WARNING):
        load_profile(config_dir)

    assert f"Ignoring unknown key '{section}'" not in caplog.text


@pytest.mark.parametrize("section", ["bank", "checks", "conventions", "reports"])
def test_section_must_be_a_mapping(
    write_profile: Callable[[str], Path], section: str
) -> None:
    config_dir = write_profile(HEADER + f"{section}: yes\n")

    with pytest.raises(ProfileError, match=f"'{section}'"):
        load_profile(config_dir)


@pytest.mark.parametrize(
    ("section", "content"),
    [
        ("bank", BANK),
        ("checks", CHECKS),
        ("conventions", CONVENTIONS),
        ("reports", REPORTS),
    ],
)
def test_unknown_sub_key_is_ignored_with_a_warning(
    config_dir_with_folders: Callable[[str], Path],
    caplog: pytest.LogCaptureFixture,
    section: str,
    content: str,
) -> None:
    # Forward compatibility, as for top-level and `books` keys.
    config_dir = config_dir_with_folders(HEADER + content + "  later_key: 1\n")

    with caplog.at_level(logging.WARNING):
        load_profile(config_dir)

    assert f"{section}.later_key" in caplog.text


# --- bank -----------------------------------------------------------------------------


def test_valid_bank_section_is_loaded(
    config_dir_with_folders: Callable[[str], Path],
) -> None:
    config_dir = config_dir_with_folders(HEADER + BANK)

    bank = load_profile(config_dir).bank

    assert bank is not None
    assert bank.export_format == "nordea-csv"
    # The statement file is written by import-bank, so it need not exist yet.
    assert bank.statement_file == (config_dir / "books" / "statement.csv").resolve()
    assert bank.fund_account == "1350"
    assert bank.fund_value_file == (config_dir / "books" / "fund-value.csv").resolve()


def test_bank_without_a_fund_is_allowed(
    config_dir_with_folders: Callable[[str], Path],
) -> None:
    content = "\n".join(line for line in BANK.splitlines() if "fund" not in line)
    config_dir = config_dir_with_folders(HEADER + content + "\n")

    bank = load_profile(config_dir).bank

    assert bank is not None
    assert bank.fund_account is None
    assert bank.fund_value_file is None


@pytest.mark.parametrize("key", ["export_format", "statement_file"])
def test_missing_bank_key_is_an_error(
    config_dir_with_folders: Callable[[str], Path], key: str
) -> None:
    lines = [line for line in BANK.splitlines() if not line.strip().startswith(key)]
    config_dir = config_dir_with_folders(HEADER + "\n".join(lines) + "\n")

    with pytest.raises(ProfileError, match=f"'bank.{key}'"):
        load_profile(config_dir)


@pytest.mark.parametrize("missing", ["fund_account", "fund_value_file"])
def test_fund_account_and_fund_value_file_go_together(
    config_dir_with_folders: Callable[[str], Path], missing: str
) -> None:
    lines = [line for line in BANK.splitlines() if not line.strip().startswith(missing)]
    config_dir = config_dir_with_folders(HEADER + "\n".join(lines) + "\n")

    with pytest.raises(ProfileError, match="fund"):
        load_profile(config_dir)


def test_unknown_export_format_is_an_error(
    config_dir_with_folders: Callable[[str], Path],
) -> None:
    config_dir = config_dir_with_folders(
        HEADER + BANK.replace("nordea-csv", "some-bank")
    )

    with pytest.raises(ProfileError, match="'bank.export_format'"):
        load_profile(config_dir)


def test_fund_account_given_as_a_number_is_normalised_to_a_string(
    config_dir_with_folders: Callable[[str], Path],
) -> None:
    config_dir = config_dir_with_folders(
        HEADER + BANK.replace('fund_account: "1350"', "fund_account: 1350")
    )

    bank = load_profile(config_dir).bank

    assert bank is not None
    assert bank.fund_account == "1350"


@pytest.mark.parametrize("value", ['"135"', '"13500"', "true", "''"])
def test_fund_account_must_be_four_digits(
    config_dir_with_folders: Callable[[str], Path], value: str
) -> None:
    config_dir = config_dir_with_folders(
        HEADER + BANK.replace('fund_account: "1350"', f"fund_account: {value}")
    )

    with pytest.raises(ProfileError, match="'bank.fund_account'"):
        load_profile(config_dir)


@pytest.mark.parametrize("value", ["''", "42", "[a, b]"])
def test_statement_file_must_be_a_path(
    config_dir_with_folders: Callable[[str], Path], value: str
) -> None:
    config_dir = config_dir_with_folders(
        HEADER
        + BANK.replace(
            "statement_file: books/statement.csv", f"statement_file: {value}"
        )
    )

    with pytest.raises(ProfileError, match="'bank.statement_file'"):
        load_profile(config_dir)


def test_statement_file_folder_must_exist(
    write_profile: Callable[[str], Path],
) -> None:
    # No `books` folder: the core would have nowhere to write the statement.
    config_dir = write_profile(HEADER + BANK)

    with pytest.raises(ProfileError, match="'bank.statement_file'"):
        load_profile(config_dir)


# --- checks ---------------------------------------------------------------------------


def test_valid_checks_section_is_loaded(
    config_dir_with_folders: Callable[[str], Path],
) -> None:
    config_dir = config_dir_with_folders(HEADER + CHECKS)

    checks = load_profile(config_dir).checks

    assert checks is not None
    assert checks.reference_chart == (config_dir / "reference").resolve()
    assert checks.documents == (config_dir / "documents").resolve()
    # The supplementary files are optional: a configured but missing file skips its
    # check, as kontroll.py does.
    assert checks.budget_file == (config_dir / "books" / "budget.csv").resolve()
    assert checks.comments_file == (config_dir / "books" / "comments.csv").resolve()
    assert checks.todo_file == (config_dir / "books" / "todo.csv").resolve()


def test_every_checks_key_is_optional(
    config_dir_with_folders: Callable[[str], Path],
) -> None:
    config_dir = config_dir_with_folders(HEADER + "checks:\n  documents: documents\n")

    checks = load_profile(config_dir).checks

    assert checks is not None
    assert checks.documents is not None
    assert checks.reference_chart is None
    assert checks.budget_file is None
    assert checks.comments_file is None
    assert checks.todo_file is None


@pytest.mark.parametrize("key", ["reference_chart", "documents"])
def test_checks_folder_must_exist(
    write_profile: Callable[[str], Path], key: str
) -> None:
    config_dir = write_profile(HEADER + f"checks:\n  {key}: missing-folder\n")

    with pytest.raises(ProfileError, match=f"'checks.{key}'"):
        load_profile(config_dir)


@pytest.mark.parametrize(
    "key", ["reference_chart", "documents", "budget_file", "comments_file", "todo_file"]
)
def test_checks_value_must_be_a_path(
    write_profile: Callable[[str], Path], key: str
) -> None:
    config_dir = write_profile(HEADER + f"checks:\n  {key}: 42\n")

    with pytest.raises(ProfileError, match=f"'checks.{key}'"):
        load_profile(config_dir)


# --- conventions ----------------------------------------------------------------------


def test_valid_conventions_section_is_loaded(
    write_profile: Callable[[str], Path],
) -> None:
    conventions = load_profile(write_profile(HEADER + CONVENTIONS)).conventions

    assert conventions.parking_accounts == ("3008",)
    # Given unquoted, YAML reads an integer; normalised as for bank_account.
    assert conventions.no_document_accounts == ("6570",)
    assert conventions.guessed_posting_marker == "Guessed posting"
    assert conventions.outlay_prefix == "outlay"


@pytest.mark.parametrize("key", ["parking_accounts", "no_document_accounts"])
@pytest.mark.parametrize("value", ['"3008"', '["300"]', "[true]", "{a: 1}"])
def test_account_lists_must_be_lists_of_four_digit_accounts(
    write_profile: Callable[[str], Path], key: str, value: str
) -> None:
    config_dir = write_profile(HEADER + f"conventions:\n  {key}: {value}\n")

    with pytest.raises(ProfileError, match=f"'conventions.{key}'"):
        load_profile(config_dir)


@pytest.mark.parametrize("key", ["guessed_posting_marker", "outlay_prefix"])
@pytest.mark.parametrize("value", ["''", "42", "[a]"])
def test_text_conventions_must_be_non_empty_text(
    write_profile: Callable[[str], Path], key: str, value: str
) -> None:
    config_dir = write_profile(HEADER + f"conventions:\n  {key}: {value}\n")

    with pytest.raises(ProfileError, match=f"'conventions.{key}'"):
        load_profile(config_dir)


# --- reports --------------------------------------------------------------------------


def test_valid_reports_section_is_loaded(
    write_profile: Callable[[str], Path],
) -> None:
    config_dir = write_profile(HEADER + REPORTS)

    reports = load_profile(config_dir).reports

    assert reports is not None
    # The output folder is created by `report`, so it need not exist yet.
    assert reports.output == (config_dir / "reports").resolve()
    assert reports.organisation_name == "Example Club"
    assert reports.organisation_number == "000000-0000"


@pytest.mark.parametrize("key", ["output", "organisation_name", "organisation_number"])
def test_missing_reports_key_is_an_error(
    write_profile: Callable[[str], Path], key: str
) -> None:
    lines = [line for line in REPORTS.splitlines() if not line.strip().startswith(key)]
    config_dir = write_profile(HEADER + "\n".join(lines) + "\n")

    with pytest.raises(ProfileError, match=f"'reports.{key}'"):
        load_profile(config_dir)


@pytest.mark.parametrize("key", ["output", "organisation_name", "organisation_number"])
@pytest.mark.parametrize("value", ["''", "42", "[a]"])
def test_reports_values_must_be_non_empty_text(
    write_profile: Callable[[str], Path], key: str, value: str
) -> None:
    lines = [
        f"  {key}: {value}" if line.strip().startswith(key) else line
        for line in REPORTS.splitlines()
    ]
    config_dir = write_profile(HEADER + "\n".join(lines) + "\n")

    with pytest.raises(ProfileError, match=f"'reports.{key}'"):
        load_profile(config_dir)
