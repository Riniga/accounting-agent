"""Account balances: opening balance plus the year's postings."""

from collections import defaultdict
from decimal import Decimal

from accounting_agent.books.model import Books


def compute_balances(books: Books) -> dict[str, Decimal]:
    """Balance per account, debit positive and credit negative."""
    balances: defaultdict[str, Decimal] = defaultdict(Decimal)
    for opening in books.opening_balances:
        balances[opening.account] += opening.amount
    for voucher in books.vouchers:
        for line in voucher.lines:
            balances[line.account] += line.debit - line.credit
    return dict(balances)
