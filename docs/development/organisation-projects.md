# Using the core from an organisation project

How an organisation project — JudoSyd, Helsingborgs Judoklubb, Aktivitet Förebygger —
uses Accounting Agent while it keeps its own books. The organisation project keeps its
data, rules and routine. The core adds shared, tested checks, and takes over more of the
work MVP by MVP (see the [roadmap](../roadmap.md)).

## What each organisation can use today

| Organisation | Can use | Keeps using its own tooling for |
|---|---|---|
| Helsingborgs Judoklubb | `import-bank` (bank statement and fund value), `validate` (every check in `kontroll.py` except members, and the reconciliation against the bank), `new-voucher` (a voucher for a bank transaction), `report` (every report except the member fees) | Members: `medlemskontroll.py`, the member checks in `kontroll.py` and the member-fee report (backlog) |
| Aktivitet Förebygger | everything the core has, once its year folder is set up in the core's format: `import-bank` (`sparbanken-syd-csv`), `validate`, `new-voucher` (salaries and invoices need its lines), `report` | reconciling the tax account; calculating salaries |
| JudoSyd | nothing yet — its books are not in files | everything |

The core has one book format, and an organisation adopts it
([ADR-010](../architecture/decisions/ADR-010-one-book-format.md)); see
[Book formats](../architecture/overview.md#book-formats).

The treasurer's decisions — which account, which supporting document, whether a posting
is a guess — stay with each organisation and its own routine (for example Helsingborgs
Judoklubb's `SOP.md`). The core writes the voucher from those decisions: `new-voucher`
takes the date, the amount, the text and the number from the bank statement and the
books, and refuses rather than writes a wrong voucher
([ADR-009](../architecture/decisions/ADR-009-core-creates-vouchers.md)). **The core never
changes or removes a voucher.** Its other writes are derived files: the bank statement and
fund-value files, and the reports
([ADR-008](../architecture/decisions/ADR-008-core-writes-derived-files.md)).

## One-time setup (per computer)

1. Install the core and its environment once, as in [`setup.md`](setup.md):

   ```bash
   git clone git@github.com:riniga/accounting-agent.git
   cd accounting-agent
   conda env create -f environment.yml
   conda activate accounting-agent
   pip install -e .
   ```

2. Keep it up to date with `git pull` in the core repository. Run
   `conda env update -f environment.yml --prune` when `environment.yml` or
   `requirements-lock.txt` changed.

Organisation projects run the core with `conda run -n accounting-agent …`. They need
nothing installed themselves and can keep their own Python version.

## Setup per organisation and fiscal year

Put an `organisation.yaml` in the folder that holds the year's books — for Helsingborgs
Judoklubb, `2026/`. Paths are relative to that folder. Every section after `books` is
optional; a check or command whose section is missing is skipped or refused.

```yaml
organisation: hbg-judo           # lowercase id; the commands use the same id
features:
  accounting: true
  payroll: false
  gmail: false
  discord: false
books:                           # validate, report
  path: Bokföring                # kontoplan.csv, ingående-balans.csv, verifikationer/
  format: front-matter
  fiscal_year: 2026
  bank_account: "1930"
bank:                            # import-bank; reconciliation in validate
  export_format: nordea-csv      # or sparbanken-syd-csv
  statement_file: Bokföring/kontoutdrag-1930.csv
  fund_account: "1350"           # optional, together with fund_value_file
  fund_value_file: Bokföring/fondvärde-1350.csv
checks:                          # the detail checks in validate
  documents: underlag            # the supporting documents
  reference_chart: kontobas      # the BAS reference chart, four CSV files
  budget_file: Bokföring/budget.csv
  comments_file: Bokföring/kommentarer.csv
  todo_file: Bokföring/att-göra.csv
conventions:                     # the organisation's own conventions
  parking_accounts: ["3008"]
  no_document_accounts: ["6570"] # accounts that need no supporting document
  guessed_posting_marker: Gissad kontering
  outlay_prefix: Utlägg
reports:                         # report
  output: Redovisning
  organisation_name: <the organisation's name>
  organisation_number: <its organisation number>
```

The budget, closing comments and to-do list use the core's file formats, including their
allowed values ([ADR-007](../architecture/decisions/ADR-007-supplementary-book-files.md)).

**New fiscal year:** copy the file into the new year's folder and change `fiscal_year`.
Commit `organisation.yaml` in the organisation's own repository. It holds configuration
only, no data.

## Daily use

From the organisation project's root:

```bash
# after downloading the bank's export (the export itself is never changed)
conda run -n accounting-agent accounting-agent import-bank hbg-judo --config-dir 2026 "2026/Bankpapper/<export>.csv"

# see which bank transactions have no voucher (date, amount and statement row)
conda run -n accounting-agent accounting-agent validate hbg-judo --config-dir 2026 --unbooked

# create the voucher for one of them — one run per bank transaction, oldest first
conda run -n accounting-agent accounting-agent new-voucher hbg-judo --config-dir 2026 --date 2026-03-05 --amount -458 --account 5010 --document "20260305-faktura-1001.pdf"

# a bank transaction against several accounts: give the other side, the bank line is added
conda run -n accounting-agent accounting-agent new-voucher hbg-judo --config-dir 2026 --date 2026-04-25 --amount -21000 --debit 7010=30000 --credit 2710=9000

# an event without a bank transaction: no --amount; the date, the text and every line
conda run -n accounting-agent accounting-agent new-voucher hbg-judo --config-dir 2026 --date 2026-04-30 --text "Faktura 12" --debit 1510=12500 --credit 3010=12500

# after every change to the books
conda run -n accounting-agent accounting-agent validate hbg-judo --config-dir 2026

# when the reports should be updated
conda run -n accounting-agent accounting-agent report hbg-judo --config-dir 2026
```

- **Exit code 1 / `RESULT: ERROR`**: the books are broken. Fix them before anything else,
  following the organisation's own routine. `report` writes nothing then, unless
  `--force` is given.
- **Warnings** (for example `personal-number`, `voucher-duplicate`): review them. They
  don't block.
- **`new-voucher`** creates one new file in the voucher folder and nothing else.
  - With `--amount` the voucher is for a bank transaction, against `--account` or
    against lines given with `--debit` and `--credit`. The lines are the other side
    only; they must add up to the bank's amount.
  - Without `--amount` the voucher has no bank transaction: an issued invoice, a salary
    run, a tax-account event, a closing entry. `--text` and every line are needed, the
    lines must balance, the date must be in the fiscal year, and the bank account
    cannot be among the lines. The same date, text and lines twice is refused.
  - A voucher belongs to at most one bank transaction. A salary run that the bank pays
    as several transactions is one voucher without the bank account, with the net as a
    liability, and one voucher per payment.
  - The core calculates nothing. Tax, employer's contributions and net salary come from
    the supporting document.
  - `--row` is needed when several bank transactions have the same date and amount;
    `validate` prints the row.
  - `--document` names a file in the documents folder and can be repeated. `--note`
    adds a note. `--guess` marks the posting with the organisation's marker, and the
    note must then say why.
  - It refuses — and writes nothing — when the transaction is missing or already has a
    voucher, the account is not in the chart, a document is not in the folder, or the
    books have errors. One error does not stop it: a bank transaction that was skipped
    earlier, since creating its voucher is the fix.
  - Below the fields it writes the accounts with their names and a link to each
    document. Leave those lines as they are; when the treasurer changes an account by
    hand, change the line too, or `validate` reports the difference.
  - A wrong voucher is not undone by the core. Removing or changing it is the
    treasurer's decision, by the organisation's routine.
- **Two forms of voucher file.** One debit and one credit line is written with an
  account in `debet`, one in `kredit`, and `belopp`, as before. Any other voucher lists
  its lines in the two fields, each `<account> <amount>`, separated by semicolons —
  `debet: 7010 30000` and `kredit: 2710 9000; 1930 21000` — and `belopp` is then the
  net on the bank account, or the total without it. The debit lines come first. The
  forms never mix in a file, and no field is repeated: the fields are valid YAML.
- **A statement without balances** (`bank-no-balances`): some banks export no balance.
  The core then cannot check the opening balance of the bank account, or the bank's own
  arithmetic; check the opening balance against a statement yourself.
- **Supporting documents:** `validate` warns for each payment out of the bank without a
  document, and for each voucher without a bank transaction and without a document
  (`documents-expected`), except on the accounts in
  `conventions.no_document_accounts`, and counts the files no voucher refers to
  (`documents-unused`). The to-do report lists those files by name.
- **`import-bank`** refuses an export that starts later than the existing statement file:
  fetch the whole year from 1 January.
- The terminal output never contains voucher texts, names or bank messages, and personal
  identity numbers are masked. It is safe to show it to an AI tool or paste it into an
  issue. **The reports are not**: they contain voucher texts, because they are the
  accounts. They stay in the organisation's own project.

For Helsingborgs Judoklubb, the core gives the same results as `kontroll.py` (except
members), the same bank statement file as `importera_kontoutdrag.py`, and the same figures
as `generera_redovisning.py` (except the member-fee report): verified in MVP-003 on the
2026 books. The member parts still need the organisation's own scripts.

## Instructions for Claude Code in an organisation project

Paste this section into the organisation project's `CLAUDE.md` (or `AGENTS.md`), and
adjust the id and the year. It is in Swedish, like the organisation projects:

```markdown
## Accounting Agent (gemensam kärna)

Den här bokföringen importeras, kontrolleras och redovisas med Accounting Agent-kärnan
(https://github.com/Riniga/accounting-agent). Kärnan skapar nya verifikationer på
kommando, men ändrar eller tar aldrig bort en befintlig.

- Ny bankexport: `conda run -n accounting-agent accounting-agent import-bank hbg-judo --config-dir 2026 <exportfil>`.
  Exporten måste börja den 1 januari; annars vägrar kärnan.
- Efter varje ändring i bokföringen, kör från projektets rot:
  `conda run -n accounting-agent accounting-agent validate hbg-judo --config-dir 2026`
  En ändring är klar först när resultatet är `RESULT: OK`. Medlemskontrollerna finns
  ännu bara i projektets egna skript (`medlemskontroll.py`, `kontroll.py`).
- `--unbooked` listar banktransaktioner efter sista verifikationen (datum, belopp och
  rad i kontoutdraget).
- **Skapa aldrig en verifikationsfil för hand.** Använd kommandot, en körning per
  banktransaktion, äldst först:
  `conda run -n accounting-agent accounting-agent new-voucher hbg-judo --config-dir 2026 --date <ÅÅÅÅ-MM-DD> --amount <belopp> --account <motkonto> [--row <rad>] [--document <fil>] [--note <text>] [--guess]`
  - Du anger bara besluten: motkonto enligt konteringsreglerna, underlag och eventuell
    anteckning. Datum, belopp, text och nummer hämtas ur kontoutdraget och bokföringen.
  - Flera konton mot en banktransaktion (till exempel lön): byt `--account` mot
    `--debit <konto>=<belopp>` och `--credit <konto>=<belopp>`, en per rad. Ange bara
    den andra sidan; bankraden läggs till av kommandot, och raderna måste gå ihop med
    bankens belopp.
  - En händelse utan banktransaktion (utställd faktura, lönekörning, skattekonto,
    bokslutspost): utelämna `--amount` och ange `--text "<vad det är>"` och alla rader
    med `--debit`/`--credit`. Debet ska vara lika med kredit, och bankkontot får inte
    vara med.
  - En verifikation hör till högst en banktransaktion.
  - Räkna inte ut belopp. Skatt, arbetsgivaravgifter och nettolön tas från underlaget.
  - `--row` behövs när flera transaktioner har samma datum och belopp.
  - Är konteringen en gissning: `--guess` och skälet i `--note`. Gissa aldrig utan det.
  - Vägrar kommandot, läs skälet och rätta anropet. Försök inte gå runt det genom att
    skriva filen själv.
  - Raderna under fälten (konton med namn, länkar till underlag) skapas av kommandot.
    Ändra dem inte.
- `validate` varnar för utbetalningar utan underlag, och för verifikationer utan
  banktransaktion som saknar underlag (`documents-expected`), och räknar
  underlag som ingen verifikation pekar på (`documents-unused`); rapporten *att-göra*
  listar dem.
- Rapporterna: `conda run -n accounting-agent accounting-agent report hbg-judo --config-dir 2026`.
  De skapas inte om bokföringen har fel. Rapporten om medlemsavgifter skapas fortfarande
  av `generera_redovisning.py`.
- `RESULT: ERROR` (exit 1) betyder att bokföringen är trasig. Rätta enligt SOP.md, och
  ändra aldrig en befintlig verifikation utan kassörens uttryckliga beslut.
- Varningar granskas och rapporteras till kassören; de stoppar inte arbetet.
- Konfigurationen finns i `2026/organisation.yaml`. Nytt år: kopiera filen och ändra
  `fiscal_year`.
- Ändra inte kärnan härifrån. Behöver kärnan kunna något nytt, skriv ett ärende i
  kärnans repo — utan verifikationstexter, namn, belopp eller andra riktiga data (repot
  är publikt).
```

## Feedback to the core

When an organisation project needs something the core cannot do yet, open an issue in
[Riniga/accounting-agent](https://github.com/Riniga/accounting-agent/issues). The
repository is public: **never put real data in an issue** — no voucher texts, names,
amounts, personal identity numbers or file names from a book folder. Describe the need,
and use made-up examples if an example is needed.
