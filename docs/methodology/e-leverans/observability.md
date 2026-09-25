# Observability: loggning, metrics, tracing, health checks & felhantering

**Kategori:** E. Leverans
**Status:** fastställd
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-observability.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Loggar är bara en del av att göra kod driftbar och diagnosticerbar. Metrics, spårning (tracing) och hälsokontroller ingår också. Det här dokumentet fastställer vad koden ska exponera, förankrat i OpenTelemetry som vedertagen, verktygsoberoende standard. Det är också den mätgrund flera andra kapitel i den här metodiken förutsätter finns. Krav på att något "ska mätas löpande" (t.ex. Sårbarhetshantering, patchning & CVD) fungerar bara om tjänsten faktiskt exponerar mått att mäta.

## Omfattning och avgränsning

Omfattar vad koden ska exponera: loggning, metrics, tracing och hälsokontroller.

Omfattar **inte**:

- Driftens övervakning av servrar och infrastruktur: en separat funktion Skanska redan har, skild från kodnivå-observability.
- Var observability-data lagras/visualiseras, eller hur en driftplattform i övrigt övervakar en miljö. Se CI/CD & automatisering och Miljöhantering & konfiguration.
- Klassificeringsregler för känslig data i allmänhet, se Sekretess & dataskydd vid AI-användning och Hantering av hemligheter. Det här dokumentet tillämpar samma grundregler specifikt på loggutdata.

## Krav (SKA)

1. Instrumentering för loggning, metrics och tracing ska ske mot OpenTelemetry (eller ett kompatibelt, öppet API), inte direkt mot en leverantörsspecifik SDK, för att undvika inlåsning.
2. Loggar ska skrivas strukturerat (JSON), med spårnings-id (trace/span-id) automatiskt inkluderat av loggningsramverket i varje rad, inte manuellt tillagt vid varje enskilt loggningsanrop.
3. Personuppgifter, autentiseringsuppgifter och hemligheter ska aldrig hamna i loggar. Automatiserad filtrering/maskning används som skydd, inte enbart förlitan på att utvecklare kommer ihåg att utelämna dem.
4. Varje tjänst ska exponera minst en hälsokontrollendpoint som skiljer mellan "lever processen" (liveness) och "redo att ta emot trafik" (readiness).
5. Varje tjänst ska exponera RED-mått (Rate, Errors, Duration) per endpoint som minimum: antal anrop, andel misslyckade anrop, och svarstidsfördelning.

## Rekommendationer (BÖR)

1. En korrelations-id med affärsbetydelse (t.ex. ordernummer) används som komplement till spårnings-id där automatisk propagering inte når fram (meddelandeköer, batch-jobb, webhooks).
2. Hälsokontrollendpoints exponerar inte detaljerad systeminformation offentligt, och skyddas separat från applikationens övriga funktionella endpoints.
3. Mättnad (saturation, t.ex. resursutnyttjande) läggs till som ett fjärde mått för tjänster där kapacitet är en känd risk.

## Vägledning och exempel

**Varför OpenTelemetry:** i maj 2026 graduerade CNCF OpenTelemetry till "Graduated"-status, på samma nivå som Kubernetes och Prometheus. Över 90 observability-leverantörer stödjer det. Det är inte längre ett val bland flera likvärdiga, utan den vedertagna standarden.

**Verktygsexempel (icke-bindande):** öppen källkod: Grafana med Loki (loggar), Tempo (tracing) och Mimir eller Prometheus (metrics); Jaeger (tracing). Kommersiella alternativ som Datadog eller Honeycomb tar också emot OpenTelemetry-data rakt av. Valet av bakomliggande plattform spelar mindre roll så länge instrumenteringen sker mot OpenTelemetry.

**RED i praktiken:** för varje endpoint eller meddelandekonsument mäts *Rate* (anrop per sekund), *Errors* (andel misslyckade anrop) och *Duration* (svarstidsfördelning, inte bara ett genomsnitt). Måtten är tjänsteagnostiska: samma tre gäller för ett HTTP-API, en gRPC-tjänst eller en meddelandekökonsument, och OpenTelemetrys automatiska instrumentering ger dem i praktiken utan extra arbete.

**Felhantering hålls medvetet lätt här:** ett fel loggas med samma struktur och kontext (inklusive spårnings-id) som allt annat. Det räcker som krav i det här dokumentet, snarare än en egen, separat kravkategori.

## Undantag

För ett äldre system som inte tekniskt kan instrumenteras mot OpenTelemetry kan en befintlig, plattformsspecifik loggnings-/metriklösning fortsätta användas tillfälligt, under förutsättning att kraven på struktur, spårnings-id och filtrering av känslig data (krav 2–3) ändå upprätthålls, och att en plan finns för att migrera.

## Källor och ramverk

- OpenTelemetry: CNCF Graduated-status (maj 2026), vendor-neutral instrumenteringsstandard.
- Praxis för strukturerad loggning, spårnings-id och korrelations-id.
- Health Endpoint Monitoring-mönstret (liveness/readiness).
- RED-metoden och Googles fyra gyllene signaler som minimimått för tjänster.
- Praxis för att skydda känslig data i loggar genom automatiserad filtrering.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Sekretess & dataskydd vid AI-användning, Hantering av hemligheter (kategori C/F), grundreglerna för känslig data som krav 3 tillämpar på loggar.
- Sårbarhetshantering, patchning & CVD (kategori C), kravet på löpande mätning av SLA-efterlevnad, som förutsätter mätgrunden i det här dokumentet.
- CI/CD & automatisering, Miljöhantering & konfiguration (kategori E), var observability-data faktiskt hanteras i drift.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
