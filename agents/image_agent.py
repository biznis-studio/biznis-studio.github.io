"""Image Agent.

Sources real photography for product, blog, tool and news pages from
Openverse, restricted to **CC0 and Public Domain Mark only**. That
restriction is the whole point: those two licences place no attribution,
share-alike, or commercial-use conditions on the work, so the images are
unambiguously safe on a commercial site. Anything CC-BY, CC-BY-SA or
otherwise conditional is never requested and never downloaded.

Images are downloaded once, cropped to a consistent 16:9, resized, and
committed into site/assets/img/ as local files. Hotlinking the original
host would be both fragile (dead links break the design) and impolite
(serving our traffic off someone else's bandwidth).

Relevance is deliberate, not automatic: each page has a hand-written
search query in QUERIES below, because "topically appropriate" is a
judgement call a keyword match gets wrong often enough to look silly.

Even though CC0/PDM require no credit, every image's source, creator and
licence is recorded in data/image_credits.json and published on the
site's credits page - crediting people who released work for free costs
nothing and is the decent thing to do.
"""
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "site" / "assets" / "img"
CREDITS_FILE = ROOT / "data" / "image_credits.json"

API = "https://api.openverse.org/v1/images/"
PEXELS_API = "https://api.pexels.com/v1/search"
# Pexels rejects a bare Python user-agent with 403, so send a real one.
UA = {"User-Agent": "Mozilla/5.0 (compatible; biznis-site/1.0; "
                    "+https://biznis-studio.github.io)"}

# Primary source when a key is configured (GitHub Actions secret
# PEXELS_API_KEY - never committed, the repo is public). The Pexels
# licence allows commercial use and modification and requires no
# attribution; we credit photographers on /credits.html regardless.
# Openverse CC0/PDM stays as the fallback so the pipeline still produces
# images with no key at all.
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
# Only licences with no attribution/share-alike/commercial conditions.
ALLOWED_LICENSES = "cc0,pdm"

# Openverse's CC0/PDM pool is dominated by museum and natural-history
# archives, so an unfiltered search confidently returns a sepia studio
# portrait for "tailor" and a ransom-note letter collage for "web design".
# Two defences: prefer a modern stock-photo source first, and refuse the
# archive collections outright on the fallback pass.
PREFERRED_SOURCES = ["rawpixel"]
BLOCKED_SOURCES = {
    "europeana", "met", "smithsonian_national_museum_of_natural_history",
    "digitaltmuseum", "finnish_heritage_agency", "museumsvictoria",
    "bio_diversity", "sciencemuseum", "geographorguk", "inaturalist",
    "svgsilh", "statensmuseum", "brooklynmuseum", "clevelandmuseum",
    "nypl", "spacex", "thorvaldsensmuseum", "wordpress", "themet",
    "smithsonian_cooper_hewitt_museum", "smithsonian_freer_gallery_of_art",
}
# Cut-out assets (transparent PNGs, clipart, stickers) look broken as card
# art - the alpha channel renders as a grey checkerboard. Restricting to
# JPEG removes the whole category, since photographs are JPEGs.
BLOCKED_CREATORS = {"themet", "thegetty", "biodiversity heritage library",
                    "smithsonian", "rijksmuseum", "nypl", "wellcome collection"}
BLOCKED_TITLE_WORDS = ("png", "transparent", "clipart", "clip art", "sticker",
                       "illustration", "vector", "icon", "collage element")
MIN_WIDTH = 1000
CARD_SIZE = (800, 450)     # 16:9 card art
HERO_SIZE = (1600, 700)    # wide homepage banner

# Hand-picked query per page slug. Relevance beats automation here.
QUERIES = {
    # --- products ---
    "freelance-scope-creep-defense-kit": ["contract signature pen", "contract document", "paperwork desk"],
    "client-retainer-renewal-kit": ["business meeting people table", "colleagues meeting office", "two people talking desk"],
    "change-request-log-template": ["spreadsheet", "notebook table data", "office paperwork"],
    "retainer-renewal-tracker-template": ["calendar", "planner diary", "schedule agenda"],
    "the-practical-guide-to-automation": ["gears machinery", "robot arm factory", "industrial machine"],
    "the-practical-guide-to-xlsx": ["spreadsheet", "financial chart paper", "accounting numbers"],
    "checklist-pdf-notion": ["checklist", "notebook pen writing", "to do list"],
    "spreadsheet-pack": ["laptop desk office", "computer desk work", "office workspace"],
    "late-payment-recovery-kit": ["overdue invoice paperwork desk",
        "calendar deadline reminder desk", "person reviewing documents worried"],
    "invoice-pack": ["accounting desk documents", "bill payment desk", "paperwork finance desk"],
    "free-online-calculator": ["calculator", "calculator desk", "numbers math"],
    "eu-digital-seller-compliance-checklist": ["european union flag", "europe flag", "brussels building"],
    "resume-gap-job-title-explainer-scripts": ["job interview", "resume cv paper", "office interview"],
    "custom-website-design-development": ["web design code", "programming code screen", "developer laptop"],
    "custom-chatbot-development": ["smartphone screen apps hands", "mobile phone typing hands", "smartphone technology desk"],
    "automation-integrations": ["server automation code screen", "gears machinery industrial",
        "conveyor belt automation factory"],
    "design-branding-visual-identity": ["graphic designer working colour palette",
        "design studio sketches branding", "designer desk colour swatches"],
    "tailored-digital-product": ["designer sketching workspace", "blueprint design desk", "creative studio desk"],
    # --- blog ---
    "telling-clients-rate-increase": ["business handshake agreement office",
        "person writing notes desk meeting", "professional discussion two people"],
    "what-to-say-scope-creep": ["person typing laptop email", "writing email keyboard hands",
        "person working laptop message"],
    "scope-creep-by-the-numbers": ["calculator money", "coins calculator", "finance desk"],
    "seven-places-worth-reading": ["books library", "bookshelf books", "reading book"],
    "pricing-digital-products": ["price tag", "shopping price", "sale tag"],
    "test-ai-assistant-before-staff-use-it": ["quality inspection checklist clipboard",
        "engineer checking test results laboratory", "person inspecting parts factory desk"],
    # --- tools ---
    "machinery-regulation-digital-instructions": ["industrial machine factory floor",
        "cnc machine manufacturing", "industrial machinery equipment"],
    "scope-creep-cost-calculator": ["calculator coins", "money calculator", "calculator"],
    "freelance-rate-calculator": ["banknotes money", "cash money", "coins currency"],
    # --- news topics ---
    "news-ai": ["server room", "data center servers", "computer server"],
    "news-quantum": ["laboratory science", "physics laboratory", "science research lab"],
    "news-technology": ["circuit board", "electronics chip", "computer hardware"],
    "news-economy": ["stock market chart", "financial chart graph", "trading screen"],
    # --- homepage hero ---
    # User picked this one explicitly - do not change the query without asking.
    "kolko-stoji-chatbot-pre-firmu": ["smartphone chat message screen",
        "customer service headset desk", "mobile phone typing hands"],
    "potrebuje-moja-firma-webstranku": ["small business owner shop counter",
        "local business storefront", "person working small business"],
    "kolko-stoji-webstranka": ["laptop website design desk", "web designer working screen",
        "person planning notes laptop"],
    "automatizacia-v-malej-firme": ["gears machinery automation", "conveyor factory automation",
        "industrial robot arm"],
    "kolko-stoji-logo-a-vizualna-identita": ["graphic designer sketching logo",
        "designer drawing brand sketches", "design studio pencil sketches paper"],
    "ktore-rozhodnutie-zverit-ai": ["fork in the road path",
        "railway track switch junction", "two paths diverging"],
    "overovanie-vam-zoberie-uspory": ["person reviewing documents magnifying glass",
        "proofreading paperwork desk close up", "person checking documents office desk"],
    "oplati-sa-nasadit-ai": ["abacus counting beads", "hand writing numbers notebook",
        "calculator pen desk paper"],
    "efaktura-2027-test": ["accounting calculator receipts", "bookkeeping ledger calculator desk",
        "financial documents spreadsheet desk"],
    "zapis-pred-nasadenim-ai": ["blank notebook pen desk", "handwriting notes paper desk",
        "clipboard checklist pen"],
    "ako-zistite-ci-ai-nieco-priniesla": ["measuring tape ruler close up",
        "stopwatch timer hand", "scales balance weighing"],
    "preco-zamestnanci-prestanu-pouzivat-ai": ["empty office desk laptop closed",
        "unused workspace empty chair office", "person turning away from computer desk"],
    "sk-copilot-vrstva": ["team working laptops office meeting",
        "colleagues office computer screens", "modern office team working"],
    "hero": ["office workspace desk", "modern office interior", "desk laptop window"],
}


def _search_pexels(query: str) -> list[dict]:
    """Pexels results normalised into the same shape as Openverse ones."""
    if not PEXELS_API_KEY:
        return []
    params = urllib.parse.urlencode({
        "query": query, "per_page": 15, "orientation": "landscape",
    })
    try:
        req = urllib.request.Request(f"{PEXELS_API}?{params}",
                                     headers={**UA, "Authorization": PEXELS_API_KEY})
        with urllib.request.urlopen(req, timeout=25) as resp:
            photos = json.load(resp).get("photos", [])
    except Exception as exc:
        print(f"[image_agent] pexels search failed '{query}': {type(exc).__name__}")
        return []
    return [{
        "url": p["src"].get("large2x") or p["src"].get("large") or p["src"]["original"],
        "title": p.get("alt") or query,
        "creator": p.get("photographer") or "Unknown",
        "license": "Pexels License",
        "source": "pexels",
        "foreign_landing_url": p.get("url") or "",
        "width": p.get("width") or 0,
        "height": p.get("height") or 0,
        "_curated": True,   # skip the relevance gate: Pexels ranks its own
                            # library well and its alt text is often empty
    } for p in photos]


def _search(query: str, source: Optional[str] = None) -> list[dict]:
    fields = {
        "q": query,
        "license": ALLOWED_LICENSES,
        "page_size": 20,
        "mature": "false",
        "extension": "jpg",
    }
    if source:
        fields["source"] = source
    params = urllib.parse.urlencode(fields)
    try:
        req = urllib.request.Request(f"{API}?{params}", headers=UA)
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.load(resp).get("results", [])
    except Exception as exc:
        print(f"[image_agent] search failed '{query}': {type(exc).__name__}")
        return []


_STOPWORDS = {"the", "a", "of", "and", "in", "on", "with", "to"}


def _is_usable(result: dict) -> bool:
    """Reject archive/museum collections and anything too small to look
    sharp as card art."""
    if result.get("_curated"):
        return (result.get("width") or 0) >= MIN_WIDTH
    if (result.get("source") or "").lower() in BLOCKED_SOURCES:
        return False
    if (result.get("creator") or "").lower().strip() in BLOCKED_CREATORS:
        return False
    title = (result.get("title") or "").lower()
    if any(word in title for word in BLOCKED_TITLE_WORDS):
        return False
    return (result.get("width") or 0) >= MIN_WIDTH


def _is_relevant(result: dict, query: str) -> bool:
    """Require the image's own title/tags to actually mention something
    from the query. Without this the CC0/PDM pool - which is small - hands
    back confidently-ranked but topically wrong photos (a Forest Service
    landscape for "physics laboratory" was the case that prompted this)."""
    if result.get("_curated"):
        return True
    words = {w for w in query.lower().split() if w not in _STOPWORDS and len(w) > 2}
    haystack = (result.get("title") or "").lower()
    haystack += " " + " ".join(
        (t.get("name") or "").lower() for t in (result.get("tags") or [])
    )
    return any(w in haystack for w in words)


def _download(url: str) -> Optional[bytes]:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as resp:
            if not (resp.headers.get("Content-Type") or "").startswith("image/"):
                return None
            return resp.read()
    except Exception:
        return None


def _process(raw: bytes, size: tuple) -> Optional[bytes]:
    """Centre-crop to the target aspect ratio, resize, save as JPEG.

    Chybajuci Pillow NESMIE zhodit cely pipeline. 2026-08-16 to presne to
    urobilo: novy clanok potreboval obrazok, PIL v CI nebol (do vtedy mali
    vsetky slugy obrazok v repozitari, takze sa sem nikdy nedoslo) a spadol
    cely beh. Chybajuci obrazok je kozmeticka chyba, nie dovod nevydat web.
    """
    try:
        from PIL import Image
    except ModuleNotFoundError:
        print("[image_agent] Pillow nie je nainstalovany - obrazky sa preskakuju "
              "(pip install -r requirements.txt)")
        return None
    try:
        im = Image.open(io.BytesIO(raw))
        im = im.convert("RGB")
    except Exception:
        return None
    tw, th = size
    target = tw / th
    w, h = im.size
    if w < 400 or h < 220:
        return None
    if w / h > target:                      # too wide -> trim sides
        new_w = int(h * target)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    else:                                   # too tall -> trim top/bottom
        new_h = int(w / target)
        top = (h - new_h) // 3              # bias upward: subjects sit high
        im = im.crop((0, top, w, top + new_h))
    im = im.resize(size, Image.LANCZOS)
    out = io.BytesIO()
    im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    return out.getvalue()


def fetch_one(slug: str, queries, size: tuple) -> Optional[dict]:
    """Try each query in order until one yields a topically relevant,
    usable image. Returns its credit record."""
    if isinstance(queries, str):
        queries = [queries]
    # Pass 0: Pexels (professional stock, best quality) when a key exists.
    # Pass 1: Openverse restricted to a modern stock source.
    # Pass 2: wider Openverse CC0/PDM pool with the archive block applied.
    attempts = [(q, "pexels") for q in queries]
    attempts += [(q, s) for s in PREFERRED_SOURCES for q in queries]
    attempts += [(q, None) for q in queries]
    for query, source in attempts:
        results = _search_pexels(query) if source == "pexels" else _search(query, source)
        for result in results:
            if not _is_usable(result) or not _is_relevant(result, query):
                continue
            src = result.get("url")
            if not src:
                continue
            raw = _download(src)
            if not raw:
                continue
            processed = _process(raw, size)
            if not processed:
                continue
            (IMG_DIR / f"{slug}.jpg").write_bytes(processed)
            return {
                "slug": slug,
                "query": query,
                "title": result.get("title") or "",
                "creator": result.get("creator") or "Unknown",
                "license": f'{result.get("license", "")} '
                           f'{result.get("license_version", "")}'.strip(),
                "source": result.get("source") or "",
                "source_page": result.get("foreign_landing_url") or "",
            }
    print(f"[image_agent] no relevant CC0/PDM image found for '{slug}'")
    return None


def _warn_missing_queries() -> None:
    """Nahlas kazdy publikovany clanok, ktory nema svoj dotaz v QUERIES.

    Existuje preto, ze clanok o logu isiel von 2026-08-01 bez obrazka a
    vsimlo sa to az 2026-08-16. Obrazok sa nefetchne sam od seba: slug musi
    byt v QUERIES. Toto je jedina vec, ktora to prezradi skor nez citatel.
    """
    from pathlib import Path as _P
    import re as _re
    root = _P(__file__).resolve().parent.parent
    slugs = set()
    for f in (root / "content" / "sk").glob("*.md"):
        slugs.add(_re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem))
    for f in (root / "content" / "blog").glob("*.md"):
        slugs.add(_re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem))
    # Nestaci sa pytat zdrojovych markdownov. Stranka bezplatneho testu
    # e-faktury sa nestavia z content/*.md ani z TOOLS, takze isla von
    # bez obrazka a tato kontrola ju nevidela (2026-08-19). Pytame sa
    # preto toho, co je naozaj publikovane.
    for adresar in ("sk", "blog", "tools"):
        for f in (root / "site" / adresar).glob("*.html"):
            if f.stem == "index":
                continue
            slugs.add(f.stem)
    chyba = sorted(s for s in slugs if s and s not in QUERIES)
    if chyba:
        print("[image_agent] POZOR - clanok bez dotazu v QUERIES, teda aj bez "
              "obrazka: " + ", ".join(chyba))


def run(force: bool = False) -> int:
    _warn_missing_queries()
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    CREDITS_FILE.parent.mkdir(parents=True, exist_ok=True)
    credits = {}
    if CREDITS_FILE.exists():
        try:
            credits = {c["slug"]: c for c in json.loads(CREDITS_FILE.read_text())}
        except Exception:
            credits = {}

    added = 0
    for slug, query in QUERIES.items():
        path = IMG_DIR / f"{slug}.jpg"
        if path.exists() and slug in credits and not force:
            continue
        size = HERO_SIZE if slug == "hero" else CARD_SIZE
        record = fetch_one(slug, query, size)
        if record:
            credits[slug] = record
            added += 1
            print(f"[image_agent] {slug}.jpg  <- {record['license']}  ({record['creator']})")
        time.sleep(1.0)   # be a polite API citizen

    CREDITS_FILE.write_text(json.dumps(sorted(credits.values(), key=lambda c: c["slug"]),
                                       indent=2) + "\n")
    print(f"[image_agent] {added} new images ({len(credits)} total)")
    return added


def has_image(slug: str) -> bool:
    return (IMG_DIR / f"{slug}.jpg").exists()


def load_credits() -> list[dict]:
    if not CREDITS_FILE.exists():
        return []
    try:
        return json.loads(CREDITS_FILE.read_text())
    except Exception:
        return []


if __name__ == "__main__":
    run(force="--force" in sys.argv)
