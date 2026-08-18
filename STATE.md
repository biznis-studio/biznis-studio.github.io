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

## Cloudová routine — vypnutá 2026-08-18 (rozhodnutie majiteľa)

Bežala dvakrát a oba razy premyslela a potom prácu stratila. Príčinou boli
**dve nezávislé poruchy prostredia**, nie jedna:

| | |
|---|---|
| zápis | `git push` → 403 · GitHub MCP `create_branch` aj `push_files` → 403 · **Claude GitHub App sa nedá nainštalovať** — v zozname účtov je len `jozefrusnak4-ux`, ktorý repozitár nevlastní |
| čítanie | **14 z 15 zberačov v poruche**, otvoriť sa podarilo **3 z 25** stránok |

Inštalácia aplikácie by opravila zápis a slepotu nie — preto sa nenaháňa.

**Ako to beží teraz:** zber v GitHub Actions (sieť má), úsudok v relácii pri
otvorenom počítači. Menej efektné, ale nevyrába to plytký záver z troch
stránok s tvárou prehľadu sveta.

**Späť sa to zapne jedným príkazom** — `RemoteTrigger update
trig_0119FrcTPSc6Z4WfJNxHmjwA` s `enabled:true`. Revízia rozhodnutia
2026-09-18.

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
