"""Deploy and then prove it actually worked.

Written after the live site sat several changes behind for hours while every
local build looked perfect. Two failure modes caused it, and both are silent:

  1. The pipeline's own push loses a race against a push from a working
     session, the run fails, and `deploy-pages` never executes.
  2. A rebase conflict on a generated file gets resolved the wrong way -
     during a rebase `--ours` means *upstream*, not your commit - and rows
     vanish from the database while the build still succeeds.

So this does not report success on "the workflow was triggered". It waits for
the run to finish, then fetches the live URL and checks the change is really
there. Exit code 0 means verified in production, nothing weaker.

Usage:
    python3 scripts/deploy.py --expect "some text that must appear on the homepage"
    python3 scripts/deploy.py --expect "..." --url https://biznis-studio.github.io/sk/
"""
import argparse
import json
import subprocess
import sys
import time
import html
import urllib.request

BASE = "https://biznis-studio.github.io"
UA = {"User-Agent": "Mozilla/5.0 (compatible; biznis-deploy-check)"}


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True).stdout.strip()


def latest_run_id() -> str:
    out = gh("run", "list", "--workflow=pipeline.yml", "--limit", "1",
             "--json", "databaseId")
    return str(json.loads(out)[0]["databaseId"])


def wait_for(run_id: str, timeout: int = 900) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = gh("run", "view", run_id, "--json", "status,conclusion",
                    "-q", ".status + \" \" + (.conclusion // \"pending\")")
        if status.startswith("completed"):
            return status.split()[-1]
        time.sleep(15)
    return "timeout"


def fetch(url: str) -> str:
    """Stiahne stránku a ROZKÓDUJE HTML entity pred porovnaním.

    Bez toho `--expect "Pospájať"` nikdy nesedí, lebo v HTML je to
    `Pospájať`. Väčšina našej slovenčiny je zakódovaná v entitách, takže
    kontrola hlásila "nie je naživo" aj vtedy, keď stránka bola nasadená
    správne — overené 2026-08-18, živá stránka bola znak po znaku
    identická s lokálnym buildom a kontrola aj tak zlyhala. Falošný poplach
    je horší než žiadna kontrola: naučí človeka ju ignorovať.
    """
    req = urllib.request.Request(f"{url}?cachebust={int(time.time())}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        surove = resp.read().decode("utf-8", "ignore")
    return html.unescape(surove)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect", required=True,
                    help="text that must be present on the live page afterwards")
    ap.add_argument("--url", default=f"{BASE}/")
    args = ap.parse_args()

    print("[deploy] triggering pipeline")
    subprocess.run(["gh", "workflow", "run", "pipeline.yml"], check=True)
    time.sleep(8)
    run_id = latest_run_id()
    print(f"[deploy] run {run_id} - waiting")

    result = wait_for(run_id)
    print(f"[deploy] run finished: {result}")
    if result != "success":
        print("[deploy] FAILED - the site was NOT updated. Check:")
        print(f"         gh run view {run_id} --log-failed")
        return 1

    # GitHub Pages needs a moment to serve the new artifact.
    for attempt in range(1, 6):
        time.sleep(15)
        try:
            body = fetch(args.url)
        except Exception as exc:
            print(f"[deploy] fetch attempt {attempt} failed: {type(exc).__name__}")
            continue
        if args.expect in body:
            print(f"[deploy] VERIFIED live at {args.url}")
            return 0
        print(f"[deploy] attempt {attempt}: expected text not live yet")

    print("[deploy] Workflow succeeded but the expected text is NOT on the live page.")
    print("         Deployed content differs from what was built - do not assume success.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
