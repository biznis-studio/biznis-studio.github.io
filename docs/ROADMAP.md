# Roadmap

Ordered by expected leverage, not by the order listed in the original brief.
Re-evaluate this ordering every iteration — see TASKBOARD.md.

## Next up

1. ~~**Competitor/Competition Analysis Agent**~~ — done: `agents/competitor_agent.py`
   checks npm/GitHub/Stack Exchange/Wikipedia supply for the run's top 20
   keywords (bounded by GitHub's 10 req/min unauthenticated search limit)
   and `demand_scoring_agent.apply_competition()` re-blends their score with
   a 25%-weighted opportunity component. See known limitations below - this
   works well for developer-tool-shaped ideas, poorly for generic single
   words.
2. ~~**Niche clustering**~~ — done: `agents/niche_agent.py` links keywords
   extracted from the *same* underlying signal (same HN title, same SE
   question) via union-find; connected components of size 2+ become a
   niche. Verified the mechanism works correctly with a synthetic
   co-occurring pair, but it found **zero real niches on the first run** -
   with ~230 signals/run and most surviving keywords being single,
   lexically distinct words (checklist, invoice, spreadsheet...), no two
   currently ever share the same sentence. This is an honest data-sparsity
   result, not a bug - expect real niches to emerge as run history
   accumulates, and revisit with embedding-based semantic clustering (see
   #4) since that could group "invoice" + "spreadsheet" + "template" as
   related even without any shared substring.
3. ~~**Content/Template Agent**~~ — done: `agents/content_agent.py` authors
   calculator/checklist/template/prompt_pack ideas as real, usable files;
   ebook/sop ship as outline skeletons (`status='draft'`) since they need
   real prose an LLM or human still has to write.
4. **LLM-assisted content drafting (ebook/sop prose)** — decided 2026-07-26:
   the user will use Claude directly (not Ollama/OpenRouter) to write the
   actual prose for `draft`-status ebook/sop outlines produced by
   `content_agent.py`. This stays a human-in-the-loop step for now rather
   than an automated API call in the pipeline (no Anthropic API key/billing
   wired into the system) - the outline skeleton is the handoff artifact.
   First one done 2026-07-26: "The Practical Guide to Automation"
   (`products.id=3`) - real ~1300-word prose replacing its outline,
   promoted to `status='ready'`, published with its own landing page.
   Remaining drafts (productivity, xlsx, appium, gantt chart) still need
   the same treatment - see TASKBOARD.md. Revisit full automation only if
   the user wants the pipeline itself to call the Claude API end-to-end
   (would need an API key + billing set up by the user first).
5. ~~**Landing Page Agent**~~ — done: `agents/landing_page_agent.py` builds a
   real static page under `site/` only for `status='ready'` products
   (calculator/checklist/template/prompt_pack) - draft ebook/sop outlines
   are skipped so nothing publishes a skeleton as a finished page. Verified
   all four formats render correctly in-browser, including a real bug found
   and fixed: the intro blurb was injected before the calculator's own
   `<h1>`, rendering visually above the title. `pages.status` stays 'draft'
   until an actual Publishing agent deploys `site/` somewhere.
6. ~~**SEO Agent**~~ — done: `agents/seo_agent.py` injects schema.org
   JSON-LD (SoftwareApplication/HowTo/CreativeWork - never
   AggregateRating/Review, since there are no real reviews to mark up),
   Open Graph tags, a genuine generic FAQ (mirrored as FAQPage schema), and
   internal "more free tools" links, idempotently (tracked via
   `pages.seo_enhanced`). Found and fixed a real bug: the HowTo step text
   was pulled from already-HTML-escaped page content, so JSON-LD literally
   contained `&quot;` instead of a real quote character - fixed with
   `html.unescape()`. sitemap.xml/feed.xml generation was added right
   after, once Publishing (below) made SITE_BASE_URL real.
7. ~~**Publishing**~~ — done 2026-07-26: chose GitHub Pages over Cloudflare
   Pages specifically because it needed no new account (Cloudflare Pages
   would have required the user to sign up there first). Enabled via
   `gh api repos/.../pages` with `build_type=workflow`; `pipeline.yml` now
   uploads `site/` as a Pages artifact and deploys it via
   `actions/deploy-pages` in a second job after every pipeline run. Live at
   https://fwwk4pb868-afk.github.io/biznis/. `SITE_BASE_URL` is set as a
   workflow-level env var, which is what turns on canonical URLs +
   sitemap.xml + feed.xml in `seo_agent.py`.
8. **Analytics Agent** — once pages are live, pull free analytics
   (Cloudflare Web Analytics is free and privacy-respecting, or
   plausible/umami self-hosted) into `analytics_events`.
9. **Conversion/Feedback loop** — once real traffic/analytics exist, close
   the loop back into demand scoring (a keyword whose product converts well
   should boost related keywords' scores).

## Explicitly deferred / needs a human decision

- **Monetization: Gumroad chosen, awaiting the user's account + first listing**
  (decided 2026-07-26). The mechanism is built: `products.monetization_url`
  (nullable) - when set, `landing_page_agent.py` replaces the free download
  link with a "Get it on Gumroad" CTA and stops copying that file into
  `site/downloads/` (no point undermining a paid listing by also giving it
  away next to it). Tested end-to-end with a placeholder URL, then
  reverted - real integration is waiting on the user to (1) create a free
  Gumroad account, (2) list a product, (3) give the resulting URL. This
  system does not create payment/seller accounts on anyone's behalf.
  Affiliate links and a newsletter platform remain deferred behind this
  same account-creation constraint - revisit once Gumroad is proven out.
- ~~**GitHub remote**~~ — done 2026-07-26: pushed to
  https://github.com/fwwk4pb868-afk/biznis (public), scheduled Action
  verified working end-to-end (manual run succeeded, bot commit landed).
- ~~**Publishing (GitHub Pages)**~~ — done 2026-07-26, see item 7 above.
- **Competitor keyword-volume tools** (e.g. real search-volume data) are
  mostly paid; look for a free-tier-compliant alternative before building
  this rather than assuming one.

## Known limitations to revisit

- npm popularity signal is seeded from a fixed list of broad terms
  (`NPM_SEED_TERMS` in `market_research_agent.py`), so it partly just
  echoes those seeds back rather than discovering genuinely new terms.
  Replace with a broader/rotating seed list or a real "trending packages"
  source once one is found that's free and ToS-compliant.
- Growth scoring only becomes meaningful after a keyword has appeared in
  2+ runs; first-run scores use a neutral prior. This resolves itself
  automatically as the scheduled pipeline accumulates history.
- Keyword clustering is exact-string-match only (no semantic dedup), so
  e.g. "chatgpt" and "chat gpt" are currently treated as different
  keywords. A local embedding model (via Ollama) would fix this cheaply.
- Product-idea filtering against npm package-name artifacts (`_looks_like_package_name`
  in `product_agent.py`) is a regex heuristic (catches "@scope/name" and
  "kebab-case" patterns), not a real dictionary check — a genuine two-word
  English niche phrase that happens to be hyphenated could theoretically be
  skipped. Revisit if that turns out to matter in practice.
- Competition scoring's fixed saturation thresholds (`_normalize()` in
  `competitor_agent.py`) conflate "code-repository density" with "consumer
  content market saturation": broad single-word keywords like "checklist"
  or "calculator" trivially max out at saturation=1.0 (millions of GitHub
  repos mention the word "automation" in code, which says nothing about
  whether a paid automation checklist ebook already saturates that market).
  This makes the opportunity component weak precisely for the generic
  umbrella terms that are actually our best product categories - it's
  currently most useful for narrow, specific, developer-tool-shaped
  keywords. The Wikipedia "dedicated article exists" check is the most
  meaningful of the four for consumer-content topics; consider weighting
  toward it, or finding a genuine consumer-search-volume proxy, before
  trusting this component heavily.
- The n-gram stopword filter in `keyword_agent.py` occasionally lets
  through incoherent sentence fragments from Stack Exchange titles (found
  "there way" - almost certainly a slice of "there's no way to..." or
  similar) that survived the 2-occurrence bar by coincidence. Caught this
  one manually and rejected the resulting product idea; the stopword list
  needs to be stricter about fragments that don't stand alone as a topic,
  rather than relying on manual review of every idea before writing content.
- Any user-facing copy that's built by directly reusing `product_ideas.rationale`
  (the landing page subtitle, meta description) needs to read correctly
  both as an internal audit note *and* as visitor-facing text, since
  `product_agent.py`'s docstring frames `rationale` as an audit trail but
  `landing_page_agent.py` displays it verbatim. Already bit us once - the
  ebook fallback rationale used to read "No specific format pattern
  matched..." on a live page (fixed 2026-07-26). Worth a dedicated
  visitor-facing blurb field if this keeps recurring as new format rules
  are added.
