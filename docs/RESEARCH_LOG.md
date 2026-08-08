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

### RL-2 — GLEIF assessed and rejected (2026-08-08)

Assessed as a flagship data mechanism. Passed Q1 (3,397,612 entities),
Q2 (published 3× daily), Q3 (unambiguous unit: the LEI). Partially
passed Q6 — GLEIF publishes monthly **stocks** (how many lapsed) but not
entity-level **flows** (which entity changed, when, from what).

**Failed Q5 (moat), decisively and on evidence:**

| Check | Result |
|---|---|
| Old full Golden Copy files public? | Yes — HTTP 206, real ZIP |
| Oldest available | at least 2022-01-14 |
| Full fields or aggregates? | Full — 475 MB CSV/JSON/XML |
| Official archive or mirrors? | Official, `goldencopy.gleif.org` |
| Entity-level transitions reconstructable? | Yes — diff any two files |

Anyone can download GLEIF's own history back to 2022 and rebuild exactly
the time series we would spend a year observing. Continuous observation
buys nothing. Rejected.

An inference was available — "if GLEIF wanted history reconstructable
they would offer deltas longer than 31 days" — and was explicitly
**not** used. It is a hypothesis. The verdict rests on downloaded files.

**The generalisable lesson:** the deciding property is not public vs.
private. It is **whether the source archives itself**. GLEIF, TED,
CORDIS, OpenAlex and Crossref are append-only registers that keep their
own history and hand it to anyone. No amount of observing them creates
an asset.

---

## Hard gate for the next candidate (adopted 2026-08-08)

Search **only** for systems that:

> publicly expose a changing state or response, do **not** publicly retain
> its historical versions, and whose state can be observed repeatedly
> without the operator's cooperation.

Three properties must hold at once:

1. **State changes** — something genuinely changes.
2. **No recoverable history** — the operator does not provide the past, so
   a competitor cannot assemble the same dataset from the source.
3. **Externally observable** — we can measure it ourselves, repeatedly,
   automatically and legally, with no internal access.

The asset shape this produces:

    source -> current state -> our observation -> OUR historical dataset

versus the shape that fails:

    source -> its own historical data -> anyone's analysis

**Q0 — Data novelty (LOCKED 2026-08-08). Checked BEFORE Q1.**

> The source must not itself retain historical answers to the same
> interactive queries in a way that lets a third party retroactively
> reconstruct our observation series.

**What Q0 may and may not assert.** "Nobody has ever recorded this" is
unprovable and must never be claimed. Q0 means only, and is worded only
as:

> At the time of candidate selection, no publicly available historical
> source was identified from which the same observations could be
> reconstructed.

That is defensible. The metaphysical version is not.

**The class being sought is not "the unarchived web"** — that is too
broad and was shown empirically to be nearly a dead end (see below). It
is a **state-after-query system**:

    input -> current state/answer -> the answer changes -> the old answer is gone

with no public append-only log, snapshot archive, or third-party service
from which the same series could be rebuilt.

This is precisely why GLEIF failed: it does serve current state, but its
own archive turns observation into ordinary reading of historical data.
In an interactive system, the query itself creates the observation.

**Q0 test — every candidate, no assumptions by system type:**

1. Is there a publicly or legitimately repeatable query mechanism?
2. Can the same query be repeated over time?
3. Does the answer change?
4. Does the operator retain historical answers?
5. Does a known third party retain them?
6. Can an older answer be reconstructed from public data?
7. If not — do our observations create a dataset that did not exist
   before the first measurement?

**Q0 casualties already established (2026-08-08), with the archiver that
killed each:**

| State class | Already archived by | Verdict |
|---|---|---|
| HTTP documents (prices, terms, listings) | Wayback — covers even small sites | ❌ |
| TLS certificates | Certificate Transparency, append-only | ❌ |
| Open ports / exposed services | Shodan, Censys | ❌ |
| DNS incl. SPF/DMARC | SecurityTrails (12y, daily granularity), WhoisFreaks, WhoisXML | ❌ |
| Public registers (GLEIF, TED, CORDIS, OpenAlex, Crossref) | themselves | ❌ |

**The finding worth more than any single candidate:** the observable
surface of the internet is archived far more thoroughly than intuition
suggests. "Surely nobody records this" is almost always wrong, and it was
exactly the assumption the whole moat was meant to rest on.

**What survives, and why:** archivers crawl; they do not ask. Wayback
stores a page, CT stores a certificate, Shodan stores a port — none of
them can store *the answer to a question nobody asked*. Surviving states
are those revealed only in response to a specific query.

If this class yields no candidate that passes Q0 **and** Q1–Q6, the
result is "no viable data mechanism found". It is not grounds for
loosening the gate.

---

## RL-3 — Flagship data-mechanism search (2026-08-08) — CLOSED, NEGATIVE

**Result: no viable data mechanism found.** Recorded as the outcome, not
as a reason to weaken Q0.

Twelve mechanisms were verified to actually return bulk data (OpenAlex
323.8M, Crossref 185.3M, GLEIF 3.4M, npm `_changes`, GH Archive, TED
183k, OpenFoodFacts 4.7M, OSM changesets, RPO, CORDIS, PyPI, Wikidata).
Q1 and Q2 were never the constraint. **Q0 and Q5 were.**

### Every state class tested, and the archiver that killed it

| State class | Already retained by | |
|---|---|---|
| HTTP documents (prices, terms, listings) | Wayback, incl. small sites | ❌ |
| TLS certificates | Certificate Transparency | ❌ |
| Open ports / services | Shodan, Censys | ❌ |
| DNS incl. SPF/DMARC | SecurityTrails (12y, daily), WhoisFreaks | ❌ |
| Public registers | themselves (GLEIF verified to 2022) | ❌ |
| Flight & hotel prices | FlightLabs, Cirium, Makcorps, FlightAware | ❌ |
| Search rankings / SERPs | Semrush (2012+, daily), Ahrefs | ❌ |
| Government appointments & wait times | governments publish it (US State Dept, GOV.UK) | ❌ |

### The structural reason — not bad luck

**Q5 and Q6 are in direct tension.** Q5 requires that nobody holds the
history. Q6 requires that someone would pay for it. But a series gets
collected precisely *because* it has recognised value — so anything worth
paying for is usually already being sold.

What remains is the set of series that are valuable but **not yet
recognised as valuable**. That set is, by construction, one we cannot
reliably find by searching: if the value were visible to us, it would be
visible to a data vendor with more resources and closer domain contact.

Continuing to search this space is lottery-ticket hunting, not research.

### Consequence for the project

A flagship built on a **proprietary dataset moat** appears structurally
unavailable to us. That does not condemn the project — it means
differentiation has to come from somewhere other than owning data nobody
else has. That is a strategy question, not another search.

Do not reopen RL-3 by relaxing Q0. Reopen it only if a *specific* system
is identified where the Q0 seven-point test can actually be passed on
evidence.

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
