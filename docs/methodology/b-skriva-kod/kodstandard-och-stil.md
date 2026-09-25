# Kodstandard & stil

**Kategori:** B. Skriva kod
**Status:** fastställd
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-kodstandard-och-stil.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Kodstil är den vanligaste, mest tidsödande och minst värdefulla diskussionen i kodgranskning när den sköts manuellt. Det här dokumentet fastställer att formatering och stil ska vara mekaniska och tekniskt genomdrivna, aldrig en smaksak som avgörs på nytt i varje pull request, oavsett vilket språk eller vilken plattform ett projekt använder.

## Omfattning och avgränsning

Omfattar mekaniskt verktygsstyrd formatering (indentering, radbrytningar, layout) och per-språkskonventioner (linters) som ett verktyg kan avgöra automatiskt, utan mänsklig tolkning.

Omfattar **inte**:

- Designnivå-kvaliteter som kräver mänskligt omdöme (namngivning, funktionsstorlek, SOLID), se Kodkvalitet & clean code.
- Säkerhetsspecifika statiska analysregler, se Secure coding-principer, även om verktygskedjan ofta är densamma.
- Den faktiska pipeline-mekaniken (hur pre-commit/CI faktiskt konfigureras och körs), se CI/CD & automatisering. Det här dokumentet slår fast *att* enforcement sker i CI, inte *hur*.
- Vad en granskare i övrigt tittar på, se Kodgranskning. Målet här är att granskaren aldrig ska behöva säga något om formatering.

## Krav (SKA)

1. Varje repo ska ha en `.editorconfig`-fil som sätter grundläggande formateringsregler (indentering, radslut, teckenkodning), oavsett vilket eller vilka språk projektet använder.
2. Varje språk/plattform i ett projekt ska ha en utsedd, automatisk formatterare vars utdata är bindande, inte en riktlinje att tolka manuellt.
3. Projekt ska i första hand använda vedertagna, etablerade verktyg och deras standardkonfiguration, inte egna, projektspecifika formaterings-/lintingregler byggda från grunden. En icke-bindande referenslista per språk finns i Vägledning nedan för team som inte redan har ett etablerat val.
4. Formatering och stil ska genomdrivas tekniskt i flera lager: ett snabbt pre-commit-steg lokalt, och en spärr i CI som blockerar sammanslagning vid avvikelse.
5. Kodgranskning ska inte behöva kommentera ren formatering som redan täcks av ett automatiskt verktyg. Om det händer upprepat är det ett tecken på att verktygskedjan är ofullständig, inte något en granskare ska kompensera för manuellt.

## Rekommendationer (BÖR)

1. Formatterarens standardinställningar bör accepteras med minimal anpassning. Egen konfiguration flyttar bara stildiskussionen från kodgranskning till verktygskonfiguration, vilket motverkar hela syftet.
2. Formatterare (layout) och linter (korrekthet/kodlukt) bör hållas begreppsmässigt åtskilda, även när ett och samma verktyg utför båda uppgifterna, så ansvarsfördelningen förblir tydlig oavsett verktygsval.
3. Pre-commit-steg bör hållas snabba (riktmärke: under ca 10 sekunder). Annars kringgås de i praktiken, vilket gör hela lagret verkningslöst.

## Vägledning och exempel

**Icke-bindande referenslista per språk** (startpunkt för team utan ett etablerat val, inte ett krav på specifik produkt):

| Språk | Formatterare (exempel) | Linter (exempel) |
|---|---|---|
| JavaScript/TypeScript | Prettier, eller Biome (kombinerat format+lint) | ESLint, eller Biome |
| Python | Ruff (kombinerat format+lint) | Ruff |
| C#/.NET | `dotnet format` (ingår i .NET SDK, styrs av `.editorconfig`) | Roslyn-analysatorer |
| Java | Google Java Format, eller Spotless | Checkstyle, PMD, SpotBugs |
| Go | `gofmt`/`goimports` (ingår i språkverktygskedjan) | `golangci-lint` |

Ett projekt som redan har ett annat, lika etablerat verktyg ska inte tvingas byta bara för att det inte står i tabellen.

Målet med kravet på mekanisk formatering (krav 2–3) är inte att avskaffa all diskussion om stil för alltid, utan att flytta den från "varje pull request, varje gång" till "en gång, när verktyget och dess konfiguration väljs för projektet". Även etablerade opinionerade verktyg fortsätter att debattera sina egna standardval internt; det är förväntat och inget tecken på att metoden inte fungerar.

## Undantag

Att införa ett formateringsverktyg på en befintlig, tidigare oformaterad kodbas kan skapa en mycket stor engångsdiff. I det läget är det tillåtet att:

- göra en enskild, isolerad "endast omformatering"-commit som inte blandas med funktionella ändringar, och
- fasa in verktyget gradvis per katalog/modul om en engångsomformatering av hela kodbasen är opraktisk,

under förutsättning att det är tydligt dokumenterat vilka delar som redan är formatterade och vilka som inte är det än.

## Källor och ramverk

- EditorConfig-specifikationen: språkoberoende grundformatering.
- Prettiers "opinionated formatter"-filosofi: mekanisk, icke förhandlingsbar formatering som eliminerar stildiskussioner i granskning.
- Etablerad praxis för lagerindelad enforcement: pre-commit lokalt, CI som den spärr som aldrig kan hoppas över.
- Branschöversikt av 2026 års verktygslandskap (Biome, Ruff m.fl.) som underlag för referenslistan ovan.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Kodkvalitet & clean code (kategori B), designnivå-kvaliteter som inte kan mekaniseras på samma sätt.
- Secure coding-principer (kategori C), säkerhetsspecifika statiska analysregler.
- Kodgranskning (kategori D), granskningen som kraven ovan ska frigöra från formateringsdiskussioner.
- CI/CD & automatisering (kategori E), pipeline-mekaniken som faktiskt kör pre-commit-/CI-spärrarna i krav 4.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Utvecklingsmetodiken, version 1.0
