# Výskum 12 účtov — čo z toho vieme použiť

2026-08-16. Zdroj zoznamu: @ai_explorer25, 16. 8. 2026.

**Poctivosť o pokrytí.** Do hĺbky som išiel po tých, ktorých práca sa dotýka
nášho problému: **Chip Huyen, Andrew Ng, Sebastian Raschka, Andrej Karpathy**
a praxi Claude Code (Boris Cherny, Thibault Sottiaux — cez oficiálnu
dokumentáciu, nie ich osobné texty). **Nepreskúmané:** Fei-Fei Li, Demis
Hassabis, Ilya Sutskever, Gary Marcus, Maxime Labonne. Prvé tri robia
frontier výskum, ktorý nám tento mesiac prácu nezmení; Marcusa a Labonna som
nečítal a nebudem predstierať opak. **Karpathyho mám cez sekundárne zhrnutia**,
nie z primárnych textov — beriem to ako slabší dôkaz.

---

## 1. Jedna veta, na ktorej sa zhodnú všetci

Karpathy to hovorí najostrejšie — **klasické počítače automatizujú to, čo vieš
špecifikovať; LLM automatizujú to, čo vieš overiť.** Modely sú „zubaté":
špičkové tam, kde existuje overiteľná odpoveď (kód, matematika), slabé
v nejednoznačnom.

To isté z iných strán:

| Kto | Formulácia |
|---|---|
| **Ng** | rozdiel oproti bežnému softvéru je nepredvídateľný výstup → remeslom je merať a riadiť |
| **Huyen** | vývoj riadený evaluáciou; bez ľudskej kontroly sa sudca nedá použiť |
| **Raschka** | *„implementácia neklame"* — porovnáva medzivýpočty s referenciou, kým nesedia |
| **Kopadze** | topológia nekupuje pravdu, treba kotvy |
| **Claude Code** | *„daj Claudovi kontrolu, ktorú vie spustiť"* — inak si overovacou slučkou ty |

**Dôsledok pre náš koncept, a je to silnejšie, než sme to mali:** firmy
nevyužívajú AI na 5 % nie preto, že je slabá, ale preto, že **svoju prácu nemajú
overiteľnú**. Nepredávame znalosť do AI. Predávame **prevod firemného
rozhodovania do overiteľnej podoby**. To je jediná vec, ktorá odomkne zvyšok.

---

## 2. Chip Huyen — najpriamejší zásah do našej metodiky

### 2.1 Šesť pascí, z ktorých sme do štyroch spadli

| Pasca | My |
|---|---|
| **Zbytočná zložitosť na začiatku** — začni priamymi volaniami, zložitosť pridávaj až keď je dokázaná | **spadli sme** — päť verzií pravidiel bez zmeny znalosti |
| **Preceňovanie skorého úspechu** — LinkedIn: mesiac na 80 %, **ďalšie štyri na 95 %** | **spadli sme** — dva prejdené scenáre sme brali ako potvrdenie |
| **Opustenie ľudského hodnotenia** — kvalita sudcu závisí od jeho modelu, promptu a prípadu | riziko: chystáme sa automatizovať hodnotenie |
| **Zbieranie prípadov použitia bez stratégie** — vznikne *„milión Slack botov"* s mizernou návratnosťou | **priamo použiteľné u zákazníka** |
| Použitie AI tam, kde stačí jednoduchšie riešenie | kvalifikačná otázka |
| Zlý produkt ≠ zlá AI — ťažká časť je UX | zatiaľ neriešime |

**To s tým „miliónom Slack botov" je hotová odpoveď na otázku, ktorý proces
u zákazníka vybrať.** Zamestnanec si vyberie to, čo pomôže jemu; firma
potrebuje to, čo má návratnosť. Preto výber procesu **nesmie byť anketa**.

### 2.2 Ľudské hodnotenie sa nesmie vypnúť

Huyen odporúča **denne ručne prejsť 30–1000 príkladov** — a to z troch dôvodov:
skorelovať ľudské hodnotenie so strojovým, pochopiť skutočné správanie
používateľov a zachytiť posun, ktorý automat prehliadne.

**Pre nás:** keď zavedieme strojové hodnotenie scenárov, **musí bežať vzorka
ručne** a musí sa sledovať zhoda. Inak meriame zhodu dvoch modelov.

### 2.3 Viac sád, nie jedna — a nám jedna chýba

Odporúča kurátorovať **viac evaluačných sád**: jednu, ktorá zodpovedá
**skutočnému rozloženiu prevádzky**, a ďalšie, ktoré režú podľa známych režimov
zlyhania.

**Máme len tie druhé.** Pätnásť scenárov sú samé hraničné prípady. Chýba nám
sada, ktorá vyzerá ako **bežný utorok** — obyčajné reklamácie v takom pomere,
v akom naozaj chodia. Bez nej nevieme, či nástroj nie je prehnane opatrný na
tom, čo je každodenné.

---

## 3. Karpathy — overiteľnosť ako kvalifikačné sito

Ak LLM automatizujú to, čo sa dá overiť, potom sa to dá otočiť na **predajnú
kvalifikáciu**, ktorá je ostrejšia než naša doterajšia „je know-how zapísané?":

> **Vieme pred začiatkom povedať, čo by dokázalo, že odpoveď je nesprávna?**

- **Áno** → rozhodnutie je overiteľné, pack má zmysel.
- **Nie** → nepredávať. Nie preto, že to nezvládneme, ale preto, že sa to
  nedá odovzdať ani obhájiť.

Diagnostika vady prejde (existuje skutočná príčina, ktorá sa raz ukáže).
„Napíš peknú odpoveď zákazníkovi" neprejde — nič to nevyvráti.

---

## 4. Raschka — mechanizmus, ktorý nám chýbal: mazanie pravidiel

Dve použiteľné veci:

**a) *„Implementácia neklame."*** Jeho postup: implementuj a porovnávaj
medzivýsledky s referenciou, kým nesedia; nezhoda odhalí to, čo článok zamlčal.
Naša obdoba je porovnanie s **uzavretým prípadom, kde skutočnú príčinu už
poznáme** — tam sa nedá diskutovať.

**b) Podpory sa zmenšujú, ako modely silnejú.** Čo dnes píšeme ako pravidlo,
aby model neurobil chybu, môže o pol roka byť mŕtva váha, ktorá už len zaberá
miesto a mätie.

**Z toho plynie mechanizmus, ktorý nám celý čas chýbal — ablácia:**

> Vypni jedno pravidlo, pusti sadu znovu. Ak sa nič nezhorší, **pravidlo sa
> zmaže.**

Doteraz mal pack len jeden smer: pribúdať. Toto je prvý spôsob, ako z neho
niečo **odstrániť na základe dôkazu**, nie dojmu. Rieši to presne tú
akumuláciu pravidiel, ktorá viedla k piatim verziám bez zmeny znalosti.

**Poznámka na okraj, ktorú si treba pamätať:** Raschka upozorňuje, že novou
záťažou je *dohliadať na agentov, ktorí dohliadajú sami na seba*. To je presne
to, čo sa mi stalo — brána a sada si začali riadiť prácu samy.

---

## 5. Prax Claude Code — priamo na efektivitu našej práce

Toto je časť, ktorá zmení, ako pracujeme spolu, nie čo predávame.

| Praktika | Stav u nás |
|---|---|
| **Daj agentovi kontrolu, ktorú vie spustiť** — inak si overovacia slučka ty | **máme** — brána + Stop hook |
| **Adverzárna kontrola v čerstvom kontexte** — recenzent vidí len diff a kritériá, nie úvahu, ktorá k tomu viedla | **nemáme** — a je to tá istá chyba, ktorú našiel Kopadze |
| **Fan out cez `claude -p` v cykle** | **nemáme** — presne toto spraví 75 behov sady uskutočniteľnými |
| **Nechaj sa vypočúvať a napíš SPEC, potom čerstvá relácia na vykonanie** | **nemáme** — a je to liek na *shaping the build* |
| **Prieskum → plán → implementácia** | čiastočne |
| **`/clear` medzi nesúvisiacimi úlohami; po dvoch neúspešných opravách vyčistiť a prepísať zadanie** | nedodržiavam |
| **CLAUDE.md prísne krátiť** — pri každom riadku sa pýtaj, či by jeho odstránenie spôsobilo chybu | **naše `memory/` narástlo** — treba prerezať |
| Skills namiesto CLAUDE.md pre to, čo je relevantné len občas | **máme** |

Za zapamätanie stoja dve varovania odtiaľ:

- **Medzera medzi dôverou a overením:** vierohodne vyzerajúca implementácia,
  ktorá nezvláda hraničné prípady. *Ak to nevieš overiť, neposielaj to ďalej.*
- **Recenzent, ktorý má nájsť medzery, ich nájde vždy** — aj keď je práca
  v poriadku. Preto sa mu musí povedať, že hlási len to, čo ovplyvňuje
  správnosť. Inak vyrobí prezbytočnenie. *(Toto je mimochodom presne to, čo som
  robil štyri dni.)*

---

## 6. Čo z toho meníme — konkrétne

**V produkte a predaji:**

1. **Preformulovať koncept na overiteľnosť.** Nie „AI nepozná vaše pravidlá",
   ale *„vašu prácu nemáte v overiteľnej podobe, preto ju AI nesmiete zveriť"*.
2. **Kvalifikačné sito Karpathyho testom** — vieme povedať, čo by odpoveď
   vyvrátilo? Ak nie, nepredávame.
3. **Výber procesu nie je anketa.** Huyenova pasca s miliónom Slack botov ide
   do ponuky ako dôvod, prečo proces vyberáme spolu s vedením, nie zbierame
   želania.
4. **Očakávanie 80 → 95 povedať vopred.** LinkedIn: mesiac na 80 %, štyri
   ďalšie na 95 %. Kto to nevie, zruší pilot v druhom mesiaci.

**V metóde:**

5. **Ablácia pravidiel** — vypni, pusti sadu, ak sa nič nezhorší, zmaž.
6. **Druhá evaluačná sada podľa skutočného rozloženia**, nie len hraničné prípady.
7. **Hodnotí čerstvý kontext**, ktorý dostane len prepis a kritériá.
8. **Ručná vzorka zostáva vždy** a sleduje sa zhoda so strojovým hodnotením.

**V našej práci:**

9. **Fan out cez `claude -p`** na beh sady.
10. **SPEC pred stavaním** — nechať sa vypočúvať, spísať, potom čistá relácia.
11. **Prerezať `memory/`** podľa testu „spôsobilo by odstránenie chybu?".

---

## Zdroje

- [Chip Huyen — Common Pitfalls in Generative AI Applications](https://huyenchip.com/2025/01/16/ai-engineering-pitfalls.html)
- [Chip Huyen — AI Engineering (kniha)](https://www.amazon.com/AI-Engineering-Building-Applications-Foundation/dp/1098166302) · [EDD rámec, zhrnutie](https://medium.com/@keerthanams1208/chip-huyen-s-evaluation-driven-development-edd-framework-from-ai-engineering-a2939cc9ecf8)
- [Claude Code — Best practices](https://code.claude.com/docs/en/best-practices)
- [Sebastian Raschka — LLM Architecture in 2026: Agent Harnesses](https://hugobowne.substack.com/p/llm-architecture-in-2026-agent-harnesses) · [blog](https://sebastianraschka.com/blog/)
- Karpathy — cez sekundárne zhrnutia: [Sequoia Ascent 2026](https://karpathy.bearblog.dev/sequoia-ascent-2026/) · [prehľad](https://www.lowtouch.ai/10-things-i-learned-andrej-karpathy-agentic-engineering/)
- Andrew Ng — *AI Engineering Skills Map* (`docs/EVAL_DISCIPLINA.md`)
- Anatoli Kopadze — *Graph Engineering* (`docs/GRAF_A_KOTVY.md`)
