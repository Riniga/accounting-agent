# Versionshantering & branchstrategi

**Kategori:** E. Leverans
**Status:** fastställd
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-versionshantering-och-branchstrategi.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Idag har varje Skanska-projekt sin egen branchstrategi, ibland ingen alls. Det här dokumentet sätter ett gemensamt, konkret golv: hur grenar hanteras, hur commit-meddelanden skrivs, hur versioner numreras, och hur en ändring spåras tillbaka till varför den gjordes. Grundat i forskning om vad som faktiskt korrelerar med leveransprestanda, inte tradition.

## Omfattning och avgränsning

Omfattar grenstruktur, commit-konventioner, versionsnumrering, och koppling mellan en ändring och det arbete den utför.

Omfattar **inte**:

- Pull request-godkännande och granskningsfokus, se Kodgranskning.
- Pipelinemekaniken (hur CI faktiskt körs, hur feature flags implementeras tekniskt), se CI/CD & automatisering.
- AI-specifik märkning av bidrag: sker på PR-nivå enligt Riktlinjer för AI-assisterade verktyg, inte i commit-meddelandet.

## Krav (SKA)

1. Grenar (feature branches) ska hållas kortlivade (riktmärke timmar till några dagar, inte veckor) och slås samman ofta.
2. En process får bara kallas trunk-based development om pålitlig CI, feature flags och en sammanslagningskö (eller motsvarande mekanism som håller huvudgrenen grön) faktiskt finns på plats.
3. Varje commit-meddelande ska tydligt beskriva vad som ändrats och varför, aldrig innehållslösa meddelanden som "fix" eller "wip". Commits görs ofta och kontinuerligt.
4. Versionsnumrering ska följa Semantic Versioning (MAJOR.MINOR.PATCH).
5. Commit-konventionerna ska inte innehålla AI-specifik märkning (t.ex. en Co-authored-by-rad för AI).
6. En pull request ska vara kopplad till ett arbetsobjekt/feature (t.ex. ett work item), inte enskilda commits. Genomdrivs tekniskt där plattformen stödjer det.

## Rekommendationer (BÖR)

1. Commit-meddelanden bör följa Conventional Commits-formatet (`typ(scope): beskrivning`) som en frivillig uppgradering utöver kravet på tydlighet, särskilt värdefullt för projekt som vill automatisera versionsnumrering och ändringslogg.
2. GitFlow (eller en långlivad release-/hotfix-grenmodell) reserveras för det smala fallet där flera parallella, publicerade versioner måste underhållas samtidigt, inte som standardval för interna projekt med kontinuerlig leverans.
3. Release-processen automatiseras med verktygsstöd (t.ex. i stil med semantic-release eller release-please) där externa konsumenter finns.

## Vägledning och exempel

**En konkret grenmodell**, som ett tydligt exempel att utgå från:

- `main` är alltid driftsättningsbar.
- En ny gren skapas från `main` med ett namn som innehåller arbetsobjektets id, t.ex. `feature/1234-kort-beskrivning` eller `bugfix/1234-kort-beskrivning`.
- Pull request öppnas så tidigt som möjligt (gärna som utkast) för synlighet, inte först när allt är klart.
- Grenen slås samman inom timmar till några dagar. Om den lever längre är det en signal om att arbetet borde delats upp mindre.
- Grenen tas bort efter sammanslagning.

**Exempel på commit-meddelanden** (krav 3):

- Otillräckligt: `fix`, `wip`, `ändringar`.
- Tillräckligt tydligt: `Rätta null-referens vid tom varukorg` eller, med Conventional Commits (BÖR 1): `fix(checkout): hantera tom varukorg utan att krascha`.

**Koppling till arbetsobjekt (krav 6):** Azure DevOps har en inbyggd branchpolicy, "Check for linked work items", som gör precis det här utan att något nytt verktyg behöver införskaffas. Idag är den bara aktiverad hos ett fåtal Skanska-projekt. Motsvarande finns i GitHub via länkade issues i PR-beskrivningen.

## Undantag

Ett projekt som redan använder GitFlow eller en långlivad grenmodell behöver inte migrera omedelbart, men bör ha en dokumenterad plan för övergång till kortlivade grenar, särskilt om projektet gör kontinuerlig leverans, där GitFlow är en mismatch snarare än ett medvetet val.

## Källor och ramverk

- DORA/Accelerate-forskning om branchlivslängd och leveransprestanda (lead time, driftsättningsfrekvens, andel misslyckade ändringar).
- Trunk-based developments tre förutsättningar: CI, feature flags, sammanslagningskö.
- Conventional Commits och Semantic Versioning som standardkombination för automatiserad versionshantering.
- Azure DevOps branchpolicyer för länkade arbetsobjekt.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Kodgranskning (kategori D), PR-godkännande och granskningsfokus.
- CI/CD & automatisering (kategori E), pipelinemekaniken och feature flags som princip 2 förutsätter.
- Riktlinjer för AI-assisterade verktyg (kategori F), var AI-märkning faktiskt sker (PR-nivå).
- Beroendehantering, paketkällor & signering (kategori C), automatiserad release-process kopplad till SBOM-generering.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
