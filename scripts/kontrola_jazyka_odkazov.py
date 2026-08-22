#!/usr/bin/env python3
"""Odkaz v próze nesmie preniesť čitateľa do iného jazyka.

2026-08-22: prepis anglickej domovskej podľa slovenskej priniesol vetu
„You can do this part yourself with our free pre-deployment record" aj
s odkazom — a ten viedol na `sk/zapis-pred-nasadenim-ai.html`. Anglický
čitateľ klikol na anglický sľub a dostal slovenský formulár.

Nechytila to žiadna existujúca brána a chytiť nemohla: cieľ vracia 200,
je v sitemape, má kanonickú adresu. Z pohľadu prehľadávača je všetko
v poriadku. Chybný je len jazyk, a ten nekontroloval nikto.

Prepínač jazyka je, prirodzene, výnimka. Rozlišujeme podľa umiestnenia:
odkaz v `nav`, `header`, `footer` alebo s atribútom `hreflang` je
navigácia a smie prekročiť jazyk. Odkaz vo vete nesmie.

Použitie:
    python3 scripts/kontrola_jazyka_odkazov.py [--korene site]
"""
from __future__ import annotations

import argparse
import posixpath
import re
import sys
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent

# odkaz aj s tým, čo mu predchádza, aby sa dal určiť rodičovský blok
ODKAZ = re.compile(r"<a\s[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", re.S | re.I)
NAVIGACIA = re.compile(r"<(nav|header|footer)\b", re.I)
KONIEC_NAV = re.compile(r"</(nav|header|footer)>", re.I)


def jazyk(cesta: str) -> str:
    """Jazyk stránky podľa jej umiestnenia v strome webu."""
    return "sk" if cesta.startswith("sk/") or "/sk/" in cesta else "en"


def v_navigacii(html: str, poloha: int) -> bool:
    """Je odkaz na tejto pozícii vnútri nav/header/footer?"""
    pred = html[:poloha]
    otvorene = len(NAVIGACIA.findall(pred))
    zatvorene = len(KONIEC_NAV.findall(pred))
    return otvorene > zatvorene


def preskumaj(koren: Path) -> list[str]:
    nalezy: list[str] = []
    for f in sorted(koren.rglob("*.html")):
        rel = f.relative_to(koren).as_posix()
        moj = jazyk(rel)
        html = f.read_text(encoding="utf-8", errors="ignore")
        for m in ODKAZ.finditer(html):
            href, text = m.group(1), m.group(2)
            if href.startswith(("http", "mailto:", "#", "//")):
                continue
            if "hreflang" in html[m.start():m.start() + 200].split(">")[0]:
                continue
            if v_navigacii(html, m.start()):
                continue
            # cieľ vyhodnotíme voči koreňu webu, nie voči stránke.
            # normpath, nie ručné nahradzovanie: prvá verzia mala
            # .replace("./", "") a to zožralo bodku aj z „../", takže
            # z „sk/../tools/" vzniklo „sk/.tools/" a cieľ sa javil ako
            # slovenský. Brána tak videla len jeden zo dvoch smerov.
            ciel = posixpath.normpath(posixpath.join(posixpath.dirname(rel),
                                                     href.split("#")[0].split("?")[0]))
            if jazyk(ciel) != moj:
                popis = re.sub(r"<[^>]+>", "", text).strip()[:60]
                nalezy.append(f"{rel} ({moj}) -> {ciel} ({jazyk(ciel)})  „{popis}\"")
    return nalezy


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--korene", default="site")
    args = ap.parse_args()

    koren = KOREN / args.korene
    if not koren.exists():
        print(f"[jazyk-odkazov] {args.korene}/ neexistuje — najprv postav web")
        return 0

    nalezy = preskumaj(koren)
    if not nalezy:
        print("[jazyk-odkazov] OK — žiadny odkaz v próze neprekračuje jazyk")
        return 0

    print(f"[jazyk-odkazov] {len(nalezy)} odkazov v próze vedie do iného jazyka:")
    for n in nalezy:
        print(f"    {n}")
    print("\nČitateľ klikne na sľub vo svojom jazyku a dostane stránku v inom.")
    print("Buď postav cieľ v jazyku stránky, alebo odkaz odstráň.")
    print("Prepínač jazyka patrí do nav/header/footer alebo dostane hreflang.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
