"""The books worked out for the reports: postings and movements per account."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from accounting_agent.books import Account, Books, Voucher

ZERO = Decimal(0)
REVENUE_CLASSES = "3"
COST_CLASSES = "45678"


@dataclass(frozen=True)
class Posting:
    """One posting line on an account, with its voucher."""

    voucher: Voucher
    debit: Decimal
    credit: Decimal


class Ledger:
    """Opening balances, postings and movements per account (debit positive)."""

    def __init__(self, books: Books, fiscal_year: int) -> None:
        self.books = books
        self.accounts: dict[str, Account] = {}
        for account in books.accounts:
            self.accounts.setdefault(account.number, account)
        self.opening: defaultdict[str, Decimal] = defaultdict(Decimal)
        for opening in books.opening_balances:
            self.opening[opening.account] += opening.amount
        self.postings: defaultdict[str, list[Posting]] = defaultdict(list)
        self.movement: defaultdict[str, Decimal] = defaultdict(Decimal)
        for voucher in books.vouchers:
            for line in voucher.lines:
                self.postings[line.account].append(
                    Posting(voucher, line.debit, line.credit)
                )
                self.movement[line.account] += line.debit - line.credit
        self.period_end = max(
            (v.date for v in books.vouchers), default=date(fiscal_year, 1, 1)
        )

    def name(self, account: str) -> str:
        """The account's local name, or ``?`` if it is not in the chart."""
        return self.accounts[account].name if account in self.accounts else "?"

    def closing(self, account: str) -> Decimal:
        """Opening balance plus the year's movement."""
        return self.opening.get(account, ZERO) + self.movement.get(account, ZERO)

    def result_accounts(self, classes: str) -> list[str]:
        """Chart accounts of the given classes that have postings."""
        return sorted(
            number
            for number in self.accounts
            if number[:1] and number[0] in classes and number in self.postings
        )

    def balance_accounts(self, classes: str) -> list[str]:
        """Chart accounts of the given classes with an opening balance or postings."""
        return sorted(
            number
            for number in self.accounts
            if number[:1]
            and number[0] in classes
            and (number in self.opening or number in self.postings)
        )

    def used_accounts(self) -> list[str]:
        """Chart accounts with an opening balance or postings."""
        return sorted(
            n for n in self.accounts if n in self.opening or n in self.postings
        )

    @property
    def revenue(self) -> Decimal:
        """Revenue so far, positive."""
        return -self._sum_movement(REVENUE_CLASSES)

    @property
    def costs(self) -> Decimal:
        """Costs and financial items so far, positive."""
        return self._sum_movement(COST_CLASSES)

    @property
    def result(self) -> Decimal:
        """Revenue minus costs."""
        return self.revenue - self.costs

    def _sum_movement(self, classes: str) -> Decimal:
        return sum(
            (
                self.movement.get(number, ZERO)
                for number in self.accounts
                if number[:1] and number[0] in classes
            ),
            ZERO,
        )

    def group_heading(self, account: str) -> str:
        """The account's group, or ``Kontogrupp NN`` for a chart without groups."""
        group = self.accounts[account].group if account in self.accounts else None
        return group.capitalize() if group else f"Kontogrupp {account[:2]}"

    def groups(self, accounts: list[str]) -> list[tuple[str, list[str]]]:
        """Consecutive accounts with the same group heading, in account order."""
        result: list[tuple[str, list[str]]] = []
        for account in sorted(accounts):
            heading = self.group_heading(account)
            if result and result[-1][0] == heading:
                result[-1][1].append(account)
            else:
                result.append((heading, [account]))
        return result
