# Using the core from an organisation project

How an organisation project — JudoSyd, Helsingborgs Judoklubb, Aktivitet Förebygger —
uses Accounting Agent while it keeps its own books. The organisation project keeps its
data, rules and routine. The core adds shared, tested checks, and takes over more of the
work MVP by MVP (see the [roadmap](../roadmap.md)).

## What each organisation can use today

| Organisation | Book format | Can use | Keeps using its own tooling for |
|---|---|---|---|
| Helsingborgs Judoklubb | `front-matter` | `import-bank` (bank statement and fund value), `validate` (every check in `kontroll.py` except members, and the reconciliation against the bank), `report` (every report except the member fees) | Members: `medlemskontroll.py`, the member checks in `kontroll.py` and the member-fee report (backlog) |
| Aktivitet Förebygger | table format | nothing yet — no reader ([Book formats](../architecture/overview.md#book-formats)) | everything |
| JudoSyd | not in files yet | nothing yet | everything |

Bookkeeping itself — creating vouchers, posting, the treasurer's decisions — is still done
by each organisation's own routine (for example Helsingborgs Judoklubb's `SOP.md`). **The
core never writes vouchers.** It writes only derived files: the bank statement and
fund-value files, and the reports, to the paths in `organisation.yaml`
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
  export_format: nordea-csv
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

# after every change to the books
conda run -n accounting-agent accounting-agent validate hbg-judo --config-dir 2026
conda run -n accounting-agent accounting-agent validate hbg-judo --config-dir 2026 --unbooked

# when the reports should be updated
conda run -n accounting-agent accounting-agent report hbg-judo --config-dir 2026
```

- **Exit code 1 / `RESULT: ERROR`**: the books are broken. Fix them before anything else,
  following the organisation's own routine. `report` writes nothing then, unless
  `--force` is given.
- **Warnings** (for example `personal-number`, `voucher-duplicate`): review them. They
  don't block.
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
(https://github.com/Riniga/accounting-agent). Kärnan skriver aldrig verifikationer; den
skriver bara kontoutdrag, fondvärde och rapporter.

- Ny bankexport: `conda run -n accounting-agent accounting-agent import-bank hbg-judo --config-dir 2026 <exportfil>`.
  Exporten måste börja den 1 januari; annars vägrar kärnan.
- Efter varje ändring i bokföringen, kör från projektets rot:
  `conda run -n accounting-agent accounting-agent validate hbg-judo --config-dir 2026`
  En ändring är klar först när resultatet är `RESULT: OK`. Medlemskontrollerna finns
  ännu bara i projektets egna skript (`medlemskontroll.py`, `kontroll.py`).
- `--unbooked` listar banktransaktioner efter sista verifikationen (datum och belopp).
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
