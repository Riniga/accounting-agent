# Kodkvalitet & clean code

**Kategori:** B. Skriva kod
**Status:** fastställd
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-kodkvalitet-och-clean-code.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Kod skrivs en gång men läses och ändras många gånger, ofta av någon annan än den som skrev den. Det här dokumentet fastställer principer för namngivning, funktionsstorlek, SOLID och komplexitet som gör kod lättare att förstå och förändra, grundade i etablerad praxis, men medvetet inte dogmatiska: fältet har en genuin, dokumenterad debatt om var gränserna går, och det redovisas öppet istället för att gömmas.

## Omfattning och avgränsning

Omfattar designnivå-kvaliteter som kräver mänskligt omdöme: namngivning, funktionsstorlek, SOLID-principerna, kommentarer, duplicering och komplexitet.

Omfattar **inte**:

- Mekaniskt verktygsstyrd formatering (indentering, radlängd, per-språk konventioner), se Kodstandard & stil.
- Hur klasser och moduler organiseras i förhållande till varandra (lager, modulgränser, arkitekturmönster), se Arkitektur- och designprinciper på kodnivå. SOLID-principerna tillämpas här på en enskild klass utformning, inte på hur klasser förhåller sig till varandra i en större struktur.
- Säkerhetsspecifik praxis (indatavalidering, kryptografi), se Secure coding-principer, även om enkel och läsbar kod indirekt minskar sårbarhetsrisk.
- Granskningsprocessen som kontrollerar att principerna följs, se Kodgranskning.

## Krav (SKA)

1. Namn (variabler, funktioner, klasser, moduler) ska vara meningsbärande och avslöja avsikt. Vilseledande eller missvisande namn är aldrig acceptabelt.
2. En klass eller modul ska ha ett enda, tydligt ansvar (Single Responsibility Principle). Om en ändring av en klass kan motiveras av mer än en orsak till förändring är det ett tecken på att den bör delas.

## Rekommendationer (BÖR)

1. En funktion/metod bör göra en sak och vara namngiven efter vad den gör. Storlek i sig är inget mål. Dela upp en funktion när det gör koden lättare att följa, inte för att nå ett visst radantal.
2. Komplexitet bör mätas objektivt med verktygsstöd, i två nivåer: ett rådgivande **riktvärde** som flaggar "bör granskas/refaktoreras", och ett högre, mer generöst **gränsvärde** som blockerar en pull request. Föreslagna startvärden, justerbara per språk/projekt:
   - **Cognitive Complexity:** riktvärde 15, PR-gräns ca 25.
   - **Cyklomatisk komplexitet:** riktvärde 10, PR-gräns ca 20.

   Cyklomatisk komplexitet mäter primärt testbarhet, kognitiv komplexitet primärt läsbarhet. Använd båda, inte den ena istället för den andra.
3. Övriga SOLID-principer (Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) och namngivna designmönster i allmänhet bör tillämpas när de löser ett verkligt, aktuellt behov av flexibilitet eller utbytbarhet, inte spekulativt "för säkerhets skull".
4. Kommentarer bör förklara **varför** (icke-uppenbara beslut, begränsningar, avvägningar), inte **vad** koden gör, vilket välnamngiven kod redan visar.
5. Duplicerad logik bör konsolideras (DRY) när dupliceringen representerar samma beslut eller regel, inte mekaniskt vid varje textlikhet. Att slå ihop kod som råkar se lika ut men förändras av olika skäl skapar felaktig koppling, inte bättre kvalitet.

## Undvik

1. **Singleton-mönstret.** Väldokumenterat som ofta mer skadligt än nyttigt: döljer beroenden, försämrar testbarhet (kan inte bytas ut i tester), skapar dold global, delad state, och fungerar dåligt med parallellitet. **Använd istället:** dependency injection, där livscykeln hanteras av en container/kompositionsrot istället för av klassen själv.
2. **Abstraktion utan nuvarande behov** ("AbstractFactoryFactory"-problemet): gränssnitt, fabriker eller lager byggda för en flexibilitet som ingen efterfrågar än. Gör koden svårare att navigera, inte lättare att ändra. **Gör istället:** bygg abstraktionen när det andra faktiska behovet uppstår.

## Vägledning och exempel

Kodkvalitet är ett omtvistat ämne, inte en exakt vetenskap. Det redovisas här öppet snarare än att gömmas. Två etablerade men delvis oense skolor ligger till grund för kraven ovan:

- **Clean Code** (Robert C. Martin): förespråkar små funktioner, meningsbärande namn, och att välnamngiven kod gör de flesta kommentarer överflödiga.
- **A Philosophy of Software Design** (John Ousterhout): argumenterar att alltför småskuren funktionsuppdelning kan öka den kognitiva bördan istället för att minska den, och att väl valda kommentarer om *varför* är undervärderade.

Kraven ovan (särskilt BÖR 1 och 4) är medvetet formulerade som en syntes av båda snarare än ett val av den ena. Det här projektets eget arbetssätt (skriv kommentarer bara när "varför" inte är uppenbart) är ett exempel på hur synteser i praktiken ser ut.

Ett exempel på ett verktyg som mäter Cognitive Complexity och cyklomatisk komplexitet konsekvent över många språk är SonarQube (finns även i en gratis Community-variant), nämnt som exempel, inte som ett påbjudet verktyg.

## Undantag

Ett krav på enskilt ansvar (SKA 2) kan tillfälligt frångås för kod som redan finns och inte är föremål för den aktuella ändringen. En liten bugfix ska inte tvinga fram en fullständig omstrukturering av en befintlig klass med flera ansvar. Notera i så fall avsteget kort (t.ex. som en kommentar eller i pull requesten) så att det är synligt som känd teknisk skuld, inte en tyst avvikelse.

## Källor och ramverk

- Robert C. Martin, *Clean Code: A Handbook of Agile Software Craftsmanship*.
- John Ousterhout, *A Philosophy of Software Design*. Se även den dokumenterade diskussionen mellan författarna om metodlängd och kommentarer.
- SOLID-principerna, inklusive dokumenterad kritik mot överanvändning ("AbstractFactoryFactory"-problemet).
- SonarSource: Cognitive Complexity och cyklomatisk komplexitet som kompletterande mått, med vedertagna standardtröskelvärden.
- Singleton som anti-mönster: dolda beroenden, försämrad testbarhet, dependency injection som rekommenderad ersättning.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Kodstandard & stil (kategori B), mekanisk formatering som kompletterar de här designnivå-principerna.
- Arkitektur- och designprinciper på kodnivå (kategori B), hur klasser/moduler organiseras i större strukturer.
- Secure coding-principer (kategori C).
- Kodgranskning (kategori D), processen som kontrollerar att kraven ovan följs, inklusive komplexitetströskelvärdena.
- Testning (kategori D), testbarhet som konsekvens av principerna här.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
