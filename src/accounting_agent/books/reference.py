"""The chart of accounts against a reference chart (BAS), as `kontroll.py` checks it.

No message quotes an account's local name or a description.
"""

import re
from collections.abc import Sequence

from accounting_agent.books.findings import Finding, Severity
from accounting_agent.books.model import Account, ReferenceChart

ACCOUNT_NUMBER = re.compile(r"\d{4}")


def normalise(text: str) -> str:
    """Collapse runs of whitespace, as the reference files and the chart may differ."""
    return " ".join(text.split())


def check_reference(
    accounts: Sequence[Account], reference: ReferenceChart
) -> list[Finding]:
    """Check each account against the reference chart; own accounts are listed once."""
    findings: list[Finding] = []
    own: set[str] = set()
    for account in accounts:
        # Malformed numbers are already errors in check_books().
        if not ACCOUNT_NUMBER.fullmatch(account.number):
            continue
        if account.number not in reference.accounts:
            own.add(account.number)
        findings += _check_account(account, reference)
    if own:
        findings.append(
            Finding(
                Severity.INFO,
                "reference-own-accounts",
                "chart of accounts",
                f"own accounts not in the reference chart: {', '.join(sorted(own))}",
            )
        )
    return findings


def _check_account(account: Account, reference: ReferenceChart) -> list[Finding]:
    location = f"account {account.number}"
    findings: list[Finding] = []
    if account.number in reference.excluded:
        findings.append(
            Finding(
                Severity.ERROR,
                "reference-excluded",
                location,
                "is on the reference chart's list of accounts not to use",
            )
        )
    description = reference.accounts.get(account.number)
    if description is not None and account.reference_description is not None:
        if not account.reference_description.strip():
            findings.append(
                Finding(
                    Severity.INFO,
                    "reference-other-meaning",
                    location,
                    "used with its own meaning; the reference chart means something "
                    "else",
                )
            )
        elif normalise(account.reference_description) != description:
            findings.append(
                Finding(
                    Severity.WARNING,
                    "reference-description",
                    location,
                    "the reference description differs from the reference chart",
                )
            )

    group_number = account.number[:2]
    group = reference.groups.get(group_number)
    if group is None:
        findings.append(
            Finding(
                Severity.ERROR,
                "reference-unknown-group",
                location,
                f"belongs to no known account group ({group_number})",
            )
        )
    elif account.group is not None and not group.upper().startswith(
        normalise(account.group).upper()
    ):
        findings.append(
            Finding(
                Severity.WARNING,
                "reference-group",
                location,
                f"the account group differs from the reference chart's group "
                f"{group_number}",
            )
        )
    return findings
