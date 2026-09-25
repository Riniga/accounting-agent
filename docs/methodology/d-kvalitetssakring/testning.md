# Testning

**Kategori:** D. Kvalitetssäkring
**Status:** fastställd
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-testning.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Tester är det som gör det möjligt att ändra kod med tillförsikt istället för rädsla. Det här dokumentet fastställer teststrategi, hantering av flaky tester, och förhållningssätt till code coverage, inklusive särskilda krav när AI-verktyg skriver produktionskod, där testning fyller en delvis annan funktion än när en människa skriver koden.

## Omfattning och avgränsning

Omfattar den generella, funktionella teststrategin: testtyper, fördelning mellan dem, coverage, och hantering av opålitliga (flaky) tester.

Omfattar **inte**:

- Säkerhetsspecifik testning (SAST/DAST), se Secure coding-principer. Resultat därifrån rapporteras som en egen, namngiven säkerhetskontroll, inte inbakat i det generella testresultatet.
- Vad som gör kod testbar i grunden (små funktioner, låg koppling), se Kodkvalitet & clean code.
- Granskningsprocessen som kontrollerar att tester finns och håller måttet, se Kodgranskning.
- Var och hur tester faktiskt körs i pipelinen, se CI/CD & automatisering.

## Krav (SKA)

1. Teststrategins fördelning mellan enhetstester, integrationstester och end-to-end-tester ska väljas utifrån var projektets faktiska risker och buggar uppstår, inte en fast, universell fördelning som antas passa alla projekt.
2. En code coverage-golvnivå ska finnas och genomdrivas tekniskt som en spärr mot att sjunka ("coverage ratchet"), aldrig som ett stigande målvärde att jaga mot 100 %. Golvet börjar lågt (riktmärke: 50 %) för att inte blockera adoption, och höjs successivt mot 70–80 % i takt med att projektet mognar.
3. Flaky tester ska karantänsättas (flyttas till en icke-blockerande testsvit) istället för att bara köras om eller ignoreras. Varje karantänsatt test ska ha en ägare och en tidsgräns för att fixas eller tas bort.
4. Antal automatiska återförsök vid ett testfel i CI ska begränsas (riktmärke: max två). Fler döljer verkliga regressioner istället för att bara hantera brus.
5. När ett AI-verktyg skriver produktionskod (inte prototyper/experiment) ska utvecklingen vara testdriven: ett människodefinierat eller människogranskat test som uttrycker det önskade beteendet ska finnas **innan** AI-verktyget skriver implementationen, som verktyget sedan itererar mot att få att passera. Testet får inte vara enbart AI-genererat och AI-godkänt utan mänsklig granskning.

## Rekommendationer (BÖR)

1. TDD (test-driven development) är ett giltigt sätt att uppnå kraven ovan för mänskligt skriven kod, men är inte obligatoriskt där. Utfallet (testad, pålitlig kod, avspeglat i coverage) kravställs, inte en specifik arbetsmetod. Prototyper och experiment undantas helt.
2. Kompletterande signaler (t.ex. mutationstestning, defekt-läckagegrad) övervägs av team som redan nått en stabil coverage-golvnivå och vill mäta testkvalitet djupare än ren täckningsyta.

## Vägledning och exempel

**Två skolor, samma princip som i Kodkvalitet & clean code:** den klassiska testpyramiden (många enhetstester) och Kent C. Dodds "Testing Trophy" (ett tjockt lager integrationstester) är båda giltiga. Vilken som passar bäst beror på var i systemet komplexiteten och riskerna faktiskt bor. Backend med tung domänlogik (prissättning, schemaläggning) tenderar att gynnas av pyramidformen; integrationstunga, moderna applikationer gynnas ofta av en tjockare integrationsnivå.

**Varför TDD är obligatoriskt för AI men inte för människor (krav 5):** skälet är specifikt kopplat till hur AI-verktyg arbetar. Boris Cherny, skaparen av Claude Code, har själv lyft fram att ge verktyget ett sätt att verifiera sitt eget arbete som den viktigaste enskilda insikten för effektivt arbete med agentisk kodning. Ett människodefinierat test innan AI:n implementerar ger exakt det: ett konkret, verifierbart facit istället för att en människa i efterhand ska lita på ett påstående om att koden fungerar (se även Riktlinjer för AI-assisterade verktyg, som redan kräver bevis snarare än löften för AI-genererad kod).

**Skanska har redan underlag att bygga vidare på:** det finns sedan tidigare framtagna teststrategier och flera välfungerande exempel på testning i enskilda projekt, hittills utan central prioritet eller spridning. Det här dokumentet ersätter inte det underlaget, utan bör kompletteras med det när metodiken fördjupas.

## Undantag

Ett befintligt projekt som redan ligger under den initiala coverage-golvnivån (krav 2) undantas inte från kravet, men kan hantera det via en dokumenterad, tidsbestämd upptrappningsplan istället för ett omedelbart hårt stopp. Samma princip gäller vid införande av ett formateringsverktyg på en befintlig kodbas (se Kodstandard & stil).

## Källor och ramverk

- Testpyramid vs. Testing Trophy (Kent C. Dodds): två giltiga, kontextberoende teststrategiformer.
- Forskning och branschpraxis om code coverage som fåfänga-metrik vid för höga mål, och coverage-golv/ratchet som bättre mekanism.
- Etablerat mönster för flaky test-karantän, inklusive Microsofts dokumenterade resultat av en "fixa eller ta bort inom två veckor"-policy.
- TDD:s dokumenterade "andra vår" för AI-kodningsagenter 2026, inklusive Boris Chernys (Claude Code) egna insikter.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Secure coding-principer (kategori C), säkerhetsspecifik testning, rapporterad separat.
- Kodkvalitet & clean code (kategori B), grunden för testbar kod.
- Riktlinjer för AI-assisterade verktyg (kategori F), kravet på bevis snarare än löften som krav 5 bygger vidare på.
- Kodgranskning (kategori D), granskningen som kontrollerar att kraven ovan följs.
- CI/CD & automatisering (kategori E), var och hur testerna faktiskt körs.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
