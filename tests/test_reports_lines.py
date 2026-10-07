"""Tests that the reports show vouchers with several lines, line by line (MVP-005).

The figures are computed by hand for the synthetic `lines/` books:
- opening balance 1930 50 000,00, 2010 -50 000,00;
- 1: 7010 30 000 / 2710 9 000, 1930 21 000 (01-25);
  2: 7510 / 2731 9 426 (01-25); 3: 1510 / 3010 12 500 (01-31);
  4: 1930 / 1510 12 500 (02-10);
  5: 7010 30 000,50 and 7010 25 000 / 2710 16 500, 2821 38 500,50 (02-25);
- revenue 12 500,00, costs 94 426,50, result -81 926,50; bank 41 500,00 at the end.
"""

from datetime import datetime
from pathlib import Path

import pytest

from accounting_agent.books import Books
from accounting_agent.formats.front_matter import read_books
from accounting_agent.reports import (
    ReportContext,
    render_balance_sheet,
    render_general_ledger,
    render_income_statement,
    render_voucher_list,
)

NBSP = " "  # the reports' thousands separator
LINES = Path(__file__).parent / "fixtures" / "books" / "lines"
CONTEXT = ReportContext(
    organisation_name="Exempelföreningen",
    organisation_number="000000-0000",
    fiscal_year=2026,
    generated_at=datetime(2026, 10, 7, 10, 15),
    bank_account="1930",
    voucher_folder="../books/verifikationer",
)


@pytest.fixture(scope="module")
def books() -> Books:
    result, findings = read_books(LINES, "1930")
    assert result is not None
    assert findings == []
    return result


def lines(text: str) -> list[str]:
    return text.splitlines()


def test_voucher_list_shows_every_account_of_a_voucher(books: Books) -> None:
    text = render_voucher_list(books, CONTEXT)

    assert "5 verifikationer. Belopp är bokfört belopp." in text
    assert (
        "| [0001](../books/verifikationer/0001_2026-01-25.md) | 2026-01-25 | "
        f"Lön januari | 30{NBSP}000,00 | 7010 Löner | "
        "2710 Personalskatt; 1930 Bankkontot | 20260125-lonespecifikation.md | "
        "Utbetald via banken. |"
    ) in lines(text)


def test_voucher_list_amount_is_the_total_of_the_debit_lines(books: Books) -> None:
    text = render_voucher_list(books, CONTEXT)

    (row,) = [line for line in lines(text) if line.startswith("| [0005]")]
    assert f"| Löner februari | 55{NBSP}000,50 |" in row


def test_general_ledger_has_one_row_per_posting_line(books: Books) -> None:
    text = render_general_ledger(books, CONTEXT)

    link = "[0005](../books/verifikationer/0005_2026-02-25.md)"
    for line in (
        "## 7010 Löner",
        f"| 2026-02-25 | {link} | Löner februari | 30{NBSP}000,50 |  | 60{NBSP}000,50 |",
        f"| 2026-02-25 | {link} | Löner februari | 25{NBSP}000,00 |  | 85{NBSP}000,50 |",
        f"|  |  | **Utgående saldo** |  |  | **85{NBSP}000,50** |",
    ):
        assert line in lines(text)


def test_general_ledger_follows_the_bank_line_of_a_salary(books: Books) -> None:
    text = render_general_ledger(books, CONTEXT)

    for line in (
        "## 1930 Bankkontot",
        "| 2026-01-25 | [0001](../books/verifikationer/0001_2026-01-25.md) | "
        f"Lön januari |  | 21{NBSP}000,00 | 29{NBSP}000,00 |",
        f"|  |  | **Utgående saldo** |  |  | **41{NBSP}500,00** |",
    ):
        assert line in lines(text)


def test_income_statement_sums_every_line(books: Books) -> None:
    text = render_income_statement(books, CONTEXT)

    for line in (
        f"| 3010 | Fakturerade tjänster | 12{NBSP}500,00 |",
        f"| 7010 | Löner | -85{NBSP}000,50 |",
        f"| 7510 | Arbetsgivaravgifter | -9{NBSP}426,00 |",
        f"| Summa intäkter | 12{NBSP}500,00 |",
        f"| Summa kostnader | -94{NBSP}426,50 |",
        f"| **Resultat hittills i år** | **-81{NBSP}926,50** |",
    ):
        assert line in lines(text)


def test_balance_sheet_balances(books: Books) -> None:
    text = render_balance_sheet(books, CONTEXT)

    for line in (
        f"| 1930 | Bankkontot | 50{NBSP}000,00 | -8{NBSP}500,00 | 41{NBSP}500,00 |",
        "| 1510 | Kundfordringar | 0,00 | 0,00 | 0,00 |",
        f"| 2710 | Personalskatt | 0,00 | 25{NBSP}500,00 | 25{NBSP}500,00 |",
        f"| 2821 | Löneskulder | 0,00 | 38{NBSP}500,50 | 38{NBSP}500,50 |",
        f"**Summa tillgångar:** 41{NBSP}500,00 kr",
        "Balansen stämmer: tillgångar är lika med eget kapital och skulder.",
    ):
        assert line in lines(text)
