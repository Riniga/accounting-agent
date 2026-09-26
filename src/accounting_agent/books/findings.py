"""Findings: the results of reading and checking books."""

from dataclasses import dataclass
from enum import IntEnum


class Severity(IntEnum):
    """How serious a finding is. Lower values sort first."""

    ERROR = 0
    WARNING = 1
    INFO = 2

    @property
    def label(self) -> str:
        """Upper-case name used in output, e.g. ``ERROR``."""
        return self.name


@dataclass(frozen=True, order=True)
class Finding:
    """One result of a check: severity, rule id, where, and what.

    The message must never quote a voucher's text — it can contain names and personal
    identity numbers (MVP-002 plan, STRIDE).
    """

    severity: Severity
    rule: str
    location: str
    message: str

    def render(self) -> str:
        """One line, e.g. ``ERROR [rule] location: message``."""
        return f"{self.severity.label} [{self.rule}] {self.location}: {self.message}"
