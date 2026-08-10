# POC-01 · `GetCase()` — experiment specification

**Status of everything upstream:** the data model in `DATA_MODEL_v0.1.md` is a
**proposal**. `PRODUCT_ARCHITECTURE_v0.2.md` is **not written and must not be**
until this experiment returns.

**We do not have a product.** We have a technical proposal and several
unverified differentiation hypotheses. This document tests one thing only.

---

## 0. The three questions, kept apart

They were mixed for weeks. This experiment answers **only the first**.

| Question | Answered by |
|---|---|
| **Technical feasibility** — can it be built on the Microsoft stack? | **This experiment** |
| **Product differentiation** — will a customer pay despite an existing QMS? | Customer evidence. Not started. |
| **IP** — do we hold something defensible competitors do not provide the same way? | Competitive audit (Intelex, ETQ, Babtec, MasterControl, Plato). Not started. |

A pass here means *buildable*. It means nothing about the other two.

---

## 1. The decision this settles

> Does a Copilot Studio **action** return the **exact, current, complete** state
> of one named case — or must we fall back on semantic retrieval, which is the
> wrong instrument for a database lookup?

**If it passes:** the case is fetched by action, knowledge is reserved for the
catalogue, and the architecture has a real foundation.
**If it fails:** the proposed architecture is rebuilt, not patched.

---

## 2. Explicitly not tested here

Time saved · user acceptance · deployment hours · willingness to pay ·
competitive differentiation · catalogue quality · multi-domain.

Adding any of these makes the result unreadable.

---

## 3. Setup — the minimum

| | |
|---|---|
| Tenant | one with Copilot Studio and Dataverse. **Prerequisite; we do not have one.** |
| `Case` table | 20 rows, real or realistic, per `DATA_MODEL_v0.1.md` §2.1 |
| `Cause` table | 5 rows is enough for T5 |
| `CauseAssessment` | empty at start |
| Agent | Copilot Studio agent, no knowledge sources at all — **isolates the action** |
| Action | `GetCase(CaseNumber) → structured record` |
| Second action | `CreateCauseAssessment(Case, Cause, Verdict, DecidedByObservation)`, marked consequential |

**Deliberate design:** knowledge sources are switched **off** during T1–T4. If the
agent has both, a correct answer proves nothing — we would not know which path
produced it.

**Case numbers must include a substring trap.** Among the 20, include
`C-2026-00417` and `C-2026-01417`, and `2334` and `12334`. Semantic retrieval
confuses these; a lookup does not. This pair is the sharpest single test in the
set.

---

## 4. Tests and pre-registered thresholds

Thresholds are fixed before any data is seen. They are not adjusted afterwards.

| # | Test | Method | PASS | FAIL |
|---|---|---|---|---|
| **T1** | **Exact identification** | Ask for each of the 20 cases by number, once, in a fresh conversation | **20/20** exactly the requested case, including both substring traps | any wrong case, or any "I found several similar" |
| **T2** | **Field completeness** | For 10 cases, check every field of §2.1 is present | **10/10** complete | any silently missing field |
| **T3** | **Freshness** ⚠️ | Change `Status` in Dataverse, ask within 60 s, fresh conversation | **10/10** show the new value on the **first** ask | any stale value |
| **T4** | **Latency** | 20 calls, measure end to end | **p95 ≤ 8 s** | p95 > 8 s |
| **T5** | **Write-back** | Agent creates a `CauseAssessment` | row created with all four fields correct **and** the user is asked to confirm before the write | writes without confirmation, or writes wrong values |
| **T6** | **Permissions** ⚠️ | User without rights to case X asks for X | refusal or empty, **no field values leaked**, in **5/5** attempts | any leakage of any field |
| **T7** | **Non-existent case** | Ask for `C-2026-99999` | states it does not exist, **5/5** | invents one, or silently returns the nearest match |
| **T8** | **Unavailable source** | Break the connection, ask | states the failure, **5/5** | fabricates an answer from context |

**T3 and T6 are blocking.** Either one failing stops the architecture regardless
of everything else:

- **T3** because a case register that shows yesterday's status is worse than no
  register — people will trust it and be wrong.
- **T6** because "we add no new access path" is the security claim the whole
  product rests on. If it leaks once, the claim is gone and cannot be repaired
  by anything downstream.

---

## 5. Second run — the comparison

Repeat **T1 and T3 only**, with the action removed and the `Case` table added as
Dataverse **knowledge** instead.

**Purpose:** to establish with evidence, not assumption, that semantic retrieval
is the wrong instrument here. **Expected — and recorded as a prediction so it can
be wrong:** knowledge passes T1 partially and fails the substring traps, and
fails T3 because indexing is not immediate.

If knowledge passes both, the design assumption *"action for the case, knowledge
for the catalogue"* was unnecessary and the architecture simplifies.

---

## 6. What each outcome means

| Result | Consequence |
|---|---|
| All pass | Architecture has a foundation. Proceed to POC-02: flows, closure rule, the loop. |
| T3 fails | **Stop.** Neither action nor knowledge gives current state → the case register cannot live in the agent's reach and the interaction model must be redesigned. |
| T6 fails | **Stop.** Security claim invalid. Nothing downstream matters. |
| T5 fails | Write-back moves to an agent flow triggered by the human; the agent proposes text only. Architecture survives, reduced. |
| T1 fails but knowledge passes | Reverse the design assumption; document it. |
| T4 fails only | Usable but unpleasant; measure again with a larger table before deciding. |

---

## 7. Recording

One row per call: test, case number, expected, returned, latency, verdict, note.
**Raw log kept** — a summary alone cannot be re-checked later.

**Deployment time is recorded from the first minute**, split by step, per
`poc/03_deployment_meranie.md`. This experiment is also the first real
measurement of §14a, and that data is as valuable as the pass/fail.

---

## 8. Blocking prerequisite

A tenant with Copilot Studio, Dataverse and rights to create tables, actions and
an agent. **We do not currently have one.** The Copilot account used on
2026-08-09/10 is not a work tenant — the interface offered "Buy Microsoft 365",
and SharePoint and OneDrive for Business were not reachable.

Until that exists, this specification cannot be executed, and **no further
architecture should be written on top of it.**
