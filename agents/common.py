"""Shared HTTP + logging helpers for all agents.

Every agent in this system only calls public, documented, no-auth-required
APIs (Hacker News/Algolia, Wikimedia, npm registry, Stack Exchange, GitHub
REST) strictly within their published rate limits and terms of use. No
scraping of pages that forbid it, no bypassing of auth walls, no synthetic
traffic.
"""
import html
import re
import time
import warnings
from datetime import datetime, timezone
from typing import Any, Optional

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

import requests

USER_AGENT = "biznis-market-research-agent/0.1 (contact: jozefrusnak4@gmail.com)"
DEFAULT_TIMEOUT = 15
DEFAULT_HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def canonical_url(base: str, path: str) -> str:
    """Absolute canonical URL for a site-relative path, directory form.

    `/blog/`, never `/blog/index.html`. Four separate call sites - the
    sitemap, the RSS feed, the blog/tools/news canonical tags and the
    IndexNow submission - each built this string by hand and drifted apart:
    /sk/ declared `/sk/` as its canonical while the sitemap listed
    `/sk/index.html`, handing Google two URLs for one page and telling it
    the one in the sitemap was the wrong one. Everything that needs an
    absolute URL for a page goes through here now.
    """
    path = path.lstrip("/")
    if path.endswith("index.html"):
        path = path[: -len("index.html")]
    return f"{base.rstrip('/')}/{path}"


# Shared visual design system for every generated page (landing_page_agent.py's
# non-calculator pages + index, blog_agent.py's blog pages, and
# content_agent.py's calculator tool) so the whole site reads as one
# product, not a pile of separately-styled documents. Rewritten after
# direct feedback that the design looked "extremely bland and
# unprofessional," then "ultra-modern," then (2026-07-28) "monotonous and
# dry": sticky glass header, decorative gradient orbs + a faint dot grid,
# gradient-hairline cards, gradient-underlined headings, a stats strip,
# and blog styles - all CSS-only, no external assets or fonts (keeps
# pages self-contained and avoids third-party font requests entirely).
SITE_CSS = """
  :root {
    color-scheme: light dark;
    --bg: #ffffff;
    --bg-alt: #fafaff;
    --surface: #f6f7fc;
    --border: #e4e7ef;
    --text: #14161f;
    --text-muted: #5b6072;
    --brand: #4f46e5;
    --brand2: #7c3aed;
    --brand3: #db2777;
    --brand-hover: #4338ca;
    --brand-contrast: #ffffff;
    --orb-a: rgba(124, 58, 237, 0.26);
    --orb-b: rgba(79, 70, 229, 0.22);
    --orb-c: rgba(219, 39, 119, 0.14);
    --dot: rgba(20, 22, 31, 0.06);
    --header-bg: rgba(255, 255, 255, 0.62);
    /* Glassmorphism tokens. A translucent surface is only readable if the
       text on it stays high-contrast, so these stay well above 50% opaque
       - the effect comes from the blur and the light edge, not from making
       the panel see-through enough to hurt legibility. */
    --ghost-fill: rgba(20, 22, 31, 0.16);
    --ghost-stroke: rgba(20, 22, 31, 0.42);
    --glass: rgba(255, 255, 255, 0.58);
    --glass-strong: rgba(255, 255, 255, 0.72);
    --glass-border: rgba(255, 255, 255, 0.75);
    --glass-blur: blur(20px) saturate(140%);
    --shadow: 0 1px 2px rgba(20, 22, 31, 0.04), 0 8px 24px rgba(20, 22, 31, 0.07);
    --shadow-lg: 0 4px 10px rgba(79, 70, 229, 0.12), 0 16px 40px rgba(20, 22, 31, 0.10);
    --radius: 16px;
    --gradient: linear-gradient(135deg, var(--brand), var(--brand2));
    --gradient-warm: linear-gradient(135deg, var(--brand2), var(--brand3));
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0a0b12;
      --bg-alt: #0d0e17;
      --surface: #151723;
      --border: #262a3a;
      --text: #f1f2f9;
      --text-muted: #9a9fb5;
      --brand: #818cf8;
      --brand2: #a78bfa;
      --brand3: #f472b6;
      --brand-hover: #a5b0fb;
      --brand-contrast: #0a0b12;
      --orb-a: rgba(124, 58, 237, 0.42);
      --orb-b: rgba(79, 70, 229, 0.34);
      --orb-c: rgba(219, 39, 119, 0.20);
      --dot: rgba(241, 242, 249, 0.05);
      --header-bg: rgba(10, 11, 18, 0.58);
      --ghost-fill: rgba(241, 242, 249, 0.14);
      --ghost-stroke: rgba(241, 242, 249, 0.40);
      --glass: rgba(28, 31, 48, 0.55);
      --glass-strong: rgba(28, 31, 48, 0.72);
      --glass-border: rgba(255, 255, 255, 0.10);
      --glass-blur: blur(20px) saturate(130%);
      --shadow: 0 1px 2px rgba(0, 0, 0, 0.35), 0 8px 24px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 4px 14px rgba(129, 140, 248, 0.18), 0 20px 48px rgba(0, 0, 0, 0.45);
    }
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    margin: 0; background: var(--bg); color: var(--text); line-height: 1.65;
    -webkit-font-smoothing: antialiased;
    background-image:
      radial-gradient(55rem 30rem at 12% -8%, var(--orb-a), transparent 60%),
      radial-gradient(45rem 26rem at 105% 2%, var(--orb-b), transparent 55%),
      radial-gradient(40rem 30rem at 70% 100%, var(--orb-c), transparent 60%),
      radial-gradient(circle at 1px 1px, var(--dot) 1px, transparent 1.5px);
    background-size: auto, auto, auto, 26px 26px;
    background-repeat: no-repeat, no-repeat, no-repeat, repeat;
    /* Fixed so the colour behind the glass shifts as you scroll - that
       movement is what makes the panels read as translucent rather than
       just lightly tinted. */
    background-attachment: fixed, fixed, fixed, fixed;
  }
  ::selection { background: var(--brand2); color: #fff; }
  .site-header {
    position: sticky; top: 0; z-index: 50;
    background: var(--header-bg);
    -webkit-backdrop-filter: var(--glass-blur); backdrop-filter: var(--glass-blur);
    border-bottom: 1px solid var(--glass-border);
  }
  .site-header-inner {
    display: flex; align-items: center; justify-content: space-between;
    max-width: 1080px; margin: 0 auto; padding: 0.85rem 1.25rem;
  }
  a.brand {
    font-weight: 800; font-size: 1.25rem; color: var(--text); text-decoration: none;
    letter-spacing: -0.03em;
  }
  /* ".studiO" is treated as etched glass: the fill is almost gone and a
     thin light stroke carries the letterforms, so it reads as pressed
     into the surface rather than printed on it. The stroke is what keeps
     it legible - a low-opacity fill on its own just looks like faded
     text. */
  a.brand span {
    background: none;
    color: transparent;
    -webkit-text-fill-color: var(--ghost-fill);
    -webkit-text-stroke: 0.7px var(--ghost-stroke);
    transition: -webkit-text-fill-color 0.25s ease, -webkit-text-stroke-color 0.25s ease;
  }
  a.brand:hover span {
    -webkit-text-fill-color: var(--ghost-stroke);
  }
  /* The terminal capital O is the logotype's one deliberate quirk - kept
     slightly heavier and tighter so it reads as a mark rather than a
     typo, and never inherits <b>'s default browser weight. */
  a.brand span b {
    font-weight: 800; letter-spacing: -0.04em;
  }
  /* Firefox has no -webkit-text-stroke, so the glass letters would vanish
     to a near-invisible fill. Give it a readable translucent fill instead. */
  @supports not (-webkit-text-stroke: 1px black) {
    a.brand span { -webkit-text-fill-color: initial; color: var(--ghost-stroke); }
  }
  .site-header nav { display: flex; gap: 1.4rem; align-items: center; }
  .site-header nav a {
    color: var(--text-muted); text-decoration: none; font-size: 0.9rem; font-weight: 600;
    transition: color 0.15s ease;
  }
  .site-header nav a:hover { color: var(--brand); }
  .site-header nav a.nav-cta {
    background: var(--gradient); color: #fff !important; padding: 0.5rem 1.1rem; border-radius: 999px;
    font-weight: 700; box-shadow: var(--shadow);
  }
  main { max-width: 720px; margin: 0 auto; padding: 3rem 1.25rem 4rem; }
  /* Dve urovne rozlozenia, nie jedna. Landing stranka ma sirku 1080 pre
     komponenty (karty, mriezky, tabulky, obrazky), ale suvisly text sa v nej
     drzi citatelnej miery ~720. Text sa NECENTRUJE - vsetko zdiela tu istu
     lavu os, inak sa stranka rozpadne na dve zarovnania. Overene 2026-08-16:
     centrovany textovy stlpec v sirokom plasti pusobil ako chaos. */
  main.wide { max-width: 1080px; }
  /* PAS (band): sekcia so suvislym textom v sirokom plasti. Nadpis vlavo,
     text vpravo - sirka je vyuzita a nevznika mrtva tretina, ktora vzniknuty
     pri obycajnom obmedzeni miery textu. Pod 900px sa pas zlozi pod seba.
     Vzniklo 2026-08-16: majitel spravne namietol, ze text zarovnany vlavo
     v sirokom kontajneri necha vpravo prazdno. */
  .band { display: grid; gap: 0.6rem 2.75rem; margin-top: 2.6rem; }
  .band > .band-head > h2 { margin-top: 0; }
  .band > .band-body > :first-child { margin-top: 0; }
  .band > .band-body > p, .band > .band-body > ul, .band > .band-body > ol {
    max-width: 68ch;
  }
  @media (min-width: 900px) {
    main.wide .band { grid-template-columns: minmax(200px, 300px) 1fr; }
    main.wide .band > .band-head { position: sticky; top: 5.5rem; align-self: start; }
    /* Cennik nie je text na citanie, ale tabulka na porovnavanie. V uzkom
       stlpci (696 px z 1080) sa stlpec s cenou zmrstil na 74 px. Tento pas
       ide na jeden stlpec, takze tabulka dostane celu sirku pasu. */
    main.wide .band.band-full { grid-template-columns: 1fr; }
    main.wide .band.band-full > .band-head { position: static; }
  }
  /* Cena sa nikdy nezalamuje - "2 400 EUR" na dva riadky vyzera ako dve ceny. */
  table th.cena, table td.cena { white-space: nowrap; width: 1%; text-align: right; }
  h1 {
    font-size: clamp(2.1rem, 5vw, 2.7rem); font-weight: 800; letter-spacing: -0.035em;
    margin: 0 0 0.5rem; line-height: 1.12; text-wrap: balance;
  }
  /* h2/h3 nemali line-height, takze dedili 1.65 z <body> - riadkovanie pre
     odsek, nie pre nadpis. Viacriadkovy nadpis v karte sa tym roztiahol a
     lamal sa nevyvazene ("Vase data / zostavaju u / vas" na tri riadky).
     Zistene meranim 2026-08-16, nie odhadom. */
  h2 {
    font-size: 1.3rem; font-weight: 750; margin-top: 2.4rem; letter-spacing: -0.015em;
    line-height: 1.22; text-wrap: balance;
  }
  main > h2::after, .card > h2:first-child::after {
    content: ""; display: block; width: 44px; height: 3px; border-radius: 3px;
    background: var(--gradient); margin-top: 0.45rem;
  }
  h3, h4 { font-size: 1.05rem; font-weight: 700; line-height: 1.25; text-wrap: balance; }
  .subtitle { color: var(--text-muted); margin: 0 0 1.75rem; font-size: 1.08rem; text-wrap: pretty; }
  .eyebrow {
    display: inline-flex; align-items: center; gap: 0.5rem;
    font-size: 0.74rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--brand); border: 1px solid var(--glass-border); border-radius: 999px;
    padding: 0.35rem 0.9rem; margin-bottom: 1.1rem; background: var(--glass);
    -webkit-backdrop-filter: var(--glass-blur); backdrop-filter: var(--glass-blur);
  }
  .eyebrow::before {
    content: ""; width: 8px; height: 8px; border-radius: 50%;
    background: var(--gradient); box-shadow: 0 0 8px var(--brand);
  }
  .card {
    background: var(--glass); border: 1px solid var(--glass-border);
    -webkit-backdrop-filter: var(--glass-blur); backdrop-filter: var(--glass-blur);
    border-radius: var(--radius);
    padding: 1.6rem 1.85rem; margin: 1.5rem 0; box-shadow: var(--shadow);
    position: relative; overflow: hidden;
  }
  .card::before {
    content: ""; position: absolute; inset: 0 0 auto 0; height: 3px;
    background: var(--gradient); opacity: 0; transition: opacity 0.2s ease;
  }
  .card:hover::before { opacity: 1; }
  a.button, button.button {
    display: inline-block; background: var(--gradient); color: var(--brand-contrast) !important;
    padding: 0.85rem 1.75rem; border-radius: 12px; text-decoration: none; font-weight: 700;
    font-size: 1rem; box-shadow: var(--shadow-lg); border: none;
    position: relative; overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  a.button::after, button.button::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(105deg, transparent 35%, rgba(255,255,255,0.28) 50%, transparent 65%);
    transform: translateX(-120%); transition: transform 0.5s ease;
  }
  a.button:hover, button.button:hover { transform: translateY(-2px) scale(1.015); }
  a.button:hover::after, button.button:hover::after { transform: translateX(120%); }
  a.button.secondary, button.button.secondary {
    background: var(--surface); color: var(--text) !important; border: 1px solid var(--border);
    box-shadow: none;
  }
  a.button.secondary:hover, button.button.secondary:hover { border-color: var(--brand); }
  table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.92rem; }
  th, td { border: 1px solid var(--border); padding: 0.65rem 0.75rem; text-align: left; }
  th { background: var(--bg-alt); font-weight: 700; }
  blockquote {
    background: var(--bg-alt); border-left: 3px solid transparent;
    border-image: var(--gradient) 1; margin: 0.9rem 0;
    padding: 0.7rem 1.15rem;
  }
  ul { padding-left: 1.3rem; }
  li { margin-bottom: 0.55rem; }
  li::marker { color: var(--brand); }
  a { color: var(--brand); }
  a:hover { color: var(--brand-hover); }
  .badge {
    display: inline-block; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.05em;
    text-transform: uppercase; color: #fff; padding: 0.3rem 0.7rem; border-radius: 999px;
    margin-bottom: 0.85rem; box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  }
  .section-title {
    display: flex; align-items: center; gap: 0.7rem;
    font-size: 0.82rem; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text-muted); margin: 3.2rem 0 0.25rem;
  }
  .section-title::before {
    content: ""; width: 26px; height: 3px; border-radius: 3px; background: var(--gradient);
  }
  .section-title::after { display: none; }
  .stats-strip {
    display: flex; flex-wrap: wrap; gap: 1rem; margin: 2rem 0 0.5rem;
  }
  .stat {
    flex: 1 1 150px; background: var(--glass); border: 1px solid var(--glass-border);
    -webkit-backdrop-filter: var(--glass-blur); backdrop-filter: var(--glass-blur);
    border-radius: var(--radius); padding: 1.1rem 1.3rem; box-shadow: var(--shadow);
  }
  .stat b {
    display: block; font-size: 1.55rem; font-weight: 800; letter-spacing: -0.02em;
    background: var(--gradient); -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
   line-height: 1.15;
  }
  .stat span { font-size: 0.8rem; color: var(--text-muted); font-weight: 600; }
  .product-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1.15rem; margin-top: 1.25rem;
  }
  /* One shared definition for every clickable card - product, service and
     blog post. They previously each had their own hover treatment (a
     corner gradient blob, a permanent top bar, and nothing at all
     respectively), which read as three unrelated components on the same
     page. Same surface, same lift, same accent bar on hover. */
  .product-card, .service-card, .post-card {
    display: block; background: var(--glass); border: 1px solid var(--glass-border);
    -webkit-backdrop-filter: var(--glass-blur); backdrop-filter: var(--glass-blur);
    border-radius: var(--radius); padding: 1.5rem 1.6rem; text-decoration: none;
    color: var(--text); box-shadow: var(--shadow); position: relative; overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
  }
  .product-card::before, .service-card::before, .post-card::before {
    content: ""; position: absolute; inset: 0 0 auto 0; height: 3px; z-index: 1;
    background: var(--gradient); opacity: 0; transition: opacity 0.2s ease;
  }
  .product-card:hover, .service-card:hover, .post-card:hover {
    transform: translateY(-3px); border-color: var(--brand); box-shadow: var(--shadow-lg);
    background: var(--glass-strong);
  }
  .product-card:hover::before, .service-card:hover::before, .post-card:hover::before {
    opacity: 1;
  }
  .product-card h3, .service-card h3, .post-card h3 {
    margin: 0.55rem 0 0.4rem; font-size: 1.08rem;
  }
  .product-card p, .service-card p, .post-card p {
    margin: 0; color: var(--text-muted); font-size: 0.9rem;
  }
  .service-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.15rem; margin-top: 1.25rem;
  }
  .card-art {
    display: block; width: 100%; height: 130px; border-radius: 12px;
    margin: -0.35rem 0 1rem;
    /* object-fit is not optional here: cards are a fluid grid, so a fixed
       height with width:100% stretches a photo to whatever ratio the
       column happens to be. `cover` crops instead of distorting. */
    object-fit: cover; object-position: center;
    background: var(--bg-alt);
  }
  .post-card .card-art { height: 110px; }
  /* Used full-width at the top of an article or tool page, the 130px card
     height becomes a ~5:1 letterbox strip. Give the page-level banner a
     sensible height so `cover` crops gently instead of severely. */
  article.post > .card-art, main > .card-art { height: 260px; margin-bottom: 1.5rem; }
  @media (max-width: 640px) {
    article.post > .card-art, main > .card-art { height: 180px; }
  }
  /* The generated SVG fallback is a gradient, so distorting it is fine and
     stretching avoids letterboxing - but object-fit would apply to it too,
     hence the explicit override. */
  svg.card-art { object-fit: fill; }
  .news-list { display: grid; gap: 0.6rem; margin-top: 1.1rem; }
  .news-item {
    display: flex; gap: 0.9rem; align-items: baseline;
    background: var(--glass); border: 1px solid var(--glass-border);
    -webkit-backdrop-filter: var(--glass-blur); backdrop-filter: var(--glass-blur);
    border-radius: 12px; padding: 0.85rem 1.1rem;
    transition: border-color 0.15s ease, transform 0.15s ease, background 0.15s ease;
  }
  .news-item:hover {
    border-color: var(--brand); transform: translateX(3px); background: var(--glass-strong);
  }
  .news-item a { text-decoration: none; font-weight: 650; color: var(--text); }
  .news-item a:hover { color: var(--brand); }
  .news-src {
    flex: none; font-size: 0.68rem; font-weight: 800; letter-spacing: 0.06em;
    text-transform: uppercase; color: var(--brand); white-space: nowrap;
  }
  .news-date { font-size: 0.75rem; color: var(--text-muted); white-space: nowrap; }
  .topic-tabs { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1.4rem 0 0.4rem; }
  .topic-tab {
    font-size: 0.78rem; font-weight: 700; text-decoration: none; color: var(--text-muted);
    border: 1px solid var(--glass-border); border-radius: 999px; padding: 0.35rem 0.85rem;
    background: var(--glass);
    -webkit-backdrop-filter: var(--glass-blur); backdrop-filter: var(--glass-blur);
  }
  .topic-tab:hover { border-color: var(--brand); color: var(--brand); }
  .widget {
    background: var(--glass); border: 1px solid var(--glass-border);
    -webkit-backdrop-filter: var(--glass-blur); backdrop-filter: var(--glass-blur);
    border-radius: var(--radius);
    padding: 1.5rem 1.75rem; margin: 1.5rem 0; box-shadow: var(--shadow);
  }
  .widget label {
    display: block; font-weight: 600; font-size: 0.88rem; color: var(--text-muted);
    margin: 0.9rem 0 0.3rem;
  }
  .widget input, .widget select {
    width: 100%; padding: 0.65rem 0.8rem; font-size: 1rem; font-family: inherit;
    color: var(--text); background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px;
  }
  .widget-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.9rem; }
  .widget-out {
    margin-top: 1.4rem; padding: 1.2rem 1.4rem; border-radius: 12px;
    background: var(--gradient); color: #fff;
  }
  .widget-out b { display: block; font-size: 1.9rem; font-weight: 800; letter-spacing: -0.02em; }
  .widget-out span { font-size: 0.85rem; opacity: 0.92; }
  .widget-note { font-size: 0.82rem; color: var(--text-muted); margin-top: 0.9rem; }
  /* Bez grid-template-columns je to jeden stlpec. V sirokom plasti z toho
     vznikne lista cez celu sirku a stranka vyzera poloprazdna. */
  .post-list {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
    gap: 1.15rem; margin-top: 1.25rem;
  }
  .post-meta {
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
    color: var(--brand);
  }
  article.post { max-width: 680px; }
  article.post h1 { margin-top: 0.6rem; }
  article.post .post-meta { margin-bottom: 0.2rem; }
  .contact-form label {
    display: block; font-weight: 600; font-size: 0.9rem; color: var(--text-muted);
    margin: 1rem 0 0.35rem;
  }
  .contact-form input, .contact-form textarea {
    width: 100%; padding: 0.7rem 0.85rem; font-size: 1rem; font-family: inherit;
    color: var(--text); background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px;
  }
  .contact-form textarea { min-height: 120px; resize: vertical; }
  .contact-form button {
    margin-top: 1.25rem; border: none; cursor: pointer; font-family: inherit;
  }
  .form-note { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.75rem; }
  .hero-banner {
    position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 2.2rem;
    box-shadow: var(--shadow-lg); border: 1px solid var(--border);
  }
  .hero-banner img { display: block; width: 100%; height: 280px; object-fit: cover; }
  .hero-banner::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(105deg, rgba(79,70,229,0.72), rgba(124,58,237,0.45) 55%, rgba(219,39,119,0.30));
  }
  .hero-banner .hero-copy {
    position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center;
    padding: 2.5rem 3rem; z-index: 2; color: #fff;
  }
  .hero-banner .hero-copy h1 {
    color: #fff; -webkit-text-fill-color: #fff; background: none; margin-bottom: 0.6rem;
    text-shadow: 0 2px 20px rgba(0,0,0,0.25);
  }
  .hero-banner .hero-copy p {
    margin: 0; max-width: 640px; font-size: 1.05rem; color: rgba(255,255,255,0.94);
    text-shadow: 0 1px 12px rgba(0,0,0,0.3);
  }
  .hero-banner .eyebrow {
    background: rgba(255,255,255,0.16); border-color: rgba(255,255,255,0.32); color: #fff;
    -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
  }
  .hero-banner .eyebrow::before { background: #fff; box-shadow: 0 0 8px rgba(255,255,255,0.9); }
  @media (max-width: 640px) {
    .hero-banner img { height: 340px; }
    .hero-banner .hero-copy { padding: 1.6rem 1.5rem; }
  }
  .hero { max-width: 720px; padding-top: 1rem; }
  .hero .subtitle { font-size: 1.15rem; }
  .hero h1 {
    background: linear-gradient(120deg, var(--text) 0%, var(--brand) 55%, var(--brand2) 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; display: inline-block;
  }
  footer {
    max-width: 1080px; margin: 3rem auto 0; padding: 1.5rem 1.25rem 2.5rem;
    font-size: 0.82rem; color: var(--text-muted); border-top: 1px solid var(--border);
    display: flex; flex-wrap: wrap; gap: 0.4rem 1.4rem; align-items: center;
  }
  footer a.brand {
    font-size: 0.95rem; font-weight: 800; letter-spacing: -0.03em;
    color: var(--text); text-decoration: none; margin-right: 0.4rem;
  }
  /* At footer size a 0.7px stroke is thinner than the rendered stem and
     the letters break up, so the footer mark leans on fill instead. */
  footer a.brand span {
    -webkit-text-fill-color: var(--ghost-stroke); -webkit-text-stroke-width: 0;
    color: var(--ghost-stroke);
  }
  footer a { color: var(--text-muted); }
  footer a:hover { color: var(--brand); }
  @media (max-width: 480px) {
    /* Found via a real mobile check: the nav link text and the "Hire us"
       pill button were each wrapping onto two lines and colliding with
       the logo on a 375px-wide screen - narrow the spacing instead of
       letting flexbox wrap mid-word. */
    .site-header-inner { padding: 0.7rem 1rem; flex-wrap: wrap; gap: 0.5rem; }
    .site-header nav { gap: 0.15rem 0.5rem; flex-wrap: wrap; }
    /* Merane 2026-08-16 na 375px: odkazy v navigacii mali vysku 21px a CTA
       33px. Odporucanie pre dotykovy terc je ~44px, takze sa do nich cez
       palec trafi len s namahou. Vyska sa robi zvislym paddingom, nie
       vacsim pismom - to by sa zas zalamovalo. */
    .site-header nav a {
      font-size: 0.78rem; white-space: nowrap;
      padding: 0.62rem 0.35rem; display: inline-flex; align-items: center;
    }
    .site-header nav a.nav-cta { padding: 0.62rem 0.95rem; }
    .widget-row { grid-template-columns: 1fr; }
    .news-item { flex-wrap: wrap; gap: 0.35rem 0.8rem; }
    .news-item .news-date { margin-left: 0 !important; }
  }
  /* Safari/Firefox versions without backdrop-filter would render these as
     washed-out translucent boxes with no blur, so fall back to the solid
     surface colour there instead. */
  @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
    .card, .product-card, .service-card, .post-card, .stat, .widget,
    .news-item, .topic-tab, .eyebrow, .site-header {
      background: var(--surface); border-color: var(--border);
    }
  }
  @media (prefers-reduced-motion: reduce) {
    a.button::after, button.button::after { display: none; }
    .card, .product-card, .post-card, .service-card, a.button, button.button { transition: none; }
  }
"""

# One accent color per product format, used for the small badge shown on
# product cards/pages - purely a scannability aid, not a claim about
# quality or popularity.
FORMAT_BADGE_COLORS = {
    "calculator": "#2563eb",
    "checklist": "#059669",
    "template": "#d97706",
    "swipe_file": "#7c3aed",
    "prompt_pack": "#0891b2",
    "ebook": "#db2777",
    "sop": "#4b5563",
    "service": "#0d9488",
}

# Public contact address for the "service" format's Get in touch CTA
# (custom website/chatbot development - not an automated digital
# download). Using the site owner's real email, so it's the one that
# should change first if a dedicated business address is set up later.
CONTACT_EMAIL = "jozefrusnak4@gmail.com"

# A small monogram favicon (inline SVG data URI - no external request).
FAVICON_DATA_URI = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect width='64' height='64' rx='14' fill='%234f46e5'/%3E"
    "%3Ctext x='32' y='44' font-family='Arial,sans-serif' font-size='34' "
    "font-weight='800' fill='white' text-anchor='middle'%3EB%3C/text%3E%3C/svg%3E"
)


def card_art(slug: str, alt: str, seed_text: str = "", depth: int = 1) -> str:
    """Card/hero artwork: a real photograph when we have one for this slug,
    otherwise the generated gradient as a graceful fallback.

    Photos come from agents/image_agent.py (CC0/Public-Domain only) and are
    served from our own site/assets/img/, so a card never depends on a
    third-party host staying up. `depth` is how many directories deep the
    referencing page sits, so the relative path resolves from products/,
    blog/, tools/ and news/ as well as the root.
    """
    from pathlib import Path as _Path
    img_path = _Path(__file__).resolve().parent.parent / "site" / "assets" / "img" / f"{slug}.jpg"
    if img_path.exists():
        prefix = "../" * depth
        return (f'<img class="card-art" src="{prefix}assets/img/{slug}.jpg" '
                f'alt="{html.escape(alt)}" loading="lazy" decoding="async" '
                f'width="800" height="450">')
    return illustration_svg(seed_text or alt)


def illustration_svg(seed_text: str, height: int = 150) -> str:
    """A deterministic, on-brand abstract illustration for a card header.

    Generated as inline SVG rather than sourced images on purpose: no
    external requests, no licensing/attribution risk, nothing to break if
    a CDN disappears, and every card gets a distinct-but-consistent look
    derived from its own title. The seed only shifts hue/positions within
    the brand's violet-indigo range, so the set still reads as one family.
    """
    h = 0
    for ch in seed_text:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    # Spread across cyan -> blue -> indigo -> violet -> magenta. A narrower
    # band (tried 232-292 first) made every card read as the same pink and
    # drifted off the indigo brand anchor; this keeps real variety while
    # every stop still sits in the brand's cool-to-violet family.
    hue = 196 + (h % 118)
    hue2 = (hue + 26 + (h >> 8) % 34)
    cx1, cy1 = 12 + (h >> 3) % 40, 20 + (h >> 5) % 40
    cx2, cy2 = 60 + (h >> 7) % 35, 45 + (h >> 11) % 45
    r1, r2 = 30 + (h >> 13) % 18, 22 + (h >> 17) % 16
    rot = (h >> 19) % 90
    uid = f"g{h % 100000}"
    return (
        f'<svg class="card-art" viewBox="0 0 400 {height}" preserveAspectRatio="none" '
        f'aria-hidden="true" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<linearGradient id="{uid}a" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0%" stop-color="hsl({hue},85%,62%)"/>'
        f'<stop offset="100%" stop-color="hsl({hue2},80%,55%)"/></linearGradient>'
        f'<radialGradient id="{uid}b"><stop offset="0%" stop-color="hsl({hue2},90%,72%)" '
        f'stop-opacity="0.85"/><stop offset="100%" stop-color="hsl({hue2},90%,72%)" '
        f'stop-opacity="0"/></radialGradient>'
        f'</defs>'
        f'<rect width="400" height="{height}" fill="url(#{uid}a)"/>'
        f'<circle cx="{cx1 * 4}" cy="{cy1}" r="{r1 * 1.6:.0f}" fill="url(#{uid}b)"/>'
        f'<circle cx="{cx2 * 4}" cy="{cy2}" r="{r2 * 1.4:.0f}" fill="#fff" opacity="0.10"/>'
        f'<g transform="rotate({rot} 200 {height // 2})" opacity="0.16" stroke="#fff" '
        f'stroke-width="1.5" fill="none">'
        f'<circle cx="200" cy="{height // 2}" r="34"/>'
        f'<circle cx="200" cy="{height // 2}" r="58"/>'
        f'<circle cx="200" cy="{height // 2}" r="82"/></g>'
        f'<path d="M0 {height} L130 {height - 46} L260 {height - 14} L400 {height - 62} '
        f'L400 {height} Z" fill="#fff" opacity="0.09"/>'
        f"</svg>"
    )


def format_badge_html(fmt: str) -> str:
    color = FORMAT_BADGE_COLORS.get(fmt, "#4b5563")
    label = fmt.replace("_", " ")
    return f'<span class="badge" style="background:{color}">{label}</span>'


# The wordmark is a *visual* asset, so it lives in exactly one place and is
# only ever used where it gets rendered with its styling (header, footer,
# banner image). Plain-text contexts - <title>, meta descriptions, RSS -
# deliberately keep "Biznis": unstyled, the terminal capital reads as a
# typo rather than a design choice, and people mistype it.
BRAND_HTML = "Biznis<span>.studi<b>O</b></span>"


def site_header_html(active_is_index: bool = False, lang: str = "en") -> str:
    """Shared sticky header.

    Slovak pages get a Slovak nav pointing at Slovak destinations. Before
    this, /sk/ inherited the English nav, so every single link threw a
    Slovak visitor into English content - the pages advertise services in
    Slovak and then every click leaves the language.

    The language link sits in the nav in BOTH directions. It used to be
    one-way: /sk/ had "English" in the nav, but the English side only
    offered "Slovensky" down in the footer, so a Slovak speaker landing on
    an English page had to scroll the whole page to find their language.
    Note this is a language *entry point*, not a page-level translation
    switcher - the two sides are different content for different audiences
    (English: the product catalogue; Slovak: the services offering), so
    there is no per-page counterpart to link to and claiming otherwise
    would send people to a page that does not exist.
    """
    if lang == "sk":
        # Slovak pages all live in /sk/, so these are siblings.
        return f"""<header class="site-header">
<div class="site-header-inner">
<a class="brand" href="index.html">{BRAND_HTML}</a>
<nav>
<a href="index.html">Slu&zcaron;by</a>
<a href="index.html#cennik">Cenn&iacute;k</a>
<a href="efaktura-2027-test.html">E-fakt&uacute;ra 2027</a>
<a href="../index.html" lang="en" hreflang="en">English</a>
<a class="nav-cta" href="index.html#kontakt">Nez&aacute;v&auml;zn&yacute; dopyt</a>
</nav>
</div>
</header>"""

    prefix = "" if active_is_index else "../"
    home_href = f"{prefix}index.html"
    # "Hire us" viedlo na #services - zoznam sluzieb bez formulara, takze
    # navstevnik, ktory chcel napisat, nemal kam kliknut. Vedie na formular.
    services_href = "#kontakt" if active_is_index else "../index.html#kontakt"
    return f"""<header class="site-header">
<div class="site-header-inner">
<a class="brand" href="{home_href}">{BRAND_HTML}</a>
<nav>
<a href="{prefix}work.html">Work</a>
<a href="{home_href}">Products</a>
<a href="{prefix}tools/index.html">Tools</a>
<a href="{prefix}news/index.html">Signals</a>
<a href="{prefix}blog/index.html">Blog</a>
<a href="{prefix}sk/index.html" lang="sk" hreflang="sk">Slovensky</a>
<a class="nav-cta" href="{services_href}">Hire us</a>
</nav>
</div>
</header>"""


MARKETING_BLURBS = {
    "calculator": "Get an instant answer for {term} - no signup, no spreadsheet, works right in your browser.",
    "checklist": "A clear, repeatable checklist for {term} - know exactly what to do next, in the right order.",
    "template": "Skip the blank page. A ready-to-use {term} template with the right structure already in place.",
    "prompt_pack": "Ready-to-paste AI prompts for {term} - works with ChatGPT, Claude, or Gemini.",
    "swipe_file": "Ready-to-send scripts for {term} - copy, adjust the details, send.",
    "service": "{term}, scoped and quoted for your actual project - get in touch to start.",
}
# Pat sluzieb zdielalo jednu vetu, v ktorej sa menil len nazov: "X, scoped and
# quoted for your actual project - get in touch to start." Na stranke, ktora
# predava dizajn, to citatelovi povie jedine to, ze text pisala sablona.
# Kazda sluzba ma vlastnu vetu o tom, CO ZAKAZNIK DOSTANE - ziadne cisla,
# ziadne sluby, ktore nevieme dodrzat.
BLURB_PODLA_SLUZBY = {
    "custom-website-design-development":
        "A finished, deployed website - not a design file someone else still has to build.",
    "custom-chatbot-development":
        "A chatbot that answers from your own documents and prices, on your own site.",
    "tailored-digital-product":
        "A calculator, template or tool shaped around one job your customers keep asking about.",
    "design-branding-visual-identity":
        "A logo with the rules and stylesheet to use it - so everything made later still looks like you.",
    "automation-integrations":
        "The weekly job you do by hand, running by itself - with the source code handed to you.",
}

# To iste platilo pre zvysok katalogu: 14 publikovanych produktovych stranok
# dostalo jednu zo siedmich sablon z MARKETING_BLURBS, v ktorej sa menil len
# nazov temy - styri "template" stranky mali doslova rovnaku vetu az na jedno
# slovo, styri "swipe_file" tiez. Kazda veta nizsie je napisana z OBSAHU suboru
# (products.file_path), nie z nazvu: co v tom subore naozaj je a na aku situaciu
# to je. Ziadne cisla, ziadne referencie, ziadna urgencia.
# Sablony v MARKETING_BLURBS zostavaju ako fallback pre produkt, ktory pipeline
# vyrobi zajtra a nikto mu este vetu nenapisal.
BLURB_PODLA_PRODUKTU = {
    "free-online-calculator":
        "Enter an amount and a percentage and see the percentage itself, the amount with the markup added, and the amount with the discount taken off.",
    "checklist-pdf-notion":
        "A checklist that walks a project from a written definition of done, through setup and a first working version, to feedback and a final quality check.",
    "eu-digital-seller-compliance-checklist":
        "The questions an EU-based seller of ebooks or templates meets in week one: selling status, VAT on digital goods, identity checks, and getting paid.",
    "the-practical-guide-to-xlsx":
        "What an .xlsx file actually is underneath, when to reach for a spreadsheet app, a CSV export or a code library, and the mistakes that waste the most time.",
    "the-practical-guide-to-automation":
        "How to choose between a built-in feature, a no-code platform and a short script for a repetitive task, and how to describe the task well enough to automate it.",
    "gpt-sol-ai-prompt-pack":
        "Prompts for explaining, comparing, troubleshooting, critiquing and planning around Gpt Sol - fill in the bracketed details and paste them into your assistant.",
    "spreadsheet-pack":
        "A log sheet with the columns already named - date, category, description, amount, status and notes - plus an example row showing how to fill it in.",
    "invoice-pack":
        "An invoice sheet with numbering, issue and due dates, line items with quantity and unit price, and the subtotal, tax and total rows already laid out.",
    "change-request-log-template":
        "A log for every extra request on a project: what was asked, who asked for it, the estimated hours and cost, and whether it was approved and when.",
    "retainer-renewal-tracker-template":
        "A tracker for contract dates: when each retainer ends, when to open the renewal conversation, the rate you are on now, and what to send next.",
    "freelance-scope-creep-defense-kit":
        "Wording for the moments a project quietly grows, from the first small extra ask to a full renegotiation, paired with a log for every addition.",
    "resume-gap-job-title-explainer-scripts":
        "Honest wording for two awkward resume questions: a gap in your work history, and a job title that did not describe what you actually did.",
    "client-retainer-renewal-kit":
        "Wording for every renewal moment - the early check-in, a client going quiet, raising your rate, ending a retainer - plus a tracker for contract dates.",
    "late-payment-recovery-kit":
        "The escalation ladder for an unpaid invoice, from the day after the due date to a formal final notice, with a tracker for where each invoice stands.",
}

MARKETING_BLURB_EBOOK_FREE = "A fast, practical guide to {term} - no fluff, just what actually works."
MARKETING_BLURB_EBOOK_PAID = "A focused guide to {term} you can read in about 15 minutes and put to use today."
MARKETING_BLURB_FALLBACK = "A practical {format} for {term}."

# When the keyword IS the format word itself (e.g. term="checklist" for a
# checklist product), using it verbatim reads as an accidental repeat
# ("A clear, repeatable checklist for Checklist"). Swap in a generic
# subject that still fits the sentence template.
GENERIC_SUBJECT_BY_FORMAT = {
    "calculator": "your numbers",
    "checklist": "your next project",
    "template": "your work",
    "prompt_pack": "everyday tasks",
    "swipe_file": "that conversation",
    "ebook": "getting started",
    "sop": "getting started",
}

# term.title() mangles acronyms ("xlsx" -> "Xlsx" instead of "XLSX"). Small,
# explicit override list rather than general acronym detection - applied
# per-word so it also fixes multi-word terms like "eu digital seller
# compliance" -> "EU Digital..." not just single-word terms.
ACRONYM_OVERRIDES = {
    "xlsx": "XLSX", "csv": "CSV", "pdf": "PDF", "seo": "SEO", "ai": "AI",
    "api": "API", "sql": "SQL", "css": "CSS", "html": "HTML", "url": "URL",
    "json": "JSON", "eu": "EU", "vat": "VAT", "kyc": "KYC", "gdpr": "GDPR",
}


def display_term(term: str) -> str:
    return " ".join(ACRONYM_OVERRIDES.get(w.lower(), w.title()) for w in term.split())


def marketing_blurb(term: str, format_: str, monetized: bool = False,
                    slug: str = "") -> str:
    """Visitor-facing copy for a product page - deliberately separate from
    `product_ideas.rationale`, which is an internal audit trail ("why the
    agent picked this") and reads like an engineering log, not marketing
    (e.g. "Keyword implies users want to compute something quickly
    online."). Real copy, but still 100% honest - no fabricated numbers,
    testimonials, or urgency that isn't true."""
    if slug and slug in BLURB_PODLA_SLUZBY:
        return BLURB_PODLA_SLUZBY[slug]
    if slug and slug in BLURB_PODLA_PRODUKTU:
        return BLURB_PODLA_PRODUKTU[slug]
    if term.strip().lower() == format_:
        subject = GENERIC_SUBJECT_BY_FORMAT.get(format_, term)
    else:
        subject = display_term(term)

    if format_ in ("ebook", "sop"):
        template = MARKETING_BLURB_EBOOK_PAID if monetized else MARKETING_BLURB_EBOOK_FREE
    else:
        template = MARKETING_BLURBS.get(format_, MARKETING_BLURB_FALLBACK)
    return template.format(term=subject, format=format_.replace("_", " "))


_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")
# [text](https://...) or [text](../relative/path.html). Applied after
# html.escape(), so brackets/parens are still literal characters. Only
# http(s) and site-relative .html targets - no javascript: etc.
# Interne odkazy sa pisu aj adresarovo ("/sk/#kontakt") a ako holy anchor
# ("#kontakt"). Do 2026-08-16 vzor pripustal len http(s) alebo .html, takze
# CTA na konci prave publikovaneho clanku zostalo ako holy text "[Napiste
# nam](/sk/#kontakt)". Odkaz, ktory sa ticho nevyrenderuje, je horsi nez
# ziadny - vyzera ako chyba autora.
_LINK_RE = re.compile(
    r"\[([^\]]+)\]\("
    r"(https?://[^)\s]+"                       # absolutne
    r"|[a-zA-Z0-9_./#-]+\.html(?:#[\w-]*)?"    # subor .html
    r"|/[a-zA-Z0-9_/-]*/(?:#[\w-]*)?"          # adresar, napr. /sk/ alebo /sk/#kontakt
    r"|#[\w-]+"                                # holy anchor
    r")\)")


def _link_sub(match: "re.Match[str]") -> str:
    text, href = match.group(1), match.group(2)
    # External links open in a new tab; internal (relative) links don't.
    extra = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
    return f'<a href="{href}"{extra}>{text}</a>'


# Rucne pisane <title> pre stranky, ktorych nadpis je spravne dlhy, ale do
# vysledkov vyhladavania sa nezmesti. h1 zostava nedotknuty. Automaticke
# skracovanie tu nestaci - vyrabalo useknute vety ("...if you freelance or run a").
SEO_TITULKY = {
    "blog/seven-places-worth-reading.html":
        "7 places worth reading if you freelance",
    "blog/telling-clients-rate-increase.html":
        "How to tell a client you are raising your rates",
    # Domovska je jedna z dvoch stranok, ktore Google vobec indexuje, takze
    # tento titulok je prakticky cela nasa pritomnost vo vysledkoch. Do
    # 2026-08-19 to bol zoznam sluzieb; teraz vedie rozdiel, ktory mame ako
    # jedini, a sluzby zostavaju za nim.
    "index.html":
        "AI your team can check - websites, design and automation | Biznis",
    "sk/preco-zamestnanci-prestanu-pouzivat-ai.html":
        "Pre\u010do zamestnanci prestan\u00fa pou\u017e\u00edva\u0165 AI vo firme",
    "tools/machinery-regulation-digital-instructions.html":
        "EU Machinery Regulation: digital instructions test",
}


def seo_titul(text: str, limit: int = 62) -> str:
    """Skrati <title> na dlzku, ktoru vyhladavac zobrazi celu.

    Nadpis clanku smie byt dlhy - h1 sa nekrati. Ale <title> nad ~62 znakov
    Google oreze uprostred slova a vysledok vyzera nedbalo. Reze sa na
    prirodzenom mieste: zatvorka, dvojbodka alebo koniec vety pred limitom,
    az potom na hranici slova. Merane 2026-08-17: 5 stranok bolo nad limitom.
    """
    text = text.strip()
    if len(text) <= limit:
        return text
    for znak in (" (", ". ", ": ", " - ", " | "):
        i = text.rfind(znak, 0, limit + 1)
        if i > limit * 0.45:
            return text[:i].rstrip(" -|:.")
    i = text.rfind(" ", 0, limit)
    return (text[:i] if i > 0 else text[:limit]).rstrip(" -|:.")


def _typografia(escaped_text: str) -> str:
    """Typograficke upravy, ktore rozhoduju o tom, ci text vyzera profesionalne.

    Zistene auditom 2026-08-16 naprieč vsetkymi clankami: slovenske mali 30-42
    jednopismenovych predloziek, ktore mohli zostat na konci riadku (v slovencine
    chyba), anglicke mali 8-28 rovnych uvodzoviek namiesto typografickych, a
    vsetky pouzivali spojovnik " - " tam, kde patri pomlcka.

    Bezi na UZ ESCAPOVANOM texte, takze &amp;, &lt; a &quot; su uz entity - preto
    sa uvodzovky hladaju ako &quot;, nie ako ".
    """
    # 1) Nezalomitelna medzera za jednopismenovym slovom (a, i, k, o, s, u, v, z).
    #    V slovencine nesmie takato predlozka alebo spojka zostat na konci riadku.
    #    Opakuje sa, kym sa text meni: "a k tomu" ma dostat nezalomitelnu
    #    medzeru pri OBOCH slovach, ale po prvej nahrade uz "k" nema pred sebou
    #    medzeru, ale entitu - jeden prechod by ho preskocil.
    for _ in range(4):
        novy = re.sub(r"(^|[\s(\u201e]|&nbsp;)([aikosuvzAIKOSUVZ])\s+",
                      lambda m: f"{m.group(1)}{m.group(2)}&nbsp;", escaped_text)
        if novy == escaped_text:
            break
        escaped_text = novy

    # 2) Spojovnik pouzity ako pomlcka -> skutocna pomlcka.
    escaped_text = escaped_text.replace(" - ", " \u2014 ")

    # 3) Rovne uvodzovky -> typograficke. Otvaracia je ta, pred ktorou je
    #    zaciatok, medzera alebo zatvorka; ostatne su zatvaracie.
    out, otvorena = [], True
    i = 0
    while i < len(escaped_text):
        if escaped_text.startswith("&quot;", i):
            pred = out[-1] if out else " "
            if otvorena or pred in " ([\u2014\n":
                out.append("\u201c"); otvorena = False
            else:
                out.append("\u201d"); otvorena = True
            i += 6
        else:
            out.append(escaped_text[i]); i += 1
    return "".join(out)


def _inline_emphasis(escaped_text: str) -> str:
    """Convert **bold**, *italic* and [text](url) links to real markup,
    applied *after* html.escape() so the punctuation (not HTML-special) is
    untouched by escaping but the tags we insert are real markup, not
    escaped text. Found this gap by shipping content that used *italic*
    emphasis and seeing literal asterisks on the live page; link support
    added for the blog, which curates external resources."""
    escaped_text = _typografia(escaped_text)
    escaped_text = _LINK_RE.sub(_link_sub, escaped_text)
    escaped_text = _BOLD_RE.sub(r"<strong>\1</strong>", escaped_text)
    escaped_text = _ITALIC_RE.sub(r"<em>\1</em>", escaped_text)
    return escaped_text


def markdown_lite_to_html(md_text: str) -> str:
    """Minimal renderer for the specific Markdown subset content_agent.py
    produces: #/## headings, "- [ ] " checklist items, "- " list items,
    "> " blockquotes, "---" rules, plain paragraphs, and inline **bold**/
    *italic* emphasis. Shared by landing_page_agent.py (web pages) and
    scripts/export_pdf.py (PDF downloads) so both never drift into two
    different parsers.

    Every block type here is hand-wrapped across multiple physical lines
    in the source (for readable line lengths), so this has to merge wrapped
    lines back into one logical block before emitting a tag - line-by-line
    classification alone would (and once did) break a wrapped list item
    into a <li> plus a stray sibling <p>, and a wrapped blockquote into
    several separate <blockquote> tags instead of one."""
    lines = md_text.splitlines()
    out: list[str] = []
    in_list = False
    buffer_type: Optional[str] = None  # 'p' | 'li' | 'li_checked' | 'blockquote'
    buffer_text: list[str] = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def flush():
        nonlocal buffer_type, buffer_text
        if buffer_text:
            text = _inline_emphasis(html.escape(" ".join(buffer_text).strip()))
            if buffer_type == "li":
                out.append(f"<li>{text}</li>")
            elif buffer_type == "li_checked":
                out.append(f"<li>☐ {text}</li>")
            elif buffer_type == "blockquote":
                close_list()
                out.append(f"<blockquote>{text}</blockquote>")
            else:  # 'p'
                close_list()
                out.append(f"<p>{text}</p>")
        buffer_text = []
        buffer_type = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if stripped == "---":
            flush()
            close_list()
            continue
        if stripped.startswith("### "):
            flush()
            close_list()
            out.append(f"<h3>{_typografia(html.escape(stripped[4:]))}</h3>")
        elif stripped.startswith("## "):
            flush()
            close_list()
            out.append(f"<h2>{_typografia(html.escape(stripped[3:]))}</h2>")
        elif stripped.startswith("# "):
            flush()
            close_list()
            out.append(f"<h1>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("- [ ] "):
            flush()
            if not in_list:
                out.append("<ul>")
                in_list = True
            buffer_type, buffer_text = "li_checked", [stripped[6:]]
        elif stripped.startswith("- "):
            flush()
            if not in_list:
                out.append("<ul>")
                in_list = True
            buffer_type, buffer_text = "li", [stripped[2:]]
        elif stripped.startswith("> "):
            if buffer_type == "blockquote":
                buffer_text.append(stripped[2:])  # same quote, wrapped across lines
            else:
                flush()
                buffer_type, buffer_text = "blockquote", [stripped[2:]]
        else:
            # Continuation of whatever block is open (li/blockquote/p), or
            # the start of a new paragraph if nothing is open.
            if buffer_type is None:
                buffer_type = "p"
            buffer_text.append(stripped)

    flush()
    close_list()
    return "\n".join(out)


def http_get(url: str, params: Optional[dict] = None, retries: int = 2,
             backoff: float = 1.5, headers: Optional[dict] = None) -> Optional[Any]:
    """GET a URL and return parsed JSON, or None on failure (never raises)."""
    hdrs = {**DEFAULT_HEADERS, **(headers or {})}
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=hdrs, timeout=DEFAULT_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 403) or resp.status_code >= 500:
                time.sleep(backoff * (attempt + 1))
                continue
            return None
        except requests.RequestException:
            time.sleep(backoff * (attempt + 1))
    return None
