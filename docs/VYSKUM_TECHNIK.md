# Výskum: techniky, ktoré vieme použiť na náš postup a na produkt

> Zadanie majiteľa 2026-08-22: „sústreď sa na deep research AI pokročilých
> techník ako zdokonaliť náš workflow a produkty."
>
> Pravidlo pre celý tento dokument: **technika sa sem zapíše len vtedy, ak sa
> dá povedať dopredu, čo by ukázalo, že nefunguje.** Inak je to inšpirácia,
> nie nález.

---

## 1. Zhoda hodnotiteľov nie je dôkaz správnosti

**Zdroj:** *Reliability without Validity: A Systematic, Large-Scale Evaluation
of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias* (arXiv
2606.19544). Meria zhodu, stabilitu a skreslenie u modelov v úlohe hodnotiteľa.

**Nález:** u dvoch nasadených hodnotiteľov namerali **stabilitu pri opakovaní
nad 0,95 a súčasne polohové skreslenie nad 0,10**. Model teda odpovedá
zakaždým rovnako a zároveň sa rozhoduje podľa toho, ktorá odpoveď je prvá.
V párovom porovnaní vyhráva pozícia A o 10 až 15 bodov častejšie. Menované
skreslenia sú polohové, dĺžkové, sebapreferenčné, formátové a driftové.

**Čo to znamená pre nás — priamo dnes.** Pred hodinou som dal S8, S9 a S17
dvom nezávislým hodnotiteľom a obaja napísali NEVYHOVEL na všetkých troch.
Chcel som to čítať ako potvrdenie. Podľa tejto práce to potvrdenie **nie je**:
dva modely, ktoré sa zhodnú, môžu byť zhodne skreslené, a zhoda meria
konzistenciu, nie správnosť.

Nie je to však bezcenné a treba rozlíšiť, ktorá časť verdiktu čím je:

| tvrdenie v hodnotení | čo to je |
|---|---|
| „reťazec `OBÍDI` sa v odpovedi nevyskytuje" | **overiteľný fakt** — platí bez ohľadu na hodnotiteľa |
| „v prepise nie je slovo napätie" | **overiteľný fakt** |
| „ďalší rozlišovač nie je najlacnejší" | **úsudok** — dvaja modeli sa zhodli, čo nič nedokazuje |
| „toto celé je NEVYHOVEL" | **úsudok o dôsledku faktov** |

Naše tri NEVYHOVEL stoja na chýbajúcich reťazcoch, teda na overiteľnej časti.
Tá obstojí. Zdôvodnenia okolo nich sú úsudok dvoch modelov a treba ich tak
čítať. Toto je presne pravidlo č. 4 z CLAUDE.md — *väčšina našej sady dokazuje
stabilitu, nie správnosť* — potvrdené zvonku, nezávisle od nás.

**Čo prijímame:** v každom hodnotení oddeliť tabuľku overiteľných faktov od
úsudku a nikdy nepísať, že zhoda hodnotiteľov niečo dokazuje.

**Čo by to vyvrátilo:** ak by sa ukázalo, že naši dvaja hodnotitelia dávajú
rôzne verdikty pri prehodení poradia kritérií a prepisu, potom aj tá
faktová časť podlieha polohovému skresleniu a treba ju merať kódom, nie
modelom.

---

## 2. Expertov písaný súbor je ten najhorší zdroj jeho uvažovania

**Zdroj:** *BC Protocol: Structured Dual-Expert Dialogue for Eliciting
High-Quality Chain-of-Thought Post-Training Data* (arXiv 2605.25549).

**Nález — a je nepríjemný.** Porovnali 20 vzoriek získaných rozhovorom
s 20 vzorkami, ktoré **ten istý expert napísal sám**, naslepo hodnotené
v piatich rozmeroch:

| rozmer | rozhovor | expert píše sám |
|---|---|---|
| prirodzenosť uvažovania (vidno pokus a omyl) | **4,80** | 1,30 |
| úplnosť reťazca | 2,91 | 2,63 |
| hustota kontrafaktov | 1,50 | 1,20 |
| informačná hustota | 3,02 | **4,07** |

Rozdiel v prirodzenosti je p = 2,4 × 10⁻⁸ pri Cliffovom δ = 1,0 — to znamená,
že **každá** vzorka z rozhovoru prekonala **každú** písanú. Príčinu nazývajú
*slepé miesto experta*: skúsený človek si medzikroky automaticky stlačí do
hotového záveru. Keď píše, píše výsledok. Uvažovanie zahodí, lebo je preňho
samozrejmé.

Opačným smerom vyhráva písanie: informačná hustota je vyššia (p = 1,1 × 10⁻⁴).
Písaný súbor je hutnejší, ale je to hutný **záver**.

**Čo to znamená pre nás.** Pravidlo č. 2 v CLAUDE.md znie: *nikdy neautorizuj
doménový obsah, odvoď ho z expertovho vlastného súboru.* Prvá polovica je
správna a nemení sa. Druhá polovica ale hovorí, že máme čerpať presne z toho
zdroja, o ktorom táto práca meria, že v ňom to, čo predávame — **rozhodovací
postup** — systematicky chýba. Predávame uvažovanie a berieme ho zo záverov.

To nie je dôvod prestať používať expertov súbor. Je to dôvod prestať sa naň
spoliehať ako na jediný zdroj: podľa nameraného rozdelenia rolí má písaný
súbor dodať **hustotu a katalóg**, rozhovor **rozhodovací postup**.

**Technika, ktorú z toho beriem — kontrafaktové sondovanie.** Nie je to
doplňujúca otázka. Je to otázka, ktorá **poruší premisu, ktorú expert
mlčky predpokladal**, a donúti ho prejsť uvažovanie znova za podmienky,
ktorá neplatí: *„a keby tá dodávka nebola od toho istého dodávateľa?"*
Práca ju označuje za najsilnejší nástroj a uvádza aj dôvod, prečo ju robiť
počas rozhovoru a nie potom: dodatočné dopisovanie kontrafaktov stojí
4–5 minút na kus.

**Čo by to vyvrátilo:** ak by pack postavený z prepisu rozhovoru dopadol na
tej istej sade rovnako alebo horšie než pack z písaného súboru. To sa dá
zmerať — ale až keď rozhovor existuje, a to je jediná vec, ktorú za majiteľa
spraviť neviem.

---

## 3. Nosné sú výstupné kontrakty, nie doménové pravidlá

**Zdroj:** ablačné testovanie nástrojových agentov, zhrnuté v *Context
Engineering: Agent Reliability Playbook 2026*; k tomu *RubricRefine*
(arXiv 2605.09730).

**Nález:** keď sa z inštrukcií agenta postupne odoberali pravidlá a merala sa
úspešnosť, **pravidlá výstupného kontraktu boli zakaždým nosné** — ich
odobratie zhoršilo výsledok u všetkých testovaných modelov. Väčšina ostatných
pravidiel nosná nebola.

**Prečo je to pre nás dôležitejšie než to znie.** Pozri, na čom padli všetky
tri dnešné scenáre:

- S8: chýba `OBÍDI` a chýba veta, čo začať zapisovať
- S17: je `POKRAČUJ` tam, kde má byť `ZASTAV`, a chýba návrh rozhodujúcej skúšky
- S9: chýba pomenovanie kandidáta

Ani jedno z toho nie je doménová chyba. Model nepovedal o extrúzii nič
nesprávne. **Vo všetkých troch prípadoch nedodržal výstupný kontrakt.**
A výstupný kontrakt je presne to, čo je podľa ablácií nosné a čo sa dá
kontrolovať kódom, nie ďalším modelom.

**Čo z toho plynie a čo z toho NEplynie.** Neplynie z toho, že máme dopísať
pravidlá do packu — to by porušilo pravidlo č. 1, verifikátor nesmie
rozhodovať, čo sa postaví. Plynie z toho niečo lacnejšie: **stav kroku sa dá
overiť reťazcom**. Ak odpoveď neobsahuje jeden z `POKRAČUJ / OBÍDI / ZASTAV`,
vie to povedať kód okamžite a bez hodnotiteľa — a podľa bodu 1 je práve
reťazcová kontrola tá časť, ktorá je overiteľná, nie úsudková.

---

## 4. Naše vlastné inštrukcie rastú 14 : 1

**Zdroj:** Boris Cherny (autor Claude Code) odporúča **zmazať systémový prompt
každých šesť mesiacov** a ablačne overiť, ktoré pravidlá treba vrátiť.
Ten istý playbook pomenúva bežnú chorobu: každý incident pridá pravidlo,
nikto žiadne neodstráni, a po osemnástich mesiacoch je z toho 6 000 tokenov
protirečení.

**Merané na nás (git história `CLAUDE.md`):**

| dátum | znakov |
|---|---|
| 2026-07-31 | 3 948 |
| 2026-08-16 | 10 438 |
| 2026-08-19 | 13 397 |
| 2026-08-22 | 14 132 |

**3,6-násobok za 22 dní.** Pridaných 250 riadkov, ubraných 18 — pomer
**13,9 : 1**. CLAUDE.md pritom sám prikazuje abláciu („mazať je dovolené
a povinné"), takže toto nie je chýbajúce pravidlo. Je to pravidlo, ktoré sa
neuplatňuje na súbor, v ktorom je napísané.

**Čo prijímame:** abláciu na inštrukciách, nie len na packu. Vypnúť pravidlo,
prejsť sadu, a ak sa nič nezhorší, zmazať ho.

**Čo by to vyvrátilo:** ak by sa po odobratí ktoréhokoľvek pravidla vrátila
chyba, ktorú to pravidlo popisuje. Presne preto sa ablácia musí merať, nie
odhadovať — a preto sa nedá spraviť „upratovaním".

---

---

## 5. Rovnaký výsledok pre všetky verzie nie je „bez zlepšenia", je bez informácie

**Zdroj:** *VeriGate: Verifier-Gated Step-Level Supervision* (arXiv 2605.30451)
a širší prúd procesných odmien.

**Nález:** keď všetky vzorky dostanú od verifikátora **tú istú** odmenu,
relatívny rozdiel medzi nimi je nula, gradient nenesie žiadnu informáciu
a učenie zastane. Volajú to degenerovaná odmena. Riešenie nie je lepší
verifikátor, ale **prepnutie na krokové hodnotenie** — hodnotiť medzikroky,
nie len výsledok, lebo krokové hodnotenie dáva signál aj tam, kde výsledok
je u všetkých rovnaký.

**Presne to sa nám stalo dnes.** Tri scenáre, tri NEVYHOVEL. Chcel som to
čítať ako „pack sa nezlepšil". Nie je to tak: sada dala všetkému to isté,
takže o rozdiele medzi verziami nepovedala **nič**. To je iný stav než
zlyhanie a robí sa s ním niečo iné.

Horšie: **nevedeli sme to ani zistiť.** Per scenár máme prepis z jediného dňa
a porovnanie so 17. 8. existuje len ako veta, ktorú napísal ten, kto beh
spravil. Vektor kritérií sa nikde neukladal.

**Postavené dnes:** `quality-packs/tests/rozlisuje.py` ukladá deterministický
vektor kritérií ku každému behu a povie, či sa medzi verziami zmenil a ktoré
kritériá sa preklopili. Overené na držaných dátach — umelá verzia s jedným
preklopeným kritériom bola zachytená menovite.

**Čo NErobí a prečo:** nepočíta skóre. Číslo, ktoré sa dá zvyšovať, by sa
začalo zvyšovať, a pravidlo č. 1 hovorí, že verifikátor nesmie rozhodovať,
čo sa postaví. Práve na tomto raz odišlo päť verzií packu bez toho, aby sa
znalosť zmenila. Preto hlási len ROZLÍŠILA / NEROZLÍŠILA a mená kritérií.

---

## 6. Ablácia sa robí v pároch, a má tri výsledky, nie dva

**Zdroj:** *ACON: Optimizing Context Compression for Long-horizon LLM Agents*
(arXiv 2510.00615, ICML 2026).

**Nález:** ACON púšťa tú istú úlohu **dvakrát** — raz s plným kontextom, raz
so skráteným. Zaujímavé sú len dvojice, kde **plný uspel a skrátený zlyhal**.
Model potom rozoberie, čo v skrátenej verzii chýbalo, a pravidlo sa podľa
toho **prepíše**. Celé bez trénovania, použiteľné aj na uzavreté modely.
Výsledok: 26–54 % menej tokenov pri zachovanom výkone.

**Čo to mení u nás.** CLAUDE.md predpisuje abláciu takto: vypni pravidlo,
prejdi sadu, a ak sa nič nezhorší, zmaž ho. To sú dva výsledky — nechať
alebo zmazať. ACON pridáva tretí, ktorý je v praxi najčastejší:

| výsledok páru | čo to znamená | čo s tým |
|---|---|---|
| bez pravidla to prejde rovnako | pravidlo nie je nosné | **zmazať** |
| bez pravidla to zlyhá presne na tom, čo pravidlo popisuje | nosné | **nechať** |
| bez pravidla to zlyhá **inak** | pravidlo mierilo vedľa | **prepísať** podľa toho zlyhania |

Tretí riadok je ten, ktorý nám chýbal. `Z8` a `Z9` v taxonómii vznikli presne
takto — obe zlyhania boli dovtedy natlačené do najbližšieho existujúceho kódu
a oprava preto mierila vedľa.

**Podmienka, bez ktorej to nefunguje:** ablácia potrebuje sadu, ktorá vôbec
**rozlišuje** (bod 5). Na degenerovanej sade vyjde každé pravidlo ako nenosné
a zmazalo by sa všetko.

*Poznámka k tomu istému prúdu, ktorá ide proti očakávaniu:* pri dnešnom
prompt cachingu je držať celú históriu často lacnejšie aj presnejšie než ju
sumarizovať. Skracovanie kontextu má byť odpoveďou na pomenované obmedzenie,
nie predvolené správanie. Nás sa to týka pri denníku a pri `memory/` —
neskracovať preventívne.

## Poradie, v akom to má cenu robiť

1. ~~Reťazcová kontrola stavu kroku~~ — **hotové 22. 8.** Ukázalo sa, že
   skript existoval od 19. 8., len sa nepúšťal do podkladu. Teraz je v ňom
   doslovný výstup a taxonómia, takže sa dali prideliť kódy Z9/Z8/Z8.
2. ~~Oddelenie faktov od úsudku~~ — **hotové 22. 8.**, tým istým krokom.
3. ~~Zistiť, či sada vôbec rozlišuje~~ — **postavené 22. 8.**
   (`tests/rozlisuje.py`). Odpoveď zatiaľ znie „z jednej verzie sa to povedať
   nedá" a to je poctivá odpoveď, nie zlyhanie nástroja.
4. ~~Oprava sady, aby S9 bol splniteľný~~ — **odpadá.** Overené proti
   `akceptacne_scenare.md`: S9 splniteľný **je**, každá časť očakávaného
   záveru sa dá dosiahnuť z jedného vstupu. Tvrdenie o nemerateľnosti
   napísal ten, kto beh spravil, prešlo cez dvoch hodnotiteľov (obaja
   s výhradou, že to overiť nevedia — podklad definíciu scenára neobsahuje)
   a prevzal som ho aj ja. Blokátor bol vymyslený, nie nájdený.
5. ~~Párová ablácia~~ — **mechanizmus postavený a prvý pokus spravený
   22. 8.** `build_pack.py --bez <sekcia>` + `tests/rozlisuje.py`. Prvý
   výsledok: sada NEROZLÍŠILA pack so sekciou od packu bez nej, hoci
   odpovede sa viditeľne líšili. Dve poučenia v
   `quality-packs/tests/vysledky/ABLACIA_2026-08-22.md`: (a) „vektor sa
   nezmenil" znamená, že sada ten rozmer nemeria, nie že sa správanie
   nezmenilo; (b) ablovať pravidlo treba proti scenáru, ktorý ho cieli —
   ja som ho pustil na scenári, kde sa nemalo kde prejaviť.
6. **Scenár, ktorý cieli sekciu o skúsenom kvalitárovi** — bez neho sa
   tá sekcia ablovať nedá vôbec.
7. **Kontrafaktový rozhovor s expertom** (bod 2) — najväčší dopad na produkt
   a jediné, čo bez majiteľa spraviť neviem.

## Zdroje

- https://arxiv.org/pdf/2606.19544 — Reliability without Validity
- https://arxiv.org/html/2605.25549v1 — BC Protocol
- https://arxiv.org/pdf/2605.09730 — RubricRefine
- https://www.digitalapplied.com/blog/context-engineering-agent-reliability-playbook-2026
- https://finance.biggo.com/news/954a98de-8b79-429f-bd7e-761c27a3b210 — odporúčanie mazať systémový prompt
- https://arxiv.org/abs/2605.30451 — VeriGate, degenerovaná odmena
- https://arxiv.org/abs/2510.00615 — ACON, párová optimalizácia pravidiel
