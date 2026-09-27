"""The supplementary files and their checks (ADR-007): fund value, budget, closing
comments and to-do list, as Helsingborgs Judoklubb's `kontroll.py` checks them.

The allowed values are the core's own format (owner decision 2026-09-26). No message
quotes a budget item's name, a comment or a task; allowed values are listed, the value
found is not.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from accounting_agent.books.balances import compute_balances
from accounting_agent.books.findings import Finding, Severity
from accounting_agent.books.masking import contains_personal_number
from accounting_agent.books.model import Books

ZERO = Decimal(0)
REVENUE = "intäkt"
COST = "kostnad"
BUDGET_KINDS = (REVENUE, COST)
COMMENT_KINDS = frozenset(
    {"princip", "händelse", "not", "avstämning", "rättelse", "revisor"}
)
TODO_OWNERS = frozenset({"kassör", "vi"})
TODO_WHEN = frozenset({"nu", "bokslut"})
TODO_STATUSES = frozenset({"öppen", "väntar", "klar"})
WAITING = "väntar"
DONE = "klar"


@dataclass(frozen=True)
class FundValue:
    """A fund holding's market value on a date."""

    date: date
    value: Decimal


@dataclass(frozen=True)
class BudgetItem:
    """A budgeted revenue or cost item with its accounts; ``amount`` None if invalid."""

    kind: str
    name: str
    accounts: tuple[str, ...]
    amount: Decimal | None
    note: str
    row: int


@dataclass(frozen=True)
class ClosingComment:
    """A comment collected for the annual accounts; ``date`` None if invalid."""

    id: str
    date: date | None
    kind: str
    accounts: tuple[str, ...]
    vouchers: tuple[str, ...]
    text: str
    row: int


@dataclass(frozen=True)
class TodoItem:
    """A task on the to-do list, for the treasurer (``kassör``) or the tools (``vi``)."""

    id: str
    owner: str
    when: str
    area: str
    task: str
    done_when: str
    status: str
    depends_on: str
    row: int


def check_fund(
    values: Sequence[FundValue], books: Books, fund_account: str
) -> list[Finding]:
    """Compare the latest market value with the booked balance of the fund account."""
    if not values:
        return []
    latest = max(values, key=lambda v: v.date)
    booked = compute_balances(books).get(fund_account, ZERO)
    return [
        Finding(
            Severity.INFO,
            "fund-value",
            f"account {fund_account}",
            f"market value {latest.value} ({latest.date}), booked {booked}, "
            f"difference {latest.value - booked} (change in value not booked)",
        )
    ]


def check_budget(items: Sequence[BudgetItem], books: Books) -> list[Finding]:
    """Budget items must use known accounts of the right class, once each."""
    known = {account.number for account in books.accounts}
    findings: list[Finding] = []
    used: dict[str, int] = {}
    revenue = costs = ZERO
    for item in items:
        location = f"budget row {item.row}"
        if item.kind not in BUDGET_KINDS:
            findings.append(
                _error(
                    "budget-type",
                    location,
                    f"unknown type; must be {REVENUE} or {COST}",
                )
            )
        if item.amount is not None:
            # As kontroll.py: an item of unknown type counts as a cost.
            if item.kind == REVENUE:
                revenue += item.amount
            else:
                costs += item.amount
        for account in item.accounts:
            finding = _check_budget_account(account, item, known, used, location)
            if finding is not None:
                findings.append(finding)
            used[account] = item.row
    findings.append(
        Finding(
            Severity.INFO,
            "budget-summary",
            "budget",
            f"budgeted revenue {revenue}, costs {costs}, result {revenue - costs}",
        )
    )
    return findings


def _check_budget_account(
    account: str, item: BudgetItem, known: set[str], used: dict[str, int], location: str
) -> Finding | None:
    if account not in known:
        return _error(
            "budget-unknown-account",
            location,
            f"account {account} is not in the chart of accounts",
        )
    if account in used:
        return _error(
            "budget-account-twice",
            location,
            f"account {account} is already on budget row {used[account]}",
        )
    if account.startswith("3") != (item.kind == REVENUE):
        return _error(
            "budget-account-type",
            location,
            f"account {account} does not fit the type {item.kind}",
        )
    return None


def check_comments(comments: Sequence[ClosingComment], books: Books) -> list[Finding]:
    """Closing comments: ids 1..N, known type, and accounts and vouchers that exist."""
    known_accounts = {account.number for account in books.accounts}
    known_vouchers = {voucher.id for voucher in books.vouchers}
    findings: list[Finding] = []
    previous = 0
    for comment in comments:
        location = f"closing comment {comment.id}"
        if comment.id != str(previous + 1):
            findings.append(
                _error(
                    "comment-id",
                    location,
                    f"id should be {previous + 1} (a sequence without gaps)",
                )
            )
        previous = int(comment.id) if comment.id.isdigit() else previous + 1
        if comment.kind not in COMMENT_KINDS:
            findings.append(
                _error(
                    "comment-type",
                    location,
                    f"unknown type; allowed: {', '.join(sorted(COMMENT_KINDS))}",
                )
            )
        findings += [
            _error(
                "comment-unknown-account",
                location,
                f"account {account} is not in the chart of accounts",
            )
            for account in comment.accounts
            if account not in known_accounts
        ]
        findings += [
            _error("comment-unknown-voucher", location, f"voucher {v} does not exist")
            for v in comment.vouchers
            if v not in known_vouchers
        ]
        if not comment.text.strip():
            findings.append(
                _error("comment-missing-text", location, "the comment is empty")
            )
        if contains_personal_number(comment.text):
            findings.append(
                Finding(
                    Severity.WARNING,
                    "personal-number",
                    location,
                    "the comment appears to contain a personal identity number",
                )
            )
    findings.append(
        Finding(
            Severity.INFO,
            "comments-summary",
            "closing comments",
            f"{len(comments)} closing comments",
        )
    )
    return findings


def check_todo(items: Sequence[TodoItem]) -> list[Finding]:
    """The to-do list: unique ids, allowed values, known dependencies, filled-in text."""
    ids = [item.id for item in items]
    findings: list[Finding] = []
    for item in items:
        findings += _check_task(item, ids)
    open_items = [item for item in items if item.status != DONE]
    per_owner = ", ".join(
        f"{owner} {sum(1 for item in open_items if item.owner == owner)}"
        for owner in sorted(TODO_OWNERS)
    )
    findings.append(
        Finding(
            Severity.INFO,
            "todo-summary",
            "to-do list",
            f"{len(open_items)} of {len(items)} tasks are not done ({per_owner})",
        )
    )
    return findings


def _check_task(item: TodoItem, ids: list[str]) -> list[Finding]:
    location = f"to-do {item.id}"
    findings: list[Finding] = []
    if ids.count(item.id) > 1:
        findings.append(
            _error("todo-duplicate-id", location, "id appears more than once")
        )
    for rule, value, allowed, what in (
        ("todo-owner", item.owner, TODO_OWNERS, "owner"),
        ("todo-when", item.when, TODO_WHEN, "value for när"),
        ("todo-status", item.status, TODO_STATUSES, "status"),
    ):
        if value not in allowed:
            findings.append(
                _error(
                    rule,
                    location,
                    f"unknown {what}; allowed: {', '.join(sorted(allowed))}",
                )
            )
    if item.depends_on and item.depends_on not in ids:
        findings.append(
            _error(
                "todo-dependency",
                location,
                f"depends on {item.depends_on}, which does not exist",
            )
        )
    if not item.task.strip() or not item.done_when.strip():
        findings.append(
            _error(
                "todo-missing-text", location, "uppgift and klart_när must be filled in"
            )
        )
    if item.status == WAITING and not item.depends_on:
        findings.append(
            Finding(
                Severity.WARNING,
                "todo-waiting",
                location,
                f"status {WAITING} but no dependency",
            )
        )
    return findings


def _error(rule: str, location: str, message: str) -> Finding:
    return Finding(Severity.ERROR, rule, location, message)
