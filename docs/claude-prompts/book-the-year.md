# Bokför året från kontoutdrag och underlag

Prompt för att låta Claude Code bygga upp en organisations bokföring från början med
`accounting-agent new-voucher`: banktransaktionerna från kontoutdraget, och händelserna
utan banktransaktion – fakturor, lönekörningar, skattekontot – från underlagen.

Den används när årsmappen är uppsatt i kärnans format
([`set-up-organisation-project.md`](set-up-organisation-project.md)) och bokföringen är
tom, eller när nya banktransaktioner och underlag har kommit in.

## Innan du kör prompten

1. `accounting-agent validate` ska ge `RESULT: OK`.
2. Underlagen ska ligga i underlagsmappen.
3. Öppna **organisationens projekt** i Claude Code och klistra in prompten nedan. Byt
   `<id>` och `2026`.

Claude stannar en gång: efter att ha läst underlagen, med ett förslag på hur varje slag
av händelse ska konteras. Därefter körs allt igenom utan fler frågor, och du granskar
redovisningen efteråt. Har projektet redan konteringsregler som täcker allt hoppar
Claude över stoppet.

---

## Prompt

    Bokföringen för 2026 ska byggas upp från kontoutdraget och underlagen.
    Organisationens id är <id> och årets mapp är 2026. Följ projektets rutin
    och bokföringsregler om de finns. Svara mig på svenska.

    ## Regler

    - Skapa varje verifikation med `accounting-agent new-voucher`. Skriv aldrig
      en verifikationsfil själv, och ändra inte en fil som kommandot har
      skapat.
    - Räkna inte ut belopp. Skatt, arbetsgivaravgifter och nettolön står i
      underlaget. Stämmer inte underlagets siffror med varandra eller med
      banken: bokför inte, skriv upp det.
    - Gissa aldrig utan markering. Är du osäker på kontot: `--guess` med skälet
      i `--note`, eller parkera enligt reglerna.
    - Vägrar kommandot: läs skälet och rätta anropet. Går det ändå inte, skriv
      upp händelsen (datum, belopp, regeln som vägrade) och fortsätt.
    - Rör inte kontoutdrag, underlag, ingående balans eller budget. Behövs ett
      konto som saknas i kontoplanen: lägg till det enligt projektets regler,
      med BAS-benämningen, och säg det i rapporten.
    - Skriv inga personnummer i verifikationer, anteckningar eller dina svar.
      I `--text` skriver du vad händelsen är, till exempel "Lön april" eller
      "Faktura 12", inte vem den gäller.
    - Kommandona skrivs `accounting-agent ...`. Finns inte kommandot i
      terminalen, kör `conda run -n accounting-agent accounting-agent ...`.

    ## Kommandot har tre användningar

    En banktransaktion mot ett konto:

        accounting-agent new-voucher <id> --config-dir 2026 --date <datum> --amount=<belopp> --account <konto>

    En banktransaktion mot flera konton. Du anger den andra sidan; bankraden
    hämtas ur kontoutdraget, och raderna måste gå ihop med bankens belopp:

        accounting-agent new-voucher <id> --config-dir 2026 --date <datum> --amount=<belopp> --debit <konto>=<belopp> --credit <konto>=<belopp>

    En händelse utan banktransaktion. Du anger datum, text och alla rader, och
    debet ska vara lika med kredit. Bankkontot får inte vara med:

        accounting-agent new-voucher <id> --config-dir 2026 --date <datum> --text "<text>" --debit <konto>=<belopp> --credit <konto>=<belopp>

    Till alla tre: `--document <filnamn>` en gång per underlag, `--note=<text>`
    för en anteckning, `--row <rad>` när flera banktransaktioner har samma
    datum och belopp. Belopp skrivs med decimalpunkt. En verifikation hör till
    högst en banktransaktion.

    Bygger du anropen i ett skript: skicka varje flagga och varje värde som ett
    eget argument i en lista, inte som en hopsatt kommandorad, och skriv
    `--amount=<belopp>` och `--note=<text>` med likhetstecken. Kör det första
    anropet och kontrollera resultatet innan du kör resten.

    Texten på en banktransaktion hämtas av kommandot ur kontoutdraget, och
    personnummer i den maskas där. Du kan inte ange den själv.

    ## Steg 1 – Utgångsläget

        accounting-agent validate <id> --config-dir 2026 --unbooked

    Har bokföringen fel: försök inte lösa dem, gå till slutrapporten.

    ## Steg 2 – Läs underlagen och föreslå kontering

    Läs underlagen och kontoutdragets obokförda rader. Para ihop dem: vilket
    underlag hör till vilken banktransaktion, och vilka underlag har ingen
    banktransaktion alls?

    Gör en konteringsmall per slag av händelse, till exempel:

    - en utställd faktura, och dess betalning;
    - en lönekörning (bruttolön, avdragen skatt, arbetsgivaravgifter,
      nettolön), och löneutbetalningen från banken;
    - en inbetalning till eller dragning från skattekontot, och händelserna på
      skattekontot enligt dess utdrag;
    - en leverantörsfaktura eller ett kvitto;
    - bankens avgifter.

    För varje mall: vilka konton som debiteras och krediteras, vilket datum
    som gäller, om det blir en eller flera verifikationer, och vilket underlag
    som kopplas.

    Täcker projektets egna konteringsregler redan allt: följ dem och hoppa
    över stoppet. Annars:

    STOPP. Visa mig mallarna, och det du inte kunde para ihop eller avgöra.
    Vänta på mitt godkännande. Skriv sedan in de godkända mallarna i
    projektets bokföringsregler, så att de gäller nästa gång.

    ## Steg 3 – Bokför

    Gå igenom året i datumordning, äldst först, och skapa verifikationerna
    enligt mallarna. Banktransaktionerna tas i den ordning kontoutdraget listar
    dem. Händelser utan banktransaktion läggs in på sitt datum.

    Kommandot skriver ut varningar om verifikationen den just skapade. Läs dem.
    `documents-expected` betyder att underlag saknas: koppla ett om det finns.

    Kör validate då och då. Fel som gäller en verifikation du just skapade
    rättas inte genom att ändra filen: skriv upp det.

    ## Steg 4 – Avsluta

        accounting-agent validate <id> --config-dir 2026 --unbooked --balances
        accounting-agent report <id> --config-dir 2026

    Slutrapport:

    - antal verifikationer, varav hur många med fler än två rader och hur
      många utan banktransaktion;
    - antal gissningar, antal poster på parkeringskonto, och antal
      verifikationer som saknar underlag;
    - banktransaktioner du inte kunde bokföra, och underlag du inte kunde
      använda, med skälet;
    - RESULT-raden, och fel per regel om det finns några;
    - saldot på bankkontot enligt bokföringen, och om det stämmer med bankens
      senaste saldo om du har det;
    - vad jag som kassör behöver besluta. Committa inte.
