"""Tests for the remaining reports (ADR-008): budget follow-up, closing comments, the
to-do report and the summary — Swedish Markdown, as `generera_redovisning.py` renders
them, without its member parts (MVP-003, out of scope).

The books are the synthetic `valid/` books (revenue 450,00, costs 588,00, result
-138,00, bank 862,00 on 2026-03-01); the budget, comments and to-do list are
`example-full`'s.
"""

from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from accounting_agent.books import (
    Books,
    Finding,
    FundValue,
    PostingLine,
    Severity,
    Voucher,
)
from accounting_agent.formats.front_matter import read_books
from accounting_agent.formats.supplements import read_budget, read_comments, read_todo
from accounting_agent.reports import (
    ReportContext,
    render_budget_follow_up,
    render_closing_comments,
    render_reports,
    render_summary,
    render_todo,
)

NBSP = " "
FIXTURES = Path(__file__).parent / "fixtures"
FULL = FIXTURES / "example-full"
FINDINGS = (
    Finding(
        Severity.WARNING,
        "bank-unbooked-recent",
        "bank statement",
        "1 unbooked transactions after 2026-03-01 (2026-03-10 to 2026-03-10, "
        "net -45.50)",
    ),
    Finding(Severity.INFO, "unbooked", "bank statement row 6", "2026-03-10, -45.50"),
    Finding(Severity.INFO, "bank-summary", "bank statement", "5 transactions"),
)


CONTEXT = ReportContext(
    organisation_name="Exempelklubben",
    organisation_number="000000-0000",
    fiscal_year=2026,
    generated_at=datetime(2026, 10, 2, 9, 0),
    bank_account="1930",
    parking_accounts=("2890",),
    fund_account="1350",
    fund_values=(FundValue(date(2026, 9, 19), Decimal("12500.00")),),
    voucher_folder="../books/verifikationer",
    guessed_posting_marker="Gissad kontering",
    no_document_accounts=("6570",),
    outlay_prefix="Utlägg",
    budget=read_budget(FULL / "budget.csv")[0] or (),
    comments=read_comments(FULL / "comments.csv")[0] or (),
    todo=read_todo(FULL / "todo.csv")[0] or (),
    findings=FINDINGS,
    statement_read=True,
)


@pytest.fixture(scope="module")
def books() -> Books:
    result, _ = read_books(FIXTURES / "books" / "valid", "1930")
    assert result is not None
    return result


def with_guessed_outlay(books: Books) -> Books:
    """Add an outlay without documents whose posting is guessed."""
    outlay = Voucher(
        series=None,
        number=6,
        date=date(2026, 3, 5),
        text="Utlägg hall",
        lines=(
            PostingLine("5010", debit=Decimal("100.00")),
            PostingLine("1930", credit=Decimal("100.00")),
        ),
        note="Hyra kanske.\nGissad kontering: hallen eller lokalen",
    )
    return replace(books, vouchers=(*books.vouchers, outlay))


def lines(text: str) -> list[str]:
    return text.splitlines()


# --- Budget follow-up -------------------------------------------------------------------


def test_budget_follow_up_compares_outcome_with_budget(books: Books) -> None:
    text = render_budget_follow_up(books, CONTEXT)

    assert text is not None
    assert text.startswith("# Budgetuppföljning\n")
    assert (
        "Budget 2026 mot bokfört utfall. **16 % av året har gått** (till 2026-03-01). "
        "Ligger utfallet i jämn takt är det ungefär lika stor andel av budgeten."
    ) in lines(text)
    for line in (
        f"| Medlemsavgifter | 3{NBSP}000,00 | 450,00 | 2{NBSP}550,00 | 15 % |",
        f"| Lokal | 6{NBSP}000,00 | 458,00 | 5{NBSP}542,00 | 8 % |",
        "| Bank | 200,00 | 130,00 | 70,00 | 65 % |",
        f"| **Summa** | **6{NBSP}200,00** | **588,00** | **5{NBSP}612,00** | **9 %** |",
        f"| **Resultat** | **-3{NBSP}200,00** | **-138,00** |",
    ):
        assert line in lines(text)


def test_accounts_outside_the_budget_are_shown_as_unbudgeted(books: Books) -> None:
    context = replace(CONTEXT, budget=CONTEXT.budget[:2])  # no item for 6570

    text = render_budget_follow_up(books, context)

    assert text is not None
    assert "| *Ej budgeterat: 6570 Bankkostnader* | 0,00 | 130,00 | -130,00 | – |" in (
        lines(text)
    )


def test_no_budget_gives_no_budget_follow_up(books: Books) -> None:
    assert render_budget_follow_up(books, replace(CONTEXT, budget=())) is None


# --- Closing comments -------------------------------------------------------------------


def test_closing_comments_are_grouped_by_type(books: Books) -> None:
    text = render_closing_comments(books, CONTEXT)

    assert text.startswith("# Bokslutskommentarer\n")
    for line in (
        "## Redovisningsprinciper",
        "- **2026-02-01**: Intäkter bokförs när pengarna kommer in.",
        "## Väsentliga händelser",
        "- **2026-03-01** (konto 3002 Medlemsavgifter; verifikation 2, 5): "
        "Medlemsavgifterna betalas via Swish.",
    ):
        assert line in lines(text)
    assert "## Noter" not in text


def test_closing_comments_are_masked(books: Books) -> None:
    comment = replace(CONTEXT.comments[0], text="Återbetalning till 19121212-1212")

    text = render_closing_comments(books, replace(CONTEXT, comments=(comment,)))

    assert "Återbetalning till [personnummer]" in text
    assert "19121212-1212" not in text


def test_no_comments_says_so(books: Books) -> None:
    text = render_closing_comments(books, replace(CONTEXT, comments=()))

    assert "Inga kommentarer." in lines(text)


# --- To-do report -----------------------------------------------------------------------


def test_todo_report_lists_the_measures_without_member_measures(books: Books) -> None:
    text = render_todo(books, CONTEXT)

    assert text.startswith("# Att göra för att vara nöjda\n")
    for line in (
        "## Krav just nu (4 av 6 uppfyllda)",
        "| Kontrollen ger inga fel | 0 fel | 0 fel | ✓ |",
        "| Alla banktransaktioner är bokförda | 1 obokförda | 0 obokförda | ✗ |",
        "| Bankens saldo stämmer med bokföringen | stämmer | stämmer | ✓ |",
        "| Inga poster ligger parkerade på 2890 | 1 poster | 0 poster | ✗ |",
        "| Inga gissade konteringar återstår | 0 verifikationer | 0 verifikationer "
        "| ✓ |",
        "| Alla utbetalningar har underlag (utom konto 6570) | 0 saknar, varav 0 "
        "utlägg | 0 saknar | ✓ |",
    ):
        assert line in lines(text)
    assert "medlem" not in text.lower()


def test_todo_report_lists_open_tasks_per_owner_and_when(books: Books) -> None:
    text = render_todo(books, CONTEXT)

    for line in (
        "## Du (kassören): uppgifter nu (1)",
        "| T1 | underlag | Lämna kvitton för februari | Alla kvitton finns i underlag "
        "| öppen |",
        "## Vi (skript och agent): uppgifter vid bokslut (1)",
        "| T3 | fond | Bokför fondens värdeförändring | Värdeförändringen är bokförd "
        "| väntar på T1 |",
    ):
        assert line in lines(text)
    assert "## Vi (skript och agent): uppgifter nu (0)\n\nInga uppgifter.\n" in text


def test_todo_report_lists_guessed_postings_and_outlays(books: Books) -> None:
    text = render_todo(with_guessed_outlay(books), CONTEXT)

    for line in (
        "| Inga gissade konteringar återstår | 1 verifikationer | 0 verifikationer "
        "| ✗ |",
        "| Alla utbetalningar har underlag (utom konto 6570) | 1 saknar, varav 1 "
        "utlägg | 0 saknar | ✗ |",
        "### Gissade konteringar (1)",
        "| 0006 | 2026-03-05 | 100,00 | 5010 / 1930 | "
        "Gissad kontering: hallen eller lokalen |",
        "### Utbetalningar utan underlag (1)",
        "| 0006 | 2026-03-05 | 100,00 | 5010 Hyra | Utlägg hall |",
    ):
        assert line in lines(text)


def test_without_conventions_those_measures_are_left_out(books: Books) -> None:
    context = replace(
        CONTEXT,
        parking_accounts=(),
        guessed_posting_marker=None,
        no_document_accounts=(),
        outlay_prefix=None,
    )

    text = render_todo(books, context)

    assert "## Krav just nu (2 av 4 uppfyllda)" in lines(text)
    assert "| Alla utbetalningar har underlag | 1 saknar | 0 saknar | ✗ |" in lines(
        text
    )
    assert "parkerade" not in text
    assert "Gissade" not in text


# --- Summary ----------------------------------------------------------------------------


def test_summary_gives_the_position_in_figures(books: Books) -> None:
    text = render_summary(books, CONTEXT)

    assert text.startswith("# Sammanfattning: läget i ekonomin\n")
    for line in (
        "| Banksaldo (1930) | 862,00 | Stämmer mot bankens kontoutdrag |",
        "| Fond (1350), bokfört värde | 0,00 |  |",
        f"| Fond (1350), marknadsvärde | 12{NBSP}500,00 | per 2026-09-19, "
        f"värdeförändring 12{NBSP}500,00 kr ej bokförd |",
        "| Intäkter hittills i år | 450,00 |  |",
        "| Kostnader hittills i år | -588,00 |  |",
        "| **Resultat hittills i år** | **-138,00** | före värdeförändring på fonden |",
        "| Eget kapital vid årets början | 800,00 |  |",
        "| Eget kapital nu (inklusive resultat hittills) | 712,00 |  |",
        "| Skulder | 150,00 |  |",
        "| Summa tillgångar | 862,00 | lika med eget kapital plus skulder |",
    ):
        assert line in lines(text)


def test_bank_balance_is_not_reconciled_without_a_statement_or_with_bank_errors(
    books: Books,
) -> None:
    error = Finding(Severity.ERROR, "bank-balance", "bank statement 2026-01-15", "x")

    for context in (
        replace(CONTEXT, statement_read=False),
        replace(CONTEXT, findings=(*FINDINGS, error)),
    ):
        text = render_summary(books, context)
        assert "| Banksaldo (1930) | 862,00 | Ej avstämt mot banken |" in lines(text)


def test_summary_compares_with_budget_and_lists_what_to_do(books: Books) -> None:
    text = render_summary(books, CONTEXT)

    for line in (
        "## Mot budget",
        f"16 % av året har gått. Intäkterna är 450,00 kr mot budget 3{NBSP}000,00 kr, "
        f"kostnaderna 588,00 kr mot budget 6{NBSP}200,00 kr. Se "
        "[budgetuppföljning](budgetuppföljning.md).",
        "## Att åtgärda",
        "### Du (kassören): 1 uppgifter nu, 0 vid bokslut",
        "- **T1** (underlag): Lämna kvitton för februari",
        "### Vi (skript och agent): 0 uppgifter nu, 1 vid bokslut",
        "Alla uppgifter, klart-kriterier och listor över berörda verifikationer finns "
        "i [att-göra](att-göra.md).",
    ):
        assert line in lines(text)
    assert "Just nu är **4 av 6 krav** uppfyllda." in text


def test_summary_reports_the_check_result_with_its_warnings(books: Books) -> None:
    text = render_summary(books, CONTEXT)

    assert "Kontrollen ger **OK** (0 fel, 1 varningar)." in lines(text)
    assert (
        "- bank statement: 1 unbooked transactions after 2026-03-01 "
        "(2026-03-10 to 2026-03-10, net -45.50)"
    ) in lines(text)


def test_summary_links_the_reports(books: Books) -> None:
    text = render_summary(books, CONTEXT)

    for line in (
        "| [Resultatrapport](resultatrapport.md) | Intäkter och kostnader per konto, "
        "resultat hittills |",
        "| [Budgetuppföljning](budgetuppföljning.md) | Utfall mot budget per post |",
        "| [Bokslutskommentarer](bokslutskommentarer.md) | Kommentarer till "
        "redovisningen |",
    ):
        assert line in lines(text)
    assert "Medlemsavgifter per medlem" not in text


def test_summary_without_budget_has_no_budget_section_or_link(books: Books) -> None:
    text = render_summary(books, replace(CONTEXT, budget=()))

    assert "## Mot budget" not in text
    assert "budgetuppföljning.md" not in text


def test_summary_masks_task_texts(books: Books) -> None:
    task = replace(CONTEXT.todo[0], task="Ring 19121212-1212")

    text = render_summary(books, replace(CONTEXT, todo=(task,)))

    assert "- **T1** (underlag): Ring [personnummer]" in lines(text)


# --- All reports ------------------------------------------------------------------------


def test_render_reports_gives_all_nine_reports_in_order(books: Books) -> None:
    assert list(render_reports(books, CONTEXT)) == [
        "sammanfattning.md",
        "att-göra.md",
        "resultatrapport.md",
        "balansrapport.md",
        "budgetuppföljning.md",
        "månadsöversikt.md",
        "huvudbok.md",
        "verifikationslista.md",
        "bokslutskommentarer.md",
    ]
