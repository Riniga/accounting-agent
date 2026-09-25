# Utvecklingsmiljö & verktyg

**Kategori:** A. Grundförutsättningar
**Status:** utkast, två punkter väntar på verifiering från IT-säkerhet/IAM-ansvariga innan de kan fastställas (se Källor och ramverk)
**Senast uppdaterad:** 2026-09-07
**Underlag:** 2026-09-04-utvecklingsmiljo-och-verktyg.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

En utvecklares dator och konto hör till organisationens mest privilegierade identiteter. Åtkomst till källkod, CI/CD-pipelines, molnkonton och ofta produktionsnära system gör den till ett högvärdesmål, inte en perifer IT-fråga. Det här dokumentet fastställer hur utvecklarens arbetsyta ska vara isolerad, hanterad och spårbar, och hur projektspecifika miljöer och verktyg hanteras, utan att låsa metodiken till en specifik teknik som VDI.

Det här är medvetet det sista kapitlet som skrivs, så att det kan förankras i och referera till hela den färdiga metodiken snarare än stå för sig själv.

## Omfattning och avgränsning

Omfattar utvecklarens generella arbetsyta: datorn/arbetsmiljön, nätverksåtkomst, administratörsrättigheter, projektspecifika utvecklingsmiljöer, och kontroll över vilka verktyg som installeras.

Omfattar **inte**:

- Vilka AI-verktyg som är godkända, se Verktyg för AI-assisterad utveckling, som är en fördjupad delmängd av "verktyg" med egen behandling.
- Applikationens driftmiljöer (dev/test/uat/prod), se Miljöhantering & konfiguration. Ett projekts devcontainer hör hit om syftet är utvecklarens arbetsyta, dit om syftet är en miljö applikationen faktiskt driftas i.
- Beroenden koden har (paket som skeppas med applikationen), se Beroendehantering, paketkällor & signering. Samma grundprincip (verifierade källor) gäller, men tillämpad på olika saker.
- Grundregeln att hemligheter aldrig ska finnas i kod, se Hantering av hemligheter. Berörs här bara i den mån det gäller utvecklarens lokala miljö (t.ex. att en lokal miljöfil med hemligheter aldrig checkas in).

## Krav (SKA)

1. Utvecklarens arbetsyta ska vara isolerad, hanterad och spårbar. Metodiken kravställer egenskapen, inte en specifik teknik. VDI/DaaS, molnbaserad utvecklingsmiljö (CDE), säker webbläsare/enklav och dedikerad fysisk dator är alla giltiga sätt att uppfylla kravet.
2. Nätverksåtkomst ska beviljas per resurs utifrån identitet och sammanhang (Zero Trust Network Access), inte enbart genom att placera utvecklingsmiljön i ett visst nätverkssegment. Ett nätverkssegment (VLAN eller motsvarande) kan vara ett av flera lager, men ska inte vara den enda kontrollen.
3. Om en separat administrativ identitetsmiljö för utveckling införs, ska den följa den moderna Enterprise Access-/Privileged Access-modellen (tiermodell), inte den avrådda Red Forest/ESAE-arkitekturen. Riktningen på ett eventuellt förtroende mellan miljöerna är central: den mer skyddade miljön får administrera den mindre skyddade, aldrig tvärtom.
4. Utvecklare ska arbeta med normalt begränsade rättigheter. Förhöjda rättigheter beviljas tillfälligt, spårat och tidsbegränsat (just-in-time), inte som ett stående adminkonto.
5. Projektspecifika utvecklingsmiljöer ska beskrivas deklarativt och versionshanteras tillsammans med koden. Miljön hanteras som kod, och teknikvalet är fritt per projekt.
6. Grundmiljön (bas-OS, standardverktyg) ska utgå från en gemensamt underhållen, versionshanterad grundavbildning.
7. Applikationskontroll (endast explicit godkänd mjukvara tillåts köras) ska tillämpas på utvecklardatorn där plattformen tekniskt stödjer det. Konkret mekanism väljs utifrån plattform.

## Rekommendationer (BÖR)

1. Installation av verktyg och programvara bör begränsas till godkända/verifierade källor (källkontroll). Detta är nedgraderat till rekommendation, inte krav, eftersom det inte alltid finns en gemensam, godkänd källa/spegling i organisationen att peka mot (se Källor och ramverk). Skärps till SKA när en sådan finns på plats.

## Vägledning och exempel

**Fyra giltiga mönster för arbetsytan (krav 1), inte bara VDI:**

| Mönster | Passar bäst för |
|---|---|
| VDI/DaaS (Desktop as a Service) | Persistent, fullständig desktop-upplevelse, äldre/specialiserade applikationer |
| Molnbaserad utvecklingsmiljö (CDE) | Ren kodutveckling, snabb onboarding, containerbaserade team |
| Säker webbläsare/enklav | Roller som mest arbetar i webbaserade verktyg |
| Dedikerad fysisk utvecklingsdator | Extrema prestandakrav (undantag, inte standardval) |

**För organisationer med en central IT-miljö:** VDI/DaaS och molnbaserad utvecklingsmiljö är ofta de realistiska förstahandsmönstren. Dedikerad fysisk dator är ett undantag för enstaka fall med extrema prestandakrav, inte något att planera för generellt.

**Byggstenarna för identitetsbaserad nätverksåtkomst (krav 2) finns ofta redan delvis i organisationen:** till exempel finmaskig LAN-segmentering utöver ren VLAN och en central identitetstjänst (t.ex. Entra ID). Det handlar då sannolikt om att tillämpa befintlig kapacitet på utvecklarmiljön specifikt, inte bygga från grunden.

**Just-in-time-åtkomst (krav 4) har ofta redan en grund i organisationen:** till exempel att utvalda användare har separata adminkonton för elevering. Metodiken formaliserar i så fall det mönstret snarare än inför ett nytt.

**Ägarskap av grundavbildningen (krav 6) ligger utanför den här metodikens avgränsning:** den underhålls av IT-drift och eventuella samarbetspartner. Metodiken refererar till att den finns och underhålls, äger den inte (samma resonemang som redan etablerat för infrastruktur som kod i Miljöhantering & konfiguration och Hantering av hemligheter).

**Applikationskontroll (krav 7), exempel:** på Windows är Windows Defender Application Control (WDAC) det nu rekommenderade verktyget. Vanligt arbetssätt: skanna en golden image för att generera en baslinjepolicy, och peka ut ett godkänt distributionsverktyg som betrodd installationskälla.

## Undantag

Ett projekt eller system som ännu inte kan uppfylla applikationskontroll (krav 7) på grund av teknisk begränsning kan använda en dokumenterad, tillfällig kompenserande kontroll (t.ex. manuell granskning av installerad mjukvara), under förutsättning att en plan finns för att stänga gapet.

## Källor och ramverk

- NIST SP 800-218 (SSDF), praktikgrupp PO.5 (miljöseparation, riskbaserad härdning av utvecklingsendpoints).
- Microsoft: Secure the developer environment for Zero Trust; CyberArk: Secure Developer Workstations.
- Jämförelse av VDI, Desktop as a Service och molnbaserade utvecklingsmiljöer (CDE) som arkitekturmönster.
- Nätverkssegmentering vs. Zero Trust Network Access; Microsofts pensionering av ESAE/Red Forest till förmån för Enterprise Access-modellen.
- Windows Defender Application Control (WDAC) som exempel på applikationskontroll.

**Krävs innan detta dokument kan fastställas fullt ut:**

1. **Verifiera med IT-säkerhet/IAM-ansvariga** om organisationens befintliga IAM-lösning redan följer Enterprise Access-/Privileged Access-modellen, eller bygger på den avrådda Red Forest/ESAE-arkitekturen (krav 3).
2. **Ta ställning till en global paketkälla/spegling** för utvecklarverktyg: antingen etablera en sådan, eller acceptera att källkontroll (BÖR 1) förblir en rekommendation tills en finns.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Verktyg för AI-assisterad utveckling (kategori A), fördjupad behandling av en delmängd av "verktyg".
- Miljöhantering & konfiguration (kategori E), applikationens driftmiljöer, till skillnad från utvecklarens arbetsyta här.
- Beroendehantering, paketkällor & signering (kategori C), samma källkontrollsprincip, tillämpad på kodens beroenden istället för utvecklarverktyg.
- Hantering av hemligheter (kategori C), hur hemligheter hanteras, även lokalt hos utvecklaren.
- CI/CD & automatisering (kategori E), pipelinen utvecklarens arbetsyta i slutänden levererar till.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Utvecklingsmetodiken, version 1.0
