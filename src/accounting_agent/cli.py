"""Command line entry point: ``accounting-agent``."""

import argparse
import io
import logging
import os
import re
import sys
from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from accounting_agent import __version__
from accounting_agent.books import (
    BankTransaction,
    Books,
    BudgetItem,
    ClosingComment,
    Finding,
    FundValue,
    PostingLine,
    Severity,
    TodoItem,
    Voucher,
    VoucherRefusedError,
    VoucherRequest,
    build_voucher,
    check_books,
    check_budget,
    check_comments,
    check_details,
    check_fund,
    check_reference,
    check_todo,
    compute_balances,
    mask_personal_numbers,
    reconcile,
)
from accounting_agent.formats import (
    bank_statement,
    front_matter,
    nordea_csv,
    reference_chart,
    supplements,
)
from accounting_agent.formats.common import parse_amount, write_text_atomically
from accounting_agent.profile import (
    BankConfig,
    BooksConfig,
    ChecksConfig,
    OrganisationProfile,
    ProfileError,
    ReportsConfig,
    load_profile,
)
from accounting_agent.reports import ReportContext, render_reports

logger = logging.getLogger(__name__)

EXIT_OK = 0
EXIT_ERROR = 1

BookReader = Callable[[Path, str], tuple[Books | None, list[Finding]]]
# One reader per book file format (ADR-006); the profile's `books.format` selects it.
READERS: dict[str, BookReader] = {"front-matter": front_matter.read_books}


def main(argv: Sequence[str] | None = None) -> int:
    """Parse ``argv`` and run the selected command. Returns the process exit code."""
    # A pipe on Windows defaults to the locale's code page; the report has Swedish
    # letters and is read by scripts and AI tools, so it is always UTF-8.
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
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

    report = commands.add_parser(
        "report", help="Write the reports (Swedish Markdown) to the configured folder."
    )
    _add_organisation_arguments(report)
    report.add_argument(
        "--force",
        action="store_true",
        help="Write the reports even if the books have errors.",
    )
    report.set_defaults(handler=_report)

    new_voucher = commands.add_parser(
        "new-voucher",
        help="Create one voucher, for a bank transaction or without one (never "
        "changes a voucher).",
        description="Create one voucher. For a bank transaction: --date and --amount, "
        "and either --account or the lines of the other side with --debit/--credit; "
        "the bank line comes from the bank statement. Without a bank transaction: "
        "--date, --text and every line with --debit/--credit, and no --amount.",
    )
    _add_organisation_arguments(new_voucher)
    new_voucher.add_argument(
        "--date",
        type=_date_argument,
        required=True,
        help="The date, YYYY-MM-DD: the bank transaction's, or the voucher's own.",
    )
    new_voucher.add_argument(
        "--amount",
        type=_amount_argument,
        help="The bank transaction's amount as the bank shows it, e.g. -458 or 200.50. "
        "Leave it out for a voucher without a bank transaction.",
    )
    new_voucher.add_argument(
        "--account",
        type=_account_argument,
        help="The one account to post a bank transaction against.",
    )
    # Both append to the same list, so the lines keep the order they are given in.
    new_voucher.add_argument(
        "--debit",
        dest="lines",
        action="append",
        type=_debit_argument,
        metavar="ACCOUNT=AMOUNT",
        help="A debit line, e.g. 7010=30000; repeatable.",
    )
    new_voucher.add_argument(
        "--credit",
        dest="lines",
        action="append",
        type=_credit_argument,
        metavar="ACCOUNT=AMOUNT",
        help="A credit line, e.g. 2710=9000; repeatable.",
    )
    new_voucher.add_argument(
        "--text",
        default="",
        help="The text of a voucher without a bank transaction.",
    )
    new_voucher.add_argument(
        "--row",
        type=int,
        help="The row in the statement file, when several transactions share the "
        "date and the amount (validate prints it).",
    )
    new_voucher.add_argument(
        "--document",
        action="append",
        default=[],
        metavar="NAME",
        help="A file in the documents folder that supports the voucher; repeatable.",
    )
    new_voucher.add_argument("--note", default="", help="A note for the voucher.")
    new_voucher.add_argument(
        "--guess",
        action="store_true",
        help="Mark the posting as a guess; the note must say why.",
    )
    new_voucher.set_defaults(handler=_new_voucher)
    return parser


def _date_argument(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError("not a date (YYYY-MM-DD)") from None


def _amount_argument(value: str) -> Decimal:
    amount = parse_amount(value)
    if amount is None:
        raise argparse.ArgumentTypeError("not an amount (decimal point, no spaces)")
    return amount


def _account_argument(value: str) -> str:
    if not re.fullmatch(r"\d{4}", value):
        raise argparse.ArgumentTypeError("not an account number (four digits)")
    return value


def _line_amount(value: str) -> tuple[str, Decimal]:
    account, equals, text = value.partition("=")
    amount = parse_amount(text) if equals else None
    if not re.fullmatch(r"\d{4}", account) or amount is None or amount <= 0:
        raise argparse.ArgumentTypeError(
            "not <account>=<amount>: four digits, and a positive amount with a "
            "decimal point and no spaces"
        )
    return account, amount


def _debit_argument(value: str) -> PostingLine:
    account, amount = _line_amount(value)
    return PostingLine(account, debit=amount)


def _credit_argument(value: str) -> PostingLine:
    account, amount = _line_amount(value)
    return PostingLine(account, credit=amount)


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
        findings = findings + _check_all(profile, config, books, args.unbooked)

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


def _check_all(
    profile: OrganisationProfile, config: BooksConfig, books: Books, unbooked: bool
) -> list[Finding]:
    """Every check that applies to the profile, after the books have been read."""
    findings = check_books(books, config.fiscal_year)
    if profile.checks is not None:
        findings += _check_details(profile, profile.checks, config, books)
    if profile.bank is not None:
        findings += _reconcile(profile.bank, config, books, unbooked)
    return findings


def _report(args: argparse.Namespace) -> int:
    profile = _load_matching_profile(args)
    if profile is None:
        return EXIT_ERROR
    if profile.reports is None or profile.books is None:
        missing = "reports" if profile.reports is None else "books"
        logger.error(
            "%s has no '%s' section in organisation.yaml; report needs one.",
            args.config_dir,
            missing,
        )
        return EXIT_ERROR

    config = profile.books
    books, findings = READERS[config.format](config.path, config.bank_account)
    if books is None:
        logger.error(
            "The books could not be read; no reports were written. Run validate for "
            "details."
        )
        return EXIT_ERROR
    # The unbooked transactions are listed so that the to-do report can count them.
    findings = findings + _check_all(profile, config, books, unbooked=True)
    errors = sum(1 for f in findings if f.severity is Severity.ERROR)
    # Reports from broken books mislead (ADR-008).
    if errors and not args.force:
        logger.error(
            "The books have %d errors; no reports were written. Run validate for "
            "details, or use --force.",
            errors,
        )
        return EXIT_ERROR
    if errors:
        logger.warning(
            "Writing reports although the books have %d errors (--force).", errors
        )

    output = profile.reports.output
    context = _report_context(profile, config, profile.reports, findings)
    # The names of unused documents go to the to-do report only, never to the terminal.
    documents = _list_documents(profile.checks)
    if documents is not None:
        used = {name for voucher in books.vouchers for name in voucher.documents}
        context = replace(context, unused_documents=tuple(sorted(documents - used)))
    reports = render_reports(books, context)
    output.mkdir(exist_ok=True)
    for name, text in reports.items():
        write_text_atomically(output / name, text)
        _emit(f"  {name}")
    period_end = max((v.date for v in books.vouchers), default=None)
    _emit(f"Wrote {len(reports)} reports to {output.name}, up to {period_end}.")
    return EXIT_OK


def _report_context(
    profile: OrganisationProfile,
    config: BooksConfig,
    reports: ReportsConfig,
    findings: list[Finding],
) -> ReportContext:
    """The reports' context: names, conventions, fund values and voucher links."""
    fund_values: tuple[FundValue, ...] = ()
    bank = profile.bank
    if bank is not None and bank.fund_value_file is not None:
        values, _ = bank_statement.read_fund_values(bank.fund_value_file)
        fund_values = values or ()
    budget, comments, todo = _supplements_for_reports(profile.checks)
    voucher_folder = None
    if config.format == "front-matter":
        try:
            relative = os.path.relpath(
                config.path / front_matter.VOUCHER_DIR, reports.output
            )
            voucher_folder = Path(relative).as_posix()
        except ValueError:
            # Different drives on Windows: no relative link is possible.
            voucher_folder = None
    return ReportContext(
        organisation_name=reports.organisation_name,
        organisation_number=reports.organisation_number,
        fiscal_year=config.fiscal_year,
        generated_at=datetime.now(),
        bank_account=config.bank_account,
        parking_accounts=profile.conventions.parking_accounts,
        fund_account=bank.fund_account if bank is not None else None,
        fund_values=fund_values,
        voucher_folder=voucher_folder,
        guessed_posting_marker=profile.conventions.guessed_posting_marker,
        no_document_accounts=profile.conventions.no_document_accounts,
        outlay_prefix=profile.conventions.outlay_prefix,
        budget=budget,
        comments=comments,
        todo=todo,
        findings=tuple(findings),
        # The summary appears only when transactions were read and reconciled.
        statement_read=any(f.rule == "bank-summary" for f in findings),
    )


def _supplements_for_reports(
    checks: ChecksConfig | None,
) -> tuple[tuple[BudgetItem, ...], tuple[ClosingComment, ...], tuple[TodoItem, ...]]:
    """The budget, comments and to-do list for the reports (their findings are the
    checks'); a file that is not configured or not readable gives an empty tuple."""
    if checks is None:
        return (), (), ()
    budget = comments = todo = None
    if checks.budget_file is not None:
        budget, _ = supplements.read_budget(checks.budget_file)
    if checks.comments_file is not None:
        comments, _ = supplements.read_comments(checks.comments_file)
    if checks.todo_file is not None:
        todo, _ = supplements.read_todo(checks.todo_file)
    return budget or (), comments or (), todo or ()


def _check_details(
    profile: OrganisationProfile,
    checks: ChecksConfig,
    config: BooksConfig,
    books: Books,
) -> list[Finding]:
    """Run the detail checks and the reference-chart check (ADR-007).

    The documents folder is listed here, so the domain stays free of I/O.
    """
    findings = check_details(
        books,
        config.bank_account,
        parking_accounts=profile.conventions.parking_accounts,
        documents=_list_documents(checks),
        no_document_accounts=profile.conventions.no_document_accounts,
    )
    if checks.reference_chart is not None:
        reference, read_findings = reference_chart.read_reference_chart(
            checks.reference_chart
        )
        findings += read_findings
        if reference is not None:
            findings += check_reference(books.accounts, reference)
    findings += _check_supplements(checks, books)
    return findings


def _list_documents(checks: ChecksConfig | None) -> frozenset[str] | None:
    """The files in the documents folder, relative to it; ``None`` if none is configured."""
    if checks is None or checks.documents is None:
        return None
    return frozenset(
        path.relative_to(checks.documents).as_posix()
        for path in checks.documents.rglob("*")
        if path.is_file()
    )


def _check_supplements(checks: ChecksConfig, books: Books) -> list[Finding]:
    """Budget, closing comments and to-do list; a missing file skips its check."""
    findings: list[Finding] = []
    if checks.budget_file is not None:
        budget, read_findings = supplements.read_budget(checks.budget_file)
        findings += read_findings
        if budget is not None:
            findings += check_budget(budget, books)
    if checks.comments_file is not None:
        comments, read_findings = supplements.read_comments(checks.comments_file)
        findings += read_findings
        if comments is not None:
            findings += check_comments(comments, books)
    if checks.todo_file is not None:
        todo, read_findings = supplements.read_todo(checks.todo_file)
        findings += read_findings
        if todo is not None:
            findings += check_todo(todo)
    return findings


def _reconcile(
    bank: BankConfig, config: BooksConfig, books: Books, unbooked: bool
) -> list[Finding]:
    """Reconcile the books against the statement file, and check the fund value."""
    transactions, findings = bank_statement.read_statement(
        bank.statement_file, config.fiscal_year
    )
    if transactions is not None:
        findings += reconcile(
            books, transactions, config.bank_account, list_unbooked=unbooked
        )
    if bank.fund_account is not None and bank.fund_value_file is not None:
        values, read_findings = bank_statement.read_fund_values(bank.fund_value_file)
        findings += read_findings
        if values is not None:
            findings += check_fund(values, books, bank.fund_account)
    return findings


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


# A bank transaction without a voucher is fixed by creating that voucher, so this one
# error does not stop new-voucher (ADR-009).
FIXED_BY_NEW_VOUCHER = "bank-unbooked"
NOT_CREATED = "No voucher was created"


def _new_voucher(args: argparse.Namespace) -> int:
    profile = _load_matching_profile(args)
    if profile is None:
        return EXIT_ERROR
    config, bank = profile.books, profile.bank
    # Only a voucher for a bank transaction needs the bank statement (MVP-005).
    for_transaction = args.amount is not None
    if config is None or (for_transaction and bank is None):
        logger.error(
            "%s has no '%s' section in organisation.yaml; new-voucher needs one.",
            args.config_dir,
            "books" if config is None else "bank",
        )
        return EXIT_ERROR

    books, read_findings = READERS[config.format](config.path, config.bank_account)
    if books is None:
        logger.error(
            "%s: the books could not be read. Run validate for details.", NOT_CREATED
        )
        return EXIT_ERROR
    before = read_findings + _check_all(profile, config, books, unbooked=False)
    errors = _blocking_errors(before)
    if errors:
        logger.error(
            "%s: the books have %d error(s). Run validate for details.",
            NOT_CREATED,
            len(errors),
        )
        return EXIT_ERROR
    transactions: tuple[BankTransaction, ...] = ()
    texts: dict[int, str] = {}
    if for_transaction and bank is not None:
        read, _ = bank_statement.read_statement(bank.statement_file, config.fiscal_year)
        if read is None:
            logger.error(
                "%s: the bank statement file %s could not be read. Run import-bank "
                "first.",
                NOT_CREATED,
                bank.statement_file.name,
            )
            return EXIT_ERROR
        transactions = read
        texts = bank_statement.read_voucher_texts(bank.statement_file)

    request = VoucherRequest(
        date=args.date,
        amount=args.amount,
        account=args.account,
        row=args.row,
        documents=tuple(args.document),
        note=args.note,
        guess=args.guess,
        lines=tuple(args.lines or ()),
        text=args.text,
    )
    # Messages name rules, dates, amounts and numbers only — never a text or a name.
    try:
        voucher = build_voucher(
            books,
            transactions,
            texts,
            config.bank_account,
            request,
            documents=_list_documents(profile.checks),
            guessed_posting_marker=profile.conventions.guessed_posting_marker,
            fiscal_year=config.fiscal_year,
        )
        voucher = replace(voucher, source=front_matter.voucher_file_name(voucher))
        with_voucher = replace(books, vouchers=(*books.vouchers, voucher))
        after = read_findings + _check_all(
            profile, config, with_voucher, unbooked=False
        )
        added = [finding for finding in after if finding not in before]
        # The safety net: whatever the checks say, a voucher that breaks the books is
        # not written.
        errors = _blocking_errors(added)
        if errors:
            logger.error("%s: it would add %d error(s).", NOT_CREATED, len(errors))
            for finding in errors:
                logger.error("%s", mask_personal_numbers(finding.render()))
            return EXIT_ERROR
        content = front_matter.render_voucher(
            voucher,
            {account.number: account.name for account in books.accounts},
            config.bank_account,
            _link_path(profile.checks, config),
        )
        front_matter.write_voucher(
            config.path / front_matter.VOUCHER_DIR, voucher, content
        )
    except VoucherRefusedError as error:
        logger.error("%s: [%s] %s", NOT_CREATED, error.rule, error)
        return EXIT_ERROR
    except (front_matter.VoucherExistsError, ValueError) as error:
        logger.error("%s: %s", NOT_CREATED, error)
        return EXIT_ERROR

    _emit_created(voucher, config.bank_account, added)
    return EXIT_OK


def _blocking_errors(findings: list[Finding]) -> list[Finding]:
    return [
        finding
        for finding in findings
        if finding.severity is Severity.ERROR and finding.rule != FIXED_BY_NEW_VOUCHER
    ]


def _link_path(checks: ChecksConfig | None, config: BooksConfig) -> str | None:
    """The path from the voucher folder to the documents folder, for the links."""
    if checks is None or checks.documents is None:
        return None
    try:
        relative = os.path.relpath(
            checks.documents, config.path / front_matter.VOUCHER_DIR
        )
    except ValueError:
        # Different drives on Windows: no relative link is possible.
        return None
    return Path(relative).as_posix()


def _emit_created(voucher: Voucher, bank_account: str, added: list[Finding]) -> None:
    """Say what was created: the number, date, amount and accounts — never the text,
    the note or a document's name."""
    # Amounts as the voucher file writes them, so the two can be compared by eye.
    amount = front_matter.format_amount(
        front_matter.voucher_amount(voucher, bank_account)
    )
    rows = [
        f"{'debit' if line.debit else 'credit'} {line.account} "
        f"{front_matter.format_amount(line.debit or line.credit)}"
        for line in voucher.lines
    ]
    if front_matter.is_simple(voucher):
        debit, credit = voucher.lines
        line = f"  {voucher.date}, {amount}, debit {debit.account}, credit {credit.account}"
        rows = []
    else:
        line = f"  {voucher.date}, {amount}, {len(rows)} lines"
    if voucher.documents:
        count = len(voucher.documents)
        line += f", {count} supporting document{'s' if count > 1 else ''}"
    _emit(f"Created voucher {voucher.id} ({voucher.source})")
    _emit(line)
    for row in rows:
        _emit(f"  {row}")
    # Only the warnings that name the new voucher: summaries change with every voucher.
    for finding in added:
        ids = finding.location.removeprefix("voucher ").split(", ")
        if (
            finding.severity is Severity.WARNING
            and finding.location.startswith("voucher ")
            and voucher.id in ids
        ):
            _emit(f"  {finding.render()}")


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
