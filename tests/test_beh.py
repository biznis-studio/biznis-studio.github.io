#!/usr/bin/env python3
"""Regresné testy pre beh, kontrolné body a rozpočty.

Netestujú šťastnú cestu. Každý z nich reprodukuje poruchu, ktorá by
bezobslužný beh rozbila — a pád je vyvolaný `os._exit`, teda tvrdo, aby
obišiel aj `except` a `finally`. Odchytená výnimka by dokázala len to, že
vieme písať `try`.

    python3 tests/test_beh.py
"""
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core.beh import Beh, RozpocetVycerpany            # noqa: E402

WORKER = '''
import os, sqlite3, sys
sys.path.insert(0, {root!r})
from core.beh import Beh
conn = sqlite3.connect(sys.argv[1]); conn.row_factory = sqlite3.Row
conn.execute("CREATE TABLE IF NOT EXISTS stopa (uzol TEXT, zapis TEXT)"); conn.commit()
b = Beh(conn, run_id="r", spustil="test")
for meno in ("uzol1", "uzol2"):
    with b.uzol(meno) as c:
        if c is not None:
            c.execute("INSERT INTO stopa VALUES (?,?)", (meno, "A"))
with b.uzol("uzol3") as c:
    if c is not None:
        c.execute("INSERT INTO stopa VALUES ('uzol3','A')")
        c.execute("INSERT INTO stopa VALUES ('uzol3','B')")
        c.commit()
        if sys.argv[2] == "zabit":
            os._exit(9)
        c.execute("INSERT INTO stopa VALUES ('uzol3','C')")
with b.uzol("uzol4") as c:
    if c is not None:
        c.execute("INSERT INTO stopa VALUES ('uzol4','A')")
b.hotovo()
'''


def _spusti(skript: Path, db: Path, rezim: str) -> int:
    return subprocess.run([sys.executable, str(skript), str(db), rezim],
                          capture_output=True).returncode


def test_pad_v_polovici_uzla_nenechá_polovicu_zápisov() -> list[str]:
    """Tvrdý pád uprostred uzla: ani kontrolný bod, ani žiadny zápis uzla."""
    chyby = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        skript = tmp / "w.py"
        skript.write_text(WORKER.format(root=str(ROOT)))
        db = tmp / "t.sqlite3"

        kod = _spusti(skript, db, "zabit")
        if kod == 0:
            chyby.append("proces mal zomrieť, ale skončil nulou")

        conn = sqlite3.connect(db); conn.row_factory = sqlite3.Row
        hotove = {r["uzol"] for r in conn.execute(
            "SELECT uzol FROM beh_uzol WHERE stav='HOTOVY'")}
        if hotove != {"uzol1", "uzol2"}:
            chyby.append(f"po páde mali byť hotové uzol1+uzol2, sú {hotove}")
        z3 = conn.execute("SELECT COUNT(*) FROM stopa WHERE uzol='uzol3'").fetchone()[0]
        if z3 != 0:
            chyby.append(f"uzol3 nechal {z3} zápisov; mal nechať 0")

        # reštart
        conn.close()
        if _spusti(skript, db, "pokracuj") != 0:
            chyby.append("reštart neskončil nulou")
        conn = sqlite3.connect(db); conn.row_factory = sqlite3.Row
        for uzol, ocakavane in (("uzol1", 1), ("uzol2", 1), ("uzol3", 3), ("uzol4", 1)):
            n = conn.execute("SELECT COUNT(*) FROM stopa WHERE uzol=?",
                             (uzol,)).fetchone()[0]
            if n != ocakavane:
                chyby.append(f"{uzol}: {n} zápisov, čakalo sa {ocakavane}")
        stav = conn.execute("SELECT stav FROM beh WHERE run_id='r'").fetchone()["stav"]
        if stav != "HOTOVO":
            chyby.append(f"beh mal skončiť HOTOVO, skončil {stav}")
        conn.close()
    return chyby


def test_rozpocet_zastavi_beh() -> list[str]:
    """Strop na uzly a na čas musí beh zastaviť, nie spomaliť."""
    chyby = []
    with tempfile.TemporaryDirectory() as tmp:
        conn = sqlite3.connect(Path(tmp) / "r.sqlite3")
        conn.row_factory = sqlite3.Row
        conn.execute("CREATE TABLE stopa (u TEXT)"); conn.commit()

        b = Beh(conn, run_id="r1", spustil="test", max_uzlov=3)
        vykonane = 0
        try:
            for i in range(8):
                with b.uzol(f"u{i}") as c:
                    c.execute("INSERT INTO stopa VALUES (?)", (str(i),))
                    vykonane += 1
        except RozpocetVycerpany:
            pass
        else:
            chyby.append("rozpočet na uzly nezastavil beh")
        if vykonane != 3:
            chyby.append(f"vykonaných {vykonane} uzlov, strop bol 3")
        if conn.execute("SELECT stav FROM beh WHERE run_id='r1'").fetchone()["stav"] != "ROZPOCET":
            chyby.append("beh sa neoznačil ako ROZPOCET")

        b2 = Beh(conn, run_id="r2", spustil="test", max_sekund=0)
        try:
            with b2.uzol("x"):
                chyby.append("uzol sa spustil napriek vyčerpanému času")
        except RozpocetVycerpany:
            pass
        conn.close()
    return chyby


def test_vlastny_zamok_nebrani_obnoveniu() -> list[str]:
    """Beh zabitý uprostred nechá zámok BEZI. Musí sa vedieť obnoviť hneď.

    Našiel to až test na SKUTOČNEJ ceste: os._exit preskočí `finally`, takže
    zámok zostane držaný behom, ktorý už neexistuje. Bez tejto vetvy by sa beh
    obnovil až 45 minút po páde, ktorý trval sekundu.
    """
    from core import evolution as ev
    chyby = []
    with tempfile.TemporaryDirectory() as tmp:
        conn = sqlite3.connect(Path(tmp) / "z.sqlite3")
        conn.row_factory = sqlite3.Row
        ev.priprav(conn)
        ev.zamkni(conn, run_id="beh-1", vlastnik="test")
        try:
            ev.zamkni(conn, run_id="beh-1", vlastnik="test")   # obnovenie
        except ev.ZamokObsadeny:
            chyby.append("vlastný zámok zablokoval obnovenie toho istého behu")
        try:
            ev.zamkni(conn, run_id="beh-2", vlastnik="test")
            chyby.append("cudzí beh prevzal živý zámok")
        except ev.ZamokObsadeny:
            pass
        conn.close()
    return chyby


if __name__ == "__main__":
    zlyhania = []
    for test in (test_pad_v_polovici_uzla_nenechá_polovicu_zápisov,
                 test_rozpocet_zastavi_beh,
                 test_vlastny_zamok_nebrani_obnoveniu):
        chyby = test()
        znacka = "OK  " if not chyby else "ZLE "
        print(f"{znacka}{test.__name__}")
        for ch in chyby:
            print(f"      {ch}")
        zlyhania += chyby
    print(f"\nzlyhaní: {len(zlyhania)}")
    raise SystemExit(1 if zlyhania else 0)
