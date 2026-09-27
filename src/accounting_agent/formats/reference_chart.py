"""Reader for a reference chart of accounts (BAS) in four CSV files (ADR-007).

The format is the one Helsingborgs Judoklubb keeps in its `kontobas/` folder: main
accounts, sub-accounts and account groups as ``nummer;beskrivning``, and the accounts not
to use as a list whose first column is the number. The files follow the shared CSV rules
(`formats.common`). Descriptions are whitespace-normalised, as `kontroll.py` does.
"""

import csv
import io
from pathlib import Path

from accounting_agent.books import Finding, ReferenceChart, Severity
from accounting_agent.books.reference import normalise
from accounting_agent.formats.common import Findings, read_csv, read_text

MAIN_FILE = "kontoplan-huvudkonto.csv"
SUB_FILE = "kontoplan-underkonto.csv"
GROUP_FILE = "kontoplan-kontoklasser.csv"
EXCLUDED_FILE = "kontoplan-använd-ej.csv"
FILES = (MAIN_FILE, SUB_FILE, GROUP_FILE, EXCLUDED_FILE)
HEADER = ["nummer", "beskrivning"]


def read_reference_chart(folder: Path) -> tuple[ReferenceChart | None, list[Finding]]:
    """Read the reference chart from ``folder``.

    Returns ``(None, findings)`` if a file is missing or cannot be read; the chart is
    then not checked against the reference, as in `kontroll.py`.
    """
    findings = Findings()
    missing = [name for name in FILES if not (folder / name).is_file()]
    if missing:
        findings.add(
            Severity.WARNING,
            "reference-missing",
            f"{folder.name}/",
            f"missing {', '.join(missing)}; the chart is not checked against the "
            f"reference chart",
        )
        return None, findings.items

    tables = [read_csv(folder / name, HEADER, findings) for name in FILES[:3]]
    excluded_text = read_text(folder / EXCLUDED_FILE, findings)
    main, sub, groups = tables
    if main is None or sub is None or groups is None or excluded_text is None:
        return None, findings.items

    accounts: dict[str, str] = {}
    for row in main + sub:
        # A main account's description wins over a sub-account with the same number.
        accounts.setdefault(row["nummer"], normalise(row["beskrivning"]))
    excluded = frozenset(
        row[0]
        for row in csv.reader(io.StringIO(excluded_text), delimiter=";")
        if row and row[0].isdigit()
    )
    reference = ReferenceChart(
        accounts=accounts,
        excluded=excluded,
        groups={row["nummer"]: normalise(row["beskrivning"]) for row in groups},
    )
    return reference, findings.items
