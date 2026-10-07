"""Reader and voucher writer for the `front-matter` book format (ADR-006, ADR-009).

The format: a chart of accounts and an opening balance as semicolon-separated UTF-8 CSV,
and one Markdown file per voucher whose fields sit between two ``---`` lines. The field
parser deliberately reproduces the semantics of the organisation's own tool (a value
starting with ``"`` is a JSON string; a line is split at its first colon), so that results
stay comparable. Every problem is reported as a finding; no finding ever quotes a
voucher's text.

A voucher is in one of two forms, never mixed (MVP-005): the simple form, with one
``debet`` and one ``kredit`` account and the amount in ``belopp``; or the lines form, with
any number of ``debet`` and ``kredit`` fields, each an account and a positive amount.

Below the fields a voucher may start with generated lines (ADR-009): the accounts with
their names, then a link to each supporting document. They repeat the fields for the
reader's sake, so they are kept out of the note and checked against the fields.
"""

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from accounting_agent.books import (
    Account,
    Books,
    Finding,
    OpeningBalance,
    PostingLine,
    Severity,
    Voucher,
)
from accounting_agent.formats.common import (
    Findings,
    Row,
    parse_amount,
    read_csv,
    read_text,
)

CHART_FILE = "kontoplan.csv"
OPENING_FILE = "ingående-balans.csv"
VOUCHER_DIR = "verifikationer"
CHART_HEADER = [
    "kontoklass",
    "kontogrupp",
    "konto",
    "bas_beskrivning",
    "lokal_benämning",
]
OPENING_HEADER = ["konto", "lokal_benämning", "ingående_balans"]
REQUIRED_FIELDS = ("verifikation", "datum", "text", "belopp", "debet", "kredit")
# The posting fields; in the lines form they are repeated, each with an amount.
LINE_FIELDS = ("debet", "kredit")
OPTIONAL_FIELDS = ("underlag",)
VOUCHER_FILE_NAME = re.compile(r"(\d{4})_(\d{4}-\d{2}-\d{2})\.md")
ACCOUNT_NUMBER = re.compile(r"\d{4}")
# The chart's `kontoklass` column must name the BAS class of the account's first digit.
CLASS_BY_FIRST_DIGIT = {
    "1": "Tillgångar",
    "2": "Eget kapital och skulder",
    "3": "Intäkter",
}
OTHER_CLASS = "Kostnader och resultat"
# The generated lines, in Swedish like the rest of the organisation's files (ADR-009).
GENERATED_ACCOUNTS = re.compile(r"Debet (\d{4}) (.+?) · Kredit (\d{4}) (.+)")
# The lines form has one generated line per posting, with its amount (MVP-005).
GENERATED_POSTING = re.compile(r"(Debet|Kredit) (\d{4}) (.+) (\d+(?:\.\d{1,2})?)")
GENERATED_DOCUMENT = re.compile(r"Underlag: \[(.+)\]\(<(.+)>\)")


class VoucherExistsError(Exception):
    """A file for the voucher's number already exists; it is never replaced (ADR-009)."""


@dataclass(frozen=True)
class _GeneratedPosting:
    """One posting as the generated lines state it.

    ``amount`` is ``None`` on the single line of the simple form, which has none.
    """

    debit: bool
    account: str
    name: str
    amount: Decimal | None


@dataclass(frozen=True)
class _GeneratedLines:
    """What a voucher's generated lines say: the postings, then the document links."""

    postings: tuple[_GeneratedPosting, ...]
    links: tuple[tuple[str, str], ...]


def read_books(path: Path, bank_account: str) -> tuple[Books | None, list[Finding]]:
    """Read an organisation's books in the `front-matter` format.

    Returns ``(None, findings)`` when the books cannot be read at all (a missing file or
    directory, invalid UTF-8, or a wrong header); otherwise the books and every finding.
    """
    findings = Findings()
    chart_rows = read_csv(path / CHART_FILE, CHART_HEADER, findings)
    opening_rows = read_csv(path / OPENING_FILE, OPENING_HEADER, findings)
    account_names = {r["konto"]: r["lokal_benämning"] for r in chart_rows or []}
    vouchers = _read_vouchers(path / VOUCHER_DIR, bank_account, account_names, findings)
    if chart_rows is None or opening_rows is None or vouchers is None:
        return None, findings.items

    books = Books(
        accounts=_accounts(chart_rows, findings),
        opening_balances=_opening_balances(opening_rows, findings),
        vouchers=vouchers,
    )
    return books, findings.items


def _accounts(rows: list[Row], findings: Findings) -> tuple[Account, ...]:
    for row in rows:
        number = row["konto"]
        # Malformed numbers are already errors in check_books().
        if not ACCOUNT_NUMBER.fullmatch(number):
            continue
        expected = CLASS_BY_FIRST_DIGIT.get(number[0], OTHER_CLASS)
        if row["kontoklass"] != expected:
            # The value found is not quoted; only the expected class is.
            findings.add(
                Severity.ERROR,
                "account-class",
                f"{CHART_FILE}:{row['_line']}",
                f"account {number} has the wrong kontoklass; expected '{expected}'",
            )
    return tuple(
        Account(
            r["konto"],
            r["lokal_benämning"],
            group=r["kontogrupp"],
            reference_description=r["bas_beskrivning"],
        )
        for r in rows
    )


def _opening_balances(
    rows: list[Row], findings: Findings
) -> tuple[OpeningBalance, ...]:
    balances: list[OpeningBalance] = []
    for row in rows:
        amount = parse_amount(row["ingående_balans"])
        if amount is None:
            findings.add(
                Severity.ERROR,
                "invalid-amount",
                f"{OPENING_FILE}:{row['_line']}",
                "ingående_balans is not a valid amount (decimal point, no spaces)",
            )
            continue
        balances.append(OpeningBalance(row["konto"], amount))
    return tuple(balances)


def _read_vouchers(
    directory: Path,
    bank_account: str,
    account_names: dict[str, str],
    findings: Findings,
) -> tuple[Voucher, ...] | None:
    if not directory.is_dir():
        findings.add(
            Severity.ERROR,
            "directory-missing",
            f"{directory.name}/",
            "voucher directory is missing",
        )
        return None

    vouchers: list[Voucher] = []
    for path in sorted(directory.iterdir()):
        match = VOUCHER_FILE_NAME.fullmatch(path.name)
        if match is None:
            findings.add(
                Severity.ERROR,
                "file-name",
                path.name,
                "unexpected file; voucher files are named NNNN_YYYY-MM-DD.md",
            )
            continue
        parsed = _read_front_matter(path, findings)
        if parsed is None:
            continue
        fields, postings, body = parsed
        generated, note = _split_generated(body)
        voucher = _to_voucher(
            path.name, match, fields, postings, note, bank_account, findings
        )
        if voucher is not None:
            if generated is not None:
                _check_generated(voucher, generated, account_names, findings)
            vouchers.append(voucher)
    return tuple(vouchers)


def _split_generated(body: str) -> tuple[_GeneratedLines | None, str]:
    """Split a voucher's body into its generated lines and the note.

    Only the top of the body counts: the account lines first — one line for the simple
    form, one per posting for the lines form — then the document lines. A line of the
    same shape further down is the writer's own and stays in the note.
    """
    lines = body.split("\n")
    postings = _generated_postings(lines)
    if not postings:
        return None, body
    # The simple form's two postings share one line.
    used = 1 if postings[0].amount is None else len(postings)
    links: list[tuple[str, str]] = []
    for line in lines[used:]:
        link = GENERATED_DOCUMENT.fullmatch(line.rstrip())
        if link is None:
            break
        links.append((link.group(1), link.group(2)))
    generated = _GeneratedLines(postings=postings, links=tuple(links))
    return generated, "\n".join(lines[used + len(links) :]).strip()


def _generated_postings(lines: list[str]) -> tuple[_GeneratedPosting, ...]:
    single = GENERATED_ACCOUNTS.fullmatch(lines[0].rstrip())
    if single is not None:
        return (
            _GeneratedPosting(True, single.group(1), single.group(2), None),
            _GeneratedPosting(False, single.group(3), single.group(4), None),
        )
    postings: list[_GeneratedPosting] = []
    for line in lines:
        match = GENERATED_POSTING.fullmatch(line.rstrip())
        if match is None:
            break
        postings.append(
            _GeneratedPosting(
                debit=match.group(1) == "Debet",
                account=match.group(2),
                name=match.group(3),
                amount=Decimal(match.group(4)),
            )
        )
    return tuple(postings)


def _check_generated(
    voucher: Voucher,
    generated: _GeneratedLines,
    account_names: dict[str, str],
    findings: Findings,
) -> None:
    """The fields are the single source; generated lines that disagree mislead."""
    # Messages name account numbers only: names and file names can hold a person's name.
    # The simple form's single line has no amounts; then sides and accounts are compared.
    with_amounts = generated.postings[0].amount is not None
    written = [
        (
            line.debit > 0,
            line.account,
            (line.debit or line.credit) if with_amounts else None,
        )
        for line in voucher.lines
    ]
    stated = [(p.debit, p.account, p.amount) for p in generated.postings]
    if written != stated:
        findings.add(
            Severity.ERROR,
            "generated-accounts",
            voucher.source,
            "the generated account lines do not match the fields 'debet' and 'kredit'",
        )
    else:
        # One warning per account, also when it is on several lines.
        names = {p.account: p.name for p in generated.postings}
        for number, name in names.items():
            if account_names.get(number, name) != name:
                findings.add(
                    Severity.WARNING,
                    "generated-account-name",
                    voucher.source,
                    f"the generated line gives account {number} another name than "
                    f"the chart of accounts",
                )
    names = tuple(name for name, _ in generated.links)
    targets_match = all(
        target == name or target.endswith(f"/{name}")
        for name, target in generated.links
    )
    if names != voucher.documents or not targets_match:
        findings.add(
            Severity.ERROR,
            "generated-documents",
            voucher.source,
            "the generated document lines do not match the field 'underlag'",
        )


Postings = list[tuple[str, str]]


def _read_front_matter(
    path: Path, findings: Findings
) -> tuple[dict[str, str], Postings, str] | None:
    """The fields, the posting fields in the order written, and the body below."""
    text = read_text(path, findings)
    if text is None:
        return None
    lines = text.splitlines()
    stripped = [line.strip() for line in lines]
    if not lines or stripped[0] != "---" or "---" not in stripped[1:]:
        findings.add(
            Severity.ERROR,
            "front-matter",
            path.name,
            "missing the fields at the top (must start and end with ---)",
        )
        return None
    end = stripped.index("---", 1)
    fields, postings = _parse_fields(lines[1:end], path.name, findings)

    present = set(fields) | {side for side, _ in postings}
    missing = [key for key in REQUIRED_FIELDS if key not in present]
    if missing:
        findings.add(
            Severity.ERROR,
            "missing-field",
            path.name,
            f"missing field(s): {', '.join(missing)}",
        )
        return None
    fields.setdefault("underlag", "")
    note = "\n".join(lines[end + 1 :]).strip()
    return fields, postings, note


def _parse_fields(
    lines: list[str], name: str, findings: Findings
) -> tuple[dict[str, str], Postings]:
    fields: dict[str, str] = {}
    postings: Postings = []
    for line_number, line in enumerate(lines, start=2):
        if not line.strip():
            continue
        key, colon, value = line.partition(":")
        key, value = key.strip(), value.strip()
        # Messages name the line or the field, never the value: it may be voucher text.
        if not colon or key not in REQUIRED_FIELDS + OPTIONAL_FIELDS:
            findings.add(
                Severity.ERROR,
                "unknown-field",
                name,
                f"line {line_number} is not a known field",
            )
            continue
        if key in LINE_FIELDS:
            # May be repeated: the lines form has one field per posting line.
            postings.append((key, value))
            continue
        if key in fields:
            findings.add(
                Severity.ERROR,
                "duplicate-field",
                name,
                f"field '{key}' appears more than once",
            )
            continue
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except ValueError:
                findings.add(
                    Severity.ERROR,
                    "quoting",
                    name,
                    f"field '{key}' has invalid quotes",
                )
                continue
        fields[key] = value
    return fields, postings


def _to_voucher(
    name: str,
    match: re.Match[str],
    fields: dict[str, str],
    postings: Postings,
    note: str,
    bank_account: str,
    findings: Findings,
) -> Voucher | None:
    file_number, file_date = int(match.group(1)), match.group(2)
    if fields["verifikation"] != str(file_number):
        findings.add(
            Severity.ERROR,
            "number-mismatch",
            name,
            f"file name has number {file_number}, the field 'verifikation' differs",
        )
    if fields["datum"] != file_date:
        findings.add(
            Severity.ERROR,
            "date-mismatch",
            name,
            f"file name has date {file_date}, the field 'datum' differs",
        )
    number = (
        int(fields["verifikation"]) if fields["verifikation"].isdigit() else file_number
    )

    try:
        voucher_date = date.fromisoformat(fields["datum"])
    except ValueError:
        findings.add(
            Severity.ERROR,
            "invalid-date",
            name,
            "datum is not a valid date (YYYY-MM-DD)",
        )
        return None
    amount = parse_amount(fields["belopp"])
    if amount is None:
        findings.add(
            Severity.ERROR,
            "invalid-amount",
            name,
            "belopp is not a valid amount (decimal point, no spaces)",
        )
        return None

    lines = _posting_lines(name, postings, amount, bank_account, findings)
    if lines is None:
        return None
    return Voucher(
        series=None,
        number=number,
        date=voucher_date,
        text=fields["text"],
        lines=lines,
        documents=tuple(d.strip() for d in fields["underlag"].split(";") if d.strip()),
        note=note,
        source=name,
    )


def _posting_lines(
    name: str,
    postings: Postings,
    amount: Decimal,
    bank_account: str,
    findings: Findings,
) -> tuple[PostingLine, ...] | None:
    """The voucher's lines, from the simple form or the lines form (MVP-005)."""
    with_amount = [len(value.split()) > 1 for _, value in postings]
    if len(postings) == len(LINE_FIELDS) and not any(with_amount):
        # The simple form: one account on each side, and the amount in `belopp`.
        accounts = dict(postings)
        debit_account, credit_account = accounts["debet"], accounts["kredit"]
        _check_bank_sign(
            name, amount, debit_account, credit_account, bank_account, findings
        )
        return (
            PostingLine(debit_account, debit=abs(amount)),
            PostingLine(credit_account, credit=abs(amount)),
        )
    if not all(with_amount):
        findings.add(
            Severity.ERROR,
            "lines-mixed",
            name,
            "a voucher with several lines needs an amount on every 'debet' and "
            "'kredit' line",
        )
        return None

    lines: list[PostingLine] = []
    for position, (side, value) in enumerate(postings, start=1):
        parts = value.split()
        line_amount = parse_amount(parts[1]) if len(parts) == 2 else None
        if line_amount is None or line_amount <= 0:
            # The position, not the value: it is what the person wrote.
            findings.add(
                Severity.ERROR,
                "invalid-line",
                name,
                f"posting line {position} is not an account and a positive amount "
                f"(decimal point, no spaces)",
            )
            return None
        if side == "debet":
            lines.append(PostingLine(parts[0], debit=line_amount))
        else:
            lines.append(PostingLine(parts[0], credit=line_amount))

    # `belopp` is what the bank shows: the net on the bank account, or the total.
    bank = [line for line in lines if line.account == bank_account]
    if bank:
        expected = sum((line.debit - line.credit for line in bank), Decimal(0))
    else:
        expected = sum((line.debit for line in lines), Decimal(0))
    if amount != expected:
        findings.add(
            Severity.ERROR,
            "amount-mismatch",
            name,
            f"belopp differs from the posting lines (expected {expected})",
        )
    return tuple(lines)


def _check_bank_sign(
    name: str,
    amount: Decimal,
    debit_account: str,
    credit_account: str,
    bank_account: str,
    findings: Findings,
) -> None:
    # In this format the amount is signed as the bank shows it: + in, - out.
    if debit_account == bank_account and amount < 0:
        message = f"debit {bank_account} (money in) but the amount is negative"
    elif credit_account == bank_account and amount > 0:
        message = f"credit {bank_account} (money out) but the amount is positive"
    elif bank_account not in (debit_account, credit_account) and amount < 0:
        message = f"the amount must be positive when {bank_account} is not involved"
    else:
        return
    findings.add(Severity.ERROR, "bank-sign", name, message)


def voucher_file_name(voucher: Voucher) -> str:
    """The name of the voucher's file: its number and its date.

    Raises:
        ValueError: if the number does not fit the name's four digits.
    """
    # The file name has four digits for the number.
    if not 1 <= voucher.number <= 9999:
        raise ValueError("The format has voucher numbers 1 to 9999.")
    return f"{voucher.number:04d}_{voucher.date.isoformat()}.md"


def render_voucher(
    voucher: Voucher,
    account_names: Mapping[str, str],
    bank_account: str,
    link_path: str | None,
) -> str:
    """Render ``voucher`` as the content of its file: the fields, the generated lines
    (ADR-009), then the note.

    ``link_path`` is the path from the voucher folder to the documents folder, with
    forward slashes; ``None`` when there is none, and the links then hold the name only.

    One debit line followed by one credit line of the same amount is written in the
    simple form; anything else in the lines form, one field and one generated line per
    posting, in the voucher's order (MVP-005).

    Raises:
        ValueError: if the voucher does not fit the format — it needs at least two
            lines with an amount each, debits that balance the credits, and accounts
            that are in the chart.
    """
    postings = voucher.lines
    if (
        len(postings) < len(LINE_FIELDS)
        or any(line.debit == line.credit for line in postings)
        or not voucher.is_balanced
    ):
        raise ValueError(
            "A voucher needs at least two lines with an amount each, and debits that "
            "balance the credits."
        )
    for line in postings:
        if line.account not in account_names:
            raise ValueError(f"Account {line.account} is not in the chart of accounts.")

    amount = voucher_amount(voucher, bank_account)
    if is_simple(voucher):
        debit, credit = postings
        fields = [f"debet: {debit.account}", f"kredit: {credit.account}"]
        generated = [
            f"Debet {debit.account} {account_names[debit.account]} · "
            f"Kredit {credit.account} {account_names[credit.account]}"
        ]
    else:
        fields = [
            f"{'debet' if line.debit else 'kredit'}: {line.account} "
            f"{format_amount(line.debit or line.credit)}"
            for line in postings
        ]
        generated = [
            f"{'Debet' if line.debit else 'Kredit'} {line.account} "
            f"{account_names[line.account]} {format_amount(line.debit or line.credit)}"
            for line in postings
        ]
    lines = [
        "---",
        f"verifikation: {voucher.number}",
        f"datum: {voucher.date.isoformat()}",
        # A JSON string keeps quotes, colons and line breaks on one line.
        f"text: {json.dumps(voucher.text, ensure_ascii=False)}",
        f"belopp: {format_amount(amount)}",
        *fields,
        f"underlag: {'; '.join(voucher.documents)}".rstrip(),
        "---",
        "",
        *generated,
    ]
    for name in voucher.documents:
        target = name if link_path is None else f"{link_path}/{name}"
        # Angle brackets let the target hold spaces and parentheses.
        lines.append(f"Underlag: [{name}](<{target}>)")
    if voucher.note:
        lines += ["", voucher.note]
    return "\n".join(lines) + "\n"


def voucher_amount(voucher: Voucher, bank_account: str) -> Decimal:
    """What `belopp` holds: the net on the bank account as the bank shows it, or the
    voucher's total when the bank account is not among its lines."""
    bank = [line for line in voucher.lines if line.account == bank_account]
    if bank:
        return sum((line.debit - line.credit for line in bank), Decimal(0))
    return voucher.total_debit


def is_simple(voucher: Voucher) -> bool:
    """True if the voucher is written in the simple form: one debit line followed by
    one credit line."""
    lines = voucher.lines
    return len(lines) == len(LINE_FIELDS) and lines[0].debit > 0 and lines[1].credit > 0


def format_amount(amount: Decimal) -> str:
    """A whole amount without decimals, any other with two — as the books write them."""
    whole = amount == amount.to_integral_value()
    return f"{amount:.0f}" if whole else f"{amount:.2f}"


def write_voucher(directory: Path, voucher: Voucher, content: str) -> Path:
    """Create the voucher's file in ``directory`` with ``content``; return its path.

    An existing voucher is never replaced (ADR-009): the file is created exclusively,
    and a number that another file already has is refused.

    Raises:
        VoucherExistsError: if a file with the voucher's number exists.
        FileNotFoundError: if ``directory`` does not exist; it is not created.
    """
    name = voucher_file_name(voucher)
    prefix = name.split("_")[0] + "_"
    if any(path.name.startswith(prefix) for path in directory.iterdir()):
        # The message gives the number only; the text may hold a name.
        raise VoucherExistsError(f"voucher {voucher.number} already has a file")
    path = directory / name
    with path.open("xb") as file:
        file.write(content.encode("utf-8"))
    return path
