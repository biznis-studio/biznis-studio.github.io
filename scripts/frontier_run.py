#!/usr/bin/env python3
"""Skutočný Frontier beh — cez zámok, kontrolné body a rozpočet.

Bezpečnostná vrstva existovala, ale nebola pripevnená k autu: `core/beh.py` bol
otestovaný na vymyslených uzloch, kým skutočná cesta bežala bez nej. Toto je to
pripevnenie. Uzly nie sú vymyslené na predvedenie rámca — sú to operácie, ktoré
tá cesta naozaj robí.

    python3 scripts/frontier_run.py                 # bežný beh
    python3 scripts/frontier_run.py --max-uzlov 2   # zastaví sa na rozpočte
    python3 scripts/frontier_run.py --beh <id>      # pokračuje v behu po páde

Vonkajšie účinky tu ZÁMERNE nie sú. Transakcia databázy ich vrátiť nevie
a tváriť sa, že áno, je horšie než ich sem nedať. Klasifikácia tých, ktoré
robí pipeline po tomto behu:

    git push          NIE JE IDEMPOTENTNÝ  · opakovanie vytvorí ďalší commit;
                                             pipeline ho rieši rebase-om a po
                                             troch pokusoch beh nezhodí
    deploy-pages      IDEMPOTENTNÝ         · nasadí aktuálny artefakt znova
    IndexNow ping     IDEMPOTENTNÝ         · opakované ohlásenie je neškodné
    Formspree / mail  NEVRATNÝ             · v tejto ceste nie je a nesmie byť

Nevratný účinok sa nikdy nesmie dostať do uzla, ktorý sa po páde opakuje.
Preto tento beh nič nepublikuje ani neodosiela — mení iba databázu.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents import frontier_agent                      # noqa: E402
from core import evolution as ev                       # noqa: E402
from core.beh import Beh, RozpocetVycerpany            # noqa: E402
from core.db import get_connection                     # noqa: E402


def _mozny_pad(uzol: str) -> None:
    """Testovacia injekcia pádu. V produkcii sa nemôže zapnúť náhodou.

    Vyžaduje DVE premenné naraz — jedna preklepom nastavená nestačí — a
    testovací príznak, ktorý v CI ani v cloude nikdy nie je nastavený.
    """
    if os.environ.get("FRONTIER_TEST_FIXTURE") != "ano-viem-co-robim":
        return
    if os.environ.get("FRONTIER_CRASH_AT") == uzol:
        print(f"[frontier_run] TESTOVACÍ PÁD v uzle {uzol}", flush=True)
        os._exit(9)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--beh", default=None, help="pokračovať v existujúcom behu")
    p.add_argument("--max-uzlov", type=int, default=40)
    p.add_argument("--max-sekund", type=int, default=1800)
    args = p.parse_args()

    run_id = args.beh or f"frontier-{int(time.time())}"
    vlastnik = ("github-actions" if os.environ.get("GITHUB_ACTIONS")
                else os.environ.get("CLAUDE_RUN_OWNER", "relacia"))

    conn = get_connection()
    ev.priprav(conn)
    zamknute = False
    try:
        try:
            ev.zamkni(conn, run_id=run_id, vlastnik=vlastnik)
            zamknute = True
        except ev.ZamokObsadeny as e:
            # Druhý beh nesmie zapísať NIČ — ani značku, ani poznatok.
            print(f"[frontier_run] LOCKED_BY_ACTIVE_RUN: {e}")
            return 0

        beh = Beh(conn, run_id=run_id, spustil=vlastnik,
                  max_uzlov=args.max_uzlov, max_sekund=args.max_sekund)
        print(f"[frontier_run] beh {run_id}; hotové uzly: "
              f"{sorted(beh.hotove()) or 'žiadne'}")

        try:
            # 1. SNÍMANIE — jediný uzol, ktorý siaha do siete.
            with beh.uzol("snimanie") as c:
                if c is None:
                    print("  snimanie: PRESKOČENÝ (kontrolný bod)")
                else:
                    n = frontier_agent.run(conn=c)
                    beh.minul("zdroje", len(frontier_agent.ZDROJE))
                    _mozny_pad("snimanie")
                    print(f"  snimanie: {n} nových položiek")

            # 2. STARNUTIE — poznatky po dobe platnosti.
            with beh.uzol("starnutie") as c:
                if c is None:
                    print("  starnutie: PRESKOČENÝ (kontrolný bod)")
                else:
                    starnuce = ev.zostarni(c)
                    _mozny_pad("starnutie")
                    print(f"  starnutie: {len(starnuce)} poznatkov starne")

            # 3. DOMNIENKY — základné predpoklady musia existovať.
            with beh.uzol("domnienky") as c:
                if c is None:
                    print("  domnienky: PRESKOČENÝ (kontrolný bod)")
                else:
                    from scripts.evolve import ZAKLADNE_DOMNIENKY
                    zalozene = 0
                    for d in ZAKLADNE_DOMNIENKY:
                        try:
                            ev.zapis_domnienku(c, **d)
                            zalozene += 1
                        except Exception as chyba:
                            if "UNIQUE" not in str(chyba):
                                raise
                    _mozny_pad("domnienky")
                    print(f"  domnienky: {zalozene} nových")

            # 4. VÝKLAD — zápis úsudku z artefaktu, ak nejaký čaká.
            #    Úsudok sa robí mimo (relácia, cloud); sem prichádza hotový
            #    artefakt, ktorý sa celý overí a zapíše v jednej transakcii.
            cakajuce = sorted((ROOT / "state" / "vyklad").glob("*.json"))
            for artefakt in cakajuce:
                with beh.uzol(f"vyklad:{artefakt.stem}") as c:
                    if c is None:
                        print(f"  vyklad {artefakt.stem}: PRESKOČENÝ (kontrolný bod)")
                        continue
                    import hashlib
                    from core import vyklad as vy
                    surovy = artefakt.read_bytes()
                    odtlacok = hashlib.sha256(surovy).hexdigest()
                    uz = c.execute(
                        "SELECT run_id, kedy FROM vyklad_artefakt WHERE odtlacok=?",
                        (odtlacok,)).fetchone()
                    if uz is not None:
                        print(f"  vyklad {artefakt.stem}: UŽ ZAPÍSANÝ "
                              f"(beh {uz['run_id']}, {uz['kedy']})")
                        continue
                    vysledok = vy.zapis(c, vy.nacitaj(artefakt))
                    c.execute(
                        "INSERT INTO vyklad_artefakt "
                        "(odtlacok, subor, run_id, polozek, kedy) VALUES (?,?,?,?,?)",
                        (odtlacok, artefakt.name, run_id, vysledok["spolu"],
                         __import__("datetime").datetime.now().isoformat()))
                    beh.minul("volania_modelu")
                    _mozny_pad("vyklad")
                    print(f"  vyklad {artefakt.stem}: {vysledok['zapisane']} "
                          f"zapísaných, {vysledok['zahodene']} zahodených")

            # 5. SPRÁVA — čo si systém pýta. Číta, nemení.
            with beh.uzol("sprava") as c:
                if c is None:
                    print("  sprava: PRESKOČENÝ (kontrolný bod)")
                else:
                    kroky = ev.dalsi_krok(c)
                    navrhy = ev.navrhy_na_seba(c)
                    _mozny_pad("sprava")
                    print(f"  sprava: {len(kroky)} krokov, {len(navrhy)} návrhov na seba")
                    for k in kroky[:5]:
                        kto = "MAJITEĽ" if k["autorita"] == "majitel" else "stroj"
                        print(f"    [{k['poradie']}] ({kto}) {k['co'][:80]}")

        except RozpocetVycerpany as e:
            print(f"[frontier_run] ROZPOCET: {e}")
            print(f"[frontier_run] beh {run_id} je obnoviteľný: "
                  f"--beh {run_id}")
            return 0

        beh.hotovo()
        print(f"[frontier_run] HOTOVO · zostatok rozpočtu: {beh.zostava()}")
        return 0
    finally:
        if zamknute:
            ev.odomkni(conn, run_id=run_id)
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
