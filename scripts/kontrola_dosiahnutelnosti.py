#!/usr/bin/env python3
"""Každá postavená stránka musí byť dosiahnuteľná z domovskej.

2026-08-30: šesť stránok nemalo ANI JEDEN vnútorný odkaz — `work.html`
(naša dôkazová stránka) a päť stránok služieb. Vyhľadávač objavuje po
odkazoch; stránka, na ktorú nikto neodkazuje, je preň ostrov. Search
Console to o `/sk/praca.html` napísala doslova: *„Referring page: None
detected."*

Obe príčiny boli regresie, nie zámer:

- `work.html` vypadol z navigácie 22. 8. pri prepise, ktorý mal na
  anglickú stranu preniesť tú istú ponuku ako na slovenskú
- päť služieb vynechával `build_catalogue_index()` filtrom
  `format != "service"` — pritom vznikla práve preto, *„aby sa 19 stránok
  nestalo nedostupnými"*, ako hovorí jej vlastný docstring

Ani jednu z nich nemohol chytiť existujúci audit: obe stránky vracajú 200,
majú kanonickú adresu aj titulok a sú v sitemape. Chýbal im len odkaz.

Sitemapa to nenahrádza a v našom prípade zvlášť nie — Google ju k 30. 8.
nikdy úspešne nestiahol.

Použitie:
    python3 scripts/kontrola_dosiahnutelnosti.py [--koren site]
"""
from __future__ import annotations

import argparse
import posixpath
import re
import sys
from collections import deque
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
ODKAZ = re.compile(r'href="([^"]+)"')


def odkazy(koren: Path, rel: str, stranky: set[str]) -> set[str]:
    html = (koren / rel).read_text(encoding="utf-8", errors="ignore")
    von: set[str] = set()
    for m in ODKAZ.finditer(html):
        h = m.group(1)
        if h.startswith(("http", "mailto:", "#", "//", "tel:", "data:")):
            continue
        ciel = posixpath.normpath(posixpath.join(
            posixpath.dirname(rel), h.split("#")[0].split("?")[0]))
        if ciel.endswith("/"):
            ciel += "index.html"
        if ciel in stranky:
            von.add(ciel)
    return von


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--koren", default="site")
    a = ap.parse_args()
    koren = KOREN / a.koren
    if not koren.exists():
        print(f"[dosiahnutelnost] {a.koren}/ neexistuje — najprv postav web")
        return 0

    stranky = {p.relative_to(koren).as_posix() for p in koren.rglob("*.html")}
    if "index.html" not in stranky:
        print("[dosiahnutelnost] chýba index.html — nie je odkiaľ začať")
        return 1

    videne, front = {"index.html"}, deque(["index.html"])
    while front:
        for c in odkazy(koren, front.popleft(), stranky):
            if c not in videne:
                videne.add(c)
                front.append(c)

    ostrovy = sorted(stranky - videne)
    if not ostrovy:
        print(f"[dosiahnutelnost] OK — všetkých {len(stranky)} stránok "
              f"je dosiahnuteľných z domovskej")
        return 0

    print(f"[dosiahnutelnost] {len(ostrovy)} stránok NEDOSIAHNUTEĽNÝCH z domovskej:")
    for s in ostrovy:
        print(f"    {s}")
    print("\nVyhľadávač objavuje po odkazoch. Na tieto stránky neodkazuje nič,")
    print("takže sú preň ostrovy — aj keď vracajú 200 a sú v sitemape.")
    print("Buď na ne odkáž (navigácia, katalóg, súvisiaca stránka), alebo ich nestav.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
