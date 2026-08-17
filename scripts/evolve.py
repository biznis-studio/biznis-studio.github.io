#!/usr/bin/env python3
"""Evolučný beh — hrana z merania späť do rozhodovania.

`run_pipeline.py` vyrobí veci. Tento skript sa pýta, či sa vôbec mali vyrobiť,
a čo si systém pýta ako ďalšie. Beží po pipeline, nie namiesto nej.

    python3 scripts/evolve.py            # čo si systém pýta ďalej
    python3 scripts/evolve.py --seed     # založí domnienky, na ktorých stojíme
    python3 scripts/evolve.py --revizia  # zapíše zmeškané revízie (mesačne)

Návratový kód je 0 aj vtedy, keď niečo padlo — padnutá domnienka je výsledok,
nie porucha. Nenulový je len pri chybe behu.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.db import get_connection
from core import evolution as ev


# Domnienky, na ktorých biznis stojí. Nevymyslené — každá je odvodená z toho,
# čo už majiteľ napísal v CLAUDE.md alebo čo je v STATE.md ako kotva. Pri každej
# je uvedené, odkiaľ pochádza, aby sa dala spochybniť aj samotná domnienka.
ZAKLADNE_DOMNIENKY = [
    {
        "domnienka": "Firmy sú ochotné zaplatiť za prevod svojej práce do overiteľnej podoby.",
        "preco_tomu_verime": "CLAUDE.md: „LLM automatizujú to, čo viete overiť.“ "
                             "Z toho stojí celá pozícia webu aj packu.",
        "co_by_ju_vyvratilo": "Šesť mesiacov od spustenia formulárov nula zaplatených "
                              "faktúr a nula dopytov, ktoré by pomenovali overiteľnosť "
                              "ako svoj problém.",
        "ako_to_zistime": "state/promises.json + počet dopytov z Formspree + faktúry",
        "datum_revizie": "2026-11-15",
        "dolezitost": 5,
    },
    {
        "domnienka": "Naším trhom sú slovenské malé a stredné firmy, nie anglický trh nástrojov.",
        "preco_tomu_verime": "CLAUDE.md, Strategy context: slovenské SERP-y našich služieb "
                             "držia len malé lokálne agentúry a bežia na ne platené reklamy.",
        "co_by_ju_vyvratilo": "Prvé reálne dopyty prídu z anglických stránok, alebo slovenské "
                              "články po troch mesiacoch neprinesú ani jednu organickú impresiu.",
        "ako_to_zistime": "Search Console podľa jazyka + pôvod dopytov z formulára",
        "datum_revizie": "2026-10-31",
        "dolezitost": 5,
    },
    {
        "domnienka": "Viazaným obmedzením je návštevnosť, nie konverzia.",
        "preco_tomu_verime": "CLAUDE.md: Gumroad ukazuje 0 zobrazení, nie 0 predajov. "
                             "Leštenie textu sedí pod bránou, ktorá sa neotvorila.",
        "co_by_ju_vyvratilo": "Návštevnosť vyrastie na stovky za mesiac a dopyty zostanú nula "
                              "— potom je chyba na stránke, nie pred ňou.",
        "ako_to_zistime": "Search Console: zobrazenia a kliky proti počtu dopytov",
        "datum_revizie": "2026-10-15",
        "dolezitost": 4,
    },
    {
        "domnienka": "Pack je formát dodania, nie produkt — výrobná linka zvládne druhú profesiu.",
        "preco_tomu_verime": "CLAUDE.md: „Pack je formát dodania, nie produkt.“",
        "co_by_ju_vyvratilo": "Druhý pack v inej profesii si vyžiada prepísanie metódy, "
                              "nie iba nový zdrojový súbor experta.",
        "ako_to_zistime": "postaviť druhý pack a zmerať, koľko z build/ sa muselo zmeniť",
        "datum_revizie": "2026-12-01",
        "dolezitost": 4,
    },
    {
        "domnienka": "Dizajn webu ovplyvňuje, či nás firma osloví.",
        "preco_tomu_verime": "Majiteľ 2026-08-16: predávame weby, ten náš je referencia, "
                             "ktorú si záujemca vie skontrolovať.",
        "co_by_ju_vyvratilo": "Po zosúladení dizajnu sa pomer návštev k dopytom nezmení.",
        "ako_to_zistime": "porovnať dopyty na návštevu pred a po dizajnovom zosúladení",
        "datum_revizie": "2026-11-30",
        "dolezitost": 2,
    },
]


def seed(conn) -> int:
    zalozene = 0
    for d in ZAKLADNE_DOMNIENKY:
        try:
            ev.zapis_domnienku(conn, **d)
            zalozene += 1
        except Exception as chyba:  # UNIQUE = už existuje, to je v poriadku
            if "UNIQUE" not in str(chyba):
                raise
    return zalozene


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", action="store_true", help="založiť základné domnienky")
    p.add_argument("--revizia", action="store_true",
                   help="zapísať zmeškané revízie (domnienka po 2. zmeškaní padá)")
    args = p.parse_args()

    conn = get_connection()
    try:
        ev.priprav(conn)

        if args.seed:
            print(f"[evolve] založených domnienok: {seed(conn)}")

        starnuce = ev.zostarni(conn)
        if starnuce:
            print(f"[evolve] poznatkov po dobe platnosti: {len(starnuce)}")

        if args.revizia:
            for d in ev.splatne_domnienky(conn):
                novy = ev.zmeskana_revizia(conn, d["id"])
                znacka = "PADLA" if novy == "VYVRATENA" else "odložená o 30 dní"
                print(f"[revizia] {d['domnienka'][:60]}… → {znacka}")

        kroky = ev.dalsi_krok(conn)
        if not kroky:
            print("[evolve] nič splatné — žiadna domnienka nie je po termíne "
                  "a žiadny poznatok nestarne.")
            return 0

        print(f"\n[evolve] {len(kroky)} vecí si systém pýta, zoradené podľa hodnoty:\n")
        for k in kroky:
            kto = "MAJITEĽ" if k["autorita"] == "majitel" else "stroj"
            print(f"  [{k['poradie']:>5}] ({kto}) {k['co']}")
            print(f"          ako: {k['ako']}")
            print(f"          vyvrátilo by: {k['vyvratilo_by']}\n")

        pre_majitela = [k for k in kroky if k["autorita"] == "majitel"]
        if pre_majitela:
            print(f"[evolve] {len(pre_majitela)} z toho nesmie rozhodnúť stroj — "
                  "menia to, čím má byť biznis.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
