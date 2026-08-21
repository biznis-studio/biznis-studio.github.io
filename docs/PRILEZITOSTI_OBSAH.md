# Príležitosti pre obsahový model — TOP 10 a ich kombinácie

> Zostavené 2026-08-21 na žiadosť majiteľa. Model: GitHub generuje a obnovuje
> obsah, návštevnosť sa speňaží reklamou. Prvý míľnik **10 000 relácií mesačne**
> (prah pre Ezoic, RPM 8–25 $ oproti 3–12 $ pri AdSense).
>
> **Prečo dlhý chvost a nie veľká téma:** Google o nás vie **0 externých
> odkazov**, takže hlavné slová sú nedosiahnuteľné. Dôkaz modelu:
> omnicalculator.com má 3,3 M návštev mesačne, 74,6 % z vyhľadávania, a stojí
> na **454 600 kľúčových slovách** — teda na počte úzkych stránok.

## Šesť filtrov, ktorými každá príležitosť musí prejsť

1. **Voľný strojový zdroj** — dá sa ťahať bez ručnej práce
2. **Licencia dovoľuje komerčné použitie** — web s reklamou je komerčný;
   napr. Open-Meteo je voľné len nekomerčne
3. **Globálne**, nie jedna krajina
4. **Mení sa** — inak to zabehnutý hráč so statickým obsahom pokryje lacnejšie
5. **Počet stránok** — koľko úzkych otázok z toho vznikne
6. **Kto tam už je** — overiť PRED stavaním, nie po ňom

## Prečo je filter 4 náš jediný trvalý náskok

Statické vzorce (prevody jednotiek, matematika, fyzika) sú obsadené a **nikdy
sa nemenia**, takže ich držiteľ nepotrebuje prevádzku. My prevádzku máme —
denný pipeline s bránami a overovaním. Náskok teda máme len tam, kde údaj
zastará. Kde nezastará, tam prehráme s tým, kto tam bol skôr.

## TOP 10

| # | Príležitosť | Zdroj | Mení sa | Stránok | Kto tam už je |
|---|---|---|---|---|---|
| 1 | **Čo zostane z platu** — daň, odvody, čistá mzda podľa krajiny a príjmu | oficiálne sadzby, PwC/KPMG súhrny | ročne | krajina × pásmo × stav = tisíce | čiastočne (národné kalkulačky, málo porovnaní) |
| 2 | **Cena práce pre zamestnávateľa** — čo firma zaplatí nad hrubú mzdu | tie isté sadzby | ročne | krajina × mzda | slabo pokryté |
| 3 | **Minimálna mzda a jej vývoj** podľa krajiny | Eurostat, ILO, národné | 1–2× ročne | krajina × rok | Wikipédia, Trading Economics |
| 4 | **Sadzby centrálnych bánk a inflácia** | ECB a Fed — **už ich ťaháme** | mesačne | krajina × ukazovateľ × rok | Trading Economics silné |
| 5 | **Termíny povinností pre firmy** naprieč jurisdikciami | úradné vestníky | priebežne | jurisdikcia × povinnosť | roztrúsené, nikto neagreguje |
| 6 | **Dovoz a clo** — HS kód × krajina | colné sadzobníky | priebežne | desaťtisíce | Avalara, Zonos, SimplyDuty |
| 7 | **Podmienky vstupu do krajiny** — víza, doklady, poplatky | konzulárne stránky | často | krajina × krajina = tisíce | iVisa, VisaHQ |
| 8 | **Pravidlá príručnej batožiny** podľa aerolínie | stránky dopravcov | občas | ~300 dopravcov × trieda | čiastočne |
| 9 | **Konce podpory softvéru a verzií** | endoflife.date je otvorený | priebežne | tisíce | endoflife.date silné |
| 10 | **Životný cyklus AI modelov a API** — konce, prelomové zmeny, limity | dokumentácia poskytovateľov | týždenne | stovky | **overené: nepokryté** |

**Overené meraním:** #10 (artificialanalysis pokrýva ceny a benchmarky, výslovne
nie deprecations, breaking changes ani limity; endoflife.date má z AI jediný
produkt), #9 (endoflife.date pokrýva jazyky, databázy, OS, frameworky, cloud).
Ostatné sú zatiaľ **predpoklad** a treba ich preveriť rovnakým spôsobom, akým
dnes padla e-faktúra a hodnotenie pracovných miest.

## Kombinácie — tu je skutočná hodnota

Jednotlivé údaje má často niekto iný. **Priesečník nemá takmer nikdy nikto**,
lebo si vyžaduje spojiť dva zdroje a udržiavať oba.

1. **#1 × #2 × mesto** → *„Z 3 000 € hrubého v Berlíne vám zostane X, firmu to
   stojí Y."* Jedna stránka na kombináciu krajina × mzda; tisíce stránok, jeden
   výpočet, vysoko platená finančná nika.
2. **#1 × #7** → *„Oplatí sa presťahovať za prácou do krajiny B?"* — spojí čistý
   príjem s tým, či tam vôbec smiete pracovať.
3. **#3 × #4** → *„Rástla minimálna mzda rýchlejšie než inflácia?"* Jedna
   stránka na krajinu a rok, odpoveď, ktorú si nikto neskladá ručne.
4. **#5 × odvetvie** → *„Čo na vás čaká v roku 2027, ak vyrábate nábytok."*
   Spojí termíny z rôznych predpisov do jedného kalendára pre jednu činnosť.
5. **#6 × #5** → *„Dovážate z Číny nábytok: clo, DPH a povinnosti k tomu."*
6. **#9 × #10** → jeden prehľad *„čo vám v roku 2027 prestane fungovať"* naprieč
   knižnicami aj modelmi.
7. **#8 × #7** → *„Letíte do krajiny X: batožina, doklady, poplatky."*

## Siedmy filter, ktorý vysvetľuje všetky dnešné popravy

Kombináciu **#1 × #2** som postavil na prvé miesto a pri prvom overení **padla**:
robí ju najmenej desať nástrojov (remotepeople 150 krajín, globalpayrollcalculator
190 krajín „always up-to-date", ecosire, eorquotes, netsalary.org, Native Teams,
Calculla, Popadex). Všetky sú zadarmo — lebo ich prevádzkujú firmy, ktoré
predávajú mzdové a EOR služby, a kalkulačka je ich návnada.

To je ten istý dôvod, prečo padla e-faktúra (fakturačné systémy) aj hodnotenie
pracovných miest (gradar, 3 000 €/rok s voľnou verziou). Odtiaľ siedmy filter,
najsilnejší zo všetkých:

> **Existuje vedľa tejto témy niekto, kto predáva službu, pre ktorú by bol tento
> obsah návnadou?** Ak áno, bude to zadarmo a lepšie, než to spravíme my — jeho
> to nemusí uživiť, nám by to muselo.

Preto prežilo #10: nikto nepredáva službu, pre ktorú by bola návnadou stránka
*„kedy vám prestane fungovať model"*. A preto sú podozrivé #1, #2, #6 a #7 —
za mzdami stoja EOR firmy, za clom colní makléri, za vízami vízové agentúry.

## Prepočítané poradie po siedmom filtri

1. **#5 Termíny povinností naprieč jurisdikciami** — poradcovia o tom píšu
   články, ale živý agregovaný kalendár nepredáva nikto ako návnadu
2. **#10 Životný cyklus AI modelov a API** — overene nepokryté, ale úzke publikum
3. **#3 × #4 Minimálna mzda verzus inflácia** — Trading Economics má dáta, ale
   nie odpoveď na otázku „rástla rýchlejšie?"
4. **#8 Príručná batožina** — aerolínie samy návnadu nepotrebujú

**Ďalší krok:** overiť #5 rovnakým spôsobom — hľadať, či existuje udržiavaný
viacjurisdikčný kalendár povinností. Ak existuje, padá aj to a ide sa nižšie.
