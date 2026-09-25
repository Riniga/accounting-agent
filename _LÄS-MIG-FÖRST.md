# Grundplåt — starta ett nytt projekt på det här sättet

Det här är ett genericerat skelett som går att kopiera in i ett helt nytt projekt och få samma en grundläggande utvecklingsprocess, kvalitetsgrindar och AI-samarbetsstruktur.

**Radera den här filen** när du har läst den — den hör inte hemma i det nya projektet.

## Så här använder du det

1. Kopiera hela `grundplat/`-trädet till roten av ditt nya repo (inklusive
   dotfiles — `.claude/`, `.github/`, `.gitignore`, `.editorconfig`, `.gitattributes`,
   `.pre-commit-config.yaml`, `.secrets.baseline`, `.env.example`).
2. Lägg projektidén i `docs/initial-idea.md`. Den får vara ofullständig, men rensa bort
   allt konfidentiellt innan den används som underlag för ett AI-verktyg.
3. Kör prompten i [`docs/claude-prompts/initialize-project.md`](docs/claude-prompts/initialize-project.md)
   i Claude Code. Claude läser den här filen och idén, ställer frågor om det som saknas,
   lägger fram ett förslag och skriver sedan, efter ditt godkännande, vision, roadmap,
   ADR:er, MVP-001 och planen för den. Platshållarna i vinkelparenteser (`<app-1>`,
   `<owner>/<repo>` osv.) ersätts i samma steg, och Claude föreslår vilka exempel- och
   stackspecifika filer som ska bort.
4. Genomför MVP-001 enligt planen. Den första MVP:n är normalt ett "walking skeleton":
   stacken, en minimal körbar del och CI med kvalitetsgrindarna på plats innan AI-verktyg
   börjar skriva produktionskod.
5. Om stacken är Python: kör `pip install pip-tools && pip-compile --generate-hashes
   --no-annotate --no-header requirements.in` **innan** `conda env create`.
   `requirements-lock.txt` finns medvetet inte i det här trädet (en fryst lock-fil hade
   blivit inaktuell direkt, se kommentaren i `requirements.in`). Kör igenom
   `docs/development/setup.md` och `environment.md` för resten av miljöuppsättningen,
   och kör om kommandot varje gång du redigerar `requirements.in`. Med en annan stack
   ersätts de Python-specifika filerna inom MVP-001.

## Vad som är med, och varför

**Kopierat rakt av (organisationsövergripande, inte projektspecifikt):**
`docs/methodology/` (hela Skanskas utvecklingsmetodik — 21 kapitel), `docs/claude-prompts/`
(redan helt generiska bootstrap-prompts), `.claude/settings.json`, `scripts/scan_instruction_files.py`,
`.editorconfig`, `.gitattributes`.

**Generiserat** (samma mönster och resonemang, men platshållare istället för riktiga
namn/värden): `AGENTS.md`, `CLAUDE.md`, `README.md`, `SECURITY.md`, alla
`docs/standards/*.md`, alla `docs/development/*.md`, `.github/workflows/ci.yml`,
`.github/workflows/dast.yml` (manuell OWASP ZAP-skiss — den var aldrig Azure-specifik, bara
felaktigt bortsorterad i ett första pass), `.github/pull_request_template.md`,
`pyproject.toml`, `pytest.ini`, `environment.yml`, `requirements.in` (en riktig, testad
minimal lista — men `requirements-lock.txt` genereras medvetet inte i förväg, se steg 5).

**Nya mallar** (fanns inte som separata filer i originalet, skapade för att göra
återanvändningen konkret): `docs/architecture/decisions/ADR-TEMPLATE.md`,
`docs/mvp/TEMPLATE.md`, `docs/plans/TEMPLATE.md`, plus ett genomarbetat exempelpar
(`EXAMPLE-mvp.md` / `EXAMPLE-plan.md`) som visar mönstret "mät en verklig baslinje innan du
låser ett tal i planen" — den enskilt viktigaste lärdomen från det här projektets P4–P7.

**Nollställt till en fungerande, tom startpunkt** (samma mekanism, men utan det här
projektets faktiska fynd): `.secrets.baseline` (färsk, tom baslinje),
`docs/methodology-compliance/gap-register.md` / `interpretations.md` / `exceptions.md`
(struktur + legend, inga rader).

## Vad som medvetet INTE är med

- **`apps/`, `packages/`** — riktig applikationskod, specifik för det här projektet.
- **Riktiga ADR:ar, MVP:er, planer, roadmap-innehåll** — det här projektets faktiska
  historik och beslut. Mallarna ovan ersätter dem.
- **`deploy/`, `migration/`, `tests/deploy/`, de Azure-specifika workflow-filerna
  (`deploy.yml`, `data-pipeline.yml`)** — hårt knutna till just den här plattformens Azure
  App Service-topologi (fyra specifika appar, specifika PowerShell-skript). Värdefullt att
  titta på som exempel i originalrepot, men inte generiskt nog att kopiera rakt av till ett
  projekt med annan infrastruktur. (`dast.yml` hör **inte** till den här kategorin — den är
  redan med, se ovan.)
- **`docs/brand/`** — Skanskas visuella identitet (loggor, färger), inte en del av
  utvecklingsprocessen.
- **`docs/notes/`** — arbetsanteckningar specifika för det här projektets MVP:er.
- **`docs/development/local-platform.md`** — beskriver en fyra-appars lokal
  startorkestrering specifik för det här projektet.
- **`docs/methodology-compliance/{a-f}-*.md`** (de faktiska bedömningarna) — det här
  projektets egna ifyllda metodik-bedömning. Ett nytt projekt gör om den övningen från
  `_template.md`.

Om du vill ha med deploy-mönstret ändå: titta på `deploy/deploy-platform.ps1` och
`.github/workflows/deploy.yml` i huvudrepot som ett arbetat exempel, och bygg din egen
version anpassad efter din infrastruktur — kopiera inte rakt av.
