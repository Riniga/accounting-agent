"""Tests for the checks on the supplementary files, on model objects (ADR-007): fund
value, budget, closing comments and to-do list, as `kontroll.py` checks them.

The allowed values are the core's own format (owner decision 2026-09-26). No message
quotes a budget item's name, a comment or a task.
"""

from datetime import date
from decimal import Decimal

from accounting_agent.books import (
    Account,
    BudgetItem,
    ClosingComment,
    Finding,
    FundValue,
    OpeningBalance,
    PostingLine,
    Severity,
    TodoItem,
    Voucher,
    check_budget,
    check_comments,
    check_fund,
    check_todo,
)
from accounting_agent.books.model import Books

BANK = "1930"
FUND = "1350"
SENSITIVE = "Hemlig Exempelperson"
ACCOUNTS = (
    Account(FUND, "Fund"),
    Account(BANK, "Bank"),
    Account("2010", "Equity"),
    Account("3001", "Training fees"),
    Account("3002", "Membership fees"),
    Account("5010", "Rent"),
    Account("6570", "Bank charges"),
)


def voucher(number: int, debit: str, credit: str) -> Voucher:
    value = Decimal("200.00")
    return Voucher(
        series=None,
        number=number,
        date=date(2026, 1, number),
        text="Text",
        lines=(PostingLine(debit, debit=value), PostingLine(credit, credit=value)),
    )


BOOKS = Books(
    accounts=ACCOUNTS,
    opening_balances=(
        OpeningBalance(FUND, Decimal("10000.00")),
        OpeningBalance("2010", Decimal("-10000.00")),
    ),
    vouchers=(voucher(1, BANK, "3002"), voucher(2, "5010", BANK)),
)


# --- Fund value -------------------------------------------------------------------------


def fund(day: str, value: str) -> FundValue:
    return FundValue(date=date.fromisoformat(day), value=Decimal(value))


def test_latest_market_value_is_compared_with_the_booked_value() -> None:
    values = (fund("2026-09-19", "12500.00"), fund("2026-08-31", "12345.67"))

    assert check_fund(values, BOOKS, FUND) == [
        Finding(
            Severity.INFO,
            "fund-value",
            f"account {FUND}",
            "market value 12500.00 (2026-09-19), booked 10000.00, difference 2500.00 "
            "(change in value not booked)",
        )
    ]


def test_fund_account_without_postings_is_booked_at_zero() -> None:
    findings = check_fund((fund("2026-09-19", "100.00"),), BOOKS, "1380")

    assert "booked 0, difference 100.00" in findings[0].message


def test_no_fund_values_give_no_findings() -> None:
    assert check_fund((), BOOKS, FUND) == []


# --- Budget -----------------------------------------------------------------------------


def item(
    kind: str,
    accounts: tuple[str, ...],
    amount: str | None,
    row: int = 2,
    name: str = "Item",
) -> BudgetItem:
    return BudgetItem(
        kind=kind,
        name=name,
        accounts=accounts,
        amount=None if amount is None else Decimal(amount),
        note="",
        row=row,
    )


BUDGET = (
    item("intäkt", ("3002", "3001"), "3000", row=2),
    item("kostnad", ("5010",), "6000", row=3),
    item("kostnad", ("6570",), "200", row=4),
)
BUDGET_SUMMARY = Finding(
    Severity.INFO,
    "budget-summary",
    "budget",
    "budgeted revenue 3000, costs 6200, result -3200",
)


def test_consistent_budget_gives_only_the_summary() -> None:
    assert check_budget(BUDGET, BOOKS) == [BUDGET_SUMMARY]


def test_unknown_budget_type_is_an_error() -> None:
    findings = check_budget((*BUDGET, item("övrigt", (), "10", row=5)), BOOKS)

    assert (
        Finding(
            Severity.ERROR,
            "budget-type",
            "budget row 5",
            "unknown type; must be intäkt or kostnad",
        )
        in findings
    )


def test_item_without_a_valid_amount_is_left_out_of_the_totals() -> None:
    # The reader reports the invalid amount; the check only skips it.
    findings = check_budget((*BUDGET, item("kostnad", (), None, row=5)), BOOKS)

    assert findings == [BUDGET_SUMMARY]


def test_budget_account_not_in_the_chart_is_an_error() -> None:
    findings = check_budget((*BUDGET, item("kostnad", ("4999",), "1", row=5)), BOOKS)

    assert (
        Finding(
            Severity.ERROR,
            "budget-unknown-account",
            "budget row 5",
            "account 4999 is not in the chart of accounts",
        )
        in findings
    )


def test_account_on_two_budget_items_is_an_error() -> None:
    findings = check_budget((*BUDGET, item("kostnad", ("5010",), "1", row=5)), BOOKS)

    assert (
        Finding(
            Severity.ERROR,
            "budget-account-twice",
            "budget row 5",
            "account 5010 is already on budget row 3",
        )
        in findings
    )


def test_account_that_does_not_fit_the_type_is_an_error() -> None:
    findings = check_budget((item("kostnad", ("3001",), "1"),), BOOKS)

    assert (
        Finding(
            Severity.ERROR,
            "budget-account-type",
            "budget row 2",
            "account 3001 does not fit the type kostnad",
        )
        in findings
    )


# --- Closing comments -------------------------------------------------------------------


def comment(
    id_: str,
    kind: str = "princip",
    accounts: tuple[str, ...] = (),
    vouchers: tuple[str, ...] = (),
    text: str = "A principle.",
    row: int = 2,
) -> ClosingComment:
    return ClosingComment(
        id=id_,
        date=date(2026, 3, 1),
        kind=kind,
        accounts=accounts,
        vouchers=vouchers,
        text=text,
        row=row,
    )


COMMENTS = (
    comment("1"),
    comment("2", kind="händelse", accounts=("3002",), vouchers=("1", "2"), row=3),
)
COMMENTS_SUMMARY = Finding(
    Severity.INFO, "comments-summary", "closing comments", "2 closing comments"
)


def test_consistent_comments_give_only_the_summary() -> None:
    assert check_comments(COMMENTS, BOOKS) == [COMMENTS_SUMMARY]


def test_comment_ids_must_run_without_gaps() -> None:
    findings = check_comments((comment("1"), comment("3", row=3)), BOOKS)

    assert (
        Finding(
            Severity.ERROR,
            "comment-id",
            "closing comment 3",
            "id should be 2 (a sequence without gaps)",
        )
        in findings
    )


def test_unknown_comment_type_is_an_error() -> None:
    findings = check_comments((comment("1", kind="annat"),), BOOKS)

    assert (
        Finding(
            Severity.ERROR,
            "comment-type",
            "closing comment 1",
            "unknown type; allowed: avstämning, händelse, not, princip, revisor, rättelse",
        )
        in findings
    )


def test_comment_on_an_unknown_account_or_voucher_is_an_error() -> None:
    findings = check_comments(
        (comment("1", accounts=("4999",), vouchers=("9",)),), BOOKS
    )

    assert (
        Finding(
            Severity.ERROR,
            "comment-unknown-account",
            "closing comment 1",
            "account 4999 is not in the chart of accounts",
        )
        in findings
    )
    assert (
        Finding(
            Severity.ERROR,
            "comment-unknown-voucher",
            "closing comment 1",
            "voucher 9 does not exist",
        )
        in findings
    )


def test_empty_comment_is_an_error() -> None:
    findings = check_comments((comment("1", text="  "),), BOOKS)

    assert (
        Finding(
            Severity.ERROR,
            "comment-missing-text",
            "closing comment 1",
            "the comment is empty",
        )
        in findings
    )


def test_personal_number_in_a_comment_is_a_warning() -> None:
    findings = check_comments((comment("1", text="Refund to 19121212-1212"),), BOOKS)

    assert (
        Finding(
            Severity.WARNING,
            "personal-number",
            "closing comment 1",
            "the comment appears to contain a personal identity number",
        )
        in findings
    )


# --- To-do list -------------------------------------------------------------------------


def task(
    id_: str,
    owner: str = "kassör",
    when: str = "nu",
    status: str = "öppen",
    depends_on: str = "",
    task_text: str = "Hand in receipts",
    done_when: str = "All receipts are in",
    row: int = 2,
) -> TodoItem:
    return TodoItem(
        id=id_,
        owner=owner,
        when=when,
        area="documents",
        task=task_text,
        done_when=done_when,
        status=status,
        depends_on=depends_on,
        row=row,
    )


TODO = (
    task("T1"),
    task("T2", owner="vi", status="klar", row=3),
    task("T3", owner="vi", when="bokslut", status="väntar", depends_on="T1", row=4),
)
TODO_SUMMARY = Finding(
    Severity.INFO,
    "todo-summary",
    "to-do list",
    "2 of 3 tasks are not done (kassör 1, vi 1)",
)


def test_consistent_todo_list_gives_only_the_summary() -> None:
    assert check_todo(TODO) == [TODO_SUMMARY]


def test_duplicate_task_id_is_an_error_on_each_row() -> None:
    findings = check_todo((*TODO, task("T1", row=5)))

    duplicates = [f for f in findings if f.rule == "todo-duplicate-id"]
    assert len(duplicates) == 2
    assert duplicates[0] == Finding(
        Severity.ERROR, "todo-duplicate-id", "to-do T1", "id appears more than once"
    )


def test_unknown_owner_when_and_status_are_errors() -> None:
    findings = check_todo(
        (task("T1", owner="styrelsen", when="snart", status="klart"),)
    )

    assert [(f.rule, f.message) for f in findings if f.severity is Severity.ERROR] == [
        ("todo-owner", "unknown owner; allowed: kassör, vi"),
        ("todo-when", "unknown value for när; allowed: bokslut, nu"),
        ("todo-status", "unknown status; allowed: klar, väntar, öppen"),
    ]


def test_dependency_on_an_unknown_task_is_an_error() -> None:
    findings = check_todo((task("T1", depends_on="T9"),))

    assert (
        Finding(
            Severity.ERROR,
            "todo-dependency",
            "to-do T1",
            "depends on T9, which does not exist",
        )
        in findings
    )


def test_task_without_text_or_done_criterion_is_an_error() -> None:
    findings = check_todo((task("T1", done_when=" "),))

    assert (
        Finding(
            Severity.ERROR,
            "todo-missing-text",
            "to-do T1",
            "uppgift and klart_när must be filled in",
        )
        in findings
    )


def test_waiting_without_a_dependency_is_a_warning() -> None:
    findings = check_todo((task("T1", status="väntar"),))

    assert (
        Finding(
            Severity.WARNING,
            "todo-waiting",
            "to-do T1",
            "status väntar but no dependency",
        )
        in findings
    )


# --- No message quotes data -------------------------------------------------------------


def test_no_message_quotes_a_name_a_comment_or_a_task() -> None:
    findings = [
        *check_budget((item("övrigt", ("4999",), "1", name=SENSITIVE),), BOOKS),
        *check_comments(
            (comment("2", kind="x", text=SENSITIVE + " 19121212-1212"),), BOOKS
        ),
        *check_todo((task("T1", owner="x", task_text=SENSITIVE, done_when=""),)),
    ]

    assert len(findings) >= 6
    for finding in findings:
        assert SENSITIVE not in finding.render()
