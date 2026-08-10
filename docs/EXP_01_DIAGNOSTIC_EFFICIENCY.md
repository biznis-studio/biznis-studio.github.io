# EXP-01 · Diagnostic efficiency

**The question, and it replaces everything technical:**

> Can an AI-guided diagnostic procedure **reduce the number and cost of
> observations** required to identify a manufacturing root cause, compared with
> conventional RCA and with generic Copilot?

**If no, the Microsoft architecture is irrelevant** and POC-00/POC-01 should
never be run. If yes, *then* it is worth asking what it should be built on.

**Needs no tenant, no licence, no Power Platform, no purchase.** Thirty closed
complaints and a stopwatch.

---

## 1. What is actually being claimed

Not *"we know more causes"* — existing eQMS knows more.
Not *"AI finds the root cause"* — shipping since 2026.

> **Control of the information sequence.** At each step, choose the observation
> that removes the most remaining hypotheses for the least cost.

This is differential diagnosis, and it has a measurable quantity:

> **Hypothesis reduction per unit of observation cost.**

That number is the product claim. If it is no better than what an experienced
person already does, there is no product — and that is a legitimate outcome
reached in days rather than months.

---

## 2. Cases

**30 closed complaints with a recorded, confirmed cause.**

| Rule | Why |
|---|---|
| Selected by **someone other than the operator of arm 3** | otherwise the sample is chosen to fit |
| Selection by a mechanical rule — e.g. *all complaints in months X–Y* | not "interesting ones" |
| Mixed categories, not only dimensional | one defect family would flatter the catalogue |
| At least 8 where the recorded cause was **initially wrong** or the case reopened | these are where sequencing matters most |
| The recorded cause is **stripped from the packet** | it is the answer key |

**Each packet contains only what was known at the start:** customer, product,
defect description, quantity, delivery date, and any photograph taken at intake.
Nothing gathered during the original investigation.

---

## 3. Arms

**Reframed 2026-08-10.** The first version pitted the tool against the
experienced engineer, as a contest. That is the wrong question and it would have
produced a useless answer — of course an experienced engineer investigates well.
**The purpose is not to beat anyone. It is to make the work easier and to let it
be done by someone who is not the senior specialist.**

The real problem is the one in front of us: **the experienced people left.**
So the question is whether their method survives their absence.

| Arm | Who | What it represents |
|---|---|---|
| **1 · Senior, no tool** | experienced quality engineer, fishbone/5-Why | **how it used to be** — today's quality and today's cost |
| **2 · Junior, no tool** | someone with under ~2 years in the role | **what actually happens now** when the senior is gone. The real baseline. |
| **3 · Junior, with tool** | same experience level as arm 2, instructions + catalogue | **the claim** |
| **4 · Senior, with tool** *(optional)* | | does it help the person who is already good, or only slow them down? |
| **5 · Plain Copilot** *(cheap control)* | no instructions | what a company gets free today |

**The primary comparison is arm 3 against arm 1.** Not to beat it — **to reach
it.** If a junior with the tool investigates roughly as well as a senior without
one, the method has transferred, and that is the whole proposition.

**Arm 2 measures the pain.** The gap between arms 1 and 2 is what the departure
of experienced people costs today. If that gap is small, there is no problem to
solve and no product — regardless of how well arm 3 performs.

**Arms must not share an operator on the same case.**

**Contamination warning, and it is serious.** Claude built the catalogue from
this company's data and has seen several of these complaints. **Claude must not
select cases and must not operate arm 3 on any case it has seen.** Any case
discussed in this project before 2026-08-10 is excluded outright.

---

## 4. The mechanic

For each case, in each arm, the operator may **request observations one at a
time**. A referee holding the closed file answers from the record — or answers
*"not recorded"*, which is itself a result.

Each request is logged with its cost class:

| Class | Examples | Weight |
|---|---|---|
| **0 · free** | already in the record: parameters, quantities, dates | 0 |
| **1 · cheap** | look at the part, ask the operator, check the order | 1 |
| **2 · moderate** | measurement, second gauge, campaign data sorted | 3 |
| **3 · expensive** | metallography, die teardown, thermal camera, material analysis | 10 |

Weights are declared **now**, before any data, and are not tuned afterwards.

**After every observation the operator states the remaining candidate causes.**
That list is the measurement — it produces the reduction curve.

Stop when the operator names a confirmed cause, or gives up, or reaches 15
observations.

---

## 5. Metrics

**Primary:**

| Metric | Definition |
|---|---|
| **Cost to correct cause** | summed weights until the recorded cause is named |
| **Hypothesis reduction per unit cost** | (initial candidates − final) ÷ total weight |
| **Correct?** | matches the recorded cause: yes / partial / no |

**Secondary:**

- observations requested
- **expensive observations that did not reduce the candidate set** — wasted spend, and the number that converts to euros
- **wrong exclusions** — the correct cause eliminated at some point and later recovered, or not
- steps to conclusion, wall-clock time
- cases where the answer was *"not recorded"* — a measure of how blind the original investigation was

---

## 6. Pre-registered thresholds

Fixed before any data is seen.

**Gate zero — is there a problem at all?**

| Arm 1 vs arm 2 | Meaning |
|---|---|
| Gap **small** (junior ≈ senior) | **Stop.** Losing experienced people costs little here. Nothing to sell. |
| Gap **large** (junior much worse or much more expensive) | The problem is real and worth measuring |

Everything below is only read if the gap is large.

| Comparison | Refuted if | Supported if |
|---|---|---|
| **Arm 3 vs arm 1** — did the method transfer? | arm 3 closes **< 40 %** of the arm 1–2 gap | arm 3 closes **≥ 70 %** of the gap in both accuracy and cost |
| Arm 3 vs arm 2 — what the tool adds | no improvement over the junior alone | clear improvement in both |
| Wasted expensive observations | arm 3 ≥ arm 2 | arm 3 **< half** of arm 2 |
| Arm 4 vs arm 1 — does it hinder the expert? | senior is **slower** with the tool | senior no slower, ideally faster |

**Arm 4 matters more than it looks.** A tool that helps juniors but irritates the
people who decide whether to buy it does not get adopted.

**The outcome that ends it is now different, and better.** Not *"the senior is
good"* — the senior was always good. It ends if the **gap between senior and
junior is small**, because then experience is not what makes the difference, and
transferring it is worth nothing.

---

## 7. What would make the result invalid

- Cases chosen by whoever operates arm 3
- The recorded cause visible in a packet
- The same person running two arms on one case
- Weights adjusted after seeing results
- Fewer than 20 usable cases
- Arm 1 operated by someone inexperienced — that is a straw man and the result
  would be worthless in the direction we would most like it to fail

---

## 7b. On "saving personnel cost" — say it accurately

The internal goal is real: the same work done by someone less senior, and less of
it. That is what makes it worth paying for.

**But it must not be said that way to the people running the test.** An
investigation whose participants believe it is measuring whether they can be
replaced does not produce clean data, and the belief is not even accurate — what
is being measured is whether **method** transfers, not whether people are
redundant.

This is also consistent with what we already commit to publicly: *we do not
promise AI replaces people.* The defensible version, internally and externally:

> The same case handled correctly by whoever happens to have it — not only by the
> one person who has done it for fifteen years.

That claim is honest, it is what the experiment measures, and it happens to be
what has commercial value.

---

## 8. What this deliberately does not test

Deployment · Microsoft architecture · price · willingness to pay · adoption ·
knowledge accumulation over time.

**One question. If it fails, none of the others matter.**
