# Prompt- och kontexthantering

**Kategori:** F. AI-samarbete i utvecklingsarbetet
**Status:** fastställd
**Senast uppdaterad:** 2026-09-05
**Underlag:** 2026-09-05-prompt-och-kontexthantering.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

AI-assisterade verktyg konfigureras och instrueras via instruktions-/kontextfiler (t.ex. CLAUDE.md-motsvarigheter). Utan gemensamma spelregler för hur sådana filer skrivs, delas och skyddas uppstår antingen ett fragmenterat lapptäcke av verktygsspecifika filer, eller en ny, obevakad säkerhetsrisk: en instruktionsfil är konfiguration som direkt styr ett AI-verktygs beteende, inte oskyldig dokumentation. Det här dokumentet fastställer hur Skanska arbetar med instruktionsfiler och återanvändbara instruktioner, oavsett vilket specifikt AI-verktyg som används.

## Omfattning och avgränsning

Omfattar format, innehåll, granskning och säkerhet för instruktions-/kontextfiler som styr AI-assisterade verktyg.

Omfattar **inte**:

- Vilka verktyg som är godkända, se Verktyg för AI-assisterad utveckling.
- De faktiska autonomi-/handlingsreglerna för AI (vad AI får göra), se Riktlinjer för AI-assisterade verktyg. Det här dokumentet handlar om hur sådana regler *förmedlas* till verktyget, inte om att formulera dem på nytt.
- Vilken data som får vara AI-indata i stort, se Sekretess & dataskydd vid AI-användning. Det här dokumentet tillämpar de reglerna specifikt på instruktionsfilers eget innehåll.
- Den generella kodgranskningsprocessen, se Kodgranskning. Instruktionsfiler går genom den processen, inte en egen.

## Krav (SKA)

1. AGENTS.md ska användas som det gemensamma, verktygsoberoende formatet för instruktionsfiler. Verktygsspecifika filer (t.ex. CLAUDE.md) hålls som tunna referenser till AGENTS.md där ett verktyg inte läser formatet nativt, inte som separat innehåll som måste hållas synkat för hand.
2. Instruktionsfiler ska granskas och versionshanteras genom samma kodgranskningsprocess som övrig kod. De är konfiguration med direkt inflytande på ett AI-verktygs beteende, inte dokumentation som kan läggas till fritt.
3. Ett AI-verktyg ska aldrig automatiskt agera på instruktioner som hittas i innehåll som inte gått igenom granskning (README, kommentarer, ärendebeskrivningar, en oreviderad instruktionsfil) utan mänskligt godkännande.
4. Instruktionsfiler ska hållas korta och fokuserade (riktmärke: runt 200 rader per fil) och innehålla det som faktiskt återkommer i praktiken, inte teoretisk best practice som inte matchar hur teamet arbetar.
5. Instruktionsfiler ska underhållas som levande dokument: uppdateras efter ett upprepat agent-misstag, en arkitektur-/verktygsförändring, eller ett granskningsfynd, inte sättas en gång och sedan glömmas.
6. Instruktionsfiler får aldrig innehålla data som klassas som konfidentiell (se Sekretess & dataskydd vid AI-användning), eftersom de normalt inkluderas automatiskt i varje AI-interaktion och sprids lätt vidare.
7. Gemensamma, organisationsövergripande principer ska refereras från projektets egen instruktionsfil (länk), inte kopieras in.
8. Instruktionsfiler ska skannas automatiserat för misstänkta eller dolda instruktionsmönster, och ändringar i dem ska flaggas tydligt i granskningsvyn, som komplement till, inte ersättning för, kraven 2–3.

## Rekommendationer (BÖR)

1. Ett gemensamt startmall-repo eller en mall-AGENTS.md bör tillhandahållas centralt, så att nya projekt inte behöver uppfinna strukturen för instruktionsfiler och referenser till gemensamma principer själva.

## Vägledning och exempel

**Var principerna konkret ska bo (krav 7)** är ett projektval, inte något metodiken pekar ut. Ett giltigt, beprövat exempel: en dedikerad katalog för principer, t.ex. `docs/architecture/principle_xx.md`, dit AGENTS.md hänvisar istället för att innehålla reglerna själv. Det här projektets eget arbetssätt är ett annat exempel på samma mönster: `CLAUDE.md` i det här repot pekar mot `PROJECT.md` och `docs/STATUS.md` istället för att duplicera deras innehåll, och Skanskas samlade `docs/output/` (den här metodiken) är i sig en organisationsnivå-instans av samma princip.

AGENTS.md-kravet (krav 1) är inte hypotetiskt hos Skanska: GitHub Copilots coding agent, redan det godkända verktyget (se Verktyg för AI-assisterad utveckling), finns på AGENTS.md:s officiella kompatibilitetslista.

## Undantag

Om ett godkänt verktyg tillfälligt saknar stöd för AGENTS.md kan dess eget, verktygsspecifika format användas som en dokumenterad övergångslösning, under förutsättning att det finns en plan för att migrera till en AGENTS.md-refererande struktur så snart stöd finns. Ett sådant undantag upphäver aldrig kraven på granskning (krav 2–3, 8) eller på att aldrig inkludera konfidentiell data (krav 6).

## Källor och ramverk

- AGENTS.md: öppen, verktygsoberoende specifikation stewardad av Agentic AI Foundation (Linux Foundation), med brett verktygsstöd inklusive GitHub Copilots coding agent.
- Etablerad praxis för utformning av AI-instruktionsfiler (filstorlek, innehåll, underhåll som levande dokument).
- Dokumenterad forskning om instruktionsfiler och liknande repository-innehåll (README, kommentarer, ärenden) som attackyta för prompt injection, med rapporterade framgångsfrekvenser på 41–84 % beroende på attacktyp.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Verktyg för AI-assisterad utveckling (kategori A), vilka verktyg som är godkända, inklusive att GitHub Copilot redan stödjer AGENTS.md.
- Riktlinjer för AI-assisterade verktyg (kategori F), de autonomi-/handlingsregler som instruktionsfiler förmedlar, samt principen att guardrails ska vara tekniska (krav 3, 8 bygger vidare på den).
- Sekretess & dataskydd vid AI-användning (kategori F), klassificeringsreglerna bakom krav 6.
- Kodgranskning (kategori D), den generella granskningsprocess instruktionsfiler går genom (krav 2).

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
