# Sårbarhetshantering, patchning & CVD

**Kategori:** C. Säkerhet
**Status:** utkast, safe harbor-formuleringen (krav 2) väntar på juridiskt granskad text i nästa iteration
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-sarbarhetshantering-patchning-och-cvd.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Det här dokumentet är den direkta operationaliseringen av NIS2 artikel 21.2(e):s krav på sårbarhetshantering och sårbarhetsavslöjande, identifierat som ett rent gap när ämnesstrukturen först stämdes av mot NIS2. Det fastställer vad som händer efter att en sårbarhet upptäckts eller rapporterats: prioritering, åtgärds-SLA, och en CVD-policy (coordinated vulnerability disclosure) med säkerhetskontakt för externt rapporterade sårbarheter.

## Omfattning och avgränsning

Omfattar hantering av sårbarheter, oavsett källa (egen kod, tredjepartsberoenden, extern rapport), efter att de upptäckts eller rapporterats.

Omfattar **inte**:

- Att förebygga/upptäcka sårbarheter i egen kod (SAST, hotmodellering), se Secure coding-principer.
- Att förebygga/upptäcka sårbarheter i beroenden (SCA), se Beroendehantering, paketkällor & signering.
- Hantering av hemligheter/credentials, eget spår.

## Krav (SKA)

1. En publicerad CVD-policy ska finnas, med en säkerhetskontakt publicerad via security.txt (RFC 9116) på en känd plats. Ägs centralt av säkerhetsarkitekt/säkerhetsavdelning.
2. CVD-policyn ska innehålla explicit safe harbor-språk för forskare som agerar i god tro, inom scope, utan att störa drift eller bryta mot integritet.
3. Sårbarheter, oavsett källa, ska prioriteras efter CVSS-baserad allvarlighetsgrad, med kortare åtgärdstid för aktivt utnyttjade sårbarheter oavsett CVSS-poäng.
4. Sårbarhetsallvarlighet ska integreras som en kompletterande dimension i Skanskas befintliga SLA/OLA-struktur per tjänst, inte hanteras som ett fristående, parallellt system.
5. SLA-efterlevnad ska mätas och rapporteras löpande, inte bara antas eller fastställas en gång och sedan glömmas.

## Rekommendationer (BÖR)

1. CVSS-baserade riktvärden föreslås som utgångspunkt vid komplettering av SLA/OLA-strukturen (krav 4): Kritisk 15 dagar (24–72 timmar om aktivt utnyttjad), Hög 30 dagar, Medel 90 dagar, Låg 180 dagar. Justeras per tjänsts befintliga avtal.
2. En extern forskare tillåts offentliggöra en sårbarhet när fixen är klar och tillåtelse getts, eller 90 dagar efter rapportering, beroende på vad som inträffar först.

## Vägledning och exempel

**security.txt** placeras på en känd, förutsägbar plats (`/.well-known/security.txt`) enligt RFC 9116-formatet. Filen är maskinläsbar och det första automatiserade skanningsverktyg och säkerhetsforskare letar efter. Samma bedömning som i Beroendehantering, paketkällor & signering gäller: EU CRA efterfrågar det uttryckligen men är sannolikt inte utlöst för Skanska. Filen förblir ändå god praxis.

**CISA:s officiella Vulnerability Disclosure Policy-mall** är ett bra utgångsexempel för hela policyns struktur (scope, hur en rapport skickas in, safe harbor, förväntade tider, förbjudna testaktiviteter), inte för att kopieras rakt av, men som ett strukturellt facit.

**Om safe harbor-texten (krav 2):** juridiska resurser hos Skanska finns för att ta fram den, men arbetet är medvetet skjutet till nästa iteration av den här metodiken. Kravet att safe harbor-språk ska finnas gäller redan nu; den exakta, juridiskt granskade lydelsen är det som saknas.

**Var ärlig om verklighetsgapet:** branschdata visar att genomsnittlig faktisk åtgärdstid för kritiska sårbarheter (60 dagar) ofta ligger långt bortom typiska SLA:er. Krav 5 (mätning och rapportering) finns specifikt för att göra det gapet synligt tidigt, inte för att en SLA-tabell i sig löser problemet.

## Undantag

För system där en sårbarhet inte kan åtgärdas inom den överenskomna SLA:n (t.ex. ett system nära utfasning, eller ett beroende utan tillgänglig patch) kan en tillfällig, dokumenterad kompenserande kontroll användas istället (t.ex. nätverksisolering, extra övervakning), under förutsättning att avsteget är godkänt av den som äger tjänstens SLA/OLA och att en plan finns för slutgiltig åtgärd.

## Källor och ramverk

- ISO/IEC 29147 (vulnerability disclosure) och ISO/IEC 30111 (vulnerability handling).
- RFC 9116: security.txt.
- CISA:s Vulnerability Disclosure Policy-mall och vägledning för att etablera ett CVD-program.
- CVSS-baserade branschriktvärden för sårbarhetsåtgärd, inklusive den dokumenterade skillnaden mellan typisk SLA och faktisk åtgärdstid.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Secure coding-principer (kategori C), förebyggande/upptäckt i egen kod.
- Beroendehantering, paketkällor & signering (kategori C), förebyggande/upptäckt i beroenden, samma CRA/security.txt-bedömning.
- Hantering av hemligheter (kategori C).

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
