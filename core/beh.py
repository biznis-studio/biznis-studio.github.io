"""Beh, kontrolné body a rozpočty — podklad pre bezobslužnú prevádzku.

Bez tohto je autonómia len šťastná cesta. Beh, ktorý spadne v treťom uzle,
musí po reštarte preskočiť prvé dva a tretí zopakovať — a hlavne po ňom nesmie
zostať polovica zápisov. Presne to sa 2026-08-17 stalo pri výklade fronty:
priechod spadol v polovici, časť poznatkov ostala zapísaná a opakovanie ich
zapísalo druhýkrát.

Dve veci, na ktorých to stojí:

1. **Kontrolný bod je v tej istej transakcii ako zápisy uzla.** Keby sa značka
   „uzol hotový" commitla zvlášť, existoval by okamih, v ktorom je uzol
   označený za hotový a jeho dáta chýbajú — alebo naopak. Preto sa commituje
   raz a naraz.

2. **`commit()` je počas uzla nečinný.** Funkcie v `core/evolution.py` si
   commitujú samy (a je to tak správne, keď ich volá človek). Vnútri uzla by
   ale každý taký commit uzavrel transakciu a rozbil atomicitu, takže uzol
   dostane spojenie, ktorému je commit potlačený, a skutočný commit spraví on.

Rozpočet nie je optimalizácia, je to stop-pravidlo. Beh, ktorý nevie, koľko mu
zostáva, sa nedá pustiť bez dozoru — „ešte jeden výskum by pomohol" je
nekonečná slučka s dobrým úmyslom.
"""

from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS beh (
    run_id      TEXT PRIMARY KEY,
    spustil     TEXT NOT NULL,
    zacal       TEXT NOT NULL,
    skoncil     TEXT,
    stav        TEXT NOT NULL,        -- BEZI | HOTOVO | PADOL | ROZPOCET
    rozpocet    TEXT NOT NULL,        -- JSON: stropy
    minute      TEXT NOT NULL         -- JSON: spotrebované
);

CREATE TABLE IF NOT EXISTS beh_uzol (
    run_id   TEXT NOT NULL,
    uzol     TEXT NOT NULL,
    stav     TEXT NOT NULL,           -- HOTOVY | PADOL
    kedy     TEXT NOT NULL,
    trvanie  REAL,
    detail   TEXT,
    PRIMARY KEY (run_id, uzol)
);
"""


class RozpocetVycerpany(Exception):
    """Stop-pravidlo zabralo. Nie je to porucha — je to koniec behu."""


class _BezCommitu:
    """Spojenie, ktorému je `commit()` počas uzla nečinný.

    Nie je to obchádzka cudzieho kódu: je to hranica transakcie. Uzol je
    najmenšia jednotka, ktorá buď nastala celá, alebo vôbec.
    """

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def commit(self) -> None:          # zámerne nič
        pass

    def __getattr__(self, meno: str):
        return getattr(self._conn, meno)


class Beh:
    """Jeden beh s kontrolnými bodmi a rozpočtom."""

    def __init__(self, conn: sqlite3.Connection, *, run_id: str, spustil: str,
                 max_uzlov: int = 40, max_sekund: int = 3600,
                 max_volani_modelu: int = 60, max_zdrojov: int = 200):
        self.conn = conn
        self.run_id = run_id
        self.zaciatok = time.monotonic()
        self.stropy = {"uzly": max_uzlov, "sekundy": max_sekund,
                       "volania_modelu": max_volani_modelu, "zdroje": max_zdrojov}
        self.minute = {"uzly": 0, "volania_modelu": 0, "zdroje": 0}
        conn.executescript(SCHEMA)
        import json
        conn.execute(
            "INSERT INTO beh (run_id, spustil, zacal, stav, rozpocet, minute) "
            "VALUES (?,?,?,'BEZI',?,?) ON CONFLICT(run_id) DO UPDATE SET stav='BEZI'",
            (run_id, spustil, datetime.now().isoformat(),
             json.dumps(self.stropy), json.dumps(self.minute)))
        conn.commit()

    # --- rozpočet ---------------------------------------------------------

    def minul(self, polozka: str, kolko: int = 1) -> None:
        self.minute[polozka] = self.minute.get(polozka, 0) + kolko

    def zostava(self) -> dict:
        von = {k: self.stropy[k] - self.minute.get(k, 0)
               for k in ("uzly", "volania_modelu", "zdroje")}
        von["sekundy"] = int(self.stropy["sekundy"] - (time.monotonic() - self.zaciatok))
        return von

    def _skontroluj_rozpocet(self) -> None:
        zost = self.zostava()
        vycerpane = [k for k, v in zost.items() if v <= 0]
        if vycerpane:
            self._uzavri("ROZPOCET")
            raise RozpocetVycerpany(
                f"vyčerpané: {', '.join(vycerpane)}; zostatok {zost}")

    # --- kontrolné body ---------------------------------------------------

    def hotove(self) -> set[str]:
        return {r["uzol"] for r in self.conn.execute(
            "SELECT uzol FROM beh_uzol WHERE run_id=? AND stav='HOTOVY'",
            (self.run_id,))}

    @contextmanager
    def uzol(self, meno: str) -> Iterator[Optional[_BezCommitu]]:
        """Vykoná uzol raz. Pri opakovanom behu ho preskočí.

        Vydá `None`, keď je uzol už hotový — volajúci to musí ošetriť, aby
        preskočenie nikdy nebolo tiché.
        """
        if meno in self.hotove():
            yield None
            return

        self._skontroluj_rozpocet()
        zac = time.monotonic()
        self.conn.execute("BEGIN")
        try:
            yield _BezCommitu(self.conn)
            # Značka aj dáta uzla idú jedným commitom. Inak existuje okamih,
            # v ktorom je uzol označený za hotový a jeho dáta chýbajú.
            self.conn.execute(
                "INSERT INTO beh_uzol (run_id, uzol, stav, kedy, trvanie) "
                "VALUES (?,?,'HOTOVY',?,?) "
                "ON CONFLICT(run_id, uzol) DO UPDATE SET stav='HOTOVY', "
                "kedy=excluded.kedy, trvanie=excluded.trvanie",
                (self.run_id, meno, datetime.now().isoformat(),
                 round(time.monotonic() - zac, 2)))
            self.conn.execute("COMMIT")
            self.minul("uzly")
        except BaseException as chyba:
            # Rollback zahodí VŠETKY zápisy uzla, aj tie, ktoré stihli prejsť.
            # Po reštarte je stav taký, ako keby uzol nikdy nezačal.
            try:
                self.conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            self.conn.execute(
                "INSERT INTO beh_uzol (run_id, uzol, stav, kedy, trvanie, detail) "
                "VALUES (?,?,'PADOL',?,?,?) "
                "ON CONFLICT(run_id, uzol) DO UPDATE SET stav='PADOL', "
                "kedy=excluded.kedy, detail=excluded.detail",
                (self.run_id, meno, datetime.now().isoformat(),
                 round(time.monotonic() - zac, 2),
                 f"{type(chyba).__name__}: {chyba}"[:300]))
            self.conn.commit()
            raise

    def _uzavri(self, stav: str) -> None:
        import json
        self.conn.execute(
            "UPDATE beh SET stav=?, skoncil=?, minute=? WHERE run_id=?",
            (stav, datetime.now().isoformat(), json.dumps(self.minute), self.run_id))
        self.conn.commit()

    def hotovo(self) -> None:
        self._uzavri("HOTOVO")

    def padol(self) -> None:
        self._uzavri("PADOL")
