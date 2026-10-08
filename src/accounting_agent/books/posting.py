"""Building a new voucher from a bank transaction (ADR-009).

The caller supplies decisions only: which bank transaction, the account to post it
against, the supporting documents, a note and whether the posting is a guess. The date,
the amount, the text and the number come from the books and the bank statement. A request
that cannot give a right voucher is refused; a refusal names dates, amounts, statement
rows and account numbers only — never a text, a name or a document's file name.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from accounting_agent.books.masking import FILE_MASK, mask_personal_numbers
from accounting_agent.books.model import (
    ZERO,
    BankTransaction,
    Books,
    PostingLine,
    Voucher,
)

# The organisation's voucher field separates documents with a semicolon.
DOCUMENT_SEPARATOR = ";"


class VoucherRefusedError(Exception):
    """The request cannot give a right voucher; ``rule`` says which rule refused it."""

    def __init__(self, rule: str, message: str) -> None:
        super().__init__(message)
        self.rule = rule


@dataclass(frozen=True)
class VoucherRequest:
    """The caller's decisions for one new voucher.

    With an ``amount`` the voucher is for a bank transaction: ``date`` and ``amount``
    point it out, with ``row`` (the row in the statement file) when several transactions
    share them. The other side is either ``account`` alone, or ``lines`` that add up to
    the bank amount; the bank line is never the caller's.

    Without an ``amount`` the voucher has no bank transaction (MVP-005): ``date``,
    ``text`` and every line in ``lines`` are the caller's.
    """

    date: date
    amount: Decimal | None = None
    account: str | None = None
    row: int | None = None
    documents: tuple[str, ...] = ()
    note: str = ""
    guess: bool = False
    lines: tuple[PostingLine, ...] = ()
    text: str = ""


def build_voucher(
    books: Books,
    transactions: Sequence[BankTransaction],
    texts: Mapping[int, str],
    bank_account: str,
    request: VoucherRequest,
    documents: frozenset[str] | None = None,
    guessed_posting_marker: str | None = None,
    fiscal_year: int | None = None,
) -> Voucher:
    """Build the voucher that ``request`` asks for; nothing is written.

    ``texts`` maps a statement row to the voucher text composed for it. ``documents`` is
    the set of files in the documents folder, or ``None`` when no folder is configured.
    ``fiscal_year`` bounds the date of a voucher without a bank transaction.

    Raises:
        VoucherRefusedError: if the request cannot give a right voucher.
    """
    note = _note(request, guessed_posting_marker)
    if request.amount is None:
        day, text, lines = _without_transaction(
            books, bank_account, request, documents, fiscal_year
        )
    else:
        _check_counter_side(books, bank_account, request)
        _check_documents(request.documents, documents)
        transaction = _select(books, transactions, texts, bank_account, request)
        day, text = transaction.date, _masked(texts[transaction.row])
        lines = _with_bank_line(request, transaction, bank_account)
    return Voucher(
        series=None,
        number=max((v.number for v in books.vouchers), default=0) + 1,
        date=day,
        text=text,
        # The debit lines first, then the credit lines, as the voucher is written and
        # read back; each side keeps the caller's order.
        lines=tuple(sorted(lines, key=lambda line: line.debit <= ZERO)),
        documents=request.documents,
        note=note,
    )


def _check_counter_side(
    books: Books, bank_account: str, request: VoucherRequest
) -> None:
    """The other side of a bank transaction: one account, or lines — not both."""
    if request.text.strip():
        raise VoucherRefusedError(
            "text-with-transaction",
            "the text of a bank transaction comes from the bank statement; leave it out",
        )
    if request.account is not None and request.lines:
        raise VoucherRefusedError(
            "account-and-lines", "give either one account or lines, not both"
        )
    if request.account is not None:
        _check_account(books, bank_account, request.account)
    elif request.lines:
        _check_lines(books, request.lines, bank_account, "account-is-bank")
    else:
        raise VoucherRefusedError(
            "account-missing", "give the account, or the lines, to post against"
        )


def _with_bank_line(
    request: VoucherRequest, transaction: BankTransaction, bank_account: str
) -> tuple[PostingLine, ...]:
    """The caller's side with the bank line from the transaction: first for money in,
    last for money out."""
    amount = abs(transaction.amount)
    money_in = transaction.amount > ZERO
    if request.account is not None:
        counter: tuple[PostingLine, ...] = (
            PostingLine(request.account, credit=amount)
            if money_in
            else PostingLine(request.account, debit=amount),
        )
    else:
        counter = request.lines
        net = sum((line.debit - line.credit for line in counter), ZERO)
        if net != -transaction.amount:
            raise VoucherRefusedError(
                "lines-unbalanced",
                f"the lines add up to {-net} on the bank account, but the bank "
                f"transaction is {transaction.amount}",
            )
    if money_in:
        return (PostingLine(bank_account, debit=amount), *counter)
    return (*counter, PostingLine(bank_account, credit=amount))


def _without_transaction(
    books: Books,
    bank_account: str,
    request: VoucherRequest,
    documents: frozenset[str] | None,
    fiscal_year: int | None,
) -> tuple[date, str, tuple[PostingLine, ...]]:
    """The date, text and lines of a voucher that has no bank transaction."""
    if request.account is not None or request.row is not None:
        raise VoucherRefusedError(
            "amount-missing",
            "an account or a statement row belongs to a bank transaction; give its "
            "amount too",
        )
    text = _masked(request.text.strip())
    if not text:
        raise VoucherRefusedError(
            "text-missing", "a voucher without a bank transaction needs a text"
        )
    lines = request.lines
    if len(lines) < 2:  # a debit and a credit
        raise VoucherRefusedError(
            "lines-missing", "a voucher needs at least one debit and one credit line"
        )
    # A voucher on the bank account always comes from a bank transaction; otherwise
    # the bank's balance could change without the bank agreeing.
    _check_lines(books, lines, bank_account, "bank-without-transaction")
    debits = sum((line.debit for line in lines), ZERO)
    credits = sum((line.credit for line in lines), ZERO)
    if debits != credits:
        raise VoucherRefusedError(
            "lines-unbalanced", f"debit {debits} differs from credit {credits}"
        )
    if fiscal_year is not None and request.date.year != fiscal_year:
        raise VoucherRefusedError(
            "date-outside-year",
            f"the date {request.date} is outside the fiscal year {fiscal_year}",
        )
    _check_documents(request.documents, documents)

    # Nothing outside the books stops the same voucher from being created twice.
    def key(posting: Sequence[PostingLine]) -> list[tuple[str, Decimal, Decimal]]:
        return sorted((line.account, line.debit, line.credit) for line in posting)

    for voucher in books.vouchers:
        if (voucher.date, voucher.text) == (request.date, text) and key(
            voucher.lines
        ) == key(lines):
            raise VoucherRefusedError(
                "duplicate",
                f"voucher {voucher.id} has the same date, text and lines",
            )
    return request.date, text, lines


def _check_lines(
    books: Books,
    lines: Sequence[PostingLine],
    bank_account: str,
    bank_rule: str,
) -> None:
    """Every line is on a known account that is not the bank account, with an amount."""
    known = {account.number for account in books.accounts}
    for line in lines:
        if line.account not in known:
            raise VoucherRefusedError(
                "account-unknown",
                f"account {line.account} is not in the chart of accounts",
            )
        if line.account == bank_account:
            raise VoucherRefusedError(
                bank_rule,
                f"account {line.account} is the bank account; its line comes from a "
                f"bank transaction, never from the caller",
            )
        if line.debit == line.credit:
            raise VoucherRefusedError(
                "line-amount", f"the line on account {line.account} has no amount"
            )
    debited = {line.account for line in lines if line.debit > ZERO}
    credited = {line.account for line in lines if line.credit > ZERO}
    both = sorted(debited & credited)
    if both:
        raise VoucherRefusedError(
            "account-on-both-sides",
            f"account {both[0]} is both debited and credited",
        )


def _masked(text: str) -> str:
    return mask_personal_numbers(text, FILE_MASK)


def _note(request: VoucherRequest, marker: str | None) -> str:
    note = _masked(request.note.strip())
    if not request.guess:
        return note
    if marker is None:
        raise VoucherRefusedError(
            "guess-marker-missing",
            "a guess needs 'conventions.guessed_posting_marker' in organisation.yaml",
        )
    if not note:
        raise VoucherRefusedError(
            "guess-without-reason", "a guess needs a note that says why it is a guess"
        )
    return f"{marker}: {note}"


def _check_account(books: Books, bank_account: str, account: str) -> None:
    if account not in {a.number for a in books.accounts}:
        raise VoucherRefusedError(
            "account-unknown", f"account {account} is not in the chart of accounts"
        )
    if account == bank_account:
        raise VoucherRefusedError(
            "account-is-bank",
            f"account {account} is the bank account; give the account to post against",
        )


def _check_documents(
    requested: tuple[str, ...], existing: frozenset[str] | None
) -> None:
    if not requested:
        return
    if existing is None:
        raise VoucherRefusedError(
            "documents-not-configured",
            "a supporting document needs 'checks.documents' in organisation.yaml",
        )
    total = len(requested)
    for position, name in enumerate(requested, start=1):
        # Messages give the position, never the name: it can hold a person's name.
        where = f"supporting document {position} of {total}"
        if name in requested[: position - 1]:
            raise VoucherRefusedError("document-twice", f"{where} is given twice")
        if DOCUMENT_SEPARATOR in name:
            raise VoucherRefusedError(
                "document-name",
                f"{where} has '{DOCUMENT_SEPARATOR}' in its name, which separates "
                f"documents in a voucher",
            )
        # Only names the folder listing holds are accepted, so no path leads outside it.
        if name not in existing:
            raise VoucherRefusedError(
                "document-missing", f"{where} is not in the documents folder"
            )


def _bank_amount(voucher: Voucher, bank_account: str) -> Decimal | None:
    """The voucher's net on the bank account, debit positive, as the bank shows it."""
    lines = [line for line in voucher.lines if line.account == bank_account]
    if not lines:
        return None
    return sum((line.debit - line.credit for line in lines), ZERO)


def _select(
    books: Books,
    transactions: Sequence[BankTransaction],
    texts: Mapping[int, str],
    bank_account: str,
    request: VoucherRequest,
) -> BankTransaction:
    """The bank transaction the request points out, if it has no voucher yet."""
    what = f"on {request.date} with the amount {request.amount}"
    matching = [
        t for t in transactions if (t.date, t.amount) == (request.date, request.amount)
    ]
    if not matching:
        raise VoucherRefusedError(
            "transaction-missing", f"the bank statement has no transaction {what}"
        )
    booked = [
        v
        for v in books.vouchers
        if (v.date, _bank_amount(v, bank_account)) == (request.date, request.amount)
    ]
    already = VoucherRefusedError(
        "already-booked", f"the bank transaction {what} already has a voucher"
    )
    if len(booked) >= len(matching):
        raise already

    if request.row is None:
        if len(matching) > 1:
            rows = ", ".join(str(t.row) for t in matching)
            raise VoucherRefusedError(
                "transaction-ambiguous",
                f"{len(matching)} bank transactions are {what}; give the statement "
                f"row ({rows})",
            )
        chosen = matching[0]
    else:
        by_row = {t.row: t for t in matching}
        if request.row not in by_row:
            raise VoucherRefusedError(
                "row-mismatch",
                f"statement row {request.row} is not a transaction {what}",
            )
        chosen = by_row[request.row]

    # Among equal transactions, the text tells which ones are booked: a row is booked
    # when as many vouchers as rows have its date, amount and text.
    text = _masked(texts[chosen.row])
    rows_with_text = sum(1 for t in matching if _masked(texts[t.row]) == text)
    vouchers_with_text = sum(1 for v in booked if v.text == text)
    if vouchers_with_text >= rows_with_text:
        raise already
    return chosen
