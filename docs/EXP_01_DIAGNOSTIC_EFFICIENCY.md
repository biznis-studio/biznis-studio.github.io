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

| Arm | Who / what | Note |
|---|---|---|
| **1 · Conventional** | experienced quality engineer, fishbone/5-Why, no AI | the real benchmark, not a straw man |
| **2 · Generic Copilot** | plain, no instructions, no catalogue | what a company gets today for free |
| **3 · Our procedure** | instructions + catalogue | the claim |

**Arms must not share an operator on the same case.** A person who has run arm 3
on a case cannot run arm 1 on it.

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

| Comparison | Refuted if | Supported if |
|---|---|---|
| Arm 3 vs arm 1 (experienced human) | cost to correct cause **≥** arm 1 | **≤ 60 %** of arm 1 |
| Arm 3 vs arm 2 (plain Copilot) | accuracy not higher **and** cost not lower | accuracy higher **and** cost lower |
| Wasted expensive observations | arm 3 ≥ arm 1 | arm 3 **< half** of arm 1 |
| Correctness | arm 3 below arm 1 | arm 3 **≥** arm 1 |

**The decisive comparison is arm 3 against arm 1, not against arm 2.** Beating
plain Copilot proves only that instructions help. **Beating an experienced
quality engineer on cost while matching accuracy is the product.**

**And the outcome that ends it:** if arm 1 is as fast, as cheap and as accurate,
the concept is dropped. An experienced person doing this well already is not a
market — it is a reason there is no market.

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

## 8. What this deliberately does not test

Deployment · Microsoft architecture · price · willingness to pay · adoption ·
knowledge accumulation over time.

**One question. If it fails, none of the others matter.**
