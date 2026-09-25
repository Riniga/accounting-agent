# Riktlinjer för AI-assisterade verktyg

**Kategori:** F. AI-samarbete i utvecklingsarbetet
**Status:** fastställd
**Senast uppdaterad:** 2026-09-05
**Underlag:** 2026-09-05-riktlinjer-for-ai-assisterade-verktyg.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Nästan alla utvecklare använder redan AI-assisterade verktyg i sitt arbete. Utan tydliga, centrala regler för vad ett sådant verktyg får göra på egen hand uppstår antingen okontrollerad autonomi (AI som committar, sammanslår eller driftsätter utan mänsklig kontroll) eller otydlighet som gör att varje team improviserar sina egna gränser. Det här dokumentet fastställer vad ett godkänt AI-verktyg får göra autonomt i utvecklingsarbetet, och vilka granskningskrav som gäller för AI-genererad kod.

## Omfattning och avgränsning

Omfattar AI-verktygets *handlingsutrymme* när det används i utvecklingsarbete: vad det får göra på egen hand, och vad som alltid kräver ett mänskligt beslut.

Omfattar **inte**:

- Vilka verktyg som är godkända och hur de anskaffas, se ämnesspåret Verktyg för AI-assisterad utveckling.
- Vilken kod eller data som får matas in i ett AI-verktyg, se ämnesspåret Sekretess & dataskydd vid AI-användning.
- Den generella kodgranskningsprocessen (checklista, roller, verktyg), se ämnesspåret Kodgranskning. Det här dokumentet lägger AI-specifika regler ovanpå den processen, utan att definiera den på nytt.

## Krav (SKA)

1. AI-verktyg får aldrig committa eller sammanslå direkt till skyddade grenar (t.ex. main). Det ska genomdrivas tekniskt med grenskydd, obligatoriska CI-kontroller och krav på minst ett mänskligt godkännande, inte bara som en skriven regel.
2. Produktionsskrivande åtgärder (driftsättning, databasändringar, destruktiva kommandon) kräver alltid ett explicit mänskligt godkännande i stunden. Ingen sådan åtgärd får ske helt autonomt, oavsett verktygets uppmätta träffsäkerhet.
3. AI-genererad kod ska granskas av en människa på samma sätt som mänskligt skriven kod, plus genomgå en automatiserad säkerhetsskanning innan sammanslagning. Aldrig en lättare granskning för att koden är AI-genererad.
4. En namngiven människa ska alltid vara ansvarig för det som slutligen sammanslås eller släpps, oavsett vem eller vad som skrev koden. Vem som granskade och godkände ska vara spårbart i efterhand.
5. Autonominivån för ett AI-verktyg ska kalibreras efter risk och reversibilitet: lågrisk-, reversibla åtgärder kan tillåtas mer autonomt; oåterkalleliga eller högriskåtgärder ska alltid gå via mänskligt godkännande.
6. Guardrails ska implementeras tekniskt (grenskydd, begränsade behörigheter, obligatoriska kontroller, pull requests, code coverage-krav). En skriven policy eller promptinstruktion räcker inte ensamt.

## Rekommendationer (BÖR)

1. Pull requests där ett AI-verktyg bidragit bör markeras som sådana, konkret som ett fält eller en etikett på pull requesten, inte en commit-trailer. *(Idag BÖR snarare än SKA eftersom det inte går att tillförlitligt tvinga fram utan att pull request först är obligatoriskt generellt. Bör skärpas till SKA och bakas in i en obligatorisk PR-mall den dagen pull request blir tvingande, se Kodgranskning.)*

## Vägledning och exempel

Kod som ligger i Azure DevOps eller GitHub gör kraven ovan praktiskt genomförbara centralt: grenskydd, obligatoriska granskare, obligatoriska CI-kontroller (inklusive code coverage) och sammanslagningsspärrar finns som inbyggda funktioner i båda plattformarna. Det handlar om att aktivera och kravställa dem, inte bygga nytt.

En viktig nyans för krav 2: ett mänskligt godkännande räcker inte om personen som godkänner inte förstår vad den godkänner. Ett "ja" på en driftsättning eller ett destruktivt databaskommando ska föregås av tillräcklig information för att beslutet är informerat, inte en reflexmässig bekräftelse.

## Undantag

Ett team kan i en avgränsad, dokumenterad pilot tillåta högre autonomi än vad kraven ovan annars medger (t.ex. automatiserad sammanslagning på en isolerad experimentgren), under förutsättning att:

- inga produktionssystem eller skyddade huvudgrenar berörs,
- avvikelsen är tidsbegränsad och dokumenterad, inklusive skälet till den, och
- en namngiven person är ansvarig för uppföljning och för att avvikelsen upphör när piloten avslutas.

Ett sådant undantag upphäver aldrig kravet på mänskligt godkännande för produktionsskrivande åtgärder (krav 2).

## Källor och ramverk

- Kalibrerad autonomi och human-in-the-loop-mönster inom AI-agent-styrning (branschpraxis 2026).
- Tekniska guardrails för kodningsagenter: grenskydd, begränsade IAM-roller, obligatoriska kontroller på infrastrukturnivå snarare än promptnivå.
- Praxis kring ansvar och spårbarhet för AI-genererad kod, samt attribution/märkning av AI-bidrag i versionshantering.
- EU AI Act, artikel 14 (mänsklig tillsyn) och artikel 26, bedömda som sannolikt inte direkt tillämpliga på ett internt kodningsverktyg (gäller högrisk-AI-system), men i linje med samma riktning som kraven ovan.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Verktyg för AI-assisterad utveckling (kategori A), vilka verktyg som är godkända. Krav 6 där ("verktyget ska tekniskt stödja guardrails") är direkt kopplat till kraven i det här dokumentet.
- Sekretess & dataskydd vid AI-användning (kategori F), vilken data som får matas in.
- Kodgranskning (kategori D), den generella granskningsprocessen som kraven ovan bygger vidare på, samt platsen där ett ev. framtida krav på tvingande pull request avgörs.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Utvecklingsmetodiken, version 1.0
