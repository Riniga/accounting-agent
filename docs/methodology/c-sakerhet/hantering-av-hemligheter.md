# Hantering av hemligheter

**Kategori:** C. Säkerhet
**Status:** fastställd
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-hantering-av-hemligheter.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Hemligheter (nycklar, lösenord, tokens, credentials) som hamnar i kod eller kodhistorik är en av de vanligaste och mest lättåtgärdade säkerhetsriskerna, men ändå ett återkommande problem. Det här dokumentet fastställer hur Skanska hanterar hemligheter istället, och rundar av kategori Säkerhet tillsammans med de tre redan skrivna spåren.

## Omfattning och avgränsning

Omfattar hemlighetshantering: var hemligheter lagras, hur åtkomst begränsas, och vad som händer när en hemlighet exponeras.

Omfattar **inte**:

- Sårbarheter i egen kod eller beroenden i övrigt, se Secure coding-principer respektive Beroendehantering, paketkällor & signering.
- Hela incident-/CVD-processen för en läckt hemlighet utöver den akuta första responsen (rotera omedelbart), se Sårbarhetshantering, patchning & CVD.
- Den AI-kontext-specifika hemlighetsskanningen (miljövariabler/konfiguration synliga för en AI-agent), se Sekretess & dataskydd vid AI-användning, som bygger vidare på grunden här.

## Krav (SKA)

1. Hemligheter ska aldrig lagras i kod, konfigurationsfiler som checkas in, eller commit-historik. De hanteras via en dedikerad hemlighetshanterare.
2. Där plattformen stödjer det (t.ex. moln-till-moln-autentisering i CI/CD) ska behovet av en lagrad hemlighet elimineras helt genom identitetsfederation (managed identities, OIDC/workload identity), inte bara lagras säkrare.
3. Åtkomst till hemligheter ska följa minsta möjliga behörighet: en applikationsidentitet får aldrig en administratörsroll, bara den specifika roll den faktiskt behöver.
4. En hemlighet som exponerats (committad, läckt, synlig i loggar) ska betraktas som komprometterad omedelbart och roteras utan dröjsmål, oavsett om repot är privat eller exponeringen var kortvarig.
5. Historikrensning genomförs som ett nödvändigt men i sig otillräckligt andra steg **efter** rotation, aldrig som första eller enda åtgärd.

## Rekommendationer (BÖR)

1. Rotation automatiseras där verktygsstödet finns; manuell rotation med utgångsvarning används som fallback.
2. Separata hemlighetsvalv används per miljö (dev/test/uat/prod) för att förhindra att en läcka i en lägre miljö exponerar produktionshemligheter.

## Vägledning och exempel

En central hemlighetshanterare (t.ex. Azure Key Vault) finns inte hos Skanska idag, men bedöms som lågtröskel att införa givet att Azure redan är den etablerade molnplattformen. Detsamma gäller OIDC/workload identity federation för CI/CD: inte i bruk idag, men en riktning värd att prioritera snarare än en avlägsen ambition.

**Viktigt att inte förväxla:** Microsoft Defender finns redan i drift och skannar, men bara infrastruktur och moln, inte kod. Kodnivå-hemlighetsskanning (att upptäcka en hårdkodad nyckel i en commit) är därför ett fortsatt obesatt behov, inte något befintlig verktygskedja redan löser. Se Sekretess & dataskydd vid AI-användning för det AI-kontext-specifika skanningskravet som bygger på samma grund.

**Ägarskap:** provisionering och drift av hemlighetsvalv är en driftfråga utanför den här metodikens avgränsning (samma mönster som grundavbildningen i Utvecklingsmiljö & verktyg), men kraven ovan (särskilt 1 och 3) är vad metodiken kravställer mot den driftfunktionen.

## Undantag

För ett äldre system som tekniskt inte kan integreras mot en central hemlighetshanterare kan en tillfällig, dokumenterad kompenserande kontroll användas (t.ex. striktare filbehörigheter och manuell rotationsrutin), under förutsättning att en plan finns för att antingen migrera systemet eller fasa ut det.

## Källor och ramverk

- Etablerad praxis för hemlighetshantering: minsta privilegium, rollbaserad åtkomst, miljöseparerade valv.
- OIDC/workload identity federation som modernt alternativ till statiska CI/CD-hemligheter: kortlivade, körningsspecifika tokens med full granskningslogg.
- Vedertagen respons vid en exponerad hemlighet: rotation omedelbart, historikrensning som nödvändigt men otillräckligt andra steg.

Fullständig källgenomgång finns i det interna forskningsunderlaget (se Underlag ovan).

## Relaterat

- Secure coding-principer (kategori C).
- Beroendehantering, paketkällor & signering (kategori C).
- Sårbarhetshantering, patchning & CVD (kategori C), den bredare processen en läckt hemlighet triggar.
- Sekretess & dataskydd vid AI-användning (kategori F), det AI-kontext-specifika hemlighetsskanningskravet som bygger på grunden här.
- Utvecklingsmiljö & verktyg (kategori A), motsvarande resonemang om driftägarskap (grundavbildning).

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Skanskas utvecklingsmetodik, version 1.0
