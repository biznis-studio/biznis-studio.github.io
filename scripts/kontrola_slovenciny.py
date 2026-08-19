#!/usr/bin/env python3
"""Kontrola pravopisu slovenských stránok cez aspell.

Prvá verzia tejto kontroly (19. 8. dopoludnia) porovnávala len slová so
zriedkavými písmenami (é ó ô ĺ ŕ ä ď) voči schválenému zoznamu. Chytila dve
chyby, ktoré ju vyvolali — a o hodinu neskôr sa ukázalo, že na živom webe
sedelo ďalších **šesť** preklepov, ktoré nemá ako vidieť: `vyjšť`, `sámi`,
`zákázku`, `napríšklad`, `nevypnáte`, `Kež`, `ponúky`. Chybné písmená tam
boli bežné (š, ť, á, u), nie zriedkavé. Brána hlásila „OK, všetky schválené"
a mýlila sa. Rozšíriť ju na všetkých 1 456 slov s diakritikou by neznamenalo
kontrolu, ale odklepnutie bez čítania.

Preto aspell so slovenským slovníkom: z 9 523 slov označí ~90 neznámych a to
sú skoro samé názvy (GitHub, Copilot, SuperFaktúra) a anglicizmy. Tie držíme
v schválenom zozname; čokoľvek nové sa musí prečítať.

Beží nad **postavenými stránkami**, nie nad zdrojom — chyba vzniká pri
prevode zdroja na stránku a v zdroji býva slovo napísané správne
(`grep` na „zadanie" našiel správne slovo, kým stránka niesla „Zaďanie").

Ak aspell alebo slovenský slovník chýba, kontrola **zlyhá nahlas**. Ticho
prejsť by z nej spravilo ozdobu, čo je presne to, čomu sa CLAUDE.md bráni.

Použitie:
    python3 scripts/kontrola_slovenciny.py            # kontrola
    python3 scripts/kontrola_slovenciny.py --schval    # zapíše aktuálny stav
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
STRANKY = KOREN / "site" / "sk"
ZOZNAM = KOREN / "data" / "sk_zname_slova.txt"


def text_stranok() -> str:
    kusy = []
    for f in sorted(STRANKY.glob("*.html")):
        s = f.read_text(encoding="utf-8", errors="ignore")
        s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
        kusy.append(html.unescape(re.sub(r"<[^>]+>", " ", s)))
    return "\n".join(kusy)


def kde_su(slova: set[str]) -> dict[str, str]:
    """Ku každému slovu nájde stránku, kde sa vyskytuje — bez toho sa nedá opraviť."""
    out: dict[str, str] = {}
    for f in sorted(STRANKY.glob("*.html")):
        s = f.read_text(encoding="utf-8", errors="ignore")
        s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
        t = html.unescape(re.sub(r"<[^>]+>", " ", s))
        pritomne = set(re.findall(r"[^\W\d_]+", t, flags=re.UNICODE))
        for w in slova & pritomne:
            out.setdefault(w, f.name)
    return out


def nezname() -> set[str]:
    if not shutil.which("aspell"):
        raise SystemExit(
            "[slovencina] CHYBA: aspell nie je nainštalovaný.\n"
            "  macOS:  brew install aspell\n"
            "  Ubuntu: sudo apt-get install -y aspell aspell-sk\n"
            "Kontrola zámerne nezlyháva ticho — bez slovníka nekontroluje nič."
        )
    hotove = subprocess.run(["aspell", "dicts"], capture_output=True, text=True)
    if "sk" not in hotove.stdout.split():
        raise SystemExit(
            "[slovencina] CHYBA: aspell nemá slovenský slovník (dict 'sk').\n"
            "  Ubuntu: sudo apt-get install -y aspell-sk"
        )
    p = subprocess.run(["aspell", "--lang=sk", "--encoding=utf-8", "list"],
                       input=text_stranok(), capture_output=True, text=True)
    return {w.strip() for w in p.stdout.splitlines() if w.strip()}


def schvalene() -> set[str]:
    if not ZOZNAM.exists():
        return set()
    return {r.strip() for r in ZOZNAM.read_text(encoding="utf-8").splitlines()
            if r.strip() and not r.startswith("#")}


def zapis(slova: set[str]) -> None:
    ZOZNAM.parent.mkdir(parents=True, exist_ok=True)
    ZOZNAM.write_text(
        "# Slová, ktoré slovenský aspell nepozná, ale sú na našich stránkach\n"
        "# správne: názvy (GitHub, Copilot, SuperFaktúra), anglicizmy, domény.\n"
        "# Kontroluje scripts/kontrola_slovenciny.py. Preklep sem NEPATRÍ —\n"
        "# oprav ho v zdroji (agents/*.py alebo content/sk/*.md).\n"
        + "\n".join(sorted(slova)) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schval", action="store_true")
    args = ap.parse_args()

    if not STRANKY.exists():
        print("[slovencina] site/sk/ neexistuje — najprv postav web")
        return 0

    su = nezname()
    if args.schval:
        zapis(su)
        print(f"[slovencina] schválených {len(su)} slov -> {ZOZNAM.relative_to(KOREN)}")
        return 0

    nove = su - schvalene()
    if not nove:
        print(f"[slovencina] OK — aspell nepozná {len(su)} slov, všetky schválené")
        return 0

    umiestnenie = kde_su(nove)
    print(f"[slovencina] {len(nove)} NESCHVÁLENÝCH slov:")
    for w in sorted(nove):
        print(f"    {w}   ({umiestnenie.get(w, '?')})")
    print("\nAk je to preklep, oprav ho v zdroji. Ak je to správne slovo")
    print("(názov, anglicizmus), schváľ ho:")
    print("    python3 scripts/kontrola_slovenciny.py --schval")
    return 1


if __name__ == "__main__":
    sys.exit(main())
