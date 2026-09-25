# Arkitektur- och designprinciper på kodnivå

**Kategori:** B. Skriva kod
**Status:** utkast, kräver arkitektexpertens granskning innan fastställande (se Vägledning och Källor)
**Senast uppdaterad:** 2026-09-06
**Underlag:** 2026-09-06-arkitektur-och-designprinciper.md (internt forskningsunderlag, publiceras inte externt)

## Syfte

Kodkvalitet (spår: Kodkvalitet & clean code) handlar om en enskild klass. Det här dokumentet handlar om nivån däröver: hur klasser och moduler organiseras i förhållande till varandra, så att en kodbas går att förstå och förändra som helhet, inte bara fil för fil.

**Viktig läsanvisning:** de befintliga arkitekturprinciperna i organisationen där metodiken togs fram var ofullständiga (mest inriktade på integration) och användaren som tagit fram det här dokumentet saknar egen arkitektexpertis. Principerna nedan är en välgrundad utgångspunkt baserad på extern research, inte ett organisationsverifierat beslut. Se Källor för vad som specifikt behöver stämmas av med en arkitekt innan status kan bli "fastställd".

## Omfattning och avgränsning

Omfattar modularitet, lagerindelning och beroenderiktning för kod inom ett givet system.

Omfattar **inte**:

- Designkvaliteter inom en enskild klass (namngivning, funktionsstorlek, SOLID), se Kodkvalitet & clean code.
- Databasschema och datamodellering specifikt, se Datamodellering & databasdesign, även om gränserna ofta sammanfaller med det här dokumentets modulgränser.
- Lösningsarkitektur: systemgränser, teknikstack på övergripande nivå, infrastrukturbeslut, ligger utanför hela den här metodikens avgränsning (se PROJECT.md). Det här dokumentet stannar vid hur kod organiseras *inom* ett system.

## Krav (SKA)

1. Beroenden inom en kodbas ska peka mot affärslogiken/domänkärnan, aldrig mot infrastrukturdetaljer (databas, webbramverk, externa tjänster), oavsett vilket namngivet mönster som används för att uppnå det.
2. En modul eller komponent ska ha en explicit, avsiktlig gräns för vad som är dess publika yta och vad som är intern implementation, inte implicit avslöjat bara för att det är tekniskt åtkomligt.
3. Modulgränser ska genomdrivas tekniskt där verktygsstöd finns (t.ex. en lintingregel som blockerar otillåtna importer över en modulgräns), inte enbart följas som en skriven konvention.

## Rekommendationer (BÖR)

1. Bounded contexts (Domain-Driven Designs strategiska koncept, en tydlig, uttalad gräns för var en term eller modell har en specifik betydelse) används som utgångspunkt för att dra modul-/systemgränser, utan att kräva DDD:s fulla taktiska verktygslåda (aggregates, repositories, etc.).

## Undvik

1. **Att införa flera arkitekturlager** (t.ex. fullständig Clean Architecture med separata lager för entiteter, use cases, gränssnitt och ramverk) i ett litet system utan ett faktiskt behov av den flexibiliteten. Samma "AbstractFactoryFactory"-problem som i Kodkvalitet & clean code, fast på arkitekturnivå. Fler lager ger fler ställen för buggar att gömma sig i och kräver ofta omfattande mockning trots löftet om bättre testbarhet. **Gör istället:** börja med en enklare struktur och låt arkitekturen växa när ett verkligt behov uppstår.

## Vägledning och exempel

**Rekommenderat förstahandsexempel: Hexagonal Architecture (Ports & Adapters).** Clean, Hexagonal och Onion Architecture löser i grunden samma problem (beroenden pekar inåt) med olika vokabulär. Inget av dem är ett krav i sig; kravet är principen i krav 1. Hexagonal Architecture lyfts fram som exempel eftersom dess kärnmetafor (en kärna omgiven av portar och adaptrar) är konkret och lätt att förklara, och eftersom den är specifikt inriktad på hur ett system integrerar med sin omvärld, vilket passar väl när befintliga arkitekturprinciper främst handlar om integration.

**Arbetsdefinition för "system"** (föreslagen tumregel, inte ett fastslaget beslut): ett system är en tjänst som drivs och utvecklas av ett team. En lösning kan spänna över flera system. Det ger en praktisk avgränsning mellan det här dokumentets modulgränser (inom ett system) och lösningsarkitekturens systemgränser (mellan system).

## Undantag

För ett befintligt system där modulgränser inte redan är tekniskt genomdrivna (krav 3) kan en stegvis införandeplan användas istället för en omedelbar, fullständig omstrukturering, samma princip som redan gäller vid införande av ett formateringsverktyg på en befintlig kodbas (se Kodstandard & stil).

## Källor och ramverk

- Clean Architecture (Robert C. Martin), Hexagonal Architecture (Alistair Cockburn) och Onion Architecture (Jeffrey Palermo): tre namn för samma underliggande beroenderiktningsprincip.
- Dokumenterad, aktuell kritik mot överarkitektur i små/enkla system.
- Domain-Driven Design (Eric Evans), särskilt det strategiska konceptet bounded contexts.

**Krävs innan detta dokument kan fastställas:** granskning av en arkitekt i organisationen som kan (1) stämma av principerna ovan (särskilt rekommendationen om Hexagonal Architecture) mot organisationens befintliga arkitekturprinciper, och (2) ta ställning till hur bounded contexts (BÖR 1) ska kopplas till Datamodellering & databasdesign när det spåret skrivs. Se avsnittet "Kvarstående uppföljning" i det interna forskningsunderlaget.

## Relaterat

- Kodkvalitet & clean code (kategori B), designkvalitet inom en enskild klass, som det här dokumentet bygger vidare på.
- Datamodellering & databasdesign (kategori B), där bounded contexts kan komma att kopplas in efter arkitektgranskning.

---

**Version:** 1.0
**Datum:** 2026-09-07
**Ansvarig:** Rickard Nisses-Gagnér, Processledare Utvecklingsmetodik
**Del av:** Utvecklingsmetodiken, version 1.0
