"""Reconciliation of the books against the bank statement (MVP-003).

The rules follow Helsingborgs Judoklubb's `kontroll.py`: the bank's own balance
arithmetic, the opening balance against the bank, and every bank voucher matched with a
bank transaction and the reverse, on (date, amount). A voucher's bank amount is the net of
its lines on the bank account, debit positive, which is what the bank shows. Messages give
dates, amounts, statement rows and voucher numbers only.
"""

from collections import Counter, defaultdict
from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from accounting_agent.books.findings import Finding, Severity
from accounting_agent.books.model import BankTransaction, Books, Voucher

ZERO = Decimal(0)
STATEMENT = "bank statement"

Key = tuple[date, Decimal]


def reconcile(
    books: Books,
    transactions: Sequence[BankTransaction],
    bank_account: str,
    list_unbooked: bool = False,
) -> list[Finding]:
    """Reconcile ``books`` against the bank ``transactions``; the summary comes last."""
    if not transactions:
        return []
    findings, opening = _check_balances(transactions)
    findings += _check_opening_balance(books, bank_account, opening, transactions)
    findings += _match(books.vouchers, transactions, bank_account, list_unbooked)
    findings.append(_summary(transactions))
    return findings


def _check_balances(
    transactions: Sequence[BankTransaction],
) -> tuple[list[Finding], Decimal | None]:
    """Every end-of-day balance implies the same balance before the first transaction."""
    per_day: dict[date, list[BankTransaction]] = defaultdict(list)
    for transaction in transactions:
        per_day[transaction.date].append(transaction)

    findings: list[Finding] = []
    movements = ZERO
    implied: Decimal | None = None
    first_implied: Decimal | None = None
    for day in sorted(per_day):
        movements += sum((t.amount for t in per_day[day]), ZERO)
        balances = [t.balance for t in per_day[day] if t.balance is not None]
        if not balances:
            continue
        day_end = balances[-1]
        if implied is not None and day_end - movements != implied:
            findings.append(
                Finding(
                    Severity.ERROR,
                    "bank-balance",
                    f"{STATEMENT} {day}",
                    f"balance {day_end} does not follow from the earlier balance and "
                    f"movements (expected {implied + movements})",
                )
            )
        implied = day_end - movements
        if first_implied is None:
            first_implied = implied
    return findings, first_implied


def _check_opening_balance(
    books: Books,
    bank_account: str,
    bank_opening: Decimal | None,
    transactions: Sequence[BankTransaction],
) -> list[Finding]:
    booked = [o.amount for o in books.opening_balances if o.account == bank_account]
    if bank_opening is None or not booked or booked[0] == bank_opening:
        return []
    first_day = min(t.date for t in transactions)
    return [
        Finding(
            Severity.ERROR,
            "bank-opening-balance",
            f"opening balance {bank_account}",
            f"opening balance is {booked[0]} but the bank's balance before {first_day} "
            f"was {bank_opening} (difference {booked[0] - bank_opening})",
        )
    ]


def _bank_amount(voucher: Voucher, bank_account: str) -> Decimal | None:
    lines = [line for line in voucher.lines if line.account == bank_account]
    if not lines:
        return None
    return sum((line.debit - line.credit for line in lines), ZERO)


def _match(
    vouchers: Sequence[Voucher],
    transactions: Sequence[BankTransaction],
    bank_account: str,
    list_unbooked: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    booked: dict[Key, list[str]] = defaultdict(list)
    for voucher in vouchers:
        amount = _bank_amount(voucher, bank_account)
        if amount is not None:
            booked[(voucher.date, amount)].append(voucher.id)
    in_books = Counter({key: len(ids) for key, ids in booked.items()})
    in_bank = Counter((t.date, t.amount) for t in transactions)

    for (day, amount), count in sorted((in_books - in_bank).items()):
        findings.append(
            Finding(
                Severity.ERROR,
                "bank-missing-transaction",
                f"voucher {', '.join(booked[(day, amount)][-count:])}",
                f"{day}, {amount} is in the books but not in the bank statement",
            )
        )

    # As kontroll.py: the first rows of each (date, amount) are the unbooked ones.
    left = in_bank - in_books
    unbooked: list[BankTransaction] = []
    for transaction in transactions:
        key = (transaction.date, transaction.amount)
        if left[key] > 0:
            left[key] -= 1
            unbooked.append(transaction)

    last_voucher = max((v.date for v in vouchers), default=date.min)
    for transaction in (t for t in unbooked if t.date <= last_voucher):
        findings.append(
            Finding(
                Severity.ERROR,
                "bank-unbooked",
                f"{STATEMENT} row {transaction.row}",
                f"{transaction.date}, {transaction.amount} has no voucher, although "
                f"later transactions are booked",
            )
        )
    recent = [t for t in unbooked if t.date > last_voucher]
    if recent:
        net = sum((t.amount for t in recent), ZERO)
        findings.append(
            Finding(
                Severity.WARNING,
                "bank-unbooked-recent",
                STATEMENT,
                f"{len(recent)} unbooked transactions after {last_voucher} "
                f"({recent[0].date} to {recent[-1].date}, net {net})",
            )
        )
        if list_unbooked:
            findings += [
                Finding(
                    Severity.INFO,
                    "unbooked",
                    f"{STATEMENT} row {t.row}",
                    f"{t.date}, {t.amount}",
                )
                for t in recent
            ]
    return findings


def _summary(transactions: Sequence[BankTransaction]) -> Finding:
    days = [t.date for t in transactions]
    with_balance = [t for t in transactions if t.balance is not None]
    latest = ""
    if with_balance:
        # The last balance of the latest day that has one, as kontroll.py reports it.
        last_day = max(t.date for t in with_balance)
        last = [t for t in with_balance if t.date == last_day][-1]
        latest = f", the bank's latest balance {last.balance} ({last.date})"
    return Finding(
        Severity.INFO,
        "bank-summary",
        STATEMENT,
        f"{len(transactions)} transactions {min(days)} to {max(days)}{latest}",
    )
