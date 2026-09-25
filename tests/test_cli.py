"""Tests for the accounting-agent command line."""

import logging
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from accounting_agent.cli import main


def test_run_reports_enabled_and_disabled_features(
    example_config_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO):
        exit_code = main(["run", "example", "--config-dir", str(example_config_dir)])

    assert exit_code == 0
    assert "enabled features: accounting" in caplog.text
    assert "disabled features: discord, gmail, payroll" in caplog.text


def test_run_fails_when_organisation_does_not_match_profile(
    example_config_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    # Guards against running one organisation's command against another's configuration.
    exit_code = main(["run", "other-org", "--config-dir", str(example_config_dir)])

    assert exit_code == 1
    assert "other-org" in caplog.text
    assert "example" in caplog.text


def test_run_fails_cleanly_on_invalid_profile(
    write_profile: Callable[[str], Path], caplog: pytest.LogCaptureFixture
) -> None:
    config_dir = write_profile("organisation: example\n")

    exit_code = main(["run", "example", "--config-dir", str(config_dir)])

    assert exit_code == 1
    assert "'features'" in caplog.text
    assert "Traceback" not in caplog.text


def test_run_fails_cleanly_on_missing_config_dir(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    exit_code = main(["run", "example", "--config-dir", str(tmp_path / "missing")])

    assert exit_code == 1
    assert "does not exist" in caplog.text


def test_missing_command_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main([])

    assert excinfo.value.code == 2


def test_run_requires_config_dir() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["run", "example"])

    assert excinfo.value.code == 2


def test_module_entry_point_runs_end_to_end(example_config_dir: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "accounting_agent",
            "run",
            "example",
            "--config-dir",
            str(example_config_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "enabled features: accounting" in result.stderr
