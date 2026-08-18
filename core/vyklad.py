"""Zápis výkladu z artefaktu — úsudok mimo, zápis vnútri.

Výklad je jediný krok, ktorý potrebuje úsudok, a zároveň ten, ktorý zapíše
naraz najviac stavu: pre 25 položiek až 25 riadkov výkladu a k tomu poznatky.
Doteraz bežal mimo bezpečnostnej vrstvy — a presne on 2026-08-17 spadol
v polovici a nechal za sebou duplikáty.

Vzor je preto rozdelený:

    ÚSUDOK  ->  ARTEFAKT (JSON)  ->  OVERENIE  ->  ATOMICKÝ ZÁPIS

Model ani agent nezapisuje do stavu priamo. Vytvorí artefakt, ten sa celý
overí, a až potom sa zapíše v jedinej transakcii vnútri uzla. Chybný artefakt
neprejde overením a nezapíše sa z neho ani riadok — polovičný výklad je horší
než žiadny, lebo vyzerá ako hotový.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from core import evolution as ev


class ChybnyArtefakt(Exception):
    """Artefakt neprešiel overením. Nezapísalo sa nič."""


POVINNE = ("signal_id", "rozhodnutie", "duvod")


def over(artefakt: dict, conn: sqlite3.Connection) -> list[dict]:
    """Overí celý artefakt PRED zápisom. Vracia položky, alebo vyhodí výnimku.

    Overuje sa všetko naraz a až potom sa zapisuje. Overovať za pochodu by
    znamenalo, že chyba v pätnástej položke nechá zapísaných štrnásť.
    """
    polozky = artefakt.get("polozky")
    if not isinstance(polozky, list) or not polozky:
        raise ChybnyArtefakt("artefakt nemá zoznam `polozky`")

    znama_signaly = {r[0] for r in conn.execute(
        "SELECT id FROM signals_raw WHERE source LIKE 'frontier:%'")}
    videne: set[int] = set()

    for i, p in enumerate(polozky):
        kde = f"položka {i}"
        chybajuce = [k for k in POVINNE if not str(p.get(k, "")).strip()]
        if chybajuce:
            raise ChybnyArtefakt(f"{kde}: chýba {', '.join(chybajuce)}")
        if p["rozhodnutie"] not in ("ZAPISANE", "ZAHODENE"):
            raise ChybnyArtefakt(
                f"{kde}: rozhodnutie {p['rozhodnutie']!r} nie je ZAPISANE ani ZAHODENE")
        try:
            sid = int(p["signal_id"])
        except (TypeError, ValueError):
            raise ChybnyArtefakt(f"{kde}: signal_id nie je číslo")
        if sid not in znama_signaly:
            raise ChybnyArtefakt(f"{kde}: signál {sid} vo fronte neexistuje")
        if sid in videne:
            raise ChybnyArtefakt(f"{kde}: signál {sid} je v artefakte dvakrát")
        videne.add(sid)

        if p["rozhodnutie"] == "ZAPISANE":
            pozn = p.get("poznatok")
            if not isinstance(pozn, dict):
                raise ChybnyArtefakt(f"{kde}: ZAPISANE bez objektu `poznatok`")
            for kluc in ("tvrdenie", "typ_zdroja", "dosah"):
                if not str(pozn.get(kluc, "")).strip():
                    raise ChybnyArtefakt(f"{kde}: poznatok nemá `{kluc}`")
            if pozn["typ_zdroja"] not in ev.PLATNOST_DNI:
                raise ChybnyArtefakt(
                    f"{kde}: neznámy typ zdroja {pozn['typ_zdroja']!r}")
    return polozky


def zapis(conn: sqlite3.Connection, artefakt: dict) -> dict:
    """Overí a zapíše. Volá sa VNÚTRI uzla — transakciu vlastní uzol.

    `conn` má počas uzla potlačený `commit()`, takže funkcie z `evolution.py`
    tu nemôžu transakciu predčasne uzavrieť.
    """
    polozky = over(artefakt, conn)

    url_signalu = {r["id"]: (r["url"], r["source"]) for r in conn.execute(
        "SELECT id, url, source FROM signals_raw WHERE source LIKE 'frontier:%'")}

    zapisane = zahodene = 0
    for p in polozky:
        sid = int(p["signal_id"])
        url, zdroj = url_signalu[sid]
        pid = None
        if p["rozhodnutie"] == "ZAPISANE":
            pozn = p["poznatok"]
            if not url:
                raise ChybnyArtefakt(
                    f"signál {sid} nemá URL — poznatok bez otvoriteľného zdroja "
                    f"sa nezapisuje")
            pid = ev.zapis_poznatok(
                conn, tvrdenie=pozn["tvrdenie"],
                druh=pozn.get("druh", "POZOROVANIE"), zdroj=url,
                typ_zdroja=pozn["typ_zdroja"], dosah=pozn["dosah"],
                dokaz=pozn.get("dokaz"))
            zapisane += 1
        else:
            zahodene += 1
        ev.zapis_vyklad(conn, signal_id=sid, zdroj=zdroj,
                        rozhodnutie=p["rozhodnutie"], duvod=p["duvod"],
                        poznatok_id=pid)
    return {"zapisane": zapisane, "zahodene": zahodene, "spolu": len(polozky)}


def nacitaj(cesta: Path) -> dict:
    try:
        return json.loads(cesta.read_text())
    except (OSError, json.JSONDecodeError) as chyba:
        raise ChybnyArtefakt(f"artefakt {cesta} sa nedá prečítať: {chyba}")
