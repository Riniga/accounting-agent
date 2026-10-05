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

    ``date`` and ``amount`` point out the bank transaction, with ``row`` (the row in the
    statement file) when several transactions share them. ``account`` is the account to
    post against; the other line is the bank account.
    """

    date: date
    amount: Decimal
    account: str
    row: int | None = None
    documents: tuple[str, ...] = ()
    note: str = ""
    guess: bool = False


def build_voucher(
    books: Books,
    transactions: Sequence[BankTransaction],
    texts: Mapping[int, str],
    bank_account: str,
    request: VoucherRequest,
    documents: frozenset[str] | None = None,
    guessed_posting_marker: str | None = None,
) -> Voucher:
    """Build the voucher that ``request`` asks for; nothing is written.

    ``texts`` maps a statement row to the voucher text composed for it. ``documents`` is
    the set of files in the documents folder, or ``None`` when no folder is configured.

    Raises:
        VoucherRefusedError: if the request cannot give a right voucher.
    """
    note = _note(request, guessed_posting_marker)
    _check_account(books, bank_account, request.account)
    _check_documents(request.documents, documents)
    transaction = _select(books, transactions, texts, bank_account, request)

    amount = abs(transaction.amount)
    if transaction.amount > ZERO:
        lines = (
            PostingLine(bank_account, debit=amount),
            PostingLine(request.account, credit=amount),
        )
    else:
        lines = (
            PostingLine(request.account, debit=amount),
            PostingLine(bank_account, credit=amount),
        )
    return Voucher(
        series=None,
        number=max((v.number for v in books.vouchers), default=0) + 1,
        date=transaction.date,
        text=_masked(texts[transaction.row]),
        lines=lines,
        documents=request.documents,
        note=note,
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
