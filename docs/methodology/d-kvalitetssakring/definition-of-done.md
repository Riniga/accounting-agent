# Definition of Done

**Kategori:** D. Kvalitetssäkring
**Status:** fastställd
**Senast uppdaterad:** 2026-09-07
**Underlag:** 2026-09-07-definition-of-done.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

En Definition of Done svarar på en enkel fråga: när är en ändring faktiskt klar? Det här dokumentet samlar de tekniska kvalitetskriterierna från alla andra kapitel till en enda, kort checklista. Den uppfinner inga nya krav, den pekar på dem. Checklistan gäller enhetligt för alla ändringar, oavsett storlek: att göra undantag för "små" ändringar är precis den typen av genväg som över tid gör stora ändringar riskabla snarare än sällsynta.

## Omfattning och avgränsning

Omfattar tekniska kvalitetskriterier för när en kodändring är redo att släppas.

Omfattar **inte**:

- Acceptanskriterier för en specifik funktion (affärsmässiga krav). Ligger utanför den här metodikens avgränsning, se PROJECT.md.
- Detaljerna bakom varje punkt. De definieras i respektive kapitel som checklistan länkar till, inte här.
- Avveckling/utfasning av programvara: medvetet utanför hela metodikens scope.

## Krav (SKA)

En ändring är inte klar förrän:

1. Koden uppfyller kodkvalitets- och kodstandardkraven (formatering automatiskt godkänd, komplexitetströskelvärden inom gräns), se Kodkvalitet & clean code, Kodstandard & stil.
2. Tester finns, täckningsgolvet hålls, och inga okontrollerade flaky tester blockerar, se Testning.
3. Pull requesten är granskad och godkänd av minst en annan människa, och kopplad till ett arbetsobjekt, se Kodgranskning, Versionshantering & branchstrategi.
4. Säkerhetskontroller (SAST, beroendeskanning) har körts, och inga oåtgärdade kritiska fynd finns, se Secure coding-principer, Beroendehantering, paketkällor & signering.
5. Inga hemligheter finns i koden eller dess historik, se Hantering av hemligheter.
6. Databasmigrationer, om tillämpligt, är bakåtkompatibla, se Datamodellering & databasdesign.
7. Dokumentation (README/ADR) är uppdaterad i samma pull request, se Dokumentation av kod.
8. Ny funktionalitet exponerar det som krävs för att vara driftbar (loggning, metrics), se Observability.
9. CI-pipelinen är grön, se CI/CD & automatisering.
10. Om ett AI-verktyg medverkat i att skriva koden: kraven i Riktlinjer för AI-assisterade verktyg och Sekretess & dataskydd vid AI-användning är uppfyllda.
11. Produktionssättningen är kopplad till en existerande, godkänd change request enligt Skanskas produktionssättningsprocess. Detta kompletterar de tekniska kriterierna ovan, det ersätter dem inte.

## Rekommendationer (BÖR)

1. Ett team kan lägga till egna, striktare kriterier utöver checklistan ovan, men aldrig ta bort något från den.
2. Checklistan revideras när metodiken själv uppdateras, eller när ett team upptäcker att ett återkommande problem inte fångas av den. Ett levande dokument, inte fastställt en gång för alla.

## Vägledning och exempel

**Checklistan är en karta, inte en lärobok.** Varje punkt är medvetet kort. Den fulla motiveringen och de exakta gränsvärdena finns i respektive kapitel. Syftet här är att kunna skummas på under en minut, inte läsas som ett eget dokument.

**Varför ingen variant för "små" ändringar:** en genväg för det som känns enkelt är precis vad som över tid gör att stora, sällan genomförda ändringar blir riskfyllda. Samma princip som redan styrt flera andra beslut i metodiken (korta grenar, små pull requests, schemaändringar i små steg): gör det som är svårt oftare, istället för att göra ett undantag för det som känns tungt.

**Change request-kopplingen (krav 11)** är medvetet en organisatorisk kontroll, inte en teknisk. Den finns för att koppla ihop den här metodikens tekniska kvalitetskrav med Skanskas redan existerande produktionssättningsprocess, så de två inte råkar bli två parallella, orelaterade godkännandevägar.

## Undantag

Ett team kan tillfälligt sakna verktygsstöd för en enskild punkt (t.ex. automatiserad SAST i ett äldre system). Se det aktuella kapitlets eget Undantag-avsnitt för hur det hanteras där. Det här dokumentet inför inga egna, separata undantag utöver vad respektive kapitel redan medger.

## Källor och ramverk

- Etablerad praxis för Definition of Done: skillnaden mellan acceptanskriterier och kvalitetskriterier, rekommenderad storlek (6–12 punkter), och DoD som ett levande snarare än statiskt dokument.
- Lagerindelat mönster för organisationsnivå-baslinjer som team kan bygga vidare på men inte underskrida.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

Refererar samtliga tidigare ämnesspår i kategorierna B, C, D, E och F. Se länkarna i checklistan ovan.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
