"""Frontier Agent — snímanie globálnej špičky AI a marketingu.

Doterajší `market_research_agent` sníma Hacker News, Wikipedia pageviews, npm,
StackExchange a GitHub trending. To je anglický vývojársky svet a odpovedá na
otázku „o čom sa hovorí“. Nás zaujíma iná otázka: **čo sa práve dá spraviť, čo
sa vlani nedalo** — teda posun v schopnostiach modelov, v tom, ako sa AI
pokročilo používa, a v tom, ako sa mení marketing a vyhľadávanie.

Zdroje sú overené naživo 2026-08-17 (HTTP 200, nie z výsledkov vyhľadávania):

    arXiv cs.AI / cs.CL      výskum, primárny zdroj
    HuggingFace daily papers  čo z výskumu si komunita naozaj všimla
    HuggingFace models        ktoré modely rastú
    OpenAI news RSS           oznámenia priamo od výrobcu
    Google Research blog      to isté z druhej strany
    Google Search Central     ako sa mení vyhľadávanie
    Search Engine Land        marketing a AI vo vyhľadávaní
    Microsoft 365 roadmap     čo pribúda v prostredí, kde naši zákazníci pracujú
    GitHub (nové agent repá)  čo sa reálne stavia

Medzera, ktorú priznávam: **Anthropic nemá RSS na `/news/rss.xml` ani na
`/engineering/rss.xml` — oba vracajú 404.** Nevymýšľam mu URL. Kým sa nenájde
overená cesta, Anthropic sníma človek.

Čo tento agent zámerne NEROBÍ: nevykladá. Sťahovanie, odstránenie duplikátov,
filtrovanie a zoradenie je práca pre obyčajný kód. Výklad — *čo to zlacňuje,
čo to umožňuje, čo to ruší* — vyžaduje úsudok a robí sa v samostatnom kroku
nad frontou, ktorú tento agent naplní. Zmiešať to znamená vyrobiť skládku,
kde sa nedá odlíšiť pozorovanie od záveru.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime
from typing import Iterable, Optional

import requests

from agents.common import DEFAULT_HEADERS, DEFAULT_TIMEOUT, http_get, now_iso
from core.db import get_connection

ZDROJ = "frontier"

# Čo považujeme za relevantné. Zámerne úzke: zaujíma nás pokročilé POUŽÍVANIE
# AI a to, ako sa mení marketing — nie každá správa, v ktorej padne slovo "AI".
# Široký filter by vrátil skládku a skládku nikto neprečíta.
RELEVANTNE = re.compile(
    r"\b("
    r"agent|agentic|multi-?agent|tool[- ]use|function call|"
    r"eval|evaluation|benchmark|verif|ground(ing|ed)|hallucinat|"
    r"context (engineering|window|management)|long[- ]context|memory|"
    r"rag|retrieval|mcp|model context protocol|connector|"
    r"reason(ing)?|chain[- ]of[- ]thought|distill|fine[- ]?tun|"
    r"prompt (engineering|optimi)|self[- ](improv|evolv)|"
    r"computer[- ]use|browser (agent|use)|coding agent|"
    r"copilot|workflow automation|"
    r"seo|geo|generative engine|ai search|ai overview|search behaviou?r|"
    r"conversion|positioning|content strategy"
    r")\b",
    re.I,
)


# --- pomocné ---------------------------------------------------------------

def _rss(url: str, limit: int) -> list[dict]:
    """Prečíta RSS/Atom a vráti položky. Nikdy nevyhodí výnimku."""
    try:
        r = requests.get(url, headers=DEFAULT_HEADERS, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:
            return []
        korene = ET.fromstring(r.content)
    except (requests.RequestException, ET.ParseError):
        return []

    polozky: list[dict] = []
    # RSS 2.0 aj Atom jedným priechodom — líšia sa len názvami značiek.
    for item in korene.iter():
        if not item.tag.endswith(("item", "entry")):
            continue
        nazov = odkaz = datum = None
        for pole in item:
            znacka = pole.tag.rsplit("}", 1)[-1]
            if znacka == "title":
                nazov = (pole.text or "").strip()
            elif znacka == "link":
                odkaz = (pole.text or pole.attrib.get("href") or "").strip()
            elif znacka in ("pubDate", "updated", "published"):
                datum = (pole.text or "").strip()
        if nazov:
            polozky.append({"nazov": nazov, "url": odkaz, "datum": datum})
        if len(polozky) >= limit:
            break
    return polozky


def _polozka(zdroj: str, typ: str, nazov: str, url: Optional[str],
             hodnota: float, surove: object) -> dict:
    return {
        "source": f"{ZDROJ}:{zdroj}",
        "signal_type": typ,
        "term": nazov[:400],
        "metric_value": hodnota,
        "url": url,
        "payload_json": json.dumps(surove, ensure_ascii=False)[:4000],
    }


# --- zdroje ----------------------------------------------------------------

def fetch_arxiv(kategorie: Iterable[str] = ("cs.AI", "cs.CL"),
                limit: int = 40) -> list[dict]:
    """Najnovšie práce. Primárny zdroj — nie niekoho zhrnutie."""
    von: list[dict] = []
    for kat in kategorie:
        polozky = _rss(
            "https://export.arxiv.org/api/query"
            f"?search_query=cat:{kat}&sortBy=submittedDate"
            f"&sortOrder=descending&max_results={limit}",
            limit,
        )
        for p in polozky:
            von.append(_polozka("arxiv", "praca", p["nazov"], p["url"], 0.0, p))
    return von


def fetch_hf_papers(limit: int = 30) -> list[dict]:
    """Denné práce na HuggingFace — filter, ktorý už spravila komunita."""
    data = http_get("https://huggingface.co/api/daily_papers",
                    params={"limit": limit})
    if not isinstance(data, list):
        return []
    von = []
    for r in data:
        praca = r.get("paper") or {}
        nazov = praca.get("title") or ""
        if not nazov:
            continue
        von.append(_polozka(
            "hf_papers", "praca", nazov,
            f"https://huggingface.co/papers/{praca.get('id','')}",
            float(praca.get("upvotes") or r.get("numComments") or 0),
            {"id": praca.get("id"), "upvotes": praca.get("upvotes")},
        ))
    return von


def fetch_hf_models(limit: int = 25) -> list[dict]:
    """Ktoré modely rastú. Schopnosť sa posúva tam, kam ide pozornosť."""
    data = http_get("https://huggingface.co/api/models",
                    params={"sort": "trendingScore", "limit": limit})
    if not isinstance(data, list):
        return []
    return [
        _polozka("hf_models", "model", r.get("id", ""),
                 f"https://huggingface.co/{r.get('id','')}",
                 float(r.get("likes") or 0),
                 {"id": r.get("id"), "likes": r.get("likes")})
        for r in data if r.get("id")
    ]


def fetch_vyrobcovia(limit: int = 15) -> list[dict]:
    """Oznámenia priamo od výrobcov. Najvyššia kvalita zdroja, žiadny prostredník.

    `ms365_roadmap` tu zámerne nie je, hoci odpovedá 200: je to firehose
    administrátorských drobností Teams a na otázku „čo sa dá nové spraviť“
    neodpovedá. Blog Microsoft 365 áno.
    """
    kanaly = {
        "openai": "https://openai.com/news/rss.xml",
        "google_research": "https://research.google/blog/rss/",
        "aws_ml": "https://aws.amazon.com/blogs/machine-learning/feed/",
        "ms365_blog": "https://www.microsoft.com/en-us/microsoft-365/blog/feed/",
    }
    von = []
    for meno, url in kanaly.items():
        for p in _rss(url, limit):
            von.append(_polozka(meno, "oznamenie", p["nazov"], p["url"], 0.0, p))
    return von


def fetch_praktici(limit: int = 25) -> list[dict]:
    """Ľudia, ktorí AI pokročilo POUŽÍVAJÚ, nie o nej píšu tlačové správy.

    Simon Willison je tu preto, že dôsledne píše, čo naozaj skúsil a čo z toho
    nevyšlo — to je presne ten druh poznatku, ktorý sa nedá vyčítať z oznámenia
    výrobcu. Ak jeho feed raz stíchne, tento zdroj sa nahrádza, nie dopĺňa.
    """
    von = []
    for p in _rss("https://simonwillison.net/atom/everything/", limit):
        von.append(_polozka("willison", "prax", p["nazov"], p["url"], 0.0, p))
    return von


def fetch_schopnosti(limit: int = 60) -> list[dict]:
    """Čo sa dá kúpiť a za koľko — naprieč všetkými výrobcami z jedného miesta.

    OpenRouter drží ceny a dĺžku kontextu stoviek modelov. Posun v cene za token
    alebo v dĺžke kontextu mení, čo je vôbec ekonomicky možné postaviť — a to je
    poznatok o schopnostiach, nie marketing.
    """
    data = http_get("https://openrouter.ai/api/v1/models")
    if not isinstance(data, dict):
        return []
    modely = data.get("data") or []
    von = []
    for m in modely[:limit]:
        ceny = m.get("pricing") or {}
        von.append(_polozka(
            "openrouter", "schopnost",
            f"{m.get('id','')} — kontext {m.get('context_length','?')}, "
            f"vstup {ceny.get('prompt','?')}/token",
            f"https://openrouter.ai/{m.get('id','')}",
            float(m.get("context_length") or 0),
            {"id": m.get("id"), "context_length": m.get("context_length"),
             "pricing": ceny},
        ))
    return von


def fetch_konektory(limit: int = 30) -> list[dict]:
    """Oficiálny register MCP serverov — čím sa dá AI napojiť na firemné dáta.

    Priamo pod našou pozíciou: overiteľnosť potrebuje prístup k tomu, čo sa
    overuje. Rast registra je merateľný signál, čo je už napojiteľné bez práce.
    """
    data = http_get("https://registry.modelcontextprotocol.io/v0/servers",
                    params={"limit": limit})
    if not isinstance(data, dict):
        return []
    von = []
    for r in data.get("servers", []):
        s = r.get("server") or r
        meno = s.get("name") or ""
        if not meno:
            continue
        von.append(_polozka(
            "mcp_registry", "konektor",
            f"{meno} — {(s.get('description') or '')[:180]}",
            s.get("repository", {}).get("url") if isinstance(s.get("repository"), dict) else None,
            0.0, {"name": meno},
        ))
    return von


def fetch_marketing(limit: int = 20) -> list[dict]:
    """Ako sa mení vyhľadávanie a marketing. Druhá polovica zadania."""
    kanaly = {
        "google_search_central": "https://developers.google.com/search/blog/feed.xml",
        "search_engine_land": "https://searchengineland.com/feed",
        "ahrefs": "https://ahrefs.com/blog/feed/",
        "moz": "https://moz.com/posts/rss/blog",
    }
    von = []
    for meno, url in kanaly.items():
        for p in _rss(url, limit):
            von.append(_polozka(meno, "marketing", p["nazov"], p["url"], 0.0, p))
    return von


def fetch_github_agenti(limit: int = 25) -> list[dict]:
    """Nové repozitáre okolo agentov — čo sa reálne stavia, nie o čom sa píše."""
    data = http_get("https://api.github.com/search/repositories", params={
        "q": f"llm agent created:>{date.today().replace(day=1).isoformat()}",
        "sort": "stars", "order": "desc", "per_page": limit,
    })
    if not isinstance(data, dict):
        return []
    return [
        _polozka("github", "repo",
                 f"{r.get('full_name','')} — {(r.get('description') or '')[:200]}",
                 r.get("html_url"), float(r.get("stargazers_count") or 0),
                 {"full_name": r.get("full_name"), "stars": r.get("stargazers_count")})
        for r in data.get("items", [])
    ]


ZDROJE = [
    fetch_arxiv,
    fetch_hf_papers,
    fetch_hf_models,
    fetch_vyrobcovia,
    fetch_praktici,
    fetch_schopnosti,
    fetch_konektory,
    fetch_marketing,
    fetch_github_agenti,
]


# --- beh -------------------------------------------------------------------

# Zdroje, ktoré slovníkový filter obchádzajú, lebo ich už predfiltrovalo to,
# že sú oficiálne alebo redakčné. „The builder's guide to GPT-5.6“ je presne to,
# čo hľadáme, a cez slovník by neprešlo — filter je na firehose (arXiv, GitHub,
# roadmap Microsoftu), nie na oznámenia výrobcu.
# Google Research tu zámerne NIE JE: je to laboratórium naprieč celou vedou
# Googlu, takže „oficiálne“ pri ňom neznamená „úzke“ — bez filtra doň natieklo
# 15 prác o dermatológii, doprave a kvantových počítačoch. Filter mu ponechal
# presne tie o uvažovaní a overiteľnosti, ktoré chceme.
BEZ_FILTRA = {
    "frontier:openai",
    "frontier:google_search_central",
    "frontier:hf_models",       # názov modelu je identifikátor, nie veta
}


def _relevantne(polozky: list[dict]) -> list[dict]:
    """Filter + odstránenie duplikátov. Obyčajný kód, žiadny model."""
    videne: set[str] = set()
    von: list[dict] = []
    for p in polozky:
        text = p["term"]
        if p["source"] not in BEZ_FILTRA and not RELEVANTNE.search(text):
            continue
        kluc = re.sub(r"\W+", "", text.lower())[:120]
        if kluc in videne:
            continue
        videne.add(kluc)
        von.append(p)
    return von


def run(run_id: Optional[int] = None) -> int:
    """Nasníma špičku do `signals_raw`. Vracia počet uložených položiek."""
    conn = get_connection()
    try:
        if run_id is None:
            cur = conn.execute(
                "INSERT INTO runs (started_at, stage, status) "
                "VALUES (?, 'frontier', 'running')", (now_iso(),))
            run_id = int(cur.lastrowid)

        surove: list[dict] = []
        for zdroj in ZDROJE:
            try:
                surove.extend(zdroj())
            except Exception as chyba:      # jeden mŕtvy zdroj nesmie zvaliť beh
                print(f"[frontier_agent] {zdroj.__name__} zlyhal: {chyba}")

        polozky = _relevantne(surove)
        teraz = now_iso()
        conn.executemany(
            "INSERT INTO signals_raw "
            "(run_id, source, signal_type, term, metric_value, url, fetched_at, payload_json) "
            "VALUES (?,?,?,?,?,?,?,?)",
            [(run_id, p["source"], p["signal_type"], p["term"], p["metric_value"],
              p["url"], teraz, p["payload_json"]) for p in polozky],
        )
        conn.commit()

        podla_zdroja: dict[str, int] = {}
        for p in polozky:
            podla_zdroja[p["source"]] = podla_zdroja.get(p["source"], 0) + 1
        rozpis = ", ".join(f"{k.split(':')[1]}={v}" for k, v in sorted(podla_zdroja.items()))
        print(f"[frontier_agent] {len(surove)} nasnímaných → "
              f"{len(polozky)} relevantných ({rozpis})")
        return len(polozky)
    finally:
        conn.close()


def na_vyklad(limit: int = 20) -> list[dict]:
    """Fronta pozorovaní, ktoré ešte nikto nevyložil.

    Toto je jediné miesto, kde sa zo skládky stáva poznatok: nad každou
    položkou treba odpovedať, čo zlacňuje, čo umožňuje, čo ruší a či to
    ohrozuje alebo posilňuje našu pozíciu. Robí to úsudok, nie tento súbor.

    Poradie NEJDE podľa `metric_value`: lajky modelu, hviezdy repozitára a
    upvoty práce sú neporovnateľné čísla v jednom stĺpci, a zoradenie podľa
    nich vytlačí oznámenie výrobcu (hodnota 0) na koniec za tisíc lajkov
    ľubovoľného modelu. Radíme podľa kvality zdroja a až vnútri nej podľa čísla.
    """
    PORADIE_ZDROJA = {
        "frontier:willison": 1,          # čo niekto naozaj skúsil
        "frontier:openai": 1,
        "frontier:google_search_central": 2,
        "frontier:ms365_blog": 2,
        "frontier:mcp_registry": 2,
        "frontier:openrouter": 3,
        "frontier:ahrefs": 3,
        "frontier:moz": 3,
        "frontier:search_engine_land": 3,
        "frontier:hf_papers": 4,
        "frontier:google_research": 4,
        "frontier:aws_ml": 5,
        "frontier:arxiv": 5,
        "frontier:github": 6,
        "frontier:hf_models": 7,
    }
    conn = get_connection()
    try:
        riadky = [dict(r) for r in conn.execute(
            "SELECT s.term, s.url, s.source, s.metric_value FROM signals_raw s "
            "WHERE s.source LIKE 'frontier:%' "
            "AND NOT EXISTS (SELECT 1 FROM poznatky p WHERE p.zdroj = s.url) "
            "ORDER BY s.id DESC")]
        riadky.sort(key=lambda r: (PORADIE_ZDROJA.get(r["source"], 9),
                                   -(r["metric_value"] or 0)))
        # Striedanie zdrojov. Bez neho zaplní vrch fronty jeden zdroj (naposledy
        # 14 z 14 riadkov Google Research) a ostatných sedem sa nikdy nedostane
        # na oči — kvalitné poradie samo o sebe rôznorodosť nezaručí.
        podla_zdroja: dict[str, list[dict]] = {}
        for r in riadky:
            podla_zdroja.setdefault(r["source"], []).append(r)
        poradie = sorted(podla_zdroja, key=lambda z: PORADIE_ZDROJA.get(z, 9))
        von: list[dict] = []
        while len(von) < limit and any(podla_zdroja.values()):
            for zdroj in poradie:
                if podla_zdroja[zdroj]:
                    von.append(podla_zdroja[zdroj].pop(0))
                    if len(von) >= limit:
                        break
        return von
    finally:
        conn.close()


if __name__ == "__main__":
    run()
