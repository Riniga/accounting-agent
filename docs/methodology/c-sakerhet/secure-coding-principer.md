# Secure coding-principer

**Kategori:** C. Säkerhet
**Status:** utkast, kräver säkerhetsarkitektens granskning innan fastställande (se Vägledning och Källor)
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-secure-coding-principer.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Det här dokumentet är den direkta operationaliseringen av NIS2 artikel 21.2(e) för mjukvaruutveckling: grundregler mot vanliga sårbarhetsklasser, hotmodellering, och automatiserad säkerhetstestning (SAST/DAST) i utvecklingsflödet, så att sårbarheter förebyggs istället för att bara åtgärdas efter fynd.

**Viktig läsanvisning:** SAST/DAST-området krävde avvägningar utanför vad som gick att förankra i Skanskas faktiska verktygsläge under den här sessionen (ingen tillgänglig säkerhetsexpertis vid tidpunkten). Principerna nedan är en välgrundad utgångspunkt, inte ett färdigt, Skanska-verifierat beslut. Se Källor för vad som specifikt behöver stämmas av med säkerhetsarkitekten innan status kan bli "fastställd".

## Omfattning och avgränsning

Omfattar sårbarheter i **egen** kod: grundregler, hotmodellering, och automatiserad säkerhetstestning (SAST/DAST).

Omfattar **inte**:

- Tredjepartsberoenden, se Beroendehantering, paketkällor & signering.
- Vad som händer efter att en sårbarhet upptäckts eller rapporterats (prioritering, patchning, CVD-policy), se Sårbarhetshantering, patchning & CVD.
- Hantering av hemligheter/credentials, eget spår, trots att det tekniskt är en sårbarhetsklass.
- Den generella teststrategin (enhetstester, täckningsmål), se Testning. Säkerhetstestning är en specialiserad delmängd som hör hit eftersom den är säkerhetsspecifik.

## Krav (SKA)

1. Utvecklare ska ha grundläggande kännedom om OWASP Top 10 (nuvarande upplaga: 2025) och CWE Top 25, för de sårbarhetsklasser som är relevanta för aktuellt språk/plattform.
2. SAST (statisk säkerhetsanalys) ska köras automatiskt vid varje pull request/commit, en teknisk spärr i pipelinen, inte en valfri eller manuell kontroll.
3. DAST (dynamisk säkerhetsanalys) ska köras mot en driftsatt test-/stagingmiljö innan produktionssättning, för alla applikationer som exponerar externa gränssnitt.
4. Lättviktig hotmodellering (t.ex. STRIDE) genomförs för varje feature eller förändring med betydande säkerhetspåverkan, inte som en årlig, tung engångsövning.

## Rekommendationer (BÖR)

1. Hotmodellering görs tidigt, i designfasen, innan kod skrivs. Det är billigast att agera på fynd då.
2. Sårbarheter som hittas av SAST/DAST prioriteras och åtgärdas enligt samma allvarlighetsbaserade process som beskrivs i Sårbarhetshantering, patchning & CVD.
3. SAST/DAST körs i samma CI-pipeline som övriga automatiska kontroller, men rapporteras och grindas som en egen, namngiven säkerhetskontroll, inte dold inuti en generell "tester godkända"-status. Ger säkerhetsfynd egen synlighet och egna, oberoende justerbara blockeringströsklar.

## Vägledning och exempel

**Hotmodellering** kräver inget särskilt verktyg för att komma igång: ett dataflödesdiagram på en whiteboard och STRIDE:s sex kategorier (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) räcker för att identifiera konkreta tekniska brister.

**SAST/DAST-verktyg (exempel, inte verifierade mot Skanskas upphandling):** verktyg med en gratis/öppen kärna sänker tröskeln att komma igång innan ett eventuellt upphandlat verktyg finns på plats: Semgrep eller CodeQL för SAST, OWASP ZAP för DAST. Detta är en riktning, inte ett beslut: verifiera med säkerhetsarkitekten vad som redan är godkänt eller upphandlat hos Skanska innan ett projekt låser sig vid ett specifikt verktyg.

**OWASP Top 10:2025** flyttade tyngdpunkten mot konfiguration och leverantörskedja: Security Misconfiguration är nu #2, och en ny kategori för brister i mjukvaruleverantörskedjan kom in på #3, direkt kopplat till Beroendehantering, paketkällor & signering.

## Undantag

Om ett äldre system inte tekniskt går att köra SAST/DAST mot (t.ex. inkompatibel plattform), kan en tillfällig, dokumenterad kompenserande kontroll (t.ex. en manuell säkerhetsgranskning inför release) användas istället, under förutsättning att en plan finns för att antingen få verktygsstöd på plats eller fasa ut systemet.

## Källor och ramverk

- [OWASP Top 10:2025](https://owasp.org/Top10/2025/), senaste upplagan, fastställd januari 2026.
- OWASP ASVS och CWE Top 25: kompletterande referenslistor (applikationsnivå-risker respektive konkreta kodmönster).
- STRIDE-hotmodellering, refererad av bl.a. Microsofts Security Development Lifecycle.
- Dokumenterad effekt av shift-left-säkerhetstestning (SAST tidigt, DAST mot driftsatt miljö): upp till 60 % färre produktionssårbarheter, upp till 90 % lägre åtgärdskostnad vid tidig upptäckt.

**Krävs innan detta dokument kan fastställas:** avstämning med Skanskas säkerhetsarkitekt om (1) befintligt SAST/DAST-läge och redan godkända/upphandlade verktyg, och (2) om de föreslagna kraven (särskilt blockeringströsklarna) matchar Skanskas faktiska risktolerans. Se avsnittet "Kvarstående uppföljning" i det interna forskningsunderlaget.

## Relaterat

- Beroendehantering, paketkällor & signering (kategori C), tredjepartsberoenden, direkt kopplat till OWASP Top 10:2025:s nya #3-kategori.
- Sårbarhetshantering, patchning & CVD (kategori C), vad som händer efter ett fynd.
- Hantering av hemligheter (kategori C).
- Testning (kategori D), den generella teststrategin som säkerhetstestningen kompletterar.
- Kodgranskning (kategori D).

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
