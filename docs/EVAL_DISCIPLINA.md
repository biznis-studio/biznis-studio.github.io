# Čo z AI Engineering Skills Map platí pre nás — a kde nám to ukazuje dieru

2026-08-16. Zdroj: Andrew Ng, *The AI Engineering Skills Map*, 14. 8. 2026
(x.com/AndrewYNg). Syntéza z vyše 10 000 pracovných inzerátov a rozhovorov
s odborníkmi a náborármi. Štyri zručnosti: stavanie a nasadzovanie AI aplikácií ·
softvérové základy · práca s coding agentmi · **shaping the build** (rozhodovanie,
čo vôbec má byť v zadaní).

---

## 1. Čo to potvrdzuje

Ng hovorí, že rozdiel medzi AI a bežným softvérom je **nepredvídateľný výstup**,
a preto je jadrom remesla vedieť správanie systému **merať, usmerňovať a riadiť** —
cez *„disciplined evals and error analysis loops"*.

To je z druhej strany presne naša predajná téza. My hovoríme zákazníkovi:
*firmy nepustia AI k ničomu s následkom, lebo nikto nevie overiť odpoveď.*
Ng hovorí tú istú vec smerom k inžinierom: kto to vie merať, je vzácny.

**Dôsledok pre pozíciu: nepredávame packy. Predávame tú disciplínu**, dodanú do
firmy, ktorá ju nemá a nemá kde ju vziať. Pack je len forma, v akej sa dodáva.

Druhá vec, ktorú to potvrdzuje: Ng píše, že agentovi treba pomôcť **uzatvárať
slučku sám tým, že mu dodáš verifikátor alebo eval**. To je presne naša brána —
`build_pack.py --check`, ktorá beží v CI a bez ktorej by sa pack nevydal.
Máme to a je to správny inštinkt, nie réžia navyše.

---

## 2. Kde máme skutočnú dieru

**Naša akceptačná sada nie je eval. Je to zoznam.**

| | Čo máme | Čo Ng popisuje ako remeslo |
|---|---|---|
| Beh | **raz**, ručne, v chate | opakovane, automaticky |
| Výsledok | vyhovel / nevyhovel | **miera úspešnosti** — pri nedeterministickom výstupe je jeden beh anekdota |
| Zlyhanie | veta v tabuľke | **error analysis** — kategorizované typy chýb, ktoré určujú, čo opraviť |
| Vývoj v čase | žiadny | trend medzi verziami, viditeľná regresia |

**Prečo to bolí konkrétne:** S1 a S2 „vyhoveli" na verzii 0.2.1. Každý bol
spustený **raz**. Pri modeli s nedeterministickým výstupom to znamená len to, že
**aspoň raz to vyšlo** — nie že to vychádza. To je slabší výrok, než sme ho
zapisovali.

A ešte konkrétnejšie: chybu so zlúčenými štítkami (`NEOVERENÁ` namiesto
`MIMO KATALÓGU`) sme našli **náhodou pri jednom behu**. Pri error analysis by
vypadla ako kategória, nie ako náhoda.

---

## 3. Čo s tým — tri veci, žiadna z nich nie je ďalšie pravidlo do packu

**A · Každý scenár beží viackrát a vykazuje sa miera, nie fajka.**
Pri 5 behoch je rozdiel medzi 5/5 a 3/5 rozdiel medzi „drží" a „občas".
Blokujúce scenáre musia byť 5/5, nie „prešlo".

**B · Taxonómia chýb namiesto voľného textu.** Zlyhanie sa zaradí, nie opíše.
Prvá verzia priamo z toho, čo sa už reálne stalo:

| Kód | Typ zlyhania | Videné |
|---|---|---|
| `Z1` | uzavrel príčinu bez rozlišujúceho pozorovania | 2026-08-10, prenos vzoru |
| `Z2` | príčina mimo katalógu neoznačená ako taká | 2026-08-15, S7 |
| `Z3` | „neviem" spracované ako „nie" | riziko, zatiaľ nenastalo |
| `Z4` | preskočený krok bez uvedenia dôvodu | riziko |
| `Z5` | navrhol opatrenie pred potvrdením príčiny | riziko |
| `Z6` | vymyslený zdroj, citácia alebo číslo | riziko |
| `Z7` | **obchodný záver namiesto diagnostického** | reálny prípad 8/2026 · znovu 2026-08-16, S17 |

Kategória, ktorá sa opakuje, je zadanie na opravu. Kategória, ktorá sa nikdy
neobjaví, je pravidlo, ktoré si možno mohol odpustiť.

**C · Hodnotenie sa dá zautomatizovať, ale nie zavrieť oči.**
Prepis rozhovoru vie oznámkovať model proti napísaným kritériám. Umožní to
opakované behy. **Musí sa to ale vzorkovať ručne** — inak meriame zhodu dvoch
modelov, nie správnosť.

---

## 3b. Hodnotenie vracia SMEROVANIE, nie známku

Doplnené 2026-08-16 (Ichigo, *Graph Engineering*). Dve veci, ktoré menia tvar
výstupu z hodnotenia:

**a) Najprv deterministická kontrola, až potom model.** *Nepoužívaj model na to,
čo vie obyčajný kód.* Či odpoveď obsahuje povinný štítok, či menuje príčinu
mimo katalógu, či navrhla opatrenie — to je hľadanie reťazca, nie úsudok.
Model nech rieši len to, čo sa kódom overiť nedá. *(Presne to som 15. 8. robil
ručne regulárnymi výrazmi — patrí to do skriptu.)*

**b) Verifikátor nevracia „vyhovel", vracia rozhodnutie, čo ďalej.** Namiesto
*„vyzerá to dobre"*:

```json
{ "pass": false,
  "kod": "Z2",
  "co": "štyri príčiny mimo katalógu bez označenia",
  "dalej": "doplniť rozlíšenie štítkov do packu" }
```

Kód je z taxonómie `Z1`–`Z6` vyššie. **Tým sa zo zoznamu zlyhaní stane zoznam
úloh** — a opakujúci sa kód je zadanie na opravu, nie pocit.

## 3c. Čo v našej procedúre chýba — päť koncov, nie dva

Článok žiada, aby mal každý krok **päť možných koncov**, nie dva:

| Koniec | Máme? |
|---|---|
| **Pass** — výstup spĺňa, čo má | áno |
| **Retry** — ten istý krok to vie napraviť | áno |
| **Reroute** — inam, iný rozlišovač | áno (`NEOVERENÁ` + ďalšia otázka) |
| **Escalate** — musí rozhodnúť človek | **NIE** |
| **Stop** — pokračovať by stálo viac, než to prinesie | **NIE** |

**To sú dve skutočné diery v diagnostike, nie v evaluácii.** Dnes procedúra
nikdy nepovie *„na toto už moje otázky nestačia, treba metalografiu"* ani
*„toto rieš s technológom"*. Ide len dopredu, kým sa nevyčerpajú kroky.

Súvisí s tým aj rozpočet: technik má konečný čas a procedúra ho nesleduje.
Článok to hovorí stroho — **pravidlo zastavenia sa pridáva skôr než opakovanie.**

**Je to zmena packu, takže ju nerobím sám** — pack je zmrazený a rozhodnutie
je majiteľovo. Zapísané ako návrh, nie ako vykonaná zmena.

## 4. Čo to mení v ponuke

Toto je predajné, nie interné:

- *„Dostanete meranie, nie sľub. Sadu prípadov, ktorú schválite, a **mieru
  úspešnosti** — nie tvrdenie, že to funguje."*
- *„Keď o pol roka niekto zmení pravidlo, uvidíte, či sa správanie zhoršilo.
  To je jediný spôsob, ako AI vo firme prežije zmenu."*

Zároveň dáva odpoveď na námietku *„veď si to spravíme sami"*: spraviť sa to dá.
Podľa Ngovej analýzy trhu je ale zručnosť merať a riadiť AI to najvzácnejšie,
čo dnes zamestnávatelia hľadajú. Firma, ktorá to nemá interne, si to buď
najme, alebo zostane pri mailoch.

---

## 5. Štvrtá zručnosť je priama kritika toho, čo som robil

Ng ju volá **shaping the build** — keď agent vie doručiť podľa zadania, práca
inžiniera sa presúva k rozhodovaniu, **čo vôbec má byť v zadaní**.

Presne to som medzi 12. a 16. 8. nerobil. Mal som funkčný verifikátor a nechal
som ho, aby určoval prácu: brána → scenár → zrážka pravidiel → nové pravidlo →
nový scenár. Päť verzií, `source/` sa nezmenil ani raz. Verifikátor vie
zodpovedať otázku *„je to konzistentné?"*. Nikdy nezodpovie *„má to vôbec
existovať?"* — a keď na to čaká, začne vyrábať prácu sám.

**Zapísané ako pravidlo:** verifikátor smie povedať, že niečo je pokazené.
Nikdy nesmie určovať, čo sa bude stavať.
