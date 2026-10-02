"""The overview reports (ADR-008): budget follow-up, closing comments, the to-do report
and the summary — Swedish Markdown, as Helsingborgs Judoklubb's
`generera_redovisning.py` renders them, without its member parts (MVP-003, out of scope).

Comment and task texts outside tables are masked here; tables mask their own cells.
"""

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from accounting_agent.books import Books, Severity, TodoItem, Voucher
from accounting_agent.books.masking import FILE_MASK, mask_personal_numbers
from accounting_agent.books.supplements import COST, REVENUE, WAITING
from accounting_agent.reports.accounts import (
    latest_fund_value,
    render_balance_sheet,
    render_general_ledger,
    render_income_statement,
    render_monthly_overview,
    render_voucher_list,
    voucher_link,
)
from accounting_agent.reports.format import (
    ReportContext,
    bold,
    format_amount,
    render_header,
    table,
)
from accounting_agent.reports.ledger import COST_CLASSES, REVENUE_CLASSES, Ledger

ZERO = Decimal(0)
COMMENT_HEADINGS = {
    "princip": "Redovisningsprinciper",
    "händelse": "Väsentliga händelser",
    "not": "Noter",
    "avstämning": "Avstämningar",
    "rättelse": "Rättelser",
    "revisor": "Revisorns anmärkningar",
}
OWNERS = (("kassör", "Du (kassören)"), ("vi", "Vi (skript och agent)"))
WHEN = (("nu", "nu"), ("bokslut", "vid bokslut"))
EQUITY_GROUP = "EGET KAPITAL"
# BAS group 20 is equity, for a chart without a group column.
EQUITY_PREFIX = "20"
REPORT_LINKS = (
    (
        "resultatrapport.md",
        "Resultatrapport",
        "Intäkter och kostnader per konto, resultat hittills",
    ),
    (
        "balansrapport.md",
        "Balansrapport",
        "Tillgångar, eget kapital och skulder, ingående och utgående",
    ),
    ("budgetuppföljning.md", "Budgetuppföljning", "Utfall mot budget per post"),
    (
        "månadsöversikt.md",
        "Månadsöversikt",
        "Intäkter, kostnader, resultat och banksaldo per månad",
    ),
    ("huvudbok.md", "Huvudbok", "Saldobalans och alla händelser per konto"),
    (
        "verifikationslista.md",
        "Verifikationslista",
        "Alla verifikationer med länk till respektive fil",
    ),
    (
        "att-göra.md",
        "Att göra",
        "Vad du och vi har att göra för att vara nöjda, med krav och listor",
    ),
    ("bokslutskommentarer.md", "Bokslutskommentarer", "Kommentarer till redovisningen"),
)


def render_reports(books: Books, context: ReportContext) -> dict[str, str]:
    """Every report, by file name, in the script's order; each ends with one newline.

    The budget follow-up is left out when there is no budget.
    """
    reports: dict[str, str | None] = {
        "sammanfattning.md": render_summary(books, context),
        "att-göra.md": render_todo(books, context),
        "resultatrapport.md": render_income_statement(books, context),
        "balansrapport.md": render_balance_sheet(books, context),
        "budgetuppföljning.md": render_budget_follow_up(books, context),
        "månadsöversikt.md": render_monthly_overview(books, context),
        "huvudbok.md": render_general_ledger(books, context),
        "verifikationslista.md": render_voucher_list(books, context),
        "bokslutskommentarer.md": render_closing_comments(books, context),
    }
    # Voucher texts appear only in table cells, which table() masks. The rest is not
    # masked as a whole: an organisation number has the same shape as a personal number.
    return {
        name: text.rstrip("\n") + "\n"
        for name, text in reports.items()
        if text is not None
    }


def _masked(text: str) -> str:
    return mask_personal_numbers(text, mask=FILE_MASK)


def _share_of_year(period_end: date) -> Decimal:
    days = (period_end - date(period_end.year, 1, 1)).days + 1
    return Decimal(days) / Decimal(366 if calendar.isleap(period_end.year) else 365)


def _percent(part: Decimal, whole: Decimal) -> str:
    return format_amount(part / whole * 100, 0) + " %" if whole else "–"


# --- Budget follow-up -------------------------------------------------------------------


def render_budget_follow_up(books: Books, context: ReportContext) -> str | None:
    """Outcome against budget per item; None when there is no budget."""
    if not context.budget:
        return None
    ledger = Ledger(books, context.fiscal_year)
    out = [render_header("Budgetuppföljning", context, ledger.period_end)]
    share = _share_of_year(ledger.period_end)
    out.append(
        f"Budget {context.fiscal_year} mot bokfört utfall. "
        f"**{format_amount(share * 100, 0)} % av året har gått** (till "
        f"{ledger.period_end}). Ligger utfallet i jämn takt är det ungefär lika stor "
        "andel av budgeten.\n"
    )
    budgeted: set[str] = set()

    def section(title: str, kind: str, sign: int) -> tuple[Decimal, Decimal]:
        # The outcome is shown positive: revenue credit minus debit, costs the reverse.
        rows: list[list[str]] = []
        total_budget = total_outcome = ZERO
        for item in (i for i in context.budget if i.kind == kind):
            budgeted.update(item.accounts)
            amount = item.amount if item.amount is not None else ZERO
            outcome = sum(
                (sign * ledger.movement.get(a, ZERO) for a in item.accounts), ZERO
            )
            rows.append(
                [
                    item.name,
                    format_amount(amount),
                    format_amount(outcome),
                    format_amount(amount - outcome),
                    _percent(outcome, amount),
                ]
            )
            total_budget += amount
            total_outcome += outcome
        classes = REVENUE_CLASSES if kind == REVENUE else COST_CLASSES
        for account in ledger.result_accounts(classes):
            if account in budgeted:
                continue
            outcome = sign * ledger.movement.get(account, ZERO)
            rows.append(
                [
                    f"*Ej budgeterat: {account} {ledger.name(account)}*",
                    format_amount(ZERO),
                    format_amount(outcome),
                    format_amount(-outcome),
                    "–",
                ]
            )
            total_outcome += outcome
        rows.append(
            [
                bold("Summa"),
                bold(format_amount(total_budget)),
                bold(format_amount(total_outcome)),
                bold(format_amount(total_budget - total_outcome)),
                bold(_percent(total_outcome, total_budget)),
            ]
        )
        out.append(f"## {title}\n")
        headers = [
            "Post",
            "Budget helår",
            "Utfall hittills",
            "Kvar av budget",
            "Utfall i % av budget",
        ]
        out.append(table(headers, rows, right=(1, 2, 3, 4)) + "\n")
        return total_budget, total_outcome

    revenue_budget, revenue = section("Intäkter", REVENUE, -1)
    cost_budget, costs = section("Kostnader", COST, +1)
    out.append("## Resultat\n")
    out.append(
        table(
            ["", "Budget helår", "Utfall hittills"],
            [
                ["Intäkter", format_amount(revenue_budget), format_amount(revenue)],
                ["Kostnader", format_amount(cost_budget), format_amount(costs)],
                [
                    bold("Resultat"),
                    bold(format_amount(revenue_budget - cost_budget)),
                    bold(format_amount(revenue - costs)),
                ],
            ],
            right=(1, 2),
        )
        + "\n"
    )
    footer = "Budgetposternas kontokoppling finns i budgetfilen."
    if context.parking_accounts:
        footer += (
            f" Intäkterna på konto {', '.join(context.parking_accounts)} är ännu inte "
            "fördelade och redovisas därför som *ej budgeterat*."
        )
    out.append(footer + "\n")
    return "\n".join(out)


# --- Closing comments -------------------------------------------------------------------


def render_closing_comments(books: Books, context: ReportContext) -> str:
    """The closing comments, grouped by type."""
    ledger = Ledger(books, context.fiscal_year)
    out = [render_header("Bokslutskommentarer", context, ledger.period_end)]
    out.append(
        "Kommentarer som samlats löpande under året och som ska med i "
        "årsredovisningen.\n"
    )
    if not context.comments:
        out.append("Inga kommentarer.\n")
    for kind, heading in COMMENT_HEADINGS.items():
        comments = [c for c in context.comments if c.kind == kind]
        if not comments:
            continue
        out.append(f"## {heading}\n")
        for comment in comments:
            references = []
            if comment.accounts:
                references.append(
                    "konto "
                    + ", ".join(f"{a} {ledger.name(a)}" for a in comment.accounts)
                )
            if comment.vouchers:
                references.append(
                    "verifikation "
                    + ", ".join(
                        str(int(v)) if v.isdigit() else v for v in comment.vouchers
                    )
                )
            mark = f" ({'; '.join(references)})" if references else ""
            day = comment.date if comment.date is not None else "–"
            out.append(_masked(f"- **{day}**{mark}: {comment.text}"))
        out.append("")
    return "\n".join(out)


# --- The measures and the to-do report --------------------------------------------------


@dataclass(frozen=True)
class Measure:
    """One requirement for being satisfied with the books right now."""

    goal: str
    now: str
    target: str
    met: bool


def _bank_amount(voucher: Voucher, bank_account: str) -> Decimal:
    return sum(
        (
            line.debit - line.credit
            for line in voucher.lines
            if line.account == bank_account
        ),
        ZERO,
    )


def _guessed(books: Books, context: ReportContext) -> list[Voucher]:
    marker = context.guessed_posting_marker
    if not marker:
        return []
    return [
        v
        for v in books.vouchers
        if v.note.lstrip().startswith(marker) or f"\n{marker}" in v.note
    ]


def _payments_without_documents(books: Books, context: ReportContext) -> list[Voucher]:
    """Money out of the bank without documents, except the accounts that need none."""
    return [
        v
        for v in books.vouchers
        if _bank_amount(v, context.bank_account) < ZERO
        and not v.documents
        and not any(
            line.debit > ZERO and line.account in context.no_document_accounts
            for line in v.lines
        )
    ]


def _is_outlay(voucher: Voucher, context: ReportContext) -> bool:
    prefix = context.outlay_prefix
    return bool(prefix) and voucher.text.lower().startswith(prefix.lower())


def _measures(books: Books, context: ReportContext) -> list[Measure]:
    errors = [f for f in context.findings if f.severity is Severity.ERROR]
    unbooked = sum(1 for f in context.findings if f.rule == "unbooked")
    bank_matches = not any(f.rule.startswith("bank-") for f in errors)
    measures = [
        Measure("Kontrollen ger inga fel", f"{len(errors)} fel", "0 fel", not errors),
        Measure(
            "Alla banktransaktioner är bokförda",
            f"{unbooked} obokförda",
            "0 obokförda",
            unbooked == 0,
        ),
        Measure(
            "Bankens saldo stämmer med bokföringen",
            "stämmer" if bank_matches else "stämmer inte",
            "stämmer",
            bank_matches,
        ),
    ]
    if context.parking_accounts:
        parked = [
            v
            for v in books.vouchers
            if any(line.account in context.parking_accounts for line in v.lines)
        ]
        measures.append(
            Measure(
                f"Inga poster ligger parkerade på {', '.join(context.parking_accounts)}",
                f"{len(parked)} poster",
                "0 poster",
                not parked,
            )
        )
    if context.guessed_posting_marker:
        guessed = _guessed(books, context)
        measures.append(
            Measure(
                "Inga gissade konteringar återstår",
                f"{len(guessed)} verifikationer",
                "0 verifikationer",
                not guessed,
            )
        )
    without = _payments_without_documents(books, context)
    goal = "Alla utbetalningar har underlag"
    if context.no_document_accounts:
        goal += f" (utom konto {', '.join(context.no_document_accounts)})"
    now = f"{len(without)} saknar"
    if context.outlay_prefix:
        now += f", varav {sum(1 for v in without if _is_outlay(v, context))} utlägg"
    measures.append(Measure(goal, now, "0 saknar", not without))
    return measures


def _measure_table(measures: list[Measure]) -> str:
    return table(
        ["Krav", "Nuläge", "Mål", "Klart"],
        [[m.goal, m.now, m.target, "✓" if m.met else "✗"] for m in measures],
    )


def _open_tasks(context: ReportContext, owner: str, when: str) -> list[TodoItem]:
    return [
        t
        for t in context.todo
        if t.owner == owner and t.when == when and t.status != "klar"
    ]


def render_todo(books: Books, context: ReportContext) -> str:
    """What the treasurer and the tools have to do: measures, tasks and the lists."""
    ledger = Ledger(books, context.fiscal_year)
    out = [render_header("Att göra för att vara nöjda", context, ledger.period_end)]
    measures = _measures(books, context)
    met = sum(1 for m in measures if m.met)
    out.append(
        "Här står vad **du (kassören)** och **vi** (skript och agent) har att göra. "
        "Listan kommer från att-göra-listan, och kraven nedan räknas ut ur bokföringen "
        "varje gång rapporterna skapas.\n"
    )
    out.append("## När är vi nöjda?\n")
    out.append(
        "- **Nöjda med läget just nu** när alla krav nedan är ✓ och alla uppgifter "
        "markerade *nu* är klara.\n"
        "- **Nöjda med året** när dessutom uppgifterna markerade *bokslut* är klara och "
        "rapporterna har lämnats till revisorn.\n"
    )
    out.append(f"## Krav just nu ({met} av {len(measures)} uppfyllda)\n")
    out.append(_measure_table(measures) + "\n")
    for owner, owner_heading in OWNERS:
        for when, when_heading in WHEN:
            tasks = _open_tasks(context, owner, when)
            out.append(f"## {owner_heading}: uppgifter {when_heading} ({len(tasks)})\n")
            if not tasks:
                out.append("Inga uppgifter.\n")
                continue
            rows = [
                [
                    t.id,
                    t.area,
                    t.task,
                    t.done_when,
                    f"väntar på {t.depends_on}" if t.status == WAITING else "öppen",
                ]
                for t in tasks
            ]
            out.append(
                table(["ID", "Område", "Uppgift", "Klart när", "Status"], rows) + "\n"
            )

    out.append("## Underlag till uppgifterna\n")
    if context.guessed_posting_marker:
        out += _guessed_section(books, context, ledger)
    out += _without_documents_section(books, context, ledger)
    return "\n".join(out)


def _guessed_section(books: Books, context: ReportContext, ledger: Ledger) -> list[str]:
    marker = context.guessed_posting_marker or ""
    guessed = _guessed(books, context)
    section = [f"### Gissade konteringar ({len(guessed)})\n"]
    if not guessed:
        return [*section, "Inga.\n"]
    rows = []
    for voucher in guessed:
        note = " ".join(voucher.note.split())
        debits = "; ".join(line.account for line in voucher.lines if line.debit)
        credits = "; ".join(line.account for line in voucher.lines if line.credit)
        accounts = f"{debits} / {credits}"
        rows.append(
            [
                voucher_link(voucher, context),
                str(voucher.date),
                format_amount(voucher.total_debit),
                accounts,
                note[note.find(marker) :][:200],
            ]
        )
    headers = ["Ver", "Datum", "Belopp", "Debet / kredit", "Skäl"]
    return [*section, table(headers, rows, right=(2,)) + "\n"]


def _without_documents_section(
    books: Books, context: ReportContext, ledger: Ledger
) -> list[str]:
    without = _payments_without_documents(books, context)
    section = [f"### Utbetalningar utan underlag ({len(without)})\n"]
    if not without:
        return [*section, "Inga.\n"]
    intro = []
    if context.outlay_prefix:
        intro.append("Utläggen först, eftersom de är den vanligaste anmärkningen.")
    if context.no_document_accounts:
        intro.append(
            f"Konto {', '.join(context.no_document_accounts)} behöver inget underlag."
        )
    if intro:
        section.append(" ".join(intro) + "\n")
    ordered = sorted(without, key=lambda v: (not _is_outlay(v, context), v.date))
    rows = [
        [
            voucher_link(v, context),
            str(v.date),
            format_amount(-_bank_amount(v, context.bank_account)),
            "; ".join(
                f"{line.account} {ledger.name(line.account)}"
                for line in v.lines
                if line.debit > ZERO
            ),
            v.text,
        ]
        for v in ordered
    ]
    headers = ["Ver", "Datum", "Belopp", "Konto", "Bankens text"]
    return [*section, table(headers, rows, right=(2,)) + "\n"]


# --- Summary ----------------------------------------------------------------------------


def _is_equity(ledger: Ledger, account: str) -> bool:
    group = ledger.accounts[account].group
    if group:
        return group.upper() == EQUITY_GROUP
    return account.startswith(EQUITY_PREFIX)


def render_summary(books: Books, context: ReportContext) -> str:
    """The position in figures, against budget, what to do, the checks and the links."""
    ledger = Ledger(books, context.fiscal_year)
    out = [
        render_header("Sammanfattning: läget i ekonomin", context, ledger.period_end)
    ]
    out += _figures(ledger, context)
    if context.budget:
        out += _against_budget(ledger, context)
    out += _what_to_do(books, context)
    out += _check_result(context)
    out.append("## Rapporter\n")
    rows = [
        [f"[{title}]({name})", content]
        for name, title, content in REPORT_LINKS
        if context.budget or name != "budgetuppföljning.md"
    ]
    out.append(table(["Rapport", "Innehåll"], rows) + "\n")
    return "\n".join(out)


def _figures(ledger: Ledger, context: ReportContext) -> list[str]:
    bank = context.bank_account
    errors = [f for f in context.findings if f.severity is Severity.ERROR]
    reconciled = context.statement_read and not any(
        f.rule.startswith("bank-") for f in errors
    )
    rows = [
        [
            f"Banksaldo ({bank})",
            format_amount(ledger.closing(bank)),
            "Stämmer mot bankens kontoutdrag"
            if reconciled
            else "Ej avstämt mot banken",
        ]
    ]
    fund_account = context.fund_account
    if fund_account is not None:
        booked = ledger.closing(fund_account)
        rows.append(
            [f"Fond ({fund_account}), bokfört värde", format_amount(booked), ""]
        )
        fund = latest_fund_value(context)
        if fund is not None:
            rows.append(
                [
                    f"Fond ({fund_account}), marknadsvärde",
                    format_amount(fund.value),
                    f"per {fund.date}, värdeförändring "
                    f"{format_amount(fund.value - booked)} kr ej bokförd",
                ]
            )

    equity = [a for a in ledger.balance_accounts("2") if _is_equity(ledger, a)]
    debts = [a for a in ledger.balance_accounts("2") if not _is_equity(ledger, a)]
    equity_start = -sum((ledger.opening.get(a, ZERO) for a in equity), ZERO)
    equity_now = -sum((ledger.closing(a) for a in equity), ZERO) + ledger.result
    liabilities = -sum((ledger.closing(a) for a in debts), ZERO)
    assets = sum((ledger.closing(a) for a in ledger.balance_accounts("1")), ZERO)
    rows += [
        ["Intäkter hittills i år", format_amount(ledger.revenue), ""],
        ["Kostnader hittills i år", format_amount(-ledger.costs), ""],
        [
            bold("Resultat hittills i år"),
            bold(format_amount(ledger.result)),
            "före värdeförändring på fonden",
        ],
        ["Eget kapital vid årets början", format_amount(equity_start), ""],
        [
            "Eget kapital nu (inklusive resultat hittills)",
            format_amount(equity_now),
            "",
        ],
        ["Skulder", format_amount(liabilities), ""],
        [
            "Summa tillgångar",
            format_amount(assets),
            "lika med eget kapital plus skulder"
            if assets == equity_now + liabilities
            else "STÄMMER INTE med eget kapital plus skulder",
        ],
    ]
    return [
        "## Läget i siffror\n",
        table(["", "Belopp (kr)", "Kommentar"], rows, right=(1,)) + "\n",
    ]


def _against_budget(ledger: Ledger, context: ReportContext) -> list[str]:
    def total(kind: str) -> Decimal:
        return sum(
            (
                i.amount
                for i in context.budget
                if i.kind == kind and i.amount is not None
            ),
            ZERO,
        )

    share = _share_of_year(ledger.period_end)
    return [
        "## Mot budget\n",
        f"{format_amount(share * 100, 0)} % av året har gått. Intäkterna är "
        f"{format_amount(ledger.revenue)} kr mot budget "
        f"{format_amount(total(REVENUE))} kr, kostnaderna "
        f"{format_amount(ledger.costs)} kr mot budget {format_amount(total(COST))} kr. "
        "Se [budgetuppföljning](budgetuppföljning.md).\n",
    ]


def _what_to_do(books: Books, context: ReportContext) -> list[str]:
    measures = _measures(books, context)
    met = sum(1 for m in measures if m.met)
    out = [
        "## Att åtgärda\n",
        "Vi är **nöjda med läget just nu** när alla krav nedan är ✓ och alla uppgifter "
        f"markerade *nu* är klara. Just nu är **{met} av {len(measures)} krav** "
        "uppfyllda. Vi är nöjda med **året** när även uppgifterna vid bokslut är "
        "klara.\n",
        _measure_table(measures) + "\n",
    ]
    for owner, heading in OWNERS:
        now = _open_tasks(context, owner, "nu")
        at_closing = _open_tasks(context, owner, "bokslut")
        out.append(
            f"### {heading}: {len(now)} uppgifter nu, {len(at_closing)} vid bokslut\n"
        )
        out += [
            _masked(
                f"- **{t.id}** ({t.area}): {t.task}"
                + (f" *(väntar på {t.depends_on})*" if t.status == WAITING else "")
            )
            for t in now
        ]
        out.append("")
    out.append(
        "Alla uppgifter, klart-kriterier och listor över berörda verifikationer finns "
        "i [att-göra](att-göra.md).\n"
    )
    return out


def _check_result(context: ReportContext) -> list[str]:
    errors = [f for f in context.findings if f.severity is Severity.ERROR]
    warnings = [f for f in context.findings if f.severity is Severity.WARNING]
    out = [
        "## Kontroll av bokföringen\n",
        f"Kontrollen ger **{'FEL' if errors else 'OK'}** ({len(errors)} fel, "
        f"{len(warnings)} varningar).\n",
    ]
    # Findings never quote voucher texts or names, so they can be listed as they are.
    out += [_masked(f"- {f.location}: {f.message}") for f in warnings]
    out.append("")
    return out
