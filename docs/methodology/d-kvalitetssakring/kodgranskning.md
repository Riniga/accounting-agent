# Kodgranskning

**Kategori:** D. Kvalitetssäkring
**Status:** fastställd
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-kodgranskning.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Kodgranskning är den sista mänskliga kontrollpunkten innan kod blir en del av den delade kodbasen. Det här dokumentet fastställer att pull request är obligatoriskt för alla (människor och AI-verktyg), samt vad en granskare faktiskt ska fokusera på, givet att formatering, komplexitet, säkerhet och testtäckning redan har egna, automatiserade kontroller (se Relaterat).

**Genomgående princip:** kraven nedan är ett golv för alla projekt, inte ett tak. Ett team som redan har en striktare process (fler obligatoriska granskare, mindre PR-gräns, etc.) fortsätter med den. Det här dokumentet sänker aldrig en befintlig ambitionsnivå; det säkerställer bara att ingen ligger under den.

## Omfattning och avgränsning

Omfattar granskningsprocessen: när den krävs, vem som granskar, vad godkännande faktiskt innebär, och vad en granskare ska fokusera på.

Omfattar **inte**:

- Formatering: redan automatiserad, se Kodstandard & stil.
- Komplexitetströskelvärden: redan automatiserade, se Kodkvalitet & clean code.
- Säkerhetsfynd (SAST/DAST): rapporteras som en egen, namngiven kontroll, se Secure coding-principer.
- Att tester finns och täckningsgolvet hålls: automatiserat, se Testning. Om testerna faktiskt testar rätt beteende är däremot en genuin del av granskningen (se krav 5).

## Krav (SKA)

1. Pull request (eller motsvarande granskningsbegäran) är obligatoriskt för alla ändringar till skyddade grenar: ingen direkt commit, för någon, människa eller AI-verktyg. Genomdrivs tekniskt via grenskydd.
2. Minst en människa som inte är författaren själv ska godkänna innan sammanslagning. Gäller oförändrat oavsett om ett AI-verktyg medverkat i att skriva koden. Inget extra godkännande krävs enbart för AI-medverkan.
3. Godkännande ska dirigeras till rätt sakkunnig automatiskt (t.ex. via en CODEOWNERS-liknande mekanism), baserat på vilka delar av kodbasen som ändras.
4. Ett tidigare godkännande ska upphöra att gälla om ändringar görs efter det. Ett nytt godkännande krävs för den nya versionen av ändringen.
5. Granskningens bar är att ändringen definitivt förbättrar kodens hälsa, inte att den är perfekt. Uppenbara problem med design, korrekthet i kantfall, eller om testerna faktiskt testar rätt beteende ska stoppa sammanslagning; personlig smak ska inte.

## Rekommendationer (BÖR)

1. Pull requests hålls små (riktmärke: 50–200 ändrade rader, ideal enligt forskning). En icke-blockerande varning visas vid ca 300 rader, som en lärande signal snarare än en spärr.
2. PR-storlek spåras som en metric över tid, för att synliggöra trender, inte bara varna i enskilda fall.
3. Granskningen koncentreras till det som inte redan är automatiserat: designens lämplighet, korrekthet i kantfall, och om testerna testar rätt beteende.

## Vägledning och exempel

**Vad en granskare faktiskt ska göra** (enligt Googles etablerade granskningsstandard): fråga om designen passar in i helheten, om ändringen gör vad den är avsedd att göra (inklusive kantfall), och om testningen är adekvat. Det finns ingen perfekt kod, bara bättre kod. Att hålla tillbaka ett godkännande för att nå en personlig idealbild är lika mycket ett fel som att godkänna slarvigt.

**Varför PR-storlek spelar så stor roll:** forskning visar konsekventa, stora effekter. PR:ar under 200 rader godkänns cirka tre gånger snabbare än stora, en 50-radig PR är 15 % mindre sannolik att behöva rullas tillbaka än en 250-radig, PR:ar över 1 000 rader har omkring 70 % lägre felupptäcktsgrad, och granskarens fokus sjunker mätbart efter ungefär en timme. Det här är en mätbar kvalitetsfaktor, inte en smaksak.

**Teknisk mekanism (exempel):** en CODEOWNERS-fil kombinerad med grenskydd som kräver granskning från kodägare och avfärdar gamla godkännanden vid nya commits ("dismiss stale approvals"). Annars kan ett godkännande kringgås genom att ändringar läggs till efteråt. **Vem som äger vilken del av kodbasen (CODEOWNERS-strukturen) avgörs av respektive team.** Metodiken kravställer bara att en dirigeringsmekanism finns, inte hur ägarskapet fördelas.

## Undantag

Vid en akut produktionsincident kan ett expedierat granskningsförfarande användas (t.ex. asynkron granskning som slutförs omedelbart efter en nödvändig driftsättning, istället för före). Kravet på minst ett mänskligt godkännande (krav 2) upphävs aldrig; bara tidpunkten för det kan förskjutas, och avsteget ska dokumenteras i efterhand.

## Källor och ramverk

- [Google: The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html) och [What to look for in a code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html).
- Kvantifierad forskning om sambandet mellan PR-storlek och granskningskvalitet/felupptäckt.
- Etablerad praxis för CODEOWNERS och grenskydd, inklusive "dismiss stale approvals".

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Riktlinjer för AI-assisterade verktyg (kategori F), grenskydd och granskningskrav för AI:s egna commits, som det här dokumentet generaliserar till alla bidragsgivare.
- Kodstandard & stil (kategori B), formatering, redan automatiserad.
- Kodkvalitet & clean code (kategori B), komplexitetströskelvärden, redan automatiserade.
- Secure coding-principer (kategori C), säkerhetsfynd, rapporterade separat.
- Testning (kategori D), testtäckning och TDD-kravet för AI-genererad kod, som krav 5 bygger vidare på.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
