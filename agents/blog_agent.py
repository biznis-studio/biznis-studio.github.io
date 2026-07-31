"""Blog Agent.

Renders hand-written Markdown posts from content/blog/ into real static
pages under site/blog/, plus a blog index page. Added on direct user
request (2026-07-28) to give the site an editorial layer: articles,
curated links to genuinely useful external resources, and business
context around the products - not auto-generated filler. Posts are
written deliberately (a human/Claude authoring pass, same policy as
ebook prose - see ROADMAP.md), never templated from keywords.

File format (content/blog/YYYY-MM-DD-slug.md):

    title: Post title
    description: One-sentence summary used for meta/cards/RSS.
    ---
    Markdown body (the shared markdown-lite subset + [text](url) links).

The date comes from the filename prefix, the URL slug from the rest.
"""
import html
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import card_art, markdown_lite_to_html, site_header_html
from agents.landing_page_agent import OG_IMAGE_TAGS, page_shell

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content" / "blog"
BLOG_DIR = ROOT / "site" / "blog"
# Slovak articles live alongside the Slovak services page rather than in
# the English blog: they target Slovak search queries, and mixing the two
# languages in one index would give Google a page it cannot classify.
SK_CONTENT_DIR = ROOT / "content" / "sk"
SK_DIR = ROOT / "site" / "sk"
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "").rstrip("/")

_FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")


def load_sk_posts() -> list[dict]:
    """Slovak articles. Same front-matter format as the English ones."""
    posts = []
    if not SK_CONTENT_DIR.exists():
        return posts
    for path in sorted(SK_CONTENT_DIR.glob("*.md")):
        m = _FILENAME_RE.match(path.name)
        if not m:
            continue
        date, slug = m.group(1), m.group(2)
        raw = path.read_text()
        if "\n---\n" not in raw:
            continue
        head, body = raw.split("\n---\n", 1)
        meta = {}
        for line in head.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        if not meta.get("title"):
            continue
        posts.append({"slug": slug, "date": date, "title": meta["title"],
                      "description": meta.get("description", ""),
                      "body_md": body.strip(), "url": f"sk/{slug}.html"})
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def build_sk_posts() -> int:
    """Render Slovak articles into site/sk/ with hreflang-correct markup."""
    from agents.landing_page_agent import OG_IMAGE_TAGS, page_shell
    posts = load_sk_posts()
    if not posts:
        return 0
    SK_DIR.mkdir(parents=True, exist_ok=True)
    for post in posts:
        extras = ""
        if SITE_BASE_URL:
            url = f"{SITE_BASE_URL}/sk/{post['slug']}.html"
            extras = (f'<link rel="canonical" href="{html.escape(url)}">\n'
                      f'<meta property="og:title" content="{html.escape(post["title"])}">\n'
                      f'<meta property="og:description" content="{html.escape(post["description"])}">\n'
                      f'<meta property="og:url" content="{html.escape(url)}">\n'
                      f'<meta property="og:type" content="article">\n' + OG_IMAGE_TAGS)
        body = (f'<article class="post">\n{card_art(post["slug"], post["title"])}\n'
                f'<span class="post-meta">{post["date"]}</span>\n'
                f'<h1>{html.escape(post["title"])}</h1>\n'
                f'<p class="subtitle">{html.escape(post["description"])}</p>\n'
                f'{markdown_lite_to_html(post["body_md"])}\n'
                f'<p><a href="index.html">&larr; Späť na služby</a></p>\n</article>')
        page = page_shell(post["title"], post["description"], body, lang="sk")
        if extras:
            i = page.lower().find("</head>")
            if i != -1:
                page = page[:i] + extras + page[i:]
        page = page.replace('<html lang="en">', '<html lang="sk">')
        (SK_DIR / f"{post['slug']}.html").write_text(page)
    print(f"[blog_agent] built {len(posts)} Slovak articles")
    return len(posts)


def load_posts() -> list[dict]:
    """Parse every post's front matter + body. Sorted newest first.
    Shared with seo_agent.py so the sitemap and RSS feed include blog
    posts without needing a DB table for them."""
    posts = []
    if not CONTENT_DIR.exists():
        return posts
    for path in sorted(CONTENT_DIR.glob("*.md")):
        m = _FILENAME_RE.match(path.name)
        if not m:
            continue
        date, slug = m.group(1), m.group(2)
        raw = path.read_text()
        if "\n---\n" not in raw:
            continue
        head, body = raw.split("\n---\n", 1)
        meta = {}
        for line in head.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        if not meta.get("title"):
            continue
        posts.append({
            "slug": slug,
            "date": date,
            "title": meta["title"],
            "description": meta.get("description", ""),
            "body_md": body.strip(),
            "url": f"blog/{slug}.html",
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def _head_extras(title: str, description: str, path: str) -> str:
    """Canonical + Open Graph for a blog page. Blog pages don't flow
    through seo_agent's pages-table injection (that's keyed to products),
    so they get their head tags at build time instead."""
    if not SITE_BASE_URL:
        return ""
    url = f"{SITE_BASE_URL}/{path}"
    return (
        f'<link rel="canonical" href="{html.escape(url)}">\n'
        f'<meta property="og:title" content="{html.escape(title)}">\n'
        f'<meta property="og:description" content="{html.escape(description)}">\n'
        f'<meta property="og:url" content="{html.escape(url)}">\n'
        f'<meta property="og:type" content="article">\n'
        + OG_IMAGE_TAGS
    )


def _with_head_extras(page_html: str, extras: str) -> str:
    if not extras:
        return page_html
    idx = page_html.lower().find("</head>")
    return page_html[:idx] + extras + page_html[idx:] if idx != -1 else page_html


def _display_date(date: str) -> str:
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    y, m, d = date.split("-")
    return f"{months[int(m) - 1]} {int(d)}, {y}"


def build_post(post: dict) -> None:
    body = f"""<article class="post">
{card_art(post["slug"], post["title"])}
<span class="post-meta">Blog · {_display_date(post["date"])}</span>
<h1>{html.escape(post["title"])}</h1>
<p class="subtitle">{html.escape(post["description"])}</p>
{markdown_lite_to_html(post["body_md"])}
<p><a href="index.html">&larr; All posts</a></p>
</article>"""
    page = page_shell(post["title"], post["description"], body)
    page = _with_head_extras(page, _head_extras(post["title"], post["description"], post["url"]))
    (BLOG_DIR / f"{post['slug']}.html").write_text(page)


def build_blog_index(posts: list[dict]) -> None:
    cards = "\n".join(
        f'<a class="post-card" href="{p["slug"]}.html">'
        f'{card_art(p["slug"], p["title"])}'
        f'<span class="post-meta">{_display_date(p["date"])}</span>'
        f'<h3>{html.escape(p["title"])}</h3>'
        f'<p>{html.escape(p["description"])}</p></a>'
        for p in posts
    )
    body = f"""<div class="hero">
<h1>Blog</h1>
<p class="subtitle">Practical notes on freelancing, automation, and what it actually looks
like to run a small digital product business in public - including the numbers.</p>
</div>
<div class="post-list">
{cards}
</div>"""
    title = "Blog - Biznis"
    description = ("Practical notes on freelancing, automation, and running a small digital "
                   "product business in public.")
    page = page_shell(title, description, body)
    page = _with_head_extras(page, _head_extras(title, description, "blog/index.html"))
    (BLOG_DIR / "index.html").write_text(page)


def run() -> int:
    posts = load_posts()
    if not posts:
        print("[blog_agent] no posts found in content/blog/ - nothing to build")
        return 0
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    for post in posts:
        build_post(post)
    build_blog_index(posts)
    print(f"[blog_agent] built {len(posts)} posts + blog index")
    build_sk_posts()
    return len(posts)


if __name__ == "__main__":
    run()
