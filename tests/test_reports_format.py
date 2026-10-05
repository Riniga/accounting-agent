"""Tests for the report building blocks (ADR-008): Swedish amounts, Markdown tables with
masking, and the report header — as Helsingborgs Judoklubb's `generera_redovisning.py`
formats them.
"""

from datetime import date, datetime
from decimal import Decimal

import pytest

from accounting_agent.reports import (
    ReportContext,
    format_amount,
    render_header,
    table,
)

NBSP = " "
CONTEXT = ReportContext(
    organisation_name="Exempelklubben",
    organisation_number="000000-0000",
    fiscal_year=2026,
    generated_at=datetime(2026, 9, 27, 10, 15),
    bank_account="1930",
)


@pytest.mark.parametrize(
    ("value", "decimals", "expected"),
    [
        (Decimal("1234.5"), 2, f"1{NBSP}234,50"),
        (Decimal("-1234567.891"), 2, f"-1{NBSP}234{NBSP}567,89"),
        (Decimal("0"), 2, "0,00"),
        (Decimal("-45.5"), 2, "-45,50"),
        (Decimal("33.3"), 0, "33"),
        (Decimal("12500"), 0, f"12{NBSP}500"),
    ],
)
def test_amounts_have_a_space_for_thousands_and_a_decimal_comma(
    value: Decimal, decimals: int, expected: str
) -> None:
    assert format_amount(value, decimals) == expected


def test_table_has_a_header_an_alignment_row_and_the_rows() -> None:
    result = table(["Konto", "Belopp"], [["1930", "862,00"]], right=(1,))

    assert result == "| Konto | Belopp |\n|---|---:|\n| 1930 | 862,00 |"


def test_table_cells_are_masked_and_pipes_escaped() -> None:
    result = table(["Text"], [["Swish 19121212-1212"], ["a|b"], [42]])

    assert result.splitlines()[2:] == [
        "| Swish [personnummer] |",
        "| a\\|b |",
        "| 42 |",
    ]


def test_header_names_the_organisation_year_period_and_generation() -> None:
    result = render_header("Resultatrapport", CONTEXT, date(2026, 3, 1))

    assert result == (
        "# Resultatrapport\n"
        "\n"
        "**Exempelklubben** (org.nr 000000-0000) · Räkenskapsår 2026 · "
        "Period 2026-01-01 till 2026-03-01 · Preliminär, bokslut ej gjort\n"
        "\n"
        "> Genererad 2026-09-27 10:15 av Accounting Agent ur bokföringen. "
        "Ändra inte för hand, rapporten skrivs över.\n"
    )
