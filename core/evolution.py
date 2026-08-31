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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

from core.db import get_connection, DB_PATH

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
-- Naraz smie stav meniť jediný beh. 2026-08-17 bežali dva cloudové behy a
-- pipeline súčasne nad tou istou `db/biznis.sqlite3`; je to binárny súbor, kde
-- súbežný zápis nekončí zlúčením, ale prepisom. Databázy sa rozišli a museli sa
-- zmierovať ručne. Autonómia bez tohto zámku je nebezpečná autonómia.
CREATE TABLE IF NOT EXISTS beh_zamok (
    id         INTEGER PRIMARY KEY CHECK (id = 1),   -- práve jeden riadok
    run_id     TEXT NOT NULL,
    vlastnik   TEXT NOT NULL,
    zacal      TEXT NOT NULL,
    plati_do   TEXT NOT NULL,        -- prežije aj pád procesu
    stav       TEXT NOT NULL         -- BEZI | HOTOVO | PADOL
);

-- Zdravie zdroja pri každom pokuse. Bez toho sa "nula položiek" nedá odlíšiť
-- od "nedosiahol som" a systém sa učí z fikcie.
CREATE TABLE IF NOT EXISTS zdroj_zdravie (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id   INTEGER,
    zdroj    TEXT NOT NULL,
    stav     TEXT NOT NULL,
    url      TEXT,
    pocet    INTEGER NOT NULL DEFAULT 0,
    trvanie  REAL,
    detail   TEXT,
    kedy     TEXT NOT NULL
);

-- Ktoré artefakty výkladu už boli zapísané. Kontrolný bod je viazaný na
-- run_id, takže NOVÝ beh by ten istý artefakt spracoval znova; idempotencia
-- zápisu by síce zabránila duplicitám, ale úsudok by sa premrhal a stav by
-- tvrdil, že sa niečo stalo dvakrát. Kľúčom je odtlačok obsahu, nie meno
-- súboru — premenovaný artefakt je ten istý artefakt.
CREATE TABLE IF NOT EXISTS vyklad_artefakt (
    odtlacok TEXT PRIMARY KEY,
    subor    TEXT NOT NULL,
    run_id   TEXT NOT NULL,
    polozek  INTEGER NOT NULL,
    kedy     TEXT NOT NULL
);

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


DENNIK = Path(__file__).resolve().parent.parent / "state" / "evolucia.jsonl"

# Obsahy záznamov, ktoré v denníku už sú. Načíta sa pri prvom zápise v behu.
_VIDENE: Optional[set] = None


def _zapis_do_dennika(druh_zaznamu: str, data: dict,
                      conn: Optional[sqlite3.Connection] = None) -> None:
    """Kazdy zapis ide aj do textoveho denníka, riadok po riadku.

    Databaza je binarny subor. Ked ju pipeline commitne sucasne so mnou,
    git ju zlucit nevie a pri rebase `--ours` znamena UPSTREAM — takze moje
    zapisy zmiznu. 2026-08-19 sa to stalo trikrat za jeden den.

    JSONL sa zlucuje ciste, lebo sa doň len pripisuje. Ked databaza o zaznamy
    pride, `nacitaj_dennik()` ich vrati; zapisy su idempotentne, takze
    prehratie nic nezduplikuje.
    """
    # Zapisuj do denníka LEN pri zápise do ozajstnej databázy projektu.
    #
    # 2026-08-30: testovacie poznatky, ktoré som schválne robil na KÓPII
    # databázy, sa aj tak zapísali do zdieľaného denníka — a obnova ich
    # potom prehrala do živej databázy ako riadky #145 až #147. Kópia
    # ochránila databázu a nechránila nič iné, lebo denník je spoločný.
    if conn is not None:
        try:
            cesty = [r[2] for r in conn.execute("PRAGMA database_list")]
        except Exception:
            cesty = []
        if not any(c and Path(c).resolve() == DB_PATH.resolve() for c in cesty):
            return

    DENNIK.parent.mkdir(parents=True, exist_ok=True)
    # Poistka proti sebe samému. Zápis s rovnakým OBSAHOM (bez času) už
    # v denníku byť nemusí druhýkrát — a práve tým, že tam bol, sa denník
    # 2026-08-20 dvakrát nafúkol na desiatky MB: obnova prehrala zápis,
    # ktorý pri prehratí vznikol znova. Idempotenciu má mať každá funkcia
    # zvlášť, ale spoľahnúť sa na to nestačilo.
    telo = json.dumps({"typ": druh_zaznamu, **data}, ensure_ascii=False, sort_keys=True)
    # Súbor sa číta RAZ za beh, nie raz za zápis. Prvá verzia tejto poistky
    # (2026-08-20) čítala celý denník pri každom zápise: pri 50 000 riadkoch
    # stál jeden zápis 117 ms a sto zápisov 11,7 s. Oprava jednej chyby si
    # vypýtala meranie, inak by nahradila nafukovanie súboru spomalením behu.
    global _VIDENE
    if _VIDENE is None:
        _VIDENE = set()
        if DENNIK.exists():
            for r in DENNIK.read_text(encoding="utf-8").splitlines():
                if not r.strip():
                    continue
                try:
                    z = json.loads(r)
                except ValueError:
                    continue
                z.pop("kedy", None)
                _VIDENE.add(json.dumps(z, ensure_ascii=False, sort_keys=True))
    if telo in _VIDENE:
        return
    _VIDENE.add(telo)
    riadok = json.dumps({"typ": druh_zaznamu, "kedy": datetime.now(timezone.utc).isoformat(),
                          **data}, ensure_ascii=False, sort_keys=True)
    with DENNIK.open("a", encoding="utf-8") as f:
        f.write(riadok + "\n")


def dopln_dosah(conn: "sqlite3.Connection", *, tvrdenie_zaciatok: str,
                dosah: str) -> int:
    """Doplní `dosah` poznatku a zapíše to aj do denníka.

    Poznatok bez `dosah` je zápis bez dôsledku — `pouzitelne_poznatky()` ho
    zámerne nevracia, takže je mŕtvy. Fronta ich preto pýta doplniť.

    Poznatok sa hľadá podľa **začiatku tvrdenia**, nie podľa ID. ID nie je
    stabilné: databáza sa pri rebase stráca a prehratie z denníka pridelí
    nové (2026-08-19 sa to stalo trikrát). Tvrdenie je to jediné, čo prežije.

    Denník doteraz zaznamenával len vznik záznamu, nie jeho neskoršiu úpravu,
    takže doplnený `dosah` by prvý rebase zmazal a nikto by sa to nedozvedel.
    Preto ide úprava do denníka rovnako ako vznik.
    """
    r = conn.execute(
        "SELECT id FROM poznatky WHERE tvrdenie LIKE ? || '%'",
        (tvrdenie_zaciatok,)).fetchall()
    if len(r) != 1:
        raise ChybaEvolucie(
            f"začiatok tvrdenia {tvrdenie_zaciatok!r} sedí na {len(r)} poznatkov; "
            "musí sedieť práve na jeden")
    # Idempotencia. Bez nej sa obnova zacyklila do seba: prehratie zapísalo
    # nový záznam, ktorý ďalšie prehratie zase prehralo. Za jeden deň to
    # z 18 doplnení spravilo 589 840 riadkov a 153 MB (2026-08-20).
    teraz = conn.execute("SELECT dosah FROM poznatky WHERE id = ?",
                         (r[0][0],)).fetchone()[0]
    if (teraz or "") == (dosah or ""):
        return r[0][0]
    conn.execute("UPDATE poznatky SET dosah = ? WHERE id = ?", (dosah, r[0][0]))
    conn.commit()
    _zapis_do_dennika("dosah", {"tvrdenie_zaciatok": tvrdenie_zaciatok, "dosah": dosah})
    return r[0][0]


ZAKLAD = Path(__file__).resolve().parent.parent / "state" / "evolucia_zaklad.jsonl"


def nacitaj_dennik() -> list[dict]:
    """Zaznamy na prehratie po strate databazy: najprv zaklad, potom denník.

    Denník vznikol 2026-08-19 a zaznamenava len to, co vzniklo po nom. Test
    obnovy v ten den ukazal, ze z 89 poznatkov by vratil 31 — zvysnych 58 je
    starsich. `evolucia_zaklad.jsonl` je jednorazovy snimok tychto starsich
    zaznamov, aby obnova nebola len ciastocna. Cita sa PRVY, lebo su starsie
    a vazby (nahradenie) sa riesia podla poradia.
    """
    out = []
    for subor in (ZAKLAD, DENNIK):
        if not subor.exists():
            continue
        for r in subor.read_text(encoding="utf-8").splitlines():
            r = r.strip()
            if r:
                try:
                    out.append(json.loads(r))
                except ValueError:
                    continue
    return out


def _dnes() -> str:
    return date.today().isoformat()


# Stĺpce doplnené až po tom, čo tabuľka vznikla. `CREATE TABLE IF NOT EXISTS`
# existujúcu tabuľku NEMENÍ, takže bez tohto zoznamu by databáza, ktorá vznikla
# skôr, nový stĺpec nikdy nedostala. Presne to sa stalo 2026-08-17: pridal som
# `domnienky.poznatok_id` ručným ALTER-om vo svojej relácii, a vzdialená
# databáza v CI ho nemala ako ho získať. Migrácia patrí do kódu, nie do rúk.
MIGRACIE = [
    ("domnienky", "poznatok_id", "INTEGER"),
    # Poznatok často nezakladá novú domnienku — podopiera existujúcu. Bez tohto
    # stĺpca sa dal len ignorovať alebo naň nasilu vyrobiť ďalšia hypotéza, čo
    # by z registra spravilo zoznam takmer rovnakých viet.
    ("poznatky", "domnienka_id", "INTEGER"),
    # Poznatok nemusí viesť k hypotéze — môže rovno spôsobiť zmenu alebo
    # experiment. Bez týchto dvoch stĺpcov ich fronta naďalej ponúkala ako
    # „bez dôsledku" a tlačila vymyslieť hypotézu k niečomu, na čo sa už
    # konalo. To je motor špirály takmer rovnakých pravidiel.
    ("poznatky", "rozhodnutie_id", "INTEGER"),
    ("poznatky", "experiment_id", "INTEGER"),
    # Pôvodná `experiments` mala názov, hypotézu a metriku, ale ani základ, ani
    # kandidáta — teda presne to, čo z experimentu robí experiment. Preto bola
    # osem mesiacov prázdna: zapísať sa do nej dala iba mienka.
    ("experiments", "domnienka_id", "INTEGER"),
    ("experiments", "trieda", "TEXT"),
    ("experiments", "metrika", "TEXT"),
    ("experiments", "sposob_merania", "TEXT"),
    ("experiments", "zaklad_popis", "TEXT"),
    ("experiments", "zaklad_hodnota", "REAL"),
    ("experiments", "kandidat_popis", "TEXT"),
    ("experiments", "kandidat_hodnota", "REAL"),
    ("experiments", "smer", "TEXT"),
    ("experiments", "vzorka", "INTEGER"),
    ("experiments", "naozivo", "INTEGER"),
    ("experiments", "rozhodnutie", "TEXT"),
    ("experiments", "poucenie", "TEXT"),
    # 2026-08-30: stĺpec bol 22. 8. pridaný ručným ALTER TABLE do lokálnej
    # databázy a do MIGRACIE nie. Test behu si schému stavia z kódu, takže
    # CI padalo na „table poznatky has no column named odvodene_z" — a padalo
    # osem behov po sebe, kým si toho majiteľ nevšimol. Ručná zmena databázy
    # nie je zmena systému.
    ("poznatky", "odvodene_z", "INTEGER"),
    # Stvrty druh dosledku. Poznatok #129: cast nasich poznatkov ma dosledok,
    # ktory schema nevedela zaznamenat - ZAPISANE PRAVIDLO v CLAUDE.md alebo
    # memory/07_Constraints.md. Take poznatky zostavali "bez dosledku" navzdy
    # a fronta ich ponukala donekonecna, hoci svoju ulohu davno splnili.
    ("poznatky", "pravidlo", "TEXT"),
    ("rozhodnutia", "datum_revizie", "TEXT"),
    ("rozhodnutia", "vrstva", "TEXT"),
]


def priprav(conn: Optional[sqlite3.Connection] = None) -> None:
    """Vytvorí tabuľky a doplní chýbajúce stĺpce. Bezpečné spustiť opakovane."""
    vlastne = conn is None
    conn = conn or get_connection()
    try:
        conn.executescript(SCHEMA)
        for tabulka, stlpec, typ in MIGRACIE:
            existujuce = {r["name"] for r in conn.execute(
                f"PRAGMA table_info({tabulka})")}
            if existujuce and stlpec not in existujuce:
                conn.execute(f"ALTER TABLE {tabulka} ADD COLUMN {stlpec} {typ}")
        conn.commit()
    finally:
        if vlastne:
            conn.close()


# --- zámok behu ------------------------------------------------------------

ZAMOK_MINUT = 45          # dlhší než najdlhší doterajší beh, kratší než cyklus


class ZamokObsadeny(Exception):
    """Iný beh práve mení stav. Toto nie je porucha — je to ochrana."""


def _teraz() -> datetime:
    return datetime.now()


def zamkni(conn: sqlite3.Connection, *, run_id: str, vlastnik: str,
           minut: int = ZAMOK_MINUT) -> None:
    """Získa zámok, alebo vyhodí ZamokObsadeny. Nikdy nečaká.

    Prebratie po páde je viazané na `plati_do`, nie na kontrolu procesu: beh
    v cudzom prostredí sa overiť nedá, takže jediné bezpečné kritérium je čas.
    Živý beh si zámok predlžuje cez `predlz_zamok`, čím sa chráni pred
    prebratím — a beh, ktorý padol, prestane predlžovať a zámok po termíne
    uvoľní sám.
    """
    teraz = _teraz()
    r = conn.execute("SELECT * FROM beh_zamok WHERE id=1").fetchone()
    # Vlastný zámok nie je prekážka, je to obnovenie. Beh zabitý uprostred
    # nechá zámok v stave BEZI (os._exit preskočí aj `finally`) a bez tejto
    # vetvy by sa nevedel obnoviť, kým zámok nevyprší — teda 45 minút po páde,
    # ktorý trval sekundu. Overené skutočným pádom 2026-08-17, nie úvahou.
    if r is not None and r["run_id"] == run_id:
        conn.execute("UPDATE beh_zamok SET plati_do=?, stav='BEZI' WHERE id=1",
                     ((teraz + timedelta(minutes=minut)).isoformat(),))
        conn.commit()
        return
    if r is not None and r["stav"] == "BEZI":
        try:
            plati_do = datetime.fromisoformat(r["plati_do"])
        except (TypeError, ValueError):
            plati_do = teraz                      # nečitateľný termín = vypršaný
        if plati_do > teraz:
            raise ZamokObsadeny(
                f"beh {r['run_id']} ({r['vlastnik']}) drží zámok do "
                f"{r['plati_do']}; tento beh sa nespúšťa"
            )
        # vypršaný zámok = beh padol; zaznamenáme to, nemlčíme o tom
        conn.execute("UPDATE beh_zamok SET stav='PADOL' WHERE id=1")

    conn.execute(
        "INSERT INTO beh_zamok (id, run_id, vlastnik, zacal, plati_do, stav) "
        "VALUES (1,?,?,?,?,'BEZI') "
        "ON CONFLICT(id) DO UPDATE SET run_id=excluded.run_id, "
        "vlastnik=excluded.vlastnik, zacal=excluded.zacal, "
        "plati_do=excluded.plati_do, stav='BEZI'",
        (run_id, vlastnik, teraz.isoformat(),
         (teraz + timedelta(minutes=minut)).isoformat()),
    )
    conn.commit()


def predlz_zamok(conn: sqlite3.Connection, *, run_id: str,
                 minut: int = ZAMOK_MINUT) -> bool:
    """Predĺži platnosť. Vráti False, ak zámok medzitým prevzal niekto iný."""
    r = conn.execute("SELECT run_id FROM beh_zamok WHERE id=1").fetchone()
    if r is None or r["run_id"] != run_id:
        return False
    conn.execute("UPDATE beh_zamok SET plati_do=? WHERE id=1",
                 ((_teraz() + timedelta(minutes=minut)).isoformat(),))
    conn.commit()
    return True


def odomkni(conn: sqlite3.Connection, *, run_id: str) -> bool:
    """Uvoľní zámok. Cudzí zámok neuvoľní — vráti False."""
    r = conn.execute("SELECT run_id FROM beh_zamok WHERE id=1").fetchone()
    if r is None or r["run_id"] != run_id:
        return False
    conn.execute("UPDATE beh_zamok SET stav='HOTOVO' WHERE id=1")
    conn.commit()
    return True


def zluc_duplicitne_poznatky(conn: sqlite3.Connection) -> int:
    """Zlúči poznatky s rovnakým zdrojom aj tvrdením a zachová väzby.

    Zápis je od 2026-08-17 idempotentný, takže nové duplikáty nevznikajú. Toto
    je oprava tých, ktoré vznikli predtým — a musí byť v kóde, lebo tú istú
    databázu opravuje aj CI, nielen jedna relácia. Mazať sa smie až po
    prepojení odkazov, inak to zastaví cudzí kľúč (a správne).
    """
    dvojice = conn.execute(
        "SELECT MIN(id) prezije, MAX(id) zmaze FROM poznatky "
        "GROUP BY zdroj, tvrdenie HAVING COUNT(*) > 1"
    ).fetchall()
    for d in dvojice:
        conn.execute("UPDATE vyklad SET poznatok_id=? WHERE poznatok_id=?",
                     (d["prezije"], d["zmaze"]))
        conn.execute("UPDATE domnienky SET poznatok_id=? WHERE poznatok_id=?",
                     (d["prezije"], d["zmaze"]))
        conn.execute("DELETE FROM poznatky WHERE id=?", (d["zmaze"],))
    conn.commit()
    return len(dvojice)


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
    odvodene_z: Optional[int] = None,
    obnova: bool = False,
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
    # Prekonané a vyvrátené sa zámerne nepočítajú: ak to isté tvrdenie znovu
    # pozorujeme, má vzniknúť nový záznam. Pri OBNOVE z denníka to ale neplatí —
    # tam nič nepozorujeme, len rekonštruujeme, takže prehratie nahradeného
    # poznatku ho vzkriesilo ako nový (2026-08-19: #94 sa vrátil ako #96 bez
    # väzby na #95). Preto sa pri obnove pozeráme na všetky stavy.
    if obnova:
        uz = conn.execute(
            "SELECT id FROM poznatky WHERE zdroj = ? AND tvrdenie = ?",
            (zdroj, tvrdenie)).fetchone()
    else:
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
            dokaz, dosah, stav, nahradza, odvodene_z)
           VALUES (?,?,?,?,?,?,?,?,?,'NOVY',?,?)""",
        (tvrdenie, druh, zdroj, typ_zdroja, zdroj_datum, _dnes(), plati_do,
         dokaz, dosah, nahradza, odvodene_z),
    )
    if nahradza is not None:
        conn.execute("UPDATE poznatky SET stav='PREKONANY' WHERE id=?", (nahradza,))
    conn.commit()
    nove_id = int(cur.lastrowid)
    _zapis_do_dennika("poznatok", {
        "id": nove_id, "tvrdenie": tvrdenie, "druh": druh, "zdroj": zdroj,
        "typ_zdroja": typ_zdroja, "zdroj_datum": zdroj_datum, "dokaz": dokaz,
        "dosah": dosah, "nahradza": nahradza,
        # ID nie je stabilné: po obnove sa prideľujú nové, takže väzba
        # nahradenia zapísaná ako číslo ukazuje po prehratí inam alebo nikam
        # (2026-08-19: PREKONANY sa po obnove vrátil ako NOVY). Tvrdenie je
        # jediné, čo prežije, tak ho zapisujeme vedľa.
        "nahradza_tvrdenie": (
            conn.execute("SELECT tvrdenie FROM poznatky WHERE id=?",
                         (nahradza,)).fetchone() or [None])[0]
        if nahradza is not None else None,
        # to isté platí pre pôvod: číslo po obnove ukazuje inam
        "odvodene_z": odvodene_z,
        "odvodene_z_tvrdenie": (
            conn.execute("SELECT tvrdenie FROM poznatky WHERE id=?",
                         (odvodene_z,)).fetchone() or [None])[0]
        if odvodene_z is not None else None}, conn=conn)
    return nove_id


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
        # VYSLEDOK je koniec reťaze, nie čakajúce pozorovanie: vlastné overené
        # meranie už odpoveď dalo. Núkať naň hypotézu znamená pýtať si domnienku
        # o niečom, čo je zmerané — a fronta by potom nikdy nevyprázdnila.
        "SELECT * FROM poznatky p WHERE p.dosah IS NOT NULL AND TRIM(p.dosah) <> '' "
        # PREKONANY sem tiež nepatrí: nahradený poznatok už dôsledok mal, len
        # ho prevzal jeho nástupca. Filtrovať iba VYVRATENY znamenalo, že
        # prekonané položky sa vracali do fronty donekonečna.
        "AND p.stav NOT IN ('VYVRATENY','PREKONANY') AND p.druh <> 'VYSLEDOK' "
        "AND p.domnienka_id IS NULL "
        # Dôsledok nie je iba hypotéza. Poznatok, ktorý viedol k zmene alebo
        # k experimentu, svoju úlohu splnil — ponúkať ho ďalej znamená pýtať
        # si druhú formuláciu toho istého.
        "AND p.rozhodnutie_id IS NULL AND p.experiment_id IS NULL "
        # Stvrty dosledok: poznatok, z ktoreho vzniklo zapisane pravidlo.
        "AND (p.pravidlo IS NULL OR TRIM(p.pravidlo) = '') "
        "AND NOT EXISTS (SELECT 1 FROM domnienky d WHERE d.poznatok_id = p.id) "
        "ORDER BY p.id DESC LIMIT ?", (limit,)
    ))


def _zapis_vazbu(conn: sqlite3.Connection, poznatok_id: int, pole: str,
                 ciel_id: int) -> None:
    """Väzbu zapíše aj do denníka, kľúčovanú TVRDENÍM poznatku.

    2026-08-21: dvadsať väzieb na rozhodnutie zmizlo pri prvom rebase, lebo
    žiadna z piatich funkcií meniacich stav do denníka nezapisovala. Obnova
    poznatok vytvorí nanovo — a bez väzby, takže fronta ho znovu ponúkne ako
    „bez dôsledku". Je to tretí výskyt tej istej triedy chyby za jeden deň
    (po `dosah` a po posúdených dvojiciach), preto sa opravuje naraz pre
    všetky väzby, nie po jednej.

    Kľúčom je tvrdenie, nie id: pri obnove sa id prideľujú nanovo.
    """
    r = conn.execute("SELECT tvrdenie FROM poznatky WHERE id=?", (poznatok_id,)).fetchone()
    if r is None:
        return
    _zapis_do_dennika("vazba", {"tvrdenie": r[0], "pole": pole, "ciel_id": ciel_id})



def odvodene_od(conn: sqlite3.Connection, poznatok_id: int) -> list[tuple[int, str]]:
    """Všetko, čo bolo z tohto poznatku odvodené — do hĺbky, nie o úroveň.

    Prečo to existuje. Architektúra „druhého mozgu ako kompilátora"
    (rvaniaaaa, 2026-08-20) pomenúva vlastnú charakteristickú poruchu:
    *„Zlý zdroj v knižnici sa ľahko odstráni. Zlý zdroj v kompilátore sa
    dotkol pätnástich stránok skôr, než si to zbadal."*

    Nám sa to stalo 2026-08-22, ešte než sme ten text čítali. Tvrdenie
    „scenár S9 sa splniť nedá" napísal ten, kto beh spravil. Prešlo do
    podkladu, odtiaľ cez dvoch nezávislých hodnotiteľov (obaja s výhradou,
    že to overiť nevedia — podklad definíciu scenára neobsahoval), odtiaľ
    do môjho zhrnutia a do dvoch dokumentov ako plánovací blokátor. Overenie
    proti zdroju trvalo dve minúty a tvrdenie neobstálo.

    Retrieval by tú vetu vyniesol raz. Kompilácia ju zabudovala štyrikrát.
    Preto poznatok nesie `odvodene_z` a preto sa dá spýtať opačne: keď toto
    padne, čo všetko treba prečítať znova.
    """
    von: list[tuple[int, str]] = []
    front = [poznatok_id]
    videne = {poznatok_id}
    while front:
        r = conn.execute(
            "SELECT id, tvrdenie FROM poznatky WHERE odvodene_z IN "
            f"({','.join('?' * len(front))})", front).fetchall()
        front = []
        for i, t in r:
            if i in videne:
                continue
            videne.add(i)
            von.append((i, t))
            front.append(i)
    return von


def siroty(conn: sqlite3.Connection) -> list[tuple[int, str]]:
    """Aktívne poznatky, ktoré nie sú napojené na nič.

    Poznatok bez väzby je záznam v kartotéke, nie skompilovaná znalosť.
    Nie každý väzbu mať musí — samostatné pozorovanie je legitímne — ale
    podiel sirôt je meradlom toho, či systém kompiluje alebo len ukladá.
    2026-08-22: 56 zo 124 aktívnych, teda 45 %.
    """
    return conn.execute(
        "SELECT id, tvrdenie FROM poznatky WHERE rozhodnutie_id IS NULL "
        "AND domnienka_id IS NULL AND experiment_id IS NULL AND nahradza IS NULL "
        "AND odporuje IS NULL AND odvodene_z IS NULL "
        "AND (pravidlo IS NULL OR TRIM(pravidlo) = '') "
        "AND stav NOT IN ('PREKONANY','VYVRATENY','ZRUSENY') ORDER BY id").fetchall()


def pripoj_k_pravidlu(conn: sqlite3.Connection, poznatok_id: int,
                      pravidlo: str) -> None:
    """Poznatok viedol k zapísanému pravidlu — to je tiež dôsledok.

    `pravidlo` je cesta a stručne čo tam pribudlo, napríklad
    ``CLAUDE.md: riadok o bráne kontrola_dosiahnutelnosti.py``.

    Bez tohto poľa pozná fronta len tri dôsledky (domnienka, rozhodnutie,
    experiment) a poznatok, z ktorého vzniklo pravidlo, ponúka donekonečna
    ako „bez dôsledku". Poznatok #129 to pomenoval a nechal rozhodnutie
    otvorené; rozhodnuté 2026-08-30 v prospech štvrtej väzby, lebo tá
    druhá možnosť — čítať tú časť fronty ako šum — znamená mať vo fronte
    trvalý šum.
    """
    if not pravidlo.strip():
        raise ChybaEvolucie("väzba na pravidlo musí povedať KDE a ČO, nie len že áno")
    conn.execute("UPDATE poznatky SET pravidlo=? WHERE id=?", (pravidlo, poznatok_id))
    conn.commit()
    _zapis_do_dennika("pravidlo", {
        "poznatok_id": poznatok_id, "pravidlo": pravidlo,
        "tvrdenie": (conn.execute("SELECT tvrdenie FROM poznatky WHERE id=?",
                                  (poznatok_id,)).fetchone() or [None])[0]}, conn=conn)

def pripoj_k_domnienke(conn: sqlite3.Connection, poznatok_id: int,
                      domnienka_id: int) -> None:
    """Poznatok podopiera existujúcu domnienku, nezakladá novú.

    Bez toho by sa dôkaz dal iba ignorovať, alebo by sa naň nasilu vyrobila
    ďalšia takmer rovnaká hypotéza — a register domnienok by prestal byť
    zoznamom toho, na čom stojíme.
    """
    d = conn.execute("SELECT stav FROM domnienky WHERE id=?", (domnienka_id,)).fetchone()
    if d is None:
        raise ChybaEvolucie(f"domnienka {domnienka_id} neexistuje")
    conn.execute("UPDATE poznatky SET domnienka_id=? WHERE id=?",
                 (domnienka_id, poznatok_id))
    conn.commit()
    _zapis_vazbu(conn, poznatok_id, "domnienka_id", domnienka_id)


def pripoj_k_rozhodnutiu(conn: sqlite3.Connection, poznatok_id: int,
                         rozhodnutie_id: int) -> None:
    """Poznatok viedol priamo k zmene, nie k hypotéze.

    Väčšina meraní o vlastnom systéme takto aj funguje: zistí sa porucha a
    hneď sa opraví. Nútiť medzi ne hypotézu je obrad, nie poznanie.
    """
    if conn.execute("SELECT 1 FROM rozhodnutia WHERE id=?",
                    (rozhodnutie_id,)).fetchone() is None:
        raise ChybaEvolucie(f"rozhodnutie {rozhodnutie_id} neexistuje")
    conn.execute("UPDATE poznatky SET rozhodnutie_id=? WHERE id=?",
                 (rozhodnutie_id, poznatok_id))
    conn.commit()
    _zapis_vazbu(conn, poznatok_id, "rozhodnutie_id", rozhodnutie_id)


def pripoj_k_experimentu(conn: sqlite3.Connection, poznatok_id: int,
                         experiment_id: int) -> None:
    """Poznatok sa stal základom merania. To je silnejší dôsledok než hypotéza."""
    if conn.execute("SELECT 1 FROM experiments WHERE id=?",
                    (experiment_id,)).fetchone() is None:
        raise ChybaEvolucie(f"experiment {experiment_id} neexistuje")
    conn.execute("UPDATE poznatky SET experiment_id=? WHERE id=?",
                 (experiment_id, poznatok_id))
    conn.commit()
    _zapis_vazbu(conn, poznatok_id, "experiment_id", experiment_id)


def _zabezpec_tabulku_dvojic(conn: sqlite3.Connection) -> None:
    """Pamäť posúdených dvojíc. Bez nej sa tá istá dvojica vracia donekonečna.

    2026-08-20: detektor ponúkal 33 dvojíc a nikde sa neukladalo, že som ich
    už videl a zamietol — takže fronta pýtala rozsúdiť tie isté znova. Hrana,
    ktorú niekto posúdil ako „toto nie je rozpor", je rovnako platný výsledok
    ako hrana potvrdená; len ju treba zapísať.

    Kľúčom je TVRDENIE, nie id: id sa pri obnove z denníka menia.
    """
    conn.execute("""CREATE TABLE IF NOT EXISTS posudene_dvojice (
        a_tvrdenie TEXT NOT NULL,
        b_tvrdenie TEXT NOT NULL,
        rozhodnutie TEXT NOT NULL,   -- ROZPOR | NIE_JE_ROZPOR
        dovod TEXT,
        kedy TEXT NOT NULL,
        PRIMARY KEY (a_tvrdenie, b_tvrdenie))""")
    conn.commit()


def zamietni_dvojicu(conn: sqlite3.Connection, *, a_tvrdenie: str,
                     b_tvrdenie: str, dovod: str) -> None:
    """Zapíše, že dvojica bola posúdená a rozpor to nie je."""
    _zabezpec_tabulku_dvojic(conn)
    par = tuple(sorted((a_tvrdenie, b_tvrdenie)))
    # Idempotencia, rovnako ako pri dopln_dosah(). Bez nej obnova prehrá zápis,
    # ktorý sama vyrobila: 2026-08-20 z 12 dvojíc 12 288 riadkov. Túto chybu
    # som v ten deň spravil DVAKRÁT, raz pri dosahu a raz tu — pravidlo
    # nestačí, musí byť v kóde.
    uz = conn.execute(
        "SELECT rozhodnutie FROM posudene_dvojice WHERE a_tvrdenie=? AND b_tvrdenie=?",
        (par[0], par[1])).fetchone()
    if uz is not None and uz[0] == "NIE_JE_ROZPOR":
        return
    conn.execute(
        "INSERT OR REPLACE INTO posudene_dvojice "
        "(a_tvrdenie, b_tvrdenie, rozhodnutie, dovod, kedy) VALUES (?,?,?,?,?)",
        (par[0], par[1], "NIE_JE_ROZPOR", dovod, _dnes()))
    conn.commit()
    _zapis_do_dennika("dvojica", {"a_tvrdenie": par[0], "b_tvrdenie": par[1],
                                  "rozhodnutie": "NIE_JE_ROZPOR", "dovod": dovod})


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
    # Procesné slová sem nepatria. „OTVORENÉ A PREČÍTANÉ“ som si písal na začiatok
    # tvrdení a detektor na tom 2026-08-18 postavil falošný rozpor medzi dvoma
    # poznatkami o úplne iných veciach. Zhoda v tom, AKO poznatok vznikol, nie je
    # zhoda v tom, ČO tvrdí. Markery sú odvtedy v poli `dokaz`, toto je poistka.
    stop = {"a", "aj", "ako", "ale", "na", "sa", "sú", "je", "to", "že", "pre",
            "the", "and", "for", "with", "that", "ktoré", "ktorá", "ktorý", "nie",
            "otvorené", "prečítané", "vlastné", "meranie", "uvádza", "opisuje",
            "hovorí", "ukazuje", "podľa", "zdroj", "článok", "práca",
            # Vlastné meno a doména. 2026-08-19 detektor ponúkol štyri „rozpory",
            # ktorých spoločné slová boli `biznis, github, studio` — teda náš
            # vlastný web, ktorý sa spomína skoro v každom poznatku o nás.
            # Zhoda v tom, O KOM poznatok je, nie je zhoda v tom, ČO tvrdí,
            # a bez tohto by tá dvojica vznikala donekonečna.
            "biznis", "studio", "github", "studiO", "biznis-studio",
            # Rovnaká trieda: nástroje a povrchy, ktoré používame všade.
            "search", "console", "google", "stránok", "stránka", "stránky"}

    def slova(text: str) -> set[str]:
        return {w for w in re.findall(r"\w{5,}", text.lower()) if w not in stop}

    _zabezpec_tabulku_dvojic(conn)
    uz_posudene = {(r[0], r[1]) for r in conn.execute(
        "SELECT a_tvrdenie, b_tvrdenie FROM posudene_dvojice")}

    dvojice = []
    for i, a in enumerate(riadky):
        sa_ = slova(a["tvrdenie"])
        for b in riadky[i + 1:]:
            if tuple(sorted((a["tvrdenie"], b["tvrdenie"]))) in uz_posudene:
                continue
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
    # Rozpor je výsledok úsudku, nie odvodený údaj — bez zápisu do denníka
    # by po rebase zmizol a dvojica by sa vrátila do fronty ako neposúdená.
    # Kľúčom je text oboch poznatkov, nie ich id (po obnove sú iné).
    def _t(i):
        r = conn.execute("SELECT tvrdenie FROM poznatky WHERE id=?", (i,)).fetchone()
        return r[0] if r else None
    _zapis_do_dennika("rozpor", {
        "novy_id": novy_id, "stary_id": stary_id, "rozhodnutie": rozhodnutie,
        "novy_tvrdenie": _t(novy_id), "stary_tvrdenie": _t(stary_id)}, conn=conn)


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
    # Rozhodnutá domnienka je výsledok, nie medzistav. Bez denníka by sa po
    # rebase vrátila medzi otvorené a merala by sa znova — s tým rozdielom,
    # že prvý výsledok by už nikto nevidel.
    _zapis_do_dennika("domnienka_rozhodnuta", {
        "domnienka_id": domnienka_id, "stav": stav, "vysledok": vysledok,
        "domnienka_text": (conn.execute(
            "SELECT domnienka FROM domnienky WHERE id=?",
            (domnienka_id,)).fetchone() or [None])[0]}, conn=conn)


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
    nove_id = int(cur.lastrowid)
    _zapis_do_dennika("rozhodnutie", {
        "id": nove_id, "co": co, "preco": preco, "vratenie": vratenie,
        "ocakavany_ucinok": ocakavany_ucinok, "datum_revizie": datum_revizie,
        "vrstva": vrstva, "zamietnute": zamietnute, "autorita": autorita})
    return nove_id


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
    # Bez zápisu do denníka by výsledok zmizol pri najbližšom rebase — rovnako
    # ako 20 väzieb 2026-08-19. Kľúčom je TEXT rozhodnutia, nie id: po obnove
    # sa prideľujú nové čísla a číslo by ukazovalo inam alebo nikam.
    _zapis_do_dennika("ucinok", {
        "rozhodnutie_id": rozhodnutie_id,
        "rozhodnutie_co": (conn.execute("SELECT co FROM rozhodnutia WHERE id=?",
                                        (rozhodnutie_id,)).fetchone() or [None])[0],
        "skutocny_ucinok": skutocny_ucinok}, conn=conn)


def nevyhodnotene_rozhodnutia(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Zmeny po termíne revízie, ktorým nikto neporovnal očakávanie so skutočnosťou."""
    return list(conn.execute(
        "SELECT * FROM rozhodnutia WHERE skutocny_ucinok IS NULL "
        "AND datum_revizie <= ? ORDER BY vrstva, datum_revizie", (_dnes(),)
    ))


def _riesene_zdroje(conn: sqlite3.Connection) -> dict[str, str]:
    """Za každý zdroj dátum poslednej zmeny, ktorá ho menovala.

    Väzba je cez meno zdroja v texte rozhodnutia, nie cez cudzí kľúč — hrubé
    zámerne: rozhodnutie často mení viac zdrojov naraz a viazať to formálne by
    znamenalo vypĺňať väzby, na ktoré sa zabudne. Ak sa dôvod zahodenia po
    oprave vráti, návrh sa objaví znova, takže hrubosť tu nič nezakryje.
    """
    von: dict[str, str] = {}
    zdroje = [z for (z,) in conn.execute("SELECT DISTINCT zdroj FROM vyklad")]
    for r in conn.execute("SELECT co, preco, zapisane FROM rozhodnutia").fetchall():
        text = f"{r['co']} {r['preco']}"
        for z in zdroje:
            kratke = z.split(":")[-1]
            if kratke and kratke in text:
                if r["zapisane"] > von.get(z, ""):
                    von[z] = r["zapisane"]
    return von


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
    riesene = _riesene_zdroje(conn)

    # 1. Zdroj, ktorého zahodenia sa opakujú z toho istého dôvodu, nie je slabý
    #    náhodou — sníma zlú vec. Počítajú sa LEN zahodenia po poslednej zmene,
    #    ktorá ten zdroj menovala: návrh, ktorý sa nedá uzavrieť, by hnal
    #    donekonečna po tom istom aj po oprave. Ak sa dôvod vráti, návrh sa
    #    vráti tiež — a to je správne, lebo oprava vtedy nezabrala.
    dovody = conn.execute(
        "SELECT zdroj, duvod, kedy FROM vyklad WHERE rozhodnutie='ZAHODENE'"
    ).fetchall()
    zhluky: dict[tuple[str, str], int] = {}
    for d in dovody:
        if d["kedy"] <= riesene.get(d["zdroj"], ""):
            continue
        zhluky[(d["zdroj"], d["duvod"])] = zhluky.get((d["zdroj"], d["duvod"]), 0) + 1
    dovody = [{"zdroj": z, "duvod": u, "n": n}
              for (z, u), n in zhluky.items() if n >= 2]
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
        "OR duvod LIKE '%nestačí%') AND kedy > ? GROUP BY zdroj",
        (None,)
    ).fetchall() if False else [
        r for r in conn.execute(
            "SELECT zdroj, duvod, kedy FROM vyklad WHERE rozhodnutie='ZAHODENE' "
            "AND (duvod LIKE '%titulok%' OR duvod LIKE '%Iba názov%' "
            "OR duvod LIKE '%nestačí%')")
        if r["kedy"] > riesene.get(r["zdroj"], "")
    ]
    zhluk2: dict[str, int] = {}
    for r in riedke:
        zhluk2[r["zdroj"]] = zhluk2.get(r["zdroj"], 0) + 1
    # Aspoň dve zahodenia, rovnako ako pri zhluku dôvodov vyššie. Jedno jediné
    # je udalosť, nie porucha — a trvalý príznak z jednej udalosti je presne to,
    # čo z brány spraví šum, ktorý sa naučím preskakovať.
    riedke = [{"zdroj": z, "n": n} for z, n in zhluk2.items() if n >= 2]
    for r in riedke:
        navrhy.append({
            "co": f"{r['zdroj']}: {r['n']}× zahodené preto, že titulok nestačil",
            "preco": "zbierame názvy tam, kde je poznatok až v texte — "
                     "zdroj potrebuje dočítanie obsahu, nie zrušenie",
            "autorita": "stroj",
        })

    # 3. Poznatok bez `dosah` je zápis bez dôsledku. Ak ich je veľa, vykladáme
    #    len nazbierané, nie premyslené.
    # Prekonaný, vyvrátený ani zrušený poznatok už dôsledok mať nemá — je to
    # história, nie skládka. Bez tejto podmienky sa fronta zasekla na jedinom
    # nahradenom zázname (#96, 2026-08-19) a pýtala ho doplniť donekonečna,
    # čím by brána začala rozhodovať, čo sa robí.
    bez_dosahu = conn.execute(
        "SELECT COUNT(*) AS n FROM poznatky "
        "WHERE (dosah IS NULL OR TRIM(dosah)='') "
        "AND stav NOT IN ('PREKONANY','VYVRATENY','ZRUSENY')"
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

    # Podiel sirôt je meradlom toho, ci systém kompiluje alebo len ukladá:
    # poznatok bez väzby je záznam v kartotéke. Nehlási sa po jednom — to by
    # zaplavilo frontu 56 krokmi — ale ako jeden krok s číslom, keď podiel
    # prekročí tretinu. Nie každý poznatok väzbu mať musí; preto prah, nie nula.
    _siroty = siroty(conn)
    _aktivne = conn.execute(
        "SELECT COUNT(*) FROM poznatky WHERE stav NOT IN "
        "('PREKONANY','VYVRATENY','ZRUSENY')").fetchone()[0] or 1
    if len(_siroty) * 3 > _aktivne:
        kroky.append({
            "poradie": 4.6,
            "co": f"Napojiť siroty: {len(_siroty)} z {_aktivne} aktívnych poznatkov "
                  f"({100 * len(_siroty) // _aktivne} %) nie je napojených na nič",
            "ako": "prejsť ich a pri každom rozhodnúť: patrí k rozhodnutiu, "
                   "k domnienke, k experimentu, je odvodený z iného poznatku — "
                   "alebo naozaj stojí sám a to je v poriadku",
            "vyvratilo_by": "siroty sú samostatné pozorovania, ktoré väzbu mať "
                            "nemajú; potom je prah zle nastavený, nie dáta",
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
