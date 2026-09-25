# Dokumentation av kod

**Kategori:** B. Skriva kod
**Status:** fastställd
**Senast uppdaterad:** 2026-09-07
**Underlag:** 2026-09-07-dokumentation-av-kod.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

README är det mest lästa och minst underhållna dokumentet i de flesta repon, och numera även det AI-verktyg läser för att förstå ett projekt. Det här dokumentet fastställer minimikrav för README, hur betydande arkitekturbeslut dokumenteras (ADR), och hur dokumentation hålls i takt med koden istället för att glida efter.

## Omfattning och avgränsning

Omfattar README-krav, Architecture Decision Records (ADR), och principen att dokumentation hänger med kodändringar.

Omfattar **inte**:

- Kodkommentarer, redan beslutat i Kodkvalitet & clean code (förklara varför, inte vad).
- Instruktionsfiler riktade till AI-verktyg (t.ex. AGENTS.md), se Prompt- och kontexthantering. Olika primärt syfte än README, även om innehåll kan överlappa.
- Själva arkitekturbesluten, se Arkitektur- och designprinciper på kodnivå. Det här dokumentet definierar formatet och processen för att dokumentera dem (ADR), inte besluten i sig.

## Krav (SKA)

1. Varje repo ska ha en README med minst: syftet (vilket problem det löser), hur man installerar/kör/testar projektet med konkreta, körbara kommandon, och ett tydligt påstående om ägarskap/status.
2. Dokumentation som beskriver en kodändring (README, API-dokumentation, m.m.) ska uppdateras i samma pull request som ändringen själv, inte som en separat, senare uppgift.
3. Betydande arkitekturbeslut ska dokumenteras som en ADR (Architecture Decision Record) i Nygard-formatet: titel, status, kontext, beslut, konsekvenser.
4. En godkänd ADR ska aldrig redigeras i efterhand. Om beslutet ändras skrivs en ny ADR som ersätter den gamla, med en länk mellan dem.
5. Körbara dokumentationsexempel (kommandon, kodsnuttar) ska valideras automatiskt som en del av pull request-kontrollkedjan, inte bara antas stämma.

## Rekommendationer (BÖR)

1. README:s innehåll prioriteras: en kort förklaring av "varför" tidigt, ett konkret användningsexempel innan läsaren behöver skrolla långt, och specifika versionskrav för beroenden.

## Vägledning och exempel

**Varför README spelar större roll än förr:** utöver att vara den första kontaktpunkten för en människa är README nu också det AI-verktyg (se Verktyg för AI-assisterad utveckling) läser för att förstå ett repo. Ett dåligt README ger sämre resultat från AI-assisterad utveckling också.

**Om ägarskapspåståendet i krav 1:** i praktiken betyder det oftast en enkel rad om att koden är proprietär och intern Skanska-egendom. En fullständig licensgenomgång (MIT, Apache 2.0 m.fl.) är sällan relevant, eftersom merparten av koden aldrig blir open source. Om ett projekt undantagsvis öppen källkod-licensieras anges den licensen istället.

**Var ADR:er lagras (exempel):** `docs/architecture/decisions/` är ett konkret, beprövat exempel med samma struktur som bland annat används i GOV.UK:s publicerade arkitekturdokumentation. Numrerade filer (t.ex. `0001-...md`, `0002-...md`) i kronologisk ordning ger samma "historik i sig är dokumentationen"-effekt som beskrivs i krav 4.

**Nygard-formatet i korthet:**

- **Titel:** kort, beskrivande.
- **Status:** förslag, godkänd, eller ersatt av en senare ADR.
- **Kontext:** vad var situationen eller problemet som krävde ett beslut?
- **Beslut:** vad beslutades?
- **Konsekvenser:** vad blir följden, positiv som negativ?

## Undantag

Ett befintligt repo som helt saknar README kan under en övergångsperiod arbeta med en minimal startversion (syfte och installationsinstruktioner) istället för att uppfylla krav 1 fullt ut direkt, under förutsättning att en plan finns för att komplettera den.

## Källor och ramverk

- Praxis för README-innehåll och varför README-kvalitet påverkar både mänsklig och AI-assisterad användning av ett repo.
- Michael Nygards ADR-format (2011) och dess vidareutveckling som branschstandard.
- Docs-as-code: dokumentation som versionshanterad markdown i samma repo som koden, uppdaterad atomärt.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Kodkvalitet & clean code (kategori B), kodkommentarer.
- Prompt- och kontexthantering (kategori F), AGENTS.md, instruktioner riktade till AI-verktyg.
- Arkitektur- och designprinciper på kodnivå (kategori B), besluten som ADR:er (krav 3–4) dokumenterar.
- CI/CD & automatisering (kategori E), pull request-kontrollkedjan som krav 5 bygger på.
- Beroendehantering, paketkällor & signering (kategori C), licensefterlevnad för tredjepartsberoenden, motsvarande men omvänt av ägarskapspåståendet i krav 1.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
