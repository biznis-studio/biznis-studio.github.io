"""Experiment — porovnanie kandidáta so základom, nie názor modelu.

Tabuľka `experiments` bola v databáze od začiatku prázdna. Nie preto, že by na
ňu nebol čas, ale preto, že jej chýbalo to, čo z experimentu robí experiment:
základ, kandidát a spôsob merania. Bez nich sa dá zapísať iba mienka.

Tri pravidlá, ktoré tento súbor vynucuje, lebo bez nich sa systém naučí
sám sebe prikyvovať:

1. **Základ je nedotknuteľný.** Zmeria sa pred tým, než kandidát existuje, a už
   sa nemení. Kandidát, ktorý si smie prepísať vlastný základ, vyhrá vždy.
2. **Rozhodnutie potrebuje obe čísla.** Bez nameraného kandidáta sa nedá
   povýšiť ani zamietnuť — len počkať. „Model si myslí, že B je lepšie" nie je
   výsledok experimentu.
3. **Zamietnutý nápad sa pamätá.** Pred založením sa hľadá podobná hypotéza,
   ktorá už raz padla, aby sa tá istá myšlienka nevracala ako nová.

Čo tu zámerne NIE JE: štatistická významnosť. Pri vzorkách, aké máme, by to
bola matematika predstierajúca istotu. Namiesto toho sa zapisuje veľkosť vzorky
a či šlo o meranie naživo alebo offline — a čítajúci si spraví úsudok sám.
"""

from __future__ import annotations

import re
import sqlite3
from datetime import date
from typing import Callable, Optional

STAVY = ("NAVRHNUTY", "ZAKLAD_ZMERANY", "KANDIDAT_ZMERANY", "UZAVRETY")
ROZHODNUTIA = ("POVYSENY", "ZAMIETNUTY", "NEROZHODNUTY")

# Stĺpce, ktoré pôvodnej tabuľke chýbali. Dopĺňa ich `priprav()` v evolution.py.
MIGRACIE = [
    ("experiments", "domnienka_id", "INTEGER"),
    ("experiments", "trieda", "TEXT"),
    ("experiments", "metrika", "TEXT"),
    ("experiments", "sposob_merania", "TEXT"),
    ("experiments", "zaklad_popis", "TEXT"),
    ("experiments", "zaklad_hodnota", "REAL"),
    ("experiments", "kandidat_popis", "TEXT"),
    ("experiments", "kandidat_hodnota", "REAL"),
    ("experiments", "smer", "TEXT"),          # 'nizsie_lepsie' | 'vyssie_lepsie'
    ("experiments", "vzorka", "INTEGER"),
    ("experiments", "naozivo", "INTEGER"),    # 1 = meranie na trhu, 0 = offline
    ("experiments", "rozhodnutie", "TEXT"),
    ("experiments", "poucenie", "TEXT"),
]


class ChybaExperimentu(Exception):
    """Krok, ktorý by z experimentu spravil mienku."""


def _slova(text: str) -> set[str]:
    return {w for w in re.findall(r"\w{5,}", (text or "").lower())}


def podobny_padnuty(conn: sqlite3.Connection, hypoteza: str) -> Optional[sqlite3.Row]:
    """Nájde už zamietnutý experiment s podobnou hypotézou.

    Podobnosť je prekryv slov, nie význam — hrubé, ale funguje ako brzda proti
    tomu, aby sa ten istý nápad vracal ako nový. Zamietnutie nie je zákaz:
    volajúci sa môže rozhodnúť pokračovať, ale musí to spraviť vedome.
    """
    ciel = _slova(hypoteza)
    if len(ciel) < 3:
        return None
    for r in conn.execute(
            "SELECT * FROM experiments WHERE rozhodnutie='ZAMIETNUTY'"):
        spolocne = ciel & _slova(r["hypothesis"])
        if len(spolocne) >= max(3, len(ciel) // 3):
            return r
    return None


def zaloz(conn: sqlite3.Connection, *, nazov: str, hypoteza: str, trieda: str,
          metrika: str, sposob_merania: str, smer: str,
          zaklad_popis: str, zaklad_hodnota: float, vzorka: int,
          naozivo: bool, domnienka_id: Optional[int] = None) -> int:
    """Založí experiment SO ZMERANÝM ZÁKLADOM. Bez neho sa založiť nedá.

    Základ sa zapisuje pri založení zámerne: keby sa dopĺňal neskôr, dal by sa
    zmerať až po tom, čo je kandidát hotový — a vtedy už nie je základom, ale
    porovnávacím pozadím vybraným tak, aby kandidát vyzeral dobre.
    """
    if smer not in ("nizsie_lepsie", "vyssie_lepsie"):
        raise ChybaExperimentu("smer je 'nizsie_lepsie' alebo 'vyssie_lepsie'")
    if not sposob_merania.strip() or len(sposob_merania.strip()) < 20:
        raise ChybaExperimentu(
            "`sposob_merania` musí byť opakovateľný postup, nie názov metriky — "
            "kto to nevie zopakovať, nevie výsledok ani spochybniť")
    if vzorka < 1:
        raise ChybaExperimentu("vzorka musí byť aspoň 1")

    cur = conn.execute(
        """INSERT INTO experiments
           (title, hypothesis, success_metric, status, created_at, domnienka_id,
            trieda, metrika, sposob_merania, zaklad_popis, zaklad_hodnota,
            smer, vzorka, naozivo)
           VALUES (?,?,?,'ZAKLAD_ZMERANY',?,?,?,?,?,?,?,?,?,?)""",
        (nazov, hypoteza, metrika, date.today().isoformat(), domnienka_id,
         trieda, metrika, sposob_merania, zaklad_popis, float(zaklad_hodnota),
         smer, vzorka, 1 if naozivo else 0))
    conn.commit()
    return int(cur.lastrowid)


def zmeraj_kandidata(conn: sqlite3.Connection, exp_id: int, *,
                     kandidat_popis: str, kandidat_hodnota: float) -> None:
    """Zapíše nameraného kandidáta. Základ sa pritom NEDOTKNE."""
    r = conn.execute("SELECT * FROM experiments WHERE id=?", (exp_id,)).fetchone()
    if r is None:
        raise ChybaExperimentu(f"experiment {exp_id} neexistuje")
    if r["status"] == "UZAVRETY":
        raise ChybaExperimentu("uzavretý experiment sa nedomeriava")
    conn.execute(
        "UPDATE experiments SET kandidat_popis=?, kandidat_hodnota=?, "
        "status='KANDIDAT_ZMERANY', started_at=COALESCE(started_at,?) WHERE id=?",
        (kandidat_popis, float(kandidat_hodnota), date.today().isoformat(), exp_id))
    conn.commit()


def uzavri(conn: sqlite3.Connection, exp_id: int, *, poucenie: str,
           regresia_presla: bool) -> str:
    """Rozhodne z nameraných čísel. Vracia rozhodnutie.

    Nie je tu miesto pre názor: povýši sa len to, čo sa zlepšilo A prešlo
    regresiou. Zhoršenie je zamietnutie. Rovnosť je NEROZHODNUTY — a to je
    plnohodnotný výsledok, nie zlyhanie.
    """
    r = conn.execute("SELECT * FROM experiments WHERE id=?", (exp_id,)).fetchone()
    if r is None:
        raise ChybaExperimentu(f"experiment {exp_id} neexistuje")
    if r["kandidat_hodnota"] is None:
        raise ChybaExperimentu(
            "kandidát nie je zmeraný — bez druhého čísla sa nedá rozhodnúť, "
            "iba veriť")
    if not poucenie.strip() or len(poucenie.strip()) < 20:
        raise ChybaExperimentu(
            "`poucenie` musí povedať, čo sme sa dozvedeli — aj pri zamietnutí, "
            "inak sa ten istý nápad vráti ako nový")

    zaklad, kandidat = r["zaklad_hodnota"], r["kandidat_hodnota"]
    lepsi = (kandidat < zaklad) if r["smer"] == "nizsie_lepsie" else (kandidat > zaklad)
    rovnake = kandidat == zaklad

    if rovnake:
        rozhodnutie = "NEROZHODNUTY"
    elif lepsi and regresia_presla:
        rozhodnutie = "POVYSENY"
    elif lepsi and not regresia_presla:
        rozhodnutie = "ZAMIETNUTY"      # zlepšil metriku a rozbil niečo iné
    else:
        rozhodnutie = "ZAMIETNUTY"

    conn.execute(
        "UPDATE experiments SET status='UZAVRETY', rozhodnutie=?, poucenie=?, "
        "ended_at=?, result=? WHERE id=?",
        (rozhodnutie, poucenie, date.today().isoformat(),
         f"základ {zaklad} → kandidát {kandidat} ({r['metrika']})", exp_id))
    conn.commit()
    return rozhodnutie


def zrus(conn: sqlite3.Connection, exp_id: int, *, preco: str) -> None:
    """Zruší experiment, keď sa ukáže, že bolo chybné MERADLO, nie kandidát.

    Toto nie je zadné dvierka na nepohodlný výsledok. Základ sa nesmie
    prepísať — takže keď sa zistí, že bol nameraný zle, jediná čestná cesta je
    experiment zrušiť, opraviť prístroj a začať odznova. Upraviť základ pod
    kandidátom by znamenalo, že si výsledok vyberiem.
    """
    if len(preco.strip()) < 20:
        raise ChybaExperimentu("zrušenie musí povedať, čo bolo s meradlom zle")
    r = conn.execute("SELECT rozhodnutie FROM experiments WHERE id=?",
                     (exp_id,)).fetchone()
    if r is None:
        raise ChybaExperimentu(f"experiment {exp_id} neexistuje")
    if r["rozhodnutie"] in ("POVYSENY", "ZAMIETNUTY"):
        raise ChybaExperimentu("uzavretý experiment sa nezrušuje spätne")
    conn.execute(
        "UPDATE experiments SET status='UZAVRETY', rozhodnutie='NEROZHODNUTY', "
        "poucenie=?, ended_at=?, result='zrušené: chybné meradlo' WHERE id=?",
        (f"ZRUŠENÉ, MERADLO BOLO CHYBNÉ: {preco}", date.today().isoformat(), exp_id))
    conn.commit()


def prehlad(conn: sqlite3.Connection) -> list[dict]:
    von = []
    for r in conn.execute("SELECT * FROM experiments ORDER BY id"):
        von.append({
            "id": r["id"], "nazov": r["title"], "stav": r["status"],
            "metrika": r["metrika"], "zaklad": r["zaklad_hodnota"],
            "kandidat": r["kandidat_hodnota"], "rozhodnutie": r["rozhodnutie"],
            "naozivo": bool(r["naozivo"]),
        })
    return von
