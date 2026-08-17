# STATE — živý stav

Prečíta sa na začiatku každej relácie, doplní sa na konci. Agent medzi behmi
zabudne, tento súbor nie. **Krátky zámerne** — čo je hotové, patrí do histórie,
nie sem.

Aktualizované: **2026-08-17**

---

## Čo je práve otvorené

| Vec | Stav | Ďalší krok |
|---|---|---|
| Akceptačná sada packu | **13 zo 17** · zlyhali S8 `Z4`, S9 `Z1`, S17 `Z7` | prehodnotiť S8 a S9 v čistom kontexte (hodnotil ich ten, kto ich spustil) |
| Taxonómia Z1–Z7 | **má dieru** | S8 = vynechaná povinná časť výstupu, S9 = procedúra sa nedopracovala k rozhodujúcemu testu — ani jedno nemá kód |
| Pack v0.5.0 | **NEVYDANÝ** — `vydane: false` v MANIFESTe | až po 17/17; každý dnešný výsledok je 1 beh, nie 5/5 |
| Nová pozícia na webe | SK **3 články** + služba, EN 1 článok + sekcia na domovskej | 3. článok postavený vrátane obrázka, **nedeployovaný a neprekorektúrovaný** |
| Tretí SK článok | `ktore-rozhodnutie-zverit-ai` | nezávislá korektúra slovenčiny nikdy nedobehla — spustiť pred deployom |
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

## Blokované na majiteľovi — autonómia stroja

**Cloudový beh evolučnej vrstvy sa nedá založiť: tri rôzne GitHub identity.**
Lokálne `gh` je prihlásené ako `fwwk4pb868-afk`, repozitár vlastní
`biznis-studio`, a na claude.ai je prepojený `jozefrusnak4-ux` (vidí len
`cestapoznania`, na „biznis“ hlási *No repos match*). API preto vracia 401
`Connect your GitHub account…`. Riešenie: prihlásiť sa na github.com ako
**`biznis-studio`** a až tam nainštalovať Claude GitHub App — alebo pridať
`jozefrusnak4-ux` ako spolupracovníka s právami na repozitár.

**Dôsledok, kým to neplatí:** zber beží sám (GitHub Actions), ale **úsudok nie**.
Vykladanie fronty je viazané na reláciu, takže systém je autonómny len vtedy,
keď je otvorený. To je presne tá časť, ktorá má byť inteligentná.

## Blokované na majiteľovi (jedno kliknutie)

**Copilot: klávesnica sa do stránky nedostáva.** Kliknutia aj JavaScript
fungujú, ale vložený text sa neobjaví — ani „test". Je to zameranie okna na
úrovni systému. **Stačí kliknúť do okna Chromu** a viem dobehnúť zvyšných
sedem scenárov. Do vtedy je pack 0.5.0 nevydaný.

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

2026-08-16 · fan out na štyroch vetvách · publikované 2 články (SK+EN) · formuláre pod všetky články oboch jazykov · prvý článok v novej pozícii · formuláre doplnené na
domovskú, work.html a pod články · „Hire us" vedie na formulár · SK stránka
zo 4 na 11 obrázkov · zavedený register sľubov a týždenná kontrola.
