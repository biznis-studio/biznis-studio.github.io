"""Check the external links we placed by hand are still reachable.

Deliberately NOT part of `audit_site.py` and NOT wired into the build
gate. Those must only fail on things we control - blocking a deploy
because somebody else's server is slow, rate-limiting us or briefly down
would make the gate untrustworthy, and people route around gates they
don't trust. Run this periodically instead, and judge the output.

Only hand-placed links are checked. `news_agent` generates ~85 headline
links that churn daily and are expected to rot; including them would bury
the handful that actually matter under noise. The ones that matter are
the cited sources on pages making legal or pricing claims, and the
Gumroad links that are the only paths to revenue on the whole site.

Findings are advisory. A failure here means "look at this", not
"something is broken" - a 403 usually means bot-blocking (Pexels does
this) and a timeout may be geography- or network-specific rather than the
site being down. Verify from a second client before changing a citation:
replacing a correct source with a worse one because our network couldn't
reach it would be a downgrade, not a fix.

Usage:
    python3 scripts/check_links.py
"""
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
TIMEOUT = 20
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# Hosts whose links are auto-generated from feeds and rot by design.
FEED_HOSTS = {
    "arstechnica.com", "arxiv.org", "phys.org", "spectrum.ieee.org",
    "www.technologyreview.com", "www.ecb.europa.eu", "www.federalreserve.gov",
}


def hand_placed_links(site_dir: Path) -> dict[str, set[str]]:
    """External URLs, minus our own domain and minus the news feeds."""
    links: dict[str, set[str]] = defaultdict(set)
    for page in sorted(site_dir.rglob("*.html")):
        for m in re.finditer(r'href="(https?://[^"]+)"', page.read_text()):
            url = m.group(1)
            host = re.sub(r"^https?://([^/]+).*", r"\1", url)
            if host in FEED_HOSTS or "biznis-studio.github.io" in url:
                continue
            links[url].add(str(page.relative_to(site_dir)))
    return links


def check(url: str) -> tuple[bool, str]:
    req = Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:
            return 200 <= resp.status < 400, str(resp.status)
    except HTTPError as exc:                 # reached the server, it said no
        return False, str(exc.code)
    except URLError as exc:                  # never got a usable response
        return False, f"unreachable ({exc.reason})"
    except Exception as exc:                 # timeouts land here too
        return False, type(exc).__name__


def main() -> int:
    links = hand_placed_links(SITE_DIR)
    print(f"[check_links] {len(links)} hand-placed external links\n")
    failures = []
    for url in sorted(links):
        ok, detail = check(url)
        print(f"  {'ok  ' if ok else 'FAIL'} {detail:<22} {url}")
        if not ok:
            failures.append((url, detail, sorted(links[url])))

    if not failures:
        print("\n[check_links] all reachable")
        return 0
    print(f"\n[check_links] {len(failures)} need a look (advisory, not a build failure):")
    for url, detail, pages in failures:
        print(f"  {url}\n      {detail} - linked from: {', '.join(pages)}")
    return 0        # advisory by design: never fail a pipeline on someone else's uptime


if __name__ == "__main__":
    sys.exit(main())
