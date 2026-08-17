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
import re
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
    poznatok_id       INTEGER,            -- z ktorého poznatku sa zrodila
    zapisane          TEXT NOT NULL,
    FOREIGN KEY (poznatok_id) REFERENCES poznatky(id)
);

-- Každá položka z fronty musí skončiť rozhodnutím: buď sa z nej stal poznatok,
-- alebo sme ju zahodili a povedali prečo. Bez zápisu zahodených sa nedá spočítať
-- výťažnosť zdroja — a zdroj, ktorého výťažnosť nikto nemeria, sa nedá zrušiť.
CREATE TABLE IF NOT EXISTS vyklad (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id   INTEGER NOT NULL UNIQUE,
    zdroj       TEXT NOT NULL,
    rozhodnutie TEXT NOT NULL,          -- ZAPISANE | ZAHODENE
    duvod       TEXT NOT NULL,
    poznatok_id INTEGER,
    kedy        TEXT NOT NULL,
    FOREIGN KEY (signal_id) REFERENCES signals_raw(id),
    FOREIGN KEY (poznatok_id) REFERENCES poznatky(id)
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
    datum_revizie TEXT NOT NULL,
    vrstva       TEXT NOT NULL,           -- 'produkt' | 'system'
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

    # Idempotencia. Zápis nie je v transakcii s ostatnými, takže výklad, ktorý
    # spadne v polovici, nechá za sebou časť poznatkov — a opakovanie ich
    # zapíše druhýkrát. Presne to sa stalo 2026-08-17: štyri poznatky vznikli
    # dvakrát, keď prvý priechod spadol na chýbajúcej URL z MCP registra.
    # V dennom behu bez dozoru by sa to opakovalo pri každom zlyhaní.
    uz = conn.execute(
        "SELECT id FROM poznatky WHERE zdroj = ? AND tvrdenie = ? "
        "AND stav NOT IN ('PREKONANY','VYVRATENY')", (zdroj, tvrdenie)
    ).fetchone()
    if uz is not None:
        return int(uz["id"])

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
    poznatok_id: Optional[int] = None,
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
            datum_revizie, stav, dolezitost, poznatok_id, zapisane)
           VALUES (?,?,?,?,?,'OTVORENA',?,?,?)""",
        (domnienka, preco_tomu_verime, co_by_ju_vyvratilo, ako_to_zistime,
         datum_revizie, dolezitost, poznatok_id, _dnes()),
    )
    conn.commit()
    return int(cur.lastrowid)


def poznatky_bez_dosledku(conn: sqlite3.Connection, limit: int = 10) -> list[sqlite3.Row]:
    """Poznatky, ktoré niečo znamenajú, ale nikdy nič nespôsobili.

    Toto je hranica medzi automatizovaným výskumom a evolúciou. Systém, ktorý
    poznatky zbiera, vykladá a zakladá, ale nikdy z nich nespraví vyvrátiteľnú
    hypotézu, je archív. Presne tu sa doteraz reťaz trhala: `domnienky` vznikali
    výhradne z ručne napísaného zoznamu v `evolve.py` a z 20 zapísaných poznatkov
    neviedol k hypotéze ani jeden.

    Zámerne vracia len poznatky s vyplneným `dosah` — kde nikto nepovedal, čo to
    mení, tam nie je z čoho hypotézu postaviť, a nasilu vyrobená hypotéza je
    horšia než žiadna.
    """
    return list(conn.execute(
        "SELECT * FROM poznatky p WHERE p.dosah IS NOT NULL AND TRIM(p.dosah) <> '' "
        "AND p.stav <> 'VYVRATENY' "
        "AND NOT EXISTS (SELECT 1 FROM domnienky d WHERE d.poznatok_id = p.id) "
        "ORDER BY p.id DESC LIMIT ?", (limit,)
    ))


def mozne_rozpory(conn: sqlite3.Connection, limit: int = 5) -> list[dict]:
    """Dvojice poznatkov o tej istej veci, ktoré si môžu odporovať.

    Rozpor sa nedá spoľahlivo nájsť kódom — „Microsoft overovanie nerieši“ a
    „Microsoft ohlásil governance agentov“ sa nelíšia ani jedným kľúčovým
    slovom, a pritom napätie medzi nimi je celý zmysel veci. Kód preto len
    predloží dvojice s prekryvom podstatných slov; rozhodnúť ich musí úsudok
    cez `oznac_rozpor`. Tichý prepis staršieho poznatku novším je zakázaný.
    """
    riadky = list(conn.execute(
        "SELECT id, tvrdenie, typ_zdroja FROM poznatky "
        "WHERE stav NOT IN ('VYVRATENY','PREKONANY') ORDER BY id DESC LIMIT 60"
    ))
    stop = {"a", "aj", "ako", "ale", "na", "sa", "sú", "je", "to", "že", "pre",
            "the", "and", "for", "with", "that", "ktoré", "ktorá", "ktorý", "nie"}

    def slova(text: str) -> set[str]:
        return {w for w in re.findall(r"\w{5,}", text.lower()) if w not in stop}

    dvojice = []
    for i, a in enumerate(riadky):
        sa_ = slova(a["tvrdenie"])
        for b in riadky[i + 1:]:
            spolocne = sa_ & slova(b["tvrdenie"])
            if len(spolocne) >= 3:
                dvojice.append({
                    "a": a["id"], "b": b["id"], "spolocne": sorted(spolocne)[:5],
                    "a_text": a["tvrdenie"][:90], "b_text": b["tvrdenie"][:90],
                })
    return dvojice[:limit]


def oznac_rozpor(conn: sqlite3.Connection, novy_id: int, stary_id: int,
                 *, rozhodnutie: str) -> None:
    """Zaznamená rozpor. `rozhodnutie` je 'NAHRADZA' alebo 'NEISTE'.

    'NAHRADZA' starý poznatok zhodí, 'NEISTE' nechá oba žiť a označí ich —
    lebo dva zdroje, ktoré si odporujú a ani jeden nie je zjavne lepší, sú
    stav neistoty, nie dôvod vybrať si ten pohodlnejší.
    """
    if rozhodnutie not in ("NAHRADZA", "NEISTE"):
        raise ChybaEvolucie("rozhodnutie je NAHRADZA alebo NEISTE")
    conn.execute("UPDATE poznatky SET odporuje=? WHERE id=?", (stary_id, novy_id))
    if rozhodnutie == "NAHRADZA":
        conn.execute("UPDATE poznatky SET stav='PREKONANY', nahradza=NULL WHERE id=?",
                     (stary_id,))
    conn.commit()


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

# --- meranie vlastnej výťažnosti -------------------------------------------
#
# Toto je jediné miesto, kde sa systém mení sám od seba. Všetko ostatné vie
# len to, čo mu niekto napísal. Zdroj sa neruší preto, že sa niekomu zdá slabý,
# ale preto, že po dostatočnom počte položiek z neho nevzniklo nič.

MIN_VZORKA = 25          # pod týmto počtom je pomer šum, nie výsledok
PRAH_ZRUSENIA = 0.04     # menej než 4 % zapísaných = zdroj neplatí za miesto


def zapis_vyklad(
    conn: sqlite3.Connection,
    *,
    signal_id: int,
    zdroj: str,
    rozhodnutie: str,
    duvod: str,
    poznatok_id: Optional[int] = None,
) -> None:
    """Zaznamená, ako dopadla jedna položka fronty. Aj zahodenie je výsledok."""
    if rozhodnutie not in ("ZAPISANE", "ZAHODENE"):
        raise ChybaEvolucie("rozhodnutie je ZAPISANE alebo ZAHODENE")
    if not duvod.strip():
        raise ChybaEvolucie(
            "zahodenie bez dôvodu je nemerateľné — práve dôvody hovoria, "
            "či je slabý zdroj alebo filter"
        )
    conn.execute(
        "INSERT OR REPLACE INTO vyklad "
        "(signal_id, zdroj, rozhodnutie, duvod, poznatok_id, kedy) "
        "VALUES (?,?,?,?,?,?)",
        (signal_id, zdroj, rozhodnutie, duvod, poznatok_id, _dnes()),
    )
    conn.commit()


def ucinnost_zdrojov(conn: sqlite3.Connection) -> list[dict]:
    """Za každý zdroj: koľko dal, koľko z toho prežilo úsudok, a čo s ním.

    `vyklad` je jediný vstup — nie počet nasnímaných položiek. Zdroj, ktorý
    nasype tisíc riadkov a nikto ich nevyloží, nie je výkonný ani neúspešný,
    je len nezmeraný, a nesmie z toho dostať ani odmenu, ani trest.
    """
    riadky = conn.execute(
        "SELECT zdroj, "
        "  SUM(rozhodnutie='ZAPISANE') AS zapisane, "
        "  COUNT(*) AS vylozene "
        "FROM vyklad GROUP BY zdroj"
    ).fetchall()

    von = []
    for r in riadky:
        vylozene = r["vylozene"] or 0
        zapisane = r["zapisane"] or 0
        pomer = zapisane / vylozene if vylozene else 0.0
        if vylozene < MIN_VZORKA:
            odporucanie = f"MERIA SA ({vylozene}/{MIN_VZORKA})"
        elif pomer < PRAH_ZRUSENIA:
            odporucanie = "ZRUSIT"
        else:
            odporucanie = "PONECHAT"
        von.append({
            "zdroj": r["zdroj"], "vylozene": vylozene, "zapisane": zapisane,
            "pomer": round(pomer, 3), "odporucanie": odporucanie,
        })
    von.sort(key=lambda z: z["pomer"], reverse=True)
    return von


# --- rozhodnutia: aj o samotnom stroji ------------------------------------
#
# `vrstva='system'` je tu podstatná. Zlepšovať sa musí nielen produkt, ale aj
# stroj, ktorý ho vyrába — a stroj sa nezlepší tým, že do neho pribúdajú vrstvy.
# Zlepší sa tým, že každá vrstva vopred povie, čo má spôsobiť, a po termíne sa
# to porovná. Vrstva, ktorá nespôsobila nič, je zbytočná bez ohľadu na to, ako
# dobre je napísaná.

def zapis_rozhodnutie(
    conn: sqlite3.Connection,
    *,
    co: str,
    preco: str,
    ocakavany_ucinok: str,
    vratenie: str,
    datum_revizie: str,
    vrstva: str,
    zamietnute: Optional[str] = None,
    autorita: str = "stroj",
    domnienka_id: Optional[int] = None,
) -> int:
    """Zapíše zmenu spolu s tým, čo má spôsobiť a ako sa odrobí.

    `ocakavany_ucinok` musí byť pozorovateľný. „Bude to lepšie“ sa nedá
    vyhodnotiť, takže sa nedá ani zamietnuť — a nezamietnuteľná zmena je presne
    tá, ktorá v systéme zostane navždy.
    """
    if vrstva not in ("produkt", "system"):
        raise ChybaEvolucie("vrstva je 'produkt' alebo 'system'")
    vagne = ("lepšie", "lepsie", "zlepší", "zlepsi", "efektívnejšie", "rýchlejšie")
    text = ocakavany_ucinok.strip().lower()
    if len(text) < 25 or (any(v in text for v in vagne) and not any(c.isdigit() for c in text)):
        raise ChybaEvolucie(
            "`ocakavany_ucinok` musí byť pozorovateľný — „bude to lepšie“ sa "
            "nedá vyhodnotiť, a teda ani zamietnuť"
        )
    if not vratenie.strip():
        raise ChybaEvolucie("zmena bez spôsobu vrátenia sa nezapisuje")

    cur = conn.execute(
        """INSERT INTO rozhodnutia
           (co, preco, zamietnute, autorita, vratenie, ocakavany_ucinok,
            datum_revizie, vrstva, domnienka_id, zapisane)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (co, preco, zamietnute, autorita, vratenie, ocakavany_ucinok,
         datum_revizie, vrstva, domnienka_id, _dnes()),
    )
    conn.commit()
    return int(cur.lastrowid)


def vyhodnot_rozhodnutie(conn: sqlite3.Connection, rozhodnutie_id: int,
                         *, skutocny_ucinok: str) -> None:
    """Porovná, čo sa čakalo, s tým, čo nastalo. Bez toho niet učenia.

    Toto pole doteraz nenastavovalo nič — takže systém vedel povedať, čo od
    zmeny čaká, ale nikdy sa nedozvedel, či to nastalo. Zmena, ktorej výsledok
    nikto neporovná, ostane navždy, lebo neexistuje dôvod ju zrušiť.
    """
    if len(skutocny_ucinok.strip()) < 15:
        raise ChybaEvolucie(
            "skutočný účinok musí byť pozorovanie, nie „ok“ — porovnáva sa "
            "s očakávaním a to porovnanie je jediný zdroj poučenia"
        )
    conn.execute("UPDATE rozhodnutia SET skutocny_ucinok=? WHERE id=?",
                 (skutocny_ucinok, rozhodnutie_id))
    conn.commit()


def nevyhodnotene_rozhodnutia(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Zmeny po termíne revízie, ktorým nikto neporovnal očakávanie so skutočnosťou."""
    return list(conn.execute(
        "SELECT * FROM rozhodnutia WHERE skutocny_ucinok IS NULL "
        "AND datum_revizie <= ? ORDER BY vrstva, datum_revizie", (_dnes(),)
    ))


def navrhy_na_seba(conn: sqlite3.Connection) -> list[dict]:
    """Systém číta vlastné dôvody zahodenia a navrhuje zmeny na sebe.

    Toto je rozdiel medzi filtrom a vrstvou, ktorá sa učí. Filter len prepúšťa.
    Tu je vstupom to, čo úsudok o vlastnej práci povedal: keď sa istý dôvod
    zahodenia opakuje, nie je to smola na položkách — je to porucha v zbere,
    a povedať sa dá, ktorá.

    Vracia návrhy, nie vykonané zmeny. Návrh, ktorý zruší zdroj, môže vykonať
    stroj; návrh, ktorý mení, čo považujeme za relevantné, mení zameranie firmy,
    a ten patrí majiteľovi.
    """
    navrhy: list[dict] = []

    # 1. Zdroj, ktorého zahodenia sa opakujú z toho istého dôvodu, nie je slabý
    #    náhodou — sníma zlú vec.
    dovody = conn.execute(
        "SELECT zdroj, duvod, COUNT(*) AS n FROM vyklad "
        "WHERE rozhodnutie='ZAHODENE' GROUP BY zdroj, duvod HAVING n >= 2"
    ).fetchall()
    for d in dovody:
        navrhy.append({
            "co": f"{d['zdroj']}: {d['n']}× zahodené z toho istého dôvodu — "
                  f"„{d['duvod'][:70]}“",
            "preco": "opakovaný dôvod je porucha zberu, nie smola na položkách",
            "autorita": "stroj",
        })

    # 2. Zahodenie pre nedostatok obsahu znamená, že zbierame titulky tam, kde
    #    treba text. To je oprava zberu, nie dôvod zrušiť zdroj.
    riedke = conn.execute(
        "SELECT zdroj, COUNT(*) AS n FROM vyklad WHERE rozhodnutie='ZAHODENE' "
        "AND (duvod LIKE '%titulok%' OR duvod LIKE '%Iba názov%' "
        "OR duvod LIKE '%nestačí%') GROUP BY zdroj"
    ).fetchall()
    for r in riedke:
        navrhy.append({
            "co": f"{r['zdroj']}: {r['n']}× zahodené preto, že titulok nestačil",
            "preco": "zbierame názvy tam, kde je poznatok až v texte — "
                     "zdroj potrebuje dočítanie obsahu, nie zrušenie",
            "autorita": "stroj",
        })

    # 3. Poznatok bez `dosah` je zápis bez dôsledku. Ak ich je veľa, vykladáme
    #    len nazbierané, nie premyslené.
    bez_dosahu = conn.execute(
        "SELECT COUNT(*) AS n FROM poznatky WHERE dosah IS NULL OR TRIM(dosah)=''"
    ).fetchone()["n"]
    if bez_dosahu:
        navrhy.append({
            "co": f"{bez_dosahu} poznatkov nemá vyplnený `dosah`",
            "preco": "poznatok bez dôsledku je zápis do skládky; buď sa doplní, "
                     "čo mení, alebo sa maže",
            "autorita": "stroj",
        })

    # 4. Ak úsudok prepustí takmer všetko, filter nefiltruje a fronta rastie
    #    rýchlejšie, než ju stíhame vykladať.
    spolu = conn.execute("SELECT COUNT(*) AS n FROM vyklad").fetchone()["n"]
    zapisane = conn.execute(
        "SELECT COUNT(*) AS n FROM vyklad WHERE rozhodnutie='ZAPISANE'"
    ).fetchone()["n"]
    if spolu >= MIN_VZORKA and zapisane / spolu > 0.8:
        navrhy.append({
            "co": f"Úsudok prepúšťa {zapisane}/{spolu} položiek",
            "preco": "buď je filter príliš voľný, alebo výklad nič nezahadzuje — "
                     "v oboch prípadoch prestal byť sitom",
            "autorita": "majitel",
        })

    return navrhy


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

    for p in poznatky_bez_dosledku(conn):
        kroky.append({
            "poradie": 4.5,
            "co": f"Postaviť vyvrátiteľnú hypotézu z poznatku #{p['id']}: "
                  f"{p['tvrdenie'][:90]}",
            "ako": f"dosah hovorí: {p['dosah'][:110]} — sformulovať, čo z toho "
                   f"vyplýva pre nás, a čím sa to dá vyvrátiť",
            "vyvratilo_by": "poznatok nemá dôsledok pre nás; potom ho označ ako "
                            "PREKONANY namiesto vymýšľania hypotézy",
            "autorita": "stroj",
        })

    for d in mozne_rozpory(conn):
        kroky.append({
            "poradie": 4.2,
            "co": f"Preveriť možný rozpor #{d['a']} vs #{d['b']} "
                  f"(spoločné: {', '.join(d['spolocne'])})",
            "ako": f"A: {d['a_text']} · B: {d['b_text']} — rozhodnúť cez "
                   f"oznac_rozpor: NAHRADZA alebo NEISTE",
            "vyvratilo_by": "hovoria o inej veci a prekryv slov je náhodný",
            "autorita": "stroj",
        })

    for r in nevyhodnotene_rozhodnutia(conn):
        kroky.append({
            "poradie": 4.0 if r["vrstva"] == "system" else 3.5,
            "co": f"Vyhodnotiť zmenu ({r['vrstva']}): {r['co']}",
            "ako": f"porovnať so skutočnosťou — očakávalo sa: {r['ocakavany_ucinok']}",
            "vyvratilo_by": f"nenastalo to; vrátenie: {r['vratenie']}",
            "autorita": r["autorita"],
        })

    for z in ucinnost_zdrojov(conn):
        if z["odporucanie"] == "ZRUSIT":
            kroky.append({
                "poradie": 3.0,
                "co": f"Zrušiť zdroj {z['zdroj']} — z {z['vylozene']} vyložených "
                      f"prežilo úsudok {z['zapisane']} ({z['pomer']:.0%})",
                "ako": "vyradiť ho zo ZDROJE vo frontier_agent.py alebo z x_watchlist.json",
                "vyvratilo_by": "zdroj práve zmenil zameranie a nová vzorka to ukáže",
                "autorita": "stroj",
            })

    kroky.sort(key=lambda k: k["poradie"], reverse=True)
    return kroky


def zrusene_zdroje(conn: sqlite3.Connection) -> set[str]:
    """Zdroje, ktoré si po dostatočnej vzorke miesto nezaslúžili.

    `frontier_agent` sa na to pýta pred každým behom, takže rozhodnutie sa
    prejaví bez toho, aby ktokoľvek zasahoval do kódu. Toto je ten rozdiel
    medzi slučkou, ktorá beží, a systémom, ktorý sa mení.
    """
    return {
        z["zdroj"] for z in ucinnost_zdrojov(conn)
        if z["odporucanie"] == "ZRUSIT"
    }
