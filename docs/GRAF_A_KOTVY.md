# Graph engineering — čo z toho berieme, čo nie, a tri veci, ktoré porušujeme

2026-08-16. Zdroj: Anatoli Kopadze, *Graph Engineering explained*, 24. 7. 2026
(x.com/AnatoliKopadze). Doplnok k `EVAL_DISCIPLINA.md`.

Poznámka na úvod: článok otvára vetou, že väčšina ľudí využíva AI na 5–10 % —
**to je presne téza, na ktorej staviame produkt.** Nie je to teda náš originálny
postreh, je to rozšírený názor v odbore. Pre nás to je dobrá správa: nemusíme
trh presviedčať, že problém existuje.

---

## 1. Podstata v štyroch vetách

- **Uzol** je jedna ohraničená úloha s definovaným vstupom a výstupom. Výstup
  musí mať pevný tvar — voľný text vie prečítať len človek, nie ďalší uzol.
- **Hrana** je skutočná dátová závislosť. Existuje len vtedy, keď po nej niečo
  reálne tečie.
- **Test falošnej hrany:** potrebuje tento krok výsledok predchádzajúceho? Ak
  nie, hrana neexistuje a čakanie je vyhodený čas.
- **Diamant** (fan out → reduce → verify → synthesize) je vzor, ktorý pokrýva
  väčšinu prípadov.

## 2. Čo je z toho pre nás najdôležitejšie — kapitola o kotvách

Toto je najsilnejšia časť článku a mieri priamo na to, čo sme postavili.

Predstav si systém, kde každý uzol kontroluje iný uzol — a všetky čítajú
podklady z toho istého zdroja. Výsledok je **konzistentný a zároveň neoverený**.
Zlyhá rovnako ako jednoduchá slučka, len neskôr, drahšie a s množstvom zelených
fajok cestou dole.

**Topológia nekupuje pravdu.** Graf potrebuje *kotvy* — veci, ktoré sa nedajú
prehovoriť: testy, ktoré naozaj zbehli, peniaze, ktoré naozaj prišli.

**Preložené na nás:** pack napísal Claude, bránu napísal Claude, scenáre napísal
Claude a vyhodnocoval ich Claude. Ak sa toho nedotkne nič zvonku, je to presne
ten uzavretý kruh — všetko sedí a nič nie je overené.

### Naše skutočné kotvy

| Kotva | Prečo je kotva |
|---|---|
| **Uzavreté reklamácie so známou skutočnou príčinou** | výsledok existuje nezávisle od nás; K2/2334 sa dal porovnať s interným šetrením |
| **Zásah, ktorý sa reálne zastavil** | AMARI/2650 — úprava matrice, ktorá bežala na nepotvrdenej príčine |
| **Námietka odborníka z prevádzky** | 2026-08-10 zhodila hypotézu jednou vetou — to sa nedá „vyargumentovať" |
| **Prechod na originálny obal v CW35–36** | Salzgitter/2802: príroda odpovie sama, bez nás |

**Čo NIE je kotva:** scenár, ktorý som si vymyslel a sám oznámkoval. Tých je
v sade väčšina. Nie sú zbytočné — chytia regresiu — ale **nepreukazujú
správnosť**, len stálosť.

### Zmrazené pravidlá

Článok hovorí, že niektoré pravidlá musia byť mimo dosahu optimalizácie práve
preto, že by ich optimalizátor rád ohol, aby vyhral. U nás sú to tri a označujem
ich za zmrazené:

1. **Bez rozlišujúceho pozorovania sa príčina nepotvrdí.**
2. **Príčina mimo katalógu sa vždy označí.**
3. **Žiadne vymyslené zdroje, citácie ani čísla.**

Sú to presne tie, ktoré by sa oplatilo ohnúť, aby nástroj vyzeral
nápomocnejšie. Preto sa nemenia bez tvojho výslovného rozhodnutia.

---

## 3. Tri veci, ktoré dnes porušujeme

**a) Pracovník a kontrolór zdieľajú kontext.** Článok to hovorí tvrdo: dať
kontrolórovi ten istý chat znamená, že si len prikyvuje iným písmom. Pri behu
akceptačnej sady som **scenár spustil aj oznámkoval ja, v jednom kontexte.**
To nie je kontrola, to je sebahodnotenie.
→ **Oprava:** hodnotí samostatný beh s čistým kontextom, ktorý dostane
**iba prepis odpovede a kritériá** — nikdy nie moju úvahu o tom, ako to dopadlo.

**b) Sadu púšťame ako reťaz.** Pätnásť scenárov medzi sebou nemá jedinú hranu —
ani jeden nepotrebuje výsledok predchádzajúceho. Púšťal som ich jeden po druhom.
→ **Oprava:** fan out. Až to spraví reálnym Ngovo *„každý scenár viackrát"* —
15 scenárov × 5 behov = 75 behov, čo sériovo nikto nikdy nespustí.

**c) Tichý výpadok uzla.** Pri jednom behu S7 sa odpoveď načítala skrátená
a takmer som ju hodnotil neúplnú.
→ **Oprava:** počítať vrátené odpovede oproti očakávanému počtu a chýbajúce
označiť, nikdy nehodnotiť neúplnú sadu ako hotovú.

---

## 4. Kde by bol graf CHYBA

Článok má vlastný zoznam „kedy graf nepoužiť" a **stavanie packu spadá rovno doň**:
úloha je prieskumná, kroky na sebe naozaj závisia a chceš schvaľovať každý krok.

| Činnosť | Graf? |
|---|---|
| Stavanie packu so zákazníkom | **nie** — prieskumné, sekvenčné, so schvaľovaním |
| Beh akceptačnej sady | **áno** — čistý fan out, žiadne hrany |
| Hľadanie chýbajúcich rozlíšení naprieč katalógom | **áno** — diamant |
| Diagnostika jedného prípadu | **nie** — je to slučka a slučka je správna |

**Diagnostika je slučka, nie graf, a to je v poriadku.** Celý náš postup stojí
na tom, že otázky idú **po jednej a v poradí podľa ceny** — tam sú hrany
skutočné. Robiť z toho graf by bola móda, nie zlepšenie.

## 5. Náklad, na ktorý netreba zabudnúť

Článok uvádza verejný prípad prepisu runtime Bun: ~535 000 riadkov za ~11 dní,
asi 50 workflowov, až 64 agentov naraz — a **zhruba 165 000 dolárov na spotrebe**,
s človekom, ktorý to celé navrhoval a strážil.

Ponaučenie pre nás: graf kupuje **šírku, nie úsudok**, a vie ticho míňať. Púšťať
ho na úzku úlohu je drahšia cesta k horšiemu výsledku.

---

## 6. Čo z toho ide do produktu

Pre zákazníka to nie je „staviame vám grafy". Je to jedna veta, ktorá sa dá overiť:

> **Kontroluje to niekto iný než ten, kto to napísal — a meriame to na vašich
> uzavretých prípadoch, kde už poznáte skutočný výsledok.**

To je zároveň odpoveď na najvážnejšiu námietku, ktorú si zákazník ani nemusí
vedieť sformulovať: *ako viem, že to nie je systém, ktorý si sám sebe prikyvuje?*
