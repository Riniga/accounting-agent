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
KNOWN_KEYS = frozenset(
    {"organisation", "features", "books", "bank", "checks", "conventions", "reports"}
)
BOOKS_KEYS = ("path", "format", "fiscal_year", "bank_account")
BANK_KEYS = ("export_format", "statement_file", "fund_account", "fund_value_file")
CHECKS_FOLDER_KEYS = ("reference_chart", "documents")
CHECKS_FILE_KEYS = ("budget_file", "comments_file", "todo_file")
CONVENTIONS_ACCOUNT_KEYS = ("parking_accounts", "no_document_accounts")
CONVENTIONS_TEXT_KEYS = ("guessed_posting_marker", "outlay_prefix")
REPORTS_KEYS = ("output", "organisation_name", "organisation_number")
# File formats the core can read (ADR-006). Named after the format, never an organisation.
BOOK_FORMATS = frozenset({"front-matter"})
# Bank export formats the core can import (ADR-008). Named after the bank's format.
BANK_EXPORT_FORMATS = frozenset({"nordea-csv"})
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
class BankConfig:
    """Where the bank statement and fund-value files are, and the bank's export format."""

    export_format: str
    statement_file: Path
    fund_account: str | None = None
    fund_value_file: Path | None = None


@dataclass(frozen=True)
class ChecksConfig:
    """Optional inputs to the checks; a check whose input is not configured is skipped."""

    reference_chart: Path | None = None
    documents: Path | None = None
    budget_file: Path | None = None
    comments_file: Path | None = None
    todo_file: Path | None = None


@dataclass(frozen=True)
class ConventionsConfig:
    """Organisation conventions the checks and reports follow (MVP-003 plan §0.4)."""

    parking_accounts: tuple[str, ...] = ()
    no_document_accounts: tuple[str, ...] = ()
    guessed_posting_marker: str | None = None
    outlay_prefix: str | None = None


@dataclass(frozen=True)
class ReportsConfig:
    """Where the reports are written, and the organisation's name and number."""

    output: Path
    organisation_name: str
    organisation_number: str


@dataclass(frozen=True)
class OrganisationProfile:
    """A validated organisation profile."""

    organisation: str
    features: dict[str, bool]
    books: BooksConfig | None = None
    bank: BankConfig | None = None
    checks: ChecksConfig | None = None
    conventions: ConventionsConfig = ConventionsConfig()
    reports: ReportsConfig | None = None

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
        bank=_parse_bank(data["bank"], path) if "bank" in data else None,
        checks=_parse_checks(data["checks"], path) if "checks" in data else None,
        conventions=(
            _parse_conventions(data["conventions"], path)
            if "conventions" in data
            else ConventionsConfig()
        ),
        reports=_parse_reports(data["reports"], path) if "reports" in data else None,
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


def _section(
    value: object,
    name: str,
    keys: tuple[str, ...],
    required: tuple[str, ...],
    path: Path,
) -> dict[str, object]:
    """Check that a section is a mapping with its required keys; warn on unknown keys."""
    if not isinstance(value, dict):
        raise ProfileError(
            f"'{name}' in {path} must be a mapping with {', '.join(keys)}."
        )
    for key in required:
        if key not in value:
            raise ProfileError(f"'{name}.{key}' is missing in {path}.")
    for key in sorted(set(value) - set(keys), key=str):
        logger.warning("Ignoring unknown key '%s.%s' in %s.", name, key, path)
    return value


def _parse_books(value: object, path: Path) -> BooksConfig:
    value = _section(value, "books", BOOKS_KEYS, BOOKS_KEYS, path)

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
    return _parse_account(value, "books.bank_account", path)


def _parse_account(value: object, key: str, path: Path) -> str:
    # Accepted quoted or unquoted; YAML reads an unquoted account number as an integer.
    text = (
        str(value) if isinstance(value, int) and not isinstance(value, bool) else value
    )
    if not isinstance(text, str) or not ACCOUNT_NUMBER.fullmatch(text):
        raise ProfileError(
            f"'{key}' in {path} must be a four-digit account number, got {value!r}."
        )
    return text


def _parse_text(value: object, key: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProfileError(f"'{key}' in {path} must be non-empty text, got {value!r}.")
    return value


def _resolve(value: object, key: str, path: Path) -> Path:
    """A path relative to the configuration directory, as for `books.path`."""
    if not isinstance(value, str) or not value:
        raise ProfileError(f"'{key}' in {path} must be a path, got {value!r}.")
    return (path.parent / value).resolve()


def _parse_folder(value: object, key: str, path: Path) -> Path:
    folder = _resolve(value, key, path)
    if not folder.is_dir():
        raise ProfileError(f"'{key}' in {path} is not a directory: {folder}.")
    return folder


def _parse_bank(value: object, path: Path) -> BankConfig:
    value = _section(value, "bank", BANK_KEYS, BANK_KEYS[:2], path)
    export_format = value["export_format"]
    if export_format not in BANK_EXPORT_FORMATS:
        raise ProfileError(
            f"'bank.export_format' in {path} must be one of "
            f"{', '.join(sorted(BANK_EXPORT_FORMATS))}, got {export_format!r}."
        )
    statement_file = _resolve(value["statement_file"], "bank.statement_file", path)
    # The core writes the statement file (ADR-008) but never creates folders for it.
    if not statement_file.parent.is_dir():
        raise ProfileError(
            f"'bank.statement_file' in {path}: the folder "
            f"{statement_file.parent} does not exist."
        )

    has_account, has_file = "fund_account" in value, "fund_value_file" in value
    if has_account != has_file:
        raise ProfileError(
            f"'bank.fund_account' and 'bank.fund_value_file' in {path} must be "
            f"given together."
        )
    return BankConfig(
        export_format=str(export_format),
        statement_file=statement_file,
        fund_account=(
            _parse_account(value["fund_account"], "bank.fund_account", path)
            if has_account
            else None
        ),
        fund_value_file=(
            _resolve(value["fund_value_file"], "bank.fund_value_file", path)
            if has_file
            else None
        ),
    )


def _parse_checks(value: object, path: Path) -> ChecksConfig:
    keys = CHECKS_FOLDER_KEYS + CHECKS_FILE_KEYS
    value = _section(value, "checks", keys, (), path)
    parsed: dict[str, Path] = {}
    for key in CHECKS_FOLDER_KEYS:
        if key in value:
            parsed[key] = _parse_folder(value[key], f"checks.{key}", path)
    for key in CHECKS_FILE_KEYS:
        # A configured but missing file skips its check, as in kontroll.py.
        if key in value:
            parsed[key] = _resolve(value[key], f"checks.{key}", path)
    return ChecksConfig(**parsed)


def _parse_conventions(value: object, path: Path) -> ConventionsConfig:
    keys = CONVENTIONS_ACCOUNT_KEYS + CONVENTIONS_TEXT_KEYS
    value = _section(value, "conventions", keys, (), path)
    accounts = {
        key: _parse_account_list(value[key], f"conventions.{key}", path)
        for key in CONVENTIONS_ACCOUNT_KEYS
        if key in value
    }
    texts = {
        key: _parse_text(value[key], f"conventions.{key}", path)
        for key in CONVENTIONS_TEXT_KEYS
        if key in value
    }
    return ConventionsConfig(**accounts, **texts)


def _parse_account_list(value: object, key: str, path: Path) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ProfileError(
            f"'{key}' in {path} must be a list of account numbers, got {value!r}."
        )
    return tuple(_parse_account(item, key, path) for item in value)


def _parse_reports(value: object, path: Path) -> ReportsConfig:
    value = _section(value, "reports", REPORTS_KEYS, REPORTS_KEYS, path)
    output = _parse_text(value["output"], "reports.output", path)
    return ReportsConfig(
        # The output folder need not exist; `report` creates it (ADR-008).
        output=_resolve(output, "reports.output", path),
        organisation_name=_parse_text(
            value["organisation_name"], "reports.organisation_name", path
        ),
        organisation_number=_parse_text(
            value["organisation_number"], "reports.organisation_number", path
        ),
    )
