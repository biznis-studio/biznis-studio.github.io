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

def footer_html(is_index: bool, lang: str) -> str:
    """Language-matched footer. A Slovak page must not link out to English
    pages in its own footer - the visitor came for Slovak."""
    if lang == "sk":
        return ('<footer><a class="brand" href="index.html">' + BRAND_HTML + '</a>'
                '<a href="index.html">Slu&zcaron;by</a>'
                '<a href="efaktura-2027-test.html">E-fakt&uacute;ra 2027</a>'
                '<a href="index.html#cennik">Cenn&iacute;k</a>'
                '<a href="../index.html">English</a>'
                '<a href="https://github.com/biznis-studio/biznis-studio.github.io" '
                'target="_blank" rel="noopener">GitHub</a></footer>')
    pre = "" if is_index else "../"
    return (f'<footer><a class="brand" href="{pre}index.html">{BRAND_HTML}</a>'
            f'<span>Built in public from real demand signals.</span>'
            f'<a href="{pre}index.html">Products</a>'
            f'<a href="{pre}tools/index.html">Free tools</a>'
            f'<a href="{pre}news/index.html">Signals</a>'
            f'<a href="{pre}blog/index.html">Blog</a>'
            f'<a href="{pre}sk/index.html">Slovensky</a>'
            f'<a href="{pre}credits.html">Photo credits</a>'
            f'<a href="https://github.com/biznis-studio/biznis-studio.github.io" '
            f'target="_blank" rel="noopener">GitHub</a></footer>')


def page_shell(title: str, meta_description: str, body_html: str, is_index: bool = False,
               lang: str = "en", canonical_path: str = "") -> str:
    """Render a full page.

    `is_index` means "lives at the site root, uses the wide layout" - it is
    NOT a claim to be the homepage. `work.html` and `credits.html` are also
    root-level, and for a long time sharing this flag handed them the
    homepage's canonical URL, which tells Google they are duplicates of /
    and should not be indexed in their own right. `canonical_path` is the
    page's own path below the site root ("" for the homepage itself), and
    is what the canonical/OG URLs are built from.
    """
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
        page_url = f"{SITE_BASE_URL}/{canonical_path}"
        # Only the real homepage is the English side of the language pair.
        # These three lines must mirror build_sk_page()'s block exactly:
        # hreflang is honoured only when BOTH pages point at each other -
        # "if two pages don't both point to each other, the tags will be
        # ignored" (Google, Localized versions of your pages).
        hreflang_tags = (
            f'<link rel="alternate" hreflang="sk" href="{SITE_BASE_URL}/sk/">\n'
            f'<link rel="alternate" hreflang="en" href="{SITE_BASE_URL}/">\n'
            f'<link rel="alternate" hreflang="x-default" href="{SITE_BASE_URL}/">\n'
        ) if not canonical_path else ""
        index_seo_tags = (
            f'<link rel="canonical" href="{page_url}">\n'
            + hreflang_tags
            + f'<meta property="og:title" content="{html.escape(title)}">\n'
            f'<meta property="og:description" content="{html.escape(meta_description)}">\n'
            f'<meta property="og:url" content="{page_url}">\n'
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
{site_header_html(active_is_index=is_index, lang=lang)}
<main{main_class}>
{body_html}
</main>
{footer_html(is_index, lang)}
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


# Form labels per language. Parameterised rather than duplicating the
# whole form for the Slovak page, so the honeypot and endpoint handling
# can never drift between the two.
FORM_LABELS = {
    "en": ("Name", "Your email", "What do you need?", "Send",
           "Goes straight to us - no account or signup needed on your end."),
    "sk": ("Meno", "V&aacute;š e-mail", "Čo potrebujete?", "Odoslať",
           "Chod&iacute; priamo n&aacute;m - nepotrebujete žiadny &uacute;čet ani registr&aacute;ciu."),
}


def contact_form_html(lang: str = "en") -> str:
    """A real contact form posting straight to Formspree - no email address
    anywhere in this page's source. The honeypot ("_gotcha") is Formspree's
    own spam-trap convention: a field hidden from real visitors via CSS
    that, if filled in, means a bot filled out every field blindly."""
    name_l, email_l, msg_l, submit_l, note = FORM_LABELS.get(lang, FORM_LABELS["en"])
    return f"""<form class="contact-form" action="{html.escape(FORMSPREE_ENDPOINT)}" method="POST">
<label for="name">{name_l}</label>
<input type="text" id="name" name="name" required>
<label for="email">{email_l}</label>
<input type="email" id="email" name="email" required>
<label for="message">{msg_l}</label>
<textarea id="message" name="message" required></textarea>
<input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">
<button type="submit" class="button">{submit_l}</button>
<p class="form-note">{note}</p>
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


def build_work_page(stats: dict) -> None:
    """Proof-of-capability page, written for a buyer rather than a builder.

    First version of this page listed page counts, lines of code and
    signal totals - facts that impress the person who wrote them and mean
    nothing to someone deciding whether to hire us. Rewritten so every
    section answers the only question a client actually has: what does
    this mean for my project.
    """
    body = f"""<span class="eyebrow">See it before you buy it</span>
<h1>Work</h1>
<p class="subtitle">The design, the products, the tools and the software that publishes all
of it - every piece of this was built by us. It is live, it works, and you can use any of it
right now. Judge the work directly instead of a page of logos.</p>

<h2>A finished website, not a mockup</h2>
<p>The site you are on is the work sample. Product pages, a blog, interactive tools,
working contact forms, a news section that updates itself, light and dark mode, and it is
built to be fast on a phone first.</p>
<p><strong>What this means for you:</strong> if you hire us for a website, this is the
standard you get - a real site that is live and working, not a design file handed over for
somebody else to build. <a href="index.html">Have a look around it.</a></p>

<h2>Software that runs without anyone touching it</h2>
<p>This site largely maintains itself. Every day it gathers fresh material, publishes it,
rebuilds its own navigation and feeds, and checks its own pages for broken links before
anything goes live. Nobody logs in to make that happen. The
<a href="news/index.html">Signals page</a> is the visible end of it - those headlines
arrived on their own.</p>
<p><strong>What this means for you:</strong> if there is something you or your team do by
hand every week - moving data between systems, rebuilding the same report, checking a
source for changes - this is what replacing it looks like in practice.</p>

<h2>Tools your customers can actually use</h2>
<p>Two free calculators that do real work in the browser: a
<a href="tools/scope-creep-cost-calculator.html">scope creep cost calculator</a> and a
<a href="tools/freelance-rate-calculator.html">freelance rate calculator</a>. No signup,
nothing stored, nothing sent anywhere. Open one and check the arithmetic yourself.</p>
<p><strong>What this means for you:</strong> an interactive tool is one of the few things
that gets shared and linked to on its own. If you want one for your customers - a quote
estimator, a sizing guide, a savings calculator - these are working examples of the
quality.</p>

<h2>Finished deliverables, not samples</h2>
<p>{stats['products']} completed digital products: script kits, templates, checklists, a
guide, an interactive calculator. Each one written as something a person can pick up and
use, not as a demonstration. Most are free and readable in full without giving us an email
address.</p>
<p><strong>What this means for you:</strong> you can judge the writing, the depth and the
level of care before you ever contact us. <a href="index.html">Read any of them.</a></p>

<h2>A visual identity applied consistently</h2>
<p>The logo, colour system, typography and layout rules here were designed for this
project, then applied across every single page - including the ones generated
automatically. Light and dark variants throughout, because roughly half of any audience
sees the dark one.</p>
<p><strong>What this means for you:</strong> we do not just make a logo and leave you to
work out how to use it. You get the rules and a working stylesheet, so everything made
later still looks like you.</p>

<div class="card">
<h2>How we take the risk off you</h2>
<p>A fixed price and a written scope, agreed before any work begins. If the job turns out
harder than we estimated, that is our problem - not a revised invoice.</p>
<p>You own the result outright, source files included, with no ongoing fees and nothing
locking you to us. And you can see the standard of the work above before you commit to
anything at all.</p>
</div>

<div class="stats-strip">
<div class="stat"><b>Fixed</b><span>price agreed in writing before work starts</span></div>
<div class="stat"><b>Yours</b><span>full rights and source files, no ongoing fees</span></div>
<div class="stat"><b>2</b><span>revision rounds included as standard</span></div>
<div class="stat"><b>Live</b><span>delivered working and deployed, not as a file</span></div>
</div>

<p style="margin-top:2rem"><a class="button" href="index.html#services">See what we build</a></p>
<h2 id="kontakt" class="section-title">Tell us what you need</h2>
<p>A short description is enough to start. We reply with what we would do, what it costs, and what we would need from you.</p>"""
    body += contact_form_html() if FORMSPREE_ENDPOINT else ""

    (SITE_DIR / "work.html").write_text(page_shell(
        "Work - Biznis",
        "Everything on this site was designed and built by us, and it is all live. "
        "Try any of it before you talk to us.",
        body, is_index=True, canonical_path="work.html"))


def build_sk_page() -> None:
    """Slovak-language services page.

    Opportunity research finding: Slovak SERPs for the exact services we
    sell ("kolko stoji webstranka", "automatizacia procesov v malej
    firme") are held only by small local agencies - no global authority,
    unlike the English equivalents where incumbents own everything. There
    are also paid ads running on those queries, which means somebody is
    already spending money to acquire these customers, so buyers exist.

    Combined with the fact that these are service enquiries worth
    hundreds to thousands of euros rather than $29 downloads, and that
    the operator is Slovak and can actually service them - same language,
    timezone, jurisdiction and invoicing - this is a far more realistic
    path to first revenue than competing in English.

    Repositioned 2026-08-08 around the operator's own strategic decision:
    the primary offering is now turning a company's EXISTING Microsoft 365
    Copilot into a structured work system for one specific process, rather
    than the previous generic web/design/automation menu.

    Why this framing and not "an AI agent for X": Microsoft ships its own
    Factory Operations Agent and AppSource already carries 8D/CAPA
    solutions, so competing head-on with an agent loses. Positioning
    Copilot as part of our delivery stack rather than as the competitor is
    the only framing found that does not require beating anyone - see
    docs/RESEARCH_LOG.md.

    This is sold as a service, not a product, and that is deliberate
    (B6 in the business gate). Nothing on this page claims a capability
    that would require software we have not built: the deliverable is
    knowledge structuring, workflow design and configuration inside the
    customer's own tenant.

    The existing services stay on the page rather than being deleted -
    they are real revenue paths and the whole Slovak article cluster links
    into them.

    NOT VALIDATED YET: no customer interview has happened. The B10
    protocol in docs/RESEARCH_LOG.md still governs. Prices below were set
    by Claude as a starting point and are the owner's to confirm.
    """
    body = """<div class="hero">
<span class="eyebrow">Firemn&aacute; AI &middot; Microsoft 365 &middot; Copilot</span>
<h1>M&aacute;te Copilot. Pou&zcaron;&iacute;vate ho na p&iacute;sanie mailov.</h1>
<p class="subtitle">Firmy platia za Microsoft 365 Copilot a vyu&zcaron;&iacute;vaj&uacute; zlomok
toho, čo vie. Nie preto, &zcaron;e by bol slab&yacute; - ale preto, &zcaron;e nepozn&aacute;
va&scaron;e postupy, va&scaron;u hist&oacute;riu ani va&scaron;e pravidl&aacute;. Postav&iacute;me nad n&iacute;m
&scaron;trukt&uacute;ru pre jeden konkr&eacute;tny proces, aby prestal byť osobn&yacute;m
asistentom a začal byť pracovn&yacute;m n&aacute;strojom.</p>
</div>

<div class="stats-strip">
<div class="stat"><b>Va&scaron;e d&aacute;ta zost&aacute;vaj&uacute; u v&aacute;s</b><span>pracujeme vo va&scaron;om Microsoft 365, ni&ccaron; sa nevyv&aacute;&zcaron;a</span></div>
<div class="stat"><b>&Zcaron;iadny nov&yacute; softv&eacute;r</b><span>pou&zcaron;&iacute;vame to, čo u&zcaron; m&aacute;te a m&aacute;te schv&aacute;len&eacute;</span></div>
<div class="stat"><b>Jeden proces, nie cel&aacute; firma</b><span>začneme t&yacute;m, ktor&yacute; st&aacute;le bol&iacute;</span></div>
<div class="stat"><b>Odovzd&aacute;me to v&aacute;m</b><span>vr&aacute;tane dokument&aacute;cie, nie ste na n&aacute;s viazan&iacute;</span></div>
</div>

{{IMG:sk-copilot-vrstva|Firemná AI nad Microsoft 365}}
<h2 class="section-title">Pre&ccaron;o Copilot vo firm&aacute;ch nedodr&zcaron;&iacute;, čo sľubuje</h2>
<p>Copilot vie odpovedať len z toho, k čomu m&aacute; pr&iacute;stup a čomu rozumie.
V be&zcaron;nej firme naraz&iacute; na tri veci:</p>
<ul>
<li><strong>Znalosť nie je zap&iacute;san&aacute;.</strong> Najd&ocirc;le&zcaron;itej&scaron;ie vie
sk&uacute;sen&yacute; človek z hlavy. V dokumentoch to nie je, tak&zcaron;e to nen&aacute;jde ani AI.</li>
<li><strong>Informácie s&uacute; roztr&uacute;sen&eacute;.</strong> Postup v SharePointe, hist&oacute;ria
pr&iacute;padov v Exceli, rozhodnutie v Teams chate, d&aacute;ta v ERP. Človek to
pospája za p&ocirc;l dňa. Copilot bez &scaron;trukt&uacute;ry to nepospája v&ocirc;bec.</li>
<li><strong>Nikto mu nepovedal, ako sa to u v&aacute;s rob&iacute;.</strong> Bez postupu
d&aacute;va v&scaron;eobecn&uacute; odpoveď namiesto tej va&scaron;ej.</li>
</ul>
<p>Preto dnes v&yacute;sledok z&aacute;vis&iacute; od toho, ako dobre vie konkr&eacute;tny
zamestnanec formulovať ot&aacute;zku. To nie je syst&eacute;m, to je n&aacute;hoda.</p>

<h2 class="section-title">&Ccaron;o pre v&aacute;s urob&iacute;me</h2>
<p>Vyberieme <strong>jeden proces</strong>, ktor&yacute; sa vo va&scaron;ej firme opakuje a
stoj&iacute; st&aacute;le rovnak&uacute; pr&aacute;cu - napr&iacute;klad rie&scaron;enie reklam&aacute;cie,
pr&iacute;pravu ponuky, spracovanie objedn&aacute;vky, zapracovanie nov&eacute;ho človeka -
a postav&iacute;me okolo neho &scaron;trukt&uacute;ru:</p>
<ol>
<li><strong>Zmapujeme, kde znalosť naozaj je</strong> - a hlavne kde ch&yacute;ba.
V&yacute;stupom je aj zoznam vec&iacute;, ktor&eacute; nikde zap&iacute;san&eacute; nie s&uacute;.</li>
<li><strong>Usporiadame ju tak, aby sa v nej dalo hľadať</strong> - kateg&oacute;rie,
&scaron;trukt&uacute;ra pr&iacute;padu, prepojenia medzi zdrojmi.</li>
<li><strong>Nastav&iacute;me postup</strong> - čo m&aacute; syst&eacute;m spraviť v ktorom kroku,
čo m&aacute; dohľadať, na čo m&aacute; upozorniť, kedy m&aacute; povedať &bdquo;toto nem&aacute;m&ldquo;.</li>
<li><strong>Overíme v&yacute;stup na va&scaron;ich re&aacute;lnych, u&zcaron; uzavret&yacute;ch pr&iacute;padoch</strong>
- porovnanie s t&yacute;m, ako to dopadlo v skutočnosti.</li>
<li><strong>Odovzd&aacute;me to aj s dokument&aacute;ciou</strong>, aby to vedel udr&zcaron;iavať
v&aacute;&scaron; človek, nie len my.</li>
</ol>
<p class="form-note"><strong>Pozn&aacute;mka k bezpe&ccaron;nosti:</strong> pracujeme vo va&scaron;om
prostred&iacute; Microsoft 365. Va&scaron;e d&aacute;ta z neho neodch&aacute;dzaj&uacute; a nepotrebujeme
ich kop&iacute;rovať k n&aacute;m.</p>

<h2 class="section-title">Ako zist&iacute;te, &zcaron;e odpoveď je spr&aacute;vna</h2>
<p>Toto je d&ocirc;vod, prečo AI vo firm&aacute;ch zost&aacute;va pri mailoch. Nie preto,
&zcaron;e by nevedela viac - ale preto, &zcaron;e <strong>nikto nevie overiť, či je
odpoveď spr&aacute;vna</strong>. Čo sa ned&aacute; skontrolovať, tomu firma nezver&iacute;
rozhodnutie s n&aacute;sledkom.</p>
<p>Preto s ka&zcaron;d&yacute;m nasaden&iacute;m dod&aacute;vame dve kontroly, ktor&eacute; be&zcaron;ia
aj po odovzdan&iacute;:</p>
<ul>
<li><strong>Kontrola znalosti pri ka&zcaron;dej zmene.</strong> Ke&zcaron; niekto uprav&iacute;
postup alebo pravidlo, strojovo sa overí, či v&scaron;etko d&aacute;va zmysel dohromady -
či niektor&yacute; krok neodkazuje na pravidlo, ktor&eacute; u&zcaron; neexistuje, či sa niečo
nevyskytuje dvakr&aacute;t, či niekde nechýba povinn&aacute; časť. <strong>Čo neprejde,
sa nenasad&iacute;.</strong></li>
<li><strong>Pevn&aacute; sada skú&scaron;obn&yacute;ch pr&iacute;padov, ktor&uacute; schvaľujete vy.</strong>
Zad&aacute;me ich pred vami a porovn&aacute;me odpoveď s t&yacute;m, čo m&aacute; vyj&scaron;ť. Časť
z nich je blokuj&uacute;ca - naprí&scaron;klad &zcaron;e syst&eacute;m mus&iacute; povedať <em>„toto
neviem"</em> namiesto vierohodnej vymyslenej odpovede. Ak zlyh&aacute; ktor&aacute;koľvek
z nich, verzia sa nevyd&aacute;va.</li>
</ul>
<p><strong>Znalosť do AI dostane ktokoľvek</strong> - stač&iacute; nahrať dokumenty.
Postup nap&iacute;&scaron;e tie&zcaron; ktokoľvek. To, čo obvykle chýba, je d&ocirc;kaz,
&zcaron;e to funguje - a &zcaron;e to funguje <strong>aj po zmene</strong>, ktor&uacute;
o pol roka urob&iacute; niekto in&yacute;.</p>

<h2 class="section-title">Ostatn&eacute; slu&zcaron;by</h2>

{{IMG:custom-website-design-development|Webstránky}}
<h2>Webstr&aacute;nky</h2>
<p>Firemn&yacute; web, produktov&aacute; str&aacute;nka alebo landing page - navrhnut&eacute; na to,
čo skutočne potrebujete, nie šabl&oacute;na s vložen&yacute;m logom. Rýchle načítanie,
funkčné na mobile, so z&aacute;kladn&yacute;m SEO, aby v&aacute;s vyhľad&aacute;vače pochopili.</p>
<p><strong>Čo to znamen&aacute; pre v&aacute;s:</strong> dostanete hotov&yacute;, nasaden&yacute;
a funguj&uacute;ci web - nie grafick&yacute; n&aacute;vrh, ktor&yacute; mus&iacute; niekto in&yacute;
naprogramovať.</p>

{{IMG:automation-integrations|Automatizácia a integrácie}}
<h2>Automatiz&aacute;cia a integr&aacute;cie</h2>
<p>Ak niečo rob&iacute;te každ&yacute; t&yacute;ždeň ručne - prepisovanie &uacute;dajov medzi
syst&eacute;mami, stavanie toho ist&eacute;ho reportu, kontrola zmien u dod&aacute;vateľa - d&aacute;
sa to nahradiť softv&eacute;rom, ktor&yacute; bež&iacute; s&aacute;m.</p>
<p><strong>Čo to znamen&aacute; pre v&aacute;s:</strong> &uacute;loha na dve hodiny t&yacute;ždenne
je približne sto hod&iacute;n ročne. Ak v&aacute;m to nedok&aacute;žeme vr&aacute;tiť, povieme to
skôr, než začneme.</p>

{{IMG:tailored-digital-product|Digitálne produkty na mieru}}
<h2>Digit&aacute;lne produkty na mieru</h2>
<p>Šabl&oacute;ny, kontroln&eacute; zoznamy, kalkulačky, sady scen&aacute;rov alebo intern&eacute;
n&aacute;stroje - postaven&eacute; na v&aacute;š konkr&eacute;tny probl&eacute;m a vo vašom jazyku,
nie generick&yacute; materi&aacute;l.</p>

{{IMG:design-branding-visual-identity|Dizajn a firemná identita}}
<h2>Dizajn a firemn&aacute; identita</h2>
<p>Logo, farebn&yacute; a typografick&yacute; syst&eacute;m, marketingov&aacute; grafika,
prezent&aacute;cie. Dostanete aj pravidl&aacute; použitia a funkčn&yacute; stylesheet, nie len
obr&aacute;zok loga.</p>

<h2>Chatboty</h2>
<p>Chatbot na jednu konkr&eacute;tnu &uacute;lohu - odpovedanie na opakuj&uacute;ce sa ot&aacute;zky
z&aacute;kazn&iacute;kov - s jasne vymedzen&yacute;m rozsahom, aby si nevym&yacute;šľal.</p>

<h2 class="section-title">Užitočn&eacute; č&iacute;tanie</h2>
<div class="post-list">SK_ARTICLES</div>

<h2 id="cennik" class="section-title">Cenn&iacute;k</h2>
<p>Ceny uv&aacute;dzame otvorene, hoci v&auml;čšina agent&uacute;r to nerob&iacute;. Je to
r&yacute;chlejšie pre v&aacute;s aj pre n&aacute;s: hneď vid&iacute;te, či sa vôbec bav&iacute;me
o rovnak&yacute;ch č&iacute;slach. Sumy s&uacute; <strong>&bdquo;od&ldquo;</strong> - konečn&uacute;
cenu dostanete p&iacute;somne po tom, ako pozn&aacute;me rozsah, a už sa nemen&iacute;.</p>
<table>
<tr><th>Čo</th><th>Cena od</th><th>Čo cenu men&iacute;</th></tr>
<tr><td><strong>Posudok jedn&eacute;ho procesu</strong> + uk&aacute;&zcaron;ka na va&scaron;om re&aacute;lnom pr&iacute;pade</td>
<td><strong>490 &euro;</strong></td>
<td>pevn&aacute; cena; ak vyjde, &zcaron;e sa nasadenie neopl&aacute;ca, povieme to</td></tr>
<tr><td><strong>Nasadenie jedn&eacute;ho procesu</strong> do v&aacute;&scaron;ho Microsoft 365</td>
<td><strong>2 400 &euro;</strong></td>
<td>počet zdrojov d&aacute;t, stav dokument&aacute;cie, počet krokov procesu</td></tr>
<tr><td>Ka&zcaron;d&yacute; ďal&scaron;&iacute; proces</td><td><strong>1 400 &euro;</strong></td>
<td>lacnej&scaron;&iacute;, lebo &scaron;trukt&uacute;ra u&zcaron; existuje</td></tr>
<tr id="cennik-sluzby"><td>Jednostr&aacute;nkov&yacute; web (landing page)</td><td><strong>590 &euro;</strong></td>
<td>množstvo obsahu, formul&aacute;re, jazykov&eacute; verzie</td></tr>
<tr><td>Firemn&yacute; web (do 8 podstr&aacute;nok)</td><td><strong>1 190 &euro;</strong></td>
<td>počet str&aacute;nok, blog, napojenie na extern&eacute; syst&eacute;my</td></tr>
<tr><td>Automatiz&aacute;cia jednej &uacute;lohy</td><td><strong>390 &euro;</strong></td>
<td>počet syst&eacute;mov, kvalita vstupn&yacute;ch d&aacute;t</td></tr>
<tr><td>Digit&aacute;lny produkt na mieru</td><td><strong>290 &euro;</strong></td>
<td>rozsah, či ide o text, tabuľku alebo interakt&iacute;vny n&aacute;stroj</td></tr>
<tr><td>Logo a z&aacute;kladn&aacute; identita</td><td><strong>390 &euro;</strong></td>
<td>počet v&yacute;stupov, šablóny, rozsah pravidiel</td></tr>
<tr><td>Chatbot</td><td><strong>690 &euro;</strong></td>
<td>rozsah znalost&iacute;, napojenie na vaše d&aacute;ta</td></tr>
</table>
<p class="form-note">Ceny s&uacute; bez DPH. Prev&aacute;dzkov&eacute; n&aacute;klady, ktor&eacute;
plat&iacute;te priamo poskytovateľovi (dom&eacute;na, hosting, jazykov&yacute; model pri chatbote),
v cene nie s&uacute; - nechceme ich mať cez seba, aby ste neboli na n&aacute;s viazan&iacute;.</p>
<p><strong>Ak sa v&aacute;m rozpočet a rozsah nestret&aacute;vaj&uacute;</strong>, povieme to a
navrhneme, čo vynechať. Menšia vec sprav&eacute;n&aacute; poriadne je lepšia než veľk&aacute; sprav&eacute;n&aacute; polovične.</p>

<div class="card">
<h2>Rozsah m&aacute;te nap&iacute;san&yacute; e&scaron;te pred podpisom</h2>
<p>Aby ste vedeli presne, čo je v cene, kto čo rob&iacute; a kde v&aacute;&scaron; človek
prevezme &scaron;taf&eacute;tu. Bez toho sa najlep&scaron;ie pon&uacute;ky rozp&aacute;raj&uacute;
a&zcaron; v polovici pr&aacute;ce.</p>
<ul>
<li><strong>Va&scaron;i odborn&iacute;ci zost&aacute;vaj&uacute; a syst&eacute;m rob&iacute; pre nich.</strong>
Prestanete ručne dohľad&aacute;vať a prepisovať. &Uacute;sudok - a zodpovednosť za
rozhodnutie - zost&aacute;va na va&scaron;om človeku, aj preto, &zcaron;e to tak chcú audity
aj z&aacute;kazn&iacute;ci.</li>
<li><strong>Prv&yacute;m krokom je spísať znalosť, ktor&aacute; je zatiaľ v hlave.</strong>
Copilot dok&aacute;&zcaron;e pracovať len s t&yacute;m, čo je zap&iacute;san&eacute;. Uk&aacute;&zcaron;eme
presne, čo chýba, d&aacute;me tomu &scaron;trukt&uacute;ru a prevedieme t&yacute;m va&scaron;ich
ľud&iacute; - samotn&eacute; know-how ale mus&iacute; prísť od nich, je to ich v&yacute;hoda.</li>
<li><strong>Pracujeme s licenciami, ktor&eacute; u&zcaron; m&aacute;te.</strong> Nič nov&eacute;
nekupujete a nie ste viazan&iacute; cez na&scaron;u fakt&uacute;ru. Prev&aacute;dzkov&eacute; &uacute;čty
(dom&eacute;na, hosting, jazykov&yacute; model) zost&aacute;vaj&uacute; na va&scaron;e meno.</li>
<li><strong>Staviame vrstvu nad va&scaron;&iacute;m QMS, ERP a SharePointom.</strong>
Nič nemigrujete a nič nevypn&aacute;te. Va&scaron;e syst&eacute;my zost&aacute;vaj&uacute; tam, kde s&uacute;.</li>
<li><strong>Prihlasovanie, podpisovanie a peniaze vraciame človeku.</strong>
Z&aacute;merne. Automatizujeme kroky okolo, rozhodnutie s pr&aacute;vnym alebo
finančn&yacute;m n&aacute;sledkom nechávame na v&aacute;s.</li>
<li><strong>Dostanete zdrojov&yacute; k&oacute;d aj dokument&aacute;ciu.</strong> Aby to vedel
udr&zcaron;iavať v&aacute;&scaron; človek. Úpravy vieme robiť aj my za pevn&yacute; poplatok,
prípadne v&aacute;m postav&iacute;me administračn&yacute; panel - dohodneme to vopred, nie potom.</li>
<li><strong>Ak sa niečo ned&aacute; spraviť poriadne, povieme to skôr, ne&zcaron; začneme.</strong>
Aj keď to znamen&aacute; men&scaron;iu zák&aacute;zku alebo odporúčanie na niekoho in&eacute;ho -
ilustr&aacute;tora, tlačiareň, špecialistu na e-shopy. Men&scaron;ia vec sprav&eacute;n&aacute;
poriadne je lep&scaron;ia ne&zcaron; veľk&aacute; sprav&eacute;n&aacute; polovične.</li>
</ul>

<div class="card">
<h2>Ako pracujeme</h2>
<p><strong>1. Poviete, čo nefunguje.</strong> Konkr&eacute;tny probl&eacute;m poviete lepšie než
zadanie - &bdquo;str&aacute;came dopyty, lebo n&aacute;s ľudia nen&aacute;jdu&ldquo; ukazuje niekam
konkr&eacute;tne.</p>
<p><strong>2. Dostanete p&iacute;somn&uacute; ponuku.</strong> Čo presne dostanete, v
ak&yacute;ch form&aacute;toch, koľko to stoj&iacute; a dokedy. Pevn&aacute; suma, dohodnut&aacute;
predt&yacute;m, než sa začne pracovať - žiadne hodinov&eacute; &uacute;čtovanie a žiadna
prekvapiv&aacute; fakt&uacute;ra.</p>
<p><strong>3. Postav&iacute;me to.</strong> Uvid&iacute;te rozpracovan&uacute; verziu, nie hotov&uacute;
vec predloženú ako fin&aacute;lnu. Dve kol&aacute; &uacute;prav s&uacute; s&uacute;časťou ceny.</p>
<p><strong>4. Patr&iacute; to v&aacute;m.</strong> Pln&eacute; komerčn&eacute; pr&aacute;va vr&aacute;tane
zdrojov&yacute;ch s&uacute;borov. Žiadne mesačn&eacute; poplatky a žiadna z&aacute;vislosť od n&aacute;s.</p>
</div>

<div class="card">
<h2>Pozrite si našu pr&aacute;cu</h2>
<p>Tento web, produkty, n&aacute;stroje aj syst&eacute;m, ktor&yacute; to všetko publikuje -
postavili sme to my. Je to živ&eacute;, funguje to a d&aacute; sa to overiť za min&uacute;tu.
<a href="../work.html">Pozrite si to</a>.</p>
<p><strong>Riziko nesieme my.</strong> Pevn&aacute; cena a p&iacute;somn&yacute; rozsah dohodnut&yacute;
predt&yacute;m, než sa začne pracovať. Ak sa pr&aacute;ca uk&aacute;že ťažšia, než sme odhadli, je to
n&aacute;š probl&eacute;m - nie upraven&aacute; fakt&uacute;ra. V&yacute;sledok je v&aacute;š vr&aacute;tane
zdrojov&yacute;ch s&uacute;borov, bez mesačn&yacute;ch poplatkov a bez viazanosti.</p>
</div>

<h2 id="kontakt" class="section-title">Ozvite sa</h2>\n""" + contact_form_html("sk") + """
<p class="form-note">Str&aacute;nka je aj <a href="../index.html">v angličtine</a>.</p>"""

    from agents.blog_agent import load_sk_posts
    cards = "\n".join(
        f'<a class="post-card" href="{a["slug"]}.html">'
        f'{card_art(a["slug"], a["title"])}'
        f'<span class="post-meta">{a["date"]}</span>'
        f'<h3>{html.escape(a["title"])}</h3>'
        f'<p>{html.escape(a["description"])}</p></a>'
        for a in load_sk_posts())
    body = body.replace("SK_ARTICLES", cards)

    # Obrazky k sekciam sluzieb. Do 2026-08-16 mala SK stranka styri obrazky a
    # vsetky boli nahlady clankov dole - samotne sluzby ziadny, kym anglicka
    # domovska ich mala 22. Fotky pritom v repozitari uz boli, len sa tu
    # nepouzivali. depth=1, lebo stranka sedi v /sk/.
    body = re.sub(r"\{\{IMG:([a-z0-9\-]+)\|([^}]+)\}\}",
                  lambda m: card_art(m.group(1), m.group(2), depth=1),
                  body)

    if SITE_BASE_URL:
        alt = (f'<link rel="canonical" href="{SITE_BASE_URL}/sk/">\n'
               f'<link rel="alternate" hreflang="sk" href="{SITE_BASE_URL}/sk/">\n'
               f'<link rel="alternate" hreflang="en" href="{SITE_BASE_URL}/">\n'
               f'<link rel="alternate" hreflang="x-default" href="{SITE_BASE_URL}/">\n'
               f'<meta property="og:title" content="Vyu\u017eite firemn\u00fd Copilot naplno">\n'
               f'<meta property="og:url" content="{SITE_BASE_URL}/sk/">\n'
               f'<meta property="og:type" content="website">\n' + OG_IMAGE_TAGS)
    else:
        alt = ""
    sk_dir = SITE_DIR / "sk"
    sk_dir.mkdir(parents=True, exist_ok=True)
    page = page_shell(
        "Vyu\u017eite firemn\u00fd Copilot naplno | Biznis",
        "Firmy platia za Microsoft 365 Copilot a pou\u017e\u00edvaj\u00fa zlomok toho, \u010do vie. "
        "Postav\u00edme nad n\u00edm \u0161trukt\u00faru pre jeden proces. D\u00e1ta zost\u00e1vaj\u00fa u v\u00e1s.",
        body, lang="sk")
    if alt:
        idx = page.lower().find("</head>")
        if idx != -1:
            page = page[:idx] + alt + page[idx:]
    page = page.replace('<html lang="en">', '<html lang="sk">')
    (sk_dir / "index.html").write_text(page)



EFA_WIDGET = """
<div class="widget">
  <label for="q1">1. Ste platiteľ DPH?</label>
  <select id="q1">
    <option value="ano">Áno, som platiteľ DPH</option>
    <option value="nie">Nie, nie som platiteľ DPH</option>
    <option value="neviem">Neviem / chystám sa ním stať</option>
  </select>

  <label for="q2">2. Ako dnes vystavujete faktúry?</label>
  <select id="q2">
    <option value="softver">Vo fakturačnom programe (iDoklad, SuperFaktúra, Kros…)</option>
    <option value="excel">V Exceli, Worde alebo ručne</option>
    <option value="system">Generuje ich môj vlastný systém alebo e-shop</option>
    <option value="uctovnik">Robí to za mňa účtovník</option>
  </select>

  <label for="q3">3. Koľko faktúr vystavíte za mesiac?</label>
  <select id="q3">
    <option value="malo">Do 10</option>
    <option value="stredne">10 až 50</option>
    <option value="vela">Viac ako 50</option>
  </select>

  <label for="q4">4. Prepisujete údaje pre faktúru odniekiaľ ručne?</label>
  <select id="q4">
    <option value="nie">Nie, vznikajú rovno vo fakturácii</option>
    <option value="ano">Áno, prepisujem ich z tabuľky, e-mailu alebo iného systému</option>
  </select>

  <div class="widget-out" id="verdict"><b id="vtitle">—</b><span id="vsub"></span></div>
  <div id="detail" style="margin-top:1.2rem"></div>
</div>
<script>
(function () {
  var ids = ['q1','q2','q3','q4'];
  function v(id){ return document.getElementById(id).value; }
  function calc() {
    var dph = v('q1'), how = v('q2'), vol = v('q3'), retype = v('q4');
    var title, sub, parts = [];

    var mustIssue = (dph === 'ano');
    var mustReceive = true; // prijímať potrebuje vedieť prakticky každý

    if (!mustIssue && dph === 'nie') {
      title = 'Vystavovať e-faktúry nemusíte';
      sub = 'ale prijímať ich potrebujete vedieť';
      parts.push('<p>Podľa schválenej úpravy sa povinnosť <strong>vystavovať</strong> e-faktúry neplatiteľov DPH netýka. Ak vám ich však pošle dodávateľ, musíte ich vedieť <strong>prijať a spracovať</strong>.</p>');
    } else if (dph === 'neviem') {
      title = 'Najprv si overte, či ste platiteľ DPH';
      sub = 'od toho závisí všetko ostatné';
      parts.push('<p>Povinnosť vystavovať e-faktúry sa viaže na platiteľov DPH. Overte si to u účtovníka — je to jedna otázka a určuje, či sa vás týka celý zvyšok.</p>');
    } else {
      title = 'Povinnosť sa vás týka';
      sub = 'od 1. januára 2027, vystavovanie aj prijímanie';
      parts.push('<p>Ako platiteľ DPH budete musieť faktúry <strong>vystavovať aj prijímať</strong> v štruktúrovanom formáte (XML podľa EN 16931). PDF v e-maile prestane stačiť.</p>');
    }

    if (how === 'softver') {
      parts.push('<h3>Čo spravte</h3><p>Pravdepodobne <strong>nič nekupujte</strong>. Napíšte svojmu dodávateľovi jednu otázku a odpoveď si nechajte písomne:</p><blockquote>Budete do konca roka 2026 podporovať vystavovanie aj prijímanie faktúr v štruktúrovanom formáte podľa EN 16931? Bude to v mojom balíku, alebo za príplatok?</blockquote><p>Ak odpoveď je áno a bez príplatku, máte hotovo.</p>');
      parts.push('<p class="widget-note"><strong>Odhadovaný náklad:</strong> 0 € až cena vyššieho balíka vášho programu.</p>');
    } else if (how === 'excel') {
      parts.push('<h3>Čo spravte</h3><p>Ručne vyrobiť platné XML podľa normy nie je reálne — Excel ani Word to nespravia. Budete potrebovať nástroj.</p><p><strong>Dobrá správa, ktorú vám väčšina článkov nepovie:</strong> štát pripravuje v rámci systému IS EFA <strong>bezplatnú webovú aplikáciu pre malých podnikateľov</strong> na vytváranie a správu faktúr v predpísanom formáte, vrátane kontroly správnosti.</p>');
      if (vol === 'malo') {
        parts.push('<p>Pri vašom objeme faktúr je <strong>bezplatná štátna aplikácia veľmi pravdepodobne úplne postačujúca.</strong> Kupovať softvér ani si dávať niečo stavať nepotrebujete.</p>');
        parts.push('<p class="widget-note"><strong>Odhadovaný náklad: 0 €.</strong> Od nás nepotrebujete nič.</p>');
      } else {
        parts.push('<p>Pri vašom objeme zvážte fakturačný program s podporou formátu — bezplatná štátna aplikácia zvládne aj toto, ale pri desiatkach faktúr mesačne oceníte automatické funkcie.</p>');
        parts.push('<p class="widget-note"><strong>Odhadovaný náklad:</strong> 0 € (štátna aplikácia) alebo bežné predplatné fakturačného programu.</p>');
      }
    } else if (how === 'uctovnik') {
      parts.push('<h3>Čo spravte</h3><p>Opýtajte sa účtovníka <strong>skôr, než čokoľvek objednáte</strong>. Časť povinnosti môže byť pokrytá tým, čo pre vás už robí. Toto je najlacnejšia otázka v celej príprave.</p>');
      parts.push('<p class="widget-note"><strong>Odhadovaný náklad:</strong> pravdepodobne 0 € navyše. Overte, či účtovník nezdvihne cenu.</p>');
    } else {
      parts.push('<h3>Čo spravte</h3><p>Toto je jediný scenár, kde ide o skutočnú prácu. Vlastný systém alebo e-shop musí začať produkovať štruktúrované XML podľa normy a vedieť prijaté faktúry spracovať. To je zásah do systému, nie nastavenie.</p><p><strong>Neodkladajte to na koniec roka 2026</strong> — vtedy bude o kapacitu dodávateľov najväčší tlak a ceny podľa toho.</p>');
      parts.push('<p class="widget-note"><strong>Odhadovaný náklad:</strong> rádovo stovky až tisíce eur podľa toho, ako je systém postavený.</p>');
    }

    if (retype === 'ano') {
      parts.push('<h3>Ešte jedna vec, ktorá sa vám oplatí</h3><p>Uviedli ste, že údaje pre faktúru odniekiaľ prepisujete ručne. Prepis je najčastejšie miesto vzniku chýb a pri prechode na štruktúrovaný formát sa to zhorší — chybná faktúra neprejde kontrolou.</p><p>Zároveň je to presne tá časť, ktorú sa oplatí automatizovať bez ohľadu na e-faktúru. Ak prepisovanie zaberie dve hodiny týždenne, je to zhruba sto hodín ročne.</p>');
    }

    document.getElementById('vtitle').textContent = title;
    document.getElementById('vsub').textContent = sub;
    document.getElementById('detail').innerHTML = parts.join('');
  }
  ids.forEach(function(id){
    var el = document.getElementById(id);
    el.addEventListener('change', calc);
  });
  calc();
})();
</script>
"""


def build_efa_tool() -> None:
    """Free Slovak decision tool for the 2027 e-invoicing obligation.

    Built instead of another explainer article. Every piece of content on
    this topic is published by a company selling invoicing software, so
    none of them lead with the fact that the state provides a free web app
    for small businesses under IS EFA - which for a low-volume Excel user
    is the entire answer. A tool that says "you need nothing, here is why"
    is the one thing nobody selling software will build.

    The obligation starts 1 January 2027 and voluntary testing is running
    now, so this is the window where people begin looking.
    """
    body = """<span class="eyebrow">Bezplatn&yacute; n&aacute;stroj</span>
<h1>Ste pripraven&iacute; na e-fakt&uacute;ru 2027?</h1>
<p class="subtitle">Od 1. janu&aacute;ra 2027 musia platitelia DPH vystavovať aj prij&iacute;mať
fakt&uacute;ry v štrukt&uacute;rovanom form&aacute;te. Odpovedzte na štyri ot&aacute;zky a
dostanete konkr&eacute;tnu odpoveď na svoju situ&aacute;ciu - vr&aacute;tane toho, či
nepotrebujete kupovať v&ocirc;bec nič.</p>
""" + EFA_WIDGET + """
<div class="card">
<h2>Pre&ccaron;o tento n&aacute;stroj vznikol</h2>
<p>O e-fakt&uacute;re 2027 je nap&iacute;san&yacute;ch desiatky &ccaron;l&aacute;nkov. Skoro
v&scaron;etky ich publikuj&uacute; firmy, ktor&eacute; predávaj&uacute; faktura&ccaron;n&yacute;
softv&eacute;r - a preto sa v nich len ťažko dozviete, že <strong>&scaron;t&aacute;t
pripravuje v r&aacute;mci syst&eacute;mu IS EFA bezplatn&uacute; webov&uacute; aplik&aacute;ciu
pre mal&yacute;ch podnikateľov</strong> na tvorbu a spr&aacute;vu fakt&uacute;r v predp&iacute;sanom
form&aacute;te.</p>
<p>Pre &ccaron;asť firiem je pr&aacute;ve to cel&aacute; odpoveď. My stav&iacute;me
automatiz&aacute;cie - a aj tak v&aacute;m to povieme, lebo predať niekomu rie&scaron;enie
probl&eacute;mu, ktor&yacute; nem&aacute;, je r&yacute;chly sp&ocirc;sob, ako pr&iacute;sť o
d&ocirc;veru.</p>
<p class="form-note">Toto je orienta&ccaron;n&yacute; n&aacute;stroj, nie da&ncaron;ov&eacute;
ani pr&aacute;vne poradenstvo. Konkr&eacute;tnu situ&aacute;ciu si potvrďte s &uacute;&ccaron;tovn&iacute;kom.
V&scaron;etko be&zcaron;&iacute; vo va&scaron;om prehliada&ccaron;i - ni&ccaron; sa neodosiela
a ni&ccaron; neukladáme.</p>
</div>

<h2>Čo hovor&iacute; z&aacute;kon</h2>
<p>Novelu z&aacute;kona o DPH schv&aacute;lila N&aacute;rodn&aacute; rada 9. decembra 2025 a
prezident ju podp&iacute;sal 16. decembra 2025. Od <strong>1. 1. 2027</strong> musia platitelia
DPH vystavovať a prij&iacute;mať fakt&uacute;ry v &scaron;trukt&uacute;rovanom XML podľa
eur&oacute;pskej normy <strong>EN 16931</strong> a elektronicky hl&aacute;siť vybran&eacute;
&uacute;daje. Dobrovoľn&eacute; testovanie be&zcaron;&iacute; u&zcaron; teraz. Cezhrani&ccaron;n&eacute;
dodania sa maj&uacute; pridať od 1. 7. 2030 v r&aacute;mci bal&iacute;ka ViDA.</p>

<h2>Ak vy&scaron;lo, &zcaron;e potrebujete z&aacute;sah do syst&eacute;mu</h2>
<p>Nie sme &uacute;&ccaron;tovn&iacute;ci ani da&ncaron;ov&iacute; poradcovia. &Ccaron;o vieme
spraviť, je technick&aacute; &ccaron;asť: aby v&aacute;&scaron; syst&eacute;m alebo e-shop
produkoval spr&aacute;vny form&aacute;t, aby sa prijat&eacute; fakt&uacute;ry spracovali samy
namiesto prepisovania, alebo aby si dva syst&eacute;my kone&ccaron;ne odovzd&aacute;vali
&uacute;daje.</p>
<p>Automatiz&aacute;ciu jednej &uacute;lohy stav&iacute;me <strong>od 390 &euro;</strong> bez
DPH, pevnou sumou dohodnutou vopred, so zdrojov&yacute;m k&oacute;dom pre v&aacute;s.
<a href="index.html#kontakt">Nap&iacute;&scaron;te n&aacute;m</a>, ako dnes fakt&uacute;ry vznikaj&uacute;.</p>
<p>Ne&ccaron;akajte v&scaron;ak z&aacute;zraky od automatiz&aacute;cie sam-o-sebe: opl&aacute;ca sa
len tam, kde je &uacute;loha dostato&ccaron;ne &ccaron;ast&aacute;. Ako si to spo&ccaron;&iacute;tať,
rozp&iacute;sali sme v &ccaron;l&aacute;nku
<a href="automatizacia-v-malej-firme.html">Automatiz&aacute;cia v malej firme: &ccaron;o sa
opl&aacute;ca a &ccaron;o je strata &ccaron;asu</a>.</p>

<p class="form-note"><strong>Zdroje:</strong>
<a href="https://e-fakturacia.finance.gov.sk/e-fakturacia/" target="_blank" rel="noopener">Ministerstvo financi&iacute; SR - Informa&ccaron;n&yacute; syst&eacute;m elektronickej fakturácie</a> &middot;
<a href="https://www.mfsr.sk/sk/media/tlacove-spravy/nova-web-stranka-15.html" target="_blank" rel="noopener">MF SR - tla&ccaron;ov&aacute; spr&aacute;va k syst&eacute;mu E-fakt&uacute;ra</a> &middot;
<a href="https://www.podnikajte.sk/dan-z-pridanej-hodnoty/efaktura-povinna-elektronicka-fakturacia-od-2027" target="_blank" rel="noopener">Podnikajte.sk</a></p>
<p><a href="index.html">&larr; Späť na slu&zcaron;by</a></p>"""

    page = page_shell(
        "Ste pripraven\u00ed na e-fakt\u00faru 2027? Bezplatn\u00fd test",
        "Odpovedzte na \u0161tyri ot\u00e1zky a zistite, \u010do mus\u00edte spravi\u0165 pred "
        "1. 1. 2027 - vr\u00e1tane toho, \u010di v\u00e1m sta\u010d\u00ed bezplatn\u00e1 "
        "aplik\u00e1cia \u0161t\u00e1tu.",
        body, lang="sk")
    if SITE_BASE_URL:
        url = f"{SITE_BASE_URL}/sk/efaktura-2027-test.html"
        extras = (f'<link rel="canonical" href="{url}">\n'
                  f'<meta property="og:title" content="Ste pripraven\u00ed na e-fakt\u00faru 2027?">\n'
                  f'<meta property="og:url" content="{url}">\n'
                  f'<meta property="og:type" content="website">\n' + OG_IMAGE_TAGS)
        i = page.lower().find("</head>")
        if i != -1:
            page = page[:i] + extras + page[i:]
    page = page.replace('<html lang="en">', '<html lang="sk">')
    sk = SITE_DIR / "sk"
    sk.mkdir(parents=True, exist_ok=True)
    (sk / "efaktura-2027-test.html").write_text(page)


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
        body, is_index=True, canonical_path="credits.html"))


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
    # These used to be internal counters - signals collected, keywords
    # scored - which flatter the person who built the pipeline and mean
    # nothing to someone deciding whether to hire us. Replaced with the
    # terms of doing business, which is what a buyer is actually weighing.
    stats_html = (
        '<div class="stats-strip">'
        '<div class="stat"><b>Fixed price</b><span>agreed in writing before any work starts</span></div>'
        '<div class="stat"><b>You own it</b><span>full rights and source files, no ongoing fees</span></div>'
        '<div class="stat"><b>Live, not a file</b><span>delivered working and deployed</span></div>'
        '<div class="stat"><b>Try it first</b><span>everything we have built is public</span></div>'
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
{blog_section}
<h2 id="kontakt" class="section-title">Tell us what you need</h2>
<p>A short description is enough to start. We reply with what we would do, what it costs, and what we would need from you.</p>
""" + (contact_form_html() if FORMSPREE_ENDPOINT else "") + """"""
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
