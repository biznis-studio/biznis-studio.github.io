"""Crawl-readiness audit for the generated site.

Checks every *.html page under site/ (recursively - all of site/products/,
site/sk/, site/tools/, site/blog/, site/news/, plus the homepage) for the
kind of gap that's easy to miss manually: missing/empty <title>, missing
or badly-sized meta description, missing canonical link, invalid JSON-LD,
and broken internal links. Run this after any change to the page
templates or SEO injection logic, or periodically as a standalone health
check - it caught two real bugs the first time it ran ad hoc (see
docs/TASKBOARD.md iteration 27): a missing homepage canonical/OG tag, and
(separately) a missing RSS discovery link across all 14 product pages.

Originally scoped to just site/products/*.html and site/index.html - that
left every site/sk/, site/tools/, site/blog/ and site/news/ page unaudited
even as most new content started shipping there. Widened to check the
whole site (iteration 70) after it missed two real over-length meta
descriptions in exactly those directories.

Exit code is non-zero if any issue is found, so this can be wired into CI
later without extra glue.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
# Same gating as the generators: without it, canonical/hreflang aren't
# emitted at all, so the checks that compare against absolute URLs are
# skipped rather than reporting false failures on a local-only build.
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "").rstrip("/")


# ČO TENTO AUDIT NEVIE — čítaj skôr, než uveríš jeho "no issues found".
#
# 2026-08-18: audit hlásil nula problémov, zatiaľ čo Google mal v indexe 2 z 44
# stránok, sitemapu nikdy nenačítal a za 19 dní spravil 9 crawl požiadaviek.
# Audit mal pravdu v tom, čo meria — tituly, popisy, kanonické odkazy, hreflang,
# vnútorné odkazy. Ale to všetko je OBSAH SÚBOROV. Ani jedna kontrola nevie
# odpovedať na otázku, na ktorej záleží: dostal sa k tomu vyhľadávač?
#
# Je to presne tá chyba, ktorú predávame ako odstránenú — deklarovaný stav
# namiesto overeného. Preto výstup od 2026-08-18 túto hranicu vypisuje sám.
# Dosah sa dá overiť len zvonku (Search Console, živé načítanie), nie zo súborov.


def audit(site_dir: Path) -> list[tuple[str, str]]:
    files = sorted(site_dir.rglob("*.html"))
    existing = {str(p.relative_to(site_dir)) for p in site_dir.rglob("*") if p.is_file()}
    issues = []

    for f in files:
        if not f.exists():
            continue
        text = f.read_text()
        rel = str(f.relative_to(site_dir))

        title_m = re.search(r"<title>(.*?)</title>", text, re.S)
        if not title_m or not title_m.group(1).strip():
            issues.append((rel, "missing/empty <title>"))

        desc_m = re.search(r'<meta name="description" content="([^"]*)"', text)
        if not desc_m:
            issues.append((rel, "missing meta description"))
        elif not (50 <= len(desc_m.group(1)) <= 160):
            issues.append((rel, f"meta description length {len(desc_m.group(1))} (recommended 50-160)"))

        # Presence alone was never enough: work.html and credits.html both
        # carried a canonical pointing at the homepage for weeks, which tells
        # Google they are duplicates of / and shouldn't be indexed at all.
        # The audit passed the whole time because a canonical *existed*.
        can_m = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        if not can_m:
            issues.append((rel, "missing canonical link"))
        elif SITE_BASE_URL:
            # An index.html may legitimately canonicalise to its directory
            # URL. Only strip the suffix when it's actually there - slicing
            # unconditionally mangles any shorter name ("work.html" became
            # "" and silently matched the homepage, hiding the very bug this
            # check was added for).
            wants = {f"{SITE_BASE_URL}/{rel}"}
            if rel.endswith("index.html"):
                wants.add(f"{SITE_BASE_URL}/{rel[:-len('index.html')]}")
            if can_m.group(1) not in wants:
                issues.append((rel, f"canonical points elsewhere: {can_m.group(1)} "
                                    f"(expected one of {sorted(wants)})"))

        if 'rel="alternate" type="application/rss+xml"' not in text:
            issues.append((rel, "missing RSS discovery link"))

        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
            try:
                json.loads(m.group(1))
            except json.JSONDecodeError as e:
                issues.append((rel, f"invalid JSON-LD: {e}"))

        for m in re.finditer(r'href="([^"#][^"]*)"', text):
            href = m.group(1)
            if href.startswith(("http", "mailto:", "data:")):
                continue
            href = href.split("#")[0]
            if not href:
                continue
            target = (f.parent / href).resolve()
            try:
                rel_target = str(target.relative_to(site_dir.resolve()))
            except ValueError:
                continue
            if rel_target not in existing:
                issues.append((rel, f"broken internal link: {href}"))

    issues.extend(_audit_hreflang(site_dir))
    return issues


def _audit_hreflang(site_dir: Path) -> list[tuple[str, str]]:
    """hreflang is only honoured when both pages point at each other.

    Google: "if two pages don't both point to each other, the tags will be
    ignored." /sk/ carried the annotation alone from launch until iteration
    72 - valid HTML, passing audit, and silently doing nothing at all. A
    one-sided hreflang is indistinguishable from a correct one by eye,
    which is exactly why it needs a machine check.
    """
    if not SITE_BASE_URL:
        return []
    issues = []
    declared = {}                       # page url -> {lang: target url}
    url_of = {}                         # page url -> repo-relative path
    for f in sorted(site_dir.rglob("*.html")):
        rel = str(f.relative_to(site_dir))
        tags = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"',
                          f.read_text())
        if not tags:
            continue
        page_url = f"{SITE_BASE_URL}/{rel[:-len('index.html')] if rel.endswith('index.html') else rel}"
        declared[page_url] = {lang: href for lang, href in tags}
        url_of[page_url] = rel

    for page_url, alts in declared.items():
        rel = url_of[page_url]
        if page_url not in alts.values():
            issues.append((rel, "hreflang set does not include the page itself"))
        for lang, target in alts.items():
            if lang == "x-default" or target == page_url:
                continue
            if target not in declared:
                issues.append((rel, f"hreflang '{lang}' -> {target} which declares no "
                                    f"hreflang back (Google ignores one-sided annotations)"))
            elif page_url not in declared[target].values():
                issues.append((rel, f"hreflang '{lang}' -> {target} does not point back"))
    return issues


if __name__ == "__main__":
    found = audit(SITE_DIR)
    print(f"Checked site/ - {'no issues found' if not found else f'{len(found)} issue(s):'}")
    if not found:
        # Bez tejto vety znie "no issues found" ako "web je v poriadku". 2026-08-18
        # bol zelený audit a súčasne 2 indexované stránky zo 44. Kontrola, ktorá
        # nepovie, čo NEOVERILA, klame presne tak, ako klame zelený SEO report.
        print("  POZOR: audit číta LEN obsah súborov. Nehovorí nič o tom, či "
              "vyhľadávač stránky našiel, načítal alebo zaradil do indexu —")
        print("  to sa dá overiť iba zvonku (Search Console: crawl stats, "
              "page indexing, stav sitemapy).")
    for rel, issue in found:
        print(f"  {rel}: {issue}")
    sys.exit(1 if found else 0)
