"""The accounts reports (ADR-008): income statement, balance sheet, general ledger,
voucher list and monthly overview — Swedish Markdown, as Helsingborgs Judoklubb's
`generera_redovisning.py` renders them, from the general book model.
"""

from decimal import Decimal

from accounting_agent.books import Books, FundValue, Voucher
from accounting_agent.reports.format import (
    ReportContext,
    bold,
    format_amount,
    render_header,
    table,
)
from accounting_agent.reports.ledger import COST_CLASSES, REVENUE_CLASSES, Ledger

ZERO = Decimal(0)
MONTHS = [
    "januari",
    "februari",
    "mars",
    "april",
    "maj",
    "juni",
    "juli",
    "augusti",
    "september",
    "oktober",
    "november",
    "december",
]
NOTE_LENGTH = 170


def render_income_statement(books: Books, context: ReportContext) -> str:
    """Revenue, costs and financial items per account group, and the result so far."""
    ledger = Ledger(books, context.fiscal_year)
    out = [render_header("Resultatrapport", context, ledger.period_end)]

    def section(title: str, accounts: list[str]) -> Decimal:
        out.append(f"## {title}\n")
        if not accounts:
            out.append("Inga poster.\n")
            return ZERO
        rows: list[list[str]] = []
        total = ZERO
        for group, members in ledger.groups(accounts):
            subtotal = ZERO
            rows.append([bold(group), "", ""])
            for account in members:
                amount = -ledger.movement[account]
                subtotal += amount
                rows.append([account, ledger.name(account), format_amount(amount)])
            rows.append(
                ["", bold(f"Summa {group.lower()}"), bold(format_amount(subtotal))]
            )
            total += subtotal
        out.append(table(["Konto", "Benämning", "Belopp"], rows, right=(2,)) + "\n")
        return total

    revenue = section("Rörelsens intäkter", ledger.result_accounts(REVENUE_CLASSES))
    costs = section("Rörelsens kostnader", ledger.result_accounts("4567"))
    financial = section("Finansiella poster", ledger.result_accounts("8"))
    operating = revenue + costs
    out.append("## Resultat\n")
    out.append(
        table(
            ["", "Belopp"],
            [
                ["Summa intäkter", format_amount(revenue)],
                ["Summa kostnader", format_amount(costs)],
                [bold("Rörelseresultat"), bold(format_amount(operating))],
                ["Finansiella poster", format_amount(financial)],
                [
                    bold("Resultat hittills i år"),
                    bold(format_amount(operating + financial)),
                ],
            ],
            right=(1,),
        )
        + "\n"
    )
    for account in context.parking_accounts:
        parked = ledger.movement.get(account, ZERO)
        if parked:
            out.append(
                f"> **Konto {account} ({ledger.name(account)})** innehåller "
                f"{format_amount(-parked)} kr av intäkterna. Det är inbetalningar som "
                "ännu inte fördelats på rätt intäktskonto, så fördelningen mellan "
                "intäktsslagen är preliminär.\n"
            )
    fund = latest_fund_value(context)
    if fund is not None and context.fund_account is not None:
        booked = ledger.closing(context.fund_account)
        out.append(
            f"> **Ej bokfört:** Fondens marknadsvärde är {format_amount(fund.value)} kr "
            f"({fund.date}) mot bokfört värde {format_amount(booked)} kr. "
            f"Värdeförändringen, {format_amount(fund.value - booked)} kr, bokförs vid "
            "bokslut och ingår inte i resultatet ovan.\n"
        )
    return "\n".join(out)


def render_balance_sheet(books: Books, context: ReportContext) -> str:
    """Assets, equity and liabilities: opening, change and closing per account."""
    ledger = Ledger(books, context.fiscal_year)
    out = [render_header("Balansrapport", context, ledger.period_end)]

    def section(
        title: str, accounts: list[str], sign: int, extra: list[list[str]]
    ) -> Decimal:
        # sign +1: assets (debit positive); -1: equity and liabilities (credit positive).
        out.append(f"## {title}\n")
        rows: list[list[str]] = []
        closing_total = ZERO
        for group, members in ledger.groups(accounts):
            group_opening = group_closing = ZERO
            rows.append([bold(group), "", "", "", ""])
            for account in members:
                opening = sign * ledger.opening.get(account, ZERO)
                closing = sign * ledger.closing(account)
                group_opening += opening
                group_closing += closing
                rows.append(
                    [
                        account,
                        ledger.name(account),
                        format_amount(opening),
                        format_amount(closing - opening),
                        format_amount(closing),
                    ]
                )
            rows.append(
                [
                    "",
                    bold(f"Summa {group.lower()}"),
                    bold(format_amount(group_opening)),
                    bold(format_amount(group_closing - group_opening)),
                    bold(format_amount(group_closing)),
                ]
            )
            closing_total += group_closing
        rows += extra
        headers = [
            "Konto",
            "Benämning",
            "Ingående balans",
            "Förändring",
            "Utgående balans",
        ]
        out.append(table(headers, rows, right=(2, 3, 4)) + "\n")
        return closing_total

    assets = section("Tillgångar", ledger.balance_accounts("1"), +1, [])
    out.append(f"**Summa tillgångar:** {format_amount(assets)} kr\n")
    result = ledger.result
    result_row = [
        "",
        "Periodens resultat",
        format_amount(ZERO),
        format_amount(result),
        format_amount(result),
    ]
    liabilities = section(
        "Eget kapital och skulder", ledger.balance_accounts("2"), -1, [result_row]
    )
    liabilities += result
    out.append(
        "**Summa eget kapital och skulder (inklusive periodens resultat):** "
        f"{format_amount(liabilities)} kr\n"
    )
    difference = assets - liabilities
    out.append(
        "Balansen stämmer: tillgångar är lika med eget kapital och skulder.\n"
        if difference == ZERO
        else f"> **Balansen stämmer inte.** Skillnad {format_amount(difference)} kr.\n"
    )
    fund = latest_fund_value(context)
    if fund is not None and context.fund_account is not None:
        out.append(
            f"> Fonden ({context.fund_account}) är bokförd till "
            f"{format_amount(ledger.closing(context.fund_account))} kr. Marknadsvärdet "
            f"var {format_amount(fund.value)} kr ({fund.date}), som bokförs vid "
            "bokslut.\n"
        )
    return "\n".join(out)


def render_general_ledger(books: Books, context: ReportContext) -> str:
    """The trial balance, then every posting per account with a running balance."""
    ledger = Ledger(books, context.fiscal_year)
    out = [render_header("Huvudbok", context, ledger.period_end)]
    accounts = ledger.used_accounts()

    out.append("## Saldobalans\n")
    rows: list[list[str]] = []
    totals = [ZERO, ZERO, ZERO, ZERO]
    for account in accounts:
        postings = ledger.postings.get(account, [])
        values = [
            ledger.opening.get(account, ZERO),
            sum((p.debit for p in postings), ZERO),
            sum((p.credit for p in postings), ZERO),
            ledger.closing(account),
        ]
        totals = [t + v for t, v in zip(totals, values, strict=True)]
        rows.append([account, ledger.name(account), *map(format_amount, values)])
    rows.append(["", bold("Summa"), *(bold(format_amount(t)) for t in totals)])
    out.append("Saldon visas med debet positivt och kredit negativt.\n")
    out.append(
        table(
            ["Konto", "Benämning", "Ingående", "Debet", "Kredit", "Utgående"],
            rows,
            right=(2, 3, 4, 5),
        )
        + "\n"
    )
    out.append(
        "Summa debet är lika med summa kredit, och summan av utgående saldon är 0.\n"
        if totals[1] == totals[2] and totals[3] == ZERO
        else "> **Saldobalansen stämmer inte.**\n"
    )

    for account in accounts:
        out.append(f"## {account} {ledger.name(account)}\n")
        balance = ledger.opening.get(account, ZERO)
        rows = [["", "", "Ingående balans", "", "", format_amount(balance)]]
        for posting in ledger.postings.get(account, []):
            balance += posting.debit - posting.credit
            rows.append(
                [
                    str(posting.voucher.date),
                    voucher_link(posting.voucher, context),
                    posting.voucher.text,
                    format_amount(posting.debit) if posting.debit else "",
                    format_amount(posting.credit) if posting.credit else "",
                    format_amount(balance),
                ]
            )
        rows.append(
            ["", "", bold("Utgående saldo"), "", "", bold(format_amount(balance))]
        )
        out.append(
            table(
                ["Datum", "Ver", "Text", "Debet", "Kredit", "Saldo"],
                rows,
                right=(3, 4, 5),
            )
            + "\n"
        )
    return "\n".join(out)


def render_voucher_list(books: Books, context: ReportContext) -> str:
    """Every voucher with its amount, accounts, documents and note."""
    ledger = Ledger(books, context.fiscal_year)
    out = [render_header("Verifikationslista", context, ledger.period_end)]
    intro = (
        f"{len(books.vouchers)} verifikationer. Belopp är bokfört belopp. Debet och "
        "kredit anges som konto och benämning."
    )
    if context.guessed_posting_marker:
        intro += (
            f" Anteckningar med *{context.guessed_posting_marker}* är preliminära och "
            "ska kontrolleras."
        )
    out.append(intro + "\n")

    def accounts(voucher: Voucher, debit: bool) -> str:
        return "; ".join(
            f"{line.account} {ledger.name(line.account)}"
            for line in voucher.lines
            if (line.debit if debit else line.credit) > ZERO
        )

    rows = []
    for voucher in books.vouchers:
        note = " ".join(voucher.note.split())
        if len(note) > NOTE_LENGTH:
            note = note[: NOTE_LENGTH - 3].rstrip() + "…"
        rows.append(
            [
                voucher_link(voucher, context),
                str(voucher.date),
                voucher.text,
                format_amount(voucher.total_debit),
                accounts(voucher, debit=True),
                accounts(voucher, debit=False),
                "; ".join(voucher.documents),
                note,
            ]
        )
    headers = [
        "Ver",
        "Datum",
        "Text",
        "Belopp",
        "Debet",
        "Kredit",
        "Underlag",
        "Anteckning",
    ]
    out.append(table(headers, rows, right=(3,)) + "\n")
    return "\n".join(out)


def render_monthly_overview(books: Books, context: ReportContext) -> str:
    """Revenue, costs, result and the bank balance per month, to the last voucher."""
    ledger = Ledger(books, context.fiscal_year)
    out = [render_header("Månadsöversikt", context, ledger.period_end)]
    months = range(1, ledger.period_end.month + 1)
    revenue = dict.fromkeys(months, ZERO)
    costs = dict.fromkeys(months, ZERO)
    bank = dict.fromkeys(months, ZERO)
    for voucher in books.vouchers:
        month = voucher.date.month
        if month not in revenue:
            continue
        for line in voucher.lines:
            first = line.account[:1]
            if first and first in REVENUE_CLASSES:
                revenue[month] += line.credit - line.debit
            elif first and first in COST_CLASSES:
                costs[month] += line.debit - line.credit
            elif line.account == context.bank_account:
                bank[month] += line.debit - line.credit

    opening_bank = ledger.opening.get(context.bank_account, ZERO)
    balance = opening_bank
    rows = []
    for month in months:
        balance += bank[month]
        rows.append(
            [
                MONTHS[month - 1].capitalize(),
                format_amount(revenue[month]),
                format_amount(-costs[month]),
                format_amount(revenue[month] - costs[month]),
                format_amount(balance),
            ]
        )
    total_revenue = sum(revenue.values(), ZERO)
    total_costs = sum(costs.values(), ZERO)
    rows.append(
        [
            bold("Summa"),
            bold(format_amount(total_revenue)),
            bold(format_amount(-total_costs)),
            bold(format_amount(total_revenue - total_costs)),
            bold(format_amount(balance)),
        ]
    )
    headers = [
        "Månad",
        "Intäkter",
        "Kostnader",
        "Resultat",
        f"Bank ({context.bank_account}) vid månadens slut",
    ]
    out.append(table(headers, rows, right=(1, 2, 3, 4)) + "\n")
    out.append(f"Ingående banksaldo: {format_amount(opening_bank)} kr.\n")
    return "\n".join(out)


def voucher_link(voucher: Voucher, context: ReportContext) -> str:
    """The voucher id, linked to its file when the context has a voucher folder."""
    label = f"{voucher.number:04d}" if voucher.series is None else voucher.id
    if context.voucher_folder and voucher.source:
        return f"[{label}]({context.voucher_folder}/{voucher.source})"
    return label


def latest_fund_value(context: ReportContext) -> FundValue | None:
    """The fund value with the latest date, if any."""
    if not context.fund_values:
        return None
    return max(context.fund_values, key=lambda v: v.date)
