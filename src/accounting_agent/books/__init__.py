"""The book domain (ADR-006, ADR-007): model, balances, checks, reconciliation, findings
and masking — no file I/O."""

from accounting_agent.books.balances import compute_balances
from accounting_agent.books.checks import check_books
from accounting_agent.books.details import check_details
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
    ReferenceChart,
    Voucher,
)
from accounting_agent.books.reconciliation import reconcile
from accounting_agent.books.reference import check_reference
from accounting_agent.books.supplements import (
    BudgetItem,
    ClosingComment,
    FundValue,
    TodoItem,
    check_budget,
    check_comments,
    check_fund,
    check_todo,
)

__all__ = [
    "Account",
    "BankTransaction",
    "Books",
    "BudgetItem",
    "ClosingComment",
    "Finding",
    "FundValue",
    "OpeningBalance",
    "PostingLine",
    "ReferenceChart",
    "Severity",
    "TodoItem",
    "Voucher",
    "check_books",
    "check_budget",
    "check_comments",
    "check_details",
    "check_fund",
    "check_reference",
    "check_todo",
    "compute_balances",
    "contains_personal_number",
    "mask_personal_numbers",
    "reconcile",
]
