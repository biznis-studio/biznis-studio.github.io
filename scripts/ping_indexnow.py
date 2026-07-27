#!/usr/bin/env python3
"""Re-ping IndexNow (Bing/Yandex/Seznam/Naver/Yep) after the site is
actually live on GitHub Pages.

agents/seo_agent.py already submits during the main pipeline run, but that
happens *before* the commit+push+deploy steps, so the key file IndexNow
needs to verify ownership isn't live yet at that point. This is a small,
standalone re-ping run as a later CI step (after actions/deploy-pages
succeeds) so the key is guaranteed to already be reachable. Best-effort -
never fails the workflow.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.seo_agent import SITE_BASE_URL, submit_to_indexnow

ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = ROOT / "db" / "indexnow_key.txt"
SITEMAP = ROOT / "site" / "sitemap.xml"


def read_sitemap_urls() -> list[str]:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.parse(SITEMAP).getroot()
    return [loc.text for loc in root.findall(".//s:loc", ns) if loc.text]


if __name__ == "__main__":
    if not KEY_FILE.exists() or not SITEMAP.exists() or not SITE_BASE_URL:
        print("[ping_indexnow] missing key file, sitemap, or SITE_BASE_URL - skipping")
        sys.exit(0)
    key = KEY_FILE.read_text().strip()
    urls = read_sitemap_urls()
    ok = submit_to_indexnow(urls, key)
    print(f"[ping_indexnow] submitted {len(urls)} urls, ok={ok}")
