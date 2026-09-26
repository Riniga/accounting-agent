# Skapa en implementationsplan

Prompt för att låta Claude Code (eller ett annat AI-verktyg) skriva implementationsplanen
för en MVP. Planen svarar på *hur* MVP:n ska genomföras. Vad och varför står redan i
MVP-dokumentet. Ingen kod skrivs i det här steget.

## Innan du kör prompten

1. MVP:n finns i `docs/mvp/MVP-NNN-<slug>.md`, skriven enligt `docs/mvp/TEMPLATE.md`,
   och är godkänd av den som äger vad som ska byggas. En plan för en MVP som
   fortfarande ändras blir inaktuell direkt.
2. MVP:n är länkad från `docs/roadmap.md`.

## Så kör du den

Skriv till exempel:

> Kör docs/claude-prompts/create-plan-prompt.md

Claude läser filen och följer avsnittet *Prompt*. Du behöver inte ange MVP:n: Claude tar
reda på den i fas 0 och säger vilken den valde och varför. Vill du planera en annan MVP
än den som ligger närmast i tur, nämn den i samma meddelande.

För MVP-001 behövs normalt inte den här prompten, eftersom
`initialize-project.md` skriver den planen.

Räkna med en dialog. Claude stannar efter undersökningen och visar en disposition av
faserna innan hela planen skrivs. Det är billigare att rätta riktningen där än i en
färdig plan.

---

## Prompt

    Skapa implementationsplanen för nästa MVP. Arbeta i faserna nedan och
    stanna där det står STOPP.

    ## Fas 0 – Identifiera MVP:n

    Ta reda på vilken MVP som ska planeras, i den här ordningen:

    1. Den MVP jag nämner i mitt meddelande, om jag nämner någon.
    2. Den aktuella grenen, om den heter `feature/mvp-NNN-<slug>`.
    3. Den första MVP:n i docs/roadmap.md som har ett MVP-dokument i
       docs/mvp/ men ännu ingen plan i docs/plans/.

    Planen sparas som docs/plans/MVP-NNN-<slug>.plan.md med samma NNN och
    slug som MVP-filen. Skriv i första raden av ditt svar vilken MVP du valde
    och varför. Om källorna pekar på olika MVP:er, eller ingen passar: STOPP
    och fråga.

    Svara mig på svenska. Planen skrivs på det språk som anges i
    docs/standards/documentation.md.

    ## Fas 1 – Läs in

    Läs:

    1. MVP-dokumentet ovan. Det är den enda källan till vad som ska levereras.
    2. AGENTS.md och docs/development/methodology.md.
    3. docs/architecture/overview.md, docs/architecture/current-state.md och
       ADR:erna i docs/architecture/decisions/ som berör MVP:n.
    4. docs/standards/: coding.md, testing.md, git.md, documentation.md,
       dependencies.md, och threat-modeling.md om MVP:n rör säkerhet.
    5. docs/plans/TEMPLATE.md och docs/plans/EXAMPLE-plan.md (om den finns kvar).
    6. De metodikkapitel i docs/methodology/ som MVP:n berör, och motsvarande
       rader i docs/methodology-compliance/gap-register.md.
    7. Den befintliga kod som MVP:n kommer att röra. Läs den faktiskt, gissa
       inte hur den fungerar utifrån filnamn.

    ## Fas 2 – Undersök och disponera

    Undersök det som planen annars skulle behöva anta: mät en baslinje, kör
    ett verktyg mot den faktiska kodbasen, kontrollera att en funktion eller ett
    API verkligen finns och fungerar som MVP:n förutsätter. Använd bara
    läsande kommandon, ändra ingenting.

    Redovisa för mig:

    - Vad undersökningen visade, särskilt om något motsäger ett antagande i
      MVP:n.
    - Hur du tolkar MVP:ns omfattning: vad som är med, och vad som ligger nära
      men medvetet lämnas utanför.
    - En disposition: faserna i ordning, med en mening var om vad fasen
      levererar.
    - Om MVP:n har betydande säkerhetspåverkan (ny autentisering eller
      behörighet, ny extern yta, nytt flöde med känslig data, ändrad
      förtroendegräns) och därför behöver en STRIDE-genomgång.
    - Nya beroenden du ser behov av, och varför.
    - Frågor som påverkar planen.

    Om undersökningen visar att MVP:n bygger på ett felaktigt antagande, säg det
    rakt ut och föreslå hur MVP:n bör justeras. Skriv inte en plan som tyst
    avviker från MVP:n.

    STOPP. Vänta på mitt godkännande av dispositionen.

    ## Fas 3 – Skriv planen

    Spara planen enligt fas 0 och följ TEMPLATE.md:s
    avsnitt.

    - **0. Investigation:** det du fann i fas 2, med siffror och källa. Skriv
      ut var ett antagande i MVP:n visade sig fel och vad planen gör i stället.
    - **1. Goal:** vad som finns när planen är genomförd, i
      implementationstermer.
    - **2. Scope boundary:** In och Out, konkret. Nämn det som ligger nära till
      hands men inte ska göras.
    - **3. Chapters addressed:** metodikkapitel och rader i gap-registret som
      planen stänger. Ta bort avsnittet om projektet inte följer metodiken.
    - **4. TODOs:** grupperade i faser. Varje fas avslutas med ett förslag på
      commit-meddelande enligt docs/standards/git.md.
    - **5. Risks / open questions:** det som är osäkert, det som skjuts upp och
      varför, och STRIDE-genomgången om den behövs.
    - **6. Found during this MVP:** lämnas tomt ("*(none yet)*"). Det fylls
      under genomförandet med fixar som upptäcks utanför planen.

    Krav på TODO-listan:

    - Varje TODO är liten nog att genomföras och verifieras för sig, och anger
      hur den verifieras (vilket test, vilket kommando, vad som ska synas).
    - När ett AI-verktyg ska skriva produktionskod kommer testet som uttrycker
      önskat beteende i en egen TODO **före** implementationen, och testet
      granskas av en människa innan implementationen påbörjas (AI-TDD, se
      docs/standards/testing.md).
    - Dokumentation, ADR:er och current-state.md uppdateras i samma fas som
      ändringen de beskriver, inte i en samlad slutfas.
    - Ett nytt beroende får en egen TODO med motivering. Ett betydande beroende
      eller strukturbeslut får också en TODO för en ADR.
    - Sista fasen verifierar MVP:ns acceptanskriterier ett och ett, mot det
      faktiska systemet.
    - Ingen TODO rör något som står under Out.

    Sätt Status till "Not started – awaiting plan review". Skriv ingen
    implementationskod, varken i planen eller i andra filer.

    ## Fas 4 – Stäm av

    1. Gå igenom MVP:ns acceptanskriterier och visa vilken TODO som uppfyller
       vart och ett. Ett kriterium utan TODO är en lucka, lägg till den eller
       ta upp den som fråga.
    2. Sammanfatta planen: antal faser, antal TODOs, nya beroenden, ADR:er och
       öppna frågor.
    3. Föreslå ett namn på feature-grenen enligt docs/standards/git.md och ett
       commit-meddelande för själva planen. Skapa inte grenen och committa inte.

---

## Efter planen

1. **Granska planen.** Det är planens ägare som godkänner den innan
   implementationen börjar (Plan Review i `docs/development/methodology.md`).
2. **Skapa feature-grenen** och genomför planen en fas i taget. Be verktyget
   uppdatera planen löpande: bocka av TODOs och skriv en kort "Result:"-rad där
   utfallet blev ett annat än planerat.
3. **Avsluta MVP:n** med `complete-mvp.md` innan pull request.
