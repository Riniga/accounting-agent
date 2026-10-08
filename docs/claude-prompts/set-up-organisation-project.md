# Sätt upp ett organisationsprojekt i kärnans format

Prompt för att låta Claude Code sätta upp en organisations årsmapp så att Accounting
Agent-kärnan kan användas: konfiguration, kontoplan, ingående balans och importerat
kontoutdrag, fram till att `validate` ger `RESULT: OK` med noll verifikationer.

Kärnan har ett bokföringsformat, och organisationen anpassar sig till det
([ADR-010](../architecture/decisions/ADR-010-one-book-format.md)). Har organisationen en
äldre bokföring i ett annat upplägg konverteras den inte: bokföringen byggs upp på nytt
från kontoutdrag och underlag. Det görs med
[`book-the-year.md`](book-the-year.md), efter den här prompten.

## Innan du kör prompten

1. Kärnan ska vara installerad **på datorn**. Det görs en gång per dator, inte per
   projekt: organisationens projekt behöver inget installerat och ingen egen kopia av
   kärnan. Kontrollera med `conda run -n accounting-agent accounting-agent --help`.
   Fungerar det inte, följ "One-time setup" i
   [`organisation-projects.md`](../development/organisation-projects.md).
2. Årsmappen ska innehålla bankens exportfil och underlagen, och gärna BAS-kontoplanen
   som referens (`kontobas`, fyra CSV-filer).
3. Öppna **organisationens projekt** (inte kärnans repo) i Claude Code och klistra in
   prompten nedan. Byt årsmappen `2026` om året är ett annat.

Projektet behöver inte ha någon `CLAUDE.md` eller några bokföringsregler sedan tidigare.
Prompten skapar dem, så att Claude Code vet hur bokföringen sköts även i nästa session.

Claude stannar en gång, efter inventeringen, med ett förslag. Inget skrivs förrän du har
godkänt det.

---

## Prompt

    Det här projektet ska börja sköta sin bokföring med Accounting Agent-kärnan.
    Du ska sätta upp årsmappen 2026 i kärnans format, fram till att kärnans
    kontroll går igenom med noll verifikationer. Du ska inte bokföra något.

    Arbeta i fyra faser och stanna där det står STOPP. Svara mig på svenska.

    ## Regler

    - Rör inte bankens exportfiler eller underlagen. De läses bara.
    - Skapa inga verifikationer. Det görs i nästa steg, med kommandot
      `accounting-agent new-voucher`.
    - Ändra inte kärnan. Saknar kärnan något, skriv upp det i rapporten.
    - Skriv inga personnummer, och kopiera inte namn ur underlag eller
      kontoutdrag till konfiguration, kontoplan eller dina svar.
    - Finns en äldre bokföring i ett annat upplägg: rör den inte och
      konvertera den inte. Den är bara en källa till kontoplan och ingående
      balans.
    - Kommandona skrivs `accounting-agent ...`. Finns inte kommandot i
      terminalen, kör `conda run -n accounting-agent accounting-agent ...`.

    ## Fas 1 – Läs kärnan

    Ta reda på var kärnan ligger: kör `pip show accounting-agent` i kärnans
    miljö och läs raden "Editable project location". Hittar du den inte, fråga
    mig efter sökvägen.

    Läs där, och bara läs:

    1. `docs/development/organisation-projects.md` – hur ett
       organisationsprojekt använder kärnan, och hur `organisation.yaml` ser ut.
    2. `docs/architecture/overview.md`, avsnittet "Book formats" – filerna och
       deras kolumner.
    3. Ett färdigt exempel: `tests/fixtures/example-lines/organisation.yaml`
       och mappen `tests/fixtures/books/lines/` (kontoplan, ingående balans och
       fem verifikationer). Följ deras form exakt.
    4. `README.md`, avsnitten om kommandona.

    Kör också `accounting-agent --help` och `accounting-agent import-bank
    --help`.

    ## Fas 2 – Inventera (bara läsning)

    Gå igenom årsmappen 2026 och ta reda på:

    1. **Bankens exportfil:** var den ligger och vilken bank den kommer från.
       Kärnan läser `nordea-csv`, `sparbanken-syd-csv` och `swedbank-csv`. Säg
       vilken som passar, eller att ingen gör det. Säg också första och sista
       datum.
    2. **Andra utdrag**, till exempel från skattekontot eller från ett andra
       bankkonto. Kärnan stämmer av ett bankkonto, det som `books.bank_account`
       pekar ut. Andra utdrag importeras inte: de är underlag. Finns det flera
       bankkonton, säg vilket som har flest transaktioner och föreslå det som
       bankkonto. Importera aldrig ett annat kontos exportfil.
    3. **Underlagen:** hur många och av vilka slag (fakturor,
       lönespecifikationer, kvitton, skattekontoutdrag). Räkna, citera inte.
    4. **Kontoplan:** vilka konton behövs för de slag av händelser som finns?
       Utgå från en äldre kontoplan om det finns en, annars från underlagens
       slag. Slå upp varje konto i BAS-referensen (`kontobas`).
    5. **Ingående balans:** vad var balansen vid årets början? Källan är
       föregående års bokslut eller balansrapport. Finns ingen källa, säg det.
    6. **Byter organisationen kontoplan?** Om den ingående balansen är uppställd
       på en äldre kontoplan än den som ska gälla nu, behövs en översättning:
       vilket nytt konto varje gammalt konto motsvarar. Flera gamla konton kan
       gå till samma nya konto. Föreslå översättningen, men gissa inte: där du
       inte kan avgöra vad ett gammalt konto var, fråga.
    7. **Räkenskapsår:** kalenderår eller brutet.
    8. **Projektets instruktioner:** finns `CLAUDE.md` eller `AGENTS.md` i
       projektets rot, och finns det en fil med bokföringsregler? Säg vad som
       finns och vad som saknas.

    STOPP. Visa mig ett förslag:

    - organisationens id (små bokstäver och bindestreck) och mappstrukturen:
      var bokföringen, kontoutdragsfilen, underlagen, BAS-referensen och
      rapporterna ska ligga;
    - hela innehållet i `organisation.yaml`. Ta med avsnittet `reports` – mappen
      där rapporterna ska skrivas, organisationens namn och dess
      organisationsnummer – annars går redovisningen inte att skapa. Exemplet
      i kärnans testmapp saknar det avsnittet; mallen i
      `organisation-projects.md` har det;
    - kontoplanen som tabell: konto, BAS-benämning, eget kort namn. Håll den så
      liten som möjligt: bara konton som behövs nu. Fler läggs till när de
      behövs;
    - ingående balans per konto, med källan, och summan (ska vara 0). Vid byte
      av kontoplan: en tabell med gammalt konto, nytt konto och belopp, där
      summan per sida och totalt är densamma före och efter. Den tabellen är
      mitt beslut som kassör, och den sparas i regelfilen under "Rättelser och
      beslut";
    - konventionerna: bankkonto, parkeringskonto för osäkra poster, konton som
      inte behöver underlag (till exempel bankavgifter), och markeringen för
      gissad kontering;
    - vilka instruktionsfiler du tänker skapa eller ändra (se fas 3, punkt 4
      och 5);
    - det du inte kunde avgöra, som frågor till mig.

    Vänta på mitt godkännande.

    ## Fas 3 – Skriv

    Skapa det jag godkände, i kärnans format:

    1. `organisation.yaml` i årsmappen.
    2. `kontoplan.csv` och `ingående-balans.csv` i bokföringsmappen, och en tom
       mapp `verifikationer`. UTF-8 utan BOM, semikolon som avgränsare,
       radslut LF, decimalpunkt.
    3. Kontoutdraget:

           accounting-agent import-bank <id> --config-dir 2026 "<exportfilen>"

       Exportfilen ändras inte. Kommandot skriver kontoutdragsfilen dit
       `organisation.yaml` pekar.
    4. `CLAUDE.md` i projektets rot. Kärnans dokument
       `docs/development/organisation-projects.md` har ett avsnitt
       "Instructions for Claude Code in an organisation project" med texten som
       ska stå där. Kopiera den och sätt in organisationens id och år. Finns
       filen redan: lägg till avsnittet och behåll resten. Stryk rader som
       hänvisar till skript som inte finns i det här projektet.
    5. En fil med bokföringsregler i bokföringsmappen, `README.md`, om ingen
       finns. Håll den kort:
       - vilka filer som finns i mappen och vad de är;
       - konventionerna från `organisation.yaml`, i klartext;
       - en tom rubrik "Konteringsregler", där reglerna skrivs in när jag har
         godkänt dem i nästa steg;
       - en tom rubrik "Rättelser och beslut", för daterade beslut.

       Skriv inga konteringsregler själv. De bestäms av mig.

    ## Fas 4 – Kontrollera

        accounting-agent validate <id> --config-dir 2026 --unbooked

    Målet är `RESULT: OK` med 0 verifikationer, och en rad `[unbooked]` per
    banktransaktion.

    Kontrollera också att redovisningen går att skapa:

        accounting-agent report <id> --config-dir 2026

    Den ska skriva rapporterna till mappen i `reports.output`. Rapporterna är
    nästan tomma nu, men kommandot ska gå igenom.

    - Fel: läs meddelandet, rätta filen du skapade och kör igen. Rätta bara
      filer du själv har skapat i den här körningen.
    - `[bank-no-balances]` betyder att bankens export saknar saldo. Då kan
      kärnan inte kontrollera ingående balans på bankkontot mot banken.
      Kontrollera den själv mot ett kontoutdrag eller årsbesked, och säg vad
      du jämförde med.
    - `[bank-opening-balance]` är ett fel: ingående balans på bankkontot
      stämmer inte med bankens saldo före årets första transaktion. Rätta inte
      siffran för att få bort felet. Ta reda på vilken som är rätt, och fråga
      mig om du inte kan avgöra det.

    Avsluta med en kort rapport: vad som skapades, RESULT-raden, antal
    obokförda banktransaktioner, antal underlag per slag, och vad som återstår
    för mig att besluta innan bokföringen kan börja. Committa inte.
