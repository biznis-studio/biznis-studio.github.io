# Opportunity Queue

Never run out of executable work. When the current task finishes, pull
the next-highest-EBV item below instead of stopping - see the Autonomy
Policy and "AI Operating System" framing in ROADMAP.md for why, and the
honest note there about why this queue holds real entries at the
project's actual current scale rather than a fixed 100-per-category quota.

Each entry: **EBV** (rough, qualitative - low/med/high), **Cost** (agent
time / real $), **Confidence**, **Dependencies**, **Human involvement**
(none / advisory / blocking). Pull items in roughly EBV order within a
category, but a low-cost near-zero-risk item can jump the queue over a
higher-EBV one that needs more validation first. When a category has
fewer than ~3 items left, spend the next unblocked turn on research to
refill it rather than inventing filler.

---

## Engineering (technical debt / code quality)

1. **Full fix for the n-gram middle-word stopword gap** - `significant_ngrams()`
   only checks a window's first/last word; a fragment like "explain there
   way" can still slip through (see docs/DECISION_JOURNAL.md-adjacent note
   in ROADMAP's known limitations). EBV: low-med. Cost: med (needs a rule
   that doesn't over-filter legitimate phrases like "guide to xlsx").
   Confidence: med. Deps: none. Human: none.
2. **Reweight competition/saturation scoring** away from GitHub code-repo
   density (which trivially maxes out for generic words like
   "checklist") toward the Wikipedia dedicated-article signal, which is
   more meaningful for consumer-content topics. EBV: med. Cost: med.
   Confidence: med. Deps: none. Human: none.
3. **Add a real test suite** for `markdown_lite_to_html()` and
   `significant_ngrams()` - both have been hand-verified after every
   change so far (worked, but slow and risks a missed regression). EBV:
   med (prevents a repeat of the blockquote/list-merging bug that shipped
   to every page). Cost: med. Confidence: high. Deps: none. Human: none.
4. **Broaden/rotate the npm seed-term list** in `market_research_agent.py`
   - it currently partly echoes its own fixed seed terms back rather than
   discovering genuinely new ones. EBV: low. Cost: low. Confidence: high.
   Deps: none. Human: none.
5. **Validate PDF export output**, not just that the subprocess exits 0 -
   check the resulting file is non-empty/opens correctly before treating
   an ebook as `ready`. EBV: low-med (silent-corruption risk is real but
   unobserved so far). Cost: low. Confidence: high. Deps: none. Human: none.
6. **Semantic keyword dedup** ("chatgpt" vs "chat gpt" currently treated
   as different keywords) - needs a local embedding model. EBV: low-med.
   Cost: high (needs Ollama installed - a real new dependency). Confidence:
   low until that's evaluated. Deps: Ollama install. Human: advisory (may
   want to approve a new local dependency).
7. **Retry IndexNow submission periodically** rather than treating the
   403 as permanently dead - Bing's backend may start trusting the key
   file over time with no code change needed. EBV: low. Cost: near-zero
   (already implemented, just needs an occasional re-check). Confidence:
   med. Deps: none. Human: none.

## Business (packaging, pricing, positioning)

1. **Price the two `core`-tier freelancer kits** (Scope Creep Kit,
   Retainer Renewal Kit) the moment Gumroad payouts activate - the
   competitor-pricing research ($19-79) already exists. EBV: high. Cost:
   near-zero. Confidence: high. Deps: Gumroad KYC (BLOCKED on the human).
   Human: blocking (already in the Human Action Batch).
2. **Bundle both freelancer "systems" into one combined offer** once
   priced individually - matches the validated "packaged system" pattern
   from iteration 18's research. EBV: med. Cost: low. Confidence: med.
   Deps: item above. Human: none once unblocked.
3. **Evaluate Ko-fi as a lower-friction monetization fallback** if Gumroad
   KYC stalls much longer (flagged in the first Strategic Review) - this
   is research/comparison work, not an account signup, so it's genuinely
   unblocked right now. EBV: med. Cost: low (research only). Confidence:
   med. Deps: none for the research; a real account only if adopted.
   Human: none for research, blocking if adopted.
4. **Split services (web dev/chatbot) onto their own trust-building
   page/case-study track** instead of sharing the homepage with $0
   downloads (flagged in the first Strategic Review) - this project
   itself is a legitimate case study ("built and launched an autonomous
   research-to-product pipeline"). EBV: med. Cost: low-med (writing).
   Confidence: med. Deps: none. Human: none.
5. **Revisit whether the `*.github.io` subdomain hurts trust** enough to
   justify a custom domain - real $ cost, so this is a judgment call, not
   pure execution. EBV: low-med, genuinely uncertain without traffic data.
   Cost: low ($ per year). Confidence: low until more evidence exists.
   Deps: some real traffic data first. Human: advisory ($ approval).

## Customer Discovery Layer (new category, added 2026-07-27 after an
## external second opinion - see Decision Journal D10)

The pipeline currently only reads keyword *frequency*, never actual
customer language ("I wish...", "I'm tired of...", "does anyone know...").
That language is a stronger demand signal than frequency alone. Scoped
honestly by what's actually free/no-auth vs. what needs a new account:

1. **HN comments, not just titles** - the Algolia HN API already used by
   `market_research_agent.py` also exposes comment text
   (`tags=comment`), currently unused. EBV: med. Cost: low (extend an
   existing integration). Confidence: high. Deps: none. Human: none.
2. **Stack Exchange comments, not just questions** - same API already in
   use, comments endpoint is free/no-auth too. EBV: med. Cost: low.
   Confidence: high. Deps: none. Human: none.
3. **GitHub Issues** (titles + bodies) on public repos - same GitHub
   search API already in use, same rate limit. Real "I wish X did Y"
   language shows up here often. EBV: med. Cost: low-med. Confidence:
   med. Deps: none. Human: none.
4. **Reddit** (public `.json` endpoints on public subreddits, no login
   needed for read-only access at low volume) - genuinely new source,
   not currently integrated at all. EBV: med-high (Reddit threads are
   often exactly "I wish/does anyone know" phrasing). Cost: med (new
   integration + ToS/rate-limit care). Confidence: med. Deps: none.
   Human: none for read-only public access.
5. **Product Hunt, IndieHackers, Discord** - suggested alongside the
   above, but explicitly NOT equally free: Product Hunt's real API needs
   an OAuth app/token, IndieHackers has no public API (would mean
   scraping, ToS risk), Discord needs server-specific access. EBV:
   unknown until evaluated. Cost: real (new account/token setup). Human:
   **blocking** - correctly belongs in the Human Action Batch if ever
   pursued, not bundled in as if it were free like items 1-4.

## Growth / distribution

1. **Audit and improve internal cross-linking density** across all 14
   pages ("more free tools" links already exist via `seo_agent.py` -
   verify they're evenly distributed, not just linking the same 2-3
   popular pages). EBV: low-med. Cost: low. Confidence: high. Deps: none.
   Human: none.
2. **Add an og:image** to the homepage and product pages - currently only
   title/description Open Graph tags exist, no preview image, which hurts
   how the site looks when shared/linked anywhere. EBV: low-med. Cost:
   low (can reuse/extend the existing favicon SVG into a proper share
   image). Confidence: high. Deps: none. Human: none.
3. **Once Search Console has real query data**, mine it for exact-phrase
   on-page copy improvements (currently impossible - no data exists yet).
   EBV: potentially high, unknown until data exists. Cost: low once data
   exists. Confidence: n/a yet. Deps: Search Console verified + ~1-2 weeks
   of data. Human: none (data access only, already granted once verified).
4. **Re-check IndexNow submission status** now that `robots.txt` and the
   RSS discovery tag exist - more crawl signals in place may change the
   403 outcome even though the root cause is unconfirmed. EBV: low. Cost:
   near-zero. Confidence: low. Deps: none. Human: none.

## Experiments (deliberately the thinnest category right now - honest
## about why: almost everything here needs real traffic to test, and
## there is none yet - see docs/CONSTRAINT_LOG.md)

1. **Hypothesis, ready to run once there's traffic**: pages with a
   service CTA ("Work with us") above the fold convert more service leads
   than below. Metric: form submissions per visit, once Formspree is live
   and there's traffic. Currently un-testable, not un-thought-of.
2. **Hypothesis, ready to run once there's traffic**: bundling the two
   freelancer products together converts better than selling them
   separately. Metric: relative click-through/purchase rate once Gumroad
   payouts + analytics both exist.

## Automation

1. **Automate PDF/derived-file regeneration** when a shared template
   changes - found and manually fixed this exact gap twice already (the
   calculator's CSS, and now the RSS link tag needed a one-off manual
   patch across 14 files). A "does this source file's content differ
   from what generated this output" check would catch it automatically
   next time. EBV: med (prevents recurring manual-patch work). Cost: med.
   Confidence: med. Deps: none. Human: none.
2. ~~**Add a pre-commit/CI check** that runs the crawl-readiness audit~~ -
   done same day this queue was created: `scripts/audit_site.py` now
   exists as a real, reusable script (checks title/meta/canonical/RSS-
   discovery/JSON-LD validity/broken links) and runs in `pipeline.yml`
   after every scheduled build. Currently non-fatal (`|| true`) - promote
   to a hard CI gate once it's run clean across a few more real scheduled
   builds and the false-positive risk on dynamically-generated content is
   better understood.
3. **Automate the Constraint Log's evidence-gathering half** (product/
   tier counts, indexing status once Search Console exists, revenue
   status) as a script that runs each pipeline execution and appends a
   data snapshot - the judgment half still needs a real reasoning pass
   (documented limitation in docs/STRATEGIC_REVIEWS.md), but the data
   collection itself doesn't. EBV: low-med. Cost: low. Confidence: high.
   Deps: none. Human: none.
