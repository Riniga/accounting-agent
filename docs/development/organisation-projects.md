# Using the core from an organisation project

How an organisation project — JudoSyd, Helsingborgs Judoklubb, Aktivitet Förebygger —
uses Accounting Agent while it keeps its own books. The organisation project keeps its
data, rules and routine. The core adds shared, tested checks, and takes over more of the
work MVP by MVP (see the [roadmap](../roadmap.md)).

## What each organisation can use today

| Organisation | Book format | Can use | Keeps using its own tooling for |
|---|---|---|---|
| Helsingborgs Judoklubb | `front-matter` | `accounting-agent validate` — the book checks, balances | Bank import and reconciliation, members, budget, BAS chart check, duplicates, supporting documents, reports (`kontroll.py`, `generera_redovisning.py`, …) |
| Aktivitet Förebygger | table format | nothing yet — no reader ([Book formats](../architecture/overview.md#book-formats)) | everything |
| JudoSyd | not in files yet | nothing yet | everything |

Bookkeeping itself — creating vouchers, posting, the treasurer's decisions — is still done
by each organisation's own routine (for example Helsingborgs Judoklubb's `SOP.md`). **The
core only reads.** It never changes an organisation's books.

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
Judoklubb, `2026/`:

```yaml
organisation: hbg-judo           # lowercase id; the commands use the same id
features:
  accounting: true
  payroll: false
  gmail: false
  discord: false
books:
  path: Bokföring                # the folder with kontoplan.csv, ingående-balans.csv, verifikationer/
  format: front-matter
  fiscal_year: 2026
  bank_account: "1930"
```

**New fiscal year:** copy the file into the new year's folder and change `fiscal_year`.
Commit `organisation.yaml` in the organisation's own repository. It holds configuration
only, no data.

## Daily use

From the organisation project's root, after every change to the books:

```bash
conda run -n accounting-agent accounting-agent validate hbg-judo --config-dir 2026
conda run -n accounting-agent accounting-agent validate hbg-judo --config-dir 2026 --balances
```

- **Exit code 1 / `RESULT: ERROR`**: the books are broken. Fix them before anything else,
  following the organisation's own routine.
- **Warnings** (for example `personal-number`): review them. They don't block.
- The output never contains voucher texts, and personal identity numbers are masked. It
  is safe to show it to an AI tool or paste it into an issue.

Until the core covers everything, run **both** the core and the organisation's own checks
(for Helsingborgs Judoklubb, `python 2026/agent/kontroll.py`). On the checks both perform, they
give the same result: verified in MVP-002 on the 2026 books.

## Instructions for Claude Code in an organisation project

Paste this section into the organisation project's `CLAUDE.md` (or `AGENTS.md`), and
adjust the id and the year. It is in Swedish, like the organisation projects:

```markdown
## Accounting Agent (gemensam kärna)

Den här bokföringen kontrolleras också av Accounting Agent-kärnan
(https://github.com/Riniga/accounting-agent). Kärnan läser bara; den ändrar aldrig
bokföringen.

- Efter varje ändring i bokföringen, kör från projektets rot:
  `conda run -n accounting-agent accounting-agent validate hbg-judo --config-dir 2026`
  En ändring är klar först när resultatet är `RESULT: OK` och projektets egen kontroll
  (`python 2026/agent/kontroll.py`) också ger OK.
- `RESULT: ERROR` (exit 1) betyder att bokföringen är trasig. Rätta enligt SOP.md, och
  ändra aldrig en befintlig verifikation utan kassörens uttryckliga beslut.
- Varningar (t.ex. `personal-number`) granskas och rapporteras till kassören; de stoppar
  inte arbetet.
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
