"""Building blocks for the Swedish Markdown reports (ADR-008): amounts, tables and the
report header, formatted as Helsingborgs Judoklubb's `generera_redovisning.py` does.

Every table cell is masked: the reports hold voucher texts by design, but never a
personal identity number.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from accounting_agent.books import FundValue
from accounting_agent.books.masking import FILE_MASK, mask_personal_numbers

NBSP = " "
PRELIMINARY = "Preliminär, bokslut ej gjort"


@dataclass(frozen=True)
class ReportContext:
    """Everything the reports need besides the books."""

    organisation_name: str
    organisation_number: str
    fiscal_year: int
    generated_at: datetime
    bank_account: str
    parking_accounts: tuple[str, ...] = ()
    fund_account: str | None = None
    fund_values: tuple[FundValue, ...] = ()
    # The voucher folder relative to the output folder, for links; None: no links.
    voucher_folder: str | None = None
    guessed_posting_marker: str | None = None


def format_amount(value: Decimal, decimals: int = 2) -> str:
    """``1234.5`` → ``'1 234,50'``: non-breaking space for thousands, decimal comma."""
    rounded = value.quantize(Decimal(1) if decimals == 0 else Decimal("0.01"))
    text = f"{abs(rounded):,.{decimals}f}".replace(",", NBSP).replace(".", ",")
    return ("-" if rounded < 0 else "") + text


def bold(text: str) -> str:
    """Markdown bold."""
    return f"**{text}**"


def table(
    headers: Sequence[str],
    rows: Iterable[Sequence[object]],
    right: Sequence[int] = (),
) -> str:
    """A Markdown table; ``right`` lists the right-aligned columns."""
    lines = [
        "| " + " | ".join(headers) + " |",
        "|"
        + "|".join("---:" if i in right else "---" for i in range(len(headers)))
        + "|",
    ]
    for row in rows:
        cells = (
            mask_personal_numbers(str(cell), mask=FILE_MASK).replace("|", "\\|")
            for cell in row
        )
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_header(title: str, context: ReportContext, period_end: date) -> str:
    """The title, the organisation and period line, and the generation note."""
    year = context.fiscal_year
    parts = [
        f"{bold(context.organisation_name)} (org.nr {context.organisation_number})",
        f"Räkenskapsår {year}",
        f"Period {year}-01-01 till {period_end}",
        PRELIMINARY,
    ]
    return (
        f"# {title}\n\n"
        + " · ".join(parts)
        + "\n\n"
        + f"> Genererad {context.generated_at:%Y-%m-%d %H:%M} av Accounting Agent ur "
        "bokföringen. Ändra inte för hand, rapporten skrivs över.\n"
    )
