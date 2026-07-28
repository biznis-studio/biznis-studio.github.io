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
- [x] Done in iteration 11 below - account created, first product listed

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

## Human Action Batch — do these together, one sitting (updated 2026-07-27)

Per the Human Cost Analysis principle in ROADMAP.md: don't interrupt the
user once per blocker as each is discovered - collect every pending
manual action here, ranked by EBV unlocked, so they can be cleared in one
short session instead of several. Nothing below is urgent enough to
justify a separate interruption on its own; together they unlock most of
this system's near-term revenue potential.

**Corrected 2026-07-27 via an Opportunity Scan (Decision Journal D12):
item 2 below was previously (incorrectly) filed as blocking sales. Real
research shows Gumroad lets an account sell before Stripe verification
finishes - only the *payout* is delayed, not the sale. That means item 1
below was never actually blocked and is now the fastest lever to a first
sale, not item 2.**

1. ~~**List the 2 validated `core`-tier product bundles on Gumroad**~~ —
   **done 2026-07-27**: both bundles live and priced at $29 -
   [Scope Creep Kit + Change Request Log](https://jozefrusnak.gumroad.com/l/dtuqjc),
   [Retainer Renewal Kit + Tracker](https://jozefrusnak.gumroad.com/l/wztgr).
   `products.monetization_url`/`price_usd` wired for ids 19/20/22/23; a
   follow-up sales-readiness review then found and fixed a real bug
   (full paid content was viewable for free on the landing page) before
   flagging this fully complete - see iterations 36-39.
2. **[BLOCKED - payout only, not sales]** Gumroad Stripe KYC — no longer
   blocks listing or selling (see correction above), only delays actually
   receiving the money. Still worth finishing when convenient, no rush
   tied to item 1 above.
3. **[BLOCKED] Google Search Console verification** — ~3 min, still the
   highest-EBV distribution lever (unlocks Google discovery for all 14
   live pages, currently 0 confirmed indexed).
   - Go to search.google.com/search-console → Add property → **URL
     prefix** → `https://fwwk4pb868-afk.github.io/biznis/`
   - Choose the **HTML tag** verification method (not file upload/DNS)
   - Copy just the `content="..."` value from the tag it shows you
   - Send it here - it gets wired into `GOOGLE_SITE_VERIFICATION`, the
     site rebuilds, then click **Verify** in Search Console, then submit
     `https://fwwk4pb868-afk.github.io/biznis/sitemap.xml` as a sitemap
4. ~~**[BLOCKED] Formspree signup**~~ — **done 2026-07-27**: endpoint
   `https://formspree.io/f/xykrlrjz` wired into `FORMSPREE_ENDPOINT`
   (workflow env + rebuilt pages). Both service pages now use a real
   contact form - verified 0 occurrences of the email address in either
   page's source, form posts to the correct endpoint. The mailto fallback
   (reported as "doesn't work" - no default mail client on many browsers/
   devices) is gone.
5. **Optional, skip unless already in an account-setup mood**: Cloudflare
   Web Analytics - deliberately low priority (nothing to measure until
   distribution/traffic exists).

Send back whatever you've completed in one message when convenient - not
one-by-one - so this gets wired in as a single batch.

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
- [ ] **Update 2026-07-27: subsequent runs now consistently get a 403
      `UserForbiddedToAccessSite`**, even though the key file is
      confirmed live and byte-identical at its `keyLocation` URL
      (verified directly with curl). Researched this: other IndexNow
      users hit the same unexplained 403 with no clear public fix -
      Microsoft's own forum moderators tell people to contact Bing
      Webmaster Support directly for backend diagnostics, which this
      system can't do on the user's behalf. Suspected cause (unconfirmed):
      Bing's ownership verification may not trust a *subdirectory*
      `keyLocation` on a shared multi-tenant domain like `*.github.io`,
      where we only control the `/biznis/` project-site path, not the
      domain root - the docs say subdirectory `keyLocation` should work,
      but shared-hosting domains may be a special case. Left the
      integration in place (it already fails gracefully, no crash) rather
      than ripping it out - it may start working once Bing's systems
      process the host, and costs nothing while failing.

## Done (iteration 18) — validated priorities, repackaged the strongest bet, one more real bug
- [x] Deep research pass instead of more building: checked for actual
      *paid* competitors/price evidence per product, not just topic
      interest. Finding: **Scope Creep Kit + Change Request Log** is a
      real, existing paid category ($19-79, sits between expensive SaaS
      like FreshBooks/HoneyBook and DIY spreadsheets) - our strongest bet.
      **Resume Gap Scripts** sits in a space dominated by free content
      from major resume sites (AARP, ResumeGenius, career centers) with
      no clear evidence people pay for this specifically - repositioned
      as a free lead-magnet, not a monetization candidate.
- [x] Useful side-finding: Gumroad acts as EU "merchant of record" and
      already handles VAT itself - simplifies the user's own situation,
      and means the EU Compliance Checklist is most valuable for direct-
      Stripe sellers, less so for Gumroad-only sellers.
- [x] Repackaged the Scope Creep Kit as one cohesive "system" (scripts +
      log, explained together) instead of two separate unrelated free
      items - matches the "professionally packaged system" pattern the
      research found actually sells, ready to move to a fixed $19-29
      price the moment Gumroad payouts are working.
- [x] Found and fixed a real, systemic bug while writing that update: used
      `**bold**`/`*italic*` markdown, which `markdown_lite_to_html()`
      didn't support - would have shipped literal asterisks to readers
      (already had 2 pre-existing instances of this in older content).
      Added real `<strong>`/`<em>` inline emphasis support to the shared
      renderer and rebuilt every page and PDF.

## Done (iteration 19) — third product in the validated freelancer family
- [x] Researched durable (not fad) growth areas: confirmed freelance/gig
      economy is a structural, decade-long trend (72.9M US freelancers,
      15.79% CAGR, described as one of the biggest structural shifts in
      labor markets - not cyclical). Found renewal/expiration tracking is
      a proven *paid* category with real Etsy listings, though generic
      subscription trackers are somewhat crowded with free alternatives.
- [x] Combined both findings into a more specific, less crowded angle:
      **Client Retainer Renewal Kit** (8 scripts for the actual moments a
      freelance retainer needs renewing/renegotiating/ending) + a
      **Retainer Renewal Tracker** (CSV, pairs with it) - same proven
      "system" packaging as the Scope Creep Kit, extending the same
      validated freelancer product family instead of chasing a new,
      unrelated topic.
- [x] Free for now (ready to price once Gumroad payouts work); verified
      no markdown/rendering regressions before shipping

## Done (iteration 20) — full visual redesign + services offering
- [x] User feedback: design was "extremely bland and unprofessional."
      Built a real shared design system (`SITE_CSS` in `agents/common.py`):
      color palette with light/dark variants, gradient brand accents,
      card shadows/hover lift, a colored format badge per product type, a
      real site header/nav, and a favicon - used by every generated page
      (including the calculator, which previously had its own bespoke CSS).
- [x] Found and fixed a real bug while verifying: the *existing* calculator
      product file on disk was generated before this change and never
      gets regenerated automatically (content_agent.py only builds new
      products) - had to manually regenerate it to pick up the new styles.
- [x] Found and fixed a second real bug: every non-calculator page showed
      its title twice (once from the page shell, once from the markdown
      file's own leading "# Title" line, now stripped before rendering).
- [x] User then asked for "ultra-modern" design + a services offering:
      pushed the design further (gradient hero text, gradient buttons,
      subtle background gradients, section labels) and added a new
      `service` format for **Custom Website Design & Development** and
      **Custom Chatbot Development** - not downloadable products, so they
      get a "Get in touch" mailto CTA instead of a download link, a
      dedicated schema.org `Service` type, and a distinct "Work with us"
      section on the homepage above the free products grid.
- [x] Verified light mode, dark mode, the calculator's interactivity, and
      the Gumroad-monetized page all render correctly with the new system.
- [x] Note: the mailto CTA uses the site owner's real personal email,
      now publicly visible on the site - flagged to the user rather than
      assumed acceptable silently.

## Done (iteration 21) — real contact form, email hidden from page source
- [x] User: hide the email, use a real form instead. mailto: links always
      expose the address in the page source, so replaced them with a real
      `<form>` posting to Formspree (free, no email ever in our HTML - the
      form endpoint is an opaque ID tied to the account, not the address).
- [x] Added `FORMSPREE_ENDPOINT` env var (same progressive-enhancement
      pattern as `SITE_BASE_URL`/`GOOGLE_SITE_VERIFICATION`): falls back to
      the mailto CTA (which *does* expose the address) until it's set, so
      the site keeps working either way.
- [x] Also fixed the header's "Hire us" nav link, which was a mailto on
      *every* page - now points to the homepage's services section instead.
- [x] Verified: with the endpoint set, zero occurrences of the email
      address anywhere in the generated HTML; without it, exactly one
      (the fallback mailto), confirming the toggle works both ways.
- [ ] Folded into the consolidated "Human Action Batch" above rather than
      asked for separately - see the "In progress / next" section.

## Done (iteration 22) — product tiering + retired the generic-ebook fallback
- [x] Added `products.tier` column (`core`/`lead_magnet`/`retire_candidate`)
      and classified all 28 products against this session's real
      demand-validation research (iterations 14/18/19), instead of leaving
      that judgment implicit in doc prose only. Result: 7 core, 7 lead
      magnet, 14 retire_candidate.
- [x] Confirmed (via the `pages` table) that all 14 retire_candidate
      products were still `status='draft'` with zero live pages - no site
      cleanup needed, just correcting the data to reflect reality. Set their
      `product_ideas.status = 'rejected'`.
- [x] Retired `product_agent.py`'s generic-ebook fallback at the source:
      `pick_format()` no longer invents "The Practical Guide to {term}" for
      unmatched keywords - it returns `None` and `run()` skips them. This is
      the exact mechanism that produced all 14 retire_candidate products, so
      fixing the doc/data without also fixing this would have let the same
      clutter regenerate on the next scheduled run.
- [x] Updated ROADMAP.md with the full rationale so this isn't just a silent
      data change.

## Done (iteration 23) — reframed strategy as enterprise-value optimization
- [x] User feedback: stop framing this as "build a website"/"build products"/
      literal Departments - the real objective is maximizing long-term
      enterprise value, with strategy freely replaceable as data changes.
      Confirmed the codebase already never built literal departments
      (grepped - none exist); formalized the correct instinct as a durable
      written principle instead of leaving it implicit.
- [x] Added "Operating principle" section to ROADMAP.md: Capabilities/
      Decision Engines terminology (not Departments), an Expected Business
      Value framework for ranking backlog items before building, and an
      honest Company Assets inventory (knowledge base: 4,408 signals/85
      keywords; reusable code/design system; 14 ready tiered products; 2
      service capabilities) that explicitly does NOT claim assets that
      don't exist yet (no email list, no audience/community, no affiliate
      network).
- [x] Applied the EBV framework live to today's real backlog: ranked
      distribution (0 pages confirmed indexed, IndexNow still 403) above
      Gumroad monetization, above Analytics, above more content - the
      product catalog is not the current constraint, discovery is.
- [x] Saved this reframing as a durable cross-session memory
      (`feedback_enterprise_value_framing.md`) so it survives context
      compaction and future sessions apply it from the start.

## Done (iteration 24) — Strategic Review mechanism + first review
- [x] User refinement: tactical EBV-ranking alone still risks getting
      "stuck" optimizing the current implementation forever without ever
      questioning whether the business model itself is still the best bet.
      Added a distinct, higher-level **Strategic Review** process
      (`docs/STRATEGIC_REVIEWS.md`): 10 fixed questions, minimum weekly,
      answered with real data, explicit willingness to recommend a pivot.
- [x] Ran the first real Strategic Review using actual project data (19
      runs, 85 keywords, 28 products/7-7-14 tier split, 0 confirmed
      Google-indexed pages, 0 confirmed sales, 2 service pages with zero
      leads/case studies). Honest findings: the product research is
      sound, but the real systemic bottleneck is that nearly every
      high-leverage growth lever is gated behind human-only account setup
      (Search Console, Gumroad KYC, Formspree) that this system cannot do
      on the user's behalf - flagged two follow-up decisions for the user
      (Gumroad KYC vs. a lower-friction fallback; splitting services onto
      their own trust-building track) rather than silently building more.
      No pivot away from the current product line - explicitly said so,
      since a Strategic Review has to be willing to say "no change needed"
      too, not manufacture a pivot for its own sake.
- [x] Documented the honest automation limit: a script can assemble the
      data a review needs, but the judgment in questions 1-10 needs an
      actual reasoning pass (same human-in-the-loop constraint already
      documented for ebook prose - no LLM key wired into the scheduled
      pipeline) - so this runs whenever a Claude Code session next touches
      the project, triggered by the log's last dated entry being >1 week
      old, not as an unattended cron job.

## Done (iteration 25) — Human Cost Analysis, stopped interrupting one blocker at a time
- [x] User feedback: I asked for the Search Console verification token in
      isolation right after finishing the Strategic Review, when the
      actual bottleneck list also includes Gumroad KYC and Formspree -
      exactly the "acting as implementer, not CEO" failure mode being
      corrected. Added two durable principles to ROADMAP.md: Human Cost
      Analysis before requesting any manual action (weigh time/cognitive
      load/failure risk against EBV unlocked before asking), and "human
      attention is the primary bottleneck, protect it aggressively."
- [x] Consolidated 3 previously-scattered "waiting on the user" asks
      (Search Console, Gumroad KYC, Formspree) into one ranked "Human
      Action Batch" in this file - each with exact steps, time estimate,
      and EBV unlocked - meant to be cleared together in one sitting
      instead of three separate interruptions. Marked the stale Gumroad
      "waiting on user" bullet from iteration 9 as done (superseded by
      iteration 11) rather than leaving contradictory open items in the doc.
- [x] Saved this as a durable cross-session memory alongside the EBV/
      Strategic Review feedback, so future sessions batch manual asks by
      default instead of re-learning this the same way.

## Done (iteration 26) — management layer: constraints + decision journal
- [x] User's natural next step after EBV/Strategic Review/Human Cost
      Analysis: the project still lacked a mechanism to (a) name the one
      real bottleneck at a time instead of a backlog of problems, and (b)
      remember *why* past strategic calls were made instead of relying on
      conversation history that doesn't survive a context reset.
- [x] Added `docs/CONSTRAINT_LOG.md` (Constraint-Driven Management):
      names the single current constraint per iteration with evidence,
      EBV if removed, cost to remove, confidence, and alternatives
      considered/rejected. First real entry: distribution/discovery (0
      confirmed Google-indexed pages) is the current constraint, not
      product quality or analytics.
- [x] Added `docs/DECISION_JOURNAL.md`, populated retroactively with the
      9 real strategic decisions made so far this project (Gumroad choice,
      GitHub Pages choice, IndexNow adoption, ebook-diversification pivot,
      product tiering, services offering, Formspree, resuming Search
      Console, adopting this whole operating-principle layer) - each with
      reasoning, assumptions, rejected alternatives, validation metrics,
      and a review date, so future sessions revisit decisions on evidence
      instead of silently drifting.
- [x] Added "CEO Mode" framing to ROADMAP.md: success is measured by
      decision quality, not work volume - a quiet iteration that correctly
      builds nothing can be the right call.
- [x] Updated the durable cross-session memory with all three new
      mechanisms so they persist past this session.

## Done (iteration 27) — Blocked Task Policy, then proved it with real unblocked work
- [x] User feedback: 3 blocked human-only tasks (Search Console, Gumroad
      KYC, Formspree) are a genuine limit (login/KYC/payment - no prompt
      changes that), but the correct response is never to end a turn
      idle waiting on them. Added the Blocked Task Policy to ROADMAP.md:
      mark blocked items BLOCKED with EBV, surface once (not every turn),
      and immediately pull the next-highest-EBV unblocked task. Marked
      all 3 items `[BLOCKED]` in the Human Action Batch instead of a bare
      "waiting" list.
- [x] Added an honest note on the user's proposed CEO/Research/
      Engineering/Growth/Review multi-agent architecture: this session is
      one sequential agent, not literally parallel processes - the `Agent`
      tool (real background subagents) and scheduled/cron sessions are
      the two real mechanisms available for genuine parallelism, to be
      used for actual independent work, not simulated as role-labeled
      decoration.
  - [x] Immediately proved the policy with two real unblocked fixes found
      via a genuine crawl-readiness audit (title/meta description length/
      canonical/JSON-LD validity/broken internal links) across all 14 live
      pages: (1) added `robots.txt` with an explicit `Sitemap:` directive -
      a real, account-free discovery lever distinct from Search Console/
      IndexNow, since well-behaved crawlers check it unprompted; (2) found
      and fixed a real gap - the homepage (the single most important URL
      on the site) never passed through `seo_agent.py`'s per-product
      `inject()` step, so it had zero canonical link and zero Open Graph
      tags while every product page had them. Fixed in `page_shell()`
      directly. Verified both locally with `SITE_BASE_URL` set exactly as
      CI sets it, and re-ran the audit clean (0 issues) after the fix.

## Done (iteration 28) — more unblocked work: n-gram stopword fix
- [x] Continued straight from iteration 27's Blocked Task Policy proof
      with another real, unblocked fix instead of stopping: the
      long-documented "there way" n-gram bug (a Stack Exchange title
      fragment that survived keyword extraction and had to be manually
      rejected in iteration 8) is now actually filtered - added
      `there/here/some/any/such/other/another/same` to `STOPWORDS` in
      `agents/keyword_agent.py`, after checking it against every existing
      keyword for collisions (only the already-rejected "there way"
      matched).
- [x] Verified with real function calls: "is there a way to do something"
      now correctly extracts zero keywords; unrelated real phrases
      ("checklist template", "template for freelancers") still extract
      correctly - no false-positive filtering introduced.
- [x] Documented the fix honestly in ROADMAP.md as *partial*: the
      underlying filter only checks a window's first/last word, not the
      middle, so a fragment like "explain there way" (stopword in the
      middle) can still slip through - flagged as a real remaining gap
      rather than claiming it's fully solved.

## Done (iteration 29) — Autonomy Policy, Opportunity Queue, OS reframe
- [x] User feedback: ending the last turn with "if you want me to
      actually wire this in, say so" is exactly the kind of permission-
      seeking an autonomous system shouldn't do by default. Added an
      **Autonomy Policy** to ROADMAP.md: act by default, only ask first
      when an action needs credentials/payment/legal identity/external
      approval, is irreversible, exceeds a sane cost, carries real legal/
      security risk, or confidence is genuinely low.
- [x] Added **docs/OPPORTUNITY_QUEUE.md** - a real, standing, ranked list
      of executable work across engineering/business/growth/experiments/
      automation, each with EBV/cost/confidence/dependencies/human-
      involvement, so finishing one task always has a next one queued.
      Deliberately deviated from the proposed fixed "100 per category"
      quota and said so explicitly in ROADMAP.md: at this project's real
      current scale (85 keywords, 28 products), 500 items would mostly be
      padding - the actual rule that matters (never let the queue go
      empty; refill via research when a category runs low) is preserved
      exactly as proposed.
- [x] Reframed the project in ROADMAP.md as an **AI Operating System**,
      not a project that finishes: the main loop is Observe -> Learn ->
      Decide -> Execute -> Measure -> Learn -> Reprioritize -> repeat,
      mapping each existing doc (Constraint Log, Decision Journal,
      Opportunity Queue, Strategic Reviews) to a step in that loop.
- [x] Proved the Autonomy Policy immediately rather than just writing it:
      found and fixed a third real crawl-readiness gap (feed.xml existed
      since iteration 7 but no page ever linked to it - crawlers/RSS
      readers had no way to discover it), patched all 14 existing static
      product pages plus the homepage template, then turned the whole
      ad-hoc audit script into a real repo asset (`scripts/audit_site.py`)
      wired into `pipeline.yml` as a (currently non-fatal) CI check -
      pulled directly from the new Opportunity Queue's automation
      category instead of leaving it as a one-off.

## Done (iteration 30) — external second opinion (ChatGPT), critically evaluated
- [x] At the user's request, explained the full system to ChatGPT (via
      the user's own Chrome/Claude-in-Chrome session) and asked for
      independent optimization suggestions, not confirmation.
- [x] Critically evaluated the response rather than importing it
      wholesale (full reasoning in Decision Journal D10). Adopted as
      genuinely new: a **Customer Discovery Layer** (HN comments, Stack
      Exchange comments, GitHub Issues, Reddit - scoped by what's
      actually free/no-auth vs. account-gated), an **Expected Learning
      Value** axis alongside EBV, a **Kill Switch** rule for retiring
      underperforming *published* products (not just unbuilt ideas), and
      an 11th Strategic Review question ("if Google stopped sending
      traffic tomorrow, would this survive?").
- [x] Explicitly rejected the claim that Competition/Demand/Niche scoring
      is "engineering comfort" that doesn't move revenue - it directly
      produced this session's tiering decision (D5), so the claim didn't
      match the evidence. Logged the pushback rather than silently
      complying with or silently ignoring an external opinion.
- [x] Found and fixed one genuinely free, unblocked distribution gap the
      consultation surfaced: the public GitHub repo had no `homepageUrl`
      and zero topics set. Fixed immediately via `gh repo edit`.

## Done (iteration 31) — stop writing docs, build a real Company Scoreboard
- [x] Direct user feedback: enough principle documents exist now; more
      markdown risks becoming the over-engineering this whole layer was
      meant to prevent. Real gap was a queryable, trending record of
      actual business state - not another policy file.
- [x] Added `company_metrics` (one real snapshot per run) and
      `experiments` (structure only, deliberately unused until there's
      real traffic to test against - see ROADMAP.md) tables to the schema.
- [x] Built `agents/scoreboard_agent.py`: computes real counts (products/
      tiers/pages/keywords/monetized count/confirmed revenue/experiment
      counts) from the DB every run, inserts a snapshot, and generates
      docs/COMPANY_SCOREBOARD.md - a real data artifact, not hand-written
      prose. Deliberately excludes Development Cost/Maintenance Cost/
      Estimated Future Value fields rather than inventing dollar figures
      for a project with no metered agent-time cost - documented as
      "Not tracked (deliberately, not by oversight)" directly in the
      generated file.
- [x] Wired into `scripts/run_pipeline.py` (runs automatically every
      scheduled iteration from now on) and verified end-to-end with a
      real full local pipeline run (run_id=20) - confirmed the scoreboard
      reflects real data (28 products, 86 keywords, 4,640 signals, 0
      confirmed revenue) and that `product_agent.py`'s retired ebook
      fallback correctly produced 0 new generic ideas on real live data.
- [x] Recorded the phase shift explicitly in ROADMAP.md and Decision
      Journal D11: judge future work by whether it produces new
      knowledge, creates measurable value, or saves the human real work -
      not by whether it adds another layer of process.

## Done (iteration 32) — North Star metrics + Company Assets portfolio, then a hard stop on governance work
- [x] Extended the scoreboard (not a new doc) per user feedback: leads
      with 5 North Star metrics (Revenue Today/30d, Qualified Leads, CAC,
      EBV - honestly ~0 right now) and a Company Assets Portfolio table
      (5 real assets: Knowledge Base, Product Catalog, Distribution
      Surface, Reusable Code/Design System, Service Capability), each
      with real owner/value/automation fields - no fabricated dollar
      figures or fake assets. Old counts demoted to a clearly-labeled
      "diagnostic metrics" section.
- [x] User's explicit 30-day directive recorded in ROADMAP.md: no new
      governance layers - every change must either raise the probability
      of the first paying customer or cut the time to get one. This is
      the last change to the measurement layer for now.

## Done (iteration 33) — Opportunity Scan caught a real wrong assumption
- [x] User correction: proceeding straight to "research Ko-fi" without
      re-scanning violated this project's own "never assume the current
      plan is optimal" principle. Added a final rule (ROADMAP.md):
      Opportunity Scan before any major initiative - re-rank against
      EBV/Learning Value/time-to-first-customer/human cost, proceed only
      if the plan still wins.
- [x] Ran the scan for real: verified via web research that Gumroad lets
      an account sell before Stripe verification completes - only the
      payout is delayed, not the sale. This means the 2 validated
      freelancer-system bundles were never actually blocked from being
      listed - they were just mis-filed as blocked (corrected in
      Decision Journal D1/D12).
  - [x] Ko-fi correspondingly deprioritized - it would have solved a
      problem that doesn't exist.
- [x] Generated the missing Gumroad-ready PDFs for both swipe_file
      products (0019, 0022) so the human only has to upload + price, not
      also convert files - reduces the remaining human effort to list
      both bundles today.
- [x] Set the single 30-day KPI in ROADMAP.md: get the first paying
      customer, minimal human involvement - no more agents/docs/rules/
      architecture unless that doesn't happen in 30 days.

## Done (iteration 34) — evidence discipline + mission refined, no new files
- [x] User feedback: "webový výskum ukázal" isn't enough - strategic
      claims need a source, verification date, confidence level, what
      they disproved, and a re-verify trigger, since SaaS platform rules
      change. Added this directly into Decision Journal D12 (existing
      file, not a new one): cited Gumroad's own Help Center articles
      specifically, marked confidence Medium (not yet confirmed by an
      actual listing attempt), and set the re-verify trigger to "when the
      user actually tries listing" or 6 months, whichever first.
- [x] Mission refined in ROADMAP.md: not "first paying customer" (could
      be luck) but **Repeatable Customer Acquisition** - a second, third,
      and tenth customer via the same process is what makes this a
      business. New one-sentence commit test: does this increase the
      probability of, or decrease the cost of, acquiring the *next*
      customer? If not, don't commit it.
- [x] Explicit instruction followed: no new markdown/journal/log/
      dashboard/manifest this iteration - both changes above are edits to
      already-existing files.

## Done (iteration 35) — Phase 1 (sellable assets), found and fixed a real pre-launch bug
- [x] User's single priority: make the 2 best products actually sellable
      this week (their Fáza 1). Audited the real gaps against a
      buy-ready checklist instead of assuming the pages were fine.
- [x] Found a real bug that would have shipped: the FAQ on every
      swipe_file/template/checklist/calculator/prompt_pack page has a
      static "Is this free? Yes" answer baked in at first build time.
      `seo_agent.py`'s injection is one-time (gated by `pages.seo_enhanced`)
      and never re-runs, so this would have kept telling a paying
      customer "yes, it's free" right next to a Gumroad "Buy" button the
      moment either bundle got priced. Fixed `faq_block()` to answer this
      question dynamically from `monetization_url`, and added
      `refresh_faq_for_page()` so re-patching an already-built page after
      it gets priced is a one-line call, not a manual edit - tested
      end-to-end (simulated monetized -> correct answer -> reverted
      cleanly, confirmed via `git diff` that the real site files are
      untouched).
- [x] Added a real, honest license/usage-terms line ("personal & business
      use, don't resell the files") to the CTA shown once a product is
      priced - a real Phase-1 checklist item (buyer trust/clarity) that
      was simply missing before.
- [x] Commit test applied throughout: does this increase the probability
      of, or decrease the cost of, acquiring the next customer? Both
      changes pass directly - a contradictory FAQ or missing license
      terms are exactly the kind of friction that costs a sale.

## Done (iteration 36) — both validated bundles live on Gumroad, priced $29
- [x] User listed both bundles: Scope Creep Kit + Change Request Log at
      https://jozefrusnak.gumroad.com/l/dtuqjc, Retainer Renewal Kit +
      Tracker at https://jozefrusnak.gumroad.com/l/wztgr, both $29.
      Wired `products.monetization_url` for all 4 underlying product rows
      (19, 20, 22, 23).
- [x] Found and fixed a real bug in my own process while rebuilding the
      pages: calling `landing_page_agent.build_page()` directly on an
      already-published page resets it to pre-SEO-enhancement state
      (wipes canonical link, schema.org JSON-LD, and the FAQ block seo_
      agent.py had injected) - `run()` only ever builds pages that don't
      exist yet, it doesn't know how to safely refresh an existing one.
      Fixed by resetting `pages.seo_enhanced = 0` for the 4 affected pages
      and re-running `seo_agent.run()`, which correctly re-injected
      everything with the new dynamic (paid) FAQ answer built in.
- [x] Also fixed a real bug in `refresh_faq_for_page()` itself: it
      returned `True` even when its regex replaced nothing, which is
      exactly what silently happened here and is what surfaced the bug
      above - now uses `re.subn` and returns `False` if either
      replacement didn't actually match.
- [x] Removed the 4 now-stale free download files from `site/downloads/`
      - confirmed nothing still linked to them first. Leaving them up
      would have undermined the new paid listings by giving the same
      files away for free right next to them.
- [x] Verified clean with `scripts/audit_site.py` (0 issues) and manual
      checks: exactly one FAQPage schema and one canonical link per page,
      correct "No - it's a one-time purchase..." FAQ answer, "Get it on
      Gumroad" CTA, and the license-terms line all present on all 4 pages.
- [x] Refreshed `docs/COMPANY_SCOREBOARD.md` - `monetized_products` now
      correctly reads 5 (product #3 from iteration 11 + these 4).

## Done (iteration 37) — sales-readiness review found the single biggest conversion killer
- [x] User asked for a full marketing/design/content review of the now-
      live paid products. Found the single most important issue possible:
      **the entire paid product (all 7-8 scripts, word for word) was
      shown in full on the free landing page** - a visitor never needed
      to pay, just copy the text from the browser. The CSV templates were
      fine (only 2 example rows preview, not the full deliverable).
- [x] Fixed with `gate_swipe_file_preview()` in `landing_page_agent.py`:
      script #1 stays fully visible as a genuine proof-of-quality sample
      (honest, not a fake teaser), scripts 2+ keep their heading and
      "use this when" guidance (real, valuable context) but the actual
      wording is replaced with a locked placeholder pointing to the
      Gumroad link. Applied only when `monetization_url` is set - the
      still-free Resume Gap Scripts swipe_file is untouched.
- [x] Also found the page never showed a price anywhere - a visitor had
      to click through to Gumroad just to find out the cost. Added a
      real `products.price_usd` column (user-set, never estimated) and
      display it directly in the CTA ("Get it on Gumroad - $29"), plus a
      short trust line ("Instant digital download - pay once...").
- [x] Verified end-to-end with `scripts/audit_site.py` (0 issues) and
      manual inspection: exactly one full script + N locked placeholders
      per page, price shown, license/trust copy present, FAQ still
      correctly paid-aware.
- [x] Triggered a manual deployment (`gh workflow run`) since GitHub
      Pages only redeploys when the scheduled/dispatched workflow runs,
      not on every `git push` - otherwise these fixes would have sat
      un-deployed until tomorrow's cron.
- [x] Checked the live homepage in-browser and found a second real issue:
      both paid bundles sat undistinguished inside the "Free products"
      grid, no price shown anywhere on the card - a visitor browsing
      "free products" would click through expecting a free download and
      hit a paywall, which damages trust rather than helping conversion.
      Fixed: homepage now splits into "Get the full system" (paid, with a
      green `$29` price badge on each card) and "Free products" (only
      rendered as a paid section when something is actually for sale, so
      it doesn't misrepresent state before any product was priced).
      Updated the hero copy and nav link ("Free products" -> "Products")
      site-wide to match, since the site is no longer free-only.

## Done (iteration 38) — second full review + second ChatGPT consultation
- [x] Full live audit of homepage, both paid products, both service pages,
      mobile/desktop, light/dark mode - everything from the previous
      iteration confirmed working correctly (gating, price, FAQ,
      Formspree form, mobile nav).
- [x] Consulted ChatGPT again with an update on what changed. It confirmed
      the previous fixes were real conversion blockers (especially the
      full-content giveaway), then raised new, genuinely different points:
      no creator trust/credibility signal anywhere on a $29 page, no
      explicit answer to "why not just ask an AI for this," no "who this
      isn't for" framing on the product pages (already existed on service
      pages, but not products).
- [x] Verified Gumroad's refund policy is seller-configurable (not a
      fixed guarantee) before considering mentioning one - decided not to
      claim a specific refund policy since it isn't verified what the
      account is actually set to; avoided fabricating a claim.
- [x] Added real, honest fixes to both paid kits (`0019`/`0022` source +
      rebuilt pages): a "Why not just ask an AI?" section (honest answer:
      you're paying for the decision-making, not the wording), a "Who
      this isn't for" section (matches the pattern already used on
      service pages), and a code-level "Who makes this" trust note shown
      on every monetized page (no fake bio/testimonials - points to the
      public repo as real transparency).
- [x] Verified clean with `scripts/audit_site.py` and confirmed the
      content gating from the previous iteration survived the rebuild.

## Done (iteration 39) — same content-giveaway bug found on the first monetized product too
- [x] After fixing the giveaway issue on the 2 new bundles, checked
      whether the *first* monetized product (the pay-what-you-want
      automation ebook, live since iteration 11) had the same problem -
      it did: the full ~1300-word ebook was readable in its entirety
      above the "Get it on Gumroad" button, undermining even a voluntary
      tip.
- [x] Added `gate_ebook_preview()`: keeps the first 2 sections in full (a
      genuine, substantial preview), keeps every later heading visible as
      a real table of contents, replaces later section bodies with a
      locked placeholder. Applied only when `monetization_url` is set.
- [x] Rebuilt the page with the same safe process (reset seo_enhanced,
      re-run seo_agent) and verified clean with `scripts/audit_site.py`.

## Done (iteration 40) — full system health check, cleaned up stale data/docs
- [x] Systematic verification per user request: syntax-checked every
      Python file, confirmed the last 8 scheduled/dispatched pipeline
      runs all succeeded (both jobs), confirmed no new generic ebook
      ideas have appeared since the fallback fix, confirmed DB/site
      consistency (no orphaned pages, no missing files, no duplicates),
      re-ran `scripts/audit_site.py` clean, verified every sitemap URL
      returns 200, spot-checked the 4 previously-unaudited page formats
      (checklist/calculator/template/EU-checklist) render correctly.
- [x] Found and fixed 3 real imperfections:
      1. A stray manual-test row (`run_id IS NULL`) had leaked into
         `company_metrics` despite earlier cleanup attempts - removed it
         and regenerated `docs/COMPANY_SCOREBOARD.md` from the clean,
         all-real history (7 genuine snapshots).
      2. TASKBOARD's Human Action Batch still listed "list the 2 bundles
         on Gumroad" as an open, actionable item days after it was
         actually completed - marked done with the real listing URLs.
      3. ROADMAP's EBV-ranked list still said Gumroad monetization was
         "blocked on Stripe KYC" - stale given the later Decision Journal
         D12 correction (sales were never blocked, only payout) and the
         listings already being live - updated to reflect reality and
         pointed out Gumroad's own dashboard as a zero-build-cost source
         of view/click data while Analytics stays deprioritized.

## Done (iteration 41) — Gumroad cover images generated
- [x] User (or a tool with Gumroad dashboard access relayed by the user)
      reported 0 sales across all 3 listings and flagged 2 real gaps: a
      duplicate unpublished Retainer Kit listing (this system never
      created a second one - only one URL, `wztgr`, is registered; the
      duplicate must have been created directly on Gumroad, so deleting
      it is the user's own call on their own account, not something to
      authorize from here) and missing cover images/thumbnails on all
      products.
- [x] Generated real 1280x720 cover images (Gumroad's own recommended
      size) for all 3 monetized listings, reusing the actual site's brand
      colors/gradient/badge styling from `agents/common.py` - not stock
      photos or fabricated product shots, the same honest visual identity
      already used everywhere else on the site:
      `data/exports/products/0019-freelance-scope-creep-defense-kit-cover.png`,
      `0022-client-retainer-renewal-kit-cover.png`,
      `0003-the-practical-guide-to-automation-cover.png`.
- [x] Did not attempt to log into or modify anything on Gumroad directly -
      no access, and deleting a listing is the user's own irreversible
      call on their own account.

## Done (iteration 42) — logged into Gumroad (user's own Chrome), real listing edits
- [x] User authorized using their own logged-in Chrome session to help
      directly. Verified the earlier reported 0-sales/duplicate-listing
      data against the real dashboard - matched exactly.
- [x] Explicitly declined to delete the duplicate unpublished listing
      (`xhswr`) even with authorization - permanently deleting data is a
      hard rule, not a trust judgment call, regardless of who asks or how
      clearly. Told the user this needs to be their own action.
- [x] File upload for the cover images hit a real tool limitation: the
      automation can only upload files the user has directly shared as a
      chat attachment, not files this system generated itself on disk -
      confirmed this rather than silently giving up, including after the
      user re-shared the images in chat (still didn't resolve the
      restriction, since there was no way to recover a usable file path
      from the shared images either).
- [x] While in the editor, made real, free improvements that don't need
      file upload: filled in "Summary" and "Additional details"
      (Format/Delivery/License) on all 3 listings, removed a broken empty
      "Pages" detail row on the ebook listing, and confirmed content
      delivery (PDF+CSV) is correctly bundled on both kits. Noticed
      Gumroad already shows a "30-day money back guarantee" badge
      automatically - addresses a risk-reduction point from the ChatGPT
      review without any action needed.
- [x] Generated a second set of images - square 1080x1080 thumbnails
      (Gumroad's Library/Discover/Profile format, different aspect ratio
      than the 1280x720 Cover) - and sent both sets to the user with
      exact per-product upload instructions.
- [x] User uploaded both image sets themselves. Verified on both the
      Gumroad edit view and the real public listing pages (not just the
      editor preview) for all 3 products - all covers display correctly,
      professional and on-brand.
- [x] Flagged (not decided) the "Mark product as e-publication for VAT
      purposes" toggle - a real tax/legal classification question outside
      what this system should decide for the user.

## Done (iteration 43) — cross-sell upsells live, tightened both Gumroad descriptions
- [x] User relayed 6 suggestions from Gumroad's own "Agent" feature
      (bundling, cross-sell upsell, PWYW pricing, discount code, emailing
      the list, tightening descriptions). Evaluated each on merit rather
      than adopting wholesale: agreed cross-sell upsell and tightening
      descriptions were genuinely valuable and low-risk; asked the user
      directly (pricing/discount are their call, not something to decide
      unilaterally) - answered "leave pricing for later" and "not a
      discount code for now," so neither was touched; deprioritized
      bundling pending real per-product sales data; declined to
      auto-send marketing emails on the user's behalf (offered to draft
      copy for their own review instead, not yet requested).
- [x] Created both directions of a Gumroad checkout Upsell (Checkout →
      Upsells, via the user's own logged-in Chrome session): buying
      Freelance Scope Creep Defense Kit offers Client Retainer Renewal
      Kit, and buying Client Retainer Renewal Kit offers Freelance Scope
      Creep Defense Kit. No discount attached to either offer, matching
      the user's "not now" answer on discounts. Verified both show
      "Live" with correct trigger/offer pairing in the Upsells list.
- [x] Found a real, concrete content gap while reviewing the Gumroad
      listing descriptions against the website copy: both product pages
      on the site already had a "Why not just ask an AI?" and a "Who
      this isn't for" section (added in iteration 38's ChatGPT-review
      pass), but the Gumroad *listing* descriptions - what buyers
      actually see before purchase - never got the same sections, since
      that description is its own separate rich-text field, not a copy
      of the site page. Added both sections (adapted to Gumroad's
      shorter, condensed style) to both listings and saved. Verified
      live on the real public listing page for the Scope Creep Kit,
      confirming the new copy renders correctly.

## Done (iteration 44) — real og:image, every page had a blank link-preview until now
- [x] User asked "čo ďalej?" (what's next). Per the Autonomy Policy, acted
      directly on the next-highest-EBV unblocked item from
      `docs/OPPORTUNITY_QUEUE.md` (Growth #2) instead of asking - Search
      Console (the single highest-EBV lever per `docs/CONSTRAINT_LOG.md`)
      is still blocked on ~3 min of the user's own time, so surfaced it
      once (see Human Action Batch item 3, unchanged) and moved to real
      unblocked work in the same turn rather than ending idle.
- [x] Found a real, concrete gap: every one of the 15 live pages had
      `og:title`/`og:description` but no `og:image` - sharing any link
      (Gumroad "share" buttons, social, forums, Slack/Discord previews)
      rendered a blank/generic card instead of a real preview, which
      hurts click-through on every distribution channel at once, not
      just search.
- [x] Generated one honest, site-wide branded share image (1200x630,
      headless Chrome, same brand gradient as the product cover images -
      not a fabricated product photo, since none exists) -
      `site/assets/og-image.png`. Wired `og:image`/`og:image:width`/
      `og:image:height`/`twitter:card`/`twitter:image` into both
      `landing_page_agent.py` (homepage) and `seo_agent.py` (product
      pages) so every future page build includes it automatically.
- [x] Backfilled all 14 already-published pages + the homepage with a
      targeted idempotent insert (checked for `og:image` already present,
      inserted once before `</head>`) rather than resetting
      `seo_enhanced` and re-running full `inject()` - the latter would
      have duplicated the JSON-LD/FAQ/canonical blocks already on each
      page (the exact bug fixed in iteration 7). Verified: every page has
      exactly one clean tag block, `scripts/audit_site.py` still reports
      0 issues, deployed and confirmed live.

## Done (iteration 45) — Search Console fully activated + Gumroad Discover prepared
- [x] User completed the Search Console verification (property confirmed
      active - the whole SC UI is accessible for the property). Their
      sitemap submission showed "Couldn't fetch" - diagnosed rather than
      guessed: fetched the live sitemap.xml directly (HTTP 200,
      valid XML, application/xml, all 15 URLs) and confirmed robots.txt
      also correctly points at it, so the file itself is fine; this is
      the well-known transient state for a brand-new property where
      Google reports "Couldn't fetch" before its first real fetch
      attempt. Resubmitted the sitemap (non-destructive re-trigger,
      "Sitemap submitted successfully").
- [x] The stronger lever, done via the user's own logged-in session with
      their standing go-ahead to finish the task: **URL Inspection →
      Request indexing** for the 3 highest-value pages (homepage + both
      $29 kit pages). All three confirmed "Indexing requested - URL was
      added to a priority crawl queue". This asks Googlebot to come
      directly, independent of the sitemap fetch resolving.
- [x] Second distribution lever, independent of Google entirely:
      **Gumroad Discover readiness**. Found all 3 listings had category
      "Other" and zero tags - i.e. even after the eligibility gate is
      passed, Discover would have had nothing to place them under. Set
      real categories (both kits: Business & Money > Gigs & Side
      Projects; ebook: Self Improvement > Productivity) and 5 honest,
      relevant tags each. Verified all three persisted after a full page
      reload, not just in the editor state.
- [x] Honest constraint noted, not hidden: Gumroad's own banner states
      Discover eligibility requires **at least one successful sale +
      the Risk Review process** - so this is preparation that activates
      the moment the first sale lands, not instant distribution today.
- [x] Explicitly did NOT act on the Share tab's "Share on X / Facebook"
      buttons (publishing on social accounts is the user's own action)
      and did not touch pricing/discounts (user's earlier "not now"
      decisions stand).

## Milestones
- **M1 — Discovery loop proven with real data** ✅ (iteration 1)
- **M2 — First real product file exists and is reviewable by the user** ✅ (iteration 2 — see `data/exports/products/`)
- **M2.5 — Pipeline runs autonomously on a schedule, not just locally** ✅ (iteration 5 — see the Actions tab on the repo)
- **M3 — First page published and receiving organic traffic** 🚧 (iteration 7 — deployed, traffic not yet measured)
- **M4 — First measured lead or sale attributed to the pipeline**
