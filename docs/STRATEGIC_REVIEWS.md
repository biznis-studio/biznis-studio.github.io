# Strategic Reviews

This log exists because of a real failure mode the user identified
2026-07-27: an autonomous agent left to its own devices tends to optimize
the *current implementation* forever, without ever asking whether the
implementation itself is still the right bet. Tactical prioritization
(EBV-ranking the backlog, see ROADMAP.md) answers "what should I build
next, given this business model." A Strategic Review answers a harder
question: "is this business model still the best available option at all,"
and it must be willing to say no.

**Rule: never assume the current strategy is correct just because it's
already implemented.** A decision made 5 iterations ago with less data than
exists now has no special protection from being reversed.

## Process

Before any significant new investment of time, and at minimum weekly, run
a full Strategic Review answering all 10 questions below, grounded in real
data (product/tier counts, competition scores, traffic, revenue,
distribution status) — never a generic or hedged non-answer. Be willing to
recommend a radical change of direction if the analysis supports one.

1. Is the current business model still the best of all available options?
2. Is there a higher EBV if we changed the product, the target market, or
   the monetization method?
3. Is the current bottleneck real, or just a local/tactical problem?
4. Are we building assets, or just producing more content?
5. If we started from zero today, would we build this company the same way?
6. Which past decisions would we *not* make the same way today?
7. What would an experienced founder with a €0 budget and one person do?
8. What are three alternative strategies with higher expected EBV?
9. Why might this company fail even with excellent execution?
10. What is the single biggest systemic bottleneck in the whole company?

**Honest limitation on automation**: there's no LLM wired into the
scheduled GitHub Actions pipeline (no Anthropic/OpenRouter/Ollama key
configured — same constraint documented in ROADMAP.md for ebook prose). A
script can assemble the *data* a review needs (product tier breakdown,
indexing/traffic status, revenue status, competition scores) but the
actual judgment in questions 1-10 requires a real reasoning pass, so this
happens whenever a Claude Code session next works on this project, not as
a fully unattended cron job. Treat "it's been a week since the last dated
entry below" as the trigger to run the next one.

---

## Review — 2026-07-27 (first review)

**Data snapshot at time of review**: 19 pipeline runs, 85 deduplicated
keywords, 4,408 raw signals collected (HN/Wikipedia/npm/Stack Exchange/
GitHub, all free/no-auth). 28 products created; tiered this session into
7 `core`, 7 `lead_magnet`, 14 `retire_candidate` (rejected, never had a
live page). 14 pages live on GitHub Pages
(fwwk4pb868-afk.github.io/biznis). **0 pages confirmed indexed by Google.**
IndexNow (Bing/Yandex/Seznam/Naver/Yep only — never covered Google) has
returned 403 since 2026-07-27 with no known fix. 1 product listed on
Gumroad (pay-what-you-want), 0 confirmed sales, payout blocked on the
user's own Stripe KYC/business-status decision. 2 service offerings (web
dev, chatbot dev) added with zero case studies, zero leads, contact form
still falling back to a hidden mailto (Formspree endpoint not yet
provided).

1. **Is the current business model still the best available option?**
   Partially, but with an important caveat: the *product* choice (validated
   digital info-products in the freelancer-tools niche, plus custom
   services) is reasonably well-supported by real competitor pricing
   research done in iterations 14/18/19. But the *distribution and
   monetization* choice is weak: it depends on a chain of external account
   setups (Google Search Console, Gumroad KYC, Formspree) that only the
   human can complete, and none are done yet. A model that generates real
   revenue shouldn't have its entire critical path run through
   human-gated account setup with no fallback.
2. **Is there a higher EBV if we changed product, market, or monetization?**
   Possibly monetization method, yes. Gumroad + a bespoke landing page is
   the right call for a low-volume digital-goods seller, but it puts 100%
   of revenue behind Stripe KYC resolution the user hasn't completed in
   over a day of otherwise-fast iteration - suggesting friction, not just
   pending time. Worth an honest gut-check with the user about whether
   Gumroad's KYC requirement is actually going to resolve, or whether a
   lower-friction alternative (e.g. Ko-fi, which has historically had a
   lighter onboarding bar for individuals) should be evaluated as a
   fallback rather than waiting indefinitely on one path.
3. **Is the current bottleneck (distribution) real, or just local?**
   Real, and more structural than it first looks. It's not just "Search
   Console isn't verified yet" - it's that *every* high-leverage growth
   channel available to a zero-budget solo operator (organic search,
   social distribution, email, paid ads) requires either a Google account
   action or a new account this system is not permitted to create on the
   user's behalf. The honest bottleneck isn't "SEO," it's "how many
   external accounts is the human willing to personally set up," which is
   a bottleneck on the human's time/attention, not on anything buildable.
4. **Are we building assets, or just producing more content?** Genuinely
   mixed. The reusable design system, the PDF export pipeline, the
   markdown renderer, and the growing keyword/signals corpus are real
   compounding assets - every new product is now near-zero-marginal-cost
   to produce because of them. But 14 of 28 products (now rejected) were
   pure content with no reuse value, produced because a scoring pipeline
   ran, not because a market gap was identified - exactly the failure mode
   this session already caught and fixed (see ROADMAP.md's tiering
   section). The correction is real, but it happened after the fact, not
   before - a sign the ideation step still needs a "would a human actually
   pay for this" gate before content gets written, not just before it gets
   published.
5. **If starting from zero today, would we build this the same way?**
   No, on one point: this project spent real effort (competitor/niche/
   clustering agents, IndexNow integration, sitemap/RSS/schema.org
   markup) on SEO-adjacent infrastructure before confirming a single
   external distribution channel actually worked end-to-end. Sequencing
   "prove one visitor can find one page" before building 6 more agents on
   top would have surfaced the Google-indexing / IndexNow-403 problem
   weeks earlier in wall-clock terms.
6. **Which past decisions would we not repeat?** Building the second and
   third service offering's landing pages (web dev, chatbot dev) before
   there was any contact-form delivery mechanism live (Formspree pending)
   or any case study to show - those pages currently can't convert a
   visitor into a lead even if one arrived, and have no proof-of-work to
   justify the price a visitor would need to trust. Also: writing 3 more
   generic single-keyword ebooks in early iterations before the
   competitor-pricing research (iteration 18) existed to tell us that
   pattern doesn't sell - unavoidable given the ordering, but confirms
   research-before-content should be the default going forward, not the
   exception.
7. **What would an experienced €0-budget, one-person founder do right
   now?** Stop building anything new. Spend one sitting doing every
   pending human-gated task in one pass - Search Console verification,
   the Gumroad KYC form, the Formspree signup - because each is a
   15-minute task blocking potentially 100% of this system's revenue, and
   no amount of additional AI-driven building substitutes for them. Then
   watch real traffic/conversion data for at least a week before writing
   anything new.
8. **Three alternative strategies with higher expected EBV:**
   (a) Pause new product creation entirely until the human clears the 3
   pending account setups and at least one week of real traffic/analytics
   exists - de-risks every future decision with real data instead of
   inference from keyword scrapes.
   (b) Lead with the 2 validated freelancer "systems" as a tiny paid
   micro-catalog on a lower-friction platform (e.g. Ko-fi shop) in
   parallel with Gumroad, so revenue isn't gated behind one payment
   processor's KYC review.
   (c) Treat the custom services (web dev/chatbot dev) as a distinct
   track from the productized-content track rather than folding both into
   one homepage - services need a channel where trust/referral matters
   (e.g. a real portfolio case study written from this very project, which
   is itself a legitimate, honest case study: "built and launched an
   autonomous research-to-product pipeline") rather than competing for
   attention against $0 digital downloads on the same page.
9. **Why might this fail even with excellent execution?** Because every
   step past "produce a good product" (get it discovered, get it trusted,
   get it paid for) currently depends on either a platform's KYC process
   the user doesn't fully control, or a distribution channel this system
   is structurally barred from creating accounts on. Excellent product
   execution cannot compensate for zero discovery - that's the real risk,
   not product quality.
10. **Single biggest systemic bottleneck?** Distribution/discovery gated
    behind human-only account actions (Search Console, Gumroad KYC,
    Formspree) - not SEO quality, not content quality, not architecture.

**Resulting decision this review**: proceed with resuming Google Search
Console (approved by the user same day as this review) as the fastest
unblock. No pivot away from the current product line - the underlying
research (freelancer swipe-file systems, competitor-validated pricing) is
sound - but flag two follow-ups for the user rather than silently keep
building: (1) whether Gumroad's KYC is actually going to resolve or a
lower-friction fallback (Ko-fi) is worth evaluating in parallel, and (2)
whether the service offerings should be split into their own
trust-building track (case study, not just a landing page) rather than
sharing the homepage with $0 downloads. Neither requires new building
today - both are decisions for the user.
