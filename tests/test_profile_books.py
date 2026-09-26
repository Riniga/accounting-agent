"""Tests for the `books` section of an organisation profile (organisation.yaml)."""

import logging
from collections.abc import Callable
from pathlib import Path

import pytest

from accounting_agent.profile import ProfileError, load_profile

HEADER = """\
organisation: example
features:
  accounting: true
"""

BOOKS = """\
books:
  path: books
  format: front-matter
  fiscal_year: 2026
  bank_account: "1930"
"""


@pytest.fixture
def config_with_books_dir(
    write_profile: Callable[[str], Path],
) -> Callable[[str], Path]:
    """Write organisation.yaml and create the `books` directory next to it."""

    def _write(content: str) -> Path:
        config_dir = write_profile(content)
        (config_dir / "books").mkdir(exist_ok=True)
        return config_dir

    return _write


def test_profile_without_books_section_has_no_books(
    write_profile: Callable[[str], Path],
) -> None:
    # `run` does not need books; only `validate` does.
    profile = load_profile(write_profile(HEADER))

    assert profile.books is None


def test_valid_books_section_is_loaded(
    config_with_books_dir: Callable[[str], Path],
) -> None:
    config_dir = config_with_books_dir(HEADER + BOOKS)

    books = load_profile(config_dir).books

    assert books is not None
    assert books.path == (config_dir / "books").resolve()
    assert books.format == "front-matter"
    assert books.fiscal_year == 2026
    assert books.bank_account == "1930"


def test_books_path_is_resolved_relative_to_the_config_dir(
    config_with_books_dir: Callable[[str], Path],
) -> None:
    config_dir = config_with_books_dir(HEADER + BOOKS.replace("path: books", "path: ."))

    books = load_profile(config_dir).books

    assert books is not None
    assert books.path == config_dir.resolve()


def test_bank_account_given_as_a_number_is_normalised_to_a_string(
    config_with_books_dir: Callable[[str], Path],
) -> None:
    config_dir = config_with_books_dir(
        HEADER + BOOKS.replace('bank_account: "1930"', "bank_account: 1930")
    )

    books = load_profile(config_dir).books

    assert books is not None
    assert books.bank_account == "1930"


def test_books_must_be_a_mapping(write_profile: Callable[[str], Path]) -> None:
    config_dir = write_profile(HEADER + "books: Bokföring\n")

    with pytest.raises(ProfileError, match="'books'"):
        load_profile(config_dir)


@pytest.mark.parametrize("key", ["path", "format", "fiscal_year", "bank_account"])
def test_missing_books_key_is_an_error(
    config_with_books_dir: Callable[[str], Path], key: str
) -> None:
    lines = [line for line in BOOKS.splitlines() if not line.strip().startswith(key)]
    config_dir = config_with_books_dir(HEADER + "\n".join(lines) + "\n")

    with pytest.raises(ProfileError, match=f"'books.{key}'"):
        load_profile(config_dir)


def test_unknown_format_is_an_error(
    config_with_books_dir: Callable[[str], Path],
) -> None:
    config_dir = config_with_books_dir(
        HEADER + BOOKS.replace("format: front-matter", "format: excel")
    )

    with pytest.raises(ProfileError, match="'books.format'"):
        load_profile(config_dir)


@pytest.mark.parametrize("value", ['"193"', '"19300"', '"19A0"', "true", "''"])
def test_bank_account_must_be_four_digits(
    config_with_books_dir: Callable[[str], Path], value: str
) -> None:
    config_dir = config_with_books_dir(
        HEADER + BOOKS.replace('bank_account: "1930"', f"bank_account: {value}")
    )

    with pytest.raises(ProfileError, match="'books.bank_account'"):
        load_profile(config_dir)


@pytest.mark.parametrize("value", ['"2026"', "2026.0", "true"])
def test_fiscal_year_must_be_an_integer(
    config_with_books_dir: Callable[[str], Path], value: str
) -> None:
    config_dir = config_with_books_dir(
        HEADER + BOOKS.replace("fiscal_year: 2026", f"fiscal_year: {value}")
    )

    with pytest.raises(ProfileError, match="'books.fiscal_year'"):
        load_profile(config_dir)


def test_books_path_must_be_an_existing_directory(
    write_profile: Callable[[str], Path],
) -> None:
    # No `books` directory is created next to organisation.yaml.
    config_dir = write_profile(HEADER + BOOKS)

    with pytest.raises(ProfileError, match="'books.path'"):
        load_profile(config_dir)


def test_unknown_books_key_is_ignored_with_a_warning(
    config_with_books_dir: Callable[[str], Path], caplog: pytest.LogCaptureFixture
) -> None:
    # Later MVPs may add keys (e.g. parking accounts); an older core should not break.
    config_dir = config_with_books_dir(HEADER + BOOKS + "  parking_accounts: []\n")

    with caplog.at_level(logging.WARNING):
        books = load_profile(config_dir).books

    assert books is not None
    assert "parking_accounts" in caplog.text


def test_books_is_no_longer_reported_as_an_unknown_key(
    config_with_books_dir: Callable[[str], Path], caplog: pytest.LogCaptureFixture
) -> None:
    config_dir = config_with_books_dir(HEADER + BOOKS)

    with caplog.at_level(logging.WARNING):
        load_profile(config_dir)

    assert "Ignoring unknown key 'books'" not in caplog.text
