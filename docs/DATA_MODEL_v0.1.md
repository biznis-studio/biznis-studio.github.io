# Data model v0.1 — what lives in Dataverse, what lives in SharePoint

Precedes `PRODUCT_ARCHITECTURE_v0.2.md`. Runtime decided: **Copilot Studio agent
+ Power Platform**, per-tenant deployment.

---

## 1. The splitting rule

Not a list of fields — a test that answers every future field without argument.

> **Dataverse** if a flow, a view, or an aggregate ever has to make a decision
> from it.
> **SharePoint** if a human or the agent reads it as content.

Two control questions:

- *"Would I ever filter, count, or trigger on this?"* → Dataverse.
- *"Is this a photo, a mail, a protocol, a drawing?"* → SharePoint.

**A field may be referenced from both, but stored once.** Duplication is how
these models rot: two copies, one gets updated, nobody knows which is true.

---

## 2. Dataverse — four tables

Three are obvious. **The fourth is the product.**

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
| **`Discriminator`** | **how to confirm *this* one rather than the one that looks the same — the core IP** |
| `Mechanism` · `Prevention` · `Detection` · `Priority` | |
| `Status` | Approved / Proposed / Rejected |
| `SourceCase` | lookup → `Case` — which case produced it |

### 2.3 `Observation` — what was actually seen

One row per observation. **Not prose in a field.**

| Column | Note |
|---|---|
| `Case` | lookup |
| `Text` | "wooden bearer intact, deformation a smooth long wave" |
| `ObservedOn` · `ObservedBy` | |
| `Cost` | choice: record / visual / measurement / **expensive test** |
| `EvidenceDocument` | url into SharePoint, optional |

`Cost` exists so the question *"how many expensive tests did we order, and did we
need them?"* is answerable by query rather than by memory. That number is the
value claim.

### 2.4 `CauseAssessment` — **the table that is the product**

For a case, for each candidate cause: is it excluded, confirmed, or still open —
**and which observation decided it.**

| Column | Note |
|---|---|
| `Case` | lookup |
| `Cause` | lookup |
| `Verdict` | Excluded / Confirmed / Open |
| `DecidedBy` | **lookup → `Observation`** |
| `DecidedOn` | |

**Why this is the core.** Every QMS stores *root cause: X* as a text field.
None stores **what was ruled out and by which observation**. That single table
delivers four things nothing else does:

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
