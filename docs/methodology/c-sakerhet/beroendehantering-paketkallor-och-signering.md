# Beroendehantering, paketkällor & signering

**Kategori:** C. Säkerhet
**Status:** fastställd
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-beroendehantering-paketkallor-och-signering.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Sårbarheter i tredjepartsberoenden är en lika stor risk som sårbarheter i egen kod. OWASP lyfte 2025 in en helt ny toppkategori för brister i mjukvaruleverantörskedjan. Det här dokumentet fastställer hur organisationen väljer, spårar, skannar och uppdaterar tredjepartsberoenden, så att kända sårbarheter, licensproblem och obemärkta versionsförändringar upptäcks innan de blir ett produktionsproblem.

## Omfattning och avgränsning

Omfattar tredjepartsberoenden: SBOM, versionslåsning, licensefterlevnad, SCA-skanning, uppdateringsrutin och paket-/artefaktsignering.

Omfattar **inte**:

- Verktyg utvecklaren själv använder (IDE, CLI), se Utvecklingsmiljö & verktyg.
- Sårbarheter i egen kod, se Secure coding-principer.
- Vad som händer efter att en sårbarhet (i egen kod eller ett beroende) hittats (triage, prioritering, åtgärd), se Sårbarhetshantering, patchning & CVD. Det här dokumentet handlar om att förebygga och upptäcka, inte åtgärda.

## Krav (SKA)

1. Ett SBOM (Software Bill of Materials) ska genereras automatiskt som en del av bygg-/leveransprocessen. SPDX är förstahandsval; CycloneDX accepteras när det ger bättre stöd i projektets verktygskedja eller ekosystem.
2. SCA-skanning (Software Composition Analysis) ska köras automatiskt i pipelinen för att upptäcka kända sårbarheter i tredjepartsberoenden. Reachability-analys (eller motsvarande brusreducerande funktion) är ett kriterium vid verktygsval, inte en efterhandstanke.
3. Beroenden ska låsas till specifika, verifierbara versioner via en lockfile eller motsvarande mekanism, inte lösa versionsintervall som kan förändras oförutsägbart vid en ny installation.
4. Automatiserad licensskanning ska ingå i samma verktygskedja som SCA, med en känd, dokumenterad process (kopplad till juridik/inköp) för att hantera licenser utanför en godkänd lista.
5. Uppdatering av beroenden ska ske via en automatiserad, återkommande rutin (t.ex. automatiska uppdaterings-pull requests), inte enbart manuell, sporadisk uppdatering.

## Rekommendationer (BÖR)

1. Paket med kryptografisk proveniens/signering (t.ex. Sigstore-baserad) bör föredras och verifieras framför paket utan, där ekosystemet stödjer det. Krävs inte universellt ännu, givet den fortsatt låga faktiska ekosystemtäckningen (2026).
2. Godkända paketkällor (en intern spegling/proxy av publika register) bör användas där sådan infrastruktur finns. Lägre prioriterat än kraven ovan. SBOM, SCA-skanning och versionslåsning täcker redan det mesta av den praktiska riskreduceringen; en källspegling är ett ytterligare, men mindre kritiskt, försvarslager.

## Vägledning och exempel

**Konkret startexempel:** Dependabot (inbyggt i GitHub, gratis) är ett rimligt förstahandsexempel för automatiserad uppdatering (krav 5) och grundläggande SCA (krav 2). Det är inte det enda alternativet. För mer avancerad reachability-analys (krav 2) finns både kommersiella verktyg och gratis/öppna alternativ som OWASP Dependency-Check.

**EU Cyber Resilience Act** bedöms inte vara direkt utlöst för en organisation som inte säljer eller levererar programvara som en egen produkt till extern marknad. SBOM-kravet ovan (krav 1) motiveras därför av god praxis och linjen från NIS2/CISA, inte av en tvingande CRA-skyldighet. Den bedömningen bör omprövas om organisationen någon gång börjar leverera programvara externt som produkt.

Kraven ovan är den direkta uppföljningen av OWASP Top 10:2025:s nya kategori för brister i mjukvaruleverantörskedjan (se Secure coding-principer).

## Undantag

För äldre system eller plattformar som saknar tekniskt stöd för lockfiles eller automatiserad SBOM-generering kan en manuell, dokumenterad process användas tillfälligt (t.ex. en manuellt underhållen beroendelista), under förutsättning att en plan finns för att antingen få verktygsstöd på plats eller fasa ut systemet.

## Källor och ramverk

- CISA:s 2026 minimikrav för SBOM, samt SPDX och CycloneDX som godkända format.
- Software Composition Analysis (SCA) och reachability-analys som brusreducerande teknik.
- Sigstore och paketregisters (npm, PyPI) provenienssignering: moget som teknik, men tidigt i faktisk ekosystemtäckning.
- OWASP Top 10:2025: den nya kategorin för brister i mjukvaruleverantörskedjan.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Utvecklingsmiljö & verktyg (kategori A), verktyg utvecklaren använder, till skillnad från beroenden koden har.
- Secure coding-principer (kategori C), sårbarheter i egen kod, samt ursprunget till OWASP-kopplingen ovan.
- Sårbarhetshantering, patchning & CVD (kategori C), vad som händer när SCA-skanningen faktiskt hittar något.
- Hantering av hemligheter (kategori C).

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Utvecklingsmetodiken, version 1.0
