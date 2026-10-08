# Testa new-voucher i ett organisationsprojekt

Prompt för att låta Claude Code prova kommandot `accounting-agent new-voucher` på en
organisations riktiga bokföring, utan att röra den. Claude arbetar i en kopia: tar bort de
sista verifikationerna där, skapar dem igen med kommandot och jämför med originalen.

Testet svarar på en fråga: skapar kommandot samma verifikationer som redan finns, och
vägrar det när det ska?

## Innan du kör prompten

1. Kärnan ska vara installerad och ha kommandot. Kontrollera med
   `accounting-agent --help`; `new-voucher` ska finnas i listan.
2. Bokföringen ska vara hel. Har du själv tagit bort eller ändrat verifikationer för att
   prova, återställ dem först.
3. Öppna **organisationens projekt** (inte kärnans repo) i Claude Code och klistra in
   prompten nedan. Byt `hbg-judo` och `2026` om organisationen eller året är ett annat.

Claude stannar en gång, efter kontrollen av utgångsläget, om något inte stämmer. Annars
kör testet klart och slutar med en rapport. Inget i den riktiga mappen ändras.

---

## Prompt

    Du ska testa kommandot `accounting-agent new-voucher` från Accounting
    Agent-kärnan på den här organisationens bokföring. Organisationens id är
    hbg-judo och årets mapp är 2026.

    Kommandot skapar en verifikation för en banktransaktion. Den som anropar
    anger bara besluten (motkonto, underlag, anteckning). Datum, belopp, text
    och nummer hämtar kommandot ur kontoutdraget och bokföringen. Testet går ut
    på att ta bort några verifikationer som vi vet är rätt, låta kommandot skapa
    dem igen och se att resultatet blir detsamma.

    Svara mig på svenska.

    ## Regler för hela testet

    - Skriv aldrig i den riktiga mappen 2026. Allt du tar bort och skapar ska
      ligga i kopian. Den riktiga mappen får du bara läsa.
    - Skapa aldrig en verifikationsfil för hand, och rätta inte en fil som
      kommandot har skapat. Blir något fel är det ett testresultat: skriv upp
      det och gå vidare.
    - Försök inte lösa problem i bokföringen eller i kärnan. Rapportera dem.
    - Skriv inga personnummer i rapporten. Namn och verifikationstexter behövs
      inte heller: hänvisa till verifikationsnummer.
    - Kommandona nedan skrivs `accounting-agent ...`. Finns inte kommandot i
      terminalen, kör `conda run -n accounting-agent accounting-agent ...`.

    ## Steg 1 – Utgångsläget (bara läsning)

    Kör mot den riktiga mappen:

        accounting-agent validate hbg-judo --config-dir 2026 --unbooked

    Skriv upp raden RESULT och antalet verifikationer.

    STOPP och fråga mig om något av detta gäller:
    - resultatet är ERROR;
    - det finns obokförda transaktioner (rader med `[unbooked]` eller
      `[bank-unbooked]`). Då saknas verifikationer redan, och testet kan inte
      skilja dem från dem du själv tar bort.

    ## Steg 2 – Kopian

    Kopiera hela mappen 2026, med allt innehåll, till en tillfällig mapp utanför
    projektet och utanför molnsynkade mappar, till exempel
    `%TEMP%\new-voucher-test\2026`. Sökvägarna i organisation.yaml är relativa,
    så kopian fungerar som den är. Resten av testet körs med
    `--config-dir <kopian>`.

    Kör validate mot kopian och kontrollera att resultatet är detsamma som i
    steg 1.

    ## Steg 3 – Ta bort de fem sista

    I kopians verifikationsmapp: ta de fem verifikationerna med högst nummer.
    Ta bara från slutet, annars blir det luckor i numreringen.

    Läs de fem originalen i den riktiga mappen och skriv upp för var och en:
    nummer, datum, belopp, debet, kredit, underlag, och om anteckningen under
    fälten börjar med organisationens markering för gissad kontering
    (`conventions.guessed_posting_marker` i organisation.yaml).

    Ta sedan bort de fem filerna i kopian och kör:

        accounting-agent validate hbg-judo --config-dir <kopian> --unbooked

    Förväntat: fem rader `INFO [unbooked] bank statement row N: <datum>,
    <belopp>`, med samma datum och belopp som de fem du tog bort.

    ## Steg 4 – Skapa dem igen

    En i taget, äldst först (lägst nummer först):

        accounting-agent new-voucher hbg-judo --config-dir <kopian> --date <datum> --amount <belopp> --account <motkonto>

    - `--date` och `--amount`: som i originalet. Beloppet med bankens tecken,
      alltså negativt för pengar ut.
    - `--account`: motkontot, det av originalets debet och kredit som inte är
      bankkontot (`books.bank_account` i organisation.yaml).
    - `--document <filnamn>`: en gång per underlag i originalet.
    - `--row <rad>`: bara om kommandot svarar `transaction-ambiguous`. Välj då
      raden från listan i steg 3.
    - `--guess --note "<skäl>"`: om originalet var en gissad kontering. Annars
      `--note "<anteckning>"` om originalet hade en anteckning du vill ha med.

    Skriv upp vad kommandot svarade för var och en: skapad (med nummer) eller
    vägrad (med regeln inom hakparentes).

    ## Steg 5 – Jämför

    Jämför varje ny fil i kopian med originalet i den riktiga mappen.

    Ska vara lika: `verifikation`, `datum`, `belopp`, `debet`, `kredit` och
    `underlag`. Beloppet jämförs som tal (`600` och `600.00` är lika).

    Får skilja sig, men ska noteras:
    - `text`. Kommandot skriver bankens namn och meddelande som
      `namn(meddelande)`. Originalet kan vara ändrat för hand eller innehålla
      ett personnummer, som kommandot maskar. Skriv bara om texten är lika
      eller inte, inte vad den är.
    - Raderna under fälten. Kommandot lägger till en rad med kontonas namn
      (`Debet … · Kredit …`) och en länkrad per underlag. De finns inte i
      originalen.

    Kontrollera också, i varje ny fil:
    - att kontonamnen på raden `Debet … · Kredit …` stämmer med kontoplanen;
    - att varje länkrad pekar på en fil som finns i underlagsmappen.

    ## Steg 6 – Det ska vägras

    Räkna filerna i kopians verifikationsmapp före och efter varje försök.
    Antalet ska inte ändras, och varje försök ska ge ett felmeddelande.

    1. Kör det sista kommandot från steg 4 en gång till.
       Förväntat: `[already-booked]`.
    2. Samma kommando med `--account 9999`. Förväntat: `[account-unknown]`.
    3. Samma kommando med `--document finns-inte.pdf`.
       Förväntat: `[document-missing]`.
    4. Ett datum och belopp som inte finns i kontoutdraget.
       Förväntat: `[transaction-missing]`.

    ## Steg 7 – Kontrollera kopian

        accounting-agent validate hbg-judo --config-dir <kopian> --unbooked

    Förväntat: samma RESULT som i steg 1, samma antal verifikationer, inga
    obokförda transaktioner och inga fynd vars regel börjar på `generated-`.

    ## Steg 8 – Städa

    Ta bort den tillfälliga mappen. Kontrollera sedan att den riktiga mappen är
    orörd: validate ska ge exakt samma RESULT och antal verifikationer som i
    steg 1.

    ## Rapport

    Avsluta med:

    1. En rad: fungerade det eller inte.
    2. En tabell med en rad per verifikation: nummer, skapad eller vägrad,
       fälten lika (ja/nej, och i så fall vilket fält som skiljer), texten lika
       (ja/nej).
    3. De fyra vägringsförsöken: förväntad regel, faktisk regel, antal filer
       oförändrat (ja/nej).
    4. RESULT-raden från steg 1, steg 7 och steg 8.
    5. Allt som inte blev som förväntat, med kommandot du körde och hela
       felmeddelandet. Särskilt: om kommandot vägrade ett konto eller ett
       underlag som originalet använde.
