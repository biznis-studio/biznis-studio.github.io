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

## In progress / next
- [ ] Decide: set up Cloudflare Web Analytics (needs your account) so
      Analytics Agent has real traffic data to read

## Backlog (see ROADMAP.md for detail and ordering rationale)
- [ ] Analytics Agent (blocked on Cloudflare account decision above)
- [ ] Conversion analysis + feedback loop back into demand scoring
- [ ] Write real prose for the remaining draft ebooks (productivity,
      xlsx, appium, gantt chart - see `products` table for status='draft')
- [ ] Affiliate links / newsletter platform (both need their own account,
      deferred behind proving out Gumroad first)

## Milestones
- **M1 — Discovery loop proven with real data** ✅ (iteration 1)
- **M2 — First real product file exists and is reviewable by the user** ✅ (iteration 2 — see `data/exports/products/`)
- **M2.5 — Pipeline runs autonomously on a schedule, not just locally** ✅ (iteration 5 — see the Actions tab on the repo)
- **M3 — First page published and receiving organic traffic** 🚧 (iteration 7 — deployed, traffic not yet measured)
- **M4 — First measured lead or sale attributed to the pipeline**
