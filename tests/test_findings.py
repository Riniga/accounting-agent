"""Tests for findings: the result of a check (severity, rule, location, message)."""

from accounting_agent.books import Finding, Severity


def test_finding_renders_as_one_line() -> None:
    finding = Finding(
        severity=Severity.ERROR,
        rule="opening-balance-sum",
        location="ingående-balans.csv",
        message="the sum is 10.00, must be 0",
    )

    assert (
        finding.render()
        == "ERROR [opening-balance-sum] ingående-balans.csv: the sum is 10.00, must be 0"
    )


def test_severity_labels() -> None:
    assert [s.label for s in Severity] == ["ERROR", "WARNING", "INFO"]


def test_findings_sort_errors_first_then_warnings_then_info() -> None:
    info = Finding(Severity.INFO, "a", "x", "m")
    warning = Finding(Severity.WARNING, "a", "x", "m")
    error = Finding(Severity.ERROR, "a", "x", "m")

    assert sorted([info, warning, error]) == [error, warning, info]


def test_findings_are_immutable_and_comparable() -> None:
    first = Finding(Severity.WARNING, "rule", "voucher 3", "message")
    second = Finding(Severity.WARNING, "rule", "voucher 3", "message")

    assert first == second
    assert hash(first) == hash(second)
