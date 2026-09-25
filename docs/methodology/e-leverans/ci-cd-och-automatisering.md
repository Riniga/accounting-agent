# CI/CD & automatisering

**Kategori:** E. Leverans
**Status:** fastställd
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-ci-cd-och-automatisering.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Det här dokumentet är den tekniska väv som binder ihop krav från flera tidigare kapitel (formatering, tester, säkerhet, kodgranskning) till en faktisk pipeline. Det fastställer en central distinktion: **CI (kontinuerlig integration) är ett ovillkorligt krav, medan CD (kontinuerlig driftsättning) är ett eftersträvat mål.** De två är inte samma sak och ska inte behandlas som ett enda krav.

## Omfattning och avgränsning

Omfattar pipeline-arkitektur: kontrollkedjans ordning, feature flags, sammanslagningsmekanik och val av driftsättningsstrategi.

Omfattar **inte**:

- *Vad* som ska kontrolleras (formatering, komplexitet, säkerhetsfynd, tester, granskning): redan fastställt i respektive kapitel. Det här dokumentet definierar bara var och hur de körs.
- Miljöernas egen konfiguration (dev/test/uat/prod), se Miljöhantering & konfiguration. Det här dokumentet definierar pipelinen som driftsätter *till* de miljöerna.

## Krav (SKA)

1. Varje pull request ska köras genom en fullständig, automatiserad kontrollkedja (bygg, test, statisk analys) innan den kan slås samman. Det här gäller ovillkorligen, oavsett om driftsättningen i övrigt är automatiserad eller fortfarande manuell.
2. Pipelinen ska ordnas fail-fast: billiga/snabba kontroller (formatering, lint) körs före dyra/långsamma (end-to-end-tester). Snabb återkoppling prioriteras.
3. Feature flags ska kategoriseras vid skapande efter grundläggande typ (release/experiment/ops/behörighet), tilldelas en ägare, och få ett förväntat borttagningsdatum. Release-flaggor ska tas bort inom en definierad tid (riktmärke: 1–4 veckor) efter full utrullning.
4. En mekanism ska säkerställa att huvudgrenen förblir grön (byggbar och testad) efter varje sammanslagning.

## Rekommendationer (BÖR)

1. Automatiserad driftsättning (CD) eftersträvas som mål för alla system, men är inte obligatoriskt där det idag är tekniskt utmanande i befintliga system. Manuell driftsättning accepteras som ett mellansteg, med en plan för att automatisera över tid.
2. Sammanslagningsmekanikens tyngd (enkel "uppdaterad gren"-kontroll kontra en full sammanslagningskö) anpassas efter faktiskt behov och risk per projekt.
3. Driftsättningsstrategi (rolling/blue-green/canary) väljs utifrån risk och kritikalitet för den specifika tjänsten, när driftsättningen väl är automatiserad.
4. Progressiv utrullning (t.ex. canary) används av team/tjänster som är redo för det, inte en generell rekommendation i den här iterationen av metodiken.
5. Pipelinens totala körtid (från commit till klar för driftsättning) hålls kort (riktmärke: inom en arbetsdag).

## Vägledning och exempel

**Varför CI och CD hålls isär:** CI (kontinuerlig integration) betyder att varje ändring byggs, testas och analyseras automatiskt innan den slås samman. Det säger inget om hur koden når produktion. CD (kontinuerlig driftsättning) betyder att den byggda, godkända koden sedan tar sig till produktion utan manuella steg. Ett projekt kan ha utmärkt CI och ändå driftsätta manuellt. Det är helt i sin ordning och ett vanligt läge. Vad som inte är i sin ordning är att sakna CI.

**Feature flags på grundnivå (Martin Fowlers klassificering):**

- **Release-flaggor:** släcker/tänder en ofärdig funktion, kortlivade, tas bort efter full utrullning.
- **Experimentflaggor:** delar trafik för att mäta ett utfall.
- **Driftflaggor:** en "kill switch" för att snabbt stänga av något vid problem.
- **Behörighetsflaggor:** styr åtkomst/entitlement.

Poängen med att sätta typ, ägare och utgångsdatum redan vid skapandet är att en flagga annars tenderar att bli kvar för alltid och göra kodbasen svårare att läsa. Samma princip gäller redan för flaky tester (karantän med ägare och deadline, se Testning).

**Driftsättningsstrategier (exempel, för team som nått dit):** canary skiftar trafik gradvis till en ny version under mätning; blue-green håller två fullständiga miljöer och växlar allt på en gång; rolling uppdaterar instanser stegvis. Ingen är universellt "rätt"; valet beror på tjänstens risk och vilken typ av felsäkerhet som är viktigast.

**Effekten av att investera i det här är dokumenterad och stor:** team som antagit kontinuerlig driftsättning driftsätter enligt DORA:s forskning omkring 208 gånger oftare, med en tredjedel så hög andel misslyckade ändringar, jämfört med team som inte gjort det.

## Undantag

Om ett system tekniskt inte kan köras genom en fullständig automatiserad kontrollkedja (krav 1), t.ex. en äldre plattform med inkompatibel verktygskedja, kan en tillfällig, dokumenterad kompenserande manuell kontrollprocess användas istället, under förutsättning att en plan finns för att antingen få verktygsstöd på plats eller fasa ut systemet. Avsteget ska godkännas och dokumenteras, inte tyst accepteras.

## Källor och ramverk

- Martin Fowlers klassificering av feature flags/toggles och "flag debt" som känt antimönster.
- Praxis för sammanslagningsköer och proportionerlig komplexitet efter faktiskt behov.
- Deployment-strategier (rolling, blue-green, canary) och progressiv leverans.
- DORA:s forskning om sambandet mellan kontinuerlig driftsättning och leveransprestanda.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Versionshantering & branchstrategi (kategori E), namngav CI, feature flags och sammanslagningsmekanik som förutsättningar; det här dokumentet definierar dem.
- Miljöhantering & konfiguration (kategori E), miljöerna pipelinen driftsätter till.
- Kodgranskning, Kodstandard & stil, Secure coding-principer, Testning: vad som faktiskt kontrolleras i kontrollkedjan (krav 1).

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Utvecklingsmetodiken, version 1.0
