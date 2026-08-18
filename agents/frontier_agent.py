"""Frontier Agent — snímanie globálnej špičky AI a marketingu.

Doterajší `market_research_agent` sníma Hacker News, Wikipedia pageviews, npm,
StackExchange a GitHub trending. To je anglický vývojársky svet a odpovedá na
otázku „o čom sa hovorí“. Nás zaujíma iná otázka: **čo sa práve dá spraviť, čo
sa vlani nedalo** — teda posun v schopnostiach modelov, v tom, ako sa AI
pokročilo používa, a v tom, ako sa mení marketing a vyhľadávanie.

Zdroje sú overené naživo 2026-08-17 (HTTP 200, nie z výsledkov vyhľadávania):

    arXiv cs.AI / cs.CL       výskum, primárny zdroj
    HuggingFace daily papers  čo z výskumu si komunita naozaj všimla
    HuggingFace models        ktoré modely rastú
    OpenAI news               oznámenia priamo od výrobcu
    Google Research           to isté z druhej strany
    AWS ML blog               referenčné nasadenia, nie sľuby
    Microsoft 365 blog        prostredie, v ktorom naši zákazníci pracujú
    Simon Willison            čo niekto naozaj skúsil a čo nevyšlo
    OpenRouter                ceny a dĺžka kontextu — čo je ekonomicky možné
    MCP register              čím sa dá AI napojiť na firemné dáta
    Google Search Central     ako sa mení vyhľadávanie
    Search Engine Land · Ahrefs · Moz   marketing a AI vo vyhľadávaní
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
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from urllib.parse import quote
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



# --- zdravie zdroja --------------------------------------------------------
#
# Najdôležitejší nález 2026-08-17: `0 položiek` nie je stav zdroja, je to
# zlúčenie siedmich rôznych stavov. Cloudový beh mal 7 z 9 zberačov "nemých"
# a vyzeralo to ako pokojný deň — pritom mu prostredie blokovalo egress.
# Systém, ktorý nerozlíši "nič nové" od "nedosiahol som", sa učí z fikcie.

STAVY_ZDROJA = (
    "USPECH",          # odpoveď prišla a niečo v nej bolo
    "PRAZDNY",         # odpoveď prišla a bola legitímne prázdna
    "TIMEOUT",
    "SIET",            # DNS, odmietnuté spojenie, TLS
    "ZAMIETNUTY",      # 401/403 — egress policy alebo autentifikácia
    "LIMIT",           # 429
    "CHYBA_SERVERA",   # 5xx
    "PARSER",          # odpoveď prišla, ale nedala sa prečítať
    "NEZNAMA",
)

_ZDRAVIE: list[dict] = []


def _zaznam(zdroj: str, stav: str, *, url: str, pocet: int = 0,
            trvanie: float = 0.0, detail: str = "") -> None:
    _ZDRAVIE.append({"zdroj": zdroj, "stav": stav, "url": url, "pocet": pocet,
                     "trvanie": round(trvanie, 2), "detail": detail[:200]})


def _stav_z_vynimky(chyba: Exception) -> tuple[str, str]:
    """Zaradí výnimku. Nezaradené patrí do NEZNAMA — nie do PRAZDNY."""
    if isinstance(chyba, requests.Timeout):
        return "TIMEOUT", str(chyba)[:200]
    if isinstance(chyba, (requests.ConnectionError, requests.TooManyRedirects)):
        return "SIET", str(chyba)[:200]
    if isinstance(chyba, ET.ParseError):
        return "PARSER", str(chyba)[:200]
    return "NEZNAMA", f"{type(chyba).__name__}: {chyba}"[:200]


def _stav_z_kodu(kod: int) -> str:
    if kod == 200:
        return "USPECH"
    if kod in (401, 403):
        return "ZAMIETNUTY"
    if kod == 429:
        return "LIMIT"
    if kod >= 500:
        return "CHYBA_SERVERA"
    return "NEZNAMA"


def _json(zdroj: str, url: str, params: Optional[dict] = None):
    """Ako http_get, ale povie PREČO nič neprišlo. Nikdy nevyhodí výnimku."""
    zac = time.monotonic()
    try:
        r = requests.get(url, params=params, headers=DEFAULT_HEADERS,
                         timeout=DEFAULT_TIMEOUT)
    except Exception as chyba:
        stav, detail = _stav_z_vynimky(chyba)
        _zaznam(zdroj, stav, url=url, trvanie=time.monotonic() - zac, detail=detail)
        return None
    stav = _stav_z_kodu(r.status_code)
    if stav != "USPECH":
        _zaznam(zdroj, stav, url=url, trvanie=time.monotonic() - zac,
                detail=f"HTTP {r.status_code}")
        return None
    try:
        data = r.json()
    except ValueError as chyba:
        _zaznam(zdroj, "PARSER", url=url, trvanie=time.monotonic() - zac,
                detail=str(chyba)[:200])
        return None
    pocet = len(data) if isinstance(data, (list, dict)) else 0
    _zaznam(zdroj, "USPECH" if pocet else "PRAZDNY", url=url, pocet=pocet,
            trvanie=time.monotonic() - zac)
    return data


# --- pomocné ---------------------------------------------------------------

def _rss(url: str, limit: int, zdroj: str = "rss") -> list[dict]:
    """Prečíta RSS/Atom. Nikdy nevyhodí výnimku, ale vždy povie, čo sa stalo."""
    zac = time.monotonic()
    try:
        r = requests.get(url, headers=DEFAULT_HEADERS, timeout=DEFAULT_TIMEOUT)
    except Exception as chyba:
        stav, detail = _stav_z_vynimky(chyba)
        _zaznam(zdroj, stav, url=url, trvanie=time.monotonic() - zac, detail=detail)
        return []
    stav = _stav_z_kodu(r.status_code)
    if stav != "USPECH":
        _zaznam(zdroj, stav, url=url, trvanie=time.monotonic() - zac,
                detail=f"HTTP {r.status_code}")
        return []
    try:
        korene = ET.fromstring(r.content)
    except ET.ParseError as chyba:
        _zaznam(zdroj, "PARSER", url=url, trvanie=time.monotonic() - zac,
                detail=str(chyba)[:200])
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
    _zaznam(zdroj, "USPECH" if polozky else "PRAZDNY", url=url,
            pocet=len(polozky), trvanie=time.monotonic() - zac)
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
            limit, "arxiv",
        )
        for p in polozky:
            von.append(_polozka("arxiv", "praca", p["nazov"], p["url"], 0.0, p))
    return von


def fetch_hf_papers(limit: int = 30) -> list[dict]:
    """Denné práce na HuggingFace — filter, ktorý už spravila komunita."""
    data = _json("hf_papers", "https://huggingface.co/api/daily_papers",
                 {"limit": limit})
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
    data = _json("hf_models", "https://huggingface.co/api/models",
                 {"sort": "trendingScore", "limit": limit})
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
        for p in _rss(url, limit, meno):
            von.append(_polozka(meno, "oznamenie", p["nazov"], p["url"], 0.0, p))
    return von


def fetch_praktici(limit: int = 25) -> list[dict]:
    """Ľudia, ktorí AI pokročilo POUŽÍVAJÚ, nie o nej píšu tlačové správy.

    Simon Willison je tu preto, že dôsledne píše, čo naozaj skúsil a čo z toho
    nevyšlo — to je presne ten druh poznatku, ktorý sa nedá vyčítať z oznámenia
    výrobcu. Ak jeho feed raz stíchne, tento zdroj sa nahrádza, nie dopĺňa.
    """
    von = []
    for p in _rss("https://simonwillison.net/atom/everything/", limit, "willison"):
        von.append(_polozka("willison", "prax", p["nazov"], p["url"], 0.0, p))
    return von


def fetch_schopnosti(limit: int = 60) -> list[dict]:
    """Čo sa dá kúpiť a za koľko — naprieč všetkými výrobcami z jedného miesta.

    OpenRouter drží ceny a dĺžku kontextu stoviek modelov. Posun v cene za token
    alebo v dĺžke kontextu mení, čo je vôbec ekonomicky možné postaviť — a to je
    poznatok o schopnostiach, nie marketing.
    """
    data = _json("openrouter", "https://openrouter.ai/api/v1/models")
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


def fetch_konektory(limit: int = 8) -> list[dict]:
    """Oficiálny register MCP serverov — čím sa dá AI napojiť na firemné dáta.

    Priamo pod našou pozíciou: overiteľnosť potrebuje prístup k tomu, čo sa
    overuje. Rast registra je merateľný signál, čo je už napojiteľné bez práce.

    `updated_since` tu nie je kozmetika. Bez neho register radí podľa `name`,
    takže `?limit=30` vracia abecedný začiatok — overené 2026-08-17: 30 z 30
    položiek začínalo na „a“ a prvé tri boli ten istý server v troch verziách.
    Nemerali sme trh, merali sme abecedu, a to isté by sme merali každý deň.

    Register nemá pojem „nové“, má len okno — takže okno JE definícia novosti.
    Deň preto, že za 24 h ide o stovky záznamov; širšie okno je firehose.
    Hlavným výstupom je preto ČÍSLO (koľko pribudlo za deň), nie zoznam mien.
    """
    od = (date.today() - timedelta(days=1)).isoformat() + "T00:00:00Z"
    videne: dict[str, dict] = {}
    kurzor, strany = None, 0
    while strany < 12:                       # strop, aby beh nemohol utiecť
        params = {"limit": 100, "updated_since": od, "version": "latest"}
        if kurzor:
            params["cursor"] = kurzor
        data = _json("mcp_registry",
                     "https://registry.modelcontextprotocol.io/v0/servers", params)
        if not isinstance(data, dict):
            break
        davka = data.get("servers") or []
        for r in davka:
            s = r.get("server") or r
            if not s.get("name"):
                continue
            # Časová pečiatka je v `_meta`, nie v `server`. Bez nej by vzorka
            # znova išla abecedne — poradie z API je podľa mena, nie podľa veku.
            meta = ((r.get("_meta") or {})
                    .get("io.modelcontextprotocol.registry/official") or {})
            s = {**s, "_kedy": meta.get("updatedAt") or meta.get("publishedAt") or ""}
            videne[s["name"]] = s        # posledná verzia mena vyhráva
        kurzor = (data.get("metadata") or {}).get("nextCursor")
        strany += 1
        if not kurzor or not davka:
            break

    if not videne:
        return []

    von = [_polozka(
        "mcp_registry", "konektor",
        # Čas odberu patrí do textu. Bez neho vyzerajú dve merania z toho istého
        # dňa ako rozpor — 2026-08-18 som na tom základe zahodil obe ako
        # nedôveryhodné, hoci číslo len rástlo (913, 918, 920).
        f"MCP register: {len(videne)} serverov pridaných alebo zmenených za 24 h "
        f"(odber {datetime.now().strftime('%Y-%m-%d %H:%M')})",
        f"https://registry.modelcontextprotocol.io/v0/servers?updated_since={od}",
        float(len(videne)), {"pocet": len(videne), "okno": "24h"},
    )]
    najnovsie = sorted(videne.items(), key=lambda kv: kv[1].get("_kedy") or "",
                       reverse=True)
    for meno, s in najnovsie[:limit]:
        von.append(_polozka(
            "mcp_registry", "konektor",
            f"{meno} — {(s.get('description') or '')[:180]}",
            "https://registry.modelcontextprotocol.io/v0/servers"
            f"?search={quote(meno)}",
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
        for p in _rss(url, limit, meno):
            von.append(_polozka(meno, "marketing", p["nazov"], p["url"], 0.0, p))
    return von


def fetch_github_agenti(limit: int = 25) -> list[dict]:
    """Nové repozitáre okolo agentov — čo sa reálne stavia, nie o čom sa píše."""
    data = _json("github", "https://api.github.com/search/repositories", {
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


def _kluc(text: str) -> str:
    """Totožnosť položky. Jedno miesto, aby sa dedup v behu a medzi behmi
    nikdy nerozišli — dva takmer rovnaké kľúče sú horšie než žiadny."""
    return re.sub(r"\W+", "", (text or "").lower())[:120]


def _relevantne(polozky: list[dict]) -> list[dict]:
    """Filter + odstránenie duplikátov. Obyčajný kód, žiadny model."""
    videne: set[str] = set()
    von: list[dict] = []
    for p in polozky:
        text = p["term"]
        if p["source"] not in BEZ_FILTRA and not RELEVANTNE.search(text):
            continue
        kluc = _kluc(text)
        if kluc in videne:
            continue
        videne.add(kluc)
        von.append(p)
    return von


def run(run_id: Optional[int] = None, conn=None) -> int:
    """Nasníma špičku do `signals_raw`. Vracia počet uložených položiek.

    `conn` je pre NODE_MODE: keď beh vedie `core.beh.Beh`, transakciu vlastní
    uzol a toto spojenie má `commit()` potlačený. Bez toho by si funkcia
    commitla sama uprostred uzla a atomicitu by rozbila. Volaná bez `conn`
    (DIRECT_MODE, teda z ruky) sa správa ako predtým.
    """
    vlastne_spojenie = conn is None
    conn = conn if conn is not None else get_connection()
    try:
        if run_id is None:
            cur = conn.execute(
                "INSERT INTO runs (started_at, stage, status) "
                "VALUES (?, 'frontier', 'running')", (now_iso(),))
            run_id = int(cur.lastrowid)

        _ZDRAVIE.clear()
        surove: list[dict] = []
        neme: list[str] = []
        for zdroj in ZDROJE:
            try:
                davka = zdroj()
            except Exception as chyba:      # jeden mŕtvy zdroj nesmie zvaliť beh
                print(f"[frontier_agent] {zdroj.__name__} zlyhal: {chyba}")
                neme.append(zdroj.__name__)
                continue
            if not davka:
                neme.append(zdroj.__name__)
            surove.extend(davka)

        polozky = _relevantne(surove)

        # Dedup MEDZI behmi. `_relevantne` odstráni duplikáty vnútri jedného
        # behu, ale RSS aj register vracajú tie isté položky celé dni, takže
        # každý ďalší beh im pridelí nové id a fronta ich podá znova ako nové.
        # Kľúč je rovnaký ako pri dedupe v behu — dva rôzne by sa rozišli.
        uz_videne = {
            _kluc(t) for (t,) in conn.execute(
                "SELECT term FROM signals_raw WHERE source LIKE 'frontier:%'")
        }
        pred = len(polozky)
        polozky = [p for p in polozky if _kluc(p["term"]) not in uz_videne]
        if pred != len(polozky):
            print(f"[frontier_agent] už videné v predošlých behoch: "
                  f"{pred - len(polozky)} položiek")

        # Zdroje, ktoré si po dostatočnej vzorke miesto nezaslúžili, sa
        # preskočia. Nikto ich nemusí mazať z kódu — rozhodlo o nich meranie
        # vlastnej výťažnosti, nie názor.
        try:
            from core import evolution as ev
            ev.priprav(conn)
            zrusene = ev.zrusene_zdroje(conn)
        except Exception:
            zrusene = set()
        if zrusene:
            pred = len(polozky)
            polozky = [p for p in polozky if p["source"] not in zrusene]
            print(f"[frontier_agent] preskočené zrušené zdroje "
                  f"({', '.join(sorted(zrusene))}): {pred - len(polozky)} položiek")

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

        # Mlčiaci zdroj vyzerá presne ako zdroj, ktorý nič nové nenašiel — a to
        # je nebezpečné, lebo nedostupnosť alebo zmena API sa tak tvári ako
        # úspech. Cloudový beh 2026-08-17 mal 7 z 9 zberačov nemých (blokovaný
        # egress) a bez tohto riadku by to hlásil ako hotový beh.
        # Zdravie sa zapisuje vždy, aj pri úspechu — inak sa nedá povedať,
        # či zdroj mlčí prvý raz alebo desiaty. „Nula položiek“ bez stavu je
        # nerozlíšiteľná od nedostupnosti; presne tak sme si 2026-08-17
        # pomýlili blokovaný egress s pokojným dňom.
        conn.executemany(
            "INSERT INTO zdroj_zdravie (run_id, zdroj, stav, url, pocet, trvanie, detail, kedy) "
            "VALUES (?,?,?,?,?,?,?,?)",
            [(run_id, z["zdroj"], z["stav"], z["url"], z["pocet"], z["trvanie"],
              z["detail"], teraz) for z in _ZDRAVIE])
        conn.commit()

        zle = [z for z in _ZDRAVIE if z["stav"] not in ("USPECH", "PRAZDNY")]
        if zle:
            print(f"[frontier_agent] ZDROJE V PORUCHE ({len(zle)}):")
            for z in zle:
                print(f"    {z['zdroj']}: {z['stav']} — {z['detail']}")
        prazdne = [z["zdroj"] for z in _ZDRAVIE if z["stav"] == "PRAZDNY"]
        if prazdne:
            print(f"[frontier_agent] legitímne prázdne: {', '.join(prazdne)}")
        return len(polozky)
    finally:
        if vlastne_spojenie:
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
        from core import evolution as ev
        ev.priprav(conn)          # fronta sa pýta na `vyklad`, ktorý nemusí ešte existovať
        riadky = [dict(r) for r in conn.execute(
            "SELECT s.id, s.term, s.url, s.source, s.metric_value FROM signals_raw s "
            "WHERE s.source LIKE 'frontier:%' "
            "AND NOT EXISTS (SELECT 1 FROM vyklad v WHERE v.signal_id = s.id) "
            "ORDER BY s.id DESC")]

        # Vylúč aj to, čo už bolo vyložené POD INÝM ID. Dedup pri zbere bráni
        # novým vloženiam, ale položky uložené pred jeho zavedením tu zostali
        # a fronta ich podávala na úsudok znova — teda tá istá práca druhýkrát.
        vylozene = {
            _kluc(t) for (t,) in conn.execute(
                "SELECT s.term FROM signals_raw s "
                "JOIN vyklad v ON v.signal_id = s.id")
        }
        riadky = [r for r in riadky if _kluc(r["term"]) not in vylozene]
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
