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
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.db import get_connection
from core import evolution as ev


# Domnienky, na ktorých biznis stojí. Nevymyslené — každá je odvodená z toho,
# čo už majiteľ napísal v CLAUDE.md alebo čo je v STATE.md ako kotva. Pri každej
# je uvedené, odkiaľ pochádza, aby sa dala spochybniť aj samotná domnienka.
ZAKLADNE_DOMNIENKY = [
    # Majiteľ 2026-08-17: „zabudni na faktúry, faktúry prídu keď budeme mať top
    # produkt.“ Faktúra preto NIE JE bránou pred stavaním — je následkom. Čo
    # zostáva merateľné, je kvalita produktu, a tá sa dá vyvrátiť aj bez tržby.
    {
        "domnienka": "Produkt bude špičkový vtedy, keď bude stáť na aktuálnej svetovej "
                     "špičke AI, nie na tom, čo sme vedeli pred rokom.",
        "preco_tomu_verime": "Majiteľ 2026-08-17: zdrojom je globálny svet AI a marketingu "
                             "a jeho pokročilého používania; aplikácia na SK trh je až dôsledok.",
        "co_by_ju_vyvratilo": "Za tri mesiace nevznikne z fronty `frontier` ani jeden poznatok, "
                              "ktorý by čokoľvek v produkte zmenil — potom je snímanie ozdoba.",
        "ako_to_zistime": "počet riadkov v `poznatky` so zdrojom `frontier:` a "
                          "s vyplneným `dosah`, ktoré viedli k zmene v repozitári",
        "datum_revizie": "2026-11-17",
        "dolezitost": 5,
    },
    {
        "domnienka": "Overiteľnosť je tá schopnosť, ktorá odlišuje náš produkt od "
                     "bežného nasadenia AI.",
        "preco_tomu_verime": "CLAUDE.md: „LLM automatizujú to, čo viete overiť.“ "
                             "Z toho stojí celá pozícia webu aj packu.",
        "co_by_ju_vyvratilo": "Špička dorieši overovanie sama — modely alebo nástroje začnú "
                              "štandardne dodávať doložiteľný postup, a naša práca sa scvrkne "
                              "na zapnutie funkcie, ktorú má každý.",
        "ako_to_zistime": "sledovať vo fronte `frontier` položky o verifikácii, "
                          "evals a doložiteľnosti (arXiv, hf_papers, oznámenia výrobcov)",
        "datum_revizie": "2026-10-31",
        "dolezitost": 5,
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
    beh_id = f"{os.environ.get('GITHUB_RUN_ID') or os.getpid()}-{int(time.time())}"
    vlastnik = ("github-actions" if os.environ.get("GITHUB_ACTIONS")
                else os.environ.get("CLAUDE_RUN_OWNER", "relacia"))
    zamknute = False
    try:
        ev.priprav(conn)

        # Stav smie meniť jediný beh. Odmietnutie nie je chyba, je to ochrana,
        # preto sa končí nulou — inak by CI hlásilo poruchu vždy, keď zámok
        # zafunguje, a niekto by ho zo zúfalstva vypol.
        try:
            ev.zamkni(conn, run_id=beh_id, vlastnik=vlastnik)
            zamknute = True
        except ev.ZamokObsadeny as e:
            print(f"[evolve] {e}")
            print("[evolve] nič sa nemení; súbežný zápis by databázu rozbil")
            return 0

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

        ucinnost = ev.ucinnost_zdrojov(conn)
        if ucinnost:
            print("\n[evolve] výťažnosť zdrojov (vyložené → zapísané):")
            for z in ucinnost:
                print(f"  {z['zdroj']:32} {z['zapisane']:>3}/{z['vylozene']:<3} "
                      f"{z['pomer']:>6.0%}  {z['odporucanie']}")

        navrhy = ev.navrhy_na_seba(conn)
        if navrhy:
            print("\n[evolve] čo systém navrhuje zmeniť sám na sebe:")
            for n in navrhy:
                kto = "MAJITEĽ" if n["autorita"] == "majitel" else "stroj"
                print(f"  ({kto}) {n['co']}\n          {n['preco']}")

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
        if zamknute:
            ev.odomkni(conn, run_id=beh_id)
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
