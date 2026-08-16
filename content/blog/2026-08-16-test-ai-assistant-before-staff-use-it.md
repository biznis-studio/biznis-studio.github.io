title: How to test an AI assistant before you let staff use it
description: Satisfaction scores tell you a conversation felt fine, not that the answer was right. Here is the test that decides if it can be trusted with real work.
---
Most internal AI assistants are tested the same way: the person who built
it asks a handful of questions, the answers read well, and it ships. That
is not a test. It is a demo run by the one person who already knows which
questions work.

The advice you find for testing assistants comes mostly from
customer-facing chatbots — conversation completion rates, satisfaction
scores, a pilot group. Those measure whether the conversation felt fine.
For work that has consequences, the only question that matters is whether
the answer was **right**, and nobody's five-star rating settles that.

## Start with the question that decides everything

Before writing a single test case, answer this about the work you want to
hand over:

> **Can you say in advance what would prove the answer wrong?**

If you can — a measurement, a record, a document, a photograph, a field in
a system — the work can be tested, and therefore trusted. If you cannot,
no amount of testing will help, and the assistant will stay where most of
them are: rewriting emails and summarising meetings.

This is not our idea. Andrej Karpathy put the general form of it plainly:
classical software automates what you can *specify*; models automate what
you can *verify*
([karpathy.bearblog.dev](https://karpathy.bearblog.dev/verifiability/)).
That is his argument about how AI progresses, not a measurement of ours,
and we are not presenting it as one. But it converts neatly into a
purchasing decision: the processes worth automating first are the ones
where being wrong leaves a trace.

## Build the test set out of cases you have already closed

The useful test material is sitting in your archive. Take real cases that
are finished — a warranty claim that was settled, an invoice discrepancy
that was resolved, a specification query that got an answer, a customer
complaint with a known root cause.

For each one, write down before you test:

- **the inputs** the assistant is allowed to see, exactly as a colleague
  would have received them;
- **the outcome that actually happened**, agreed by the person who owns
  that work;
- **the observation that distinguishes it** — the thing that, had it come
  back the other way, would have made a different answer correct.

That last line is the one people skip, and it is the one that turns a
subjective read into a test. Without it you can only ask "does this look
reasonable?", which is the same soft question you were trying to escape.

## Mark some cases as blocking

Not every case carries the same weight. A few of them are ones where a
wrong answer costs real money, sends someone to do an expensive test they
did not need, or gives a customer a commitment you cannot keep.

Mark those as **blocking**: if one of them fails, the assistant is not
released. Not "released with a note in the handover document" — not
released. A rule you have never seen stop anything is not a rule, so the
first time one fails, let it stop the release. That single event is what
makes everyone treat the rest of the set seriously.

## Grade the answers with someone who did not write the material

Whoever produced the knowledge base will read its answers charitably. They
know what was meant, so they see it in the text. Hand the test results to
someone who was not involved, give them the expected outcome and nothing
else, and let them mark each answer as matching, not matching, or unclear.
"Unclear" is a real category and should be counted — an answer nobody can
grade is an answer nobody can act on.

## What a testable answer looks like

Three properties make the difference between an answer that takes twenty
minutes to check and one that takes one:

**It says what it relied on.** Which document, which record, which
paragraph. Checking then means opening one reference rather than
re-deriving the whole thing.

**It says what it does not know.** An explicit "not established" beats a
confident sentence covering the same gap, because it tells the reader
precisely where to look.

**It keeps the order.** Expert work is a sequence — the cheap check before
the expensive one. An answer in the wrong order sounds just as plausible
and sends someone to run a costly test before they have read the record on
their own desk.

## Run the set again after every change — including changes you did not make

You will edit the knowledge, someone will add a rule, and one day your
tenant's provider will swap the model underneath your assistant without
asking. Today that means behaviour changes quietly and nobody can say
whether it improved. With a test set, it means you re-run the cases and
read the result.

That is the actual value of the set: it is the only thing that can take
"done" back.

## Where we come in

We take **one process** that repeats in your company and put it into a form
that can be checked — running inside the Microsoft 365 you already own and
have already approved, not on a new platform with another monthly bill.
The acceptance set described above is part of what you receive: the cases
are yours, you approve them, and the check runs on every later change.

What that proves is bounded, and worth stating: a passing set proves the
behaviour on those cases, on that version. It says nothing about cases
nobody wrote down. That is exactly why the set is built from your real
closed work, and why it grows every time reality produces a case the set
did not have.

A review of a single process has a fixed price, and if it shows the work
is not verifiable enough to hand over, we will say so and you will have
that in writing. [Tell us which process it is](../index.html#kontakt) and
we will tell you whether it passes the question at the top of this page.
