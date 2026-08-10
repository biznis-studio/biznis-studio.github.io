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

> By which mechanism does the agent obtain the **exact, current, complete** state
> of one named case?

**Amended 2026-08-10.** The first version asked only *action vs knowledge*. That
presupposed our own design — that a custom `GetCase()` action is the answer — and
would have steered the experiment toward the thing we invented. Microsoft
documents a **Dataverse MCP server in Copilot Studio** through which an agent can
reach Dataverse tables directly. **Three arms, not two:**

| Arm | Mechanism | If this wins |
|---|---|---|
| **A · Native** | Dataverse MCP / built-in Dataverse access | **We build no action at all.** A chunk of assumed work — and of assumed IP — disappears. |
| **B · Action** | Custom `GetCase()` API plugin | Our original assumption; costs build and maintenance |
| **C · Knowledge** | Dataverse table as knowledge source | Simplest, and probably wrong for a lookup — to be shown, not asserted |

**Arm A is tested first.** If the platform already does this, building B is
waste, and finding that out after building it is the expensive order.

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
| Agent | Copilot Studio agent. **One arm enabled at a time** — never two, or the result cannot be attributed |
| Arm A | Dataverse MCP / native access configured to the `Case` table |
| Arm B | `GetCase(CaseNumber) → structured record` |
| Arm C | `Case` table added as Dataverse knowledge |
| Write test | `CreateCauseAssessment(Case, Cause, Verdict, DecidedByObservation)`, marked consequential |

**Deliberate design:** exactly one arm is enabled at a time, and during T1–T4 all
other sources are **off**. If the agent has two paths, a correct answer proves
nothing — we would not know which produced it.

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
| | *T6 in a trial environment tests the **mechanism** only. The security boundary that matters — real groups, real roles, real inheritance — exists only in the production tenant. **T6 is run twice**: once in the trial as a smoke test, once in the production tenant before any claim is made.* | | | |
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

## 5. Running the three arms

**T1 and T3 are run against all three arms.** T2, T4, T5, T7, T8 only against
whichever arm passes T1 and T3.

**Predictions, recorded in advance so they can be wrong:**

| Arm | T1 substring traps | T3 freshness |
|---|---|---|
| A native | pass | pass |
| B action | pass | pass |
| C knowledge | **fail** | **fail** — indexing is not immediate |

**If A passes:** arm B is not built. The custom action was our invention, not a
requirement, and dropping it removes build, maintenance and one deployment step.
**If C passes both:** the whole *action-for-the-case* assumption was unnecessary
and the architecture simplifies further than we expected.

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

## 8. POC-00 — provisioning, and it is its own test

The environment is not a prerequisite to be arranged and forgotten. **Whether it
can be stood up at all, and in how long, is the first measurement of §14a.**
Record the time for each step.

| # | Step | Note |
|---|---|---|
| 1 | Obtain a **Copilot Studio trial** | availability can be restricted by an administrator |
| 2 | Create a **Trial Power Platform environment** | trial environments expire after ~30 days and take the agents and data with them — **the POC must finish inside that window, and nothing of value may live only there** |
| 3 | Enable the **Dataverse datastore** at creation | Copilot Studio requires a Dataverse datastore for a full agent |
| 4 | Confirm the environment appears in the Copilot Studio switcher | if it does not, stop here — nothing downstream will work |
| 5 | Create the `Case` table | minimum columns per `DATA_MODEL_v0.1.md` §2.1 |
| 6 | Create one record | |
| 7 | Confirm the record can be read deterministically by **arm A** | the cheapest possible go/no-go |
| 8 | Only then run POC-01 | |

**Environment choice, decided:**

| Environment | POC-01 | T6 | Verdict |
|---|---|---|---|
| Copilot Studio trial + own Dataverse environment | ✅ | mechanism only | **start here** — no IT dependency |
| M365 Developer tenant | maybe | artificial | **only after** confirming the subscription actually carries the Copilot Studio entitlements and capacity; an E5 developer subscription is not evidence that it does |
| Constellium production | later | **real** | for T6 and for deployment measurement, once the mechanism is proven |

**Until step 4 passes, no further architecture is written.**
