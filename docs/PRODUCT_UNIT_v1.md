# Product unit v1 — what the customer buys, and what arrives in two days

Written 2026-08-11. Replaces the "complaint agent" framing, which was too narrow
and put us in a fight with QMS vendors we cannot win.

**Test this document has to pass:** if we cannot say concretely what is bought and
what exists 48 hours after signature, we do not have a product.

---

## 1. Why this does not compete with a QMS

**A QMS is a system of record.** It holds what was decided, by whom, when, with
what evidence, and proves it to an auditor.

**The professional work happens somewhere else.** Assessing whether a deviation
is acceptable, writing the answer to the customer, preparing for an audit,
updating an FMEA after a complaint — that is done in **Word, Excel, Outlook,
Teams, and in someone's head.**

That is exactly where Copilot already sits.

| | QMS | Us |
|---|---|---|
| Side of the process | recording the decision | **making and drafting it** |
| Where it lives | its own application | **the tools the work is already done in** |
| What it needs from the customer | migration, admin, training | **their existing documents** |
| Question it answers | *what was decided?* | *what should be decided, and on what basis?* |

**Consequence for positioning:** we never say "instead of your QMS". We say
*"before the QMS entry exists"* — the reasoning and drafting that precedes the
record.

**Status: INFERENCE.** It follows from what a QMS is and where Copilot runs. It
is not customer evidence, and no customer has confirmed they experience the split
this way.

---

## 2. The product unit

**One pack = one profession's decision layer, delivered into the customer's own
Microsoft 365.**

Not a system. Not a migration. Not a licence to a platform of ours.

### What the customer buys

| Component | What it is | Ours or theirs |
|---|---|---|
| **Domain knowledge model** | the terminology, categories, causal structure and evidence rules of the profession | **ours** — this is the IP |
| **Decision procedure** | the ordered method: what to establish first, what discriminates, what may not be concluded | **ours** |
| **Agents** | 1–3 agents in their Copilot, carrying the procedure | **ours** |
| **Validation set** | 10–15 scenarios with expected behaviour, run as an acceptance test | **ours** |
| **Their documents** | standards, work instructions, drawings, past cases | **theirs, and they stay theirs** |
| **Update mechanism** | how a new finding gets into the knowledge, and who approves it | **ours as method, theirs as governance** |

### What exists 48 hours after signature

| Day | Step | Who |
|---|---|---|
| **0** | Written-knowledge check: does what the pack needs exist in writing? | us, 2 h |
| **1** | Their documents placed where Copilot can read them | them, guided |
| **1** | Agent installed in their Copilot | us, 1 h |
| **1** | **Acceptance test run in front of them** — the validation set, scored | us, 1 h |
| **2** | Terminology adjusted to their words, retest | us, 2–3 h |
| **2** | Handover, and the "what it cannot do" sheet | us, 1 h |

**Delivered:** a working agent in their tenant, a scored acceptance test they
watched, and a written list of what it will refuse to do.

**Not delivered:** any claim about time saved. That is theirs to measure, and the
measurement kit is a separate, priced item.

### The qualifying gate, and it is refused business if it fails

> **If the knowledge does not exist in writing, the pack cannot be delivered in
> two days.** Then what is sold first is a **knowledge structuring engagement**,
> at a fixed price, and the pack follows.

Selling a two-day pack into a company whose know-how is in people's heads
produces a disappointed customer and a bad reference. This gate is the difference
between a product and a rescue project.

---

## 3. Five candidate packs for Quality

Ordered by how far they sit from a QMS — the first is furthest, and therefore
safest.

### P1 · Posúdenie odchýlky *(deviation / concession assessment)*

**The task:** a part is out of specification. Ship it, rework it, scrap it, or ask
the customer? Needs the drawing, the standard, the customer's specific
requirements, and what was decided in comparable cases.

**Frequency:** daily to weekly. **Stakes:** high — a wrong concession is a
customer escalation; an unnecessary scrap is money.

**Why not a QMS:** the QMS records the concession. It does not help you reach it.

**Delivered output:** a structured assessment — what the deviation is, which
requirement it touches, what was decided before in comparable cases, what is
missing to decide, and a draft of the request to the customer.

### P2 · Príprava na zákaznícky a certifikačný audit

**The task:** an audit is coming. Which evidence for which requirement, what was
found last time, what was promised and whether it was done, where the gaps are.

**Frequency:** several times a year, always under time pressure.

**Why not a QMS:** the QMS holds the records. Assembling them into "we are ready
for this audit" is manual work every single time.

**Delivered output:** a readiness list by requirement, with the location of the
evidence and named gaps.

### P3 · Odpoveď zákazníkovi na reklamáciu

**Deliberately narrow: the response, not the investigation.**

**The task:** the cause is known. Now write it in the customer's format, in the
right tone, with the right evidence and the right degree of commitment — a
response that does not concede more than the facts support.

**Frequency:** every complaint. **Stakes:** a badly worded 8D creates obligations
that outlive the defect.

**Why not a QMS:** the QMS stores the 8D. Writing it is a Word document under
deadline.

**Delivered output:** a draft in their format, with the excluded causes and their
evidence — and a warning where the text concedes more than the record supports.

### P4 · Aktualizácia FMEA a kontrolného plánu po reklamácii

**The task:** a complaint revealed a failure mode. Is it in the PFMEA? Should the
control plan change? Which other products share the mechanism?

**Frequency:** should be every complaint. **Reality:** it is the step that gets
skipped, which is why the same defect returns.

**Why not a QMS:** this is the loop nobody closes, and no system forces it.

**Delivered output:** a proposed PFMEA row change with justification, and a list
of other products sharing the mechanism.

### P5 · Zaškolenie nového človeka na proces

**The task:** a new quality engineer must reach the point of handling a case
alone.

**Frequency:** rising, and it is the reason this project started.

**Why not a QMS:** training material is documents. Nothing turns them into a
guided path through real work.

**Delivered output:** a guided path through the real process, with the questions
a senior would ask, and where the answers live.

---

## 4. Ranking, and it is a judgement, not evidence

| Pack | Distance from QMS | Frequency | Deliverable in 2 days | Verdict |
|---|---|---|---|---|
| **P1 deviation** | far | daily | yes — needs drawings and standards | **strongest candidate** |
| **P3 response** | far | every complaint | yes — needs past 8Ds and the format | **strong, and closest to what we already built** |
| **P2 audit prep** | medium | seasonal | yes | good, but bursty demand |
| **P4 FMEA update** | medium | should be constant | needs their PFMEA | valuable, harder to deliver fast |
| **P5 onboarding** | far | rising | yes | the real pain, hardest to price |

**P1 and P3 first.** P3 reuses most of what already exists — the catalogue, the
discriminators, the 8D output contract — and P1 is the highest-frequency
professional decision in a quality department that no QMS assists.

---

## 5. What is not established

- **No customer has been asked** whether any of these five is a paid problem.
- **The QMS split in §1 is inference**, not observed behaviour.
- **The two-day delivery is a design target**, never executed once.
- **Pricing is absent** — and the competitive audit put the eQMS ceiling at
  roughly €9–20 per user per month, which constrains what a pack can cost.
- **The claim "Copilot becomes a professional" remains untested.** What is
  established is narrower: with a domain catalogue attached, Copilot refused to
  conclude without evidence where plain Copilot did not (2026-08-09/10, nine
  scenarios and three real complaints).

**The next step is not another pack and not architecture. It is asking one
quality manager outside this company whether P1 or P3 is a problem they would pay
to remove.**
