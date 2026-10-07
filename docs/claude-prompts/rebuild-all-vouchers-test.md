# Bygg om alla verifikationer i en kopia

Prompt för att låta Claude Code pröva `accounting-agent new-voucher` på en hel
årsbokföring: i en kopia tas **alla** verifikationer bort och skapas igen med kommandot,
en i taget, med originalens beslut (motkonto, underlag, anteckning). Sedan jämförs
resultatet med originalen, fält för fält och saldo för saldo.

Det är samma test som [`test-new-voucher.md`](test-new-voucher.md), men på allt i stället
för de fem sista. Kör den lilla varianten först om kommandot aldrig har provats i
projektet.

## Innan du kör prompten

1. Kärnan ska vara installerad och ha kommandot. Kontrollera med
   `accounting-agent --help`; `new-voucher` ska finnas i listan.
2. Bokföringen ska vara hel: `validate` ska ge `RESULT: OK` och inga obokförda
   transaktioner.
3. Öppna **organisationens projekt** (inte kärnans repo) i Claude Code och klistra in
   prompten nedan. Byt `hbg-judo` och `2026` om organisationen eller året är ett annat.

Den riktiga mappen ändras inte. Kopian med den ombyggda bokföringen lämnas kvar, så att
du kan titta på den. Om den ombyggda bokföringen ska ersätta den riktiga är kassörens
beslut och ingår inte i testet.

---

## Prompt

    Du ska testa kommandot `accounting-agent new-voucher` från Accounting
    Agent-kärnan genom att bygga om hela årets verifikationer i en kopia.
    Organisationens id är hbg-judo och årets mapp är 2026.

    Kommandot skapar en verifikation för en banktransaktion. Den som anropar
    anger bara besluten (motkonto, underlag, anteckning). Datum, belopp, text
    och nummer hämtar kommandot ur kontoutdraget och bokföringen. Besluten finns
    redan, i de befintliga verifikationerna. Testet är att ta bort alla
    verifikationer i en kopia, skapa dem igen med kommandot utifrån de besluten,
    och se att bokföringen blir densamma.

    Svara mig på svenska.

    ## Regler för hela testet

    - Skriv aldrig i den riktiga mappen 2026. Den får du bara läsa. Allt du tar
      bort och skapar ska ligga i kopian.
    - Varje verifikation ska skapas av kommandot `new-voucher`. Skriv aldrig en
      verifikationsfil själv, varken för hand eller från ett skript, och rätta
      inte en fil som kommandot har skapat.
    - Du får skriva ett hjälpskript som anropar kommandot en gång per
      verifikation och loggar svaret. Lägg skriptet och loggen i den tillfälliga
      mappen, inte i projektet.
    - Blir något fel är det ett testresultat. Försök inte lösa problem i
      bokföringen eller i kärnan. Rapportera dem.
    - Skriv inga personnummer, namn eller verifikationstexter i rapporten eller
      i loggen. Hänvisa till verifikationsnummer.
    - Kommandona nedan skrivs `accounting-agent ...`. Finns inte kommandot i
      terminalen, kör `conda run -n accounting-agent accounting-agent ...`.

    ## Steg 1 – Utgångsläget (bara läsning)

    Kör mot den riktiga mappen och spara utskriften i den tillfälliga mappen:

        accounting-agent validate hbg-judo --config-dir 2026 --unbooked --balances

    Skriv upp raden RESULT, antalet verifikationer och antalet fynd per regel.
    Saldona under `BALANCES` är facit för steg 6.

    STOPP och fråga mig om resultatet är ERROR, eller om det finns obokförda
    transaktioner (rader med `[unbooked]` eller `[bank-unbooked]`).

    ## Steg 2 – Arbetslistan (bara läsning)

    Läs alla verifikationer i den riktiga mappen, i nummerordning, och gör en
    arbetslista med en rad per verifikation:

    - nummer;
    - datum;
    - belopp, med tecken som i fältet `belopp`;
    - motkonto: det av `debet` och `kredit` som inte är bankkontot
      (`books.bank_account` i organisation.yaml);
    - underlag: filnamnen i fältet `underlag`, åtskilda av semikolon;
    - anteckning: all text under fälten, alltså efter den andra raden `---`;
    - gissning: ja om anteckningen börjar med organisationens markering för
      gissad kontering (`conventions.guessed_posting_marker` i
      organisation.yaml) följd av kolon.

    STOPP och fråga mig om någon verifikation inte har bankkontot på ena sidan.
    Kommandot skapar bara verifikationer för banktransaktioner.

    ## Steg 3 – Kopian

    Kopiera hela mappen 2026, med allt innehåll, till en tillfällig mapp utanför
    projektet och utanför molnsynkade mappar, till exempel
    `%TEMP%\rebuild-test\2026`. Sökvägarna i organisation.yaml är relativa, så
    kopian fungerar som den är.

    Ta bort alla verifikationsfiler i kopians verifikationsmapp. Mappen själv
    ska finnas kvar, tom.

    Koppla sedan bort kommentarsfilen i kopian: spara en kopia av kopians
    organisation.yaml och ta bort raden `comments_file:` under `checks`.
    Kommentarerna hänvisar till verifikationsnummer, och så länge de
    verifikationerna inte finns är det ett fel (`comment-unknown-voucher`).
    Kommandot vägrar när bokföringen har fel. Raden läggs tillbaka i steg 6.

    Kör sedan:

        accounting-agent validate hbg-judo --config-dir <kopian> --unbooked

    Förväntat: 0 verifikationer, inga fel, och lika många `[unbooked]`-rader som
    det finns rader i kontoutdraget. STOPP och fråga mig om det finns fel.

    ## Steg 4 – Skapa alla igen

    Gå igenom arbetslistan i nummerordning och kör för varje rad:

        accounting-agent new-voucher hbg-judo --config-dir <kopian> --date <datum> --amount=<belopp> --account <motkonto>

    med dessa tillägg:

    - `--document <filnamn>`, en gång per underlag.
    - Anteckning: är raden en gissning, ge `--guess --note=<skälet>`, där
      skälet är anteckningen utan markeringen och kolonet i början. Annars
      `--note=<anteckningen>` om den inte är tom. Skicka anteckningen
      oförändrad, med radbrytningar.
    - Skriv `--amount=` och `--note=` med likhetstecken, som ovan. Ett värde
      som börjar med bindestreck tolkas annars som en flagga.
    - `--row <rad>` när flera rader i kontoutdraget har samma datum och belopp.
      Raden är radnumret i kontoutdragsfilen (`bank.statement_file`), där
      rubrikraden är rad 1. Välj så här bland raderna med rätt datum och belopp
      som du inte redan har använt:
        1. raden vars text är lika med originalets `text`, där radens text är
           `namn(meddelande)`, eller bara `namn` när meddelandet är tomt;
        2. annars den lägsta raden.
      Räkna hur många gånger du fick använda regel 2.

    Nummerordning är viktig: kommandot ger nästa lediga nummer, så numren blir
    desamma som originalens bara om ordningen är densamma.

    Logga för varje rad: originalets nummer, och om den skapades (med numret
    kommandot gav) eller vägrades (med regeln inom hakparentes). Kommandot kan
    också skriva varningar om den nya verifikationen; räkna dem per regel.

    STOPP slingan direkt om en verifikation vägras eller får ett annat nummer än
    originalet. Alla följande nummer skulle då förskjutas. Gå till rapporten och
    redovisa hur långt du kom, kommandot du körde och hela felmeddelandet.

    Under tiden kan validate visa `[bank-unbooked]` som fel för äldre
    transaktioner, om originalen inte är bokförda i datumordning. Det stoppar
    inte kommandot och är väntat.

    ## Steg 5 – Jämför fil för fil

    Jämför varje verifikation i kopian med originalet med samma nummer.

    Ska vara lika, räkna antalet som är det:
    - filnamnet;
    - `verifikation`, `datum`, `debet`, `kredit`;
    - `belopp`, jämfört som tal (`600` och `600.00` är lika);
    - `underlag`, jämfört som lista av filnamn;
    - anteckningen: texten under de genererade raderna i den nya filen ska vara
      lika med originalets text under fälten, bortsett från blanksteg och
      tomrader i början och slutet. Har originalet ett personnummer i
      anteckningen maskar kommandot det; räkna de fallen för sig.

    Får skilja sig, räkna antalet:
    - `text`. Originalet kan vara ändrat för hand eller innehålla ett
      personnummer, som kommandot maskar som `[personnummer]`. Dela upp
      skillnaderna i: originalet har personnummer, och övriga.

    Nytt i varje fil, kontrollera att det stämmer:
    - en rad `Debet <konto> <namn> · Kredit <konto> <namn>`, där kontona är
      fältens och namnen är kontoplanens;
    - en rad `Underlag: [<filnamn>](<...>)` per underlag, i fältets ordning.

    ## Steg 6 – Jämför bokföringen

    Lägg först tillbaka kopians ursprungliga organisation.yaml, med raden
    `comments_file:`. Kör sedan:

        accounting-agent validate hbg-judo --config-dir <kopian> --unbooked --balances

    Jämför med utskriften från steg 1:

    - `BALANCES`: varje konto ska ha samma saldo. Jämför som tal: `12.5` och
      `12.50` är lika. Det här är testets viktigaste rad.
    - antalet verifikationer ska vara detsamma;
    - inga obokförda transaktioner, och inga fynd vars regel börjar på
      `generated-`;
    - antalet fynd per regel. Två skillnader är väntade: `personal-number` kan
      bli färre, eftersom kommandot maskar personnummer i text och anteckning,
      och `voucher-duplicate` kan ändras när texter ändras. Allt annat ska vara
      lika, också `comment-unknown-voucher` (inga).

    ## Steg 7 – Lämna kopian, kontrollera originalet

    Ta inte bort kopian. Skriv ut var den ligger.

    Kör validate mot den riktiga mappen en sista gång. RESULT och antalet
    verifikationer ska vara exakt som i steg 1.

    ## Rapport

    Avsluta med:

    1. En rad: blev bokföringen densamma eller inte.
    2. Antal: verifikationer i arbetslistan, skapade, vägrade.
    3. Jämförelsen fil för fil: antal lika per fält, och numren på dem som
       skiljer sig, per fält.
    4. Texterna: antal lika, antal där originalet har personnummer, antal
       övriga. Anteckningarna: antal lika, antal med maskat personnummer, antal
       övriga.
    5. Hur många gånger raden valdes med regel 2 i steg 4.
    6. Saldona: lika på alla konton, eller vilka konton som skiljer sig och med
       hur mycket.
    7. RESULT-raden från steg 1, steg 6 och steg 7, och antalet fynd per regel
       i steg 1 och steg 6 sida vid sida.
    8. Varningar som kommandot skrev ut i steg 4, antal per regel.
    9. Allt som inte blev som förväntat, med kommandot du körde och hela
       felmeddelandet.
    10. Sökvägen till kopian.
