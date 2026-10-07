"""Tests for `accounting-agent new-voucher` with several lines, and without a bank
transaction (MVP-005), on a private copy of the synthetic `example-lines` organisation.

Its statement has two transactions without a voucher: row 4, 2026-03-25, -21000 (a salary)
and row 5, 2026-03-28, 12500 (the payment of an invoice that is not recorded yet).
Whatever is refused must leave every file as it was.
"""

import shutil
from pathlib import Path

import pytest

from accounting_agent.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
SALARY = ("--date", "2026-03-25", "--amount", "-21000")
SALARY_LINES = ("--debit", "7010=30000", "--credit", "2710=9000")
INVOICE = (
    "--date",
    "2026-03-20",
    "--text",
    "Faktura 2",
    "--debit",
    "1510=12500",
    "--credit",
    "3010=12500",
)
PAYSLIP = "20260325-lonespecifikation.md"
# Names, messages and texts that must never be printed.
SECRETS = ("Exempel Anställd", "Exempelkunden", "Lön mars", "Faktura 2", "Hemlig")


@pytest.fixture
def fixtures(tmp_path: Path) -> Path:
    """A private copy of all fixtures, so that a test can write to the books."""
    target = tmp_path / "fixtures"
    shutil.copytree(FIXTURES, target)
    return target


@pytest.fixture
def org(fixtures: Path) -> Path:
    return fixtures / "example-lines"


def vouchers(fixtures: Path) -> Path:
    return fixtures / "books" / "lines" / "verifikationer"


def content(fixtures: Path, name: str) -> str:
    return (vouchers(fixtures) / name).read_bytes().decode("utf-8")


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


# --- A bank transaction against several accounts ---------------------------------


def test_salary_is_created_with_the_bank_line_from_the_statement(
    fixtures: Path, org: Path
) -> None:
    before = snapshot(fixtures)

    exit_code = new_voucher(
        org, *SALARY, *SALARY_LINES, "--document", PAYSLIP, "--note", "Utbetald."
    )

    assert exit_code == 0
    after = snapshot(fixtures)
    assert set(after) - set(before) == {"books/lines/verifikationer/0006_2026-03-25.md"}
    assert {name: after[name] for name in before} == before
    assert content(fixtures, "0006_2026-03-25.md") == (
        "---\n"
        "verifikation: 6\n"
        "datum: 2026-03-25\n"
        'text: "Exempel Anställd(Lön mars)"\n'
        "belopp: -21000\n"
        "debet: 7010 30000\n"
        "kredit: 2710 9000\n"
        "kredit: 1930 21000\n"
        f"underlag: {PAYSLIP}\n"
        "---\n"
        "\n"
        "Debet 7010 Löner 30000\n"
        "Kredit 2710 Personalskatt 9000\n"
        "Kredit 1930 Bankkontot 21000\n"
        f"Underlag: [{PAYSLIP}](<../../../example-lines/documents/{PAYSLIP}>)\n"
        "\n"
        "Utbetald.\n"
    )


def test_output_lists_each_line_and_nothing_secret(
    org: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = new_voucher(
        org, *SALARY, *SALARY_LINES, "--document", PAYSLIP, "--note", "Hemlig"
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Created voucher 6 (0006_2026-03-25.md)" in out
    assert "2026-03-25, -21000, 3 lines, 1 supporting document" in out
    assert "debit 7010 30000" in out
    assert "credit 2710 9000" in out
    assert "credit 1930 21000" in out
    for secret in (*SECRETS, PAYSLIP, "lonespecifikation", "Löner", "Personalskatt"):
        assert secret not in out


def test_one_account_against_the_bank_prints_one_line_as_before(
    org: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = new_voucher(org, *SALARY, "--account", "7010")

    out = capsys.readouterr().out
    assert exit_code == 0
    # Amounts are printed as the voucher file writes them: whole without decimals.
    assert "2026-03-25, -21000, debit 7010, credit 1930" in out


# --- A voucher without a bank transaction ----------------------------------------


def test_invoice_is_created_without_a_bank_transaction(
    fixtures: Path, org: Path
) -> None:
    exit_code = new_voucher(org, *INVOICE, "--document", "20260320-faktura-2.md")

    assert exit_code == 0
    assert content(fixtures, "0006_2026-03-20.md") == (
        "---\n"
        "verifikation: 6\n"
        "datum: 2026-03-20\n"
        'text: "Faktura 2"\n'
        "belopp: 12500\n"
        "debet: 1510\n"
        "kredit: 3010\n"
        "underlag: 20260320-faktura-2.md\n"
        "---\n"
        "\n"
        "Debet 1510 Kundfordringar · Kredit 3010 Fakturerade tjänster\n"
        "Underlag: [20260320-faktura-2.md]"
        "(<../../../example-lines/documents/20260320-faktura-2.md>)\n"
    )


def test_salary_run_without_the_bank_account_keeps_every_line(
    fixtures: Path, org: Path
) -> None:
    exit_code = new_voucher(
        org,
        "--date",
        "2026-03-25",
        "--text",
        "Löner mars",
        "--debit",
        "7010=30000.50",
        "--debit",
        "7010=25000",
        "--debit",
        "7510=17281.66",
        "--credit",
        "2710=16500",
        "--credit",
        "2731=17281.66",
        "--credit",
        "2821=38500.50",
    )

    assert exit_code == 0
    text = content(fixtures, "0006_2026-03-25.md")
    assert (
        "belopp: 72282.16\n"
        "debet: 7010 30000.50\n"
        "debet: 7010 25000\n"
        "debet: 7510 17281.66\n"
        "kredit: 2710 16500\n"
        "kredit: 2731 17281.66\n"
        "kredit: 2821 38500.50\n"
    ) in text
    assert text.endswith("Kredit 2821 Löneskulder 38500.50\n")


def test_text_is_masked_and_never_printed(
    fixtures: Path, org: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    arguments = [a if a != "Faktura 2" else "Hemlig 19121212-1212" for a in INVOICE]

    exit_code = new_voucher(org, *arguments)

    out = capsys.readouterr().out
    assert exit_code == 0
    assert 'text: "Hemlig [personnummer]"\n' in content(fixtures, "0006_2026-03-20.md")
    assert "Hemlig" not in out
    assert "2026-03-20, 12500, debit 1510, credit 3010" in out


def test_the_same_voucher_twice_creates_one(
    fixtures: Path, org: Path, caplog: pytest.LogCaptureFixture
) -> None:
    assert new_voucher(org, *INVOICE) == 0
    after_first = snapshot(fixtures)

    assert new_voucher(org, *INVOICE) == 1

    assert snapshot(fixtures) == after_first
    assert "[duplicate]" in caplog.text
    assert "voucher 6" in caplog.text


def test_voucher_without_a_bank_transaction_needs_no_bank_section(
    fixtures: Path, org: Path
) -> None:
    config = org / "organisation.yaml"
    text = config.read_bytes().decode("utf-8")
    start, end = text.index("bank:"), text.index("checks:")
    config.write_bytes((text[:start] + text[end:]).encode("utf-8"))

    assert new_voucher(org, *INVOICE) == 0
    assert (vouchers(fixtures) / "0006_2026-03-20.md").is_file()


def test_bank_transaction_still_needs_a_bank_section(
    fixtures: Path, org: Path, caplog: pytest.LogCaptureFixture
) -> None:
    config = org / "organisation.yaml"
    text = config.read_bytes().decode("utf-8")
    start, end = text.index("bank:"), text.index("checks:")
    config.write_bytes((text[:start] + text[end:]).encode("utf-8"))
    before = snapshot(fixtures)

    assert new_voucher(org, *SALARY, *SALARY_LINES) == 1
    assert snapshot(fixtures) == before
    assert "no 'bank' section" in caplog.text


# --- The whole flow --------------------------------------------------------------


def test_invoice_salary_and_payment_leave_valid_books(
    org: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert new_voucher(org, *INVOICE) == 0
    assert new_voucher(org, *SALARY, *SALARY_LINES, "--document", PAYSLIP) == 0
    payment = ("--date", "2026-03-28", "--amount", "12500", "--account", "1510")
    assert new_voucher(org, *payment) == 0
    capsys.readouterr()

    exit_code = validate(org, "--unbooked", "--balances")

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "8 vouchers" in out
    assert "(errors: 0," in out
    assert "unbooked" not in out
    assert "1930;33000" in out  # the bank's latest balance
    assert "1510;0" in out  # both invoices are paid


# --- Refusals leave every file as it was -----------------------------------------


@pytest.mark.parametrize(
    ("arguments", "rule"),
    [
        (
            (*SALARY, "--debit", "7010=30000", "--credit", "2710=8000"),
            "lines-unbalanced",
        ),
        ((*SALARY, *SALARY_LINES, "--account", "7010"), "account-and-lines"),
        ((*SALARY, *SALARY_LINES, "--text", "Egen text"), "text-with-transaction"),
        (SALARY, "account-missing"),
        ((*SALARY, *SALARY_LINES, "--credit", "1930=21000"), "account-is-bank"),
        (
            (*SALARY, "--debit", "7999=30000", "--credit", "2710=9000"),
            "account-unknown",
        ),
        (
            (*SALARY, "--debit", "7010=30000", "--credit", "7010=9000"),
            "account-on-both-sides",
        ),
        (
            ("--date", "2026-03-20", "--debit", "1510=1", "--credit", "3010=1"),
            "text-missing",
        ),
        (("--date", "2026-03-20", "--text", "X", "--debit", "1510=1"), "lines-missing"),
        (
            (
                "--date",
                "2026-03-20",
                "--text",
                "X",
                "--debit",
                "1510=2",
                "--credit",
                "3010=1",
            ),
            "lines-unbalanced",
        ),
        (
            (
                "--date",
                "2026-03-20",
                "--text",
                "X",
                "--debit",
                "1930=1",
                "--credit",
                "3010=1",
            ),
            "bank-without-transaction",
        ),
        (
            (
                "--date",
                "2027-01-01",
                "--text",
                "X",
                "--debit",
                "1510=1",
                "--credit",
                "3010=1",
            ),
            "date-outside-year",
        ),
        (
            ("--date", "2026-03-20", "--text", "X", "--account", "3010"),
            "amount-missing",
        ),
        ((*INVOICE, "--document", "saknas.md"), "document-missing"),
    ],
    ids=[
        "bank-lines-do-not-add-up",
        "account-and-lines",
        "text-for-a-bank-transaction",
        "no-account-and-no-lines",
        "bank-account-among-the-lines",
        "unknown-account",
        "account-on-both-sides",
        "no-text",
        "one-line",
        "unbalanced",
        "bank-account-without-a-transaction",
        "date-outside-the-year",
        "account-without-an-amount",
        "missing-document",
    ],
)
def test_refused_request_writes_nothing(
    fixtures: Path,
    org: Path,
    caplog: pytest.LogCaptureFixture,
    arguments: tuple[str, ...],
    rule: str,
) -> None:
    before = snapshot(fixtures)

    exit_code = new_voucher(org, *arguments)

    assert exit_code == 1
    assert snapshot(fixtures) == before
    assert f"[{rule}]" in caplog.text
    for secret in (*SECRETS, "Egen text", "saknas.md"):
        assert secret not in caplog.text


@pytest.mark.parametrize(
    "line",
    [
        "7010",
        "7010=",
        "7010=abc",
        "701=100",
        "7010=-100",
        "7010=0",
        "7010=1,50",
        "=100",
    ],
)
def test_malformed_line_is_rejected_before_anything_is_read(
    fixtures: Path, org: Path, line: str
) -> None:
    before = snapshot(fixtures)

    with pytest.raises(SystemExit) as raised:
        new_voucher(org, *SALARY, "--debit", line, "--credit", "2710=9000")

    assert raised.value.code == 2
    assert snapshot(fixtures) == before
