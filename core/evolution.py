"""Evolučná vrstva — to, čo doterajšej linke chýbalo.

`scripts/run_pipeline.py` je rovná čiara: snímanie -> kľúčové slová -> nika ->
skóre -> konkurencia -> produkt -> obsah -> stránky -> SEO -> scoreboard.
Scoreboard čísla zapíše a **nikto ich nečíta**. Neexistuje hrana z merania späť
do rozhodovania, takže ďalší beh je rovnaký ako predošlý bez ohľadu na to, čo
predošlý ukázal. Tabuľka `experiments` v DB existuje od začiatku a má nula
riadkov — Experiment Engine bol vyhlásený a nikdy nezapojený.

Táto vrstva pridáva tri veci a nič iné:

1. `poznatky`   — tvrdenie SO ZDROJOM a s dobou platnosti. Odvodenie sa nikdy
                  nesmie ticho stať faktom, preto je `druh` vynútený a prechod
                  medzi druhmi vyžaduje dôkaz.
2. `domnienky`  — strategický predpoklad, ktorý MUSÍ niesť vetu „čo by ho
                  vyvrátilo". Bez nej sa riadok nedá vložiť. To je
                  kvalifikačný filter z CLAUDE.md prevedený zo zvyku do schémy.
3. `experiments`— existujúca tabuľka, konečne zapojená.

Čo tu zámerne NIE JE: meta-optimalizátor, graf grafov, viacmodelová rada.
Pri nule zaplatených faktúr by optimalizovali prázdno. Pridajú sa vtedy, keď
kotva prestane byť nula — nie skôr.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional

from core.db import get_connection

# --- druh poznatku ---------------------------------------------------------
# Poradie je záväzné: nič sa nesmie posunúť doprava bez dôkazu uvedeného v
# `dokaz`. Práve tento tichý posun (odvodenie -> fakt) je spôsob, akým sa
# systém naučí nepravdu a potom ju obhajuje.
DRUHY = ("POZOROVANIE", "ODVODENIE", "HYPOTEZA", "VYSLEDOK", "FAKT")

# --- životný cyklus --------------------------------------------------------
STAVY_POZNATKU = ("NOVY", "AKTIVNY", "STARNE", "PREKONANY", "VYVRATENY")
STAVY_DOMNIENKY = ("OTVORENA", "POTVRDENA", "VYVRATENA", "NEROZHODNUTA")

# Ako rýchlo poznatok starne podľa typu zdroja. AI poznatky sa kazia najrýchlejšie.
PLATNOST_DNI = {
    "model": 60,        # schopnosti modelov, ceny, limity
    "nastroj": 90,      # produkty, API, konektory
    "trh": 180,         # dopyt, konkurencia, ceny na trhu
    "zakaznik": 365,    # čo zákazník naozaj povedal
    "vlastne": 365,     # naše vlastné merania
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS poznatky (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    tvrdenie      TEXT NOT NULL,
    druh          TEXT NOT NULL,
    zdroj         TEXT NOT NULL,          -- URL alebo 'vlastne meranie: <co>'
    typ_zdroja    TEXT NOT NULL,          -- kľúč do PLATNOST_DNI
    zdroj_datum   TEXT,                   -- kedy zdroj vznikol, nie kedy sme ho našli
    zapisane      TEXT NOT NULL,
    plati_do      TEXT NOT NULL,
    dokaz         TEXT,                   -- čo oprávňuje tento druh
    dosah         TEXT,                   -- čo to zlacňuje/umožňuje/ruší
    stav          TEXT NOT NULL DEFAULT 'NOVY',
    nahradza      INTEGER,                -- id poznatku, ktorý týmto padá
    odporuje      INTEGER,
    FOREIGN KEY (nahradza) REFERENCES poznatky(id),
    FOREIGN KEY (odporuje) REFERENCES poznatky(id)
);

CREATE TABLE IF NOT EXISTS domnienky (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    domnienka         TEXT NOT NULL UNIQUE,
    preco_tomu_verime TEXT NOT NULL,
    co_by_ju_vyvratilo TEXT NOT NULL,     -- bez tohto sa riadok nevloží
    ako_to_zistime    TEXT NOT NULL,      -- konkrétne meranie, nie „uvidíme“
    datum_revizie     TEXT NOT NULL,
    stav              TEXT NOT NULL DEFAULT 'OTVORENA',
    dolezitost        INTEGER NOT NULL,   -- 1-5: koľko na nej stojí
    zmeskane_revizie  INTEGER NOT NULL DEFAULT 0,
    vysledok          TEXT,
    zapisane          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rozhodnutia (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    co           TEXT NOT NULL,
    preco        TEXT NOT NULL,
    zamietnute   TEXT,                    -- aké alternatívy padli a prečo
    autorita     TEXT NOT NULL,           -- 'stroj' | 'majitel'
    vratenie     TEXT NOT NULL,           -- ako sa to odrobí
    ocakavany_ucinok TEXT NOT NULL,
    skutocny_ucinok  TEXT,
    domnienka_id INTEGER,
    zapisane     TEXT NOT NULL,
    FOREIGN KEY (domnienka_id) REFERENCES domnienky(id)
);
"""


class ChybaEvolucie(Exception):
    """Vloženie, ktoré by porušilo pravidlo vrstvy."""


def _dnes() -> str:
    return date.today().isoformat()


def priprav(conn: Optional[sqlite3.Connection] = None) -> None:
    """Vytvorí tabuľky. Bezpečné spustiť opakovane."""
    vlastne = conn is None
    conn = conn or get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        if vlastne:
            conn.close()


# --- poznatky --------------------------------------------------------------

def zapis_poznatok(
    conn: sqlite3.Connection,
    *,
    tvrdenie: str,
    druh: str,
    zdroj: str,
    typ_zdroja: str,
    zdroj_datum: Optional[str] = None,
    dokaz: Optional[str] = None,
    dosah: Optional[str] = None,
    nahradza: Optional[int] = None,
) -> int:
    """Zapíše poznatok. Odmietne tri veci, ktoré nás už stáli čas.

    - neznámy druh alebo typ zdroja (preklep by inak vyrobil tichú kategóriu)
    - FAKT alebo VYSLEDOK bez `dokaz` — presne takto sa odvodenie stane faktom
    - zdroj, ktorý nevyzerá ako zdroj (prázdny reťazec, „podľa mňa“)
    """
    if druh not in DRUHY:
        raise ChybaEvolucie(f"neznámy druh {druh!r}; povolené: {', '.join(DRUHY)}")
    if typ_zdroja not in PLATNOST_DNI:
        raise ChybaEvolucie(
            f"neznámy typ zdroja {typ_zdroja!r}; povolené: {', '.join(PLATNOST_DNI)}"
        )
    if druh in ("FAKT", "VYSLEDOK") and not (dokaz or "").strip():
        raise ChybaEvolucie(
            f"{druh} musí niesť `dokaz` — čo ho oprávňuje byť viac než odvodenie"
        )
    if not (zdroj or "").strip():
        raise ChybaEvolucie("poznatok bez zdroja sa nezapisuje")

    plati_do = (date.today() + timedelta(days=PLATNOST_DNI[typ_zdroja])).isoformat()
    cur = conn.execute(
        """INSERT INTO poznatky
           (tvrdenie, druh, zdroj, typ_zdroja, zdroj_datum, zapisane, plati_do,
            dokaz, dosah, stav, nahradza)
           VALUES (?,?,?,?,?,?,?,?,?,'NOVY',?)""",
        (tvrdenie, druh, zdroj, typ_zdroja, zdroj_datum, _dnes(), plati_do,
         dokaz, dosah, nahradza),
    )
    if nahradza is not None:
        conn.execute("UPDATE poznatky SET stav='PREKONANY' WHERE id=?", (nahradza,))
    conn.commit()
    return int(cur.lastrowid)


def zostarni(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Označí poznatky po dobe platnosti ako STARNE a vráti ich.

    Nemaže ich — starnúci poznatok treba prehodnotiť, nie zabudnúť. Toto je
    jediné miesto, kde systém sám prizná, že už niečomu nemusí veriť.
    """
    conn.execute(
        "UPDATE poznatky SET stav='STARNE' "
        "WHERE plati_do < ? AND stav IN ('NOVY','AKTIVNY')",
        (_dnes(),),
    )
    conn.commit()
    return list(conn.execute(
        "SELECT * FROM poznatky WHERE stav='STARNE' ORDER BY plati_do"
    ))


# --- domnienky -------------------------------------------------------------

def zapis_domnienku(
    conn: sqlite3.Connection,
    *,
    domnienka: str,
    preco_tomu_verime: str,
    co_by_ju_vyvratilo: str,
    ako_to_zistime: str,
    datum_revizie: str,
    dolezitost: int,
) -> int:
    """Zapíše strategický predpoklad.

    `co_by_ju_vyvratilo` je povinné a nesmie byť vyhýbavé. Toto je kvalifikačný
    filter z CLAUDE.md — „vieme vopred povedať, čo by dokázalo, že je to zle?“ —
    prenesený zo zvyku do schémy, kde sa nedá obísť zábudlivosťou.
    """
    vyhybave = {"uvidime", "uvidíme", "cas ukaze", "čas ukáže", "neviem", "-", ""}
    if co_by_ju_vyvratilo.strip().lower() in vyhybave:
        raise ChybaEvolucie(
            "`co_by_ju_vyvratilo` musí byť pozorovateľná udalosť, nie „uvidíme“"
        )
    if ako_to_zistime.strip().lower() in vyhybave:
        raise ChybaEvolucie("`ako_to_zistime` musí byť konkrétne meranie")
    if not 1 <= dolezitost <= 5:
        raise ChybaEvolucie("dolezitost je 1-5")

    cur = conn.execute(
        """INSERT INTO domnienky
           (domnienka, preco_tomu_verime, co_by_ju_vyvratilo, ako_to_zistime,
            datum_revizie, stav, dolezitost, zapisane)
           VALUES (?,?,?,?,?,'OTVORENA',?,?)""",
        (domnienka, preco_tomu_verime, co_by_ju_vyvratilo, ako_to_zistime,
         datum_revizie, dolezitost, _dnes()),
    )
    conn.commit()
    return int(cur.lastrowid)


def splatne_domnienky(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Domnienky, ktorých dátum revízie prešiel a ešte sú otvorené."""
    return list(conn.execute(
        "SELECT * FROM domnienky WHERE stav='OTVORENA' AND datum_revizie <= ? "
        "ORDER BY dolezitost DESC, datum_revizie",
        (_dnes(),),
    ))


def zmeskana_revizia(conn: sqlite3.Connection, domnienka_id: int) -> str:
    """Revízia prešla bez dôkazu. Po druhom zmeškaní domnienka padá.

    Toto je mechanizmus, ktorý dokáže vziať „hotovo“ späť. Bez neho systém iba
    povyšuje: raz vyslovená domnienka by žila navždy, lebo ju nikto aktívne
    nevyvráti — a presne tak vznikne stratégia, ktorú nikto nikdy neoveril.
    """
    riadok = conn.execute(
        "SELECT zmeskane_revizie, ako_to_zistime FROM domnienky WHERE id=?",
        (domnienka_id,),
    ).fetchone()
    if riadok is None:
        raise ChybaEvolucie(f"domnienka {domnienka_id} neexistuje")

    zmeskane = riadok["zmeskane_revizie"] + 1
    if zmeskane >= 2:
        conn.execute(
            "UPDATE domnienky SET stav='VYVRATENA', zmeskane_revizie=?, vysledok=? "
            "WHERE id=?",
            (zmeskane,
             "Dve revízie prešli bez dôkazu. Nie je vyvrátená dôkazom proti — "
             "padá preto, že sme ju dvakrát nevedeli overiť, a tak sa na nej "
             "nedá stavať.",
             domnienka_id),
        )
        novy_stav = "VYVRATENA"
    else:
        conn.execute(
            "UPDATE domnienky SET zmeskane_revizie=?, datum_revizie=? WHERE id=?",
            (zmeskane,
             (date.today() + timedelta(days=30)).isoformat(),
             domnienka_id),
        )
        novy_stav = "OTVORENA"
    conn.commit()
    return novy_stav


def rozhodni_domnienku(
    conn: sqlite3.Connection, domnienka_id: int, *, stav: str, vysledok: str
) -> None:
    if stav not in STAVY_DOMNIENKY:
        raise ChybaEvolucie(f"neznámy stav {stav!r}")
    if not vysledok.strip():
        raise ChybaEvolucie("rozhodnutie domnienky musí niesť dôvod")
    conn.execute(
        "UPDATE domnienky SET stav=?, vysledok=? WHERE id=?",
        (stav, vysledok, domnienka_id),
    )
    conn.commit()


# --- čo robiť ďalej --------------------------------------------------------

def hodnota_informacie(domnienka: sqlite3.Row) -> float:
    """Hrubé poradie: dôležitosť × ako dlho je po termíne.

    Zámerne priehľadné a nie model. Presnejšie číslo by predstieralo istotu,
    ktorú nemáme — a poradie stačí na to, aby stroj vedel, čo vziať ako ďalšie.
    """
    try:
        po_termine = (date.today() - date.fromisoformat(domnienka["datum_revizie"])).days
    except (TypeError, ValueError):
        po_termine = 0
    return domnienka["dolezitost"] * (1 + max(po_termine, 0) / 30)


def dalsi_krok(conn: sqlite3.Connection) -> list[dict]:
    """Zoradený zoznam toho, čo si systém pýta ako ďalšie.

    Vracia dáta, nie príkaz. Kto to vykoná, hovorí `autorita`: čokoľvek, čo
    mení, čím má byť biznis, patrí majiteľovi aj vtedy, keď to stroj navrhol.
    """
    kroky: list[dict] = []

    for d in splatne_domnienky(conn):
        kroky.append({
            "poradie": round(hodnota_informacie(d), 2),
            "co": f"Rozhodnúť domnienku: {d['domnienka']}",
            "ako": d["ako_to_zistime"],
            "vyvratilo_by": d["co_by_ju_vyvratilo"],
            "autorita": "majitel" if d["dolezitost"] >= 4 else "stroj",
        })

    for p in conn.execute(
        "SELECT * FROM poznatky WHERE stav='STARNE' ORDER BY plati_do"
    ):
        kroky.append({
            "poradie": 1.0,
            "co": f"Preveriť starnúci poznatok: {p['tvrdenie']}",
            "ako": f"otvoriť {p['zdroj']} a potvrdiť alebo nahradiť",
            "vyvratilo_by": "zdroj už tvrdí niečo iné alebo neexistuje",
            "autorita": "stroj",
        })

    kroky.sort(key=lambda k: k["poradie"], reverse=True)
    return kroky
