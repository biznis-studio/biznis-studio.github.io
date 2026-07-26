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
2. **Niche clustering** — currently `niches`/`niche_keywords` are unused.
   Group related keywords (e.g. via simple co-occurrence or, once available,
   embeddings from a local model) so product ideas target a *cluster* of
   validated demand, not one isolated keyword.
3. ~~**Content/Template Agent**~~ — done: `agents/content_agent.py` authors
   calculator/checklist/template/prompt_pack ideas as real, usable files;
   ebook/sop ship as outline skeletons (`status='draft'`) since they need
   real prose an LLM or human still has to write.
4. **LLM-assisted ideation and content drafting** — once either (a) Ollama
   is installed locally, or (b) the user provides an OpenRouter API key
   (their choice — this requires an account, which this system will not
   create on the user's behalf), swap the rule-based `product_agent`
   title/rationale generation and the new Content Agent's drafting for
   LLM calls, with the existing rule-based path kept as a zero-cost
   fallback.
5. **Landing Page Agent** — generate a static page (Astro/plain HTML) per
   built product from a template, with metadata wired for the SEO Agent
   below. Deployable free via Cloudflare Pages or GitHub Pages.
6. **SEO Agent** — metadata, schema.org markup, FAQ generation, internal
   linking between landing pages, sitemap/RSS generation.
7. **Publishing** — actual deploy step (Cloudflare Pages via GitHub Actions,
   or GitHub Pages) once there's at least one landing page.
8. **Analytics Agent** — once pages are live, pull free analytics
   (Cloudflare Web Analytics is free and privacy-respecting, or
   plausible/umami self-hosted) into `analytics_events`.
9. **Conversion/Feedback loop** — once real traffic/analytics exist, close
   the loop back into demand scoring (a keyword whose product converts well
   should boost related keywords' scores).

## Explicitly deferred / needs a human decision

- **Monetization integrations** (affiliate links, Gumroad/Lemonsqueezy for
  digital downloads, newsletter platform) — these involve creating accounts
  and agreeing to third-party terms, which this system will flag for you
  rather than do autonomously.
- **GitHub remote + Cloudflare deployment** — the local git repo is ready;
  pushing to a GitHub remote and wiring Cloudflare Pages needs your
  go-ahead since it creates externally-visible, shared state.
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
