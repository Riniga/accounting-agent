"""Command line entry point: ``accounting-agent``."""

import argparse
import logging
import sys
from collections.abc import Callable, Sequence
from decimal import Decimal
from pathlib import Path

from accounting_agent import __version__
from accounting_agent.books import (
    Books,
    Finding,
    Severity,
    check_books,
    compute_balances,
    mask_personal_numbers,
    reconcile,
)
from accounting_agent.formats import bank_statement, front_matter, nordea_csv
from accounting_agent.profile import (
    BankConfig,
    BooksConfig,
    OrganisationProfile,
    ProfileError,
    load_profile,
)

logger = logging.getLogger(__name__)

EXIT_OK = 0
EXIT_ERROR = 1

BookReader = Callable[[Path, str], tuple[Books | None, list[Finding]]]
# One reader per book file format (ADR-006); the profile's `books.format` selects it.
READERS: dict[str, BookReader] = {"front-matter": front_matter.read_books}


def main(argv: Sequence[str] | None = None) -> int:
    """Parse ``argv`` and run the selected command. Returns the process exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = _build_parser().parse_args(argv)
    return args.handler(args)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="accounting-agent",
        description="Shared bookkeeping core for organisation projects.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    run = commands.add_parser("run", help="Run the agent core for one organisation.")
    _add_organisation_arguments(run)
    run.set_defaults(handler=_run)

    validate = commands.add_parser(
        "validate", help="Check that an organisation's books are consistent."
    )
    _add_organisation_arguments(validate)
    validate.add_argument(
        "--balances",
        action="store_true",
        help="Also list the balance per account (debit +, credit -).",
    )
    validate.add_argument(
        "--unbooked",
        action="store_true",
        help="Also list the bank transactions after the last voucher (date, amount).",
    )
    validate.set_defaults(handler=_validate)

    import_bank = commands.add_parser(
        "import-bank",
        help="Turn a bank export into the organisation's statement or fund-value file.",
    )
    _add_organisation_arguments(import_bank)
    import_bank.add_argument(
        "export", type=Path, help="The file downloaded from the bank; never changed."
    )
    import_bank.set_defaults(handler=_import_bank)
    return parser


def _add_organisation_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("organisation", help="Organisation id, e.g. 'my-club'.")
    parser.add_argument(
        "--config-dir",
        type=Path,
        required=True,
        help="The organisation's configuration directory (contains organisation.yaml).",
    )


def _load_matching_profile(args: argparse.Namespace) -> OrganisationProfile | None:
    """Load the profile and check it belongs to the organisation asked for."""
    try:
        profile = load_profile(args.config_dir)
    except ProfileError as error:
        logger.error("%s", error)
        return None

    # Guards against running one organisation's command against another's data.
    if profile.organisation != args.organisation:
        logger.error(
            "Asked to run '%s', but %s belongs to '%s'.",
            args.organisation,
            args.config_dir,
            profile.organisation,
        )
        return None
    return profile


def _run(args: argparse.Namespace) -> int:
    profile = _load_matching_profile(args)
    if profile is None:
        return EXIT_ERROR

    logger.info("Organisation '%s'", profile.organisation)
    logger.info("enabled features: %s", ", ".join(profile.enabled_features) or "(none)")
    logger.info(
        "disabled features: %s", ", ".join(profile.disabled_features) or "(none)"
    )
    return EXIT_OK


def _validate(args: argparse.Namespace) -> int:
    profile = _load_matching_profile(args)
    if profile is None:
        return EXIT_ERROR
    if profile.books is None:
        logger.error(
            "%s has no 'books' section in organisation.yaml; validate needs one.",
            args.config_dir,
        )
        return EXIT_ERROR

    config = profile.books
    books, findings = READERS[config.format](config.path, config.bank_account)
    _emit(
        f"Validation of books for '{profile.organisation}' "
        f"(fiscal year {config.fiscal_year})"
    )
    if books is not None:
        _emit(
            f"  {len(books.accounts)} accounts, "
            f"{len(books.opening_balances)} opening balances, "
            f"{len(books.vouchers)} vouchers"
        )
        findings = findings + check_books(books, config.fiscal_year)
        if profile.bank is not None:
            findings = findings + _reconcile(profile.bank, config, books, args.unbooked)

    _emit_findings(findings)
    if books is not None and args.balances:
        _emit_balances(compute_balances(books))

    _emit("")
    if books is None:
        _emit("RESULT: ERROR (the books could not be read)")
        return EXIT_ERROR
    counts = {s: sum(1 for f in findings if f.severity is s) for s in Severity}
    result = "ERROR" if counts[Severity.ERROR] else "OK"
    _emit(
        f"RESULT: {result} (errors: {counts[Severity.ERROR]}, "
        f"warnings: {counts[Severity.WARNING]}, info: {counts[Severity.INFO]})"
    )
    return EXIT_ERROR if counts[Severity.ERROR] else EXIT_OK


def _reconcile(
    bank: BankConfig, config: BooksConfig, books: Books, unbooked: bool
) -> list[Finding]:
    """Read the statement file and reconcile the books against it."""
    transactions, findings = bank_statement.read_statement(
        bank.statement_file, config.fiscal_year
    )
    if transactions is None:
        return findings
    return findings + reconcile(
        books, transactions, config.bank_account, list_unbooked=unbooked
    )


def _import_bank(args: argparse.Namespace) -> int:
    profile = _load_matching_profile(args)
    if profile is None:
        return EXIT_ERROR
    if profile.bank is None:
        logger.error(
            "%s has no 'bank' section in organisation.yaml; import-bank needs one.",
            args.config_dir,
        )
        return EXIT_ERROR
    if not args.export.is_file():
        logger.error("The export %s does not exist.", args.export)
        return EXIT_ERROR

    # Messages name files, dates and counts only — never a row's name or message.
    try:
        export = nordea_csv.read_export(args.export)
        if isinstance(export, nordea_csv.StatementExport):
            _write_statement(profile.bank.statement_file, export)
        elif profile.bank.fund_value_file is None:
            logger.error(
                "%s is a fund-value export, but 'bank.fund_value_file' is not "
                "configured.",
                args.export.name,
            )
            return EXIT_ERROR
        else:
            written = bank_statement.write_fund_values(
                profile.bank.fund_value_file, export.values
            )
            _emit(
                f"Wrote {profile.bank.fund_value_file.name}: {written.values} values, "
                f"latest {written.latest_date}."
            )
    except (
        nordea_csv.ExportFormatError,
        bank_statement.StatementRefusedError,
    ) as error:
        logger.error("%s", error)
        return EXIT_ERROR
    return EXIT_OK


def _write_statement(path: Path, export: nordea_csv.StatementExport) -> None:
    written = bank_statement.write_statement(path, export.rows)
    if written.replaced_rows is not None:
        _emit(f"Replaced {written.replaced_rows} rows with {written.rows}.")
    _emit(
        f"Wrote {path.name}: {written.rows} rows, "
        f"{written.first_date} to {written.last_date}."
    )


def _emit_findings(findings: list[Finding]) -> None:
    for severity in Severity:
        group = [f for f in findings if f.severity is severity]
        if group:
            _emit("")
            _emit(f"{severity.label} ({len(group)})")
            for finding in group:
                _emit(f"  {finding.render()}")


def _emit_balances(balances: dict[str, Decimal]) -> None:
    _emit("")
    _emit("BALANCES (debit +, credit -)")
    for account in sorted(balances):
        _emit(f"{account};{balances[account]}")


def _emit(line: str) -> None:
    """Write one report line to stdout — always masked (methodology E4 SKA 3)."""
    sys.stdout.write(mask_personal_numbers(line) + "\n")
