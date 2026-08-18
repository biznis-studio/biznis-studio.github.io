# STATE — živý stav

Prečíta sa na začiatku každej relácie, doplní sa na konci. Agent medzi behmi
zabudne, tento súbor nie. **Krátky zámerne** — čo je hotové, patrí do histórie,
nie sem.

Aktualizované: **2026-08-18** (večerný beh)

---

## Čo je práve otvorené

| Vec | Stav | Ďalší krok |
|---|---|---|
| Akceptačná sada packu | **13 zo 17** · zlyhali S8 `Z4`, S9 `Z1`, S17 `Z7` | prehodnotiť S8 a S9 v čistom kontexte (hodnotil ich ten, kto ich spustil) |
| Taxonómia Z1–Z7 | **má dieru** | S8 = vynechaná povinná časť výstupu, S9 = procedúra sa nedopracovala k rozhodujúcemu testu — ani jedno nemá kód |
| Pack v0.5.0 | **NEVYDANÝ** — `vydane: false` v MANIFESTe | až po 17/17; každý dnešný výsledok je 1 beh, nie 5/5 |
| Nová pozícia na webe | SK **3 články** + služba, EN 1 článok + sekcia na domovskej | 3. článok je naživo (HTTP 200, obrázok 200) |
| Evolučná vrstva | beží cez `scripts/frontier_run.py`; `experiments` má **2 merania naživo** so základom zmeraným pred zásahom (#3 index, #4 podiel 404) | domerať kandidáta 2026-08-25; predtým bola tabuľka „prázdna" len zdanlivo — mala 2 uzavreté, oba offline |
| Výklad fronty | úsudok mimo → artefakt JSON → overenie → atomický zápis v uzle | úsudok stále robí človek alebo cloud; automatický ho nerobí nikto |
| Inbound dráha | skill `/dopyt` hotový | napojiť na to, čo chodí z formulára |
| Sľuby aktív | **10 aktív**, žiadne po termíne | týždenná kontrola beží sama |
| Zákaznícke údaje na verejnom repozitári | **13 riadkov na origin/main** (mená + čísla prípadov) | brána `scripts/kontrola_repozitara.py` blokuje nové; **o už zverejnenom rozhoduje majiteľ** |

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

## Viditeľnosť vo vyhľadávaní — meraním 2026-08-18

Toto je momentálne najtvrdšia hrana: web je hotový a nikto ho nevidí.

| | |
|---|---|
| stránok v indexe | **2 zo 43** |
| „Not indexed" | **0, „No reasons"** — Google o zvyšku nevie, nezamietol ho |
| sitemapa | **„Couldn't fetch", Discovered pages 0**, 24 h po opätovnom odoslaní |
| požiadavky Googlebota | **9 za tri týždne**, Purpose **Refresh 100 %, Discovery 0 %** |
| z toho 404 | **22 %** — `/favicon.ico`, opravené 2026-08-18, naživo 200 |
| `/sk/` v inšpekcii URL | „URL is unknown to Google", žiadna odkazujúca stránka, Last crawl N/A |

**Naša strana je čistá vo všetkom merateľnom zvonku:** sitemapa 200 /
`application/xml` / 43 URL / parsuje sa, aj s hlavičkou Googlebota aj cez IPv6;
robots.txt povoľuje; domovská odkazuje na `/sk/` trikrát bez `nofollow`;
kanonické URL konzistentné; 0 osirelých stránok.

**Druhý kanál, nezávislý od Googlu:** IndexNow (Bing/Yandex/Seznam) sa pinguje
každý beh a **odosielanie funguje** — 200 na 43 URL, kľúčový súbor naživo.
Či z toho niečo vzniklo, je pre nás **nemerateľné**: bing.com aj DuckDuckGo
vrátia na `site:` dotaz CAPTCHA, a Bing Webmaster Tools nemá prihlásený účet.
Sonda tiež ukázala, že **neplatný kľúč vráti 202**, takže úspešný stavový kód
nedokazuje ani platnosť kľúča.

**Obchádzka, ktorá beží:** `/sk/` aj domovská zaradené do priority crawl queue
cez inšpekciu URL (2026-08-18, domovská až na druhý pokus — prvý zlyhal na chybe
Googlu). Rozhodnutie #20, revízia 2026-08-25. Merajú to experimenty #3 a #4,
ktorých základ je zapísaný pred zásahom a už sa nedá prepísať.

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

**Bing Webmaster Tools: nie je prihlásený účet.** Kým sa doň majiteľ neprihlási
(má účet Microsoft cez M365), je stav v Bingu pre nás nemerateľný — hoci doň
odosielame 43 URL po každom behu. Účty nezakladám.

**Copilot: klávesnica sa do stránky nedostáva.** Kliknutia aj JavaScript
fungujú, ale vložený text sa neobjaví — ani „test". Je to zameranie okna na
úrovni systému. **Stačí kliknúť do okna Chromu** a viem dobehnúť zvyšných
sedem scenárov. Do vtedy je pack 0.5.0 nevydaný.

*Obchádzka vyskúšaná a zamietnutá 2026-08-18:* v Search Console sa to isté dá
obísť cez `form_input` na prvku namiesto klávesnice. V Copilote nie — vstupné
pole je `contenteditable` SPAN, nie formulárový prvok, a `form_input` ho
odmieta („Element type SPAN is not a supported form input"). Netreba to skúšať
znovu.

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

2026-08-18 · brána na zákaznícke údaje (pravidlo vynucoval neexistujúci skript) ·
zistené, že mená zákazníkov sú na verejnom origin/main · `/favicon.ico` vyrobený
a nasadený, bral 22 % rozpočtu prehľadávania · sitemapa neprečítaná ani po 24 h,
`/sk/` aj domovská obídené cez priority crawl queue · dva experimenty naživo so
základom zmeraným pred zásahom · fronta poznatkov 10 → 1 po tom, čo dôsledkom
prestala byť iba hypotéza.
