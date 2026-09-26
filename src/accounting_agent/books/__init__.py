"""The book domain (ADR-006, ADR-007): model, balances, checks, reconciliation, findings
and masking — no file I/O."""

from accounting_agent.books.balances import compute_balances
from accounting_agent.books.checks import check_books
from accounting_agent.books.findings import Finding, Severity
from accounting_agent.books.masking import (
    contains_personal_number,
    mask_personal_numbers,
)
from accounting_agent.books.model import (
    Account,
    BankTransaction,
    Books,
    OpeningBalance,
    PostingLine,
    Voucher,
)
from accounting_agent.books.reconciliation import reconcile

__all__ = [
    "Account",
    "BankTransaction",
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
    "reconcile",
]
