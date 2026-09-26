"""The core book model (ADR-006): general double-entry vouchers with posting lines.

The model holds what an organisation's files say, including mistakes such as duplicates
or unbalanced vouchers; finding those is the checks' job, not the model's.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

ZERO = Decimal(0)


@dataclass(frozen=True)
class Account:
    """An account in the chart of accounts (kontoplan)."""

    number: str
    name: str


@dataclass(frozen=True)
class OpeningBalance:
    """An account's balance at the start of the fiscal year; debit positive."""

    account: str
    amount: Decimal


@dataclass(frozen=True)
class PostingLine:
    """One account with a debit or a credit amount on a voucher (kontering)."""

    account: str
    debit: Decimal = ZERO
    credit: Decimal = ZERO

    def __post_init__(self) -> None:
        for side in (self.debit, self.credit):
            # Floats would make balances inexact; amounts must come in as Decimal.
            if not isinstance(side, Decimal):
                raise TypeError(f"Amounts must be Decimal, got {type(side).__name__}.")
            if side < ZERO:
                raise ValueError("Posting amounts cannot be negative.")
        if self.debit > ZERO and self.credit > ZERO:
            raise ValueError("A posting line has a debit or credit amount, not both.")


@dataclass(frozen=True)
class Voucher:
    """One recorded business event (verifikation) with its posting lines."""

    series: str | None
    number: int
    date: date
    text: str
    lines: tuple[PostingLine, ...]
    documents: tuple[str, ...] = ()
    note: str = ""
    source: str = ""

    @property
    def id(self) -> str:
        """The voucher's identity: series letters followed by the number, e.g. B12."""
        return f"{self.series or ''}{self.number}"

    @property
    def total_debit(self) -> Decimal:
        """Sum of the debit amounts."""
        return sum((line.debit for line in self.lines), ZERO)

    @property
    def total_credit(self) -> Decimal:
        """Sum of the credit amounts."""
        return sum((line.credit for line in self.lines), ZERO)

    @property
    def is_balanced(self) -> bool:
        """True when debits equal credits."""
        return self.total_debit == self.total_credit


@dataclass(frozen=True)
class Books:
    """An organisation's books for one fiscal year."""

    accounts: tuple[Account, ...]
    opening_balances: tuple[OpeningBalance, ...]
    vouchers: tuple[Voucher, ...]


@dataclass(frozen=True)
class BankTransaction:
    """One row of the bank statement (ADR-007).

    Deliberately without the counterparty's name or the message: nothing built on the
    model can then quote them. ``row`` is the row in the statement file, for locating it.
    """

    date: date
    amount: Decimal
    balance: Decimal | None
    row: int
