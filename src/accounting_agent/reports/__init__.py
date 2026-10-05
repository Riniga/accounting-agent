"""The reports (ADR-008): Swedish Markdown rendered from the book model — no file I/O.

The CLI writes the returned texts to the organisation's configured output folder.
"""

from accounting_agent.reports.accounts import (
    render_balance_sheet,
    render_general_ledger,
    render_income_statement,
    render_monthly_overview,
    render_voucher_list,
)
from accounting_agent.reports.format import (
    ReportContext,
    format_amount,
    render_header,
    table,
)
from accounting_agent.reports.overview import (
    render_budget_follow_up,
    render_closing_comments,
    render_reports,
    render_summary,
    render_todo,
)

__all__ = [
    "ReportContext",
    "format_amount",
    "render_balance_sheet",
    "render_budget_follow_up",
    "render_closing_comments",
    "render_general_ledger",
    "render_header",
    "render_income_statement",
    "render_monthly_overview",
    "render_reports",
    "render_summary",
    "render_todo",
    "render_voucher_list",
    "table",
]
