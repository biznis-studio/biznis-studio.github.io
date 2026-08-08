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

---

## Strategic pivot (2026-08-08) — supersedes the data-moat objective

RL-1 to RL-3 produced a precise negative: **do not build a business case
on finding a public dataset nobody else has.** That is removed from the
decision architecture.

**New objective:**

> Build a profitable AI-enabled service where proprietary workflow,
> execution capability and customer integration create the moat — not
> exclusive ownership of public data.

**New sequencing:**

    PROBLEM -> PAYMENT -> WORKFLOW -> AI AUTOMATION -> PRODUCTISATION

never `AI -> application -> look for a problem`.

**Opening question** — no longer "what data can we own?" but:

> What repeated corporate work does someone today pay a person, an agency
> or an internal department to do, which AI can turn into a standardised
> service with materially better economics?

The search space is far larger than RL-3's, because the target is no
longer "something nobody has". It is **something most customers do badly,
expensively or manually**, which we can do more cheaply and more
consistently.

### BUSINESS GATE (all eight, before a single article or line of product)

1. **Real paid problem** — a concrete loss of time, money, risk or
   opportunity. Not "it would be interesting to know X".
2. **Substantially automatable** — AI must take over a significant share
   of the work. A 10% assist to an expert is not a foundation.
3. **Low marginal human cost per case** — otherwise it is an AI agency
   producing manual work slightly cheaper. This is the margin.
4. **Objectively checkable output** — a document, standard, database,
   rule or benchmark to verify the result against.
5. **Immediately usable** — report, audit, monitoring, decision, alert,
   action plan, documentation, workflow. Not an "insight".
6. **Service first, product later** — deliver manually with AI behind it,
   learn what customers actually buy, automate the repeating parts. No
   six months of SaaS before the first customer.
7. **Route to recurring revenue** — a one-off audit may be the entry
   product; the goal is monitoring, periodic review, updates, workflow.
8. **Why not just use ChatGPT/Claude directly?** The hardest question.
   "We have a better prompt" is not an answer. It must be a specialised
   workflow, systems integration, automatic input collection, result
   validation, a domain model, an audit trail, templates and methodology,
   monitoring, or automatic execution of the next step.

**AI is not the product. AI is the production mechanism.**

### Working concept (2026-08-08) — AI Operational Knowledge System

Not a brand. A concept to be tested and discarded if it fails B1–B10.

> Turn a company's existing documents, experience and working data into an
> AI-assisted work system that retains know-how, guides the worker through
> the process, and automates repeating expert work.

**Positioning — this is the part that changes everything.** Not "we sell
you AI that handles complaints" (which puts us head-to-head with
Microsoft's own Factory Operations Agent and with QMS vendors) but:

> we take the AI you already own in Microsoft 365 and turn it from an
> individual assistant into a standardised work system for a specific
> business activity.

Microsoft supplies the platform; we supply methodology, workflow, domain
configuration and the way it is actually used. A company using Excel for
accounting is not competing with Microsoft. **Copilot is part of our
stack, not our competitor.** This is the first framing today where Q8
has an answer that does not require beating anyone.

Shape:

    company data -> structured knowledge model -> AI workflow
      -> Copilot/agents -> decision/action -> feedback

First domain: Quality. First workflow: complaints / 8D. The same engine
then applies to maintenance, production, purchasing, logistics, HSE,
engineering, customer service, internal audit, training.

**The intended moat** is not unique data (RL-3 closed that route). It is
workflow architecture + deployment methodology + domain modules +
accumulated implementation knowledge. Not uncopyable — and it does not
need to be. Productised deployment + domain expertise + distribution +
trust + recurring revenue is a sufficient combination for a profitable
business; it does not have to be a Google-grade technical moat.

**Strongest economic argument** is not productivity but **know-how
retention**: turnover, onboarding time, and dependence on individuals are
costs a CFO can already quantify. "Your know-how stops walking out of the
door" beats "we are faster".

### BUSINESS GATE v2 (B1–B10) — supersedes Q1–Q8 for this concept

| | Gate |
|---|---|
| B1 | **Pain** — is the problem expensive enough? |
| B2 | **Frequency** — does it recur often enough? |
| B3 | **AI leverage** — can AI remove a significant share of the manual work? |
| B4 | **Microsoft fit** — buildable inside what the company already runs? |
| B5 | **Standardisation** — can 60–80% transfer between customers? |
| B6 | **Buyer** — a named person with budget and a reason to buy? |
| B7 | **Deployment** — first implementation without months of integration? |
| B8 | **Recurring value** — reason to pay again next year? |
| B9 | **Competitive position** — is the value more than what Microsoft or a QMS vendor already ships? |
| B10 | **Customer evidence** — can we reach 5–10 relevant people and find out whether they consider this budget-worthy? |

**B10 is now the binding constraint, not more desk research.** Today
established that a theoretically attractive mechanism is not enough. The
next experiment is conversations, not a crawler.

### B10 interview protocol — pre-registered, same discipline as RL-1..RL-3

Customer interviews are extremely good at confirming whatever the
interviewer hopes. A warm "that sounds useful" is the interview
equivalent of the 64.1% figure: pleasant, quotable and worthless. The
same guardrails apply.

**Ask about the past, never about the future.** Intentions are free;
behaviour is evidence.

- ✅ "Walk me through the last complaint you handled. What did you have
  to look up, and where?"
- ✅ "How long did it take, and how much of that was finding information
  rather than solving the problem?"
- ✅ "When [experienced person] left, what specifically got harder?"
- ✅ "What have you already tried or bought to fix this?"
- ❌ "Would you use a system that…" — unfalsifiable, always yes
- ❌ "Would you pay for…" — hypothetical money is always available
- ❌ Any question that describes our concept before they describe their problem

**Never pitch before they have described the work.** The moment the
concept is on the table, everything afterwards is contaminated. Describe
it only at the end, and only to ask what they would *stop doing*.

**Pre-registered pass criteria — written before the first interview, so
warm responses cannot be rationalised into validation:**

| Signal | Counts as evidence |
|---|---|
| Named a specific recurring task and estimated its time cost unprompted | strong |
| Has already paid someone (internal or external) to reduce this | strong |
| Named the person who holds the know-how and what happens without them | strong |
| Volunteered a budget line or an owner for it | strong |
| "Sounds interesting", "we should look at that", "send me info" | **zero** |
| Enthusiasm without a named task, cost or owner | **zero** |

**Decision thresholds, fixed in advance (n = 5–10):**

- **0–1 strong signals** → the pain is not budget-worthy. Drop the
  concept; do not reformulate it and re-interview.
- **2–4** → real but not yet a business. Narrow to whichever single
  workflow produced the signals and re-test.
- **5+** → proceed to B6/B7: identify the named buyer and design the
  smallest deliverable that can be sold.

**Also test B9 in the room, not at a desk.** Ask directly: *"Has a
Microsoft partner already pitched you something like this?"* The
competitive set is not Microsoft itself — it is the thousands of partners
selling Copilot adoption and deployment. Five candidate spaces have
already been found occupied today by assuming they were empty; this one
gets checked with the customer rather than assumed either way.

**Conflict-of-interest boundary — non-negotiable.** The obvious first
contacts are the operator's employer and its direct competitors. The
employer's internal materials, data and cases are not an input to this
business, and interviewing inside a competitor about processes learned at
the employer is a real professional risk, not a formality. Interviews
must stay at the level of the operator's own professional expertise.

### Standing warning carried over from RL-1

Having domain knowledge in an area is **not** a reason to build a product
for it. Verify the economics of a specific repeated task first. Turning a
topic into a product before checking who pays is precisely the failure
mode RL-1 documented.

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
