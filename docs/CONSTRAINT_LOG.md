# Constraint Log

A company is limited by a very small number of real constraints at any
given time. This log's only job is to name *the* current one - not a list
of problems - so effort stops getting spread across everything and
concentrates on the one thing actually capping enterprise value. Update
this every iteration, not just weekly (contrast with
docs/STRATEGIC_REVIEWS.md, which questions the business model itself on a
~weekly cadence - this log tracks the tactical constraint, more often).

**Rule: never optimize anything that is not the primary constraint.** If
the evidence says the constraint changed, reprioritize the roadmap
immediately - don't keep working on yesterday's bottleneck out of momentum.

---

## 2026-07-27 — Distribution / human-gated account setup

- **Current primary constraint**: Discovery. 14 products have a live,
  finished landing page and 0 are confirmed indexed by Google. The
  constraint isn't content quality, product quality, or code - it's that
  nobody outside this system has a reliable way to find any of these
  pages yet, so their expected revenue is ~0 regardless of how good they
  are.
- **Evidence supporting it**:
  - `site:biznis-studio.github.io` search confirmed 0 indexed pages
    (iteration 17).
  - IndexNow (the one implemented free/no-account indexing path) has
    returned 403 `UserForbiddedToAccessSite` since 2026-07-27 with no
    known fix, and only covers Bing/Yandex/Seznam/Naver/Yep anyway, never
    Google.
  - Google Search Console - the direct fix - was started, then paused
    mid-setup, and only re-approved by the user this session; verification
    isn't complete yet.
  - 0 analytics exist, so there's no way to test whether traffic is
    actually the constraint versus assuming it - this is the single
    biggest gap in the evidence for this entry and should be resolved by
    the next review once Search Console is verified.
- **Expected Business Value if removed**: High and multiplicative, not
  additive - fixing discovery doesn't help one product, it unlocks the
  revenue potential of all 14 already-built, already-tiered pages
  simultaneously (7 of them already classified `core` on real demand
  evidence). This is why it outranks "build more products" or "polish
  SEO further" in the EBV ranking in ROADMAP.md.
- **Cost to remove**: Low and mostly non-engineering. Search Console
  verification is ~3 minutes of the user's time plus code already wired
  (`GOOGLE_SITE_VERIFICATION` env var, progressive-enhancement pattern
  already built in `landing_page_agent.py`). The remaining cost is
  calendar time waiting for Google to actually crawl/index once verified,
  not more building.
- **Confidence level**: Medium-high. High confidence that 0 indexed pages
  means 0 organic discovery is happening. Medium confidence that Search
  Console verification alone fully resolves it - a brand-new domain with
  no backlinks may still index slowly even once verified; this should be
  rechecked with real Search Console data (impressions/clicks) once
  available, not assumed solved the moment verification succeeds.
- **Alternative constraints considered and rejected (for now)**:
  - *Product/content quality* - rejected: the `core`-tier products
    already have real competitor-pricing validation (iterations 18-19);
    more polish here has a lower EBV than fixing discovery for the
    products that already exist.
  - *Monetization (Gumroad KYC)* - a real, separate blocker, but it only
    matters once traffic exists to convert - ranked second, not primary,
    per the EBV ranking in ROADMAP.md.
  - *Analytics* - rejected as the primary constraint on purpose: there's
    nothing to measure until discovery produces visits; instrumenting
    before that would just show zeros.
  - *Design/UX* - already addressed in earlier iterations (iteration 20);
    no new evidence it's currently limiting anything.
- **Next review trigger**: once Search Console is verified and has
  accumulated at least a few days of impression data, re-evaluate whether
  discovery is resolved or whether a *new* constraint (e.g. click-through
  rate, or conversion once visits exist) has taken its place. Don't wait
  for the full weekly Strategic Review if this resolves sooner - a
  constraint change updates this log immediately.

## 2026-07-30 — constraint changed: not discovery, but *winnability*

**Previous entry named discovery (0 indexed pages) as the constraint. That
is now resolved and was not the real limit.**

- **Evidence gathered, not assumed.** Gumroad: 0 sales *and 0 views* -
  nobody reached the page, so this was never a conversion, price, copy or
  design problem. Product pages verified live and purchasable by direct
  test (price shown, buy button active, not disabled, no warning), which
  also disproves the hypothesis that the failed Gumroad identity
  verification was suppressing sales - that blocks payouts only.
  `site:biznis-studio.github.io` on Google returns real results, indexed
  one day ago. So: indexed, reachable, purchasable, and still zero.

- **The actual constraint.** A manual SERP check for
  "scope creep cost calculator freelance" - the query our most
  differentiated free tool targets - returns a full first page of
  established competitors: Sengi, Teamz Lab, AI Biz Hub, **Harvest** (a
  major time-tracking SaaS), Invopoint, Jobbers, Agiled. Seven existing
  calculators for the same job. A 4-day-old domain with zero backlinks
  does not out-rank those, this year or possibly ever.

- **What this exposes in the system itself.** `demand_scoring_agent`
  measures *interest* and calls it opportunity. The competition component
  is derived from GitHub/npm/Stack Exchange density, which iteration 3
  already recorded as a poor proxy for consumer-content saturation. That
  caveat now has a concrete, costly example: the pipeline happily built
  products for a category owned by incumbents, because nothing in it ever
  asks "could we actually rank for this?"

- **Honest limit on fixing it automatically.** A winnability check needs
  real SERP data. Scraping Google is against its terms and gets blocked;
  proper SERP APIs are paid. So this cannot be closed inside the
  unattended pipeline for free - it has to be a manual check during a
  working session, exactly as done here. Recording that rather than
  pretending an automated fix is coming.

- **Consequence for strategy.** SEO cannot be the acquisition mechanism
  for the first customer. It stays running (it is automated and costs
  nothing) but is demoted from *the plan* to *background*. The catalogue's
  role changes: it is no longer the thing being sold to strangers via
  search, it is verifiable proof of capability for the services - which
  are worth 100x per sale and are bought via outreach and portfolio, not
  via a keyword.
