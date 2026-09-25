# Sekretess & dataskydd vid AI-användning

**Kategori:** F. AI-samarbete i utvecklingsarbetet
**Status:** fastställd
**Senast uppdaterad:** 2026-09-05
**Underlag:** 2026-09-05-sekretess-och-dataskydd-vid-ai-anvandning.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Ett godkänt, säkert AI-verktyg (spår: Verktyg för AI-assisterad utveckling) skyddar inte automatiskt mot att fel data matas in i det. Det här dokumentet fastställer vilken kod och data som får matas in i AI-assisterade utvecklingsverktyg, så att företagshemligheter, personuppgifter och annan känslig information inte läcker till en extern tjänst, oavsett hur pålitligt verktyget i övrigt är.

## Omfattning och avgränsning

Omfattar vilken data och kod som är tillåten *indata* till ett AI-verktyg.

Omfattar **inte**:

- Om ett verktyg är godkänt att använda överhuvudtaget, se Verktyg för AI-assisterad utveckling.
- Vad AI får göra autonomt med det den fått tillgång till, se Riktlinjer för AI-assisterade verktyg.
- Att hemligheter aldrig ska finnas lagrade i kod, se Hantering av hemligheter. Det här dokumentet adresserar en bredare, AI-specifik risk: att hemligheter läcker via AI:ns kontext (miljövariabler, konfigurationsfiler, terminalutdata) även när de i teorin aldrig borde finnas i själva källkoden.
- Vilken klassificering data i en given driftmiljö (dev/test/uat/prod) faktiskt har, se Miljöhantering & konfiguration. Det här dokumentet utgår från datans klassificering, oavsett vilken miljö den råkar ligga i.

## Krav (SKA)

1. AI-hantering av data styrs av organisationens befintliga dataklassificeringsmodell (Konfidentialitet, Riktighet, Tillgänglighet). Konfidentialitetsdimensionen ska ha en uttrycklig, skriven regel för vad som gäller vid AI-användning per klassningsnivå.
2. Data med hög konfidentialitetsklassning får aldrig matas in i ett AI-verktyg, oavsett om verktyget i övrigt är godkänt. Endast data med tillräckligt låg konfidentialitetsklassning, enligt regeln i krav 1, är tillåten indata.
3. Om material som matas in i ett AI-verktyg kan innehålla personuppgifter, ska ett giltigt personuppgiftsbiträdesavtal (DPA) finnas med leverantören. Ansvaret för detta kan aldrig läggas över på leverantören.
4. Om ett AI-verktyg är agentiskt och kan vidarebefordra data till ytterligare tredjepartstjänster, ska det klarläggas vilka dessa är och att de omfattas av motsvarande avtalsmässiga skydd som huvudverktyget.
5. Hemligheter (nycklar, lösenord, tokens) ska aktivt skannas bort eller maskeras innan de når ett AI-verktygs kontext. Miljövariabler, konfigurationsfiler och terminalutdata är kända läckagevägar, inte bara källkoden.
6. Hemlighetsskanning riktad mot AI-kontext sker i flera oberoende steg: vid skrivning, före commit, innan kontext skickas till modellen, och vid pull request.
7. Granskning av AI-genererad kod (se Riktlinjer för AI-assisterade verktyg) inkluderar uttryckligen sökning efter hårdkodade hemligheter. AI-ursprung är aldrig skäl till lättare granskning på den punkten.
8. Data i utvecklings- och testmiljöer ska vara anonymiserad eller syntetisk testdata. I miljöer som UAT, där vissa system hanterar riktig produktionsdata, avgörs vad som gäller av datans faktiska klassificering (krav 1–2), inte av miljöns namn.

## Rekommendationer (BÖR)

1. Utöver de obligatoriska kontrollpunkterna i krav 6 bör lokal sekretessmaskning övervägas direkt i utvecklarens editor/terminal, så att en hemlighet aldrig blir synlig för modellen i första läget. Om modellen aldrig ser hemligheten kan den heller inte läcka den.

## Vägledning och exempel

**Obekräftat och under uppföljning:** om det befintliga Microsoft-avtalet innehåller ett personuppgiftsbiträdesavtal som uttryckligen täcker Copilots AI-specifika databehandling (krav 3) är i skrivande stund inte verifierat. Kravet gäller oavsett. Det är själva verifieringen som är en öppen uppgift för den som förvaltar avtalet.

Dev-/testmiljöns krav på anonymiserad/syntetisk data (krav 8) är redan etablerad praxis på många håll. Det här dokumentet bekräftar den snarare än inför något nytt. UAT kräver mer eftertanke: fråga alltid "vilken klassificering har den här datan faktiskt, i det här systemet?" innan något UAT-material matas in i ett AI-verktyg. Anta aldrig att UAT per definition är säkert bara för att det inte heter "produktion".

## Undantag

Ett undantag från konfidentialitetsgränsen i krav 2 kan medges för ett specifikt, avgränsat behov (t.ex. felsökning som kräver verklig data), men endast om:

- den som äger datans klassificering (dataägare/motsvarande) gett ett skriftligt, dokumenterat godkännande i förväg,
- undantaget är tidsbegränsat och gäller en namngiven uppgift, inte generell användning, och
- kravet på personuppgiftsbiträdesavtal (krav 3) ändå är uppfyllt om personuppgifter kan förekomma.

## Källor och ramverk

- GDPR artikel 28: krav på personuppgiftsbiträdesavtal (DPA) mellan personuppgiftsansvarig och biträde. Ansvaret för efterlevnad kan inte läggas över på leverantören.
- Risk för dolda, oavtalade biträdesled när agentiska AI-verktyg internt anropar ytterligare tredjepartstjänster.
- Dokumenterad, betydande ökning (81 % under 2025) av läckta hemligheter kopplade till AI-assisterade kodningsverktyg, inklusive ett eget stort läckageläge via MCP-konfigurationsfiler.
- Praxis för flerskiktad sekretesskanning: vid skrivning, före commit, innan kontext skickas till modellen, vid pull request.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Verktyg för AI-assisterad utveckling (kategori A), vilka verktyg som är godkända.
- Riktlinjer för AI-assisterade verktyg (kategori F), vad AI får göra, inklusive granskningskravet i krav 7 här.
- Hantering av hemligheter (kategori C), grundregeln att hemligheter aldrig ska finnas i kod.
- Miljöhantering & konfiguration (kategori E), klassificering av data per driftmiljö, avgörande för UAT-nyansen i krav 8.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Utvecklingsmetodiken, version 1.0
