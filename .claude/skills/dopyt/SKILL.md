---
name: dopyt
description: Spracovanie prichádzajúceho dopytu — kvalifikácia, výber služby, návrh odpovede a cenový rámec. Použi vždy, keď príde dopyt z formulára, e-mailu alebo LinkedIn správy.
---

Spracuješ dopyt do bodu, kde stačí, aby ho Jozef prečítal a odoslal.
**Odpoveď nikdy neodosielaš ty.** Pripravíš ju.

`$ARGUMENTS` je text dopytu. Ak je prázdny, vypýtaj si ho.

---

## KROK 1 — kvalifikačné sito

Jediná otázka, ktorá rozhoduje, či to vieme dodať:

> **Vieme pri tej ich úlohe vopred povedať, čo by dokázalo, že odpoveď je
> nesprávna?**

- **Áno** → rozhodnutie je overiteľné, vrstva má zmysel. Pokračuj.
- **Nie** → **nepredávame to.** Nedá sa odovzdať ani obhájiť. Povedz to
  v odpovedi rovno a ponúkni to, čo spraviť vieme.
- **Neviem z dopytu posúdiť** → to je otázka do odpovede, nie dôvod hádať.

Druhá otázka: **je ich know-how niekde zapísané?** Ak je len v hlavách,
prvá zákazka je štruktúrovanie, nie nasadenie. Pack do firmy bez zapísaného
know-how vyrobí dokument, ktorý nikto nepoužije — a zlú referenciu.

## KROK 2 — čo z ponuky sedí

| Situácia v dopyte | Čo ponúknuť |
|---|---|
| majú M365, jeden opakovaný proces bolí | **posudok jedného procesu, 490 €** |
| posudok už prebehol, chcú to nasadiť | **nasadenie, 2 400 €** |
| chcú viac procesov naraz | jeden najprv; ďalší **1 400 €** |
| know-how nie je zapísané | najprv štruktúrovacia zákazka |
| chcú web, automatizáciu, identitu | bežné služby z cenníka |
| chcú niečo, čo nerobíme | povedz to a odporuč koho hľadať |

**Ceny sú z cenníka na stránke a nemenia sa podľa toho, kto sa pýta.**

## KROK 3 — čo v dopyte chýba

Vypíš, čo potrebujeme vedieť, a **zoraď podľa toho, čo najviac mení odpoveď**.
Do odpovede daj **najviac tri otázky**. Zvyšok si nechaj na hovor.

Skoro vždy chýba: aký proces · kto ho dnes robí a ako dlho · či je postup
zapísaný · či majú M365 s Copilotom · kto o tom rozhoduje.

## KROK 4 — návrh odpovede

Krátky. Konkrétny. Bez marketingových prísľubov.

**Štruktúra:** čo z dopytu chápem · či to vieme a prečo si to myslím ·
najviac tri otázky · konkrétny ďalší krok s cenou a rozsahom · podpis.

**Čo v odpovedi nikdy nesmie byť:**

- **Číslo, ktoré nemáme namerané.** Žiadne „ušetríte 30 %".
- **Referencie, logá ani počty klientov**, ktoré nemáme.
- Sľub, že AI nahradí ľudí.
- Zoznam toho, čo nedostanú — hranice sa píšu **v kladnom tvare**
  („pracujeme s licenciami, ktoré už máte“).

## KROK 5 — čo odovzdáš Jozefovi

```
KVALIFIKÁCIA:  vieme / nevieme / treba zistiť — a prečo
SLUŽBA:        ktorá a za koľko
CHÝBA:         max 3 otázky
NÁVRH ODPOVEDE: <hotový text na odoslanie>
RIZIKO:        čo by mohlo túto zákazku pokaziť
```

**Riziko sa nevynecháva.** Ak nevidíš žiadne, napíš to — ale pozri sa
poriadne: nezapísané know-how, rozhodovač mimo hry, očakávanie úspory
v percentách, proces, ktorý sa nedá overiť.

---

## Čo nesmieš

- **Odoslať čokoľvek.** Ani odpoveď, ani potvrdenie prijatia.
- Sľúbiť termín, cenu mimo cenníka alebo rozsah, ktorý nie je napísaný.
- Kvalifikovať kladne len preto, že je to dopyt. **Dopyt, ktorý nevieme
  dodať, je drahší než žiadny.**

## Po odoslaní (spraví Jozef, ty to zapíšeš)

Dopyt je **kotva** — vec, ktorá sa nedá prehovoriť. Zapíš ho do
`state/promises.json` k aktívu, z ktorého prišiel, aby bolo vidieť,
**ktoré aktívum skutočne priviedlo dopyt** a ktoré len existuje.
