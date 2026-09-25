# Initiera projektet

Prompt för att låta Claude Code (eller ett annat AI-verktyg) gå från en projektidé till ett
uppstartat projekt: ifyllda styrdokument, en första roadmap, MVP-001 och en plan för den.
Ingen applikationskod skrivs i det här steget.

## Innan du kör prompten

1. Kopiera hela Grundplåten till roten av det nya repot, inklusive dotfiles (se
   `_LÄS-MIG-FÖRST.md`).
2. Lägg projektidén i **`docs/initial-idea.md`**. Den får vara ofullständig och rörig:
   anteckningar, ett mejl, en skiss i punktform. Det viktiga är att den finns. Innehåller
   den något konfidentiellt, rensa bort det först. Idéfilen blir AI-verktygets kontext.
3. Öppna repot i Claude Code och klistra in prompten nedan.

Räkna med en dialog, inte en enda körning. Claude stannar två gånger: efter analysen
(för att ställa frågor) och efter förslaget (för att få ditt godkännande). Först därefter
skrivs något till disk.

---

## Prompt

    Vi ska initiera ett nytt projekt från Grundplåten. Projektidén finns i
    docs/initial-idea.md. Arbeta i fem faser och stanna där det står STOPP.

    Svara mig på svenska. Projektdokumenten skrivs på det språk som anges i
    docs/standards/documentation.md.

    ## Fas 1 – Läs in

    Läs, i den här ordningen:

    1. _LÄS-MIG-FÖRST.md – vad Grundplåten innehåller och vad som ska ersättas.
    2. docs/initial-idea.md – projektidén. Det här är den enda källan till vad
       projektet ska göra.
    3. AGENTS.md och CLAUDE.md – arbetssättet och AI-reglerna.
    4. docs/development/methodology.md – processen Vision → Roadmap → MVP → Plan.
    5. docs/vision.md, docs/roadmap.md, docs/architecture/overview.md,
       docs/architecture/current-state.md – mallarna som ska fyllas i.
    6. docs/mvp/TEMPLATE.md, docs/mvp/EXAMPLE-mvp.md, docs/plans/TEMPLATE.md,
       docs/plans/EXAMPLE-plan.md – formatet för MVP och plan.
    7. docs/architecture/decisions/ADR-TEMPLATE.md.
    8. docs/methodology/index.md – bara indexet, inte alla kapitel.

    Sök sedan igenom hela trädet efter platshållare i vinkelparenteser (<...>) och
    lista vilka filer som har dem. Notera också vilka filer som förutsätter en
    viss teknikstack (till exempel pyproject.toml, environment.yml, pytest.ini,
    requirements.in och CI-flödet i .github/workflows/).

    ## Fas 2 – Analysera och fråga

    Redovisa för mig:

    - Din förståelse av idén, på högst tio rader: vad som ska byggas, för vem,
      och vilket problem det löser.
    - Vad idén säger tydligt, och vad den inte säger alls.
    - Om något i idéfilen ser ut att kunna vara känsligt (kunddata, interna
      system, hemligheter), flagga det innan du går vidare.

    Ställ sedan de frågor som behövs för att fylla i mallarna utan att gissa.
    Gruppera dem och håll dem till det som faktiskt saknas. Typiskt gäller det:

    - Projektnamn och kort namn (används i repo, miljöer och resurser).
    - Ägare: produktägare och ansvarig för tekniken.
    - Teknikstack, eller om den ännu är obestämd.
    - Repo- och CI-plattform (GitHub eller Azure DevOps) och driftmiljö.
    - Vilken data systemet hanterar och hur den klassas.
    - Integrationer mot andra system.
    - Vilket AI-verktyg teamet använder.
    - Kända tidskrav eller andra ramar.

    STOPP. Vänta på mina svar.

    ## Fas 3 – Föreslå

    Utifrån idén och mina svar, lägg fram ett samlat förslag, fortfarande utan
    att skriva något till disk:

    1. **Vision** – syfte, önskat resultat som förmågor, och några principer.
    2. **Roadmap** – 3–5 områden (R1, R2, …), vart och ett med en mening om vad
       det etablerar. Bara rubriker, inga detaljer.
    3. **MVP-001** – det första steget. Utgångspunkten är ett "walking skeleton":
       den tunnaste möjliga versionen som går hela vägen genom kedjan, med repo,
       vald stack, en minimal körbar del med ett test, CI med metodikens
       kvalitetsgrindar (lint, test, hemlighetsskanning, beroendeskanning) och,
       om det är aktuellt, driftsättning till en utvecklingsmiljö. Här ingår
       också en första metodikbedömning i docs/methodology-compliance/. Skälet
       är att grindarna ska finnas innan AI-verktyg börjar skriva produktionskod.
       Om idén talar för en annan första MVP, föreslå den och motivera varför.
    4. **MVP-002** – den första leveransen med verkligt användarvärde ur idén.
       Bara en rubrik och en mening. Den detaljeras först när MVP-001 är klar.
    5. **Arkitekturbeslut** – vilka ADR:er som behövs nu. Minst ett om att
       projektet följer utvecklingsmetodiken och ett om teknikstack och
       repostruktur (som "Proposed" om stacken inte är avgjord).
    6. **Anpassning av Grundplåten** – vilka filer som inte passar projektet
       (till exempel Python-specifika filer om stacken är en annan) och vad du
       föreslår: behålla, anpassa i MVP-001 eller ta bort.
    7. **Öppna frågor** – det som fortfarande är okänt och inte behöver avgöras
       nu.

    STOPP. Vänta på mitt godkännande eller mina ändringar.

    ## Fas 4 – Skriv

    När jag har godkänt, skriv eller uppdatera:

    - docs/vision.md
    - docs/roadmap.md, med MVP-001 länkad och MVP-002 som rubrik
    - README.md, AGENTS.md, CLAUDE.md och SECURITY.md – ersätt platshållarna,
      ändra inte reglerna i dem
    - docs/architecture/overview.md – beskriv läget som det är: det finns ingen
      kod än. Planerad struktur och stack skrivs under "Planned Evolution" och
      märks som planerad, inte som befintlig
    - docs/architecture/current-state.md – med applikationerna som "Planned"
    - ADR:erna från fas 3 i docs/architecture/decisions/, plus indexraden i
      README.md där
    - docs/mvp/MVP-001-<slug>.md enligt TEMPLATE.md
    - docs/plans/MVP-001-<slug>.plan.md enligt TEMPLATE.md, med TODOs i faser
      och ett förslag på commit-meddelande per fas. Avsnitt 0 (Investigation)
      beskriver vad som behöver undersökas eller mätas innan en siffra eller ett
      verktyg låses, i stället för att anta det
    - platshållare i docs/development/ och docs/standards/ som du kan fylla i
      utifrån mina svar. Lämna resten orörda och notera dem

    Regler under hela fasen:

    - Hitta inte på. Det som inte framgår av idén eller mina svar skrivs som
      "Unknown – to be decided" och tas upp under öppna frågor.
    - Skriv ingen applikationskod och skapa inga filer under apps/ eller
      packages/. Det görs i MVP-001 enligt planen.
    - Ändra inte docs/methodology/. Den är organisationens metodik, inte
      projektets.
    - docs/initial-idea.md lämnas oförändrad som historiskt underlag. Länka
      den från docs/vision.md.

    ## Fas 5 – Stäm av och avsluta

    1. Sök igen efter platshållare (<...>) och lista de som finns kvar, med
       skälet till att de står kvar.
    2. Föreslå, men utför inte, att följande tas bort: _LÄS-MIG-FÖRST.md,
       docs/mvp/EXAMPLE-mvp.md, docs/plans/EXAMPLE-plan.md och de filer i
       Grundplåten som enligt fas 3 inte passar projektet. Ta bort dem först
       när jag har sagt ja.
    3. Sammanfatta vad som har skapats och ändrats.
    4. Föreslå ett commit-meddelande. Committa inte själv.
    5. Beskriv nästa steg: granska planen för MVP-001, skapa en feature-gren
       och börja implementera fas för fas enligt AGENTS.md.

---

## Efter initieringen

- **Genomför MVP-001** fas för fas enligt planen. Planen är redan skriven, så
  `create-plan-prompt.md` behövs först för MVP-002.
- **Avsluta en MVP** med `complete-mvp.md` innan pull request.
- **Nästa MVP:** detaljera MVP-002 utifrån roadmapen med `docs/mvp/TEMPLATE.md`,
  och skapa sedan planen med `create-plan-prompt.md`.
