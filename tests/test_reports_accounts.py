"""Tests for the accounts reports (ADR-008): income statement, balance sheet, general
ledger, voucher list and monthly overview, in Swedish, as Helsingborgs Judoklubb's
`generera_redovisning.py` renders them.

The figures are computed by hand for the synthetic `valid/` books:
- opening balance 1930 1 000,00, 2010 -800,00, 2890 -200,00;
- 1: 6570 / 1930 130,00 (01-07); 2: 1930 / 3002 200,00 (01-15);
  3: 5010 / 1930 458,00 (02-01); 4: 2890 / 2010 50,00 (02-10);
  5: 1930 / 3002 250,00 (03-01);
- revenue 450,00, costs 588,00, result -138,00; bank 862,00 at the end.
"""

from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from accounting_agent.books import Books, FundValue, PostingLine, Voucher
from accounting_agent.formats.front_matter import read_books
from accounting_agent.reports import (
    ReportContext,
    render_balance_sheet,
    render_general_ledger,
    render_income_statement,
    render_monthly_overview,
    render_reports,
    render_voucher_list,
)

NBSP = " "
VALID = Path(__file__).parent / "fixtures" / "books" / "valid"
CONTEXT = ReportContext(
    organisation_name="Exempelklubben",
    organisation_number="000000-0000",
    fiscal_year=2026,
    generated_at=datetime(2026, 9, 27, 10, 15),
    bank_account="1930",
    voucher_folder="../books/verifikationer",
)
FUND = (FundValue(date(2026, 9, 19), Decimal("12500.00")),)


@pytest.fixture(scope="module")
def books() -> Books:
    result, _ = read_books(VALID, "1930")
    assert result is not None
    return result


def lines(text: str) -> list[str]:
    return text.splitlines()


# --- Income statement -------------------------------------------------------------------


def test_income_statement_groups_accounts_and_sums_them(books: Books) -> None:
    text = render_income_statement(books, CONTEXT)

    assert text.startswith("# Resultatrapport\n")
    for line in (
        "## Rörelsens intäkter",
        "| **Huvudintäkter** |  |  |",
        "| 3002 | Medlemsavgifter | 450,00 |",
        "|  | **Summa huvudintäkter** | **450,00** |",
        "## Rörelsens kostnader",
        "| **Lokalkostnader** |  |  |",
        "| 5010 | Hyra | -458,00 |",
        "| 6570 | Bankkostnader | -130,00 |",
        "| Summa intäkter | 450,00 |",
        "| Summa kostnader | -588,00 |",
        "| **Rörelseresultat** | **-138,00** |",
        "| Finansiella poster | 0,00 |",
        "| **Resultat hittills i år** | **-138,00** |",
    ):
        assert line in lines(text)
    assert "## Finansiella poster\n\nInga poster.\n" in text


def test_income_statement_notes_parked_income(books: Books) -> None:
    context = replace(CONTEXT, parking_accounts=("3002",))

    text = render_income_statement(books, context)

    assert (
        "> **Konto 3002 (Medlemsavgifter)** innehåller 450,00 kr av intäkterna. "
        "Det är inbetalningar som ännu inte fördelats på rätt intäktskonto, så "
        "fördelningen mellan intäktsslagen är preliminär."
    ) in lines(text)


def test_income_statement_notes_the_unbooked_fund_value(books: Books) -> None:
    context = replace(CONTEXT, fund_account="1350", fund_values=FUND)

    text = render_income_statement(books, context)

    assert (
        f"> **Ej bokfört:** Fondens marknadsvärde är 12{NBSP}500,00 kr (2026-09-19) "
        f"mot bokfört värde 0,00 kr. Värdeförändringen, 12{NBSP}500,00 kr, bokförs "
        "vid bokslut och ingår inte i resultatet ovan."
    ) in lines(text)


def test_accounts_without_a_group_are_grouped_by_their_two_digits(
    books: Books,
) -> None:
    # Aktivitet Förebygger's chart has no group column (ADR-007).
    no_groups = replace(
        books, accounts=tuple(replace(a, group=None) for a in books.accounts)
    )

    text = render_income_statement(no_groups, CONTEXT)

    assert "| **Kontogrupp 30** |  |  |" in lines(text)


# --- Balance sheet ----------------------------------------------------------------------


def test_balance_sheet_shows_opening_change_and_closing(books: Books) -> None:
    text = render_balance_sheet(books, CONTEXT)

    assert text.startswith("# Balansrapport\n")
    for line in (
        "## Tillgångar",
        f"| 1930 | Bankkontot | 1{NBSP}000,00 | -138,00 | 862,00 |",
        "**Summa tillgångar:** 862,00 kr",
        "## Eget kapital och skulder",
        "| 2010 | Eget kapital | 800,00 | 50,00 | 850,00 |",
        "| 2890 | Skulder | 200,00 | -50,00 | 150,00 |",
        "|  | Periodens resultat | 0,00 | -138,00 | -138,00 |",
        "**Summa eget kapital och skulder (inklusive periodens resultat):** 862,00 kr",
        "Balansen stämmer: tillgångar är lika med eget kapital och skulder.",
    ):
        assert line in lines(text)


def test_balance_sheet_notes_the_fund_market_value(books: Books) -> None:
    context = replace(CONTEXT, fund_account="1350", fund_values=FUND)

    text = render_balance_sheet(books, context)

    assert (
        f"> Fonden (1350) är bokförd till 0,00 kr. Marknadsvärdet var "
        f"12{NBSP}500,00 kr (2026-09-19), som bokförs vid bokslut."
    ) in lines(text)


def test_balance_sheet_that_does_not_balance_says_so(books: Books) -> None:
    # Balanced vouchers cannot unbalance the sheet; an opening balance that does not
    # sum to 0 can (check_books() reports it as an error, but --force still renders).
    broken = replace(
        books,
        opening_balances=tuple(
            replace(o, amount=Decimal("-700.00")) if o.account == "2010" else o
            for o in books.opening_balances
        ),
    )

    text = render_balance_sheet(broken, CONTEXT)

    assert "> **Balansen stämmer inte.** Skillnad 100,00 kr." in lines(text)


# --- General ledger ---------------------------------------------------------------------


def test_general_ledger_starts_with_a_trial_balance(books: Books) -> None:
    text = render_general_ledger(books, CONTEXT)

    assert text.startswith("# Huvudbok\n")
    for line in (
        "## Saldobalans",
        f"| 1930 | Bankkontot | 1{NBSP}000,00 | 450,00 | 588,00 | 862,00 |",
        "| 3002 | Medlemsavgifter | 0,00 | 0,00 | 450,00 | -450,00 |",
        f"|  | **Summa** | **0,00** | **1{NBSP}088,00** | **1{NBSP}088,00** | **0,00** |",
        "Summa debet är lika med summa kredit, och summan av utgående saldon är 0.",
    ):
        assert line in lines(text)


def test_general_ledger_lists_every_posting_with_a_running_balance(
    books: Books,
) -> None:
    text = render_general_ledger(books, CONTEXT)

    for line in (
        "## 1930 Bankkontot",
        f"|  |  | Ingående balans |  |  | 1{NBSP}000,00 |",
        "| 2026-01-07 | [0001](../books/verifikationer/0001_2026-01-07.md) | "
        "Bankens årsavgift |  | 130,00 | 870,00 |",
        "| 2026-03-01 | [0005](../books/verifikationer/0005_2026-03-01.md) | "
        'Swish: medlemsavgift "VT26" | 250,00 |  | 862,00 |',
        "|  |  | **Utgående saldo** |  |  | **862,00** |",
    ):
        assert line in lines(text)


def test_without_a_voucher_folder_the_voucher_is_not_a_link(books: Books) -> None:
    text = render_general_ledger(books, replace(CONTEXT, voucher_folder=None))

    assert "| 2026-01-07 | 0001 | Bankens årsavgift |  | 130,00 | 870,00 |" in lines(
        text
    )


# --- Voucher list -----------------------------------------------------------------------


def test_voucher_list_has_one_row_per_voucher(books: Books) -> None:
    text = render_voucher_list(books, CONTEXT)

    assert text.startswith("# Verifikationslista\n")
    assert "5 verifikationer. Belopp är bokfört belopp." in text
    for line in (
        "| [0003](../books/verifikationer/0003_2026-02-01.md) | 2026-02-01 | "
        "Lokalhyra februari | 458,00 | 5010 Hyra | 1930 Bankkontot | "
        "20260201-faktura-lokal-1001.pdf | "
        "Hyra för februari. Fakturan betalades via bankgiro. |",
        "| [0005](../books/verifikationer/0005_2026-03-01.md) | 2026-03-01 | "
        'Swish: medlemsavgift "VT26" | 250,00 | 1930 Bankkontot | '
        "3002 Medlemsavgifter | "
        "20260301-transaktion-in-250.pdf; 20260301-kvitto.pdf |  |",
    ):
        assert line in lines(text)


def test_voucher_list_names_the_guessed_posting_marker(books: Books) -> None:
    context = replace(CONTEXT, guessed_posting_marker="Gissad kontering")

    text = render_voucher_list(books, context)

    assert (
        "Anteckningar med *Gissad kontering* är preliminära och ska kontrolleras."
        in text
    )


def test_long_notes_are_shortened(books: Books) -> None:
    long_note = replace(books.vouchers[0], note="Ord " * 60)

    text = render_voucher_list(replace(books, vouchers=(long_note,)), CONTEXT)

    row = next(line for line in lines(text) if line.startswith("| [0001]"))
    note = row.split(" | ")[-1].removesuffix(" |")
    assert len(note) == 168
    assert note.endswith("…")


def test_voucher_with_several_lines_lists_every_account(books: Books) -> None:
    split = Voucher(
        series="B",
        number=7,
        date=date(2026, 3, 5),
        text="Delad",
        lines=(
            PostingLine("1930", debit=Decimal("300.00")),
            PostingLine("3002", credit=Decimal("200.00")),
            PostingLine("2890", credit=Decimal("100.00")),
        ),
    )

    text = render_voucher_list(replace(books, vouchers=(split,)), CONTEXT)

    assert (
        "| B7 | 2026-03-05 | Delad | 300,00 | 1930 Bankkontot | "
        "3002 Medlemsavgifter; 2890 Skulder |  |  |"
    ) in lines(text)


# --- Monthly overview -------------------------------------------------------------------


def test_monthly_overview_has_one_row_per_month_to_the_last_voucher(
    books: Books,
) -> None:
    text = render_monthly_overview(books, CONTEXT)

    assert text.startswith("# Månadsöversikt\n")
    for line in (
        "| Månad | Intäkter | Kostnader | Resultat | Bank (1930) vid månadens slut |",
        f"| Januari | 200,00 | -130,00 | 70,00 | 1{NBSP}070,00 |",
        "| Februari | 0,00 | -458,00 | -458,00 | 612,00 |",
        "| Mars | 250,00 | 0,00 | 250,00 | 862,00 |",
        "| **Summa** | **450,00** | **-588,00** | **-138,00** | **862,00** |",
        f"Ingående banksaldo: 1{NBSP}000,00 kr.",
    ):
        assert line in lines(text)
    assert "| April |" not in text


# --- All reports ------------------------------------------------------------------------


def test_render_reports_gives_every_report_but_the_budget_without_one(
    books: Books,
) -> None:
    # Phase 9 added the summary, the to-do report and the closing comments; the budget
    # follow-up only comes with a budget.
    reports = render_reports(books, CONTEXT)

    assert set(reports) == {
        "sammanfattning.md",
        "att-göra.md",
        "resultatrapport.md",
        "balansrapport.md",
        "huvudbok.md",
        "verifikationslista.md",
        "månadsöversikt.md",
        "bokslutskommentarer.md",
    }
    for text in reports.values():
        assert text.endswith("\n")
        assert not text.endswith("\n\n")
        assert "Period 2026-01-01 till 2026-03-01" in text


def test_the_organisation_number_is_not_masked(books: Books) -> None:
    # Regression (phase 8): masking the whole text hid the organisation number, which
    # has the same shape as a personal identity number. Only table cells are masked.
    context = replace(CONTEXT, organisation_number="802000-1234")

    for text in render_reports(books, context).values():
        assert "(org.nr 802000-1234)" in text
