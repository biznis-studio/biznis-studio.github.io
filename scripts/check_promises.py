#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ktore aktiva su po termine a nesplnili svoj slub.

Existuje preto, ze system vedel len povysovat. Clanok, stranka ani sluzba sa
doteraz nedali zabit - nebolo podla coho. Toto je prvy mechanizmus, ktory vie
povedat "toto stiahni".

    python3 scripts/check_promises.py           # co je po termine
    python3 scripts/check_promises.py --vsetko  # cely register

Exit 1 = nieco caka na ROZHODNUTIE CLOVEKA. Nie je to chyba, je to fronta.
"""
from __future__ import annotations
import json, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "state" / "promises.json"


def main() -> int:
    if not REG.exists():
        print("register neexistuje:", REG)
        return 0
    data = json.loads(REG.read_text(encoding="utf-8"))
    dnes = date.today()
    vsetko = "--vsetko" in sys.argv

    # Najprv validacia. Aktivum bez slubu je diera v systeme - nedalo by sa
    # nikdy zabit - a nesmie zhodit kontrolu ostatnych.
    chybne = [a.get("id", "?") for a in data["aktiva"]
              if not a.get("slub") or not a.get("datum_kontroly")]
    if chybne:
        print("CHYBA - aktivum bez slubu alebo datumu kontroly: " + ", ".join(chybne))
        print("Aktivum, ktore sa neda ohodnotit, sa neda ani zabit. Doplnit alebo zmazat.\n")

    po_termine, blizi_sa = [], []
    for a in data["aktiva"]:
        if a.get("stav") == "zabite" or a.get("id") in chybne:
            continue
        d = date.fromisoformat(a["datum_kontroly"])
        dni = (d - dnes).days
        if dni < 0:
            po_termine.append((a, -dni))
        elif dni <= 14:
            blizi_sa.append((a, dni))

    if vsetko:
        print(f"# Register aktiv ({len(data['aktiva'])})\n")
        for a in data["aktiva"]:
            print(f"[{a['stav']:>9}] {a['id']:<22} kontrola {a['datum_kontroly']}")
            print(f"            slub: {a['slub']}")
        print()

    if po_termine:
        print(f"## PO TERMINE - caka na rozhodnutie ({len(po_termine)})\n")
        for a, dni in sorted(po_termine, key=lambda x: -x[1]):
            print(f"  {a['id']} - {dni} dni po termine")
            print(f"    co:   {a['co']}")
            print(f"    slub: {a['slub']}")
            print(f"    -> splnil? ANO = novy datum_kontroly. NIE = stav 'zabite'.\n")

    if blizi_sa:
        print(f"## Blizi sa ({len(blizi_sa)})\n")
        for a, dni in sorted(blizi_sa, key=lambda x: x[1]):
            print(f"  {a['id']} - o {dni} dni ({a['datum_kontroly']})")
        print()

    if not po_termine and not blizi_sa:
        print("Ziadne aktivum nie je po termine ani sa neblizi.")

    return 1 if (po_termine or chybne) else 0


if __name__ == "__main__":
    raise SystemExit(main())
