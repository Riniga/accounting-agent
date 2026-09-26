"""Reader for the `front-matter` book format (ADR-006).

The format: a chart of accounts and an opening balance as semicolon-separated UTF-8 CSV,
and one Markdown file per voucher whose fields sit between two ``---`` lines. The field
parser deliberately reproduces the semantics of the organisation's own tool (a value
starting with ``"`` is a JSON string; a line is split at its first colon), so that results
stay comparable. Every problem is reported as a finding; no finding ever quotes a
voucher's text.
"""

import json
import re
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


def read_books(path: Path, bank_account: str) -> tuple[Books | None, list[Finding]]:
    """Read an organisation's books in the `front-matter` format.

    Returns ``(None, findings)`` when the books cannot be read at all (a missing file or
    directory, invalid UTF-8, or a wrong header); otherwise the books and every finding.
    """
    findings = Findings()
    chart_rows = read_csv(path / CHART_FILE, CHART_HEADER, findings)
    opening_rows = read_csv(path / OPENING_FILE, OPENING_HEADER, findings)
    vouchers = _read_vouchers(path / VOUCHER_DIR, bank_account, findings)
    if chart_rows is None or opening_rows is None or vouchers is None:
        return None, findings.items

    books = Books(
        accounts=tuple(Account(r["konto"], r["lokal_benämning"]) for r in chart_rows),
        opening_balances=_opening_balances(opening_rows, findings),
        vouchers=vouchers,
    )
    return books, findings.items


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
    directory: Path, bank_account: str, findings: Findings
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
        fields, note = parsed
        voucher = _to_voucher(path.name, match, fields, note, bank_account, findings)
        if voucher is not None:
            vouchers.append(voucher)
    return tuple(vouchers)


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
