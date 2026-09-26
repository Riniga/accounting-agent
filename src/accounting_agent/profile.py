"""Organisation profile: which organisation a run is for and which features it uses.

The profile is read from ``organisation.yaml`` in the organisation's configuration
directory. It is the only place organisation-specific settings enter the core.
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

PROFILE_FILE_NAME = "organisation.yaml"
KNOWN_KEYS = frozenset({"organisation", "features", "books"})
BOOKS_KEYS = ("path", "format", "fiscal_year", "bank_account")
# File formats the core can read (ADR-006). Named after the format, never an organisation.
BOOK_FORMATS = frozenset({"front-matter"})
# Lowercase slug, as used on the command line and in file and resource names.
ORGANISATION_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
ACCOUNT_NUMBER = re.compile(r"\d{4}")


class ProfileError(Exception):
    """The organisation profile is missing or invalid."""


@dataclass(frozen=True)
class BooksConfig:
    """Where an organisation's books are and how to read them."""

    path: Path
    format: str
    fiscal_year: int
    bank_account: str


@dataclass(frozen=True)
class OrganisationProfile:
    """A validated organisation profile."""

    organisation: str
    features: dict[str, bool]
    books: BooksConfig | None = None

    @property
    def enabled_features(self) -> list[str]:
        """Names of enabled features, sorted."""
        return sorted(name for name, enabled in self.features.items() if enabled)

    @property
    def disabled_features(self) -> list[str]:
        """Names of disabled features, sorted."""
        return sorted(name for name, enabled in self.features.items() if not enabled)


def load_profile(config_dir: Path) -> OrganisationProfile:
    """Read and validate ``organisation.yaml`` from ``config_dir``.

    Raises:
        ProfileError: if the directory or file is missing, or the content is invalid.
    """
    if not config_dir.is_dir():
        raise ProfileError(f"Configuration directory {config_dir} does not exist.")

    path = config_dir / PROFILE_FILE_NAME
    if not path.is_file():
        raise ProfileError(f"{PROFILE_FILE_NAME} not found in {config_dir}.")

    try:
        # safe_load: the file must never be able to construct arbitrary Python objects.
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ProfileError(f"{path} is not valid YAML: {error}") from error

    if not isinstance(data, dict):
        raise ProfileError(
            f"{path} must contain a mapping with 'organisation' and 'features'."
        )

    for key in sorted(set(data) - KNOWN_KEYS, key=str):
        logger.warning("Ignoring unknown key '%s' in %s.", key, path)

    return OrganisationProfile(
        organisation=_parse_organisation(data.get("organisation"), path),
        features=_parse_features(data.get("features"), path),
        books=_parse_books(data["books"], path) if "books" in data else None,
    )


def _parse_organisation(value: object, path: Path) -> str:
    if not isinstance(value, str) or not ORGANISATION_ID.fullmatch(value):
        raise ProfileError(
            f"'organisation' in {path} must be a lowercase id such as 'my-club', "
            f"got {value!r}."
        )
    return value


def _parse_features(value: object, path: Path) -> dict[str, bool]:
    if not isinstance(value, dict):
        raise ProfileError(
            f"'features' in {path} must be a mapping of feature names to true/false."
        )

    features: dict[str, bool] = {}
    for name, enabled in value.items():
        # bool is checked exactly: YAML 1 or "true" must not silently count as enabled.
        if not isinstance(name, str) or not isinstance(enabled, bool):
            raise ProfileError(
                f"Feature {name!r} in {path} must be set to true or false, got {enabled!r}."
            )
        features[name] = enabled
    return features


def _parse_books(value: object, path: Path) -> BooksConfig:
    if not isinstance(value, dict):
        raise ProfileError(
            f"'books' in {path} must be a mapping with {', '.join(BOOKS_KEYS)}."
        )

    for key in BOOKS_KEYS:
        if key not in value:
            raise ProfileError(f"'books.{key}' is missing in {path}.")
    for key in sorted(set(value) - set(BOOKS_KEYS), key=str):
        logger.warning("Ignoring unknown key 'books.%s' in %s.", key, path)

    return BooksConfig(
        path=_parse_books_path(value["path"], path),
        format=_parse_books_format(value["format"], path),
        fiscal_year=_parse_fiscal_year(value["fiscal_year"], path),
        bank_account=_parse_bank_account(value["bank_account"], path),
    )


def _parse_books_path(value: object, path: Path) -> Path:
    if not isinstance(value, str) or not value:
        raise ProfileError(
            f"'books.path' in {path} must be a directory name, got {value!r}."
        )
    books_dir = (path.parent / value).resolve()
    if not books_dir.is_dir():
        raise ProfileError(f"'books.path' in {path} is not a directory: {books_dir}.")
    return books_dir


def _parse_books_format(value: object, path: Path) -> str:
    if value not in BOOK_FORMATS:
        raise ProfileError(
            f"'books.format' in {path} must be one of {', '.join(sorted(BOOK_FORMATS))}, "
            f"got {value!r}."
        )
    return str(value)


def _parse_fiscal_year(value: object, path: Path) -> int:
    # bool is a subclass of int; `true` must not become year 1.
    if not isinstance(value, int) or isinstance(value, bool):
        raise ProfileError(
            f"'books.fiscal_year' in {path} must be a year, got {value!r}."
        )
    return value


def _parse_bank_account(value: object, path: Path) -> str:
    # Accepted quoted or unquoted; YAML reads an unquoted account number as an integer.
    text = (
        str(value) if isinstance(value, int) and not isinstance(value, bool) else value
    )
    if not isinstance(text, str) or not ACCOUNT_NUMBER.fullmatch(text):
        raise ProfileError(
            f"'books.bank_account' in {path} must be a four-digit account number, "
            f"got {value!r}."
        )
    return text
