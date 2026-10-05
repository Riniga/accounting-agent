"""Regression test: the report is UTF-8 even when stdout is a pipe (MVP-003 plan §6).

On Windows, Python writes to a pipe in the locale's code page (cp1252), so Swedish
letters such as the to-do owner `kassör` arrived garbled in whatever read the output —
an organisation project's script or an AI tool. The organisation's own `kontroll.py`
avoids this by reconfiguring stdout to UTF-8. On Linux CI the locale is UTF-8 already,
so this test only fails on Windows without the fix.
"""

import os
import subprocess
import sys
from pathlib import Path

FULL = Path(__file__).parent / "fixtures" / "example-full"


def test_piped_report_is_utf8() -> None:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in ("PYTHONIOENCODING", "PYTHONUTF8")
    }
    env["PYTHONUTF8"] = "0"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "accounting_agent",
            "validate",
            "example",
            "--config-dir",
            str(FULL),
        ],
        capture_output=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert "(kassör 1, vi 1)".encode() in result.stdout
