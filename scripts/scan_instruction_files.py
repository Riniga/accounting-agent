#!/usr/bin/env python3
"""Scan instruction files for suspicious or hidden Unicode characters.

Methodology F3 SKA 8 (023-P7): instruction files (AGENTS.md, CLAUDE.md, and anything
equivalent) are automatically scanned for suspicious/hidden instruction patterns, as a
complement to — not a replacement for — human review (F3 SKA 2-3).

This checks for Unicode characters used to hide text from a casual reader while still
being interpreted by software: zero-width characters, bidirectional-override characters
(can make text visually reorder to hide a substring), and Unicode tag characters (an
established technique for embedding invisible payloads in otherwise-plain text). None of
these have a legitimate reason to appear in a plain-Markdown instruction file.

Usage:
    python scripts/scan_instruction_files.py AGENTS.md CLAUDE.md [...]

Exits 0 if every given file exists and is clean, 1 if any file contains a flagged
character or is missing.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

# (start, end) inclusive codepoint ranges, plus a short reason for each.
_SUSPICIOUS_RANGES: list[tuple[int, int, str]] = [
    (0x200B, 0x200F, "zero-width / directional-mark character"),
    (0x202A, 0x202E, "bidirectional override/embedding character"),
    (0x2060, 0x2064, "word joiner / invisible operator"),
    (0x2066, 0x2069, "bidirectional isolate character"),
    (0xFEFF, 0xFEFF, "zero-width no-break space (BOM)"),
    (0xE0000, 0xE007F, "Unicode tag character (invisible payload technique)"),
]
# Individually listed, not part of a contiguous range worth naming as one.
_SUSPICIOUS_CODEPOINTS: dict[int, str] = {
    0x00AD: "soft hyphen",
}


def _reason_for(codepoint: int) -> str | None:
    if codepoint in _SUSPICIOUS_CODEPOINTS:
        return _SUSPICIOUS_CODEPOINTS[codepoint]
    for start, end, reason in _SUSPICIOUS_RANGES:
        if start <= codepoint <= end:
            return reason
    return None


def scan_file(path: Path) -> list[str]:
    """Return a list of human-readable findings for one file; empty if clean."""
    findings: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line_number, line in enumerate(text.splitlines(), start=1):
        for column, char in enumerate(line, start=1):
            reason = _reason_for(ord(char))
            if reason is None:
                continue
            name = unicodedata.name(char, "UNNAMED")
            findings.append(
                f"{path}:{line_number}:{column}: U+{ord(char):04X} ({name}) — {reason}"
            )
    return findings


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: scan_instruction_files.py FILE [FILE ...]", file=sys.stderr)
        return 2

    all_findings: list[str] = []
    for arg in argv:
        path = Path(arg)
        if not path.is_file():
            # A missing instruction file is itself worth failing on — this script is a
            # CI gate, not a best-effort report.
            all_findings.append(f"{arg}: file not found")
            continue
        all_findings.extend(scan_file(path))

    if all_findings:
        print("Suspicious characters found in instruction file(s):\n")
        for finding in all_findings:
            print(f"  {finding}")
        print(
            "\nIf this is a deliberate, legitimate use (unlikely in a plain-Markdown "
            "instruction file), remove the character or raise it for review before "
            "merging — do not silently widen this script's allowlist to make it pass."
        )
        return 1

    print(f"Clean: {len(argv)} instruction file(s) scanned, no suspicious characters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
