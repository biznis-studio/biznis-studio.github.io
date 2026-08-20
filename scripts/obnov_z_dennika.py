#!/usr/bin/env python3
"""Vráti do databázy zápisy, ktoré z nej zmizli pri rebase.

Databáza je binárny súbor a git ju zlúčiť nevie. Keď pipeline commitne svoju
verziu súčasne so mnou, pri rebase vyhrá jedna a druhá sa stratí. Preto ide
každý zápis poznatku a rozhodnutia aj do `state/evolucia.jsonl`, ktorý sa
zlučuje po riadkoch.

Tento skript denník prehrá. Zápisy sú idempotentné — `zapis_poznatok` vráti
existujúce id pri rovnakom zdroji a tvrdení — takže prehratie nič
nezduplikuje a dá sa spustiť koľkokrát treba.

    python3 scripts/obnov_z_dennika.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.db import get_connection
from core import evolution as ev


def main() -> int:
    conn = get_connection()
    ev.priprav(conn)
    pred_p = conn.execute("SELECT COUNT(*) FROM poznatky").fetchone()[0]
    pred_r = conn.execute("SELECT COUNT(*) FROM rozhodnutia").fetchone()[0]

    zaznamov = 0
    def _id_podla_tvrdenia(conn, tvrdenie):
        """Väzba nahradenia sa prehráva podľa tvrdenia, nie podľa ID.

        Pri obnove sa ID prideľujú nanovo, takže číslo z denníka ukazuje inam.
        Staršie záznamy `nahradza_tvrdenie` nemajú — tam sa väzba stratí a to
        je lepšie než ju obnoviť nesprávne.
        """
        if not tvrdenie:
            return None
        r = conn.execute("SELECT id FROM poznatky WHERE tvrdenie = ?",
                         (tvrdenie,)).fetchone()
        return r[0] if r else None

    for z in ev.nacitaj_dennik():
        zaznamov += 1
        if z["typ"] == "poznatok":
            ev.zapis_poznatok(
                conn, tvrdenie=z["tvrdenie"], druh=z["druh"], zdroj=z["zdroj"],
                typ_zdroja=z["typ_zdroja"], zdroj_datum=z.get("zdroj_datum"),
                dokaz=z.get("dokaz"), dosah=z.get("dosah"),
                nahradza=_id_podla_tvrdenia(conn, z.get("nahradza_tvrdenie")),
                obnova=True)
            # Stav nesie len základový snímok. Zmeny stavu robené mimo
            # zapis_poznatok (oznac_rozpor, ručný zásah) sa do denníka nikdy
            # nedostali, takže bez tohto by sa štyri prekonané poznatky
            # vrátili ako NOVY (zmerané 2026-08-19).
            if z.get("stav") and z["stav"] != "NOVY":
                conn.execute("UPDATE poznatky SET stav=? WHERE tvrdenie=?",
                             (z["stav"], z["tvrdenie"]))
                conn.commit()
        elif z["typ"] == "rozhodnutie":
            if conn.execute("SELECT 1 FROM rozhodnutia WHERE co=?", (z["co"],)).fetchone():
                continue
            ev.zapis_rozhodnutie(
                conn, co=z["co"], preco=z["preco"],
                ocakavany_ucinok=z["ocakavany_ucinok"], vratenie=z["vratenie"],
                datum_revizie=z["datum_revizie"], vrstva=z["vrstva"],
                zamietnute=z.get("zamietnute"), autorita=z.get("autorita", "stroj"))
        elif z["typ"] == "dvojica":
            # Posúdená dvojica je výsledok úsudku, nie odvodený údaj —
            # bez prehratia by sa po strate databázy vrátila do fronty.
            ev.zamietni_dvojicu(conn, a_tvrdenie=z["a_tvrdenie"],
                                b_tvrdenie=z["b_tvrdenie"], dovod=z.get("dovod", ""))
        elif z["typ"] == "dosah":
            # Úprava, nie vznik. Musí sa prehrať PO poznatku, ktorý mení —
            # denník je chronologický, takže poradie sedí samo.
            try:
                ev.dopln_dosah(conn, tvrdenie_zaciatok=z["tvrdenie_zaciatok"],
                               dosah=z["dosah"])
            except ev.ChybaEvolucie:
                # Poznatok medzitým nahradený alebo zrušený — úprava sa zahodí,
                # ale beh nepadne: denník je archív, nie príkaz.
                pass

    po_p = conn.execute("SELECT COUNT(*) FROM poznatky").fetchone()[0]
    po_r = conn.execute("SELECT COUNT(*) FROM rozhodnutia").fetchone()[0]
    conn.close()

    print(f"[obnova] denník: {zaznamov} záznamov")
    print(f"[obnova] poznatky {pred_p} -> {po_p}   rozhodnutia {pred_r} -> {po_r}")
    if po_p == pred_p and po_r == pred_r:
        print("[obnova] nič nechýbalo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
