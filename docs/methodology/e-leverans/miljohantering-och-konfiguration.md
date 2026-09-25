# Miljöhantering & konfiguration

**Kategori:** E. Leverans
**Status:** fastställd
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-miljohantering-och-konfiguration.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Dev, test, UAT och prod är namn de flesta Skanska-projekt redan använder, men hur miljöerna faktiskt konfigureras och skiljs åt varierar helt. Det här dokumentet fastställer var konfiguration hör hemma, hur miljöer definieras utan att glida isär över tid (miljödrift), och hur mycket miljöer behöver likna varandra.

**Terminologinot:** det etablerade engelska begreppet är "environment parity". Den direkta svenska översättningen "miljöparitet" undviks medvetet eftersom den lätt läses som en felskrivning av "Miljöpartiet". **"Miljökonsistens"** används genomgående istället.

## Omfattning och avgränsning

Omfattar hur applikationens driftmiljöer (dev/test/uat/prod) konfigureras, hålls konsistenta, och skyddas.

Omfattar **inte**:

- Utvecklarens egen arbetsyta/dator, se Utvecklingsmiljö & verktyg.
- Den grundläggande regeln att hemligheter aldrig ska finnas i kod, och hur de hanteras generellt, se Hantering av hemligheter. Det här dokumentet specificerar hur hemligheter separeras *per miljö*.
- Vilken data som får finnas i en given miljö utifrån dess klassificering, se Sekretess & dataskydd vid AI-användning, som redan slår fast att UAT:s faktiska dataklassificering (inte namnet) avgör vad som gäller.
- Pipelinen som driftsätter till miljöerna, se CI/CD & automatisering.

## Krav (SKA)

1. Konfiguration som varierar mellan miljöer (databasadresser, API-nycklar, funktionsflaggor) ska lagras i miljövariabler eller motsvarande extern konfigurationsmekanism, aldrig hårdkodad i eller incheckad tillsammans med koden.
2. En exempelfil som visar vilka konfigurationsvärden som krävs (t.ex. `.env.example`) ska checkas in; de faktiska värdena, särskilt hemligheter, ska aldrig checkas in.
3. Miljöer ska definieras och återskapas via kodifierad konfiguration, inte handkonfigureras. Ändringar görs genom den kodifierade processen, aldrig direkt i en miljö, särskilt inte produktion.
4. En efemär förhandsgranskningsmiljö (om en sådan används) får aldrig produktionshemligheter eller oklassificerad produktionsdata.

## Rekommendationer (BÖR)

1. Miljökonsistens eftersträvas graderat: full likhet (versioner, konfiguration, infrastruktur) för kritiska komponenter, kontrollerade avvikelser accepteras för stödtjänster av lägre kritikalitet. Exempel på kritiska komponenter: databasmotor och -version, körtidsmiljö/språkversion, kärnaffärslogikens beroenden. Exempel på stödtjänster där avvikelse kan accepteras: loggnings-/övervakningsagentversioner, icke-kritiska mockade tredjepartstjänster.
2. Efemära förhandsgranskningsmiljöer per pull request lämnas medvetet som en framtida möjlighet att utvärdera, inte en aktiv rekommendation i den här iterationen av metodiken.

## Vägledning och exempel

**Namngivningen dev/test/uat/prod är redan gemensam** hos Skanska, även om konfigurationsmekanismen inte är det. Det här dokumentet bygger vidare på den namngivningen istället för att uppfinna ny terminologi.

**Grundprincipen (krav 1) kommer från "The Twelve-Factor App":** allt som varierar mellan miljöer ska vara utbytbart utan att koden ändras. Konfigurationsvärden är granulära och oberoende av varandra, inte en enda monolitisk "miljöfil" att växla mellan.

**Miljödrift, inte avsaknad av separata miljöer, är den vanligaste bakomliggande orsaken** när "det fungerar på min maskin" inträffar. Lösningen (krav 3) är disciplin kring *hur* en miljö ändras, inte bara att miljöerna finns som begrepp.

**Skanska har redan organisatorisk kapacitet för krav 3:** ett team hanterar infrastruktur som kod. Det här dokumentet kravställer principen (kodifierade, återskapbara miljöer). Det befintliga teamet är den naturliga funktionen att kravställa mot, utan att metodiken pekar ut ett specifikt IaC-verktyg.

## Undantag

För ett äldre system som ännu inte är fullt kodifierat (krav 3) kan handkonfiguration fortsätta tillfälligt, under förutsättning att ändringar dokumenteras och att en plan finns för att föra över miljön till den infrastruktur-som-kod-process Skanska redan har på plats.

## Källor och ramverk

- The Twelve-Factor App: principen om config i miljön.
- Praxis och forskning om miljödrift och graderad miljökonsistens.
- Praxis för efemära förhandsgranskningsmiljöer, inklusive den vanliga säkerhetsmissen att kopiera produktionshemligheter dit.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Utvecklingsmiljö & verktyg (kategori A), utvecklarens egen arbetsyta, till skillnad från applikationens driftmiljöer här.
- Hantering av hemligheter (kategori C), grundregeln som krav 4 bygger vidare på.
- Sekretess & dataskydd vid AI-användning (kategori F), UAT:s dataklassificering, som avgör vad som gäller oavsett miljönamn.
- CI/CD & automatisering (kategori E), pipelinen som driftsätter till miljöerna som definieras här.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
