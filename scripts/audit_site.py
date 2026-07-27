"""Crawl-readiness audit for the generated site.

Checks every page under site/ for the kind of gap that's easy to miss
manually: missing/empty <title>, missing or badly-sized meta description,
missing canonical link, invalid JSON-LD, and broken internal links. Run
this after any change to the page templates or SEO injection logic, or
periodically as a standalone health check - it caught two real bugs the
first time it ran ad hoc (see docs/TASKBOARD.md iteration 27): a missing
homepage canonical/OG tag, and (separately) a missing RSS discovery link
across all 14 product pages.

Exit code is non-zero if any issue is found, so this can be wired into CI
later without extra glue.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"


def audit(site_dir: Path) -> list[tuple[str, str]]:
    files = sorted(site_dir.glob("products/*.html")) + [site_dir / "index.html"]
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

        if 'rel="canonical"' not in text:
            issues.append((rel, "missing canonical link"))

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

    return issues


if __name__ == "__main__":
    found = audit(SITE_DIR)
    print(f"Checked site/ - {'no issues found' if not found else f'{len(found)} issue(s):'}")
    for rel, issue in found:
        print(f"  {rel}: {issue}")
    sys.exit(1 if found else 0)
