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
