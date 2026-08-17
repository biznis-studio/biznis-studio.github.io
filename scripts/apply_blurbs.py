#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zapise rucne pisane popisy produktov a sluzieb do databazy.

Popisy su v agents/common.py, ale zobrazuju sa z tabulky `pages`. Pipeline
databazu prepisuje, takze pri kazdom merge sa rucne pisane vety stratia a
vratia sa sablonove - 2026-08-17 sa to stalo dvakrat za hodinu.

Spusta sa po kazdom merge s origin, pred buildom:
    python3 scripts/apply_blurbs.py
"""
from __future__ import annotations
import sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agents.common import BLURB_PODLA_SLUZBY  # noqa: E402

try:
    from agents.common import BLURB_PODLA_PRODUKTU
except ImportError:
    BLURB_PODLA_PRODUKTU = {}


def main() -> int:
    vsetky = {**BLURB_PODLA_SLUZBY, **BLURB_PODLA_PRODUKTU}
    db = sqlite3.connect(ROOT / "db" / "biznis.sqlite3")
    zapisane, chybajuce = 0, []
    for slug, veta in vsetky.items():
        r = db.execute("UPDATE pages SET meta_description=?, seo_enhanced=0 WHERE url=?",
                       (veta, f"products/{slug}.html"))
        if r.rowcount:
            zapisane += r.rowcount
        else:
            chybajuce.append(slug)
    db.commit()
    print(f"[blurbs] zapisanych {zapisane} z {len(vsetky)}")
    if chybajuce:
        print("[blurbs] slug bez stranky v tabulke pages: " + ", ".join(chybajuce))
    # Sablonova veta v databaze = rucne pisany popis sa stratil.
    sablony = ("scoped and quoted", "Skip the blank page", "Ready-to-send scripts for",
               "A clear, repeatable checklist for")
    zvysok = [u for (u, d) in db.execute("SELECT url, meta_description FROM pages")
              if d and any(s in d for s in sablony)]
    if zvysok:
        print(f"[blurbs] POZOR - este {len(zvysok)} stranok ma sablonovu vetu:")
        for u in zvysok:
            print("   ", u)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
