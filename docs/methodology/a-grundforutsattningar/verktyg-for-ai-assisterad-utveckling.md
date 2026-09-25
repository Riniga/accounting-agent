# Verktyg för AI-assisterad utveckling

**Kategori:** A. Grundförutsättningar
**Status:** fastställd
**Senast uppdaterad:** 2026-09-05 (kompletterad efter spår 5)
**Underlag:** 2026-09-04-verktyg-for-ai-assisterad-utveckling.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

De allra flesta utvecklare använder redan AI-assisterade verktyg i sitt arbete, oavsett om organisationen har tagit ställning till det eller inte. Utan ett tydligt, känt sätt att godkänna verktyg uppstår antingen okontrollerad användning ("shadow AI") eller att arbete i onödan bromsas av att ingen vet vad som är tillåtet. Det här dokumentet fastställer *hur* ett AI-assisterat utvecklingsverktyg blir godkänt att använda hos Skanska, inte vilket enskilt verktyg som är bäst.

## Omfattning och avgränsning

Omfattar godkännande, anskaffning och konfiguration av AI-assisterade utvecklingsverktyg (agentiska CLI-/IDE-verktyg, IDE-integrerade kodassistenter, och AI-chattverktyg använda i utvecklingsarbete).

Omfattar **inte**:

- Vad ett godkänt verktyg får göra autonomt när det används (t.ex. om AI får committa direkt), se ämnesspåret Riktlinjer för AI-assisterade verktyg.
- Vilken kod eller data som faktiskt får matas in i ett AI-verktyg, se ämnesspåret Sekretess & dataskydd vid AI-användning.
- Innehåll i och arbetssätt kring instruktionsfiler (t.ex. CLAUDE.md-motsvarigheter), se ämnesspåret Prompt- och kontexthantering.
- Utvecklarens generella verktygsmiljö och dator, se ämnesspåret Utvecklingsmiljö & verktyg.

## Krav (SKA)

1. AI-assisterade utvecklingsverktyg får endast användas via organisationens egna avtal (business-/enterprise-nivå). Personliga eller konsumentkonton får inte användas för arbetsrelaterat innehåll.
2. Avtalet med leverantören ska garantera att indata (prompts, kod, kontext) inte används för att träna leverantörens modeller, samt ange en definierad, kort datalagringstid.
3. Ett AI-verktyg ska vara godkänt genom den etablerade processen för nya SaaS-/molnverktyg (Digi-ORA), utökad med de AI-specifika kriterierna i det här dokumentet, innan det används i utvecklingsarbete.
4. En uppdaterad lista över godkända AI-verktyg ska finnas tillgänglig för alla utvecklare.
5. Åtkomst till godkända AI-verktyg ska knytas till organisationens ordinarie identitetshantering (SSO) och följa gällande process för nyanställning, rollbyte och avslut, inte fristående kontohantering per verktyg och utvecklare.
6. Ett verktyg godkänns endast om det tekniskt går att begränsa till de handlingsregler som gäller för AI i utvecklingsarbetet (se Riktlinjer för AI-assisterade verktyg), t.ex. stödjer arbete via grenar/pull requests och kan nekas direkt skrivrätt till skyddade grenar eller produktionssystem. Ett verktyg som bara kan instrueras via prompt att avstå, utan teknisk spärr, uppfyller inte kravet. *(Tillagd 2026-09-05, efter genomgång av spår 5.)*

## Rekommendationer (BÖR)

1. Om ett godkänt verktyg stödjer MCP (Model Context Protocol) eller motsvarande externa integrationer, bör dessa granskas separat utifrån minsta-privilegium, med en förd inventering och autentiserade, loggade anslutningar. *(Nedgraderat medvetet från krav till rekommendation eftersom området ännu inte bedöms moget nog för Skanska att kravställa hårt.)*
2. Godkännandekriterierna bör struktureras efter ett etablerat ramverk (t.ex. NIST AI RMF: Govern, Map, Measure, Manage) snarare än en egen, improviserad checklista.
3. Ett verktygs stöd för organisationsgemensamma instruktionsfiler bör vägas in vid godkännande, även om innehållet i sådana filer hör till ett annat ämnesspår.

## Vägledning och exempel

Idag (2026) är **GitHub Copilot** det godkända verktyget för AI-assisterad kodning hos Skanska, möjliggjort av det befintliga Microsoft-avtalet. Det är ett konkret exempel på hur krav 1–2 uppfylls i praktiken, inte en begränsning till just det verktyget. Microsoft Copilot är godkänt som officiellt AI-verktyg för andra ändamål, men används i praktiken inte för kodning.

Ett nytt AI-verktyg som saknar organisationsavtal kan inte godkännas för användning på riktiga projekt, oavsett hur välfungerande det är. Avtalsläget kommer alltid före funktionalitet i bedömningen.

## Undantag

Ett tidsbegränsat, dokumenterat undantag kan medges för att pilota eller utforska ett ännu inte formellt godkänt verktyg (t.ex. i ett internt utrednings- eller metodikarbete), under förutsättning att:

- inget känsligt eller konfidentiellt material (företagshemligheter, personuppgifter, icke-offentlig information) någonsin matas in i verktyget,
- undantaget och skälet till det är dokumenterat i det aktuella arbetets egna underlag, och
- verktyget inte används för att skriva eller ändra kod i produktionssatta system.

Ett sådant undantag ersätter inte ett formellt godkännande och ger inte rätt att använda verktyget utanför den avgränsade uppgiften det beviljades för.

## Källor och ramverk

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework): struktur för godkännandeprocessen (Govern/Map/Measure/Manage), inklusive vägledning för tredjeparts-/leverantörs-AI.
- [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) och ISO/IEC 42001 (AI-ledningssystem).
- MCP-säkerhet: [SentinelOne](https://www.sentinelone.com/cybersecurity-101/cybersecurity/mcp-security/), [Red Hat](https://www.redhat.com/en/blog/model-context-protocol-mcp-understanding-security-risks-and-controls).
- Branschdata om AI-styrningsgapet (97 % användning, 30 % styrning) och betydelsen av en utsedd ägare: se fullständig källförteckning i underlaget.

Fullständig källgenomgång och resonemang finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Riktlinjer för AI-assisterade verktyg (kategori F), vad ett godkänt verktyg får göra autonomt.
- Sekretess & dataskydd vid AI-användning (kategori F), vilken data som får matas in.
- Prompt- och kontexthantering (kategori F), instruktionsfiler och återanvändbara instruktioner.
- Utvecklingsmiljö & verktyg (kategori A), utvecklarens generella arbetsyta.

(Länkas direkt när respektive dokument är skrivet, se den interna ämnesstrukturen för fullständig lista.)

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
