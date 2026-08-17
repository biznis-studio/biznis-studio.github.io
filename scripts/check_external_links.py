#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Overi, ze externe odkazy na webe este ziju.

Existuje preto, ze crawl audit zamerne kontroluje len to, co ovladame -
externe odkazy su mimo neho. 2026-08-17 sa takto na web dostal zdroj, ktory
vracal 404: URL prisla z vyhladavania a nikto ju neotvoril. Citovat mrtvy
zdroj je horsie nez necitovat nic.

    python3 scripts/check_external_links.py            # clanky a stranky
    python3 scripts/check_external_links.py --vsetko   # aj news a produkty

Exit 1 = aspon jeden odkaz je mrtvy. 403/405 od anti-bot ochrany sa
neratuju ako chyba - overuju sa este raz cez GET.
"""
from __future__ import annotations
import re, ssl, sys, urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
# Stranky, ktore agreguju cudzie titulky, sa nekontroluju: odkazy tam vznikaju
# automaticky z RSS a ich zivotnost neovladame.
PRESKOCIT = {"news/index.html"}


def stav(url: str) -> int | str:
    ctx = ssl.create_default_context()
    for metoda in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, headers=UA, method=metoda)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
                if r.status == 200:
                    return 200
                posledny = r.status
        except Exception as e:
            posledny = getattr(e, "code", None) or type(e).__name__
    return posledny


def main() -> int:
    vsetko = "--vsetko" in sys.argv
    odkazy: dict[str, set[str]] = defaultdict(set)
    for f in sorted((ROOT / "site").rglob("*.html")):
        rel = str(f.relative_to(ROOT / "site"))
        if not vsetko and rel in PRESKOCIT:
            continue
        for u in re.findall(r'href="(https?://[^"]+)"', f.read_text(encoding="utf-8", errors="ignore")):
            if "biznis-studio.github.io" in u:
                continue
            odkazy[u].add(rel)

    zle, neoverene = [], []
    for u in sorted(odkazy):
        k = stav(u)
        if k == 200:
            continue
        # 403/405 vracia anti-bot ochrana aj na zive stranky (Pexels, niektore
        # vladne weby). Nie je to dokaz, ze odkaz je mrtvy - je to dokaz, ze
        # sme ho neoverili. Hlasi sa zvlast a nezhadzuje kontrolu, inak by
        # zvonila nadarmo a zacala by sa ignorovat.
        if k in (401, 403, 405, 406, 429):
            neoverene.append((u, k))
            continue
        zle.append((u, k, sorted(odkazy[u])))
        print(f"  MRTVY {k}  {u}")
        for kde in sorted(odkazy[u]):
            print(f"          na {kde}")
    if neoverene:
        print("\n  neoverene (anti-bot ochrana, nie dokaz mrtveho odkazu):")
        for u, k in neoverene:
            print(f"    {k}  {u}")
    print(f"\noverenych: {len(odkazy)} · mrtvych: {len(zle)} · neoverenych: {len(neoverene)}")
    return 1 if zle else 0


if __name__ == "__main__":
    raise SystemExit(main())
