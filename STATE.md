# STATE — živý stav

Prečíta sa na začiatku každej relácie, doplní sa na konci. Agent medzi behmi
zabudne, tento súbor nie. **Krátky zámerne** — čo je hotové, patrí do histórie,
nie sem.

Aktualizované: **2026-08-17** (večerný beh)

---

## Čo je práve otvorené

| Vec | Stav | Ďalší krok |
|---|---|---|
| Akceptačná sada packu | **13 zo 17** · zlyhali S8 `Z4`, S9 `Z1`, S17 `Z7` | prehodnotiť S8 a S9 v čistom kontexte (hodnotil ich ten, kto ich spustil) |
| Taxonómia Z1–Z7 | **má dieru** | S8 = vynechaná povinná časť výstupu, S9 = procedúra sa nedopracovala k rozhodujúcemu testu — ani jedno nemá kód |
| Pack v0.5.0 | **NEVYDANÝ** — `vydane: false` v MANIFESTe | až po 17/17; každý dnešný výsledok je 1 beh, nie 5/5 |
| Nová pozícia na webe | SK **3 články** + služba, EN 1 článok + sekcia na domovskej | 3. článok je naživo (HTTP 200, obrázok 200) |
| Evolučná vrstva | celá skutočná cesta beží cez `scripts/frontier_run.py` — zámok, kontrolné body, rozpočet, atomické uzly | `experiments` má stále **0 riadkov** — bez porovnania kandidáta so základom niet experimentu |
| Výklad fronty | úsudok mimo → artefakt JSON → overenie → atomický zápis v uzle | úsudok stále robí človek alebo cloud; automatický ho nerobí nikto |
| Inbound dráha | skill `/dopyt` hotový | napojiť na to, čo chodí z formulára |
| Sľuby aktív | **10 aktív**, žiadne po termíne | týždenná kontrola beží sama |

## Kotvy — čo hovorí realita

Toto je jediné, čo do rozhodovania smie vstupovať ako dôkaz.

| Kotva | Hodnota | Odkedy |
|---|---|---|
| Zaplatené faktúry | **0** | — |
| Dopyty z formulára | **0** | formuláre pribudli až 2026-08-16 |
| Predaje Gumroad | **0** (0 zobrazení) | mesiac |
| Search Console | bez reálnych dát | — |
| Reálne prípady cez pack | **3**, všetky interné | 2026-08-09/10 |

**Prázdna kotva nie je záporný výsledok.** Znamená, že sa ešte nemeria —
a do 2026-08-16 sa ani nedalo ozvať: anglická domovská ani „Hire us" nemali
formulár.

## Čo je zmrazené a nedotýka sa

- **Pack** — mení sa len keď si to vynúti reálny prípad alebo rozhodnutie
  majiteľa. Medzi 12. a 16. 8. bolo päť verzií a `source/` sa nezmenil ani raz.
- **Snímanie (S1–S6)** — odložené na koniec. Pri prázdnych kotvách je to
  telemetria ničoho.
- **Ablácia pravidiel** — predčasná, kým sada nebola odbehnutá celá.

## Čo čaká na rozhodnutie majiteľa

1. **Obchodný záver v diagnostike** (Z7): doplniť do packu pravidlo, že
   uznanie/zamietnutie reklamácie nie je diagnostický výstup?
2. **Znečistený materiál čapu** je v katalógu 3× plus raz s dodatkom, takže
   presná zhoda ich rozdelí a jedna väzba je neviditeľná. Zjednotiť názvy?
3. **Druhý pack v inej profesii** — jediný chýbajúci dôkaz, že je to výrobná
   linka a nie jeden dokument.

## Blokované na majiteľovi (jedno kliknutie)

**Copilot: klávesnica sa do stránky nedostáva.** Kliknutia aj JavaScript
fungujú, ale vložený text sa neobjaví — ani „test". Je to zameranie okna na
úrovni systému. **Stačí kliknúť do okna Chromu** a viem dobehnúť zvyšných
sedem scenárov. Do vtedy je pack 0.5.0 nevydaný.

## Cloudová autonómia — čo sa naozaj ukázalo (2026-08-17)

Routine `Frontier loop` beží denne o 9:32. Prvý ostrý beh odhalil **tri
obmedzenia prostredia**, ktoré rozhodujú o tom, čo tam vôbec má zmysel púšťať:

| | |
|---|---|
| `git push` z cloudu | **403 — egress policy.** Cloudová relácia nemá povolené písať na github.com. Sankcionovaná cesta je GitHub MCP, nie git. |
| dosah na zdroje | **7 z 9 zberačov nemých**, 15 z 25 položiek sa nedalo otvoriť — väčšina domén je z cloudu blokovaná |
| veľkosť stavu | `db/biznis.sqlite3` má **20 MB**; cez GitHub MCP sa taký súbor rozumne poslať nedá |

**Čo sa medzitým zmenilo:** výklad už nezapisuje priamo. Úsudok vytvorí JSON
artefakt do `state/vyklad/`, ten sa celý overí a zapíše v jednej transakcii
vnútri uzla — takže cloudový beh nemusí mať právo zápisu do stavu, stačí mu
odovzdať artefakt.

**Dôsledok:** cloudový beh v tejto podobe **nevie výskum ani uložiť výsledok**.
Jeho commit `789581c` zostal v pieskovisku a zanikol. Prácu, ktorú našiel, som
zopakoval ručne — ale to nie je autonómia, to je drahý spôsob, ako mať nápady.

**Čo z toho vyplýva pre architektúru** (rozhodnutie o smerovaní, nie o kóde —
preto čaká na majiteľa): zber patrí do GitHub Actions, ktoré sieť majú;
cloudový beh by mal iba vykladať to, čo už je v databáze, a stav evolučnej
vrstvy by nemal žiť v 20 MB binárnom súbore, ale v malom zlučiteľnom formáte.

## Web — stav meraním (2026-08-17)

| | |
|---|---|
| šablónové popisy | **0** (bolo 19 z 19 stránok) |
| stránky bez kontaktného formulára | **2**, obe zámerne (credits, news) |
| rovné úvodzovky v článkoch | **0** |
| mŕtve externé odkazy | **0** z 28 |
| rozbité vnútorné odkazy | **0** z 690 |
| kontrast textu | 7,48 tmavý · 6,25 svetlý (limit 4,5) |
| dotykový terč na 375 px | 40 px · žiadne pretečenie |

## Posledný beh

2026-08-17 · postavená evolučná vrstva a snímanie špičky (14 zdrojov) ·
prvý výklad fronty (25 položiek, 11 zapísaných) · zámok behu proti súbežnému
zápisu · zmierené rozídené databázy po incidente so štyrmi súbežnými zapisovateľmi ·
tri chyby zberu opravené (abecedná vzorka registra, mlčiace zdroje, dedup medzi
behmi) · tretí SK článok naživo · `jozefrusnak4-ux` pridaný ako správca repozitára,
cloudová routine založená a spustená.
