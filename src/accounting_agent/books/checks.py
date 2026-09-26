"""General checks on the book model — valid for every file format (ADR-006).

Severities follow the organisations' own tooling: broken books are errors; a personal
identity number in a voucher text is a warning. No message quotes a voucher's text.
"""

import re
from collections.abc import Iterable
from decimal import Decimal

from accounting_agent.books.findings import Finding, Severity
from accounting_agent.books.masking import contains_personal_number
from accounting_agent.books.model import Account, Books, OpeningBalance, Voucher

ACCOUNT_NUMBER = re.compile(r"\d{4}")
# BAS: classes 1 (assets) and 2 (equity and liabilities) carry balances between years.
BALANCE_ACCOUNT_CLASSES = ("1", "2")
ZERO = Decimal(0)


def check_books(books: Books, fiscal_year: int) -> list[Finding]:
    """Run every general check and return the findings, in the order found."""
    findings, known_accounts = _check_chart(books.accounts)
    findings += _check_opening_balances(books.opening_balances, known_accounts)
    findings += _check_numbering(books.vouchers)
    for voucher in books.vouchers:
        findings += _check_voucher(voucher, known_accounts, fiscal_year)
    return findings


def _check_chart(accounts: Iterable[Account]) -> tuple[list[Finding], set[str]]:
    findings: list[Finding] = []
    known: set[str] = set()
    for account in accounts:
        if ACCOUNT_NUMBER.fullmatch(account.number):
            known.add(account.number)
        else:
            findings.append(
                _error("account-number", f"account {account.number}", "not four digits")
            )
    return findings, known


def _check_opening_balances(
    balances: Iterable[OpeningBalance], known_accounts: set[str]
) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    total = ZERO
    for balance in balances:
        location = f"opening balance {balance.account}"
        total += balance.amount
        if balance.account not in known_accounts:
            findings.append(
                _error(
                    "opening-balance-unknown-account",
                    location,
                    "account is not in the chart of accounts",
                )
            )
        elif not balance.account.startswith(BALANCE_ACCOUNT_CLASSES):
            findings.append(
                _error(
                    "opening-balance-not-balance-account",
                    location,
                    "only balance accounts (classes 1-2) have an opening balance",
                )
            )
        if balance.account in seen:
            findings.append(
                _error("opening-balance-duplicate", location, "appears more than once")
            )
        seen.add(balance.account)
    if total != ZERO:
        findings.append(
            _error(
                "opening-balance-sum", "opening balance", f"sum is {total}, must be 0"
            )
        )
    return findings


def _check_numbering(vouchers: Iterable[Voucher]) -> list[Finding]:
    # In file order, per series — a gap or a duplicate shows as an unexpected number.
    findings: list[Finding] = []
    last_number: dict[str | None, int] = {}
    for voucher in vouchers:
        expected = last_number.get(voucher.series, 0) + 1
        if voucher.number != expected:
            findings.append(
                _error(
                    "voucher-numbering",
                    f"voucher {voucher.id}",
                    f"expected number {expected} (gap or duplicate)",
                )
            )
        last_number[voucher.series] = voucher.number
    return findings


def _check_voucher(
    voucher: Voucher, known_accounts: set[str], fiscal_year: int
) -> list[Finding]:
    location = f"voucher {voucher.id}"
    findings = [
        _error(
            "voucher-unknown-account",
            location,
            f"account {line.account} is not in the chart of accounts",
        )
        for line in voucher.lines
        if line.account not in known_accounts
    ]
    debited = {line.account for line in voucher.lines if line.debit > ZERO}
    credited = {line.account for line in voucher.lines if line.credit > ZERO}
    for account in sorted(debited & credited):
        findings.append(
            _error(
                "voucher-same-account",
                location,
                f"account {account} is both debited and credited",
            )
        )
    if not voucher.is_balanced:
        findings.append(
            _error(
                "voucher-unbalanced",
                location,
                f"debit {voucher.total_debit} differs from credit {voucher.total_credit}",
            )
        )
    if voucher.total_debit == ZERO and voucher.total_credit == ZERO:
        findings.append(_error("voucher-zero-amount", location, "the amount is 0"))
    if not voucher.text.strip():
        findings.append(_error("voucher-missing-text", location, "the text is empty"))
    if voucher.date.year != fiscal_year:
        findings.append(
            _error(
                "voucher-outside-fiscal-year",
                location,
                f"date {voucher.date} is outside the fiscal year {fiscal_year}",
            )
        )
    if contains_personal_number(voucher.text):
        findings.append(
            Finding(
                Severity.WARNING,
                "personal-number",
                location,
                "the text appears to contain a personal identity number",
            )
        )
    return findings


def _error(rule: str, location: str, message: str) -> Finding:
    return Finding(Severity.ERROR, rule, location, message)
