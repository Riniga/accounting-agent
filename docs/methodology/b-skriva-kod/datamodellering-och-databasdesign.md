# Datamodellering & databasdesign

**Kategori:** B. Skriva kod
**Status:** utkast, krav 1–6 välgrundade men BÖR 7 väntar på samma arkitektgranskning som Arkitektur- och designprinciper på kodnivå
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-datamodellering-och-databasdesign.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Ett databasschema är lika mycket en del av kodbasen som applikationskoden, men behandlas sällan så. Det här dokumentet fastställer hur scheman versionshanteras, hur migrationer görs säkert utan driftstopp, och var ansvaret för dataintegritet faktiskt ligger.

## Omfattning och avgränsning

Omfattar schemadesign, migrationer/versionshantering av databasschema, normalisering och dataintegritet (teknikoberoende, inte bundet till specifikt databasval).

Omfattar **inte**:

- Modulgränser och bounded contexts på kodnivå, se Arkitektur- och designprinciper på kodnivå. BÖR 7 nedan är en direkt tillämpning av det spårets koncept på databasnivå.
- Klassificering av känslig data och hur den skyddas (t.ex. kryptering av specifika kolumner), se Sekretess & dataskydd vid AI-användning och Hantering av hemligheter. Den tekniska mekaniken för det varierar för mycket mellan databastyper för att kravställas generiskt här.
- Pipelinemekaniken som kör migrationer, se CI/CD & automatisering.

## Krav (SKA)

1. Databasscheman ska vara versionshanterade och granskningsbara i git, på samma sätt som kod, inte handpålagda ändringar direkt i en databas.
2. Migrationer ska vara bakåtkompatibla med den för närvarande körande applikationsversionen. En migration ska kunna slutföras medan den gamla applikationsversionen fortfarande körs, innan den nya applikationskoden driftsätts.
3. En brytande schemaändring (t.ex. att ta bort en kolumn eller tabell) ska delas upp i flera steg (expand–migrera–contract), aldrig en enda operation som kräver att applikation och schema byts ut samtidigt.
4. Dataintegritet (obligatoriska fält, unika värden, främmande nycklar) ska genomdrivas med databasens egna integritetsvillkor. Applikationsvalidering är ett komplement för användarupplevelse, inte den enda garanten.

## Rekommendationer (BÖR)

1. Normalisering (tredje normalformen som utgångspunkt) används som standard. Medveten denormalisering motiveras av ett faktiskt, uppmätt prestandabehov, inte i förväg "för säkerhets skull".
2. Ett versionerat migrationsverktyg används istället för handskrivna, ospårade ändringar. Val av specifikt verktyg lämnas helt öppet.
3. **(Föreslaget, väntar på samma arkitektgranskning som redan efterfrågats för Arkitektur- och designprinciper på kodnivå)** Varje system äger sitt eget databasschema. Andra system läser eller skriver inte direkt i ett annat systems tabeller; integration sker via API:er eller händelser, inte via en delad databas.

## Vägledning och exempel

**Expand-contract i praktiken:** en brytande schemaändring (krav 3) delas upp i separata driftsättningar: lägg till en ny kolumn, skriv till både gammal och ny samtidigt, fyll i historiska data, växla applikationen till att läsa från den nya kolumnen, och ta först då bort den gamla. Fyra driftsättningar, aldrig driftstopp. Stora teknikorganisationer (Stripe, Shopify, GitHub) gör konsekvent så här, aldrig en enda stor schemaändring i ett steg.

**Vad "bounded context" betyder** (för BÖR 3): en avgränsad del av verksamheten där ett begrepp har en entydig betydelse och egen datamodell. Till exempel kan "kund" betyda olika saker i en säljprocess och en supportprocess. Kopplat till det här dokumentet: ett system (en tjänst ett team äger, se Arkitektur- och designprinciper på kodnivå) bör äga sitt eget schema istället för att dela databas med andra system.

**Databasens integritetsvillkor (krav 4) är snabbare och mer centralt garanterade** än motsvarande kontroller i applikationskod, och skyddar även mot skrivvägar som inte går via applikationen: andra tjänster, batch-jobb, eller framtida migrationer som skriver direkt till databasen.

**Okänt läge att utreda:** om det redan finns etablerad praxis för databasmigrationer i organisationens projekt är i skrivande stund inte klarlagt (till skillnad från de flesta andra kapitel, där svaret var ett bekräftat "inget finns"). Värt att stämma av innan kraven ovan tillämpas brett, så de kompletterar snarare än duplicerar eller motsäger något som redan fungerar.

## Undantag

För ett befintligt system där migrationer idag inte är bakåtkompatibla (krav 2–3) kan en stegvis övergångsplan användas istället för en omedelbar omställning, under förutsättning att planen är dokumenterad och att inga nya, icke-bakåtkompatibla migrationer tillkommer under tiden.

## Källor och ramverk

- Expand-Contract-mönstret för bakåtkompatibla, driftstoppsfria schemaändringar.
- Kategorier av migrationsverktyg (versionerade CLI:er, deklarativa schema-som-kod-verktyg, ORM-integrerade migratorer): nämnda som ansatser, inte specifika produkter.
- Praxis och motivering för databasnivå-integritetsvillkor framför enbart applikationsvalidering.
- Domain-Driven Design, det strategiska konceptet bounded context.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Arkitektur- och designprinciper på kodnivå (kategori B), bounded contexts och modulgränser på kodnivå, som BÖR 3 tillämpar på databasnivå. Samma pågående arkitektgranskning gäller båda.
- Versionshantering & branchstrategi, CI/CD & automatisering (kategori E), kontinuerlig driftsättning som krav 2–3 är en direkt förutsättning för.
- Sekretess & dataskydd vid AI-användning, Hantering av hemligheter (kategori C/F), skydd av känslig data i specifika kolumner.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Utvecklingsmetodiken, version 1.0
