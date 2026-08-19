# Task Board

> Iterácie 1–49 sú v `docs/TASKBOARD_ARCHIVE.md` (presunuté 2026-08-19).

## Done (iteration 50) — unified card treatment + stronger glassmorphism
- [x] User: "na kartách používaš rozdielny efekt" (the cards use different
      effects). Correct - three clickable card types had grown three
      unrelated hover treatments: product cards had a scaling gradient
      blob in the corner, service cards a permanently-visible top bar, and
      blog cards nothing but a lift. Collapsed all three into one shared
      rule: same surface, same lift, same brand border, same gradient
      accent bar fading in on hover. Removed the now-duplicated
      `.post-card` block that would have overridden the shared definition.
- [x] User: "daj tam väčší sklenený efekt". Extended glassmorphism from
      the header alone to cards, stat tiles, widgets, news items, topic
      tabs and eyebrows: translucent surfaces with `backdrop-filter`
      blur + saturation and a light edge. Two supporting changes were
      needed for it to actually read as glass rather than flat tint -
      the background orbs were strengthened (glass needs something behind
      it to refract) and the background set to `fixed`, so the colour
      behind each panel shifts while scrolling.
- [x] Kept legibility as the constraint: the glass tokens stay above 50%
      opaque, so body text contrast is unaffected - the effect comes from
      blur and the edge highlight, not from making panels see-through.
- [x] Added an `@supports not (backdrop-filter)` fallback to solid
      surfaces, so browsers without support get the previous opaque design
      instead of washed-out translucent boxes with no blur.
- [x] Process note worth recording: resolving `db/biznis.sqlite3` with
      `--ours` during a **rebase** took the upstream side, not mine, and
      silently dropped the new design service's DB rows while leaving its
      HTML file behind as an orphan (absent from homepage and sitemap).
      Caught by checking the service count after the rebuild rather than
      assuming the merge was fine. In a rebase `--ours` is upstream and
      `--theirs` is the commit being replayed - the reverse of a merge.

## Done (iteration 51) — repositioned: a studio, not a template shop
- [x] User pushback, and correct: "to čo ponúkame je ďaleko za nejakými
      šablónami a scriptami" - the site (and the social banner) sold the
      cheapest thing in the catalogue while four real services sat
      underneath it. The offering is design, websites, custom digital
      products, chatbots and automation; the ready-made templates are the
      catalogue, not the business.
- [x] Rewrote the top-level positioning everywhere it appears:
      - Hero: "We design and build the digital side of your business",
        with the four service lines named explicitly in the subtitle and
        the ready-made catalogue demoted to a closing clause.
      - Eyebrow: "Design · Build · Automate" (was "Real demand signals").
      - Page title: "Design, Websites, Custom Digital Products &
        Automation" (was "Digital Products & Custom Development").
      - Section headings: "What we build for you" (was the weak "Work
        with us"), "Ready-made systems", "Free downloads".
      - New X/social banner listing the four services as tags instead of
        describing the company as a script vendor.
- [x] `scripts/audit_site.py` caught the rewritten meta description at 164
      characters, over the 160 limit where search engines truncate -
      shortened to 136 rather than shipping a description that would be
      cut mid-sentence in results. Worth noting the audit paid for itself
      here: this is exactly the kind of detail a copy rewrite breaks
      silently.
- [x] Brand assets for social profiles generated in the site's own visual
      identity: `data/exports/brand/avatar.png` (800x800 monogram) and
      `banner-x.png` (1500x500).
- [x] Declined to create social accounts on the user's behalf - account
      creation means accepting terms of service and establishing identity,
      which has to be the person responsible. Prepared everything around
      it instead: checked handle availability across X/GitHub, wrote the
      bio copy, and produced the profile imagery, so the signup itself is
      a few minutes of the user's time.

## Done (iteration 52) — wordmark unified where it renders, plain name where it does not
- [x] Asked for an opinion on rolling `Biznis.studiO` out everywhere, and
      gave a split recommendation the user agreed with: apply the wordmark
      only where it is **rendered with its styling** (header, footer,
      social banner), and keep plain "Biznis" in text-only contexts
      (`<title>`, meta descriptions, RSS). Unstyled, the terminal capital
      reads as a typo rather than a design choice, and people mistype it -
      the logotype is a visual asset, the name is what you write.
- [x] Favicon and social avatar deliberately left as the "B" monogram.
      They render at 16px and ~40px respectively, where ".studiO" is an
      unreadable smudge; a single letter is the correct mark at that size,
      not a compromise.
- [x] Added `BRAND_HTML` as the single source for the wordmark so the
      header and footer cannot drift apart, and generalised the CSS from
      `.site-header a.brand` to `a.brand`.
- [x] Footer mark needed its own treatment rather than reusing the
      header's: at 0.95rem a 0.7px stroke is thinner than the rendered
      stem, so the letters break up. The footer leans on fill instead of
      the etched stroke.
- [x] Found stale copy while touching this: the RSS feed was still titled
      "Biznis - Free Digital Products" with a description about free
      checklists and prompt packs - contradicting the repositioning and
      wrong on its own terms now that most products are paid. Retitled and
      rewritten in both the feed and the `<link rel="alternate">` tag.
- [x] Stated an honest strategic view alongside the branding answer:
      design has stopped being the constraint. With 0 sales and near-zero
      traffic, the next hour is worth more spent on distribution than on
      brand refinement - offered without refusing the branding work, which
      was small and worth finishing.

## Done (iteration 53) — capability audit: only offer what can actually be delivered
- [x] User instruction, and a serious one: **only offer services we can
      genuinely deliver ourselves, with light help at most.** Audited all
      four existing services against real capability rather than assuming
      the copy was fine because it read well.
- [x] Reassessed direction on real data first, not from the armchair.
      Decisive finding: Gumroad shows **0 views**, not just 0 sales. Zero
      sales at zero views is not a product, price, copy or design problem -
      nobody has arrived. Everything this session polished sits downstream
      of a gate that has not opened. Also relevant: the project is 4 days
      old and the domain changed 2 days ago, so Search Console is still
      processing and has no data at all. "We are at zero" is currently the
      absence of evidence, not evidence of failure.
- [x] Surfaced a real blocker found in the dashboard: Gumroad reports
      **identity verification failed** ("The identity information you
      entered cannot be verified"). Payouts are blocked until the user
      fixes it - a sale today could not reach him. User action, flagged
      rather than attempted.
- [x] **Design service rewritten to match actual capability.** It had
      promised hand illustration, spot artwork, icon sets "drawn to fit",
      and "layered source files" - none of which can be honestly
      delivered. Now states precisely what is delivered and in which
      formats (SVG vector logos, colour/type systems as a written guide
      *and* a working stylesheet, web/UI designed directly in real
      HTML/CSS rather than as a picture of a website, marketing graphics,
      PDF/PPTX decks, SVG icon sets), plus an explicit **"What we do not
      offer"** section: no hand illustration or character art, no
      photography, no print/CMYK/prepress, no layered PSD or Figma source.
- [x] **Added Automation & Integrations** as a real service. It was named
      in the homepage hero with nothing to click - a claim with no page
      behind it - and it is the capability this operation can deliver most
      reliably. Includes its own honest limits: no managed 24/7 ops, no
      automating anything needing credentials/payment authority/legal
      identity, no bypassing services whose terms forbid automation, no
      enterprise platform work. Also says plainly that a task taking ten
      minutes a month is not worth automating.
- [x] **Website service**: added what it does not cover - no web apps with
      accounts and a database, no direct card-payment shops (integrate an
      existing checkout instead, merchant account stays the client's), no
      content-update retainers.
- [x] **Chatbot service**: stated up front that a chatbot needs a paid
      third-party language model account which stays in the client's name
      and is billed to them directly - no hidden dependency on us. Also
      reworded the AI-tooling credibility line per the standing
      instruction not to advertise that angle.
- [x] Five services now, each with an explicit boundary. A studio that
      claims everything is useless to a buyer - the "what we do not offer"
      sections are what make the rest credible.

## Done (iteration 54) — found the real cause of zero traffic, and it is not what we assumed
- [x] User challenged the assumption directly: is the failed Gumroad
      identity verification actually the cause of zero visits? Tested it
      rather than reasoned about it. **No.** Product pages load for a
      visitor, price displays, the buy button is present and not disabled,
      no warning banner - the products are purchasable. Verification
      blocks *payouts*, not sales or visibility. Good challenge; the
      original framing would have sent effort at the wrong thing.
- [x] Also disproved the next assumption: the site **is** indexed. A
      `site:` query on Google returns real results, crawled a day earlier.
      So: indexed, reachable, purchasable - and still zero views.
- [x] **The actual cause, found by checking a real SERP.** Searching the
      exact query our best free tool targets - "scope creep cost
      calculator freelance" - returns a first page owned by established
      competitors: Sengi, Teamz Lab, AI Biz Hub, **Harvest** (a major
      time-tracking SaaS), Invopoint, Jobbers, Agiled. Seven existing
      calculators for the same job. A 4-day-old domain with zero backlinks
      does not out-rank that. Being indexed is worthless on page five.
- [x] **This exposes a real flaw in the pipeline, not just bad luck.**
      `demand_scoring_agent` measures interest and treats it as
      opportunity. Its competition component comes from GitHub/npm/Stack
      Exchange density, which iteration 3 already flagged as a poor proxy
      for consumer-content saturation - that caveat now has a concrete,
      expensive example. Nothing in the system ever asks "can we actually
      rank for this?"
- [x] Recorded the honest limit rather than promising a fix: closing that
      gap needs real SERP data, and scraping Google violates its terms
      while proper SERP APIs are paid. So winnability stays a manual check
      during working sessions. Logged in `docs/CONSTRAINT_LOG.md` with the
      full evidence chain.
- [x] **Strategic consequence, acted on.** SEO is demoted from *the plan*
      to *background* - it is automated and free, so it keeps running, but
      it cannot deliver the first customer. The catalogue's role changes
      from "product sold to strangers via search" to "verifiable proof of
      capability" for the services, which are worth far more per sale and
      are bought on evidence and outreach.
- [x] Built `/work.html` as that proof: the site, the unattended pipeline,
      the working tools, the products, the public source - each one
      clickable and checkable. Leads with an explicit statement that this
      is our own project and not client work, and closes with **"What this
      does not prove"**, conceding that building well for yourself is not
      the same as building well for a client, and offering fixed price
      agreed in writing as the way to carry that risk for the buyer.
      Added to the nav in first position.
- [x] Caught myself publishing an unverified figure: I had hardcoded "85%
      of runs completed successfully" as a guess. The real number was 92%.
      Rather than correct a number that would silently rot, removed the
      percentage entirely and linked the public Actions history, where
      every run's outcome - success and failure - is visible and always
      current.

## Done (iteration 55) — rewrote Work and the homepage stats for buyers, not builders
- [x] User read the new Work page and called it correctly: it was full of
      things that flatter whoever built them and mean nothing to a
      customer - page counts, "static HTML with no framework, no build
      step", lines of Python, signal totals, unattended-run counts. A
      client evaluating a studio is asking one question, and none of that
      answered it.
- [x] Rewrote the page so every section follows the same shape: **what we
      built -> try it yourself -> what this means for your project.** The
      technical facts either became a benefit or were deleted:
      - "25 pages, static HTML, no framework" -> "a finished website, not
        a mockup - this is the standard you get, live and working, not a
        design file for somebody else to build"
      - "7,642 signals, 4,933 lines of Python, 33 runs" -> "software that
        runs without anyone touching it... if there is something you do by
        hand every week, this is what replacing it looks like"
      - the calculators reframed around why a client would want one (an
        interactive tool is one of the few things that gets shared and
        linked to on its own)
      - the design section now promises the *rules and a stylesheet*, not
        just a logo, which is the actual client pain
- [x] Same fix on the homepage: the stats strip was internal machinery
      ("market signals analyzed", "keywords demand-scored"). Replaced with
      the terms of doing business, which is what a buyer weighs - fixed
      price agreed in writing, full rights and source files, delivered
      live rather than as a file, everything public to try first.
- [x] Kept both honesty sections deliberately - "Read this first" (this is
      our own project, not client work) and "What this does not prove"
      (building for yourself is not building for a client; the first
      client takes that partly on trust, and a fixed written price is what
      we put against it). Those are the reason the rest is believable.
- [x] Verified by grep that no builder-speak survived the rewrite on
      either page.

## Done (iteration 56) — corrected my own over-broad SEO conclusion, found the winnable half
- [x] Dropped the repeated KYC/payout mention at the user's direct
      instruction. I had verified myself that it has no bearing on demand
      or traffic, then kept raising it in closing summaries anyway. Fair
      correction.
- [x] More importantly, corrected a reasoning error of my own: the
      previous iteration concluded from **one** saturated SERP that SEO
      could not deliver the first customer. That generalised from a single
      data point.
- [x] Second check changed the conclusion. "email to client about scope
      creep what to say" returns replyguard.ai, two Reddit threads,
      whereismyproject.com, a personal blog and kitchen.co - no
      incumbents, no dedicated tools. Winnable.
- [x] **The real pattern:** tool/calculator queries in this niche are
      owned by established players; *conversational* queries ("what do I
      say", "how do I tell a client") are served only by forum threads and
      small blogs. Conversational queries are exactly what this catalogue
      answers, because what we sell is scripts. We had been aiming at the
      wrong half of the keyword space.
- [x] Also exposed a funnel mismatch: the Scope Creep Kit page contains
      the answer to those queries but gates it behind a purchase. A
      searcher wants the answer, not a buying decision - so a gated
      product page will not win an informational query no matter how good
      it is.
- [x] Published `blog/what-to-say-scope-creep.html` targeting that gap:
      three complete, genuinely usable scripts given away free, structured
      around Google's own "People also ask" questions (how to tell a
      client something is out of scope, what to say when they call it
      small, a better way to say "scope creep"), plus the tracking habit
      that makes the wording stick. Routes to the kit only for the
      moments it does not cover, and says plainly that if the free scripts
      solve your problem you need nothing else from us.

## Done (iteration 57) — broadened the search and found a better market
- [x] User: do not confine the research to one family. Correct - the work
      had narrowed to freelance client-communication queries in English.
- [x] Widened it and found the strongest opportunity of the whole
      exercise: **Slovak SERPs for our actual services are contested only
      by small local agencies.** "koľko stojí webstránka pre malú firmu"
      returns tomarco.sk, webision.sk, ravensoft.sk, velocis.sk;
      "automatizácia procesov v malej firme" returns bizmatica.sk,
      ui42.sk, becode.sk, eWay-CRM. No global incumbent on either - and
      paid ads are running on the second, meaning somebody is already
      buying these customers, so demand is proven rather than assumed.
- [x] The strategic weight is not just lower difficulty: these are
      service enquiries worth hundreds to thousands of euros instead of
      $29 downloads, and the operator can actually service them - same
      language, timezone, jurisdiction, invoicing, and the option to meet
      in person. Local service work is bought on trust and proximity,
      which is the one axis where a business with no portfolio is least
      disadvantaged.
- [x] Published `/sk/` - a Slovak services page covering all five
      offerings, with the same honesty sections as the English site
      ("Úprimne: sme noví", no invented references). Wired hreflang
      alternates both directions plus x-default, its own canonical,
      `lang="sk"`, a sitemap entry, and a cross-link from the English
      footer, so Google serves the right language instead of treating the
      two as duplicates.
- [x] Refactored `contact_form_html()` to take a language rather than
      duplicating the form - the honeypot and endpoint handling cannot
      drift between the two versions that way.
- [x] Proofread the Slovak and fixed six real grammar errors before
      publishing ("stavíme"→"staviame", "čásť"→"časť", "ponúku"→"ponuku",
      "lógá"→"logá", "závislosť na nás"→"od nás",
      "prepísavanie"→"prepisovanie"), plus a plural-agreement error in a
      stat tile. Bad Slovak on a Slovak page destroys credibility faster
      than no Slovak page at all.
- [x] Deliberately published **no prices**, despite the research
      surfacing real market rates (one-pager from ~599 €, company site
      from ~999 €, freelancer 500–2 000 €). What to charge commits the
      owner publicly and is his call.
- [x] Also drafted a **Late Payment Recovery Kit** (8 escalation scripts +
      a payment tracker) after finding that "how to politely chase an
      unpaid invoice freelance" is held by Reddit threads and small blogs,
      with Google explicitly flagging that a top result was *missing* the
      freelance angle - an underserved query with no product of ours
      behind it.

## Done (iteration 58) — both open decisions made and shipped
- [x] Asked to decide rather than defer, so both were decided and
      implemented, with the reasoning recorded in Decision Journal D13/D14.
- [x] **Prices published on the Slovak page.** The agencies ranking for
      "koľko stojí webstránka" publish prices, and that is part of why
      they rank - the query *is* a price question, so a page without one
      does not answer it. Set at the lower-middle of the researched market
      (one-pager from 590 €, company site 1 190 €, automation 390 €,
      custom product 290 €, identity 390 €, chatbot 690 €): credible,
      below agency rates, clearly above hobbyist. Stated ex-VAT, with
      third-party running costs excluded and paid by the client directly
      so they are never locked to us. Added a column explaining what moves
      each price, and a line offering to cut scope rather than quality if
      budget and scope do not meet.
- [x] **Late Payment Recovery Kit released free**, not at $29. The
      constraint is that nobody arrives - the paid kits have zero *views*,
      so a third paid listing changes nothing. A complete free kit is
      something people link to, which attacks the real constraint, and it
      supports the services where revenue is orders of magnitude larger.
      Pricing it later is one edit; a missed linking opportunity does not
      come back.
- [x] Both decisions flagged to the owner with the actual numbers, since
      published prices are a public commitment on his behalf - decided,
      not hidden.
- [x] Proofread the new Slovak pricing copy again and fixed further errors
      ("Súmy"→"Sumy", "Čo cenu meni"→"mení", "číslach").

## Done (iteration 59) — closed a deliverability gap I had just created
- [x] User restated the standing rule: only offer what can actually be
      delivered. Rechecked against what had just shipped, and found a real
      gap I had introduced an hour earlier.
- [x] **The Slovak pricing table had no boundaries.** The English service
      pages each carry a "what we do not offer" section; the new Slovak
      page listed six services with prices and nothing else. A buyer
      landing there saw commitments with no limits. Added the full list in
      Slovak: no web apps with accounts and a database, no shop with its
      own payment gateway, no hand illustration or character art, no
      photography, no print/prepress, no 24/7 operations, nothing
      requiring the client's credentials or legal identity, no automating
      services whose terms forbid it, and a chatbot needs a paid language
      model account in the client's own name.
- [x] **Fixed a claim that was simply untrue**, in English as well as
      Slovak: "you get a site you can edit, and documentation for how".
      For a non-technical small business receiving hand-written HTML, that
      is false - nobody is going to edit raw markup. Replaced with two
      honest options agreed before work starts: text changes come back to
      us at a small fixed fee, or we build a simple admin panel, which
      costs extra and needs a hosting account in the client's name. Said
      plainly that any agency claiming you can "just edit" hand-written
      HTML is hoping you never try.
- [x] Proofread the new Slovak again and fixed further grammar errors
      ("tá čásť", "s vlastným platobným bránou" - wrong gender agreement,
      plus two compound-word slips).
- [x] Worth recording as a pattern: the gap appeared precisely because a
      *new surface* was added quickly (a whole page in another language)
      while the honesty sections lived only on the older pages. Boundaries
      have to be part of the template, not bolted on per page.

## Done (iteration 60) — Slovak content published; stopped advertising our own weakness
- [x] User correction, and an important one: copy like "We are new, so
      there is no client list... that is a harder thing to fake than a
      testimonial" is not professional marketing, it puts people off, and
      it is unclear who it is even addressed to. Correct.
- [x] I had conflated two different things: **not lying** and **volunteering
      your weakness in the headline**. Professional marketing does neither
      fabricate nor confess. The hard line stays exactly where it was - no
      invented testimonials, no logos of companies we have not worked
      with, no fabricated numbers - but nothing obliges us to open with
      "we have no clients".
- [x] Rewrote every instance of it, keeping the substance and dropping the
      apology:
      - Work page opener → "The design, the products, the tools and the
        software that publishes all of it - every piece of this was built
        by us. It is live, it works, and you can use any of it right now."
      - "What this does not prove" → **"How we take the risk off you"**:
        same content (fixed price, written scope, we absorb an
        underestimate, you own the result) framed as the guarantee it
        actually is rather than as a confession.
      - Slovak "Úprimne: sme noví" → "Pozrite si našu prácu" with the same
        risk-transfer promise stated as a strength.
      - Website and chatbot service pages: "this is a new service
        offering, no long portfolio" → "See the standard before you
        commit", pointing at the live site as a better thing to judge than
        a portfolio of screenshots.
- [x] Published two Slovak articles targeting the exact queries verified
      as winnable: **"Koľko stojí webstránka pre malú firmu"** (real market
      ranges, what actually drives price, what is never included, how to
      spot an overpriced quote, and when you do not need a website at all)
      and **"Automatizácia v malej firme: čo sa oplatí"** (the arithmetic
      first, what to automate, what not to, what to ask a supplier).
- [x] Extended `blog_agent` with Slovak article support - separate
      directory, `lang="sk"`, own canonicals, sitemap entries - rather
      than mixing languages in one blog index, which would give Google a
      page it cannot classify.
- [x] Found and fixed a bug in the same pass: the articles were built and
      in the sitemap but **not linked from the Slovak page** - an earlier
      patch had failed to apply silently because its anchor string did not
      match. Caught by checking the rendered output rather than trusting
      the patch reported success.

## Done (iteration 61) — studied the official best practices and applied them
- [x] Read Anthropic's official Claude Code best practices rather than
      relying on my own habits, then applied the three that this project
      was measurably losing time to.
- [x] **"Give Claude a check it can run."** This was the biggest gap. The
      correct rebuild sequence is nine steps with a non-obvious ordering
      constraint, and I had been retyping it as an inline heredoc roughly
      fifteen times in a single session - which is exactly how a step gets
      skipped. Now `scripts/build_site.py`: one command, correct order,
      and it ends by running the crawl audit and **exiting non-zero if the
      audit fails**, so "do not ship" is a signal rather than a judgement
      call.
- [x] **Verification must hit production, not the local build.**
      `scripts/deploy.py --expect "<text>"` triggers the pipeline, waits
      for the run to actually finish, then fetches the live URL and
      confirms the expected text is really there. Exit 0 means verified in
      production - nothing weaker. Written because the live site sat
      several changes behind for hours today while every local build
      looked perfect, and I reported progress from the build rather than
      from the site.
- [x] **Wrote `CLAUDE.md`.** The project had none, so every session
      re-derived its rules from the docs. Kept deliberately short per the
      guidance that bloated files get ignored - only things that would
      cause real mistakes if removed: the commands, the required env vars,
      the four gotchas that have genuinely bitten (SEO markup wiped on
      rebuild, `--ours` meaning upstream during a rebase, silent deploy
      failure, the calculator page bypassing `page_shell`), the content
      rules, and a short strategy summary pointing at the existing logs.
- [x] Did **not** add: hooks, subagents or new governance docs. The
      guidance is explicit that these are for things needing a hard
      guarantee or isolated context, and the 30-day no-new-layers
      directive still stands. The three changes above remove real,
      measured waste; anything further would be process for its own sake.

## Done (iteration 62) — studied loops/graphs properly, then used them on real work
- [x] Read the official docs on dynamic workflows (graphs) and `/goal`
      (autonomous loops) rather than guessing. The distinction that
      matters: a **graph** moves the plan into a script so it can fan out
      across many items with intermediate results staying out of context;
      a **loop** re-runs until a verifiable condition holds, judged by a
      separate evaluator rather than the model doing the work.
- [x] Applied it to the two things this project does repeatedly by hand:
      - `.claude/skills/ship/` - build, audit, commit, rebase (with the
        `--theirs` warning and a row-count check), deploy and **verify on
        the live URL**. Encodes the sequence that has gone wrong twice.
      - `.claude/skills/find-opportunities/` - the SERP winnability method,
        including the classification rules and the two patterns already
        established, so it is not re-derived each time.
- [x] Ran a real fan-out instead of describing one: one research agent
      across six Slovak queries at once. It reported back honestly that it
      could **not** reach Google (EU consent wall), used DuckDuckGo, and
      explicitly flagged that it had no ad data and no People-Also-Ask
      data rather than inventing them. That is the standard wanted.
- [x] Verified its most load-bearing claim myself, and **one did not
      replicate**: it reported a `github.io` site ranking page 1 for
      "potrebuje moja firma webstránku". On Google it is not there - that
      was a DuckDuckGo-only result. Not repeated as fact. This is exactly
      why a fan-out's findings get checked rather than trusted.
- [x] What my own Google checks *did* confirm: both target SERPs are held
      by small Slovak operators (webvista.sk, martinpavlic.sk,
      magnetica.sk, upsight.sk / webize.sk, chatbotnamieru.sk, taibot.sk,
      vlad-weby.sk), **paid ads are running** on the website query -
      answering the demand question the subagent could not - and the
      top-ranking result for the chatbot query is an editorial pricing
      article, i.e. exactly the format to write.
- [x] Published both, in Slovak: **"Koľko stojí chatbot pre firmu"**
      (three price tiers, the language-model running cost most price lists
      omit, the security point that the API key must not sit in page code,
      and a full section on when *not* to buy one) and **"Potrebuje moja
      firma webstránku?"** which opens by admitting we sell websites and
      then explains when a free Google business profile is enough.
- [x] Used `scripts/build_site.py` for the build - first real use of the
      tooling written in the previous iteration.

## Done (iteration 63) — found a real market gap and built the thing nobody sells
- [x] Started writing another "e-faktúra 2027" explainer, then binned it.
      User was right on both counts: it was surface-level, and it would
      have been the forty-seventh copy of an article EY, Podnikajte,
      Fakturix, FLOWii and others already published.
- [x] Went deeper and found the actual gap. **Every piece of content on
      this topic is published by a company selling invoicing software** -
      so none of them lead with the fact that the state, under IS EFA,
      provides a **free web application for small businesses** to create
      and manage invoices in the required format. For a low-volume Excel
      user that free app is the entire answer, and nobody selling software
      has any reason to say so.
- [x] Verified the legal facts from primary and independent sources rather
      than from an ad: the VAT law amendment was passed by the National
      Council on 9 Dec 2025 and signed 16 Dec 2025 - law, not a proposal.
      From 1.1.2027 VAT payers must issue *and receive* structured XML
      (EN 16931 / Peppol BIS); voluntary testing is running now;
      cross-border follows 1.7.2030 under ViDA.
- [x] Built **`/sk/efaktura-2027-test.html`** instead of an article: four
      questions, then a concrete verdict for that specific situation -
      what changes, what to do, and an estimated cost. Runs entirely in
      the browser, stores nothing.
- [x] The output most competitors would never ship: for a non-VAT payer on
      Excel with low volume it says **"cost 0 €, you need nothing from
      us"** and points at the state's free app. Verified by driving three
      scenarios through the tool and reading the rendered output, not by
      assuming the branches work.
- [x] Why this is the right shape of asset: the obligation is a hard dated
      deadline with real urgency (not manufactured), the SERP is held by
      small players with paid ads running (demand proven, verified on
      Google directly), and a decision tool is linkable and shareable in a
      way a forty-seventh explainer is not. It also filters leads - the
      only people who contact us are the ones whose own system genuinely
      needs changing.

## Done (iteration 64) — global gap research, verified, and the first asset built
- [x] Fixed a real defect first: **every link on the Slovak pages went to
      English pages.** Header and footer are now language-aware; all six
      Slovak pages carry Slovak chrome.
- [x] Ran a global opportunity fan-out with hard criteria: legality, and
      the studio must be able to deliver it itself. The agent checked
      seven candidates and, usefully, **rejected five as already
      saturated** (EUDR GeoJSON validators, Factur-X validators, Digital
      Product Passport, Shopify Scripts, UK employment templates) - a
      rejection list is worth as much as a shortlist.
- [x] Verified the winning candidate against the **primary source** rather
      than the agent's summary. EUR-Lex, Regulation (EU) 2023/1230
      Article 10(7): instructions may be digital, but must be reachable
      from a marking on the machine, printable and downloadable, in a
      language set by each member state, and **"accessible online during
      the expected lifetime of the machinery and for at least 10 years
      after the placing on the market"**.
- [x] Why this fits better than anything found so far: the obligation is a
      requirement to keep a URL alive for ~25 years. Every incumbent
      (Quanos, kothes, EquipmentCloud, Instrktiv) sells a subscription
      CCMS - a 30-person machine builder will neither afford that nor
      trust it to exist in 2040. **Our hardest constraint - static files,
      no backend - is the product's main virtue here.**
- [x] Built the first asset: a free checker at
      `/tools/machinery-regulation-digital-instructions.html`. It computes
      the real obligation window from service life, restates exactly what
      Article 10(7) demands, and - the part no subscription vendor will
      publish - multiplies their monthly fee across the full obligation.
      A 15-year machine on a 250 EUR/month platform shows **75,000 EUR**.
      **Correction (iteration 75):** that figure was wrong. The tool
      computed the window as life + 10 when Article 10(7)(c) means
      whichever of the two is longer. The correct answer for that example
      is 15 years and **45,000 EUR**. Left the original line intact rather
      than quietly editing it, so the error stays visible in the record.
- [x] Found and fixed a bug before shipping: an apostrophe inside a
      single-quoted JS string broke the entire inline script silently, so
      the tool rendered but did nothing. Caught by driving the tool and
      reading its output rather than trusting that it built. Added a
      parse check of every inline script as part of verification.
- [x] Scope stated on the page: we publish documents, we are not a
      notified body, and this is not conformity assessment or legal advice.
- [x] Honest gap carried forward from the research: buyer-side demand for
      this is **not yet verified**. The regulation, dates and competitor
      landscape are confirmed; that machine builders perceive the 10-year
      hosting as *their* problem is not. That is what the free tool is
      for - it will show whether anyone searches for this.

## Done (iteration 65) — closed the last service gap in Slovak content
- [x] **Correction (iteration 76): the claim below is wrong.** Design/
      branding was not the *only* uncovered service - "Digitálny produkt
      na mieru" (290 EUR in the pricing table) had no article then and
      still has none. That is deliberate, not an oversight: iteration 66
      SERP-checked custom-tool pricing and rejected it as held by real
      incumbents with fresh 2026 content. Left the original wording
      below rather than rewriting it, so the mistake stays visible.
- [x] Design/branding was the one service of five (web, automation, custom
      digital products, design/branding, chatbots) with no Slovak article.
      Ran `find-opportunities` on 6 candidate queries via a subagent first
      (WebSearch fallback - Google's EU consent wall blocked WebFetch again,
      same known issue), then personally re-verified the weakest signal
      ("cena za branding firmy", where WebSearch returned Polish results)
      with a real `google.com/search?gl=sk&hl=sk` fetch through the browser.
- [x] Confirmed: page 1 held only by small local studios (Livora, LL
      studio, AnimaGraf, Webovica, Concept23, Grafitek), **two paid ads
      running** (Visual Communication, Kreativ Gang) - commercial demand
      proven the same way it was for the chatbot/web queries. One close
      competitor (opulon.org, a near-identical pricing article published
      ~3 weeks earlier) noted rather than ignored - differentiated on the
      house style's "what we don't do" + supplier-questions sections.
- [x] Published **"Koľko stojí logo a vizuálna identita pre firmu"**:
      four price tiers (AI generator through full identity), what pricing
      pages omit (vector source files, IP transfer, revision counts), when
      not to buy branding at all, and our own price (390 €).
- [x] Shipped and verified live via `scripts/deploy.py`, but the first
      `--expect` phrase was a bad choice (text that lives in the sitewide
      pricing table, not the article) and the script correctly reported
      failure. Re-verified manually with a phrase actually in the article
      body plus a sitemap check before calling it done - the deploy itself
      had succeeded; the check was wrong, not the ship.

## Done (iteration 66) — opportunity fan-out that honestly found nothing, and that's the right answer
- [x] Ran a 12-candidate fan-out across two tracks: more "long-lived legal
      obligation" niches shaped like the Machinery Regulation win (a
      regulation that requires a URL to stay live for years - static
      site's structural advantage over SaaS), and new Slovak
      conversational/pricing queries adjacent to the 5 already-covered
      services. All checked against primary sources (EUR-Lex, Slov-lex,
      live SERPs), not summary blogs.
- [x] Rejected all 12, each for a real reason, not a vibe: EU AI Act Art.
      50 chatbot-disclosure obligation is genuinely novel (applies from
      2 Aug 2026) but already saturated - multiple free generators plus
      the EU's own official checker rank, several SK blogs published in
      the prior 1-3 weeks; European Accessibility Act explicitly exempts
      microenterprises (our own client base) in its primary text; SK
      Whistleblowing channel (zákon 189/2023) is real but only applies at
      50+ employees and is already owned by a funded SaaS
      (whisly.sk) running paid ads; the rest (SEO pricing, custom-tool
      pricing, maintenance retainers, invoice-reminder automation,
      late-payment letter templates, lead-gen calculators) are each held
      by real incumbents with fresh content or paid ads.
- [x] One lead flagged by the agent as unverified - EPR/OZV packaging
      registration for small e-shops - checked personally against the
      primary source (Zákon o odpadoch 79/2015 Z.z. on Slov-lex) rather
      than trusted secondhand. Confirmed it is an ongoing paid
      registration + annual reporting relationship with a producer
      responsibility organization, not a "publish once, stays live"
      obligation - the static-site wedge does not apply. Rejected.
- [x] Reported zero candidates rather than padding to a fake shortlist,
      per the project's standing anti-fabrication rule. The Machinery
      Regulation asset (iteration 64) still hasn't shown buyer-side
      demand data yet either - the honest state is "watch what's already
      built" this round, not "build something new for the sake of it."

## Done (iteration 67) — studied "graph engineering", applied it to our own pipeline
- [x] User pointed at an X article on graph/fan-out engineering (worker/
      checker context separation, "anchors" as numbers that can't argue
      back, and the "fake-edge test": for any two sequential steps, ask
      whether the second actually needs the first's output - if not, it's
      not a real dependency, run them concurrently). Applied it to our own
      code instead of writing more content.
- [x] Two of its three ideas were already unknowingly practiced here:
      worker/checker separation matches `04_Lessons.md`'s "subagent
      research must be re-verified on primary sources" (the EPR/OZV check
      last iteration was exactly this); anchors match the standing "never
      publish an unverified number" rule. Confirms the practice rather
      than changing it.
- [x] The fake-edge test found a real one: `market_research_agent.py`'s
      five source fetchers (HN, Wikipedia, npm, Stack Exchange, GitHub)
      ran in a sequential `for` loop despite zero data dependency between
      them - plus two of the five (npm: 9 seed terms, Stack Exchange: 4
      sites) looped sequentially *inside* themselves for the same reason.
      Fanned out all of it with `ThreadPoolExecutor` (DB writes stay
      single-threaded - sqlite3 connections aren't thread-safe).
- [x] Measured rather than assumed, since network I/O timing is noisy and
      the user's source material warned against topology-without-anchors:
      3 sequential runs averaged 8.98s, 3 fully-parallel runs after the
      fix averaged 4.21s - real signal under real variance (one outlier
      at 9.66s from what looks like a source's rate-limit backoff), not a
      fabricated "2x faster" headline. Output unchanged: 232 signals,
      same per-source counts, confirmed byte-identical across runs.
- [x] Scope stayed to what the fake-edge test actually found - did not
      restructure the rest of `run_pipeline.py`'s stages, which have real
      data dependencies (keyword_agent needs signals_raw, product_agent
      needs demand_scores, etc.) and are correctly sequential already.

## Done (iteration 68) — first real GSC data point, and a conversion bug it prompted us to find
- [x] First non-zero Search Console Performance numbers appeared (1 click,
      2 impressions, 7/27-7/29) - but the only query row shown was
      `site:github.io`, a manual index-check operator, not organic
      demand. Too sparse to act on; noted honestly rather than
      over-reading 3 data points into a trend.
- [x] Since traffic data wasn't actionable yet, audited what's fully in
      our control regardless of volume: the path from "convinced reader"
      to "contact form" on our own pages. Found a real bug across **all
      5 SK service articles** - every closing CTA ("Napíšte nám",
      "Cenník") linked to bare `index.html` instead of `#kontakt` or
      `#cennik`. A reader who finished an article and clicked through
      landed at the top of the page and had to scroll and hunt for the
      form themselves.
- [x] Checked the English side for the same pattern first - it doesn't
      have it. EN blog posts link to specific product/tool pages, and
      the EN homepage is a product catalogue with no contact form to
      miss, so no fix needed there; the bug was specific to the SK
      service-article CTAs.
- [x] Fixed all 5 source `.md` files, rebuilt, verified the anchors landed
      in the generated HTML for every article before shipping, deployed
      and verified live.
- [x] Sitemap still shows "Couldn't fetch" as of same-day resubmission
      (expected - under 24h since resubmit, not yet a second failure).

## Done (iteration 69) — ruled out a false fix, researched and declined a real one
- [x] Researched the persistent sitemap "Couldn't fetch" status against 6
      GitHub community threads. The most commonly cited fix (`.nojekyll`)
      does **not** apply to us - verified `actions/upload-pages-artifact`
      (our deploy method) never runs Jekyll processing at all, so a
      missing `.nojekyll` file was never the cause. Did not add it just
      because it's the popular answer. Every other commonly-cited cause
      (content-type header, robots.txt, XML validity, sitemap size) was
      already ruled out in iteration 68. Conclusion: genuinely
      unexplained by any documented cause - likely a Search-Console-side
      quirk for a brand-new low-authority domain, not a site defect.
      Real GSC crawl activity already confirmed (1 click/2 impressions),
      so Google is reaching the site through other paths regardless.
- [x] Researched free Slovak business directories as a distribution
      channel that doesn't wait on organic SEO's sandbox period.
      Verified quality before recommending, not just existence:
      DatabázaFiriem.com is a real, 15+ year, actively-updated directory
      (133k listings, not a link farm) with free registration.
      FinStat.sk is authoritative but auto-populated from state
      registers, not something to "register" into - moot unless this
      project is a formally registered business entity (unconfirmed).
      Presented the DatabázaFiriem.com option with an honest cost (needs
      an account + public business info submitted externally) - **user
      declined** (2026-08-01). Not re-raised.

## Done (iteration 70) — ChatGPT consult, PLR site rejected, real audit coverage gap found
- [x] Consulted ChatGPT for an outside critical read (user-initiated). Its
      core diagnosis - distribution is the bottleneck, not production -
      matches what iteration 66/69 already concluded independently; took
      as confirmation, not a new insight. Evaluated every suggestion on
      individual merit rather than adopting the list wholesale:
      accepted (partially) the Machinery Reg tool's "checker" framing
      critique - it was half right, the tool already computes and shows
      the real 10-year cost, only the title/H1/meta said "checker" not
      cost, so retitled without touching the calculation; rejected the
      "publish case studies from completed work" suggestion as premature
      (0 completed paid service engagements exist yet); noted "don't
      worry about Search Console at this stage" as agreement with our
      own prior conclusion, not new information.
- [x] User linked a PLR (Private Label Rights) reseller course site
      (plr.digitalguru.sk). Evaluated it plainly rather than acting on it
      by default: it teaches buying generic pre-made content cheap and
      reselling via paid ads, with unverified self-reported numbers
      ("€1.4M+ sales"). Directly contradicts this project's own rules
      (no unverified numbers, no generic/unverified content) and would
      *increase* the production/distribution imbalance ChatGPT just
      flagged, not fix it. Declined, explained why.
- [x] Searched GitHub for legitimate open-source tools that could help.
      Found `backlink-pilot` - a real tool that auto-submits a site to
      226 external directories/awesome-lists with one command. Did not
      install or run it: it is third-party code of unverified
      trustworthiness performing mass unreviewed external submissions on
      our behalf, which is out of scope even with user permission (the
      standing rule against running untrusted downloaded code). The rest
      of the GitHub search turned up only curated link-lists, not tools.
- [x] User asked for zero-risk technical distribution work. Found a real,
      previously unknown gap: `scripts/audit_site.py` - the crawl
      audit gating every deploy - only ever checked `site/products/*.html`
      and `site/index.html`. Every `site/sk/`, `site/tools/`, `site/blog/`
      and `site/news/` page (exactly where the last ~10 iterations have
      shipped) was never actually audited, just eyeballed at ship time.
      Widened the glob to the whole site. Running it immediately found 2
      real over-length meta descriptions it had been silently missing -
      one introduced by this same session's own Machinery Reg retitle.
      Fixed both, audit now passes clean against the real full site.

## Done (iteration 71) — the SK articles were five dead ends, not a cluster
- [x] Reassessed direction from data rather than opinion. External
      distribution is closed off for now (user declined the directory
      listing and the outreach plan), and SEO on a 1-week-old domain is
      time-bound, so the question became: what ranking lever is still
      *fully* under our control and unused? Measured the site's internal
      link graph to find out instead of guessing.
- [x] Found a real one. Every Slovak article had exactly **one** inbound
      link (`sk/index.html`) and **zero** links to each other - five
      isolated dead-end pages rather than one topic cluster. The
      e-faktúra tool had zero outbound body links at all. On a
      zero-authority domain internal linking is one of the few genuine
      levers available, and it was sitting entirely unused.
- [x] Fixed it systematically, not by hand-editing five files:
      `blog_agent` now generates a "Ďalej čítajte" block on every SK
      article. Pairs are **curated** rather than computed - with five
      articles a similarity score is noise, and a wrong "related" link is
      worse than no link - with a newest-first fallback so future
      articles are covered without touching code.
- [x] Added the two links worth placing by hand: a contextual in-prose
      link from the automation article to the e-faktúra 2027 tool at the
      exact paragraph about re-typing data into an invoicing system (the
      obligation that paragraph describes is literally what the tool
      tests), and a back-link from the tool to that article. Also found
      and fixed the same bare-`index.html` CTA bug on the tool page that
      iteration 68 fixed in the articles - it had been missed because the
      tool is generated by `landing_page_agent`, not `blog_agent`.
- [x] Verified by re-measuring, not by assuming: inbound links per SK
      page went from 1 to 3-6, distributed evenly (added chatbot to the
      website article's related list once the first measurement showed it
      still stranded at 2).
- [x] The same pass surfaced a Slovak typography error that had shipped
      unnoticed since the first SK article: all five opened quotes
      correctly with `„` but closed with a straight ASCII `"` instead of
      `“`. 13 occurrences, including one spanning a line break that the
      scripted fix deliberately skipped and was corrected by hand.
      CLAUDE.md explicitly requires proofreading Slovak before
      publishing; this is exactly the class of error that rule exists for.

## Done (iteration 72) — user asked for a language switcher; found a broken hreflang behind it
- [x] User asked whether the site should have a settable EN/SK language
      switcher so visitors don't have to click around. Investigated the
      real state before building anything, and the question turned out to
      sit on top of two actual defects.
- [x] **Defect 1, the visible one the user felt:** the language link was
      one-way. `/sk/` had "English" in the nav on every page, but the
      English side only offered "Slovensky" down in the footer - a Slovak
      speaker landing on an English page had to scroll the entire page to
      find their own language. Added to the English nav; verified on all
      32 English pages, including `free-online-calculator.html`, which
      bypasses `page_shell()` (it takes the shared header, so the
      documented gotcha didn't bite this time - checked rather than
      assumed).
- [x] **Defect 2, invisible and worse:** hreflang existed only on
      `/sk/index.html`. Verified against Google's own documentation
      before acting: *"If two pages don't both point to each other, the
      tags will be ignored."* So the annotation has been silently
      discarded since /sk/ launched - Google was serving neither language
      preferentially to anyone. Homepage now carries the identical
      reciprocal block, checked byte-for-byte against /sk/'s.
- [x] Pushed back on the literal request where it would have hurt, with
      reasons rather than preference: **no auto-detect/redirect** by
      browser language (Google prefers an explicit selector, and on a site
      whose whole current bottleneck is getting indexed, auto-redirecting
      Googlebot risks hiding a version entirely); **no per-page
      translation switcher**, because EN and SK are not translations -
      English is the product catalogue, Slovak is the services offering,
      and there is no Slovak "Freelance Scope Creep Defense Kit" to point
      at. A switcher promising one would land people on a 404.
- [x] Corrected `blog_agent`'s docstring, which claimed SK articles were
      rendered "with hreflang-correct markup" - they have never had any
      hreflang, and correctly shouldn't, having no English counterpart.
      A docstring asserting a property the code doesn't have is the kind
      of thing a future session would trust and build on.

## Done (iteration 73) — swept for what the audit can't see, found two real SEO bugs
- [x] The hreflang bug in iteration 72 passed every audit for weeks, so
      the question became: what *other* classes of error is the audit
      blind to? Swept 39 pages for eight of them rather than assuming.
- [x] **Bug 1 - `work.html` and `credits.html` canonicalised to the
      homepage**, not to themselves. That tells Google they are duplicates
      of `/` and should not be indexed in their own right - two real pages
      excluded from search by their own markup. Root cause:
      `page_shell()`'s `is_index` flag was quietly doing two unrelated
      jobs, "root-level page, wide layout" and "this page IS the
      homepage". Both pages wanted the first and silently got the second.
      Iteration 72's hreflang addition rode in on the same flag and made
      it worse (both pages started claiming to be the English side of the
      language pair). Split the concerns: `canonical_path` names each
      page's own URL; the hreflang pair is emitted only for the real
      homepage.
- [x] **Bug 2 - the sitemap advertised a URL the page itself disclaims.**
      `/sk/` declared `/sk/` canonical while the sitemap listed
      `/sk/index.html`. Four call sites (sitemap, RSS feed, canonical
      tags, IndexNow) each built absolute URLs by hand and had drifted
      apart. Unified behind `agents.common.canonical_url()`, directory
      form throughout. Sitemap, canonicals, OG tags and the feed now
      agree exactly, with zero orphan sitemap entries.
- [x] Then closed the hole properly rather than just fixing the instances:
      added both checks to `audit_site.py` - canonical must point at the
      page itself, and hreflang must be reciprocal. **Verified the new
      checks actually fire by running them against the unfixed site
      first** (2 canonical + 4 hreflang failures, exit 1) instead of
      trusting a green run on already-fixed output. That run also exposed
      a bug in my own check: an unconditional `index.html` slice mangled
      shorter filenames, so `work.html` matched the homepage and hid the
      exact bug the check was written for. Fixed before relying on it.
- [x] Swept and confirmed genuinely clean, so they're ruled out rather
      than unexamined: img alt text, `<html lang>` vs directory, exactly
      one h1 per page, unique titles and meta descriptions, og:url vs
      canonical agreement, and inline `<script>` syntax (the apostrophe
      class of silent breakage from iteration 64) via `node --check`.

## Done (iteration 74) — checked the links nothing had ever checked
- [x] `audit_site.py` skips http(s) links by design, so no check had ever
      confirmed our cited sources still resolve. Swept the 14 hand-placed
      external links, excluding the ~85 auto-generated news headlines
      (they churn daily; including them would bury the ones that matter).
- [x] **All 3 Gumroad links verified 200** - the only paths to revenue on
      the entire site, and nothing had ever verified them.
- [x] Found the primary government source on the e-faktúra tool,
      `e-fakturacia.finance.gov.sk`, hangs indefinitely from here.
      Confirmed with three independent clients before believing it: curl
      with a real Chrome UA (60s), an actual browser (300s), and urllib
      (ConnectionResetError). DNS resolves and `www.finance.gov.sk`
      itself returns 200, so it is that specific vhost, not the domain.
- [x] **Deliberately did not swap the link out.** Search engines still
      index it as the current official IS EFA page, and a global outage
      is indistinguishable from our own network being blocked - replacing
      a correct citation with a worse one because we couldn't reach it
      would be a downgrade, not a fix. Added the Ministry's own press
      release on the E-faktúra system alongside it instead: verified
      reachable, and verified to genuinely be an MF SR page on this exact
      topic (its body text wouldn't extract, so it is cited only as an
      official source, not as backing for any specific claim). The page
      no longer rests its credibility on one link.
- [x] Built `scripts/check_links.py` and **deliberately kept it out of
      the build gate**. Gates must only fail on things we control;
      blocking a deploy because someone else's server is briefly down
      makes the gate untrustworthy, and people route around gates they
      don't trust. Its own first run proves the point - indiehackers.com
      returned a transient 502 and Pexels a bot-blocking 403, neither a
      real problem.
- [x] Checked the two pending GSC items rather than leaving them open:
      sitemap still "Couldn't fetch" 24h after resubmission (second
      failure, every documented cause already ruled out in iteration 69 -
      nothing further to do from our side), and the Page Indexing report
      still returns "Processing data, please check again in a day or so".
      Stopped poking it; there is no signal there yet to act on.

## Done (iteration 75) — the tools were never checked for being *right*, only for parsing
- [x] Spotted the real gap in iteration 73's sweep: `node --check` proves
      a script parses, never that it computes the right answer. The
      project's hardest rule is "never publish an unverified number", and
      three calculators had been publishing numbers nobody had verified.
- [x] **Found a genuine legal error on the Machinery tool.** It computed
      the obligation window as `life + 10`. Article 10(7)(c) of Regulation
      (EU) 2023/1230, checked against the EUR-Lex primary text rather than
      any summary, requires instructions be accessible "during the
      expected lifetime of the machinery or related product **and** for at
      least 10 years after the placing on the market". Both windows start
      at the placing on the market, so they overlap - the obligation is
      whichever is longer, not the sum. Corrected to `Math.max(life, 10)`.
- [x] The error was not small and not in our favour: a 15-year machine
      showed 25 years and 75,000 EUR against the correct 15 years and
      45,000 EUR. We overstated a legal duty by a decade and a
      competitor's cost by 67% - on the one page whose entire credibility
      rests on getting a regulation right, and while telling readers what
      the Regulation "actually requires".
- [x] The sharpest detail: **the page's own prose quoted the Regulation
      correctly the whole time.** Only the calculator misread the very
      sentence printed above it. Verbatim quoting is not the same as
      correctly implementing what was quoted, and nothing in the pipeline
      compares the two.
- [x] Verified the fix by executing the real widget code against a stubbed
      DOM instead of reading it: 15y->15/45,000, 5y->10/30,000 (floor
      applies), 10y->10 (boundary), 30y->30/36,000. Ran the same harness
      over the other two calculators - scope-creep and freelance-rate are
      both arithmetically correct and needed no change.
- [x] Corrected the iteration-64 TASKBOARD entry that cited 75,000 EUR as
      a selling point, annotating it rather than silently rewriting it so
      the error stays visible in the record.

## Done (iteration 76) — price consistency verified, and a false claim in our own records
- [x] Continued the content-correctness sweep that iteration 75 started
      (as opposed to the markup sweep, which is exhausted). Next class:
      **do our own prices agree across the site?** A published price that
      contradicts another published price is a credibility problem and a
      potential dispute with a real customer, and nothing had checked it.
- [x] Extracted every euro figure from every Slovak page and compared the
      ones we present as *our* prices against the canonical pricing table
      on `/sk/`. **All consistent:** automation 390, chatbot 690, logo
      390, websites 590 / 1 190, each matching the table exactly. The
      other figures on those pages are competitor market ranges, which is
      what they are presented as. No change needed - a clean result that
      is now established rather than assumed.
- [x] The check surfaced something else: the pricing table has **six**
      line items, and only **five** articles exist. "Digitálny produkt na
      mieru" (290 EUR) has no Slovak article.
- [x] That gap is deliberate - iteration 66 SERP-checked custom-tool
      pricing and rejected it as held by real incumbents with fresh 2026
      content. **But our records claimed otherwise:** iteration 65 stated
      design/branding was "the one service of five" without an article,
      and `memory/03_Tasks.md` said "all 5 SK service articles". Both
      would have told a future session that coverage was complete.
- [x] Corrected both, and recorded *why* there is no article rather than
      just noting the gap - a bare gap invites someone to close it by
      writing for a query we already know we would lose. Annotated the
      iteration-65 entry instead of rewriting it, same as the 75,000 EUR
      correction, so the mistake stays visible in the record.

## Done (iteration 77) — a day of falsification, closed with a negative result
- [x] User rejected the previous week's output as "pure AI average" and set
      a quality bar: own thesis, own findings, tools that decide rather
      than calculate, and a flagship that would hurt to have copied.
      Agreed rather than defended - five Slovak articles shared one
      template with the numbers swapped, and correctness work (canonical,
      hreflang, arithmetic) cannot produce demand no matter how much of it
      is done.
- [x] Designed one flagship candidate instead of producing more: a
      self-collected dataset on machinery documentation availability, on
      the reasoning that a daily pipeline can build a longitudinal dataset
      a competitor cannot copy in a weekend.
- [x] Ran it as a **falsification experiment** under the user's protocol:
      pre-registered decision thresholds, a mandatory UNKNOWN category,
      unit of analysis fixed in advance, and a stop rule. Full record in
      **`docs/RESEARCH_LOG.md` (RL-1)**.
- [x] Six approaches, six failures, each for a specific reason: Wayback
      all-PDF (population was marketing material); Wayback docs-only
      (failures cluster per manufacturer, so per-document aggregation is
      the wrong statistic); hand-picked frame (selection bias); systematic
      Wikidata frame (11 of 199 yielded data); static accessibility census
      (64.7% UNKNOWN); rendered calibration (84% of eligible UNKNOWNs
      resolved - the stop rule fired, UNKNOWN was an instrument artifact).
- [x] **The protocol earned its keep.** An early pass produced 64.1%,
      which would have read as "64% of manufacturers' documentation is
      unavailable" - false, driven by brochures and by three defects in
      our own classifier, none of which crashed anything. It was only
      caught because the protocol forced segmentation and an UNKNOWN
      category. A favourite hypothesis (dead documentation subdomains =
      "the problem is URL infrastructure") also died: 0% HOST_GONE in the
      systematic frame, it was an artifact of hand-picking large firms.
- [x] Verified and kept: 9 manufacturers (12 domains) publish at a direct
      public URL, re-verified 12/12. Recorded honestly as validation of
      one positive class, not of the classifier - and as too thin (~12
      URLs) to seed an observatory.
- [x] Closed the line. **Machinery Regulation removed from flagship
      candidates** - not for lack of interest but because no cheap, open,
      representative data source exists. None of RL-1's numbers may become
      site content; they describe our instruments, not any market.
- [x] Adopted the day's real output as a standing rule: work runs
      `observable property -> population -> measurement -> falsification ->
      dataset -> product`, never `topic -> content -> tool -> SEO -> look
      for evidence`. Future flagship candidates must pass the 7-point
      filter in `docs/RESEARCH_LOG.md`.

## Milestones
- **M1 — Discovery loop proven with real data** ✅ (iteration 1)
- **M2 — First real product file exists and is reviewable by the user** ✅ (iteration 2 — see `data/exports/products/`)
- **M2.5 — Pipeline runs autonomously on a schedule, not just locally** ✅ (iteration 5 — see the Actions tab on the repo)
- **M3 — First page published and receiving organic traffic** 🚧 (iteration 7 — deployed, traffic not yet measured)
- **M4 — First measured lead or sale attributed to the pipeline**
