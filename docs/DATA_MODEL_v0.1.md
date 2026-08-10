# Data model v0.1 — what lives in Dataverse, what lives in SharePoint

Precedes `PRODUCT_ARCHITECTURE_v0.2.md`. Runtime decided: **Copilot Studio agent
+ Power Platform**, per-tenant deployment.

---

## 1. The splitting rule

Not a list of fields — a test that answers every future field without argument.

> **Dataverse** is the system of truth for **structured, relational and stateful
> data** over which decisioning, automation, validation, reporting or aggregation
> is performed.
> **SharePoint** is the repository for **document content, evidence and
> artefacts**, whose primary value is their content and their file form.

**Corrected 2026-08-10.** The first version said "SharePoint if a human or the
agent reads it as content". That is a heuristic, not a rule: *being read by the
agent is not a property of the data*. The agent can read structured data through
an action. The rule must follow the **semantics of the data**, not its consumer.

**A field may be referenced from both, but stored once.** Duplication is how
these models rot: two copies, one gets updated, nobody knows which is true.

---

## 2. Dataverse — four tables

Four tables plus `Evidence`. `CauseAssessment` is the load-bearing one —
see §8 before calling it differentiation.

### 2.1 `Case` — the complaint

State machine and everything a flow drives from.

| Column | Type | Note |
|---|---|---|
| `CaseNumber` | text | 2334 |
| `Customer` | text / lookup | |
| `Product` | text | profile number |
| `DefectCategory` | choice | 35 values |
| `ReceivedOn` · `DueCause` · `DueForm` · `DueEffectiveness` | date | flows compute the three due dates |
| `Owner` | user | |
| `Status` | choice | D0…D8, Effectiveness, Closed |
| `QtyAffected` · `QtyDelivered` | number | share is calculated, never stored |
| `ConfirmedCause` | **lookup → `Cause`** | never free text — see §4 |
| `EffectivenessResult` | choice | Effective / Not effective / Pending |
| `EvidenceFolderUrl` | url | the one link into SharePoint |

### 2.2 `Cause` — the catalogue

121 rows at delivery.

| Column | Note |
|---|---|
| `Name` · `Category` | |
| **`Discriminator`** | how to confirm *this* one rather than the one that looks the same |
| `Mechanism` · `Prevention` · `Detection` · `Priority` | |
| `Status` | Approved / Proposed / Rejected |
| `SourceCase` | lookup → `Case` — which case produced it |

### 2.3 `Observation` — the finding

One row per observation. **Not prose in a field.**

| Column | Note |
|---|---|
| `Case` | lookup |
| `Text` | "wooden bearer intact, deformation a smooth long wave" |
| `ObservedOn` · `ObservedBy` | |
| `Method` | choice: record / visual / **measurement** / **physical test** / document / interview |
| `Cost` | choice: free / cheap / **expensive** |

### 2.3b `Evidence` — the artefact that supports it

**Separated from `Observation` on 2026-08-10, and the distinction matters.**
An observation is a *finding*; evidence is an *artefact* that supports it. One
observation may rest on several artefacts, and one artefact may support several
observations.

| Column | Note |
|---|---|
| `Observation` | lookup |
| `Type` | photo / measurement protocol / process record / customer document / other |
| `FileUrl` | → SharePoint |

**Why the separation earns its place.** Collapsing them makes two questions
unanswerable that are worth money:

- *On what were our decisions actually based — measurement, photograph, test,
  document, or someone's recollection?*
- *How many expensive tests did we order, and did the case turn on them?*

The chain is therefore **Cause → CauseAssessment → deciding Observation →
Evidence**, never CauseAssessment → Evidence.

### 2.4 `CauseAssessment` — the decision trajectory

For a case, for each candidate cause: is it excluded, confirmed, or still open —
**and which observation decided it.**

| Column | Note |
|---|---|
| `Case` | lookup |
| `Cause` | lookup |
| `Verdict` | Excluded / Confirmed / Open |
| `DecidedBy` | **lookup → `Observation`** |
| `DecidedOn` | |

**What it delivers** — see §8 for what is and is not novel about it:

1. **A defensible 8D.** The "excluded causes" section stops being prose and
   becomes a record with evidence attached to each exclusion.
2. **Catalogue improvement, measurable.** Query: *which discriminator actually
   decides most cases?* Discriminators that never decide anything are dead
   weight and can be rewritten.
3. **The knowledge loop, closed by data.** A case that reaches `Confirmed`
   against no existing `Cause` is precisely the signal that a cause is missing —
   the thing that happened by hand on 2026-08-09.
4. **Repeat detection.** *This customer, this category, this cause — how often?*
   That is systemic-cause analysis, produced as a side effect rather than as an
   annual exercise.

---

## 3. SharePoint — evidence only

One folder per case, linked from `Case.EvidenceFolderUrl`.

| Content | Why not Dataverse |
|---|---|
| Photos | binary, read by humans; the agent may read them if the surface allows |
| Customer claim, mails, CMR | documents |
| Measurement protocols | documents |
| Drawings, work instructions, standards | shared library, not per-case |
| Generated 8D output | document, produced at the end |

**No case state in SharePoint. No evidence rows in SharePoint.** SharePoint holds
files; Dataverse holds facts about them.

---

## 4. Two rules that must not be relaxed

**`ConfirmedCause` is a lookup, never text.** Free text cannot be counted, and
everything in §2.4 collapses without the relation.

**A case cannot reach `Closed` without:** a `ConfirmedCause`, at least one
`CauseAssessment` with `Verdict = Confirmed` carrying a `DecidedBy`, and at least
one with `Verdict = Excluded`. Whether that is enforced by business rule, flow
with revert, or approval gate is a POC question — **the rule itself is not.**

---

## 5. Where the agent fits

| Reads | How | Note |
|---|---|---|
| `Cause` catalogue | Dataverse knowledge | domain knowledge, changes slowly |
| The current case | **action, not knowledge** | structured and frequently changing — Microsoft's own guidance |
| Evidence documents | SharePoint knowledge | photos and protocols |

**Open POC question, and it is the decisive one:** whether Dataverse *knowledge*
retrieves a specific case deterministically enough, or whether the case must be
fetched by an **action** while knowledge is reserved for the catalogue. Design
assumption: **action for the case, knowledge for the catalogue.** To be tested,
not assumed.

---

## 6. POC — the smallest thing that proves the model

```
create case            → Dataverse row, flow sets three due dates
attach evidence        → SharePoint folder, url written back
agent reads case       → action or knowledge (the open question)
agent proposes         → observations and cause assessments
human confirms         → CauseAssessment.Verdict = Confirmed + DecidedBy
flow changes status    → validates §4 before allowing Closed
scheduled flow         → deadline and effectiveness detection
```

**Measured, not demonstrated:** person-hours to deploy, latency from write to
agent visibility, whether the closure rule holds, and whether a case that needs a
new cause is detected by the data or only by a person noticing.

---

## 7. Correction to the record

**A15 ("agent cannot write back — structural blocker") is withdrawn.** It was
true of one configuration — a declarative agent shipping no actions — and was
generalised into a platform limit. Across the Microsoft agent platform, write-back
is available through actions and agent flows. What remains open is *which runtime
and which mechanism*, and how it deploys per tenant. That is an architecture
question, not evidence that the product is impossible.

**New cost line for §14a**, and it is not small: the economics can no longer be
*M365 Copilot + our product*. It is **M365 Copilot + Copilot Studio capacity +
Power Platform / Dataverse + our deployment + our IP**. Agent flows consume
Copilot Studio capacity per action, and exhausted capacity can make an agent
unavailable. This must be priced before anything is offered to a customer.


---

## 8. Prior art — the differentiation claim, checked

**Checked 2026-08-10, at the owner's request, before treating `CauseAssessment`
as IP.**

**The earlier claim — "every QMS stores root cause as text; none stores what was
ruled out and by which observation" — is WITHDRAWN. It is false.**

Existing CAPA software already supports this conceptually. One vendor describes
it directly: engineers *"add contributing factors under each category with
evidence, **rule them in or out**, and document the progression directly in the
CAPA file."* Ishikawa, 5-Why and fault-tree structures with evidence attached are
standard, and **Is / Is-Not analysis** — recording explicitly what the problem is
*not* — is a decades-old quality technique, not an invention of ours.

**What may still be different — stated as hypotheses, not findings:**

| Hypothesis | Why it might hold | Status |
|---|---|---|
| **The discriminator is a reusable, maintained artefact**, not a fishbone redrawn per case | Standard practice builds the cause tree ad hoc for each complaint. A catalogue where each cause carries *how to tell it from the one that looks the same*, reused across cases, is a different object. | **UNVERIFIED** |
| **The catalogue receives feedback from outcomes** — which discriminators actually decide cases, which never do | Requires the assessment data to loop back into the knowledge, which is not the same as recording it per case | **UNVERIFIED** |
| **A confirmed cause with no catalogue match is a detected signal**, not something a person happens to notice | Turns knowledge growth from attention into a query | **UNVERIFIED** |

**Method limitation, stated so it is not over-read:** this check was one search
over vendor marketing pages, not product documentation or hands-on evaluation.
It is enough to withdraw the "nobody does this" claim. It is **not** enough to
conclude that the three hypotheses above are unmet by existing products.

**Consequence.** `CauseAssessment` is a sound data model and probably necessary.
It is **not** established as differentiation. The competitive comparison against
real CAPA products (Intelex, ETQ, Babtec, Plato, MasterControl and similar) is
now a required piece of work before any claim is made to a customer — and before
G8 can be argued.
