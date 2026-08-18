"""Rebuild the whole site, correctly, in one command.

This exists because the correct rebuild sequence is nine steps long, has a
non-obvious ordering constraint, and was being retyped by hand every time -
which is exactly how steps get skipped.

The ordering constraint that matters: calling `landing_page_agent.build_page()`
on an already-published page resets it to its pre-SEO state, wiping the
canonical link, JSON-LD and FAQ that `seo_agent` injected. So every rebuild
MUST set `pages.seo_enhanced = 0` and re-run `seo_agent` afterwards. Forgetting
that silently strips SEO markup from every page while the build reports success.

Usage:
    python3 scripts/build_site.py            # rebuild everything
    python3 scripts/build_site.py --fast     # skip network work (images, news)
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def zapis_favicon() -> Path:
    """Vyrobí /favicon.ico.

    Stránky deklarujú ikonu ako vloženú SVG data-URI, čo prehliadačom stačí.
    Prehľadávače si však /favicon.ico pýtajú podľa konvencie bez ohľadu na to,
    čo je v HTML — Search Console 2026-08-18 ukázal, že **2 z 9 požiadaviek
    Googlebota na celý web** boli práve tieto a vrátili 404. Pri deviatich
    požiadavkách za tri týždne je to 22 % rozpočtu prehľadávania premrhaných
    na súbor, ktorý sa dá vyrobiť raz.
    """
    from PIL import Image, ImageDraw

    velkosti = (16, 32, 48, 64)
    zaklad = 256
    obr = Image.new("RGBA", (zaklad, zaklad), (0, 0, 0, 0))
    kresli = ImageDraw.Draw(obr)
    # rovnaké farby a tvar ako vložená SVG ikona v page_shell()
    kresli.rounded_rectangle([0, 0, zaklad - 1, zaklad - 1], radius=56, fill=(79, 70, 229, 255))
    # „B" vykreslené ako obdĺžniky — nezávisí od toho, aké písma sú na stroji,
    # takže CI a lokálny build vyrobia bajt za bajt to isté
    L, R, T, D, t = 76, 170, 60, 196, 26      # ľavý, pravý, horný, dolný okraj, hrúbka ťahu
    biela = (255, 255, 255, 255)
    kresli.rectangle([L, T, L + t, D], fill=biela)          # zvislý ťah
    kresli.rectangle([L, T, R, T + t], fill=biela)          # horné rameno
    kresli.rectangle([L, 115, R, 141], fill=biela)          # stredné rameno
    kresli.rectangle([L, D - t, R, D], fill=biela)          # dolné rameno
    kresli.rectangle([R - t, T, R, 141], fill=biela)        # pravý ťah hornej slučky
    kresli.rectangle([R - t, 115, R, D], fill=biela)        # pravý ťah dolnej slučky

    cesta = ROOT / "site" / "favicon.ico"
    obr.save(cesta, format="ICO", sizes=[(v, v) for v in velkosti])
    return cesta


def main(fast: bool = False) -> int:
    from agents import (blog_agent, image_agent, landing_page_agent as lpa,
                        news_agent, seo_agent, tools_agent)
    from core.db import get_connection

    if not fast:
        image_agent.run()          # fetch any missing artwork first, so cards find it

    # 1. Build pages for products that do not have one yet.
    lpa.run()

    conn = get_connection()

    # 2. Rebuild every existing product page so it picks up template changes.
    rows = conn.execute(
        """SELECT p.id AS product_id, p.title, p.format, p.file_path,
                  p.monetization_url, p.price_usd, k.term
           FROM products p
           JOIN product_ideas pi ON pi.id = p.idea_id
           JOIN keywords k ON k.id = pi.target_keyword_id
           JOIN pages pg ON pg.product_id = p.id"""
    ).fetchall()
    rebuilt = 0
    for row in rows:
        try:
            if lpa.build_page(dict(row)):
                rebuilt += 1
        except Exception as exc:                       # one bad page must not stop the build
            print(f"[build_site] FAILED product_id={row['product_id']}: {exc}")
    print(f"[build_site] rebuilt {rebuilt}/{len(rows)} product pages")

    stats = {
        "products": conn.execute(
            "SELECT COUNT(*) FROM products WHERE status='ready'").fetchone()[0],
        "signals": conn.execute("SELECT COUNT(*) FROM signals_raw").fetchone()[0],
        "keywords": conn.execute("SELECT COUNT(*) FROM keywords").fetchone()[0],
        "pages": conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0],
        "runs": conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0],
        "loc": 0,
    }
    pages = conn.execute(
        """SELECT pg.url, pg.title, pg.meta_description, p.format,
                  p.monetization_url, p.price_usd
           FROM pages pg JOIN products p ON p.id = pg.product_id ORDER BY pg.id"""
    ).fetchall()

    # 3. THE STEP THAT IS EASY TO FORGET - see module docstring.
    conn.execute("UPDATE pages SET seo_enhanced = 0")
    conn.commit()
    conn.close()

    # 4. Everything that is not a product page.
    lpa.build_index([dict(p) for p in pages], stats=stats)
    lpa.build_sk_page()
    lpa.build_efa_tool()
    lpa.build_work_page(stats)
    lpa.build_credits_page()
    blog_agent.run()
    tools_agent.run()
    if fast:
        news_agent.build_page()    # rebuild from stored headlines, no fetching
    else:
        news_agent.run()

    # 5. Re-inject SEO markup that step 2 wiped.
    seo_agent.run()

    # Rucne pisane <title> pre stranky, ktorych nadpis je spravne dlhy, ale do
    # vysledkov vyhladavania sa nezmesti. Bezi az po seo_agent, aby ho ten
    # neprepisal. h1 zostava nedotknuty.
    import re as _re
    from agents.common import SEO_TITULKY
    _n = 0
    for _cesta, _titul in SEO_TITULKY.items():
        _f = ROOT / "site" / _cesta
        if not _f.exists():
            print(f"[titulky] POZOR - stranka neexistuje: {_cesta}")
            continue
        _h = _f.read_text(encoding="utf-8")
        _novy, _pocet = _re.subn(r"<title>.*?</title>", f"<title>{_titul}</title>",
                                 _h, count=1, flags=_re.S)
        if _pocet:
            _f.write_text(_novy, encoding="utf-8")
            _n += 1
    print(f"[titulky] rucne prepisanych: {_n} z {len(SEO_TITULKY)}")

    # 5b. /favicon.ico — pýta si ho prehľadávač, nie HTML. Viď zapis_favicon().
    _ico = zapis_favicon()
    print(f"[favicon] {_ico.relative_to(ROOT)} ({_ico.stat().st_size} B)")

    # 6. The check Claude can read: non-zero exit means do not ship.
    audit = subprocess.run([sys.executable, str(ROOT / "scripts" / "audit_site.py")])
    if audit.returncode != 0:
        print("[build_site] AUDIT FAILED - do not deploy")
        return 1
    print("[build_site] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(fast="--fast" in sys.argv))
