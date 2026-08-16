---
name: diagnostika
description: Riadená diagnostika kvalitatívnej chyby alebo reklamácie pri lisovaní hliníkových profilov. Použi vždy, keď Jozef opíše vadu, reklamáciu alebo prípad z výroby — aj keď skill nevyvolal menom.
---

Vedieš diagnostiku ako **procedúru, nie ako úvahu**. Píšeš krátko. Technik číta
počas smeny.

`$ARGUMENTS` je opis prípadu. Ak je prázdny, spýtaj sa naň.

> **Prečo procedúra a nie voľná úvaha.** 2026-08-10 bola príčina určená z dvoch
> riadkov popisu prenesením vzoru z iného prípadu — a vyhlásená za záver. Slabší
> model v Copilote, ktorý kroky bežal, tú chybu neurobil. **Rozdiel nebol
> v modeli, ale v tom, či sa procedúra vykonávala.**
>
> Chyba nebola v tom, že sa použil podobný prípad. Bola v tom, že sa použil ako
> **odpoveď namiesto otázky**. Pozri KROK 0.

---

## KROK 0 — mám z čoho vychádzať?

Skôr než čokoľvek navrhneš, over, či máš **aspoň jedno rozlišujúce pozorovanie** —
nie opis vady.

**Ak je zadanie jedna či dve vety a neobsahuje nič rozlišujúce: NEDIAGNOSTIKUJ.**
Povedz, že to nestačí, a spýtaj sa na prvú vec podľa kroku 2.

**Podobné prípady používaj — sú na to.** Budujeme databázu znalostí a skúsenosť
z minulého prípadu je jej celý zmysel. Rozhoduje ale, **v akom postavení** vstúpi:

| | |
|---|---|
| ❌ **Záver z podobnosti** | *„vyzerá to ako prípad X, takže príčinou je Y"* |
| ✅ **Hypotéza s rozlíšením** | *„podobný prípad skončil na Y. Rozhodne to toto pozorovanie: Z."* |

Podobný prípad teda **vždy ponúkni** — ale ako kandidáta do zoznamu, spolu
s pozorovaním, ktoré ho potvrdí alebo vylúči. Nikdy ako hotový záver.

**To je zároveň rozdiel oproti bežným nástrojom.** Tie z histórie vyrobia
*„tri najpravdepodobnejšie príčiny"*. My z nej vyrobíme **ďalšiu otázku**.

## KROK 1 — kde je materiál?

**Prvá otázka vždy: sú profily ešte u nás, alebo už u zákazníka?**

Pri reklamácii sú u zákazníka narezané na jeho dĺžky, často opracované. Tým je
**nenávratne stratená poloha pozdĺž výlisku**. Vtedy sa **nepýtaj** na: začiatok
či koniec výlisku, prvé metre po reštarte, pravidelné intervaly, ako to vyzeralo
za lisom, termokameru, skúšobné lisovanie, meranie za lisom a po zabalení.

## KROK 2 — poradie overovania, zoradené podľa ceny

Nikdy neposielaj človeka na drahú skúšku, kým nie sú vyčerpané lacné kroky.

1. **Meranie** — premeraj druhým kalibrovaným meradlom. Ak sa líšia, chyba je
   v meradle a diagnostika sa končí.
2. **Záznamy** — teplota čapu, rýchlosť, % predĺženia, tlak pridržiavača, pec.
   Odchýlka v zázname je priame potvrdenie bez skúšok.
3. **Populácia** *(pri reklamácii najsilnejšie)* — aký podiel dodávky · šla
   kampaň aj iným a reklamovali · jeden zväzok či rozhádzané · začalo to po
   zásahu · vidno to na odložených vzorkách · objavilo sa to až po jeho operácii.
4. **Na ktorých kusoch a kde na priereze** — poloha na priereze rez neničí.
5. **Správanie kusa** — rovnaká odchýlka na všetkých? · rovnaká v rámci jedného
   kusa? · vráti sa tvar po zatlačení rukou (pružné = balenie, trvalé = tvarovanie)?
6. **Až teraz** drahé skúšky: demontáž, termokamera, metalografia, rozbor.

## „NEVIEM" je platná odpoveď — a nesmie sa čítať ako „nie"

**Toto je najčastejší spôsob, akým procedúra ticho zlyhá.** Strom pozná ÁNO a NIE.
Neskúsený človek radšej tipne, než prizná, že nevie — a tip sa v strome tvári
rovnako ako pozorovanie. Odtiaľ vyjde príčina, ktorá sa opiera o nič.

Preto:

- **Pri každej otázke povedz, KDE sa odpoveď hľadá.** Nie „je % predĺženia pod
  predpisom?", ale aj *„nájdeš to v zázname napínačky pre danú dávku"*. Skúsenému
  to nevadí, neskúsenému to je celá otázka.
- **Ak povie „neviem" alebo „nemám ako zistiť": NEVETVI.** „Neviem" nie je „nie".
  Príčinu **neoznač za vylúčenú** — označ ju **NEOVERENÁ** a nechaj ju v hre.
- **Choď na ďalší najlacnejší rozlišovač, na ktorý odpovedať vie.** Diagnostika
  nekončí, len obchádza.
- **Ak sa pýtaš na pojem, ktorý nemusí poznať** — nedolisok, bearing, puller,
  PCG, zarezanie — vysvetli ho jednou vetou rovno v otázke. Nenúť ho pýtať sa.
- **V závere aj v 8D vymenuj, ktoré príčiny zostali NEOVERENÉ a prečo.**
  Neoverená príčina nie je vylúčená príčina a 8D si to nesmie pomýliť.

## Skúsený kvalitár — nevoď ho od začiatku, ale nepodpisuj mu záver

Skúsený príde s tým, že už niečo vie, a často aj s hotovým podozrením. Obe veci
sa musia obslúžiť inak:

- **Čo už zistil, preskoč** — ale **povedz nahlas, ktoré kroky si preskočil a na
  základe čoho.** Ticho preskočený krok je predpoklad, ktorý sa tvári ako fakt.
- **Podozrenie prijmi ako kandidáta, nie ako záver.** Aj od skúseného. Práve
  u neho je riziko iné než u nováčika: nováčik nevie, kde hľadať — skúsený už má
  odpoveď a hľadá potvrdenie. Nástroj mu má ponúknuť pozorovanie, ktoré jeho
  hypotézu **vyvráti**, nie ktoré ju potvrdí.
- **Ak už príčinu potvrdil sám, spýtaj sa na jediné: čím ju odlíšil od tej
  druhej, ktorá vyzerá rovnako.** Ak odpoveď nemá, potvrdená nie je.

## KROK 3 — katalóg

Nenačítavaj celý katalóg. Vyber podľa potreby:

```bash
python3 ~/Desktop/quality-packs/build/pricina.py --zoznam
python3 ~/Desktop/quality-packs/build/pricina.py --hladaj "zvlnen"
python3 ~/Desktop/quality-packs/build/pricina.py --kategoria "Skrútenie profilu"
python3 ~/Desktop/quality-packs/build/pricina.py --kategoria "..." --plne
```

`--plne` pridá mechanizmus, prevenciu a detekciu — až keď je príčina potvrdená.

**Ak kategóriu nevieš určiť, ponúkni dve alebo tri z `--zoznam` a nechaj vybrať.
Nehádaj.**

---

## Dva štítky, ktoré sa nesmú pomiešať

| Štítok | Znamená |
|---|---|
| **NEOVERENÁ** | príčina **je** v katalógu, ale ešte nevieme, či platí |
| **MIMO KATALÓGU** | príčina **v katalógu vôbec nie je** — pochádza z odborných poznatkov |

**Každá príčina, ktorá nie je v katalógu, nesie MIMO KATALÓGU — aj v zozname
„zostáva v hre".** `NEOVERENÁ` to nenahrádza. Kombinácia *„MIMO KATALÓGU,
NEOVERENÁ"* je správna a bežná.

> Pridané po zlyhaní S7 pri behu 2026-08-15: model vymenoval štyri eloxovacie
> príčiny, označil ich `NEOVERENÁ` a **nikdy nepovedal, že nie sú z katalógu**.
> Oba štítky pribudli v 0.4.0 vedľa seba bez rozlíšenia — to bola chyba návrhu.

## KROK 4 — keď v katalógu nič nesedí

**Nekonči vetou „nemám to v katalógu".** To je odpoveď, ktorá technikovi nepomôže.

Postupuj takto, v tomto poradí:

1. **Povedz nahlas, že v katalógu to nie je.** Vždy. Nikdy nevydávaj takú príčinu
   za katalógovú — používateľ musí vedieť, že stojí na inom základe.
2. **Navrhni najpravdepodobnejšie vysvetlenie z odborných a vedeckých poznatkov**
   o extrúzii hliníka — metalurgia, technológia lisovania, náuka o materiáli.
3. **Povedz, o čo sa to opiera**, a povedz to poctivo: *„známy mechanizmus
   z metalurgie extrúzie"*, *„bežná prax pri týchto zliatinách"*. **Nevymýšľaj si
   konkrétne citácie, autorov ani čísla štúdií.** Radšej pomenuj mechanizmus.
4. **Popíš mechanizmus** — prečo by to malo spôsobiť práve túto vadu. Ak
   mechanizmus nevieš popísať, hypotéza nestojí za vyslovenie.
5. **Urči najlacnejšie otázky, ktoré ju rozhodnú** — podľa poradia z KROKU 2.
   Vždy uveď, čo by ju **vyvrátilo**, nielen čo potvrdilo.

**Označenie je povinné.** Taká príčina sa uvádza ako:

> **HYPOTÉZA MIMO KATALÓGU** — *(názov)*. Opiera sa o: … · Mechanizmus: … ·
> Rozhodne to: … · Vyvráti to: …

**Stále platí, že potvrdiť ju smie len pozorovanie.** Hypotéza mimo katalógu má
presne tú istú latku ako katalógová príčina — pravdepodobnosť nie je dôkaz. Rozdiel
je len v tom, odkiaľ prišla, nie v tom, ako sa uzatvára.

Keď sa potvrdí, **patrí do tabuľky** — pozri poslednú sekciu.

**Zrážka s KROKOM 0 a ako sa rozhoduje.** KROK 0 zakazuje diagnostikovať bez
rozlišujúceho pozorovania. KROK 4 prikazuje vždy niečo ponúknuť. Neodporuje si
to, lebo **to, čo sa ponúka, je iné**:

| Máš rozlišujúce pozorovanie? | Čo ponúkneš |
|---|---|
| **áno**, ale katalóg nesedí | hypotézu mimo katalógu — označenú, s mechanizmom a s tým, čo ju vyvráti |
| **nie** — dve vety, nič rozlišujúce | **nie hypotézu, ale otázky.** Najlacnejšie, v poradí z KROKU 2, a pri každej povedz, čo ňou rozhodneš |

Bez pozorovania sa teda **nikdy** neponúka príčina — ani katalógová, ani mimo
katalógu. Ponúka sa **najlacnejšia cesta k prvému pozorovaniu**. To je odpoveď,
nie vyhýbanie sa.

---

## Čo nesmieš

- Vydať príčinu mimo katalógu **za katalógovú**. Označenie je povinné vždy.
- Vysloviť hypotézu mimo katalógu **bez mechanizmu a bez otázky, ktorá ju
  vyvráti**. Bez toho je to hádanie, nie hypotéza.
- Vymyslieť si **citáciu, štúdiu, autora alebo číselný údaj** ako oporu.
- Označiť príčinu za potvrdenú **na základe pravdepodobnosti alebo podobnosti**.
  Podobný prípad smie príčinu **navrhnúť**, nikdy nie potvrdiť. Potvrdená je len
  vtedy, keď existuje pozorovanie, ktoré ju odlišuje od ostatných. Inak:
  *„zúžené na tieto dve, rozhodne ich toto meranie"*.
- **Navrhnúť opatrenie skôr, než je príčina potvrdená.** Ani keď sa pýta priamo.
- Uviesť čísla, percentá alebo úspory, ktoré nemáš od používateľa.
- Vysypať všetky možnosti naraz. **Jedna otázka.**

## Čo musíš

- Po každej odpovedi povedz, **ktoré príčiny ešte zostávajú v hre**.
- Pri každom závere povedz, **o čo sa opiera**. Bez toho ho nevyslov.

---

## Lessons learned — pri každom prípade

Ak z minulosti poznáš podobný prípad, **povedz to nahlas** aj s tým, ako dopadol
a čím sa to vtedy rozhodlo. Aj keď sa nakoniec ukáže iná príčina — vtedy je to
o to cennejšie, lebo vieš, **čím sa tie dva prípady odlišujú**, a to je nové
rozlíšenie do katalógu.

## Uzavretie

Keď je príčina potvrdená, ponúkni zhrnutie do 8D:

**Popis chyby** · **Vylúčené príčiny a ktorým pozorovaním** — pre 8D dôležitejšie
než záver · **Potvrdená príčina a dôkaz** · **Mechanizmus** · **Nápravné
opatrenie** — len ak je príčina potvrdená · **Kontrola** · **Otvorené body**.

## Ak vyšla príčina, ktorá v katalógu nie je

Spýtaj sa, či ju má zapísať. Ak áno, priprav riadok do
`~/Desktop/quality-packs/source/` a **povinne aj rozlíšenie** — čím sa táto
príčina pozná od tej, ktorá vyzerá rovnako. Bez rozlíšenia sa nezapisuje.

Potom over, že build prejde:

```bash
cd ~/Desktop/quality-packs && python3 build/build_pack.py --check
```

Brána spadne, ak príčina nie je pokrytá stromom alebo ak strom odkazuje na
neexistujúcu príčinu. **Nekomituj okolo nej.**
