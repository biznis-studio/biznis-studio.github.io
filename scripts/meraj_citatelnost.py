#!/usr/bin/env python3
"""Deterministické meranie čitateľnosti článku. Rovnaký vstup = rovnaké číslo.

Metrika: počet viet nad 28 slov. Zámerne jedno číslo, nie index — zložený
index sa nedá overiť ručne a nikto nevie, čo v ňom rozhodlo.
"""
import re
import sys
from pathlib import Path


def vety_nad(cesta: Path, limit: int = 28) -> tuple[int, list]:
    t = Path(cesta).read_text()
    telo = re.sub(r"^---.*?---", "", t, flags=re.S)          # frontmatter preč
    # Odrážka je CELÝ blok vrátane odsadených pokračovacích riadkov. Pôvodná
    # verzia mazala len prvý riadok, takže zvyšok odrážky sa zlepil
    # s predchádzajúcou vetou a vyrobil „vetu“ so 60 slovami, ktorá v texte
    # neexistuje. Meradlo hlásilo chybu tam, kde žiadna nebola.
    telo = re.sub(r"^\s*[-*|>#][^\n]*(?:\n[ \t]+[^\n]*)*$", "", telo, flags=re.M)
    telo = re.sub(r"https?://\S+|\[|\]|\(|\)|\*|`", " ", telo)
    vety = [v.strip() for v in re.split(r"(?<=[.!?])\s+", telo) if v.strip()]
    dlhe = [(len(v.split()), v[:60]) for v in vety if len(v.split()) > limit]
    return len(dlhe), sorted(dlhe, reverse=True)


if __name__ == "__main__":
    n, zoznam = vety_nad(Path(sys.argv[1]))
    print(f"viet nad 28 slov: {n}")
    for pocet, ukazka in zoznam:
        print(f"  {pocet} slov · {ukazka}…")
