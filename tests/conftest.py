"""Shared test fixtures."""

from collections.abc import Callable
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def example_config_dir() -> Path:
    """Configuration directory of the synthetic example organisation."""
    return FIXTURES / "example"


@pytest.fixture
def write_profile(tmp_path: Path) -> Callable[[str], Path]:
    """Write ``organisation.yaml`` with the given content and return its directory."""

    def _write(content: str) -> Path:
        (tmp_path / "organisation.yaml").write_text(content, encoding="utf-8")
        return tmp_path

    return _write
