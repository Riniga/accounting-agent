# Accounting Agent – gemensam arkitektur

## Bakgrund

Idag finns tre separata lösningar för ekonomiadministration:

- **JudoSyd**
  - Läser bokföringsunderlag från PDF.
  - Sammanställer ekonomiska rapporter.
  - Kan läsa och analysera Gmail via MCP.
  - Kommunicerar och begär åtgärder via Discord.
  - Kan köras schemalagt som Python-applikation.

- **Helsingborgs Judoklubb**
  - Hanterar kontoutdrag och bokföring.
  - Matchar banktransaktioner mot underlag.
  - Konterar utifrån kontoplan och regler.
  - Lagrar bokföring huvudsakligen som CSV och Markdown.
  - Sammanställer rapporter.

- **AF**
  - Liknande bokföringsfunktioner.
  - Har dessutom mer avancerad hantering av löner och löneutbetalningar.

Gemensamt för lösningarna är att arbetet idag huvudsakligen sker genom VS Code och Claude Code. AI:n har tillgång till projektets instruktioner, scripts och data och kan därifrån analysera och utföra arbetet.

## Problem

De tre projekten utvecklas idag relativt oberoende av varandra.

Det innebär risk för att samma funktionalitet implementeras och underhålls flera gånger, exempelvis:

- import av transaktioner
- matchning mot underlag
- kontering
- validering
- rapportgenerering
- AI-instruktioner
- integrationer
- loggning
- felhantering

Målet är därför att behålla organisationernas data separat men centralisera generell funktionalitet.

---

# Målbild

Lösningen bör utvecklas från **tre separata AI-projekt** till:

> **En gemensam Accounting Agent med tre separata organisationsprofiler.**

Övergripande arkitektur:

```text
                    ┌──────────────────────┐
                    │   Accounting Agent   │
                    │   Claude / LLM       │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │    Gemensam kärna    │
                    │                      │
                    │ import               │
                    │ matchning            │
                    │ kontering            │
                    │ validering           │
                    │ rapportering         │
                    │ löner                │
                    │ actions              │
                    │ integrations         │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
        ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
        │ JudoSyd │       │ Hbg Judo│       │   AF    │
        │ config  │       │ config  │       │ config  │
        │ data    │       │ data    │       │ data    │
        │ rules   │       │ rules   │       │ rules   │
        └─────────┘       └─────────┘       └─────────┘
```

---

# 1. Gemensam kärna

Ett separat projekt/repository skapas, exempelvis:

```text
accounting-agent-core/

  src/
    importers/
      bank_csv.py
      pdf.py
      email.py

    accounting/
      transactions.py
      matching.py
      posting.py
      validation.py

    payroll/
      payroll.py

    reporting/
      monthly_report.py
      annual_report.py

    integrations/
      gmail.py
      discord.py

    agent/
      tools.py
      workflow.py

  models/
    transaction.py
    voucher.py
    account.py
    document.py

  tests/

  pyproject.toml
  README.md
```

Grundprincipen är:

> `accounting-agent-core` ska inte känna till JudoSyd, Helsingborgs Judoklubb eller AF.

All kod som är generell ska ligga här.

---

# 2. Separata organisationsprojekt

Varje organisation behåller ett eget projekt och egen datalagring.

Exempel:

```text
hbg-judo-accounting/

  config/
    organisation.yaml
    chart-of-accounts.yaml
    accounting-rules.yaml

  data/
    bank/
    receipts/
    invoices/
    payroll/

  books/
    2026/
      transactions.csv
      vouchers/
      journal.md

  reports/

  instructions/
    accounting.md
    payroll.md

  CLAUDE.md
```

Organisationsprojekten ska huvudsakligen innehålla:

- data
- kontoplan
- organisationsspecifika regler
- instruktioner
- konfiguration
- genererade rapporter

De ska innehålla så lite egen programkod som möjligt.

---

# 3. Gemensam datamodell

Alla informationskällor bör normaliseras till en gemensam intern datamodell.

En transaktion kan exempelvis representeras som:

```text
Transaction
 ├─ id
 ├─ date
 ├─ amount
 ├─ counterparty
 ├─ description
 ├─ source
 ├─ source_document
 ├─ account
 ├─ cost_center
 ├─ status
 ├─ confidence
 └─ notes
```

Informationen kan ursprungligen komma från exempelvis:

- bank-CSV
- PDF
- faktura
- kvitto
- Gmail
- löneunderlag

Efter import ska resten av systemet i möjligaste mån arbeta mot samma datamodell.

Det minskar beroendet mellan bokföringslogiken och formatet på källdatan.

---

# 4. Agenten arbetar genom definierade verktyg

På sikt bör AI-agenten inte själv manipulera filer och bokföringsdata fritt.

Agenten bör istället få tillgång till tydligt definierade verktyg, exempelvis:

```text
get_unprocessed_transactions()

find_supporting_documents()

suggest_posting()

post_transaction()

validate_books()

generate_report()

search_email()

create_email_draft()

request_user_action()
```

Ansvarsfördelningen blir då:

### AI-agent

Ansvarar för:

- förståelse
- analys
- resonemang
- klassificering
- val av åtgärd
- hantering av osäkerhet

### Python-kod

Ansvarar för:

- filoperationer
- datalagring
- bokföringsoperationer
- validering
- beräkningar
- integrationer
- audit/loggning

Det gör lösningen mer deterministisk, testbar och säker.

---

# 5. Organisationerna definierar capabilities

Samma agent ska kunna användas för olika organisationer.

Exempel JudoSyd:

```yaml
organisation: judosyd

features:
  accounting: true
  payroll: false
  gmail: true
  discord: true

approval:
  posting: automatic
  payment: human
  email_send: human
```

Helsingborgs Judoklubb:

```yaml
organisation: hbg-judo

features:
  accounting: true
  payroll: false
  gmail: false
  discord: false
```

AF:

```yaml
organisation: af

features:
  accounting: true
  payroll: true
  gmail: false
  discord: false
```

På så sätt kan samma kodbas användas samtidigt som organisationerna har olika behov.

---

# 6. Human-in-the-loop

Agenten ska själv kunna avgöra när den behöver hjälp.

Grundflödet kan beskrivas som:

```text
Observe
   ↓
kontoutdrag / PDF / mail / löneunderlag
   ↓
Understand
   ↓
matcha / klassificera / analysera
   ↓
Decide
   ↓
kan agenten lösa detta säkert?
   ↓
 ┌─────────────┐
 JA            NEJ
 ↓              ↓
Execute      Ask Human
 ↓              ↓
bokför       Discord
rapportera   annan kanal
arkivera        ↓
   ↑____________↓
```

En viktig del av datamodellen bör därför vara **confidence**.

Exempel:

```text
confidence >= 0.95
→ automatisk hantering

confidence 0.70–0.95
→ hantera men flagga för kontroll

confidence < 0.70
→ begär mänskligt beslut
```

De exakta nivåerna ska senare definieras utifrån risk och typ av operation.

---

# 7. Approval policies

Olika typer av operationer ska kunna ha olika krav på mänskligt godkännande.

Exempel:

```yaml
approval:

  classify_transaction:
    mode: automatic

  bookkeeping:
    mode: confidence_based

  create_report:
    mode: automatic

  create_email:
    mode: automatic

  send_email:
    mode: human

  payment:
    mode: human

  payroll_payment:
    mode: human
```

Det gör det möjligt att successivt öka graden av automation utan att ge agenten obegränsad autonomi.

---

# 8. Schemalagd körning

Agenten ska kunna startas med organisation som parameter.

Exempel:

```bash
accounting-agent run judosyd
accounting-agent run hbg-judo
accounting-agent run af
```

Scheduler kan sedan starta respektive körning enligt organisationens behov.

Exempelvis:

```text
07:00  accounting-agent run judosyd
07:15  accounting-agent run hbg-judo
07:30  accounting-agent run af
```

På längre sikt kan även eventbaserade körningar användas.

---

# 9. Audit trail

Eftersom systemet arbetar med ekonomi måste alla viktiga beslut kunna följas i efterhand.

Exempel:

```text
2026-09-25 07:31

Organisation:
Helsingborgs Judoklubb

Transaction:
2026-09-23 / ICA Maxi / -842.50

Supporting document:
receipt-20260923-ica.pdf

Agent decision:
Account 5460

Confidence:
0.97

Action:
Posted automatically

Reason:
Matched supplier and receipt.
Purchase classified according to accounting rule FOOD-003.
```

Det ska gå att svara på:

> Vad gjorde agenten, varför gjorde den det och vilket underlag användes?

---

# 10. Önskad slutstruktur

Målet är ungefär:

```text
accounting-agent-core/
        │
        ├──────────────┐
        │              │
        ▼              ▼
      agent           tools
        │              │
        └──────┬───────┘
               │
         accounting API
               │
     ┌─────────┼─────────┐
     ▼         ▼         ▼

 judosyd/   hbg-judo/    af/

 config      config      config
 data        data        data
 rules       rules       rules
 books       books       books
 reports     reports     reports
```

Organisationsprojekten ska helst innehålla **ingen eller mycket liten egen Python-kod**.

---

# 11. Migreringsstrategi

Systemet bör inte skrivas om från början.

Befintliga fungerande lösningar används istället som utgångspunkt.

## Steg 1 – Helsingborgs Judoklubb som pilot

Helsingborgs Judoklubb används som första implementation eftersom bokföringsflödet är relativt tydligt:

```text
kontoutdrag
     ↓
transaktioner
     ↓
matchning mot underlag
     ↓
kontering
     ↓
bokföring
     ↓
rapport
```

Identifiera vilka delar som är generella.

Flytta dessa successivt till `accounting-agent-core`.

## Steg 2 – Kör Hbg Judo genom core

När funktionalitet flyttats ska Hbg Judo använda core istället för lokal implementation.

Målet är:

```text
Hbg Judo
   ↓
configuration
   ↓
accounting-agent-core
```

utan duplicerad implementation.

## Steg 3 – Migrera JudoSyd

När kärnan fungerar flyttas JudoSyd över.

Det introducerar ytterligare capabilities:

```text
Gmail
Discord
PDF-import
scheduled agent
```

Dessa implementeras som generella integrationer.

## Steg 4 – Migrera AF

AF migreras sist.

AF används som stresstest eftersom organisationen introducerar mer komplex funktionalitet:

```text
payroll
salary calculations
salary documentation
payments
additional approval rules
```

Även dessa funktioner ska i möjligaste mån bli generella capabilities i core.

---

# 12. Principer

Följande arkitekturprinciper bör styra utvecklingen.

### Data tillhör organisationen

Organisationernas ekonomiska data ska aldrig blandas.

### Kod tillhör plattformen

Generell funktionalitet ska implementeras en gång.

### Configuration over customization

Skillnader mellan organisationerna ska i första hand lösas genom konfiguration och regler, inte genom separata kodgrenar.

### AI beslutar – kod utför

LLM används där förståelse och bedömning behövs.

Deterministisk Python används där exakta operationer behövs.

### Human-in-the-loop vid risk

Osäkra eller känsliga operationer kräver mänskligt beslut.

### Everything is auditable

Agentens viktiga beslut och åtgärder ska kunna granskas i efterhand.

---

# 13. Nästa konkreta steg

Första arbetet bör **inte** vara att skapa hela målarkitekturen.

Börja istället med Helsingborgs Judoklubb.

### MVP-001 – Extract Accounting Core

Mål:

> Identifiera och extrahera den första generella bokföringsfunktionaliteten från Helsingborgs Judoklubb till `accounting-agent-core`.

Första analysen bör besvara:

1. Vilka scripts finns idag?
2. Vilka datamodeller används?
3. Vilka delar är Hbg Judo-specifika?
4. Vilka delar är generella?
5. Vilka regler ligger idag implicit i prompts eller Python?
6. Vilka funktioner bör bli agent-tools?
7. Vilka operationer kräver mänskligt godkännande?

Efter analysen skapas den minsta möjliga gemensamma kärnan.

Ingen funktionalitet ska flyttas bara för att uppnå en snygg arkitektur.

> **Extrahera först när det finns en fungerande konkret funktion att generalisera.**

---

# Vision

Den långsiktiga visionen är:

> **En gemensam AI-baserad ekonomiadministratör som kan arbeta för flera organisationer genom samma kodbas, men med strikt separerade data, regler och behörigheter.**

Agenten ska självständigt kunna:

- samla in ekonomiskt underlag
- identifiera nya transaktioner
- hitta och matcha underlag
- föreslå eller genomföra kontering
- validera bokföringen
- hantera återkommande administrativa processer
- skapa rapporter
- bevaka inkommande information
- identifiera problem
- begära mänskliga beslut när det behövs
- fortsätta arbetet efter att beslut erhållits

Människan ska framför allt behöva hantera **undantag, godkännanden och beslut** – inte rutinmässig administration.
