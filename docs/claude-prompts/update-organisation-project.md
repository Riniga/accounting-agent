# Uppdatera ett organisationsprojekt till kärnans senaste version

Prompt för att låta Claude Code gå igenom ett organisationsprojekt och se till att dess
egna instruktioner – `CLAUDE.md`, rutinen (SOP), reglerna och konfigurationen – stämmer
med vad Accounting Agent-kärnan kan i dag.

Kör den varje gång kärnan har fått ett nytt kommando eller en ny regel, och alltid innan
du låter Claude bokföra efter en sådan ändring. Annars följer Claude en rutin som säger
något annat än kärnan gör, till exempel att verifikationer skrivs för hand.

Prompten ändrar bara instruktioner och konfiguration. Den rör aldrig bokföringsdata.

## Innan du kör prompten

1. Uppdatera kärnan (`git pull` i kärnans repo, eller checka ut den gren du vill använda).
2. Öppna **organisationens projekt** (inte kärnans repo) i Claude Code och klistra in
   prompten nedan. Byt `hbg-judo` och `2026` om organisationen eller året är ett annat.

Claude stannar en gång, efter genomgången, och visar vad som behöver ändras. Inget skrivs
förrän du har godkänt förslaget.

---

## Prompt

    Det här projektet sköter sin bokföring med Accounting Agent-kärnan. Kärnan
    har ändrats. Du ska se till att projektets egna instruktioner och
    konfiguration stämmer med kärnan som den är nu. Organisationens id är
    hbg-judo och årets mapp är 2026.

    Arbeta i fyra faser och stanna där det står STOPP. Svara mig på svenska.

    ## Regler

    - Ändra bara instruktioner, rutiner och konfiguration. Rör aldrig
      bokföringsdata: verifikationer, kontoplan, ingående balans, kontoutdrag,
      budget, kommentarer, medlemsfiler och underlag ska vara orörda.
    - Ändra inte vad reglerna säger om bokföringen: konteringsregler, kassörens
      beslut och beslutsloggen. Du ändrar hur saker görs, inte vad som är rätt.
      Tycker du att en regel behöver ändras, skriv det som en fråga till mig.
    - Ändra inte kärnan. Saknar kärnan något, skriv upp det i rapporten.
    - Skriv inga personnummer, och kopiera inte namn eller verifikationstexter
      till instruktionsfilerna.
    - Kommandona skrivs `accounting-agent ...`. Finns inte kommandot i
      terminalen, kör `conda run -n accounting-agent accounting-agent ...`.

    ## Fas 1 – Läs kärnan

    Ta reda på var kärnan ligger: kör `pip show accounting-agent` i kärnans
    miljö och läs raden "Editable project location". Hittar du den inte, fråga
    mig efter sökvägen.

    Läs där, och bara läs:

    1. `docs/development/organisation-projects.md` – hur ett
       organisationsprojekt använder kärnan. Det här är huvudkällan. Avsnittet
       "Instructions for Claude Code in an organisation project" innehåller
       texten som ska stå i projektets CLAUDE.md.
    2. `README.md` – kommandona och `organisation.yaml`.
    3. `docs/architecture/decisions/` – de två senaste ADR:erna, och de som
       huvudkällan hänvisar till.

    Kör också `accounting-agent --help` och `accounting-agent <kommando> --help`
    för varje kommando. Det som hjälptexten säger gäller, om den och
    dokumenten skiljer sig.

    Sammanfatta för dig själv: vilka kommandon finns, vad skriver kärnan, vad
    vägrar den, och vad säger den att organisationen fortfarande gör själv.

    ## Fas 2 – Läs projektet och jämför

    Läs projektets egna instruktioner:

    - `CLAUDE.md` och `AGENTS.md`, om de finns;
    - `2026/organisation.yaml`;
    - rutinen steg för steg (till exempel `2026/Bokföring/SOP.md`);
    - reglerna för bokföringen (till exempel `2026/Bokföring/README.md`);
    - beskrivningen av projektets egna skript (till exempel
      `2026/agent/README.md`).

    Kör sedan, och spara bara antal per regel:

        accounting-agent validate hbg-judo --config-dir 2026 --unbooked

    Gör en lista över skillnader. Leta särskilt efter:

    1. **Steg som görs för hand men som kärnan nu gör.** Till exempel att en
       verifikationsfil skrivs för hand, att nästa nummer räknas ut för hand,
       eller att ett eget skript körs där kärnan har ett kommando.
    2. **Regler som säger emot kärnan.** Till exempel hur en verifikationsfil
       ser ut, vad som får stå under fälten, eller vad som räknas som fel.
    3. **Avsnittet om kärnan i CLAUDE.md.** Jämför ord för ord med kärnans
       text i huvudkällan.
    4. **Konfigurationen.** Finns varje avsnitt som kommandona behöver, och
       varje konvention som rutinen förutsätter (till exempel markeringen för
       gissad kontering och konton som inte behöver underlag)?
    5. **Filnamn och hänvisningar som beror på verifikationsnummer.**
       Underlag som heter som ett verifikationsnummer, och filer som hänvisar
       till verifikationer med nummer (kommentarer, medlemsbetalningar). Säg
       vilka filer det gäller och hur många rader, inte vad som står där.
    6. **Fel i bokföringen just nu.** Kommandot som skapar verifikationer
       vägrar när bokföringen har fel. Säg vilka regler som ger fel och hur
       många, och vad som behöver göras för att bokföringen ska gå att
       fortsätta på. Är bokföringen tom eller ofullständig, säg det.
    7. **Sådant som projektets egna skript fortfarande behövs för.** Det ska
       stå kvar i rutinen.

    STOPP. Visa mig:

    - en tabell: fil, vad den säger i dag, vad den bör säga, och varför;
    - det som inte är en instruktionsändring utan ett beslut för mig som
      kassör, som frågor;
    - det som kärnan saknar.

    Vänta på mitt godkännande. Jag kan stryka eller ändra rader.

    ## Fas 3 – Skriv

    Gör de ändringar jag godkände, och bara dem.

    - I CLAUDE.md: ersätt avsnittet om kärnan med kärnans nuvarande text,
      med organisationens id och år insatta. Behåll resten av filen.
    - I rutinen: skriv om de berörda stegen så att de använder kärnans
      kommandon, med kommandot utskrivet. Behåll stegens numrering om det går,
      eftersom andra dokument hänvisar till dem.
    - I reglerna: rätta beskrivningen av filformat och arbetsflöde. Lägg en
      daterad rad i beslutsloggen om att rutinen har ändrats och varför.
    - Ta inte bort projektets egna skript. Skriv i rutinen vilka som har
      ersatts av kärnan och vilka som fortfarande används.

    ## Fas 4 – Kontrollera

    1. Läs rutinen från början till slut som om du skulle bokföra en ny
       banktransaktion. Finns varje kommando du behöver utskrivet, och säger
       något steg emot ett annat?
    2. Kör `--help` för varje kommando som rutinen nämner och kontrollera att
       flaggorna i rutinen finns.
    3. Kör validate igen. Antalet fynd per regel ska vara som i fas 2: du har
       inte rört bokföringen.
    4. Visa `git status` och en sammanfattning av varje ändrad fil. Committa
       inte.

    Avsluta med en kort rapport: vad som ändrades, vad som återstår för mig
    att besluta, och om rutinen nu går att följa från början till slut.
