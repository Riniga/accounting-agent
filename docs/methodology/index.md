# Utvecklingsmetodik

## Vad är det här?

Det här är en samlad metodik för hur vi utvecklar mjukvara: en uppsättning principer och krav för hur kod ska skrivas, granskas, säkras och levereras, samt hur vi arbetar tillsammans med AI-verktyg som en del av utvecklingsarbetet.

Metodiken är inte ett regelverk för sin egen skull. Den finns för att svara på en enkel fråga: **hur bygger vi programvara som håller, som går att lita på, förstå, ändra och skydda, oavsett vem som byggde den eller vilket projekt den hör till?**

## Varför finns det här?

Initiativet till metodiken kommer från **NIS2**, EU:s cybersäkerhetslagstiftning, som bland annat ställer krav på hur organisationer ska arbeta säkert när de utvecklar och underhåller mjukvara. NIS2 var det som satte igång arbetet, men metodiken stannar inte vid lagens minimikrav. Den täcker allt som krävs för att utveckla mjukvara med hög kvalitet, inte bara det som är juridiskt obligatoriskt.

## Vem är det här för?

**Den här startsidan är skriven för alla.** Du behöver inte vara utvecklare för att förstå vad metodiken innehåller och varför den finns.

**Kapitlen den länkar vidare till är däremot skrivna för praktiker:** utvecklare, arkitekter, säkerhetsansvariga och andra som faktiskt bygger eller granskar mjukvara. De använder fackspråk och förutsätter teknisk bakgrund. Om du inte är tekniskt insatt är det helt förväntat att enskilda kapitel är svåra att följa i detalj. Den här sidan är till för att du ändå ska förstå helheten, syftet och var i materialet du hittar svar på en fråga.

## Innehåll

Metodiken är indelad i sex områden. Varje område innehåller ett antal kapitel: korta, fristående dokument med tydliga krav och rekommendationer inom ett avgränsat ämne.

### A. Grundförutsättningar

Vilka verktyg och vilken arbetsmiljö en utvecklare behöver, inklusive vilka AI-verktyg som är godkända att använda.

- [**Utvecklingsmiljö & verktyg**](a-grundforutsattningar/utvecklingsmiljo-och-verktyg.md): hur en utvecklares dator och arbetsmiljö ska vara uppsatt för att vara säker och lätt att underhålla. *(Väntar på IT-säkerhet/IAM-verifiering för två punkter innan det räknas som fastställt, se kapitlets sidhuvud.)*
- [**Verktyg för AI-assisterad utveckling**](a-grundforutsattningar/verktyg-for-ai-assisterad-utveckling.md): vilka AI-verktyg som är godkända, och hur de godkänns.

### B. Skriva kod

Hur kod ska se ut för att vara lätt att förstå, ändra och lita på, oavsett programmeringsspråk.

- [**Kodkvalitet & clean code**](b-skriva-kod/kodkvalitet-och-clean-code.md): namngivning, hur stora funktioner bör vara, och hur man undviker onödigt komplicerad kod.
- [**Kodstandard & stil**](b-skriva-kod/kodstandard-och-stil.md): att formatering av kod sköts automatiskt av verktyg, så att det aldrig blir en diskussion mellan människor.
- [**Arkitektur- och designprinciper på kodnivå**](b-skriva-kod/arkitektur-och-designprinciper.md): hur klasser och moduler organiseras i förhållande till varandra, avgränsat från lösningsarkitektur. *(Väntar på en arkitekts granskning innan det räknas som fastställt, se kapitlets sidhuvud.)*
- [**Datamodellering & databasdesign**](b-skriva-kod/datamodellering-och-databasdesign.md): hur databasscheman ändras utan driftstopp, och varför databasen själv, inte bara koden, ska skydda mot felaktig data. *(Kraven är fastställda; en rekommendation väntar på samma arkitektgranskning som kapitlet ovan, se sidhuvudet.)*
- [**Dokumentation av kod**](b-skriva-kod/dokumentation-av-kod.md): vad ett README minst måste innehålla, och hur viktiga tekniska beslut skrivs ner så de går att förstå i efterhand.

### C. Säkerhet

Hur säkerhetsproblem förebyggs, upptäcks och hanteras: i egen kod, i färdiga byggstenar vi återanvänder, och i hur vi hanterar lösenord och nycklar.

- [**Secure coding-principer**](c-sakerhet/secure-coding-principer.md): grundregler för att undvika vanliga säkerhetshål när kod skrivs. *(Väntar på säkerhetsarkitektens granskning innan det räknas som fastställt, se kapitlets sidhuvud.)*
- [**Beroendehantering, paketkällor & signering**](c-sakerhet/beroendehantering-paketkallor-och-signering.md): hur vi håller koll på, granskar och uppdaterar den externa kod vi bygger på.
- [**Sårbarhetshantering, patchning & CVD**](c-sakerhet/sarbarhetshantering-patchning-och-cvd.md): vad som händer när ett säkerhetsproblem upptäcks eller rapporteras utifrån, och hur snabbt det ska åtgärdas. *(Ett krav på "safe harbor"-formulering väntar på juridiskt granskad text i nästa iteration, se sidhuvudet.)*
- [**Hantering av hemligheter**](c-sakerhet/hantering-av-hemligheter.md): hur lösenord, nycklar och liknande hanteras säkert, aldrig i själva koden.

### D. Kvalitetssäkring

Hur vi vet att koden faktiskt fungerar och håller måttet innan den släpps.

- [**Testning**](d-kvalitetssakring/testning.md): hur mycket och vilken typ av tester som behövs, och varför AI-genererad kod har ett extra krav som mänskligt skriven kod inte har.
- [**Kodgranskning**](d-kvalitetssakring/kodgranskning.md): att en pull request alltid ska granskas av en människa innan den slås samman, och vad granskaren faktiskt ska leta efter.
- [**Definition of Done**](d-kvalitetssakring/definition-of-done.md): en kort checklista som samlar de viktigaste kraven från övriga kapitel. När är en ändring faktiskt klar att släppa?

### E. Leverans

Hur kod tas om hand, testas automatiskt och sätts i drift på ett kontrollerat, spårbart sätt.

- [**Versionshantering & branchstrategi**](e-leverans/versionshantering-och-branchstrategi.md): hur grenar i kodhanteringssystemet hålls korta och lätta att slå ihop, hur commit-meddelanden skrivs, och hur en ändring kopplas till varför den gjordes.
- [**CI/CD & automatisering**](e-leverans/ci-cd-och-automatisering.md): varför automatiska kontroller på varje ändring är obligatoriskt, medan automatiserad driftsättning är ett mål snarare än ett krav idag.
- [**Miljöhantering & konfiguration**](e-leverans/miljohantering-och-konfiguration.md): var inställningar (t.ex. lösenord till en databas) hör hemma, och hur dev/test/uat/prod-miljöer hålls från att glida isär från varandra över tid.
- [**Observability: loggning, metrics, tracing, health checks & felhantering**](e-leverans/observability.md): vad koden ska visa upp om sig själv för att gå att felsöka och övervaka i drift.

### F. AI-samarbete i utvecklingsarbetet

Hur AI-verktyg som Claude Code och GitHub Copilot används i det dagliga arbetet: vad de får göra själva, vilken information de får se, och hur vi instruerar dem.

- [**Riktlinjer för AI-assisterade verktyg**](f-ai-samarbete/riktlinjer-for-ai-assisterade-verktyg.md): vad ett AI-verktyg får göra på egen hand, och vad som alltid kräver att en människa godkänner.
- [**Sekretess & dataskydd vid AI-användning**](f-ai-samarbete/sekretess-och-dataskydd-vid-ai-anvandning.md): vilken information som får, respektive aldrig får, delas med ett AI-verktyg.
- [**Prompt- och kontexthantering**](f-ai-samarbete/prompt-och-kontexthantering.md): hur vi skriver och delar instruktioner till AI-verktyg på ett enhetligt och säkert sätt.

## Så läser du ett kapitel

Varje kapitel är kort och byggt på samma mall, oavsett ämne:

- **Syfte:** varför området finns med, i ett stycke.
- **Omfattning och avgränsning:** vad kapitlet tar upp, och vad det uttryckligen lämnar till ett annat kapitel.
- **Krav (SKA):** det som alltid måste följas. Om ett krav inte är uppfyllt ska det synas och åtgärdas, inte bortförklaras.
- **Rekommendationer (BÖR):** god praxis som ska följas om inget särskilt talar emot det i det enskilda fallet.
- **Undvik** (finns bara i vissa kapitel): konkreta saker som ofta *ser ut* som god praxis men som erfarenhetsmässigt gör mer skada än nytta.
- **Vägledning och exempel:** konkret tillämpning, ofta med exempel på verktyg. Exemplen är just exempel, inte påbud om en viss produkt.
- **Undantag:** hur och av vem ett avsteg från kraven kan godkännas, och hur det ska dokumenteras.
- **Källor och ramverk:** varifrån kraven är hämtade, för den som vill läsa vidare eller förstå resonemanget bakom.
- **Relaterat:** vilka andra kapitel som hänger ihop med det här.

Ett kapitel märkt **utkast** i sitt eget sidhuvud är inte färdigt förankrat än, vanligtvis för att det väntar på att en expert (t.ex. en säkerhetsarkitekt eller jurist) ska granska en specifik detalj. Det framgår i så fall tydligt i kapitlets inledning.

## Om AI-samarbete som ett eget område

Att AI-samarbete (område F) är ett eget huvudområde, inte en fotnot, är medvetet. AI-assisterade verktyg är redan en del av det dagliga utvecklingsarbetet, och utan tydliga spelregler för dem uppstår antingen okontrollerad användning eller onödig osäkerhet om vad som är tillåtet. Samma krav på struktur, motivering och källor gäller där som i alla andra områden.

## Nuläge

Metodiken har tagits fram löpande, ett kapitel i taget. **Version 1.0 är komplett: samtliga 21 planerade kapitel finns på plats.** 16 av dem är fastställda. 5 är märkta **utkast** i sina sidhuvuden, eftersom de väntar på en sista genomgång av en namngiven expert (säkerhetsarkitekt, arkitekt, IT-säkerhet/IAM eller jurist) på en avgränsad punkt. Det framgår tydligt i respektive kapitels sidhuvud och i listan ovan. Att ett kapitel är märkt utkast betyder att det går att läsa och använda redan nu, men att den utpekade detaljen inte är slutgiltigt bekräftad.

Metodiken är avsiktligt generell: den ska fungera för många olika projekt och team, inte peka ut enskilda verktyg eller leverantörer som obligatoriska. Där ett verktyg ändå nämns är det som exempel för att göra ett krav konkret, inte som ett påbud.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Vad:** Startsida för utvecklingsmetodiken, version 1.0
