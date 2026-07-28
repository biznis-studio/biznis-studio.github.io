"""Landing Page Agent.

Turns each `products` row with status='ready' into an actual static HTML
page under `site/`, and registers it in `pages`. Draft-status products
(ebook/sop outlines - see content_agent.py) are skipped: publishing a
skeleton as if it were a finished landing page would misrepresent it.

Per-format rendering:
  - calculator: the generated tool *is* the page - copied as-is into
    site/products/, with a short intro paragraph injected above the tool.
  - checklist / prompt_pack (Markdown): rendered with a small built-in
    Markdown-subset renderer (headings, checklist items, blockquotes,
    paragraphs, hr) into the page body, plus a download link to the raw file.
  - template (CSV): rendered as an HTML preview table, plus a download link.

If `products.monetization_url` is set (e.g. a Gumroad listing - set
manually once the user creates one, this system doesn't create payment
accounts on anyone's behalf), the download link is replaced with a link to
that listing and the file is *not* also copied into site/downloads/ - no
point undermining a paid listing by giving the same file away for free
next to it.
"""
import csv
import html
import io
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import (BRAND_HTML, CONTACT_EMAIL, FAVICON_DATA_URI, SITE_CSS, format_badge_html,
                            card_art, markdown_lite_to_html, marketing_blurb, now_iso,
                            site_header_html, slugify)
from agents.pdf_export import export as export_pdf
from core.db import get_connection, init_db

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
PAGES_DIR = SITE_DIR / "products"
DOWNLOADS_DIR = SITE_DIR / "downloads"

# Set once the user creates a Google Search Console property for this site
# and chooses the HTML-tag verification method - without this, Google may
# not discover/index the site at all for a long time.
GOOGLE_SITE_VERIFICATION = os.environ.get("GOOGLE_SITE_VERIFICATION", "")

# Set once the user creates a free Formspree form and gives us its endpoint
# (https://formspree.io/f/XXXXXXXX) - lets "service" pages use a real
# contact form that forwards to the site owner's email without ever
# putting that email address in the page source. Falls back to a mailto
# CTA (which *does* expose the address) until this is configured.
FORMSPREE_ENDPOINT = os.environ.get("FORMSPREE_ENDPOINT", "")

# Same var seo_agent.py uses. Needed here too because the homepage
# (index.html) is built directly by this module and never passes through
# seo_agent.py's post-hoc inject() (that only processes rows in the
# `pages` table, one per product - the homepage isn't a "product"). Found
# via a crawl-readiness audit: every product page had a canonical link,
# the homepage - the single most important URL on the whole site - had
# none at all.
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "").rstrip("/")

# One site-wide share image (not per-product - there's no real product
# photography, and a generic branded card is honest, unlike a fabricated
# product photo) used for every page's og:image/twitter:image, so links
# shared anywhere (Gumroad, social, forums) show a real preview instead of
# a blank box. Generated once via headless Chrome, committed as a static
# asset - see site/assets/og-image.png.
OG_IMAGE_TAGS = (
    f'<meta property="og:image" content="{SITE_BASE_URL}/assets/og-image.png">\n'
    f'<meta property="og:image:width" content="1200">\n'
    f'<meta property="og:image:height" content="630">\n'
    f'<meta name="twitter:card" content="summary_large_image">\n'
    f'<meta name="twitter:image" content="{SITE_BASE_URL}/assets/og-image.png">\n'
    if SITE_BASE_URL else ""
)

# Human-readable download-button labels - fmt.replace("_", " ") alone would
# still read as internal jargon for some formats ("swipe file" isn't a term
# most visitors recognize; found this after "Download swipe_file" - with
# the underscore visible - shipped to production).
DOWNLOAD_LABEL_BY_FORMAT = {
    "swipe_file": "scripts",
    "prompt_pack": "prompts",
}

def page_shell(title: str, meta_description: str, body_html: str, is_index: bool = False) -> str:
    verification_tag = (
        f'<meta name="google-site-verification" content="{html.escape(GOOGLE_SITE_VERIFICATION)}">\n'
        if GOOGLE_SITE_VERIFICATION else ""
    )
    main_class = ' class="wide"' if is_index else ""
    # The homepage doesn't go through seo_agent.py's per-product inject()
    # step, so it's the only page that needs its canonical/OG tags added
    # right here rather than post-hoc.
    index_seo_tags = ""
    if is_index and SITE_BASE_URL:
        index_seo_tags = (
            f'<link rel="canonical" href="{SITE_BASE_URL}/">\n'
            f'<meta property="og:title" content="{html.escape(title)}">\n'
            f'<meta property="og:description" content="{html.escape(meta_description)}">\n'
            f'<meta property="og:url" content="{SITE_BASE_URL}/">\n'
            f'<meta property="og:type" content="website">\n'
            + OG_IMAGE_TAGS
        )
    # feed.xml has existed since iteration 7 but nothing ever linked to it -
    # crawlers/RSS readers have no way to discover it without this tag.
    # Site-wide (not just index), same SITE_BASE_URL-gating as everything
    # else that asserts a live URL.
    rss_link_tag = (
        f'<link rel="alternate" type="application/rss+xml" title="Biznis - New products, tools and articles" '
        f'href="{SITE_BASE_URL}/feed.xml">\n'
        if SITE_BASE_URL else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(meta_description)}">
<link rel="icon" href="{FAVICON_DATA_URI}">
{verification_tag}{index_seo_tags}{rss_link_tag}<style>{SITE_CSS}</style>
</head>
<body>
{site_header_html(active_is_index=is_index)}
<main{main_class}>
{body_html}
</main>
<footer><a class="brand" href="{'' if is_index else '../'}index.html">{BRAND_HTML}</a>
<span>Built in public from real demand signals.</span>
<a href="{'' if is_index else '../'}index.html">Products</a>
<a href="{'' if is_index else '../'}tools/index.html">Free tools</a>
<a href="{'' if is_index else '../'}news/index.html">Signals</a>
<a href="{'' if is_index else '../'}blog/index.html">Blog</a>
<a href="{'' if is_index else '../'}credits.html">Photo credits</a>
<a href="https://github.com/biznis-studio/biznis-studio.github.io" target="_blank" rel="noopener">GitHub</a></footer>
</body>
</html>
"""


def gate_swipe_file_preview(raw: str) -> str:
    """For a *priced* swipe_file, showing every script in full on the free
    landing page gives away 100% of what's being sold - found this during
    a real sales-readiness review: a visitor never needed to pay, just
    copy the page. Keeps the first script's exact wording as a real proof-
    of-quality sample (a genuine, honest preview - not a fake teaser), and
    the heading + "Use this when..." guidance for every other script
    (real, valuable context that doesn't give away the deliverable), but
    replaces scripts 2+ with a single locked placeholder line each."""
    lines = raw.splitlines()
    out = []
    quote_buf = []
    quote_seen_count = 0

    def flush():
        nonlocal quote_buf, quote_seen_count
        if not quote_buf:
            return
        quote_seen_count += 1
        if quote_seen_count == 1:
            out.extend(quote_buf)  # first script: full, real sample
        else:
            out.append("> 🔒 *Full script included in the paid kit - see it "
                        "instantly after purchase.*")
        quote_buf = []

    for line in lines:
        if line.startswith(">"):
            quote_buf.append(line)
        else:
            flush()
            out.append(line)
    flush()
    return "\n".join(out)


def gate_ebook_preview(raw: str, free_sections: int = 2) -> str:
    """Same problem as gate_swipe_file_preview, found on the ebook format
    while auditing every monetized product for the same issue: the full
    ~1300-word ebook was readable in its entirety right above the "Get it
    on Gumroad" button, so there was no reason to pay anything - even on a
    pay-what-you-want listing. Keeps the first `free_sections` "## "
    headings in full (a genuine, substantial preview - not a teaser
    paragraph), keeps every later heading visible as a real table of
    contents, but replaces each later section's body with a single locked
    placeholder line."""
    lines = raw.splitlines()
    out = []
    sections_seen = 0
    gating = False

    for line in lines:
        if line.startswith("## "):
            sections_seen += 1
            gating = sections_seen > free_sections
            out.append(line)
            if gating:
                out.append("")
                out.append("🔒 *Full section included after purchase - see it "
                            "instantly on Gumroad.*")
            continue
        if gating:
            continue
        out.append(line)
    return "\n".join(out)


def csv_to_html_table(csv_text: str, max_rows: int = 10) -> str:
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)
    if not rows:
        return "<p><em>Empty template.</em></p>"
    header, *body = rows
    out = ["<table>", "<tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in header) + "</tr>"]
    for row in body[:max_rows]:
        out.append("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def inject_intro_into_calculator(html_text: str, intro_html: str, meta_description: str, fmt: str) -> str:
    """Insert the format badge + intro right after the tool's own <h1> (not
    right after <body> - that would render the subtitle above the title),
    add a meta description + favicon, the shared site header right after
    <body>, and the same footer nav every other page gets."""
    h1_match = re.compile(r"<h1>", re.IGNORECASE).search(html_text)
    if h1_match:
        insert_at = h1_match.start()
        html_text = html_text[:insert_at] + format_badge_html(fmt) + "\n" + html_text[insert_at:]
    h1_close_match = re.compile(r"</h1>", re.IGNORECASE).search(html_text)
    if h1_close_match:
        insert_at = h1_close_match.end()
        html_text = html_text[:insert_at] + "\n" + intro_html + html_text[insert_at:]

    # The calculator ships with its own <style> block, copied from SITE_CSS
    # at the time the product file was generated - and never regenerated
    # since. That silently froze this one page on an old design while every
    # other page moved on (found when a site-wide CSS fix landed everywhere
    # except here). Replace the block from the live SITE_CSS on every build
    # so it cannot drift again.
    html_text = re.sub(r"<style>.*?</style>", lambda _m: f"<style>{SITE_CSS}</style>",
                       html_text, count=1, flags=re.DOTALL)

    head_match = re.compile(r"</head>", re.IGNORECASE).search(html_text)
    if head_match:
        # The calculator is the one page type that doesn't go through
        # page_shell() (the generated tool *is* the page), so anything
        # page_shell adds site-wide has to be repeated here or the
        # calculator silently drifts - the RSS discovery link went missing
        # exactly this way and was caught by scripts/audit_site.py.
        rss_tag = (
            f'<link rel="alternate" type="application/rss+xml" '
            f'title="Biznis - New products, tools and articles" href="{SITE_BASE_URL}/feed.xml">\n'
            if SITE_BASE_URL else ""
        )
        verification = (
            f'<meta name="google-site-verification" '
            f'content="{html.escape(GOOGLE_SITE_VERIFICATION)}">\n'
            if GOOGLE_SITE_VERIFICATION else ""
        )
        meta_tag = (f'<meta name="description" content="{html.escape(meta_description)}">\n'
                    f'<link rel="icon" href="{FAVICON_DATA_URI}">\n'
                    f'{verification}{rss_tag}')
        html_text = html_text[:head_match.start()] + meta_tag + html_text[head_match.start():]

    body_match = re.compile(r"<body>", re.IGNORECASE).search(html_text)
    if body_match:
        insert_at = body_match.end()
        html_text = html_text[:insert_at] + "\n" + site_header_html() + html_text[insert_at:]

    footer = ('<footer>Generated by the Biznis pipeline from real demand signals. '
              '<a href="../index.html">Back to all products</a></footer>\n')
    body_close = re.compile(r"</body>", re.IGNORECASE).search(html_text)
    if body_close:
        html_text = html_text[:body_close.start()] + footer + html_text[body_close.start():]

    return html_text


def contact_form_html() -> str:
    """A real contact form posting straight to Formspree - no email address
    anywhere in this page's source. The honeypot ("_gotcha") is Formspree's
    own spam-trap convention: a field hidden from real visitors via CSS
    that, if filled in, means a bot filled out every field blindly."""
    return f"""<form class="contact-form" action="{html.escape(FORMSPREE_ENDPOINT)}" method="POST">
<label for="name">Name</label>
<input type="text" id="name" name="name" required>
<label for="email">Your email</label>
<input type="email" id="email" name="email" required>
<label for="message">What do you need?</label>
<textarea id="message" name="message" required></textarea>
<input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">
<button type="submit" class="button">Send</button>
<p class="form-note">Goes straight to us - no account or signup needed on your end.</p>
</form>"""


def build_page(product: dict) -> Optional[dict]:
    title = product["title"]
    fmt = product["format"]
    term = product["term"]
    monetization_url = product.get("monetization_url")
    price_usd = product.get("price_usd")
    src_path = ROOT / product["file_path"]
    if not src_path.exists():
        return None

    slug = slugify(title)
    meta_description = marketing_blurb(term, fmt, bool(monetization_url))[:160]
    intro_html = f'<p class="subtitle">{html.escape(meta_description)}</p>'

    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    if fmt == "calculator":
        raw = src_path.read_text()
        page_html = inject_intro_into_calculator(raw, intro_html, meta_description, fmt)
        page_path = PAGES_DIR / f"{slug}.html"
        page_path.write_text(page_html)
    else:
        raw = src_path.read_text()
        if fmt == "template":
            body = csv_to_html_table(raw)
        else:  # checklist, prompt_pack, ebook, sop
            # Every generator's file starts with "# {title}" as its own
            # standalone document title - redundant with the page's own
            # <h1> shown just above this card, so drop that one line here.
            content_lines = raw.splitlines()
            if content_lines and content_lines[0].strip().startswith("# "):
                raw = "\n".join(content_lines[1:])
            if fmt == "swipe_file" and monetization_url:
                raw = gate_swipe_file_preview(raw)
            elif fmt in ("ebook", "sop") and monetization_url:
                raw = gate_ebook_preview(raw)
            body = markdown_lite_to_html(raw)

        if fmt == "service":
            # Not a download - a custom-scoped offering, so the CTA is a
            # contact method instead of a file. Prefer the real contact
            # form (email address never appears in the page source) once
            # Formspree is configured; fall back to mailto (which *does*
            # expose the address) until then.
            cta = contact_form_html() if FORMSPREE_ENDPOINT else (
                f'<a class="button" href="mailto:{CONTACT_EMAIL}">Get in touch</a>')
            trust_note = ""
        elif monetization_url:
            # Paid listing: don't also give the file away for free alongside it.
            price_label = f" - ${price_usd:.0f}" if price_usd else ""
            cta = (f'<a class="button" href="{html.escape(monetization_url)}" '
                   f'target="_blank" rel="noopener">Get it on Gumroad{html.escape(price_label)}</a>\n'
                   '<p class="form-note">Instant digital download - pay once on Gumroad\'s '
                   "secure checkout, use it right away. Personal &amp; business use "
                   "license: use it for your own work or your clients' work. Don't "
                   "resell, redistribute, or republish the files themselves.</p>")
            # Found via a sales-readiness review: paying $29 to a page with
            # zero indication of who made it or why to trust it is a real
            # conversion barrier - honest, not a fake bio/testimonial.
            trust_note = (
                '<div class="card"><h2>Who makes this</h2>'
                "<p>Built by one person, researched against real competitor "
                "pricing and freelancer pain points rather than generated on "
                "the spot - the same process and design system used across "
                'this entire site. See <a href="https://github.com/biznis-studio/biznis-studio.github.io" '
                'target="_blank" rel="noopener">the project repo</a> for exactly '
                "how it's built.</p></div>\n"
            )
        else:
            trust_note = ""
            if fmt in ("ebook", "sop"):
                # A raw .md isn't a great deliverable for a standalone
                # document (and some marketplaces won't even accept it as
                # an upload type) - a proper PDF is the better artifact.
                download_name = src_path.stem + ".pdf"
                export_pdf(src_path, DOWNLOADS_DIR / download_name, title=title)
            else:  # checklist, prompt_pack, template - fine as their native file
                download_name = src_path.name
                shutil.copyfile(src_path, DOWNLOADS_DIR / download_name)
            label = DOWNLOAD_LABEL_BY_FORMAT.get(fmt, fmt.replace("_", " "))
            cta = (f'<a class="button" href="../downloads/{html.escape(download_name)}" '
                   f'download>Download {html.escape(label)}</a>')

        body_html = (f"{format_badge_html(fmt)}\n<h1>{html.escape(title)}</h1>\n{intro_html}\n"
                     f'<div class="card">{body}</div>\n{trust_note}{cta}')
        page_path = PAGES_DIR / f"{slug}.html"
        page_path.write_text(page_shell(title, meta_description, body_html))

    return {
        "url": str(page_path.relative_to(SITE_DIR)),
        "title": title,
        "meta_description": meta_description,
    }


def _product_card(p: dict) -> str:
    # A monetized product sitting undistinguished in a "Free products" grid
    # actively misleads a visitor into expecting a free download - found
    # this during a sales-readiness review. A price badge next to the
    # format badge sets the right expectation before the click, not after.
    price_badge = (
        f'<span class="badge" style="background:#16a34a;margin-left:0.4rem">${p["price_usd"]:.0f}</span>'
        if p.get("monetization_url") and p.get("price_usd") else ""
    )
    return (f'<a class="product-card" href="products/{Path(p["url"]).name}">'
            f'{card_art(Path(p["url"]).stem, p["title"], depth=0)}'
            f'{format_badge_html(p["format"])}{price_badge}'
            f'<h3>{html.escape(p["title"])}</h3>'
            f'<p>{html.escape(p["meta_description"])}</p></a>')


def build_credits_page() -> None:
    """Photo credits. CC0/Public Domain images carry no legal attribution
    requirement, but naming the photographers who released work for free
    costs nothing and is simply the decent thing to do."""
    from agents.image_agent import load_credits
    credits = load_credits()
    if not credits:
        return
    rows = "\n".join(
        f"<tr><td>{html.escape(c.get('title') or '(untitled)')}</td>"
        f"<td>{html.escape(c.get('creator') or 'Unknown')}</td>"
        f"<td>{html.escape((c.get('license') or '').upper())}</td>"
        f"<td>{html.escape(c.get('source') or '')}</td></tr>"
        for c in credits
    )
    body = f"""<h1>Photo credits</h1>
<p class="subtitle">Every photograph on this site comes from
<a href="https://www.pexels.com" target="_blank" rel="noopener">Pexels</a>, or is published
under Creative Commons Zero (CC0) or the Public Domain Mark via Openverse.</p>
<div class="card">
<p>None of these licences requires attribution, and we could legally list nothing here. We
list them anyway: these photographers gave their work away for free, and that deserves a name
against it. Photos are stored on our own server rather than hot-linked, so we are not
spending anyone else's bandwidth either.</p>
<p>Stock photography by <a href="https://www.pexels.com" target="_blank" rel="noopener">Pexels</a>.</p>
</div>
<table>
<tr><th>Image</th><th>Creator</th><th>Licence</th><th>Source</th></tr>
{rows}
</table>"""
    (SITE_DIR / "credits.html").write_text(page_shell(
        "Photo credits - Biznis",
        "Credits for the CC0 and public domain photography used across this site.",
        body, is_index=True))


def build_index(pages: list[dict], stats: Optional[dict] = None) -> None:
    # Local import: blog_agent imports page_shell from this module, so a
    # module-level import here would be a circular dependency.
    from agents.blog_agent import load_posts

    services = [p for p in pages if p["format"] == "service"]
    paid_products = [p for p in pages if p["format"] != "service" and p.get("monetization_url")]
    free_products = [p for p in pages if p["format"] != "service" and not p.get("monetization_url")]

    service_cards = "\n".join(
        f'<a class="service-card" href="products/{Path(p["url"]).name}">'
        f'{card_art(Path(p["url"]).stem, p["title"], depth=0)}'
        f'{format_badge_html(p["format"])}'
        f'<h3>{html.escape(p["title"])}</h3>'
        f'<p>{html.escape(p["meta_description"])}</p></a>'
        for p in services
    )
    paid_cards = "\n".join(_product_card(p) for p in paid_products)
    free_cards = "\n".join(_product_card(p) for p in free_products)
    services_section = (
        f'<h2 id="services" class="section-title">What we build for you</h2>\n'
        f'<div class="service-grid">{service_cards}</div>\n'
        if services else ""
    )
    # Only show a distinct "Get the full system" section once something is
    # actually for sale - an empty paid section would be as misleading in
    # the other direction (implying nothing here costs money at all,
    # before anything was ever monetized).
    paid_section = (
        f'<h2 class="section-title">Ready-made systems</h2>\n'
        f'<div class="product-grid">{paid_cards}</div>\n'
        if paid_products else ""
    )
    # Stats strip: real counts from the DB only - the whole point is that
    # these are honest, verifiable numbers (the repo is public), never
    # marketing-inflated ones.
    stats_html = ""
    if stats:
        stats_html = (
            '<div class="stats-strip">'
            f'<div class="stat"><b>{stats["signals"]:,}</b><span>market signals analyzed</span></div>'
            f'<div class="stat"><b>{stats["keywords"]}</b><span>keywords demand-scored</span></div>'
            f'<div class="stat"><b>{stats["products"]}</b><span>products built &amp; published</span></div>'
            '<div class="stat"><b>100%</b><span>open source, built in public</span></div>'
            "</div>"
        )

    posts = load_posts()[:3]
    blog_section = ""
    if posts:
        post_cards = "\n".join(
            f'<a class="post-card" href="blog/{p["slug"]}.html">'
            f'{card_art(p["slug"], p["title"], depth=0)}'
            f'<span class="post-meta">{p["date"]}</span>'
            f'<h3>{html.escape(p["title"])}</h3>'
            f'<p>{html.escape(p["description"])}</p></a>'
            for p in posts
        )
        blog_section = (
            f'<h2 class="section-title">From the blog</h2>\n'
            f'<div class="post-list">{post_cards}</div>\n'
            f'<p><a href="blog/index.html">All posts &rarr;</a></p>\n'
        )

    hero_img = card_art("hero", "Workspace", depth=0)
    body = f"""<div class="hero-banner">
{hero_img}
<div class="hero-copy">
<span class="eyebrow">Design &middot; Build &middot; Automate</span>
<h1>We design and build the digital side of your business</h1>
<p>Brand identity and design. Websites and chatbots. Custom digital products built to your
brief. And automation for the work you should not be doing by hand. Plus a growing
catalogue of ready-made tools you can use today.</p>
</div>
</div>
{stats_html}
{services_section}
{paid_section}
<h2 class="section-title">Free downloads</h2>
<div class="product-grid">{free_cards}</div>
{blog_section}"""
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "index.html").write_text(page_shell(
        "Biznis - Design, Websites, Custom Digital Products & Automation",
        "Digital studio: brand identity and design, websites and chatbots, digital products built to your brief, and automation. Plus free tools.",
        body,
        is_index=True,
    ))


def run(run_id: Optional[int] = None) -> list[int]:
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    query = """SELECT p.id AS product_id, p.title, p.format, p.file_path,
                      p.monetization_url, p.price_usd, k.term
               FROM products p
               JOIN product_ideas pi ON pi.id = p.idea_id
               JOIN keywords k ON k.id = pi.target_keyword_id
               LEFT JOIN pages pg ON pg.product_id = p.id
               WHERE p.status = 'ready' AND pg.id IS NULL"""
    to_build = cur.execute(query).fetchall()

    ts = now_iso()
    new_page_ids = []
    for row in to_build:
        try:
            result = build_page(dict(row))
        except Exception as exc:  # e.g. Chrome missing for a PDF export - don't take the whole run down
            print(f"[landing_page_agent] failed to build page for product_id={row['product_id']}: {exc}")
            continue
        if not result:
            continue
        cur.execute(
            """INSERT INTO pages (product_id, url, title, meta_description, status, created_at)
               VALUES (?, ?, ?, ?, 'draft', ?)""",
            (row["product_id"], result["url"], result["title"], result["meta_description"], ts),
        )
        new_page_ids.append(cur.lastrowid)
    conn.commit()

    all_pages = cur.execute(
        """SELECT pg.url, pg.title, pg.meta_description, p.format,
                  p.monetization_url, p.price_usd
           FROM pages pg JOIN products p ON p.id = pg.product_id
           ORDER BY pg.id"""
    ).fetchall()
    stats = {
        "signals": cur.execute("SELECT COUNT(*) FROM signals_raw").fetchone()[0],
        "keywords": cur.execute("SELECT COUNT(*) FROM keywords").fetchone()[0],
        "products": cur.execute("SELECT COUNT(*) FROM products WHERE status='ready'").fetchone()[0],
    }
    conn.close()
    build_index([dict(p) for p in all_pages], stats=stats)

    print(f"[landing_page_agent] built {len(new_page_ids)} new pages "
          f"({len(all_pages)} total in site/)")
    return new_page_ids


if __name__ == "__main__":
    run_id_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run(run_id_arg)
