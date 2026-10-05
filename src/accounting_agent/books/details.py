"""Detail checks from the first organisation's `kontroll.py` that go beyond the general
checks (MVP-003): duplicates, date order, revenue and cost accounts on the unexpected
side, supporting documents, parking accounts, unused accounts and the chart's own rules.

No message quotes a voucher's text, an account's name or a document's file name — any of
them can hold a person's name.
"""

from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import date
from decimal import Decimal

from accounting_agent.books.findings import Finding, Severity
from accounting_agent.books.model import Account, Books, Voucher

ZERO = Decimal(0)
# BAS: class 3 is revenue; classes 4–8 are costs and financial items.
REVENUE_CLASSES = ("3",)
COST_CLASSES = ("4", "5", "6", "7", "8")
# kontroll.py counts a voucher without documents as a cost when it debits classes 4–7.
DOCUMENT_COST_CLASSES = ("4", "5", "6", "7")


def check_details(
    books: Books,
    bank_account: str,
    parking_accounts: Sequence[str] = (),
    documents: frozenset[str] | None = None,
) -> list[Finding]:
    """Run the detail checks.

    ``documents`` is the set of file paths, relative to the documents folder, that exist;
    ``None`` means no documents folder is configured, and existence is not checked.
    """
    findings = _check_chart(books.accounts)
    findings += _check_date_order(books.vouchers)
    for voucher in books.vouchers:
        findings += _check_account_sides(voucher)
        if documents is not None:
            findings += _check_documents(voucher, documents)
    findings += _check_duplicates(books.vouchers, bank_account)
    findings += _summarise_documents(books.vouchers)
    for account in parking_accounts:
        findings += _summarise_parking(books.vouchers, account)
    findings += _summarise_unused(books)
    return findings


def _check_chart(accounts: Sequence[Account]) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    for account in accounts:
        location = f"account {account.number}"
        if not account.name.strip():
            findings.append(
                Finding(Severity.ERROR, "account-missing-name", location, "has no name")
            )
        if account.number in seen:
            findings.append(
                Finding(
                    Severity.WARNING,
                    "account-duplicate",
                    location,
                    "appears more than once in the chart of accounts",
                )
            )
        seen.add(account.number)
    return findings


def _check_date_order(vouchers: Iterable[Voucher]) -> list[Finding]:
    findings: list[Finding] = []
    previous: date | None = None
    for voucher in vouchers:
        if previous is not None and voucher.date < previous:
            findings.append(
                Finding(
                    Severity.WARNING,
                    "voucher-date-order",
                    f"voucher {voucher.id}",
                    f"date {voucher.date} is earlier than the previous voucher "
                    f"({previous})",
                )
            )
        previous = voucher.date
    return findings


def _check_account_sides(voucher: Voucher) -> list[Finding]:
    findings: list[Finding] = []
    location = f"voucher {voucher.id}"
    for line in voucher.lines:
        if line.debit > ZERO and line.account.startswith(REVENUE_CLASSES):
            findings.append(
                Finding(
                    Severity.WARNING,
                    "revenue-account-debited",
                    location,
                    f"revenue account {line.account} is debited ({line.debit}); "
                    f"is that right?",
                )
            )
        if line.credit > ZERO and line.account.startswith(COST_CLASSES):
            findings.append(
                Finding(
                    Severity.WARNING,
                    "cost-account-credited",
                    location,
                    f"cost account {line.account} is credited ({line.credit}); "
                    f"is that right?",
                )
            )
    return findings


def _check_documents(voucher: Voucher, documents: frozenset[str]) -> list[Finding]:
    total = len(voucher.documents)
    return [
        Finding(
            Severity.ERROR,
            "document-missing",
            f"voucher {voucher.id}",
            f"supporting document {position} of {total} is not in the documents folder",
        )
        for position, name in enumerate(voucher.documents, start=1)
        if name not in documents
    ]


def _signed_amount(voucher: Voucher, bank_account: str) -> Decimal:
    """The amount as the bank shows it: the bank net, or the total when no bank line."""
    bank = [line for line in voucher.lines if line.account == bank_account]
    if bank:
        return sum((line.debit - line.credit for line in bank), ZERO)
    return voucher.total_debit


def _check_duplicates(vouchers: Iterable[Voucher], bank_account: str) -> list[Finding]:
    groups: defaultdict[tuple[date, Decimal, str], list[str]] = defaultdict(list)
    for voucher in vouchers:
        key = (voucher.date, _signed_amount(voucher, bank_account), voucher.text)
        groups[key].append(voucher.id)
    return [
        Finding(
            Severity.WARNING,
            "voucher-duplicate",
            f"voucher {', '.join(ids)}",
            f"same date, amount and text ({day}, {amount})",
        )
        for (day, amount, _), ids in groups.items()
        if len(ids) > 1
    ]


def _summarise_documents(vouchers: Sequence[Voucher]) -> list[Finding]:
    without = [v for v in vouchers if not v.documents]
    if not without:
        return []
    costs = sum(
        1
        for v in without
        if any(
            line.debit > ZERO and line.account.startswith(DOCUMENT_COST_CLASSES)
            for line in v.lines
        )
    )
    return [
        Finding(
            Severity.INFO,
            "documents-summary",
            "vouchers",
            f"{len(without)} of {len(vouchers)} vouchers have no supporting document "
            f"(of which {costs} costs)",
        )
    ]


def _summarise_parking(vouchers: Iterable[Voucher], account: str) -> list[Finding]:
    postings = 0
    net = ZERO
    for voucher in vouchers:
        lines = [line for line in voucher.lines if line.account == account]
        if lines:
            postings += 1
            net += sum((line.credit - line.debit for line in lines), ZERO)
    if not postings:
        return []
    return [
        Finding(
            Severity.INFO,
            "parking-summary",
            f"account {account}",
            f"{postings} postings, net {net} to distribute (should be 0 at closing)",
        )
    ]


def _summarise_unused(books: Books) -> list[Finding]:
    used = {o.account for o in books.opening_balances}
    used |= {line.account for v in books.vouchers for line in v.lines}
    unused = sorted({a.number for a in books.accounts} - used)
    if not unused:
        return []
    return [
        Finding(
            Severity.INFO,
            "unused-accounts",
            "chart of accounts",
            f"unused accounts: {', '.join(unused)}",
        )
    ]
