# Automatizovaný digitálny ekosystém — návrh

2026-08-16. Návrh, nie stav. Čo z toho beží dnes, je označené.

**Cieľ:** firma, ktorá beží ako graf slučiek. Sníma trh, vyrába aktíva, overuje
ich, publikuje, meria dopad a učí sa — človek stojí len tam, kde sa rozhoduje
alebo kde vzniká záväzok.

---

## 0. Podmienka, bez ktorej je celý zvyšok ozdoba

**Ekosystém, ktorý si sám odhlasuje úspech, vyrobí dokonalé artefakty a nula
tržieb.** To nie je hypotéza — je to popis posledného mesiaca: zelená brána,
zelený audit, zelené CI, žiadny zákazník.

Preto celý návrh stojí na jednom pravidle:

> **Každý uzol, ktorý niečo tvrdí, musí byť pripojený aspoň na jednu kotvu —
> vec, ktorá sa nedá prehovoriť.**

Kotvy tohto biznisu, zoradené podľa sily:

| Kotva | Prečo sa nedá prehovoriť |
|---|---|
| **Zaplatená faktúra** | buď prišli peniaze, alebo neprišli |
| **Dopyt z formulára / odpoveď človeka** | existuje alebo neexistuje |
| **Search Console: impresie a kliky** | meria Google, nie my |
| **Živá URL a jej obsah** | buď je tam, alebo nie |
| **Uzavretý prípad so známym výsledkom** | výsledok vznikol bez nás |
| **Exit code brány a auditu** | nula alebo nie |

Všetko ostatné — počet článkov, verzií, commitov, „vyzerá to dobre" — je
**vnútorná konzistencia** a do rozhodovania nesmie vstupovať ako dôkaz.

---

## 1. Tvar grafu

Päť vrstiev. Šípka je hrana len tam, kde naozaj tečú dáta.

```
  ┌── SNÍMANIE ──────────────────────────────────────────┐
  │  S1 Search Console   S2 dopyty/formulár   S3 predaje │   denne, paralelne
  │  S4 živá stránka     S5 SERP kontrola     S6 pošta   │   (žiadne hrany
  └──────────────────────┬───────────────────────────────┘    medzi nimi)
                         │  fakty, nie dojmy
                ┌────────▼─────────┐
                │  R  ROZHODNUTIE  │  ← ČLOVEK. Úzke hrdlo zámerne.
                └────────┬─────────┘
  ┌──────────────────────▼───────────────────────────────┐
  │  VÝROBA — fan out, jeden pracovník na jedno aktívum  │
  │  V1 článok   V2 stránka   V3 nástroj   V4 variant    │
  └──────────────────────┬───────────────────────────────┘
  ┌──────────────────────▼───────────────────────────────┐
  │  OVEROVANIE                                          │
  │  G  brány (KÓD, deterministické)                     │
  │  K  kontrolór (model, ČISTÝ kontext, vracia kód)     │
  └──────────────────────┬───────────────────────────────┘
                ┌────────▼─────────┐
                │  P  PUBLIKOVANIE │  ← ČLOVEK pri všetkom navonok
                └────────┬─────────┘
  ┌──────────────────────▼───────────────────────────────┐
  │  UČENIE — späť do snímania                           │
  │  U1 vyhodnotenie sľubu   U2 ablácia   U3 zabitie     │
  └──────────────────────────────────────────────────────┘
```

### Test falošných hrán — čo sa dá naozaj paralelizovať

| Dvojica | Skutočná hrana? |
|---|---|
| S1…S6 navzájom | **nie** → všetkých šesť beží naraz |
| V1…V4 navzájom | **nie** → fan out, každý vo vlastnom worktree |
| Brána `G` → kontrolór `K` | **áno** — nemá zmysel dávať modelu to, čo padne na schéme |
| Výroba → publikovanie | **áno**, a je tam človek |
| Snímanie → výroba | **len cez R.** Bez rozhodnutia je to výroba pre výrobu |

**Nájdená falošná hrana v tom, ako pracujeme dnes:** SEO článok a stránka služby
sa robia v rade, hoci na seba nečakajú. Rovnako beh 17 scenárov × 5 opakovaní —
85 úplne nezávislých behov, ktoré púšťam po jednom.

---

## 2. Uzly — kontrakt každého z nich

Uzol bez kontraktu je skrytý workflow napchatý do jedného promptu. Preto každý
uzol má: **jednu úlohu · pevný vstup · pevný výstup · rozpočet · päť koncov.**

### Snímanie (denne, bez človeka, len čítanie)

| Uzol | Vstup | Výstup |
|---|---|---|
| **S1** Search Console | API | `{dotaz, impresie, kliky, pozicia, datum}` |
| **S2** dopyty | Formspree | `{zdroj, sprava, datum}` — **nikdy neodpovedá sám** |
| **S3** predaje | Gumroad | `{produkt, zobrazenia, predaje}` |
| **S4** živá stránka | `deploy.py` | `{url, ok, co_chyba}` |
| **S5** SERP | `find-opportunities` | `{dotaz, kto_drzi, sanca}` |
| **S6** pošta | schránka | `{od, tema, vyzaduje_rozhodnutie}` |

**Rozpočet:** 10 minút na uzol, 1× denne. Výstup do `STATE.md`, nie do chatu.

### R — rozhodnutie (človek, nezastupiteľné)

Vstup: rozdiel v `STATE.md` oproti včerajšku. Výstup: **nula až tri zadania.**

Sem patrí to, čo agent nesmie: čo sa bude stavať, čo sa zabije, komu sa píše,
čo stojí peniaze. Toto hrdlo je zámerné — bez neho ekosystém vyrába objem.

### Výroba (fan out, izolovane)

Kontrakt každého pracovníka:

```json
{ "typ": "clanok|stranka|nastroj|variant",
  "cielovy_dotaz": "…",
  "slub": "merateľná podmienka úspechu",
  "datum_kontroly": "YYYY-MM-DD",
  "subory": ["…"] }
```

**`slub` a `datum_kontroly` sú povinné.** Aktívum bez merateľného sľubu sa
nevyrába — nie je totiž ako zistiť, či ho o mesiac zabiť.

### Overovanie — dve úrovne, v tomto poradí

**G — brány (kód, žiadny model).** Bežia dnes: `audit_site.py`,
`build_pack.py --check`, Stop hook. Doplniť: kontrola tvrdení — **číslo
v publikovanom texte musí mať zdroj**, inak sa nepublikuje.

**K — kontrolór (model, čistý kontext).** Vidí **len výstup a kritériá**, nikdy
úvahu autora. Vracia smerovanie, nie známku:

```json
{ "pass": false, "kod": "Z6",
  "co": "veta o 30 % úspore bez zdroja",
  "dalej": "odstrániť číslo alebo doplniť odkaz" }
```

### P — publikovanie (človek pri všetkom navonok)

Neautomatizuje sa nikdy: odoslanie správy, publikovanie navonok, čokoľvek za
peniaze, prihlasovacie údaje, prijatie podmienok. Nie zo zdvorilosti — je to
hranica, kde vzniká záväzok.

### Učenie (späť do snímania)

- **U1 vyhodnotenie sľubu.** V `datum_kontroly` sa aktívum porovná so svojím
  sľubom. Splnil → zostáva. Nesplnil → **na zabitie.**
- **U2 ablácia.** Vypni pravidlo, pusti sadu; ak sa nič nezhorší, zmaž.
- **U3 zabitie.** Aktívum, ktoré dvakrát nesplnilo sľub, sa stiahne. Bez toho
  ekosystém len rastie.

---

## 3. Vie tento systém vziať späť „hotovo"?

Jediný test, ktorý ohodnotí celý návrh.

| Vec | Čo ju odznačí |
|---|---|
| Pack | `vydane: false` v MANIFESTe pri zlyhaní blokujúceho scenára — **beží** |
| Web | audit spadne → Stop hook nepustí koniec ťahu — **beží** |
| Verzia | chýba záznam alebo `DÔVOD ZMENY` → nevydá sa — **beží** |
| **Článok / stránka** | **U1 — nesplnený sľub v termíne → na zabitie** — chýba |
| **Služba v cenníku** | **žiadny dopyt do dátumu kontroly → stiahnuť** — chýba |
| **Pravidlo v packu** | **U2 ablácia** — chýba |

**Tri z piatich chýbajú a všetky tri sú na strane biznisu, nie techniky.**
To je presná diagnóza posledného mesiaca: vieme odznačiť kód, nevieme odznačiť
obchodné rozhodnutie.

---

## 4. Slučka pod každým uzlom

Graf koordinuje, slučka robí uzol dôveryhodným.

```
prečítaj STATE + CONSTRAINTS → konaj → over (najprv kód, potom kontrolór)
   → zapíš STATE (čo sa zmenilo, čo zostalo otvorené, ďalší krok)
   → stop, keď je splnená podmienka ALEBO vyčerpaný rozpočet
```

Nikdy nie „agent povedal, že je hotovo". Vyčerpaný rozpočet je **informácia**,
nie zlyhanie — vráť čiastkový výsledok a napíš, čo by chýbalo do konca.

---

## 5. Čo z toho beží dnes

| | |
|---|---|
| **beží** | pipeline webu · audit · Stop hook · brána packu · CI · skills · pamäť (`07_Constraints`) |
| **beží čiastočne** | snímanie (Search Console ručne) · výroba (sériovo, nie fan out) |
| **nebeží** | `STATE.md` naprieč reláciami · kontrolór v čistom kontexte · sľub + dátum kontroly pri aktívach · U1/U2/U3 · rozpočty · kontrola tvrdení |

---

## 6. Poradie stavania — najlacnejšie a najúčinnejšie najprv

1. **`STATE.md` + sľub a dátum kontroly pri každom aktíve.** Bez toho sa nedá
   nič zabiť a ekosystém len rastie. *Jeden súbor, hodina práce.*
2. **U1 — vyhodnotenie sľubov.** Cron, ktorý raz týždenne vypíše, čo je po
   termíne a nesplnilo. **Prvý mechanizmus, ktorý vie povedať „toto zabi".**
3. **Inbound dráha:** dopyt → kvalifikácia → návrh → ponuka → follow-up →
   termín. Jediná časť akvizície, ktorá sa smie automatizovať.
4. **Kontrolór v čistom kontexte** pre publikovaný text (tvrdenia, slovenčina).
5. **Fan out výroby** — až keď je uzol dôveryhodný. Skôr je to rýchlejšia cesta
   k šíreniu chýb.
6. **Snímanie S1–S6** — až posledné. Kým sú kotvy prázdne, je to telemetria
   ničoho.

**Bod 1 a 2 sú to celé.** Zvyšok je zrýchlenie; tieto dva sú jediné, ktoré
menia to, že systém vie len povyšovať.

---

## 6b. Korekcie po oponentúre (ChatGPT, 2026-08-16)

Dve vecné opravy, ktoré prijímam, a jedna, ktorú neprijímam.

**PRIJATÉ — snímanie je dnes divadlo.** Šesť senzorov vyzerá ako observability
vrstva, ale bez objemu je to *„telemetria ničoho"*. Pri nule impresií a nule
predajov meria šesť uzlov ticho a vracia zelené fajky. **Presúva sa z bodu 3
poradia na koniec** — zapína sa až vtedy, keď je čo snímať.

**PRIJATÉ — ablácia je zatiaľ predčasná.** Pri sérii 0 → 0 → 0 nehovorí
vypnutie pravidla nič. *(S jednou výhradou: ablácia proti akceptačnej sade je
riadené meranie, nie trhové dáta — takže predčasná je preto, že sme sadu ešte
ani raz neodbehli celú, nie preto, že by závisela od trhu.)*

**PRIJATÉ — preformulovanie cieľa.** „Celá firma autonómna" je architektonický
cieľ, nie obchodný, a dá sa splniť dokonale pri firme bez zákazníkov. Nahrádza
sa tvrdším:

> **Minimalizovať počet ľudských rozhodnutí potrebných na dosiahnutie jedného
> merateľného obchodného výsledku.**

**NEPRIJATÉ — „odstrániť človeka z uzla ROZHODNUTIE".** V tom uzle sedia veci,
ktoré sa automatizovať nesmú: záväzok voči zákazníkovi, výdavok, odoslaná
správa. Automatizovať sa dá **výber spomedzi vopred schválených možností**
s registrovanou hypotézou — nie samotné rozhodnutie vstúpiť do záväzku.
Hranica zostáva tam, kde vzniká záväzok.

**Zhoda v tom podstatnom:** akvizícia **outbound sa automatizovať nesmie** —
agent optimalizovaný na „získaj zákazníkov" prirodzene skončí pri cold maile,
scrapingu a DM, a bude sa pritom považovať za úspešný. **Inbound sa
automatizovať dá ďaleko:** dopyt → kvalifikácia → návrh → cenová ponuka →
follow-up → termín.

## 7. Čo tento návrh nerieši a treba to povedať

**Nevyrobí dopyt.** Ani jeden uzol nezistí, či niekto chce to, čo predávame —
vie len rýchlejšie ukázať, že nechce. Automatizovaný ekosystém s nulovým
dopytom je nula za jednotku času.

**Kotvy S1–S3 sú dnes takmer prázdne.** Search Console nemá reálne dáta,
Gumroad má nula zobrazení. Systém postavený na prázdnych kotvách meria ticho.

**Preto najdrahšia časť je stále mimo grafu:** jeden človek zvonku, ktorý
povie, že toto je problém, za ktorý zaplatí. Ekosystém tú odpoveď vie prijať,
spracovať a využiť — vyrobiť ju nevie.
