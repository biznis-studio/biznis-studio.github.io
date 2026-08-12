---
name: diagnostika
description: Riadená diagnostika kvalitatívnej chyby alebo reklamácie pri lisovaní hliníkových profilov. Použi vždy, keď Jozef opíše vadu, reklamáciu alebo prípad z výroby — aj keď skill nevyvolal menom.
---

Vedieš diagnostiku ako **procedúru, nie ako úvahu**. Píšeš krátko. Technik číta
počas smeny.

`$ARGUMENTS` je opis prípadu. Ak je prázdny, spýtaj sa naň.

> **Toto pravidlo existuje kvôli konkrétnemu zlyhaniu.** 2026-08-10 bola príčina
> určená z dvoch riadkov popisu prenesením vzoru z iného prípadu — v písanej
> úvahe, mimo procedúry. Slabší model v Copilote, ktorý procedúru bežal, tú chybu
> neurobil. **Rozdiel nebol v modeli, ale v tom, či sa bežali kroky.**

---

## KROK 0 — mám z čoho vychádzať?

Skôr než čokoľvek navrhneš, over, či máš **aspoň jedno rozlišujúce pozorovanie** —
nie opis vady.

**Ak je zadanie jedna či dve vety a neobsahuje nič rozlišujúce: NEDIAGNOSTIKUJ.**
Povedz, že to nestačí, a spýtaj sa na prvú vec podľa kroku 2.

**Nikdy nepreberaj vysvetlenie z iného prípadu preto, že sa naň podobá.**
Podobnosť nie je dôkaz. Ak ti niečo pripomína iný prípad, povedz to ako otázku.

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

## Čo nesmieš

- Uviesť príčinu, ktorá **nie je v katalógu**. Ak nič nesedí, povedz to a navrhni,
  aké pozorovanie by rozhodlo. Ak sa potvrdí, patrí to do tabuľky — pozri nižšie.
- Označiť príčinu za potvrdenú **na základe pravdepodobnosti alebo podobnosti**.
  Potvrdená je len vtedy, keď existuje pozorovanie, ktoré ju odlišuje od
  ostatných. Inak: *„zúžené na tieto dve, rozhodne ich toto meranie"*.
- **Navrhnúť opatrenie skôr, než je príčina potvrdená.** Ani keď sa pýta priamo.
- Uviesť čísla, percentá alebo úspory, ktoré nemáš od používateľa.
- Vysypať všetky možnosti naraz. **Jedna otázka.**

## Čo musíš

- Po každej odpovedi povedz, **ktoré príčiny ešte zostávajú v hre**.
- Pri každom závere povedz, **o čo sa opiera**. Bez toho ho nevyslov.

---

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
