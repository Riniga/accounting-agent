"""The book domain (ADR-006): model, balances, findings and masking — no file I/O."""

from accounting_agent.books.balances import compute_balances
from accounting_agent.books.checks import check_books
from accounting_agent.books.findings import Finding, Severity
from accounting_agent.books.masking import (
    contains_personal_number,
    mask_personal_numbers,
)
from accounting_agent.books.model import (
    Account,
    Books,
    OpeningBalance,
    PostingLine,
    Voucher,
)

__all__ = [
    "Account",
    "Books",
    "Finding",
    "OpeningBalance",
    "PostingLine",
    "Severity",
    "Voucher",
    "check_books",
    "compute_balances",
    "contains_personal_number",
    "mask_personal_numbers",
]
