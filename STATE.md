# STATE — živý stav

Prečíta sa na začiatku každej relácie, doplní sa na konci. Agent medzi behmi
zabudne, tento súbor nie. **Krátky zámerne** — čo je hotové, patrí do histórie,
nie sem.

Aktualizované: **2026-08-18** (večerný beh)

---

## Čo je práve otvorené

| Vec | Stav | Ďalší krok |
|---|---|---|
| Akceptačná sada packu | **doterajšie výsledky sú v otázke** — pack v `localStorage` niesol 1 736 znakov textu rozhrania, takže behy od 17. 8. netestovali postavený artefakt | pack vyčistený 19. 8.; sadu dobehnúť znovu, hodnotí niekto iný než ten, kto ju spustil |
| Taxonómia Z1–Z9 | **diera zaplnená 2026-08-19** — `Z8` nenavrhol rozhodujúci test, `Z9` chýba dopredu-akcia | konce v packu **existujú** (`ZASTAV`, `ODOVZDAJ ČLOVEKU`); chýba **spúšťač prechodu na ne**. A pri S9 je pod tým ešte diera medzi ČASŤOU I a II — 6 príčin zo 125 je pri reklamácii nedosiahnuteľných |
| Pack v0.5.0 | **NEVYDANÝ** — `vydane: false` v MANIFESTe | až po 17/17; každý dnešný výsledok je 1 beh, nie 5/5 |
| Nová pozícia na webe | SK **10 článkov + 2 nástroje zadarmo**; kalkulačka má 5 vstupných odkazov namiesto 1, test e-faktúry má obrázok, cenník sa pod 640 px skladá na karty, dotykové ciele v pätičke 40 px namiesto 22 px (19. 8., všetko overené naživo pri 375/768/1280 px) | h1 domovskej je **rozhodnutie majiteľa**; EN strana zaostáva za SK; prelinkovanie katalógu **zamietnuté** — 0 zobrazení, žiadna veličina, ktorá by sa tým pohla |
| Evolučná vrstva | beží cez `scripts/frontier_run.py`; `experiments` má **2 merania naživo** so základom zmeraným pred zásahom (#3 index, #4 podiel 404) | domerať kandidáta 2026-08-25; **príčina #4 je známa** — obe 404 sú `/favicon.ico`, súbor sa od 19. 8. generuje a vracia 200, podiel klesne až po ďalšom prehľadávaní |
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

## Pack — dva nálezy 2026-08-19

**Druhý je vážnejší: pack chodil do Copilota ako jeden riadok.**
`execCommand('insertText')` zahodí všetky zalomenia — 25 318 znakov skončilo
v jednom odseku (`br: 0`, `textContent` bez jediného `\n`). Pack je pritom
štruktúrovaný dokument: nadpisy, päť koncov a vetvy stromov stoja na riadkoch.
**Takto to išlo do každého behu od 17. 8.**

Oprava: vkladať syntetickou udalosťou `paste` s `DataTransfer`. Overené sondou
vopred (tri riadky → tri odseky) aj na celom packu → **385 riadkov**.

**Kontrola pred každým behom** (nie po ňom): 385 riadkov, 25 702 znakov,
0 z 13 kľúčových značiek chýba, 0 výskytov „Stlačením klávesu".

### Prvý nález — text rozhrania v packu

## Pack — nález 2026-08-19

Pack sa do Copilota vkladá z `localStorage.__pack`. Ten sa 17. 8. vyzobal
z **vykresleného DOM**, takže zobral aj ovládacie pomôcky rozhrania:

| | |
|---|---|
| pred vyčistením | 27 434 znakov |
| po vyčistení | 25 700 znakov |
| odstránené | 17× „Stlačením klávesu Tab prejdete na tlačidlo Ďalšie možnosti", 14 zdvojených nadpisov |
| postavený `.docx` dáva | 25 492 znakov |
| nadpis | bol odseknutý na `profil`, doplnený na `profilov` |

**Obsahovo bol pack celý** — po vyčistení sedí všetkých 13 kľúčových značiek
a všetkých päť koncov (`POKRAČUJ`, `ZOPAKUJ`, `OBÍDI`, `ODOVZDAJ ČLOVEKU`,
`ZASTAV`). Strata bola v obale, nie v procedúre.

**Dôsledok:** behy S3, S4, S5, S8, S9, S10, S12 zo 17. 8. netestovali artefakt,
ktorý sa vydáva. Či to zmenilo výsledky, sa nevie — zistí sa jedine dobehnutím.
Záloha pôvodného je v `localStorage.__pack_zaloha_2026_08_19`.

## Sada — dobehnuté 2026-08-19, nehodnotené

Dva behy na vyčistenom a štruktúrovanom packu. **Hodnotenie zámerne chýba** —
spustil ich ten istý, kto by ich hodnotil. Prepisy sú v
`~/Desktop/quality-packs/tests/vysledky/2026-08-19_S{8,17}_nehodnotene.md`.

**Tretia chyba vstupu, nájdená pri S17:** keď model dostane pack ako samostatnú
prvú správu, **vytiahne si z neho názov kategórie a spracuje ho ako sťažnosť**.
Pri S17 odpovedal na vetu „Hrúbka steny mimo tolerancie", ktorú nikto neposlal.
Odvtedy idú pack a zadanie v jednej správe — pri S8 sa to už nestalo.

**Čo hovorí S8 o mojej vlastnej hypotéze:** tvrdil som, že sploštenie packu
mohlo spôsobiť zlyhania. Na S8 **nespôsobilo**. Chýbajúca dopredu-akcia
(kód `Z9`) pretrvala aj po odstránení oboch chýb vstupu — teplota správne
NEOVERENÁ, nič si nedopísal, ale nepovedal, čo začať zapisovať.
Označenie stavu kroku sa zmenilo z nesprávneho `POKRAČUJ` na **žiadne**.

**S9 odhalil štruktúrnu dieru v packu.** *(Toto nahrádza môj predchádzajúci
záver, že ide o vadu zadania. Bol nesprávny — vstup stačí.)*

Katalóg má pri príčine *Uvoľnenie zvyškového napätia až po výrobe* pole
`Nasledok`: **„Profil je pri expedícii rovný, ale u zákazníka alebo po obrábaní
sa skrúti"** — takmer doslovne vstup S9. A `Rozlisenie` je presne to, čo
kritérium žiada: *„Odložte niekoľko kusov a premerajte ich s odstupom
(napr. po 3–7 dňoch)."*

Lenže tá príčina leží v kategórii *Skrútenie profilu*, teda v **`ČASTI II`,
ktorú pack výslovne označuje „(materiál ešte u nás)"**. S9 je reklamácia, takže
model správne šiel do `ČASTI I` a pýtal sa na populáciu. **Sedem otázok ČASTI I
do stromov nevedie.**

Príčina, ktorej vlastný príznak je „u zákazníka sa skrúti", je teda uložená
v časti pre materiál, ktorý u zákazníka nie je. **Model sa držal packu a k
jedinej príčine, ktorá vstup vysvetľuje, sa procedúrou nemohol dostať.**

Nie je to zlyhanie úsudku ani vada sady. Je to diera medzi dvoma časťami packu
— a je to zmena packu, teda tvoje rozhodnutie.

**Rozsah, nie anekdota: 6 príčin zo 125**, v šiestich rôznych kategóriách, má
príznak, ktorý sa prejaví až u zákazníka, a všetky ležia v `ČASTI II`:

| kategória | príčina | príznak |
|---|---|---|
| Kolmosť medzi stenami | Tenká stena s veľkým rozpätím | uhol u zákazníka mimo tolerancie |
| Nevhodné balenie | Použitie náhradného obalu | profily poškodené u zákazníka |
| Prasklina v zvarovom spoji | Nedostatočná teplota v zváracej komore | praskne pri ohýbaní u zákazníka |
| Skrútenie profilu | Uvoľnenie zvyškového napätia | u zákazníka sa skrúti |
| Vtrúseniny | Nečistoty v materiáli čapu | prejaví sa pri obrábaní u zákazníka |
| Škrabance | Nesprávna manipulácia pri balení | zistené až u zákazníka |

Pri reklamácii je teda pre pack nedosiahnuteľných práve tých šesť príčin, ktoré
sú na reklamácie stavané.

## Hodnotenie — postavená deterministická kontrola

`tests/kontrola.py` v quality-packs. `EVAL_DISCIPLINA.md` §3b ju predpisuje od
16. 8. s poznámkou *„presne to som robil ručne regulárnymi výrazmi — patrí to
do skriptu"*; štyri dni to skript nebol a ja som tú istú prácu spravil ručne
pri troch behoch, zakaždým trochu inak.

**Verdikt nevydáva.** Vypíše, ktoré kritériá sa dajú rozhodnúť reťazcom a ako
dopadli, plus zoznam tých, ktoré kód rozhodnúť **nevie** a patria hodnotiteľovi.

| prepis | deterministicky zlyhalo |
|---|---|
| S8 | 3 zo 7 · chýba dopredu-akcia `Z9`, chýba stav kroku, chýba `OBÍDI` |
| S9 | 1 zo 7 · nenavrhol premeranie s odstupom `Z8` |
| S17 | 2 zo 6 · koniec nie je `ZASTAV`, nenavrhol drahú skúšku `Z8` |

Prvá verzia hlásila pri S9 zlyhanie navyše — vzor chytil vetu aj s popretím
(*„nepôjdem po otázkach o polohe vady pozdĺž výlisku"*). Doplnené rozpoznanie
popretia, sonda overila obe strany.

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

*Overené 19. 8.:* obe sitemapy sa Googlebotovi servírujú bezchybne — HTTP 200,
`application/xml`, platné XML, 45 a 12 URL. So `Last read` prázdnym a `Type: Unknown`
to znamená, že Google ich ešte nikdy neprečítal. Strana servera je vylúčená.

0a. **Zapísať štúdio do Zoznam.sk?** Dnes na nás nevedie ani jeden odkaz,
   ktorý by prenášal váhu: v HTML, ktoré GitHub servíruje Googlebotovi, sú
   oba odkazy na náš web `rel=nofollow` (tretí, bez nofollow, dorobí až
   JavaScript). To je časť príčiny, prečo je Discovery 0 %.
   Overil som dva katalógy a **nie sú zameniteľné**: Azet.sk zobrazuje web
   firmy len ako text, bez `<a href>` — nedáva nič. Zoznam.sk vydáva
   23 obyčajných `<a href>` bez `rel` v jedinej mestskej kategórii, priamo
   v HTML zo servera.
   **Nerobím to sám:** registrácia je založenie účtu a vystúpenie navonok.
   Cenu ani podmienky zápisu som neoveroval — to je ďalší krok, ak to
   majiteľ chce.
   *Vyvrátiteľné:* ak do 14 dní od zápisu Search Console neukáže žiadnu
   zmenu v crawl requests ani v Discovery, odkaz z katalógu nie je páka
   a ďalšie katalógy nemá zmysel riešiť.

0b. **Napísať do packu spúšťač prechodu na koniec?** Pack 0.5.0 už má päť
   koncov vrátane `ODOVZDAJ ČLOVEKU` a `ZASTAV` — S8 aj S9 na ňom bežali a po
   tej ceste nešli. Nechýba koniec, chýba **podmienka, kedy sa naň prejde**:
   nikde nie je, po koľkých ťahoch s rovnocennými NEOVERENÝMI sa ide na
   `ZASTAV`, ani že chýbajúci záznam žiada `ODOVZDAJ ČLOVEKU`. Rozhodovanie
   pritom fungovalo — model nič nedopísal a nič nevylúčil natvrdo.
   **Pack je zmrazený, takže to nerobím sám.** Vyvrátiteľné: ak sa po doplnení
   podmienky oba scenáre zmenia na VYHOVEL bez zásahu do rozhodovacích stromov,
   hypotéza platí.
   *(Pôvodne som sem napísal „doplniť koniec ESKALUJ". Bolo to zlé — ten koniec
   v packu už je. Opravené 2026-08-19.)*

0. **Analytika: zbierať, alebo nie?** Web nemá žiadnu — 0 zhôd na `gtag`,
   `analytics`, `plausible`, `umami`, `matomo`, `fathom` vo všetkých HTML, a
   GitHub Pages nedáva serverové logy. Keby Google zajtra začal posielať
   návštevnosť, dozvieme sa iba súhrnné kliky v Search Console s dvoj- až
   trojdňovým oneskorením. **Prvá návštevnosť sa nedá spätne dorátať.**
   Proti tomu stojí, že pri dnešných nulových kotvách by to meralo nič, a že
   akékoľvek sledovanie návštevníka je rozhodnutie o súkromí a o záväzku
   (súhlas, GDPR) — teda tvoje, nie moje.

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

**Copilot NIE JE zablokovaný. Overené 2026-08-19.** Karta má
`visibilityState: hidden` a `hasFocus: false`, preto syntetické klávesy do
stránky nechodia a `form_input` na `contenteditable` SPAN neplatí. Funkčná
cesta bola zapísaná už 17. 8. v `~/Desktop/quality-packs/tests/vysledky/`
a tento súbor o nej nevedel:

1. `document.querySelector('[contenteditable="true"]').focus()`
2. `document.execCommand('insertText', false, <text>)` — overené, text prejde
3. klik na tlačidlo **Odoslať**, nie Enter

**Vstup je len na pripisovanie:** `execCommand('delete')` ani `selectAll`
obsah nevymažú. Pole sa čistí reloadom stránky, nie mazaním. Pack sa vkladá
z `localStorage.__pack`, ktorý je stále naplnený.

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
