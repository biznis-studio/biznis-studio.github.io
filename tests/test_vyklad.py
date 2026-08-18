#!/usr/bin/env python3
"""Regresné testy pre zápis výkladu.

Výklad je krok, ktorý zapíše naraz najviac stavu, a práve on 2026-08-17 spadol
v polovici a nechal duplikáty. Testy sú preto o odmietnutí a o atomicite, nie
o tom, že sa dá zapísať správny artefakt.

    python3 tests/test_vyklad.py
"""
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core import evolution as ev            # noqa: E402
from core import vyklad as vy               # noqa: E402
from core.beh import Beh                    # noqa: E402


def _db(tmp: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(tmp / "t.sqlite3")
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE signals_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER, source TEXT,
        signal_type TEXT, term TEXT, metric_value REAL, url TEXT,
        fetched_at TEXT, payload_json TEXT)""")
    for i in (1, 2, 3):
        conn.execute("INSERT INTO signals_raw (id, source, term, url, fetched_at) "
                     "VALUES (?,'frontier:test',?,?,'2026-01-01')",
                     (i, f"polozka {i}", f"https://example.com/{i}"))
    conn.commit()
    ev.priprav(conn)
    return conn


def test_chybny_artefakt_nezapise_nic() -> list[str]:
    """Chyba v poslednej položke nesmie nechať zapísané tie predošlé."""
    chyby = []
    with tempfile.TemporaryDirectory() as tmp:
        conn = _db(Path(tmp))
        artefakt = {"polozky": [
            {"signal_id": 1, "rozhodnutie": "ZAHODENE", "duvod": "v poriadku"},
            {"signal_id": 2, "rozhodnutie": "ZAHODENE", "duvod": "tiež v poriadku"},
            {"signal_id": 3, "rozhodnutie": "MOZNO", "duvod": "chyba tu"},
        ]}
        try:
            vy.zapis(conn, artefakt)
            chyby.append("chybný artefakt prešiel")
        except vy.ChybnyArtefakt:
            pass
        n = conn.execute("SELECT COUNT(*) FROM vyklad").fetchone()[0]
        if n != 0:
            chyby.append(f"po odmietnutom artefakte je vo vyklad {n} riadkov, má byť 0")
        conn.close()
    return chyby


def test_pad_pocas_zapisu_nenecha_polovicu() -> list[str]:
    """Výnimka uprostred uzla vráti aj to, čo už bolo zapísané."""
    chyby = []
    with tempfile.TemporaryDirectory() as tmp:
        conn = _db(Path(tmp))
        b = Beh(conn, run_id="r", spustil="test")
        try:
            with b.uzol("vyklad") as c:
                vy.zapis(c, {"polozky": [
                    {"signal_id": 1, "rozhodnutie": "ZAHODENE", "duvod": "a"},
                    {"signal_id": 2, "rozhodnutie": "ZAHODENE", "duvod": "b"}]})
                raise RuntimeError("pád po zápise, pred commitom")
        except RuntimeError:
            pass
        n = conn.execute("SELECT COUNT(*) FROM vyklad").fetchone()[0]
        if n != 0:
            chyby.append(f"po páde je vo vyklad {n} riadkov, má byť 0")
        hotove = conn.execute(
            "SELECT COUNT(*) FROM beh_uzol WHERE stav='HOTOVY'").fetchone()[0]
        if hotove != 0:
            chyby.append("padnutý uzol sa označil za hotový")
        conn.close()
    return chyby


def test_opakovany_zapis_neduplikuje() -> list[str]:
    """Ten istý artefakt zapísaný dvakrát dá ten istý stav."""
    chyby = []
    with tempfile.TemporaryDirectory() as tmp:
        conn = _db(Path(tmp))
        artefakt = {"polozky": [
            {"signal_id": 1, "rozhodnutie": "ZAPISANE", "duvod": "má dôsledok",
             "poznatok": {"tvrdenie": "tvrdenie A", "typ_zdroja": "trh",
                          "dosah": "mení to, čo staviame"}},
            {"signal_id": 2, "rozhodnutie": "ZAHODENE", "duvod": "mimo domény"}]}
        vy.zapis(conn, artefakt)
        conn.commit()
        vy.zapis(conn, artefakt)
        conn.commit()
        p = conn.execute("SELECT COUNT(*) FROM poznatky").fetchone()[0]
        v = conn.execute("SELECT COUNT(*) FROM vyklad").fetchone()[0]
        if p != 1:
            chyby.append(f"poznatkov {p}, má byť 1")
        if v != 2:
            chyby.append(f"výkladov {v}, má byť 2")
        conn.close()
    return chyby


if __name__ == "__main__":
    zlyhania = []
    for test in (test_chybny_artefakt_nezapise_nic,
                 test_pad_pocas_zapisu_nenecha_polovicu,
                 test_opakovany_zapis_neduplikuje):
        ch = test()
        print(f"{'OK  ' if not ch else 'ZLE '}{test.__name__}")
        for c in ch:
            print(f"      {c}")
        zlyhania += ch
    print(f"\nzlyhaní: {len(zlyhania)}")
    raise SystemExit(1 if zlyhania else 0)
