# Koncept — prečo firmy nevyužijú AI ani na 5 % a čo s tým predávame

Napísané 2026-08-16. Nahrádza rámovanie „nástroj na reklamácie" — to bol
**príklad, na ktorom sa to postavilo**, nie predmet podnikania.

---

## 1. Situácia

Firmy AI **už majú**. Licencie sú kúpené, Copilot je v Microsofte, ChatGPT má
každý druhý v prehliadači. Používa sa na: preformulovať e-mail, zhrnúť dokument,
preložiť text, napísať zápis z porady.

To je práca, ktorá firmu **nestojí peniaze**. Peniaze stoja rozhodnutia — a tie
sa AI nezverujú.

## 2. Prečo sa to zastaví práve tam — tri dôvody, nie jeden

**Prvý: AI nepozná pravidlá tejto firmy.** Pozná svetový priemer. Preto pomôže
s e-mailom (ten je všade rovnaký) a nepomôže s rozhodnutím, ktoré závisí od
toho, ako to robíme **my** — od našich tolerancií, predpisov, zákazníkov,
histórie. Firma to skúsi, dostane všeobecnú odpoveď a usúdi, že „na odbornú
prácu sa to nedá".

**Druhý: AI nemá postup.** Chat odpovie na to, na čo sa spýtaš. Odborná práca je
ale **poradie** — čo overiť najskôr, čo je lacné, čo rozhodne. Bez poradia
dostaneš vierohodnú odpoveď v zlom slede a človek ide robiť drahú skúšku skôr,
než sa pozrel do záznamu, ktorý má na stole.

**Tretí, a ten je rozhodujúci: nikto nevie overiť, či je odpoveď správna.**
Preto sa AI nepustí k ničomu, čo má následok. Toto je skutočný strop. Nie
schopnosti modelu — **dôvera**. A dôvera nevzniká tým, že model je lepší; vzniká
tým, že sa dá skontrolovať.

## 3. Čo predávame

**Vrstvu, ktorá tie tri veci odstráni — do AI, ktorú firma už má.**

Žiadny nový systém, žiadna migrácia, žiadna naša platforma s mesačným
poplatkom navyše.

| Diera | Čo dodáme |
|---|---|
| AI nepozná ich pravidlá | **znalosť firmy**, vytiahnutá z ich vlastných materiálov a zoštruktúrovaná tak, aby sa dala vykonávať, nie len čítať |
| AI nemá postup | **procedúru** — poradie otázok podľa ceny overenia, so zákazom uzavrieť záver bez rozlišujúceho pozorovania |
| Nikto neovería odpoveď | **bránu** (kontroluje konzistenciu znalosti pri každej zmene) a **akceptačnú sadu** (kontroluje správanie na pevných scenároch) |

**Tretí riadok je to, čím sa líšime.** Znalosť do AI dostane hocikto — nahrá
dokumenty. Postup napíše tiež. Ale nikto nedodáva **dôkaz, že to funguje a že to
po zmene stále funguje.** Bez neho je to ďalší chatbot, ktorému firma nezverí
nič dôležité — čiže presne tých 5 %.

## 3b. Nezávislé potvrdenie tejto tézy

Andrew Ng, *AI Engineering Skills Map* (14. 8. 2026), syntéza z vyše 10 000
pracovných inzerátov a rozhovorov: rozdiel medzi AI a bežným softvérom je
**nepredvídateľný výstup**, preto je jadrom remesla vedieť správanie **merať,
usmerňovať a riadiť** — cez disciplinované evaly a analýzu chýb.

**Je to tá istá vec z druhej strany.** My hovoríme firme: *AI nepustíte
k ničomu s následkom, lebo nikto neoverí odpoveď.* Trh práce hovorí: *kto to
vie merať, je vzácny.* Firma, ktorá tú zručnosť nemá interne, si ju buď najme,
alebo zostane pri mailoch.

Podrobne, aj s tým, čo nám ešte chýba: `docs/EVAL_DISCIPLINA.md`.

## 4. Prečo to nie je „AI asistent na mieru"

Asistent na mieru je konfigurácia. Toto je **výrobná linka**:

- zdroj pravdy je **jeden súbor u zákazníka** (tabuľka, ktorú vlastní jeho odborník)
- z neho sa **stavia** artefakt, nikdy sa needituje ručne
- pri každej zmene beží **brána**; čo neprejde, nevydá sa
- pred vydaním beží **akceptačná sada**; blokujúce scenáre musia prejsť
- zmena znalosti = zmena riadku v tabuľke, nie prepisovanie promptu

To znamená, že to **vydrží po odovzdaní**. Konfigurácia sa rozpadne pri prvej
zmene, ktorú urobí niekto iný. Toto sa nerozpadne ticho — brána spadne.

## 5. Čo je dnes dokázané a čo nie

**Dokázané, existuje a beží:**

- pack pre jednu profesiu, postavený z tabuľky odborníka (36 kategórií, 125 príčin)
- brána, ktorá **zachytila tri skutočné chyby**, vrátane chyby v návrhu
- akceptačná sada, kde **päť blokujúcich scenárov prešlo v reálnom Copilote**
- pri troch reálnych prípadoch to dalo výsledok — v jednom sa zastavila úprava
  nástroja, ktorá bežala na nepotvrdenej príčine

**Nedokázané, a netvárime sa inak:**

- **že sa štruktúra prenesie na inú profesiu.** Máme jeden pack v jednej doméne.
  Kým nie je druhý v úplne inej, je to jeden dokument, nie výrobná linka.
- **koľko času to ušetrí.** Nemeriame to a číslo si nevymyslíme.
- **že to niekto mimo nás chce kúpiť.** Nikto zvonku to zatiaľ nepovedal.

## 6. Najbližší krok, ktorý to posunie

**Druhý pack v úplne inej profesii** — aby tvrdenie z bodu 4 („výrobná linka",
nie „jeden dokument") prestalo byť tvrdením. Nepotrebuje zákazníka ani súhlas
a je to jediný chýbajúci dôkaz, ktorý vieme dodať sami.

**Nie ďalšie pravidlo do existujúceho packu.** Katalóg sa naposledy zmenil
12. 8.; päť verzií po ňom menilo pravidlá o pravidlách. To je uzavreté.
