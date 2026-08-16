# Architektúra — Copilot ako mozog v tenante, GitHub ako dielňa na metódu

2026-08-16. Odpovedá na otázku: *ako to postaviť tak, aby to firma s prísnou
ochranou dát vedela schváliť.*

---

## 1. Rozhodujúca vec: čo je metóda a čo sú dáta

Firma nás pustí alebo nepustí podľa jedinej otázky: **odchádzajú z tenanta
firemné dáta?** Preto musí byť hranica jasná ešte pred prvým riadkom.

| | **Metóda** (pack) | **Dáta** (prípady) |
|---|---|---|
| Čo to je | kategórie, príčiny, rozlíšenia, postup, brána, scenáre | konkrétne reklamácie, zákazníci, čísla, mená, fotky |
| Odkiaľ | odborné know-how, zovšeobecnené | z prevádzky |
| Kde žije | **GitHub** — verzované, s bránou a CI | **výhradne v tenante** (SharePoint / OneDrive / Teams) |
| Kto to vidí | my aj zákazník | **len zákazník** |
| Opustí to tenant? | je to metóda, nie ich dáta | **nikdy** |

**Pravidlo, ktoré sa neporušuje: do GitHubu nejde ani jeden zákaznícky prípad.**
Ani anonymizovaný, ani „len na test". Akonáhle by šiel, GitHub sa stáva novým
spracovateľom firemných dát a celé schvaľovanie padá — to je presne to, čo je
v `8D-Agent/DATA_SECURITY_pre_IT.md` popísané ako variant B, ktorý potrebuje
samostatné schválenie.

**Precedens, že to platí aj pre nás:** pri stavaní quality packu sme zo zdroja
museli vyčistiť firemné označenia a jeden zákaznícky identifikátor z testovacích
scenárov — commit *„Vyčistiť zdroj od zákazníckych a firemných údajov"*. Nie je
to teoretické pravidlo, už raz sa porušilo.

## 2. Ako to beží

```
GITHUB (metóda)                        TENANT ZÁKAZNÍKA (dáta)
─────────────────                      ────────────────────────
zdrojová tabuľka  ──┐
procedúra           │   build + brána      dokument s packom
scenáre             ├──────────────────▶   v ich SharePointe/OneDrive
                    │   + akceptačná sada          │
verzia            ──┘                              ▼
                                            Copilot ─── číta ich dokumenty
                                               │        (ich oprávnenia)
                                               ▼
                                        odpoveď + zápis prípadu
                                        späť do ICH úložiska
```

**Jednosmerná šípka je celý trik.** Z GitHubu do tenanta ide **len pack**.
Z tenanta von neide nič.

## 3. Zápis — kde sa to skutočne rieši

Toto bola najdlhšie neriešená diera: Copilot v chate si nič nepamätá a nikam
nezapisuje. Odpoveď **nie je GitHub** — tam by išli dáta.

| Čo treba zapísať | Kam | Poznámka |
|---|---|---|
| priebeh a záver prípadu | **do ich úložiska** (SharePoint zoznam, Excel, Word) | nikdy k nám |
| nová príčina / rozlíšenie objavené na prípade | **do GitHubu** — ale **len zovšeobecnené**, bez zákazníka, čísla a kontextu | toto je legitímny prínos naspäť do metódy |

**Tá druhá cesta je jadro produktu a treba ju povedať nahlas:** prípad
u zákazníka odhalí, že v katalógu chýba príčina. Do metódy sa vráti **veta
o mechanizme a jeho rozlíšení**, nie prípad. Tak rastie pack bez toho, aby čokoľvek
citlivé opustilo firmu.

## 4. Prekážka, ktorú netreba obchádzať

**Bez licencie Copilota sa znalosť nedá zavesiť ako súbor.** Overené 2026-08-08:
Agent Builder ponúka len „Add specific URL". Preto sa pack v tej ceste vkladá do
konverzácie ako text alebo príloha.

Overené 2026-08-15 na reálnom účte: **vložený ako text funguje** — päť
blokujúcich scenárov prešlo. Nie je to elegantné, ale je to cesta, ktorá
nevyžaduje od IT vôbec nič.

| Cesta | Čo treba od IT | Kedy ju použiť |
|---|---|---|
| **Pack ako príloha do chatu** | **nič** | pilot, prvý kontakt, dôkaz pred rozhodnutím |
| **Pack v ich SharePointe + agent** | licencie + inštalácia agenta | keď to už chcú používať denne |

**Prvá cesta je predajný argument.** Zákazník si to vyskúša bez jediného
schvaľovacieho kola. To je najlacnejší možný vstup do firmy, aký existuje.

## 5. Čo z toho ide do ponuky

- *„Nič neodchádza z vášho tenanta. Do vášho Microsoftu ide jeden dokument;
  vaše prípady zostávajú u vás."*
- *„Vyskúšate to bez zásahu IT — priložením súboru do chatu."*
- *„Metóda je verzovaná a testovaná mimo vašich dát. Preto ju vieme zlepšovať
  bez toho, aby sme sa k vašim dátam vôbec priblížili."*

## 6. Čo tu nie je dokázané

- **Zápis prípadu späť do SharePointu** v licenčnej ceste nie je odskúšaný.
  Vieme, že akcie a agent flows zapisovať vedia — neoverili sme to sami.
- **Purview so šifrovaním** môže dokumenty pred agentom skryť **ticho**.
  Povinný test na jednom označenom dokumente pred nasadením.
- Nikto zvonku zatiaľ nepovedal, že túto hranicu potrebuje tak, ako si myslíme.
