"""Reader for the `front-matter` book format (ADR-006).

The format: a chart of accounts and an opening balance as semicolon-separated UTF-8 CSV,
and one Markdown file per voucher whose fields sit between two ``---`` lines. The field
parser deliberately reproduces the semantics of the organisation's own tool (a value
starting with ``"`` is a JSON string; a line is split at its first colon), so that results
stay comparable. Every problem is reported as a finding; no finding ever quotes a
voucher's text.

Below the fields a voucher may start with generated lines (ADR-009): the accounts with
their names, then a link to each supporting document. They repeat the fields for the
reader's sake, so they are kept out of the note and checked against the fields.
"""

import json
import re
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
GENERATED_DOCUMENT = re.compile(r"Underlag: \[(.+)\]\(<(.+)>\)")


@dataclass(frozen=True)
class _GeneratedLines:
    """What a voucher's generated lines say: accounts as (number, name), then links."""

    debit: tuple[str, str]
    credit: tuple[str, str]
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
        fields, body = parsed
        generated, note = _split_generated(body)
        voucher = _to_voucher(path.name, match, fields, note, bank_account, findings)
        if voucher is not None:
            if generated is not None:
                _check_generated(voucher, generated, account_names, findings)
            vouchers.append(voucher)
    return tuple(vouchers)


def _split_generated(body: str) -> tuple[_GeneratedLines | None, str]:
    """Split a voucher's body into its generated lines and the note.

    Only the top of the body counts: the account line first, then the document lines.
    A line of the same shape further down is the writer's own and stays in the note.
    """
    lines = body.split("\n")
    accounts = GENERATED_ACCOUNTS.fullmatch(lines[0].rstrip())
    if accounts is None:
        return None, body
    links: list[tuple[str, str]] = []
    for line in lines[1:]:
        link = GENERATED_DOCUMENT.fullmatch(line.rstrip())
        if link is None:
            break
        links.append((link.group(1), link.group(2)))
    generated = _GeneratedLines(
        debit=(accounts.group(1), accounts.group(2)),
        credit=(accounts.group(3), accounts.group(4)),
        links=tuple(links),
    )
    return generated, "\n".join(lines[1 + len(links) :]).strip()


def _check_generated(
    voucher: Voucher,
    generated: _GeneratedLines,
    account_names: dict[str, str],
    findings: Findings,
) -> None:
    """The fields are the single source; generated lines that disagree mislead."""
    # Messages name account numbers only: names and file names can hold a person's name.
    debit, credit = voucher.lines
    if (generated.debit[0], generated.credit[0]) != (debit.account, credit.account):
        findings.add(
            Severity.ERROR,
            "generated-accounts",
            voucher.source,
            "the generated account line does not match the fields 'debet' and 'kredit'",
        )
    else:
        for number, name in (generated.debit, generated.credit):
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


def _read_front_matter(
    path: Path, findings: Findings
) -> tuple[dict[str, str], str] | None:
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

    fields: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:end], start=2):
        if not line.strip():
            continue
        key, colon, value = line.partition(":")
        key, value = key.strip(), value.strip()
        # Messages name the line or the field, never the value: it may be voucher text.
        if not colon or key not in REQUIRED_FIELDS + OPTIONAL_FIELDS:
            findings.add(
                Severity.ERROR,
                "unknown-field",
                path.name,
                f"line {line_number} is not a known field",
            )
            continue
        if key in fields:
            findings.add(
                Severity.ERROR,
                "duplicate-field",
                path.name,
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
                    path.name,
                    f"field '{key}' has invalid quotes",
                )
                continue
        fields[key] = value

    missing = [key for key in REQUIRED_FIELDS if key not in fields]
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
    return fields, note


def _to_voucher(
    name: str,
    match: re.Match[str],
    fields: dict[str, str],
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

    debit_account, credit_account = fields["debet"], fields["kredit"]
    _check_bank_sign(
        name, amount, debit_account, credit_account, bank_account, findings
    )
    magnitude = abs(amount)
    return Voucher(
        series=None,
        number=number,
        date=voucher_date,
        text=fields["text"],
        lines=(
            PostingLine(debit_account, debit=magnitude),
            PostingLine(credit_account, credit=magnitude),
        ),
        documents=tuple(d.strip() for d in fields["underlag"].split(";") if d.strip()),
        note=note,
        source=name,
    )


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
