"""Tests for the chart of accounts against a reference chart (BAS), as `kontroll.py`
checks it (MVP-003 plan §0.3).

The reference fixture is a tiny excerpt in the organisation's four-file format, with an
invented sub-account; it is not a copy of the BAS chart. No message quotes an account's
local name or a description.
"""

from pathlib import Path

import pytest

from accounting_agent.books import (
    Account,
    Finding,
    ReferenceChart,
    Severity,
    check_reference,
)
from accounting_agent.formats.front_matter import read_books
from accounting_agent.formats.reference_chart import read_reference_chart

FIXTURES = Path(__file__).parent / "fixtures"
REFERENCE = FIXTURES / "reference"
VALID_BOOKS = FIXTURES / "books" / "valid"
LOCAL_NAME = "Hemlig Exempelperson"

REFERENCE_CHART = ReferenceChart(
    accounts={
        "1930": "Företagskonto/checkkonto/affärskonto",
        "2010": "Eget kapital",
        "3002": "Försäljning av tjänster",
        "5010": "Lokalhyra",
    },
    excluded=frozenset({"1370"}),
    groups={
        "13": "FINANSIELLA ANLÄGGNINGSTILLGÅNGAR",
        "19": "KASSA OCH BANK",
        "20": "EGET KAPITAL",
        "30": "HUVUDINTÄKTER",
        "50": "LOKALKOSTNADER",
    },
)


def account(
    number: str,
    group: str | None = None,
    reference_description: str | None = None,
) -> Account:
    return Account(
        number, LOCAL_NAME, group=group, reference_description=reference_description
    )


CLEAN = (
    account("1930", "Kassa och bank", "Företagskonto/checkkonto/affärskonto"),
    account("2010", "EGET KAPITAL", "Eget kapital"),
    account("5010", "Lokalkostnader", "Lokalhyra"),
)


def check(*accounts: Account) -> list[Finding]:
    return check_reference(accounts, REFERENCE_CHART)


# --- Reading the reference chart --------------------------------------------------------


def test_reference_chart_is_read_from_its_four_files() -> None:
    reference, findings = read_reference_chart(REFERENCE)

    assert findings == []
    assert reference is not None
    # Main accounts and sub-accounts together; descriptions with whitespace normalised.
    assert reference.accounts["2890"] == "Övriga kortfristiga skulder"
    assert reference.accounts["3002"] == "Försäljning av tjänster"
    assert len(reference.accounts) == 8
    assert reference.excluded == frozenset({"1370"})
    assert reference.groups["19"] == "KASSA OCH BANK"


@pytest.mark.parametrize(
    "name",
    [
        "kontoplan-huvudkonto.csv",
        "kontoplan-underkonto.csv",
        "kontoplan-kontoklasser.csv",
        "kontoplan-använd-ej.csv",
    ],
)
def test_missing_reference_file_is_a_warning_and_skips_the_check(
    tmp_path: Path, name: str
) -> None:
    folder = tmp_path / "reference"
    folder.mkdir()
    for path in REFERENCE.iterdir():
        if path.name != name:
            (folder / path.name).write_bytes(path.read_bytes())

    reference, findings = read_reference_chart(folder)

    assert reference is None
    assert findings == [
        Finding(
            Severity.WARNING,
            "reference-missing",
            "reference/",
            f"missing {name}; the chart is not checked against the reference chart",
        )
    ]


def test_wrong_header_in_a_reference_file_skips_the_check(tmp_path: Path) -> None:
    folder = tmp_path / "reference"
    folder.mkdir()
    for path in REFERENCE.iterdir():
        (folder / path.name).write_bytes(path.read_bytes())
    (folder / "kontoplan-huvudkonto.csv").write_bytes(b"konto;namn\n1930;Bank\n")

    reference, findings = read_reference_chart(folder)

    assert reference is None
    assert [(f.severity, f.rule) for f in findings] == [(Severity.ERROR, "header")]


# --- The chart's own columns in the `front-matter` format -------------------------------


def test_front_matter_reader_keeps_group_and_reference_description() -> None:
    books, _ = read_books(VALID_BOOKS, "1930")

    assert books is not None
    bank = books.accounts[0]
    assert (bank.number, bank.group, bank.reference_description) == (
        "1930",
        "Kassa och bank",
        "Företagskonto/checkkonto/affärskonto",
    )
    # An empty BAS description means "own meaning", not "no column".
    assert books.accounts[3].reference_description == ""


def test_account_class_that_does_not_match_the_first_digit_is_an_error(
    tmp_path: Path,
) -> None:
    books_dir = tmp_path / "books"
    books_dir.mkdir()
    for path in VALID_BOOKS.iterdir():
        if path.is_file():
            (books_dir / path.name).write_bytes(path.read_bytes())
    (books_dir / "verifikationer").mkdir()
    chart = books_dir / "kontoplan.csv"
    chart.write_bytes(
        chart.read_bytes().replace(
            b"Eget kapital och skulder;Eget kapital;2010",
            "Tillgångar;Eget kapital;2010".encode(),
        )
    )

    _, findings = read_books(books_dir, "1930")

    assert (
        Finding(
            Severity.ERROR,
            "account-class",
            "kontoplan.csv:3",
            "account 2010 has the wrong kontoklass; expected 'Eget kapital och skulder'",
        )
        in findings
    )


# --- Checks against the reference chart -------------------------------------------------


def test_chart_that_matches_the_reference_gives_no_findings() -> None:
    assert check(*CLEAN) == []


def test_account_on_the_do_not_use_list_is_an_error() -> None:
    findings = check(*CLEAN, account("1370", "Finansiella anläggningstillgångar", ""))

    assert (
        Finding(
            Severity.ERROR,
            "reference-excluded",
            "account 1370",
            "is on the reference chart's list of accounts not to use",
        )
        in findings
    )


def test_own_accounts_not_in_the_reference_are_listed_once() -> None:
    findings = check(
        *CLEAN,
        account("3099", "Huvudintäkter", ""),
        account("1990", "Kassa och bank", ""),
    )

    assert findings == [
        Finding(
            Severity.INFO,
            "reference-own-accounts",
            "chart of accounts",
            "own accounts not in the reference chart: 1990, 3099",
        )
    ]


def test_empty_reference_description_means_an_own_meaning() -> None:
    findings = check(*CLEAN, account("3002", "Huvudintäkter", ""))

    assert findings == [
        Finding(
            Severity.INFO,
            "reference-other-meaning",
            "account 3002",
            "used with its own meaning; the reference chart means something else",
        )
    ]


def test_reference_description_that_differs_is_a_warning() -> None:
    findings = check(*CLEAN, account("3002", "Huvudintäkter", "Försäljning av varor"))

    assert findings == [
        Finding(
            Severity.WARNING,
            "reference-description",
            "account 3002",
            "the reference description differs from the reference chart",
        )
    ]


def test_whitespace_differences_in_the_description_are_ignored() -> None:
    assert check(account("5010", "Lokalkostnader", "  Lokalhyra ")) == []


def test_account_in_no_known_group_is_an_error() -> None:
    findings = check(*CLEAN, account("6570", "Övriga externa tjänster", ""))

    assert (
        Finding(
            Severity.ERROR,
            "reference-unknown-group",
            "account 6570",
            "belongs to no known account group (65)",
        )
        in findings
    )


def test_group_that_differs_from_the_reference_is_a_warning() -> None:
    # The chart's group must be the start of the reference group, case-insensitively.
    findings = check(account("1930", "Bank", "Företagskonto/checkkonto/affärskonto"))

    assert findings == [
        Finding(
            Severity.WARNING,
            "reference-group",
            "account 1930",
            "the account group differs from the reference chart's group 19",
        )
    ]


def test_format_without_group_or_description_columns_skips_those_rules() -> None:
    # Aktivitet Förebygger's chart has neither column (ADR-007).
    assert check(account("1930"), account("5010")) == []


def test_accounts_that_are_not_four_digits_are_left_to_the_general_checks() -> None:
    assert check(*CLEAN, account("19300")) == []


def test_no_message_quotes_a_name_or_a_description() -> None:
    findings = check(
        account("1370", LOCAL_NAME, LOCAL_NAME),
        account("3002", LOCAL_NAME, LOCAL_NAME),
        account("6570", LOCAL_NAME, ""),
        account("3990", LOCAL_NAME, ""),
    )

    assert len(findings) >= 4
    for finding in findings:
        assert LOCAL_NAME not in finding.render()
        assert "Försäljning" not in finding.render()
