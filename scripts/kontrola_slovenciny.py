#!/usr/bin/env python3
"""Zachytí preklepy v slovenčine, ktoré vznikli chybným zápisom písmena.

Dvakrát za dva dni sa na živý web dostalo slovo s nesprávnym písmenom, oba
razy z ručne písaného zápisu v zdrojáku: `sprav&eacute;n&aacute;` dalo
„spravéná" namiesto „spravená" a `Za\\u010fanie` dalo „Zaďanie" namiesto
„Zadanie". Ani jedno nenašla kontrola — prvé som uvidel náhodou pri
overovaní niečoho iného, druhé až pri cielenom hľadaní.

Slovník nemáme a nechceme ho sem ťahať. Nepotrebujeme ho: chyba tejto
triedy skoro vždy vyrobí **zriedkavé písmeno** (é, ó, ô, ĺ, ŕ, ä, ď) a
takých slov je na celom slovenskom webe okolo dvesto. Držíme si ich
schválený zoznam a kontrolujeme rozdiel. Nové slovo teda neznamená chybu —
znamená, že ho niekto musí raz prečítať a pridať.

Beží nad **postavenými stránkami**, nie nad zdrojom: chyba vzniká práve pri
prevode zdroja na stránku, takže kontrolovať vstup by ju minulo (to je tá
istá lekcia ako pri obrázkoch, poznatok #78).

Použitie:
    python3 scripts/kontrola_slovenciny.py            # kontrola, nenulový kód pri náleze
    python3 scripts/kontrola_slovenciny.py --schval    # zapíše aktuálny stav ako schválený
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
STRANKY = KOREN / "site" / "sk"
ZOZNAM = KOREN / "data" / "sk_zriedkave_slova.txt"

# Písmená, ktoré sú v slovenčine zriedkavé — chybný zápis ich vyrobí oveľa
# častejšie, než sa vyskytujú správne, takže pomer signálu k šumu je vysoký.
ZRIEDKAVE = "éóôĺŕäď"

SLOVO = re.compile(r"[A-Za-zÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽáäčďéíĺľňóôŕšťúýž]{3,}")


def _text(cesta: Path) -> str:
    s = cesta.read_text(encoding="utf-8", errors="ignore")
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def najdene() -> dict[str, str]:
    """Slovo so zriedkavým písmenom -> súbor, kde sa prvý raz našlo."""
    out: dict[str, str] = {}
    for f in sorted(STRANKY.glob("*.html")):
        for w in SLOVO.findall(_text(f)):
            wl = w.lower()
            if any(p in wl for p in ZRIEDKAVE):
                out.setdefault(wl, f.name)
    return out


def schvalene() -> set[str]:
    if not ZOZNAM.exists():
        return set()
    return {r.strip() for r in ZOZNAM.read_text(encoding="utf-8").splitlines()
            if r.strip() and not r.startswith("#")}


def zapis(slova: dict[str, str]) -> None:
    ZOZNAM.parent.mkdir(parents=True, exist_ok=True)
    hlavicka = (
        "# Slová so zriedkavými písmenami (é ó ô ĺ ŕ ä ď) na slovenských\n"
        "# stránkach, ktoré niekto prečítal a schválil. Kontroluje\n"
        "# scripts/kontrola_slovenciny.py. Nové slovo v zozname nie je chyba —\n"
        "# je to vec, ktorú treba raz prečítať. Chybné slovo sem NEPRIDÁVAJ,\n"
        "# oprav ho v zdroji.\n"
    )
    ZOZNAM.write_text(hlavicka + "\n".join(sorted(slova)) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schval", action="store_true",
                    help="zapíše aktuálny stav ako schválený zoznam")
    args = ap.parse_args()

    if not STRANKY.exists():
        print("[slovencina] site/sk/ neexistuje — najprv postav web")
        return 0

    su = najdene()
    if args.schval:
        zapis(su)
        print(f"[slovencina] schválených {len(su)} slov -> {ZOZNAM.relative_to(KOREN)}")
        return 0

    nove = {w: f for w, f in su.items() if w not in schvalene()}
    if not nove:
        print(f"[slovencina] OK — {len(su)} slov so zriedkavým písmenom, všetky schválené")
        return 0

    print(f"[slovencina] {len(nove)} NESCHVÁLENÝCH slov so zriedkavým písmenom:")
    for w, f in sorted(nove.items()):
        print(f"    {w}   ({f})")
    print("\nPrečítaj ich. Ak sú správne, spusti:")
    print("    python3 scripts/kontrola_slovenciny.py --schval")
    print("Ak nie, oprav ich v zdroji — do zoznamu chybné slovo nepatrí.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
