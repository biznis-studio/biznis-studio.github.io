# Task Board

## Done (iteration 1)
- [x] Project scaffold, docs, `.gitignore`, `requirements.txt`
- [x] SQLite schema (`db/schema.sql`) covering the full intended loop
- [x] Market Research + Trend Agent (5 free, no-auth APIs)
- [x] Keyword Discovery Agent (n-gram extraction, per-source rank normalization)
- [x] Demand Scoring Agent (frequency/breadth/growth components)
- [x] Product Idea Generation Agent (rule-based format matching)
- [x] Orchestrator (`scripts/run_pipeline.py`) + JSON/CSV export
- [x] Dockerfile + docker-compose.yml
- [x] GitHub Actions workflow for a daily scheduled run (activated in iteration 5)
- [x] First real end-to-end run producing 12 product ideas from live data

## Done (iteration 2)
- [x] Filtered npm package-name artifacts out of product ideation (e.g.
      "@editorjs/checklist", "react-spreadsheet" aren't market topics)
- [x] Content/Template Agent: real files for calculator/checklist/template/
      prompt_pack, outline-only drafts for ebook/sop
- [x] Verified the generated calculator actually computes correctly and
      fixed a dark-mode contrast bug found during manual browser testing
- [x] Wired Content Agent into the orchestrator; report now includes each
      idea's product file path/status

## Done (iteration 3)
- [x] Competitor Analysis Agent (`agents/competitor_agent.py`): checks
      npm/GitHub/Stack Exchange/Wikipedia supply for the run's top 20
      keywords, bounded by GitHub's 10 req/min unauthenticated search limit
- [x] Demand Scoring Agent split into two passes; pass 2 re-blends the
      checked shortlist's score with a 25%-weighted opportunity component
- [x] Found and documented a real limitation: the competition signal
      saturates trivially (1.0) for generic single-word keywords like
      "checklist"/"calculator" since GitHub code-repo density isn't the
      same thing as consumer-content market saturation — logged in
      ROADMAP.md rather than presented as solved

## Done (iteration 4)
- [x] Niche Clustering Agent (`agents/niche_agent.py`): union-find over
      keywords that co-occurred in the same underlying signal
- [x] Verified the clustering + DB-insertion logic is correct with a
      synthetic co-occurring pair on a scratch DB copy
- [x] Confirmed 0 niches on the real run is an honest data-sparsity result
      (single-word keywords, ~230 signals/run), not a bug — documented in
      ROADMAP.md rather than papered over

## Done (iteration 5)
- [x] Installed GitHub CLI, authenticated, pushed repo to
      https://github.com/fwwk4pb868-afk/biznis (public)
- [x] Verified the scheduled Action end-to-end: manual `workflow_dispatch`
      run succeeded and the bot commit landed back on `main`
- [x] Decided: ebook/sop prose will be written using Claude directly by the
      user, not an automated Ollama/OpenRouter call — updated ROADMAP.md
- [x] Landing Page Agent (`agents/landing_page_agent.py`): real static
      pages under `site/` for "ready" products only; found and fixed a
      real bug (intro blurb rendering above the calculator's own title)
      during manual browser verification

## Done (iteration 6)
- [x] SEO Agent (`agents/seo_agent.py`): schema.org JSON-LD (no fake
      ratings/reviews - explicitly excluded per project rules), Open Graph
      tags, a genuine FAQ mirrored as FAQPage schema, internal "more free
      tools" links - injected idempotently via new `pages.seo_enhanced` column
- [x] Added a lightweight DB migration mechanism (`core/db.py::MIGRATIONS`)
      since `CREATE TABLE IF NOT EXISTS` doesn't add columns to existing tables
- [x] Found and fixed a real bug: HowTo step text was pulled from
      already-HTML-escaped page content, so JSON-LD literally contained
      `&quot;` instead of a real quote character
- [x] Deliberately did NOT build sitemap.xml/RSS yet - both assert "this is
      live at this URL", not true until `SITE_BASE_URL` is set at deploy time

## Done (iteration 7)
- [x] Chose GitHub Pages over Cloudflare Pages (no new account needed) and
      deployed `site/`: enabled Pages via `gh api ... build_type=workflow`,
      added a `deploy-pages` job to `pipeline.yml` using
      `actions/upload-pages-artifact` + `actions/deploy-pages`
- [x] Implemented `generate_sitemap`/`generate_rss` in `seo_agent.py`, now
      that `SITE_BASE_URL` is a real deployed URL - fixed a real bug along
      the way (RSS `pubDate` was ISO 8601, not the RFC-822 the spec requires)
- [x] Caught and fixed a second real bug: repeated manual testing (resetting
      `seo_enhanced` to re-test) had left `site/` pages with tripled
      JSON-LD/FAQ/link blocks - fully regenerated cleanly before committing
- [x] Verified locally end-to-end with `SITE_BASE_URL` set exactly as CI sets it

- [x] Triggered the deploy workflow and confirmed the site is live and
      working: https://fwwk4pb868-afk.github.io/biznis/ (checked the index,
      the calculator's interactivity, and sitemap.xml/feed.xml over HTTP)

## Done (iteration 8)
- [x] Wrote the first genuinely Claude-authored ebook: "The Practical Guide
      to Automation" (~1300 words, matches the site's Markdown-lite
      renderer's supported syntax), replacing its outline skeleton;
      promoted `products.id=3` to `status='ready'`
- [x] Rejected product idea #9 ("there way") - a garbage n-gram fragment
      from Stack Exchange text, not a real topic; a real gap in the n-gram
      stopword filter to revisit, not something worth writing content for
- [x] Found and fixed a real content-quality bug while reviewing the new
      page: the visible subtitle was showing product_agent's *internal*
      fallback rationale ("No specific format pattern matched...") instead
      of reader-facing copy - fixed the fallback string and backfilled all
      9 existing product_ideas rows that had the old text
- [x] Built + SEO-enhanced the new page, verified in-browser

## Done (iteration 9) — monetization infrastructure
- [x] User decided: Gumroad first (over affiliate links / newsletter), to
      generate actual profit rather than keep building free-only infra
- [x] Added `products.monetization_url` (nullable, via DB migration).
      `landing_page_agent.py`: when set, the CTA becomes "Get it on
      Gumroad" and the file stops being copied into `site/downloads/` -
      no point undermining a paid listing with a free copy next to it
- [x] Fixed `blurb_for()` to say "Paid" instead of always "Free" once a
      product is monetized - would've been a false claim otherwise
- [x] Tested the whole mechanism end-to-end with a placeholder Gumroad URL,
      confirmed the CTA/meta-description swap correctly, then reverted to
      the free state (no real listing exists yet)
- [ ] **Waiting on the user**: create a free Gumroad account, list one
      product, send the resulting URL - this system does not create
      payment/seller accounts on anyone's behalf

## Done (iteration 10) — PDF export
- [x] Found Gumroad's file picker won't accept `.md` uploads; built
      `agents/pdf_export.py` (shared by `landing_page_agent.py` and the new
      `scripts/export_pdf.py` CLI) rendering through the same Markdown-lite
      parser as the web page, then headless Chrome's `--print-to-pdf`
- [x] Refactored `markdown_lite_to_html` into `agents/common.py` so
      `landing_page_agent.py` and `pdf_export.py` could both use it without
      a circular import
- [x] ebook/sop downloads now serve a proper typeset PDF instead of raw
      `.md`; checklist/prompt_pack/template stay in their native format on
      purpose (their own copy tells the reader to paste/open them elsewhere)
- [x] Made this resilient for CI: wrapped each page build in try/except so
      one broken PDF export can't crash the whole daily run, and added
      `browser-actions/setup-chrome` to `pipeline.yml` rather than trusting
      the Ubuntu runner's ambient Chrome install
- [x] Generated `data/exports/products/0003-the-practical-guide-to-automation.pdf`
      for the user to upload to Gumroad directly

## Done (iteration 11) — first monetized product live 🎉
- [x] User created the Gumroad account and listed "The Practical Guide to
      Automation" (pay-what-you-want): https://jozefrusnak.gumroad.com/l/pcdkn
- [x] Set `products.monetization_url`, rebuilt the page - CTA now reads
      "Get it on Gumroad", meta description correctly says "Paid" not
      "Free", and the PDF is no longer also given away in `site/downloads/`
- [x] Verified in-browser: no duplicate JSON-LD, correct copy, link points
      to the real listing

## Done (iteration 12) — second real ebook while Stripe/KYC is pending
- [x] Wrote "The Practical Guide to Working with XLSX Files" (~1300 words),
      promoted `products.id=1` to `status='ready'` - free-to-download for
      now, ready to monetize the moment the user's Gumroad payout is set up
- [x] Found and fixed a real bug in my own draft: a bullet point ("Ignoring
      multiple sheets") was missing its "- " marker and had silently merged
      into the previous list item's paragraph - caught by reading the
      rendered page, not just the source Markdown
- [x] Fixed title casing ("XLSX" not "Xlsx") in both the DB and the PDF -
      added an optional `title` param to `pdf_export.export()` so it can
      use the real product title instead of deriving one from the filename
- [x] User was asked for a government ID by Stripe (standard KYC for
      payouts) and then asked to classify as company/sole trader/non-profit
      - flagged that Slovak law on when personal sales require a "živnosť"
      is outside what this system should decide, pointed to an "Individual"
      option and financnasprava.sk / an accountant for certainty

## Done (iteration 13) — replaced robotic copy with real marketing copy
- [x] Every live page's subtitle/meta description was showing
      `product_ideas.rationale` verbatim - an internal audit note, not
      marketing copy ("Keyword implies users want to compute something
      quickly online."). Added `agents.common.marketing_blurb()`: honest,
      format-specific, visitor-facing copy. `rationale` stays DB-only.
- [x] Fixed two more real bugs surfaced by this: keyword-equals-format-name
      echo ("A clear, repeatable checklist for Checklist") and acronym
      mangling ("Xlsx" instead of "XLSX")

## Done (iteration 14) — real market research, one original product, one critical bug fix
- [x] User pushback: stop writing more generic keyword-driven ebooks: "be
      original, do real research." Ran actual web research (not the
      internal keyword-scraping pipeline) on what digital products
      genuinely sell in 2026 - finding: hyper-specific audience+problem
      intersections outsell broad generic guides, which is exactly what
      our "Practical Guide to X" ebooks are *not*.
- [x] Built one genuinely original product from that research + this
      project's own lived experience: "EU Digital Seller Compliance
      Checklist" - the business-status/VAT/KYC confusion the user hit
      firsthand this session, generalized into an honest, appropriately-
      hedged orientation checklist (explicitly not tax/legal advice).
      Registered as a manually-curated product_idea (`source:
      manual_research`, not auto-scored) rather than faking a demand signal.
- [x] Found and fixed a real, previously-invisible rendering bug while
      reviewing that page: `markdown_lite_to_html()` classified every
      *physical* line independently, so a word-wrapped bullet point broke
      into a `<li>` plus a stray sibling `<p>`, and a wrapped blockquote
      split into several separate `<blockquote>` tags. This affected every
      previously-published page with a multi-line bullet or quote (i.e.
      almost all of them) - rewrote the renderer to merge wrapped lines
      into one logical block before emitting a tag, then rebuilt every page
      (and every ebook PDF, which shares the same renderer).

## Done (iteration 15) — diversified beyond ebooks, 3 more research-driven products
- [x] User: "don't focus only on ebooks, expand into other digital product
      types, pick based on demand, be original." Mined our own real
      signals_raw data (HN/Stack Exchange, not Wikipedia noise) for
      recurring, specific, well-defined pain points instead of generic
      single-keyword topics.
- [x] Found two genuinely recurring, validated signals: "My boss keeps
      changing the requirements" (Stack Exchange) and two separate
      questions about explaining resume gaps / inaccurate job titles.
      Cross-checked against 2026 market research on what non-ebook formats
      actually sell (templates, tested scripts - "swipe files" - over
      generic advice).
- [x] Shipped 3 new products, all free for now (ready to monetize once
      Stripe is sorted): **Freelance Scope Creep Defense Kit** (new
      `swipe_file` format - 7 ready-to-send scripts), **Change Request Log
      Template** (CSV, pairs with the kit above), **Resume Gap & Job Title
      Explainer Scripts** (`swipe_file`, written carefully to encourage
      honest self-description, never fabricating a title or gap reason)
- [x] Added `swipe_file` as a first-class format: marketing copy, generic-
      subject fallback, and FAQ entries alongside the existing formats
- [x] Verified all 3 pages render correctly, including that the
      previous session's blockquote/list-merging bug fix holds up under
      genuinely multi-script content (7 separate scripts, each one
      correctly merged into a single `<blockquote>`)

## In progress / next
- [ ] Decide: set up Cloudflare Web Analytics (needs your account) so
      Analytics Agent has real traffic data to read
- [ ] Google Search Console verification (paused mid-setup per user's request)

## Backlog (see ROADMAP.md for detail and ordering rationale)
- [ ] Analytics Agent (blocked on Cloudflare account decision above)
- [ ] Conversion analysis + feedback loop back into demand scoring
- [ ] Affiliate links / newsletter platform (both need their own account,
      deferred behind proving out Gumroad first)

## Done (iteration 16) — full quality audit across all 10 live pages
- [x] Systematically checked title/subtitle/schema/CTA on every single
      live page instead of only spot-checking the newest ones
- [x] Found and fixed a real bug: the download button read "Download
      swipe_file" - the raw internal format string, underscore visible -
      on both new swipe_file products. Added `DOWNLOAD_LABEL_BY_FORMAT` so
      button text is always real words ("scripts", "prompts"), not a
      format identifier.
- [x] Rebuilt and re-verified all 10 pages; confirmed the calculator's
      lack of a download button is correct by design (the tool itself is
      the deliverable), not a missed case

## Done (iteration 17) — real, no-account distribution: IndexNow
- [x] Checked actual Google indexing status (`site:` search) - confirmed
      0 pages indexed, as expected for a brand-new site with no Search
      Console/backlinks. Google itself doesn't support any free instant-
      index API - Search Console is still the only path there.
- [x] Found IndexNow: a genuinely free, no-account protocol supported by
      Bing/Yandex/Seznam/Naver/Yep - just a self-generated key file hosted
      at the site root proves ownership, then a plain HTTP POST asks them
      to (re)crawl specific URLs, usually within minutes instead of days.
- [x] Implemented in `agents/seo_agent.py` (`get_or_create_indexnow_key`,
      `submit_to_indexnow`) - persists the key in `db/indexnow_key.txt`
      (must survive `site/` being wiped and rebuilt every run) and submits
      the sitemap's URLs whenever `SITE_BASE_URL` is set.
- [x] Found and fixed a real ordering bug before shipping: the main
      pipeline run submits to IndexNow *before* commit+push+deploy, so the
      key file isn't live yet for them to verify ownership. Added
      `scripts/ping_indexnow.py` as a second, standalone re-ping that runs
      as a CI step *after* `actions/deploy-pages` succeeds, so the first
      real submission is guaranteed to hit a live key file.
- [x] Tested both paths locally against the real deployed site - both
      submissions returned `ok=True`.

## Milestones
- **M1 — Discovery loop proven with real data** ✅ (iteration 1)
- **M2 — First real product file exists and is reviewable by the user** ✅ (iteration 2 — see `data/exports/products/`)
- **M2.5 — Pipeline runs autonomously on a schedule, not just locally** ✅ (iteration 5 — see the Actions tab on the repo)
- **M3 — First page published and receiving organic traffic** 🚧 (iteration 7 — deployed, traffic not yet measured)
- **M4 — First measured lead or sale attributed to the pipeline**
