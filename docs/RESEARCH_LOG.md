# Research log

Empirical records of what was measured, what failed, and why. Not a
governance doc — the standing "no new process docs" rule stands. This
exists because negative results have to be written down somewhere or they
get rediscovered at full cost, and the user asked for them to live in an
internal log rather than on the website.

**Nothing in this file is site content.** The figures below are properties
of instruments we built, not claims about any market or company. They must
not be published, quoted in articles, or used as marketing. That is the
whole point of recording them here.

---

## RL-1 — Machinery documentation availability (2026-08-02) — CLOSED, NEGATIVE

**Question:** can we build a defensible, self-collected dataset about how
European machinery manufacturers keep documentation available, and use it
as the basis for a flagship?

**Answer: no.** Not because the topic is uninteresting, but because no
cheap, open, sufficiently representative data source exists for it.
Machinery Regulation is therefore removed from flagship candidates.

### What was tried, in order, and how each one died

| Approach | Result | Why it failed |
|---|---|---|
| Wayback CDX, all archived PDFs | 275 docs, 64.1% "not available" | Population was brochures and customer magazines, not documentation. Aggregate meaningless. |
| Wayback CDX, documentation-only | 237 docs, 68.7% | Failures cluster at manufacturer level, so per-document aggregation averages two distinct populations. Wrong statistic, not just a wrong number. |
| Hand-picked 40 manufacturers | bimodal, 13 usable | Convenience sample biased to large well-known firms. |
| Wikidata systematic frame (199) | 11 of 199 yielded data | Wayback coverage of documentation PDFs is far too sparse. Retrospective route closed. |
| Static accessibility census (199) | 64.7% UNKNOWN | Instrument could not assess two thirds of the population. |
| Rendered-browser calibration (n=30) | 84% of eligible UNKNOWNs resolved | Pre-registered stop rule fired: UNKNOWN was an artifact of the instrument, not a property of the population. |

### The claim that was nearly published, and was not

An early pass produced **64.1%**, which would have read as
"64% of European manufacturers' documentation is unavailable". It was
false. It was driven by marketing PDFs and by defects in our own
classifier. It survived until segmentation was run, and it only got
segmented because the protocol required a mandatory UNKNOWN category and
pre-registered decision thresholds.

Three classifier defects were caught in pre-run validation, all of which
would have produced confident wrong output without crashing:
robots-disallowed treated as "no documentation"; absence asserted from a
single crawled page; the word "login" anywhere in a page (including the
global header) read as an authentication gate.

### A hypothesis that did not survive its own sample

Dead documentation subdomains (`www2.trumpf.com`, `www3.festo.com` — both
NXDOMAIN while the parent domains serve normally) suggested a strong
thesis: *the problem is not document retention, it is URL infrastructure.*
In the systematic frame, HOST_GONE was **0%**. The thesis was an artifact
of hand-picking large German firms with legacy subdomains.

### What was verified and does stand

Nine manufacturers (12 domains) publish documentation at a direct public
URL — independently re-verified 12/12, HTTP 200 + `application/pdf`.
This validates the DIRECT_PUBLIC positive class only; it is **not** a
validated classifier and does not extrapolate to other classes.

Too thin to seed an observatory: one documentation URL was captured per
manufacturer, so the cohort would be ~12 URLs. An observatory over 12 URLs
has no statistical power, and expanding it requires solving exactly the
crawling problem shown above to be intractable.

### Terms that must never be attached to these numbers

- ❌ "64.7% of manufacturers…" — an instrument artifact
- ❌ "84% of websites…" — a calibration result about our crawler
- ❌ "X% do not have documentation" — bounded crawls cannot establish absence
- ❌ any "non-compliant" or Art. 10(7) violation framing — a legal
  assessment no crawl can carry

The existing free tool at `/tools/machinery-regulation-digital-instructions.html`
is unaffected: it states the regulation's requirement and computes a cost,
both corrected and verified (see TASKBOARD iteration 75). It makes no
claim about industry behaviour and none may be added to it.

---

## Standing rule adopted from RL-1

The project had been running:

    topic -> content -> tool -> SEO -> look for evidence

RL-1 established the correct order empirically:

    observable property -> population -> measurement -> falsification
      -> dataset -> only then a product

**A measurable property and a defensible route to the data must exist
before any thesis, article, tool, SEO plan or business model.**

### Filter for any future flagship candidate

A candidate must satisfy all seven:

1. A publicly observable population exists, assemblable **without hand-picking**.
2. The unit of measurement is unambiguous (company, product, price, URL,
   document, offer) — never something requiring subjective judgement.
3. Data can be collected automatically, ideally daily or weekly.
4. **Change over time is itself the value** — not a one-off snapshot.
5. The result could be surprising. If the outcome is predictable, it is
   not a flagship.
6. The result supports a concrete decision, not just an interesting statistic.
7. "We don't know" is a legitimate outcome. UNKNOWN must be a first-class
   result in the new project too.
