# Architecture

## Status legend
✅ implemented and tested · 🚧 partially implemented · ⬜ not started

## Loop graph (from the project brief) vs. current implementation

```
Market Research        ✅ agents/market_research_agent.py
      ↓
Keyword Discovery       ✅ agents/keyword_agent.py
      ↓
Niche Clustering        ✅ agents/niche_agent.py (co-occurrence/union-find;
      ↓                   found 0 real niches on runs 1-6, then 1 genuine
      ↓                   one on run 7 - a real Stack Exchange question
      ↓                   about a CodeIgniter bug, narrow but correct)
Demand Scoring (pass 1) ✅ agents/demand_scoring_agent.py::score_run()
      ↓                   (ranks the full pool so we know which ~20 to
      ↓                    spend GitHub's 10 req/min budget checking)
Competition Analysis    ✅ agents/competitor_agent.py (top-20 shortlist only -
      ↓                   see known limitations in ROADMAP.md)
Demand Scoring (pass 2) ✅ agents/demand_scoring_agent.py::apply_competition()
      ↓
Product Ideas           ✅ agents/product_agent.py
      ↓
Product Creation        ✅ agents/content_agent.py (calculator/checklist/template/
      ↓                   prompt_pack ship "ready"; ebook/sop are outline-only "draft")
Landing Page            ✅ agents/landing_page_agent.py (only for "ready"
      ↓                   products - static site under site/, pages.status
      ↓                   stays 'draft' until an actual Publishing agent exists)
SEO Optimization        ✅ agents/seo_agent.py (schema.org JSON-LD, OG tags,
      ↓                   genuine FAQ, internal links; sitemap.xml/feed.xml
      ↓                   emit once SITE_BASE_URL is set - see below)
Publishing              ✅ GitHub Pages, deployed via .github/workflows/
      ↓                   pipeline.yml (actions/deploy-pages) - live at
      ↓                   https://fwwk4pb868-afk.github.io/biznis/
Traffic Collection      ⬜ not started
      ↓
Analytics               ⬜ not started (schema exists: pages, analytics_events)
      ↓
Conversion Analysis     ⬜ not started
      ↓
User Feedback           ⬜ not started
      ↓
Product Improvement     ⬜ not started
      ↓
New Product Ideas       🔁 loop closes back to Product Ideas once analytics exist
```

## Why these 4 stages first

A discovery engine that can't tell "real demand" from "noise" will poison
every downstream stage (you'll write SEO content for a movie title nobody
will buy a product about). So the highest-leverage first slice was: prove
we can pull real signals from free APIs, extract genuine keyword candidates,
score them defensibly, and turn the winners into concrete (not vague)
product briefs — end to end, no mocked data. That's what's built.

## Data flow

```
5 free public APIs
   │  (agents/market_research_agent.py)
   ▼
signals_raw (SQLite)  — one row per raw hit, full payload kept for audit
   │  (agents/keyword_agent.py: stopword-filtered n-gram extraction,
   │   per-source percentile-rank normalization so no source's raw units
   │   (pageviews in the 100k range vs. HN points in the hundreds) dominate)
   ▼
keywords + keyword_run_stats (SQLite) — cumulative candidate list + per-run snapshot
   │  (agents/demand_scoring_agent.py::score_run(): frequency 40% + breadth 40% + growth 20%)
   ▼
demand_scores (SQLite, pass 1)
   │  (agents/competitor_agent.py: checks top 20 by pass-1 score against
   │   npm/GitHub/Stack Exchange/Wikipedia supply - GitHub's unauthenticated
   │   10 req/min search limit is why this is a shortlist, not all ~60)
   ▼
competition_checks (SQLite)
   │  (agents/demand_scoring_agent.py::apply_competition(): re-blends the
   │   checked 20 to frequency 30% + breadth 30% + growth 15% + opportunity 25%)
   ▼
demand_scores (SQLite, pass 2 for the checked subset)
   │  (agents/product_agent.py: regex format-matching, excludes
   │   Wikipedia-only keywords and npm package-name artifacts as
   │   non-commercial/non-topic noise)
   ▼
product_ideas (SQLite)
   │  (agents/content_agent.py: deterministic per-format generators -
   │   calculator/checklist/template/prompt_pack are genuinely usable
   │   output; ebook/sop are outline skeletons, status='draft')
   ▼
products (SQLite) + data/exports/products/*.{html,md,csv}
   │  (agents/landing_page_agent.py: builds a real page only for
   │   status='ready' products - calculator is copied through as-is,
   │   checklist/prompt_pack get a tiny built-in Markdown renderer,
   │   template gets an HTML table preview - each with a download link)
   ▼
pages (SQLite) + site/index.html + site/products/*.html + site/downloads/*
   │  (agents/seo_agent.py: injects schema.org JSON-LD + OG tags + a real
   │   FAQ + internal links into each page in place, idempotently via
   │   pages.seo_enhanced; sitemap.xml/feed.xml wait for SITE_BASE_URL)
   ▼
site/products/*.html (enhanced in place)
   → data/exports/run_XXXX.json + _ideas.csv
```

## Database schema

See [db/schema.sql](../db/schema.sql) — the single source of truth. Summary:

| Table | Purpose |
|---|---|
| `runs` | One row per pipeline execution; tracks stage/status/timing |
| `signals_raw` | Raw hits from the 5 free APIs, full JSON payload kept |
| `keywords` | Deduplicated, cumulative keyword candidates |
| `keyword_run_stats` | Per-run occurrence/weight snapshot (powers growth scoring) |
| `competition_checks` | Per-run npm/GitHub/Stack Exchange/Wikipedia supply check, top-20 shortlist only |
| `demand_scores` | Per-run score + components per keyword (re-blended for the checked shortlist) |
| `niches` / `niche_keywords` | Co-occurrence-based keyword clusters (`niche_agent.py`); empty until 2+ keywords share a signal |
| `product_ideas` | Generated product briefs (title, format, rationale, target keyword) |
| `products` | Actually-built product files (path, format, status ready/draft); `monetization_url` set once a product is listed for sale; `tier` (`core`/`lead_magnet`/`retire_candidate`) records validated-demand classification, see ROADMAP.md |
| `pages` | Landing pages for "ready" products (`landing_page_agent.py`); `status` stays 'draft' until deployed; `seo_enhanced` flags whether `seo_agent.py` already processed it |
| `analytics_events` | Traffic/conversion events (empty until publishing exists) |

## Design decisions worth knowing

- **No LLM dependency yet.** No local Ollama install or OpenRouter key was
  present in this environment, so both Product Idea Generation and Content
  Generation are rule-based/template-based, not LLM-generated. This keeps
  the system 100% free and fully deterministic/auditable, at the cost of
  creativity. Formats that can be genuinely useful without free-text
  writing (calculator, checklist, template, prompt_pack) ship as "ready";
  formats that need real prose (ebook, sop) are intentionally left as
  reviewable outline skeletons at status='draft' rather than faking
  finished content. First thing to upgrade once a model is wired in (see
  ROADMAP).
- **SQLite lives in git**, not `.gitignore`d. For a single-writer, low-volume
  pipeline this is simpler and freer than standing up Supabase/Turso, and it
  gives free version history of the whole business's memory for nothing.
  Revisit if the file grows large or multiple writers appear.
- **Per-source percentile-rank normalization** in the keyword agent, not raw
  log-scaling — otherwise Wikipedia's 100k+ pageviews would always outrank
  HN's ~500-point stories regardless of actual relative significance.
- **Product ideation no longer has a generic-ebook fallback.**
  `product_agent.py::pick_format()` used to turn any keyword that didn't
  match a specific format pattern into a "The Practical Guide to {term}"
  ebook idea. Real research this session showed this pattern is exactly
  what produced 14 low-value, never-promoted `retire_candidate` products
  (see `products.tier`, ROADMAP.md) - so it was removed. Unmatched keywords
  are now skipped entirely; ebook-format ideas only get created through
  deliberate manual research (`sources_json` tag `manual_research`), not
  raw keyword frequency.
- **Wikipedia is kept but fenced off from product ideation.** It's a decent
  general zeitgeist/timely-content signal but a poor proxy for "a problem
  someone would pay to have solved" (top pageviews skew celebrity/movie/
  sports). It stays in `keywords` for a future SEO/content-timing use case.
- **No AggregateRating/Review schema.org markup, ever.** The project's
  absolute rules forbid fake reviews; since there are no real ones yet,
  `seo_agent.py` only emits schema types that don't assert social proof
  (SoftwareApplication, HowTo, CreativeWork, FAQPage). Revisit only once
  genuine user reviews exist to mark up.
- **Sitemap.xml/feed.xml are gated on `SITE_BASE_URL` being set.** Both
  formats assert "this is live at this URL" - emitting them against a
  domain that doesn't exist would be misleading busywork. Now that GitHub
  Pages is live, `pipeline.yml` sets `SITE_BASE_URL` to the real deployed
  URL and both files generate with genuine absolute URLs.
- **GitHub Pages over Cloudflare Pages.** Chosen specifically because it
  needed no new account - Cloudflare Pages would have required the user to
  sign up there first, and this system doesn't create accounts on anyone's
  behalf. Deployed via `actions/upload-pages-artifact` + `actions/deploy-pages`
  as a second job in `pipeline.yml`, rather than GitHub Pages' classic
  branch-based source, since `site/` lives in a subdirectory of the repo
  (classic Pages only supports `/` or `/docs`).
- **Monetization is a nullable URL, not a payment integration.**
  `products.monetization_url` is the entire mechanism: unset means "free
  download," set means "link to that URL instead, and stop giving the file
  away for free next to it." No payment processing, checkout flow, or
  API keys live in this codebase - Gumroad (or whatever's chosen) handles
  all of that on its own platform, since this system doesn't create
  payment/seller accounts on the user's behalf.
- **Ebook/sop downloads are PDF, not raw Markdown.** Discovered 2026-07-26
  that Gumroad's file picker won't even accept `.md` as an upload type -
  and a raw Markdown file was never a great look for a standalone document
  anyway (checklist/prompt_pack stay Markdown on purpose, since their own
  copy tells the reader to paste it into Notion/a PDF/plain text - they're
  meant to be reused, not read as-is). `agents/pdf_export.py` renders
  through the same `markdown_lite_to_html()` used for the web page, then
  shells out to headless Chrome's `--print-to-pdf` (no PDF library is
  installed, and Chrome is already present). `landing_page_agent.py` wraps
  each PDF export in a try/except so one broken export can't take down the
  whole daily pipeline run; CI explicitly installs Chrome via
  `browser-actions/setup-chrome` rather than trusting the runner image's
  ambient contents.
- **Visitor-facing copy is never `product_ideas.rationale` verbatim.**
  Found 2026-07-26 that every single live page's subtitle read like an
  internal audit log ("Keyword implies users want to compute something
  quickly online.") because `landing_page_agent.py` displayed `rationale`
  directly. `agents.common.marketing_blurb()` now generates real,
  format-specific copy instead; `rationale` stays in the DB purely as an
  audit trail of why the agent picked an idea, never shown to a visitor.
- **`markdown_lite_to_html()` merges wrapped lines into one logical block
  before emitting a tag.** The original version classified each physical
  line independently, so a bullet or blockquote wrapped across multiple
  lines in the source (done for readable line lengths) broke into a `<li>`
  plus a stray sibling `<p>`, or several separate `<blockquote>` tags. This
  silently affected nearly every previously-published page. Fixed by
  buffering each block's text across lines and only flushing it to a tag
  once a blank line or a new block marker appears.
- **Not every product idea has to come from the automated keyword
  pipeline.** `product_ideas.target_keyword_id` is nullable and
  `keywords.sources_json` accepts a `"manual_research"` tag for exactly
  this: a genuinely researched, hyper-specific idea (see
  "EU Digital Seller Compliance Checklist") registered the same way an
  auto-discovered one would be, just without pretending a scraped signal
  drove it. `demand_score`/`latest_score` stay NULL for these - there's
  nothing to fake a number for.
- **`swipe_file` is a real format, not a repurposed one.** Ready-to-send
  scripts (a "swipe file" in copywriting terms) needed their own format
  string rather than being force-fit into `prompt_pack` (which implies AI
  prompts specifically) or `template` (which implies a spreadsheet).
  `content_agent.py` doesn't generate this format automatically yet - so
  far it's only used for manually-researched products (see "Freelance
  Scope Creep Defense Kit", "Resume Gap & Job Title Explainer Scripts") -
  but `landing_page_agent.py`'s renderer, `marketing_blurb()`, and
  `seo_agent.py`'s FAQ/schema all already support it the same as any
  other Markdown-based format.
- **IndexNow submission happens twice, deliberately.** `seo_agent.py`
  submits during the main pipeline run (before commit+push+deploy), which
  is fine for every run except the very first time the key file itself
  changes/appears - IndexNow needs to fetch `keyLocation` to verify
  ownership, and the key file isn't live at that point yet.
  `scripts/ping_indexnow.py` re-submits as a separate CI step *after*
  `actions/deploy-pages` succeeds, so there's always at least one
  submission per run guaranteed to hit an already-live key file. Google
  doesn't participate in IndexNow (no free instant-index API from Google
  exists) - only Search Console gets pages into Google specifically.
  **Update:** submissions now consistently return a 403
  `UserForbiddedToAccessSite` even with the key file confirmed live -
  suspected (unconfirmed) cause is Bing not trusting subdirectory
  `keyLocation` ownership proof on a shared multi-tenant domain like
  `*.github.io`, where we only control `/biznis/`, not the domain root.
  Other IndexNow users report the same unexplained error with no public
  fix. Left in place since it fails gracefully and costs nothing - see
  TASKBOARD.md.
- **`markdown_lite_to_html()` supports `**bold**`/`*italic*` inline
  emphasis**, added after shipping content that used it and getting
  literal asterisks on the live page. Applied via regex *after*
  `html.escape()` (so raw asterisks in prose are untouched by escaping,
  but the `<strong>`/`<em>` tags this inserts are real markup, not
  escaped text) - see `_inline_emphasis()` in `agents/common.py`.
- **One shared design system (`SITE_CSS` in `agents/common.py`) for every
  page**, including the calculator, which used to carry its own bespoke
  CSS. A single source of truth for colors/typography/spacing means a
  future redesign only touches one constant. Learned the hard way that
  changing `content_agent.py`'s calculator generator doesn't retroactively
  fix the *already-built* calculator file sitting in
  `data/exports/products/` - `content_agent.py` only writes a product file
  once, when the idea is first promoted, so an existing file needs a
  manual/explicit regeneration to pick up a generator change.
- **`service` is a format with no downloadable file.** Custom Website
  Design & Development and Custom Chatbot Development are real offerings,
  not automated digital products - `landing_page_agent.py` gives this
  format a contact CTA instead of a download link, and `seo_agent.py`
  marks it up as schema.org `Service` (no `Offer`/price, since work is
  custom-quoted, not fixed-price). The homepage renders services in a
  separate "Work with us" section above the free-product grid rather than
  mixing them into the same grid.
- **The service contact CTA never hardcodes a visible mailto as the only
  path.** A `mailto:` link always exposes the address in the page source
  to anyone (and every scraper). `FORMSPREE_ENDPOINT` (unset by default)
  switches `contact_form_html()` to a real `<form>` POSTing to Formspree's
  free tier instead - the endpoint is an opaque ID tied to the account,
  so the actual address never appears in the site's HTML at all. Falls
  back to the mailto CTA only until that's configured, so the site never
  breaks either way.
