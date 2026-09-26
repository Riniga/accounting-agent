# Avsluta en MVP

Prompt för att låta Claude Code (eller ett annat AI-verktyg) gå igenom en färdig MVP innan
pull request. Det här är MVP Review i `docs/development/methodology.md`. Hela
ändringsuppsättningen granskas mot MVP:n, planen, standarderna och Definition of Done.
Det som saknas åtgärdas, och allt valideras igen.

Erfarenheten är att det är här saker fångas som annars glöms: dokumentation som inte
hängt med, en plan som inte uppdaterats, ett acceptanskriterium som bara antogs vara
uppfyllt, en ny miljövariabel som saknas i `.env.example`. Hoppa inte över steget för
att MVP:n känns klar.

## Innan du kör prompten

1. Alla faser i planen är genomförda och committade på feature-grenen.
2. Arbetskopian är ren, så att det som granskas är det som faktiskt ligger i grenen.

## Så kör du den

Stå på MVP:ns feature-gren och skriv till exempel:

> Kör docs/claude-prompts/complete-mvp.md

Claude läser filen och följer avsnittet *Prompt* nedan. Du behöver inte ange vilken MVP
det gäller: Claude tar reda på det i fas 0 och säger vilken MVP den valde och varför.
Vill du avsluta en annan MVP än den grenen pekar på, nämn den bara i samma meddelande.

Claude åtgärdar självklara luckor direkt, till exempel dokumentation som inte
uppdaterats eller ett saknat test för beteende som redan ingår i MVP:n. Allt som ändrar
beteende, omfattning eller ett beslut tas upp med dig först.

---

## Prompt

    Avsluta den aktuella MVP:n och förbered den för pull request. Arbeta i
    faserna nedan och stanna där det står STOPP.

    Svara mig på svenska. Projektdokumenten skrivs på det språk som anges i
    docs/standards/documentation.md.

    ## Fas 0 – Identifiera MVP:n

    Ta reda på vilken MVP som ska avslutas, i den här ordningen:

    1. Den MVP jag nämner i mitt meddelande, om jag nämner någon.
    2. Den aktuella grenen: `feature/mvp-NNN-<slug>` pekar på
       docs/mvp/MVP-NNN-*.md och docs/plans/MVP-NNN-*.plan.md.
    3. Den plan i docs/plans/ vars Status är "In progress" eller
       "Implemented".

    Skriv i första raden av ditt svar vilken MVP du valde och varför, till
    exempel "MVP-002 (från grenen feature/mvp-002-common-book-model)". Om
    källorna pekar på olika MVP:er, eller ingen passar: STOPP och fråga.

    Finns det redan en öppen pull request för grenen (gh pr list --head
    <grenen>), ge PR-beskrivningen i fas 4 som en ersättning för den
    befintliga, inte som en ny.

    ## Fas 1 – Läs in

    Läs:

    1. MVP-dokumentet och dess plan i docs/plans/.
    2. AGENTS.md och docs/development/methodology.md (avsnittet MVP Review).
    3. docs/standards/: coding.md, testing.md, git.md, documentation.md,
       dependencies.md, och threat-modeling.md om MVP:n rör säkerhet.
    4. .github/pull_request_template.md. Dess Definition of Done är
       checklistan pull requesten ska uppfylla.
    5. .github/workflows/ci.yml, så att du vet vilka kontroller CI kör.
    6. docs/architecture/overview.md, current-state.md och ADR-indexet.
    7. docs/methodology-compliance/gap-register.md, de rader planen säger
       att den stänger.

    Gå sedan igenom hela ändringsuppsättningen mot main: git log och git diff
    för grenen. Läs ändringarna, inte bara filnamnen.

    ## Fas 2 – Granska

    Kontrollera punkterna nedan. Verifiera mot det faktiska systemet och den
    faktiska koden. Ett kriterium är inte uppfyllt för att planen säger att det
    är gjort.

    **Mål och omfattning**
    - MVP:ns mål är uppnått, och varje acceptanskriterium är verifierat ett och
      ett. Ange hur (test, kommando, observation).
    - Varje TODO i planen är avbockad, eller har en "Result:"-rad som förklarar
      varför utfallet blev ett annat.
    - Inga ändringar ligger utanför planens Scope boundary, och ingen orelaterad
      refaktorering har blandats in.

    **Kod**
    - Koden följer coding.md och är enkel att förstå.
    - Ingen onödig komplexitet eller abstraktion i förtid. Kod har bara flyttats
      till ett delat paket om den faktiskt används av minst två appar.
    - Inga kvarglömda felsökningsutskrifter, bortkommenterad kod, döda grenar
      eller TODO-kommentarer utan ägare.

    **Test**
    - Nytt beteende har tester, och varje buggrättning har ett regressionstest.
    - För AI-skriven produktionskod fanns testet före implementationen och var
      granskat av en människa (AI-TDD). Kontrollera det i planen och
      commit-historiken.
    - Testerna är deterministiska och kör utan nätverk. Täckningsgolvet hålls.
      Inga nya tester i karantän utan ägare och slutdatum.

    **Säkerhet och beroenden**
    - Inga hemligheter i koden eller historiken. Granska särskilt AI-genererad
      kod efter hårdkodade värden.
    - Nya miljövariabler finns i .env.example, utan värden.
    - STRIDE-genomgång finns i planen om MVP:n har betydande säkerhetspåverkan.
    - Nya beroenden är motiverade i planen, låsfilen är uppdaterad och
      licenserna tillåtna enligt dependencies.md.
    - Databasmigrationer, om några, är bakåtkompatibla med den version som kör.
    - Loggning läcker inte hemligheter eller personuppgifter.

    **Drift**
    - Ny funktionalitet har den loggning och de mätvärden som behövs för att
      kunna drivas och felsökas.

    **Dokumentation**
    - README.md och AGENTS.md stämmer, till exempel kommandon, struktur och
      lokala körinstruktioner.
    - docs/architecture/overview.md och current-state.md stämmer, inklusive
      appstatus och antal tester.
    - Viktiga arkitekturbeslut har en ADR och en rad i ADR-indexet. En godkänd
      ADR har inte redigerats, den har ersatts.
    - docs/development/ är uppdaterad om uppsättningen av miljön har ändrats.
    - docs/standards/ är uppdaterad om en konvention har ändrats.

    **Metodik**
    - Gap-registrets rader som MVP:n stänger är uppdaterade. Nya luckor som
      upptäckts är tillagda.
    - Projektval som gjorts under MVP:n finns i interpretations.md, och
      tidsbegränsade avvikelser finns i exceptions.md.

    **Git**
    - Inga temporära filer, genererade artefakter, cachar, stora filer eller
      .env är committade.
    - Commit-meddelandena följer git.md, och grenens namn följer
      namnstandarden.

    Redovisa resultatet i tre grupper:

    - **A. Åtgärdas direkt:** luckor som inte ändrar beteende, omfattning
      eller beslut. Till exempel dokumentation, planens status, ett saknat test
      för beteende som redan ingår, kvarglömd felsökningskod.
    - **B. Behöver ditt beslut:** allt som ändrar beteende eller omfattning,
      ett acceptanskriterium som inte är uppfyllt, eller ett säkerhetsfynd.
    - **C. Uppföljning:** sådant som hör hemma i en senare MVP eller i
      backlogen, inte i den här.

    Åtgärda grupp A. Finns det något i grupp B, STOPP och vänta på mitt beslut.

    ## Fas 3 – Validera igen

    Kör lokalt samma kontroller som CI kör enligt ci.yml, till exempel
    pre-commit över alla filer, hela testsviten med täckning och skanningen
    av instruktionsfiler. Redovisa det faktiska resultatet. Om något fallerar,
    åtgärda det och kör om. Påstå aldrig att en kontroll gått igenom utan att
    ha kört den.

    ## Fas 4 – Stäng MVP:n och förbered pull request

    1. Fyll i "Outcome at close" i MVP-dokumentet med dagens datum. Ge ett
       ärligt utfall (delivered, partially delivered eller not delivered) och
       redovisa kriterium för kriterium vad som faktiskt blev av, även det som
       inte blev som tänkt.
    2. Sätt planens Status till "Implemented – pending PR".
    3. Uppdatera "Current Status" i docs/roadmap.md, och för in punkterna i
       grupp C i backlogen eller gap-registret.
    4. Ge mig:
       - en sammanfattning av vad MVP:n levererade
       - vilka kontroller som kördes, med resultat
       - vad som ändrades under avslutet
       - kvarstående risker och öppna frågor
       - förslag på commit-meddelande för ändringarna under avslutet
       - förslag på PR-titel
       - PR-beskrivning ifylld enligt .github/pull_request_template.md, med
         varje punkt i Definition of Done avbockad eller överstruken med en
         kort motivering

    Committa inte, pusha inte, skapa inte pull requesten och merga inte.

---

## Efter avslutet

1. Granska ändringarna från avslutet och committa dem.
2. Skapa pull requesten med den föreslagna beskrivningen. Minst en annan
   människa än författaren granskar och godkänner.
3. När pull requesten är mergad: detaljera nästa MVP från roadmapen med
   `docs/mvp/TEMPLATE.md` och skapa planen med `create-plan-prompt.md`.
