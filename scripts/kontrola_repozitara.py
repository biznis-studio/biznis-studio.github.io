#!/usr/bin/env python3
"""Blokujúca kontrola: zákaznícke údaje sa nesmú dostať do repozitára.

Prečo existuje ako samostatný súbor: CLAUDE.md tvrdil, že toto vynucuje
`quality-packs/build/build_pack.py --check`. Ten skript v repozitári nikdy
nebol a nespúšťal ho nikto. Pravidlo teda existovalo len ako veta a 2026-08-18
sa ukázalo, že mená zákazníkov a čísla prípadov sú na verejnom origin/main.

Čo kontroluje:
  - mená zákazníkov a identifikátory prípadov v sledovaných súboroch
  - e-mailové adresy mimo vlastných domén

Čo NEKONTROLUJE — a nesmie sa to zamieňať s tým, že je to v poriadku:
  - históriu gitu (údaj raz zverejnený sa zmazaním súboru neodpublikuje)
  - obsah, ktorý zákazníka opisuje bez toho, aby ho menoval
  - čokoľvek mimo pracovného stromu
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Mená sa sem dopĺňajú, keď pribudne zákazník. Zoznam je zámerne konkrétny:
# všeobecný vzor („s.r.o.") by hlásil planý poplach na každom marketingovom texte.
ZAKAZNICI = ("constellium", "salzgitter", "uniron", "amari")

# Identifikátor prípadu: štvorciferné číslo hneď za menom zákazníka alebo za
# lomkou. Práve dvojica meno+číslo robí z údaja zákaznícky, nie meno samotné.
VZOR_PRIPADU = re.compile(r"\b(?:" + "|".join(ZAKAZNICI) + r")\s*/\s*\d{3,5}\b", re.I)

VLASTNE_DOMENY = ("biznis-studio.github.io", "example.com", "users.noreply.github.com")
VZOR_EMAILU = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Vlastný e-mail majiteľa nie je zákaznícky údaj.
POVOLENE_EMAILY = {"jozefrusnak4@gmail.com", "actions@users.noreply.github.com"}

PRIPONY = {".md", ".py", ".json", ".html", ".txt", ".yml", ".yaml", ".csv"}

# Známy dlh z 2026-08-18. Tieto riadky UŽ SÚ na verejnom origin/main — kontrola
# ich preto neblokuje, lebo blokovaním by sa nič neodpublikovalo a zastavila by
# len pipeline. Blokuje čokoľvek NAVYŠE. Zoznam sa smie iba skracovať; keď sa
# vyprázdni, celá výnimka aj s touto poznámkou sa zmaže.
# Rozhodnutie o už zverejnenom obsahu patrí majiteľovi — je to záväzok voči
# tretej strane, nie technická voľba.
ZNAMY_DLH = {
    "docs/COMPETITIVE_AUDIT_v1.md",
    "docs/ENTERPRISE_COPILOT_PRODUCT_ARCHITECTURE.md",
    "docs/GRAF_A_KOTVY.md",
    "docs/POC_01_GetCase_SPEC.md",
    "memory/03_Tasks.md",
    "memory/04_Lessons.md",
}


# Kontrola musí vynechať samu seba: zoznam mien je jej vstup, nie únik.
# Po prvom commitnutí sa stala sledovaným súborom a zhodila sama seba —
# preto to nie je poznámka, ale riadok kódu.
VYNECHANE = {"scripts/kontrola_repozitara.py"}


def sledovane_subory() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    return [ROOT / p for p in out
            if Path(p).suffix in PRIPONY and p not in VYNECHANE]


# Súbory, ktoré rastú pripisovaním, a strop, pri ktorom je jasné, že rastú
# zle. Denník evolúcie sa 2026-08-20 nafúkol zo 118 riadkov na 590 022
# (153 MB), lebo obnova zapisovala záznam, ktorý potom sama znova prehrala.
# Verzia s 76 MB stihla odísť na verejný origin. Strop je tu preto, aby to
# druhý raz nikto nezistil až z varovania GitHubu pri pushi.
STROPY_MB = {"state/evolucia.jsonl": 5.0, "state/evolucia_zaklad.jsonl": 5.0}


def prekrocene_stropy() -> list[str]:
    out = []
    for rel, strop in STROPY_MB.items():
        f = ROOT / rel
        if not f.exists():
            continue
        mb = f.stat().st_size / (1024 * 1024)
        if mb > strop:
            out.append(f"{rel}: {mb:.1f} MB (strop {strop} MB) — "
                       f"pravdepodobne sa zapisuje to, čo sa prehráva")
    return out


def main() -> int:
    nalezy: list[str] = []
    dlh: list[str] = []

    velke = prekrocene_stropy()
    if velke:
        print("SÚBOR RASTIE MIMO KONTROLY:")
        for v in velke:
            print("  " + v)
        return 1

    for cesta in sledovane_subory():
        try:
            text = cesta.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = cesta.relative_to(ROOT)

        for i, riadok in enumerate(text.splitlines(), 1):
            nizky = riadok.lower()

            kam = dlh if str(rel) in ZNAMY_DLH else nalezy

            if VZOR_PRIPADU.search(riadok):
                kam.append(f"{rel}:{i}  identifikátor prípadu zákazníka")
                continue

            if any(z in nizky for z in ZAKAZNICI):
                kam.append(f"{rel}:{i}  meno zákazníka")
                continue

            for email in VZOR_EMAILU.findall(riadok):
                if email in POVOLENE_EMAILY:
                    continue
                if any(email.endswith(d) for d in VLASTNE_DOMENY):
                    continue
                kam.append(f"{rel}:{i}  cudzia e-mailová adresa: {email}")

    if dlh:
        print(f"ZNÁMY DLH — {len(dlh)} riadkov už na verejnom origin/main "
              f"(neblokuje, čaká na rozhodnutie majiteľa):")
        for n in dlh:
            print(f"  {n}")
        print()

    if not nalezy:
        print("Nové zákaznícke údaje: žiadne.")
        print("POZOR: nekontroluje sa história gitu. Raz zverejnený údaj tam zostáva.")
        return 0

    print(f"NOVÉ ZÁKAZNÍCKE ÚDAJE — {len(nalezy)} nálezov:\n")
    for n in nalezy:
        print(f"  {n}")
    print(
        "\nRepozitár je verejný. Zmazanie súboru údaj neodpublikuje —"
        "\nzostáva v histórii a v kópiách, ktoré si už ktokoľvek stiahol."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
