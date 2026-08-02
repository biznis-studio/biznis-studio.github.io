"""Free Widgets Agent.

Builds small, genuinely useful, self-contained interactive tools under
site/tools/. Added on user request for "free widgets that attract
attention" - the strategy being that a calculator answering a question
someone is actively searching for is a far better entry point than a
landing page asking them to buy something.

Design constraints, all deliberate:
  - Vanilla JS inline, no libraries, no build step, no external requests.
  - Every tool answers one specific question and shows its arithmetic, so
    the result is checkable rather than a black box.
  - Each tool links to the relevant paid kit *after* delivering its value,
    never as a gate in front of it.
"""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.common import card_art
from agents.landing_page_agent import OG_IMAGE_TAGS, SITE_BASE_URL, page_shell

TOOLS_DIR = Path(__file__).resolve().parent.parent / "site" / "tools"


SCOPE_CREEP_WIDGET = """
<div class="widget">
  <div class="widget-row">
    <div>
      <label for="rate">Your effective hourly rate</label>
      <input id="rate" type="number" min="0" step="5" value="75">
    </div>
    <div>
      <label for="cur">Currency</label>
      <select id="cur">
        <option value="$">$ USD</option>
        <option value="&euro;">&euro; EUR</option>
        <option value="&pound;">&pound; GBP</option>
      </select>
    </div>
  </div>
  <div class="widget-row">
    <div>
      <label for="hours">Unbilled "quick favour" hours per week</label>
      <input id="hours" type="number" min="0" step="0.5" value="2">
    </div>
    <div>
      <label for="clients">Concurrent clients doing this</label>
      <input id="clients" type="number" min="1" step="1" value="1">
    </div>
  </div>
  <div class="widget-out">
    <b id="year">&mdash;</b>
    <span id="breakdown">per year of work you did and nobody paid for</span>
  </div>
  <p class="widget-note" id="detail"></p>
</div>
<script>
(function () {
  var ids = ['rate', 'hours', 'clients', 'cur'];
  function fmt(cur, n) {
    return cur + Math.round(n).toLocaleString('en-US');
  }
  function calc() {
    var rate = parseFloat(document.getElementById('rate').value) || 0;
    var hours = parseFloat(document.getElementById('hours').value) || 0;
    var clients = parseFloat(document.getElementById('clients').value) || 1;
    var cur = document.getElementById('cur').value;
    var week = rate * hours * clients;
    document.getElementById('year').textContent = fmt(cur, week * 52);
    document.getElementById('detail').textContent =
      fmt(cur, week) + ' per week  ·  ' + fmt(cur, week * 4.33) + ' per month  ·  ' +
      fmt(cur, week * 26) + ' per 6-month project. That is ' +
      (hours * clients) + ' hours a week you are working for free.';
  }
  ids.forEach(function (id) {
    var el = document.getElementById(id);
    el.addEventListener('input', calc);
    el.addEventListener('change', calc);
  });
  calc();
})();
</script>
"""

RATE_WIDGET = """
<div class="widget">
  <div class="widget-row">
    <div>
      <label for="income">Target take-home income per year</label>
      <input id="income" type="number" min="0" step="1000" value="60000">
    </div>
    <div>
      <label for="cur2">Currency</label>
      <select id="cur2">
        <option value="$">$ USD</option>
        <option value="&euro;">&euro; EUR</option>
        <option value="&pound;">&pound; GBP</option>
      </select>
    </div>
  </div>
  <div class="widget-row">
    <div>
      <label for="expenses">Yearly business expenses (tools, insurance, accountant)</label>
      <input id="expenses" type="number" min="0" step="500" value="6000">
    </div>
    <div>
      <label for="tax">Tax + social contributions (%)</label>
      <input id="tax" type="number" min="0" max="90" step="1" value="30">
    </div>
  </div>
  <div class="widget-row">
    <div>
      <label for="weeks">Working weeks per year (after holiday/sick)</label>
      <input id="weeks" type="number" min="1" max="52" step="1" value="45">
    </div>
    <div>
      <label for="billable">Genuinely billable hours per week</label>
      <input id="billable" type="number" min="1" max="60" step="1" value="25">
    </div>
  </div>
  <div class="widget-out">
    <b id="hourly">&mdash;</b>
    <span>minimum hourly rate to actually hit your target</span>
  </div>
  <p class="widget-note" id="detail2"></p>
</div>
<script>
(function () {
  var ids = ['income', 'expenses', 'tax', 'weeks', 'billable', 'cur2'];
  function fmt(cur, n) { return cur + Math.round(n).toLocaleString('en-US'); }
  function calc() {
    var income = parseFloat(document.getElementById('income').value) || 0;
    var expenses = parseFloat(document.getElementById('expenses').value) || 0;
    var tax = parseFloat(document.getElementById('tax').value) || 0;
    var weeks = parseFloat(document.getElementById('weeks').value) || 1;
    var billable = parseFloat(document.getElementById('billable').value) || 1;
    var cur = document.getElementById('cur2').value;
    var taxRate = Math.min(Math.max(tax, 0), 95) / 100;
    var gross = (income / (1 - taxRate)) + expenses;
    var hours = weeks * billable;
    var hourly = gross / hours;
    document.getElementById('hourly').textContent = fmt(cur, hourly) + ' / hour';
    document.getElementById('detail2').textContent =
      'You need to invoice about ' + fmt(cur, gross) + ' a year to take home ' +
      fmt(cur, income) + ' after tax and expenses, across ' + Math.round(hours) +
      ' billable hours. A day rate at this level is roughly ' + fmt(cur, hourly * 8) + '.';
  }
  ids.forEach(function (id) {
    var el = document.getElementById(id);
    el.addEventListener('input', calc);
    el.addEventListener('change', calc);
  });
  calc();
})();
</script>
"""


MACHINERY_WIDGET = """
<div class="widget">
  <label for="m1">Do you place machinery on the EU market (manufacture, import or rebrand)?</label>
  <select id="m1">
    <option value="yes">Yes</option>
    <option value="no">No, we only use machinery</option>
  </select>

  <label for="m2">How do you supply instructions for use today?</label>
  <select id="m2">
    <option value="paper">Printed manual in the crate</option>
    <option value="pdf">PDF on our website or on a USB stick</option>
    <option value="portal">A hosted documentation portal / CCMS subscription</option>
  </select>

  <div class="widget-row">
    <div>
      <label for="m3">Member states you sell into</label>
      <input id="m3" type="number" min="1" max="27" step="1" value="4">
    </div>
    <div>
      <label for="m4">Expected service life of the machine (years)</label>
      <input id="m4" type="number" min="1" max="40" step="1" value="15">
    </div>
  </div>

  <label for="m5">If you use a subscription documentation platform, what does it cost per month? (0 if none)</label>
  <input id="m5" type="number" min="0" step="10" value="0">

  <div class="widget-out">
    <b id="myears">&mdash;</b>
    <span>minimum years your instructions URL must keep resolving</span>
  </div>
  <div id="mdetail" style="margin-top:1.2rem"></div>
</div>
<script>
(function () {
  var ids = ['m1','m2','m3','m4','m5'];
  function val(id){ var e=document.getElementById(id); return e.value; }
  function calc() {
    var inScope = val('m1') === 'yes';
    var how = val('m2');
    var states = Math.max(1, parseInt(val('m3')) || 1);
    var life = Math.max(1, parseInt(val('m4')) || 1);
    var monthly = parseFloat(val('m5')) || 0;
    var years = life + 10;
    var parts = [];

    document.getElementById('myears').textContent = years + ' years';

    if (!inScope) {
      parts.push('<p>Article 10(7) places the obligation on whoever <strong>places the machinery on the market</strong> - manufacturers, importers and anyone rebranding it. As a user you are not the duty holder, though you should expect suppliers to give you a durable link rather than a PDF.</p>');
      document.getElementById('mdetail').innerHTML = parts.join('');
      return;
    }

    parts.push('<h3>What the Regulation actually requires</h3>');
    parts.push('<p>If you choose to supply instructions digitally, Article 10(7) of Regulation (EU) 2023/1230 requires you to:</p><ul>' +
      '<li>mark <strong>on the machine itself</strong> how to reach the digital instructions</li>' +
      '<li>present them so the user can <strong>print, download and save</strong> them</li>' +
      '<li>keep them <strong>accessible online for the expected lifetime plus at least 10 years</strong> after the machine was placed on the market</li>' +
      '<li>provide them in a language determined by each member state you sell into</li></ul>');
    parts.push('<p>For your inputs that is <strong>' + years + ' years</strong> of guaranteed availability, in <strong>' + states + ' language set' + (states>1?'s':'') + '</strong>.</p>');

    if (how === 'paper') {
      parts.push('<h3>Your situation</h3><p>Paper remains allowed, so nothing forces you to change. The reason most builders move anyway is cost: reprinting and reshipping a manual in ' + states + ' languages for every unit, and reissuing it whenever anything changes. Digital removes the reprint, but replaces it with a hosting obligation you are then stuck with for ' + years + ' years.</p>');
    } else if (how === 'pdf') {
      parts.push('<h3>Your situation - this is the common trap</h3><p>A PDF on your website looks like it already satisfies this, and mostly it does <em>today</em>. The parts that usually do not hold up: a marking on the machine that points to a <strong>stable</strong> address, and a commitment that the same address still resolves in ' + years + ' years - through a site redesign, a CMS migration, or a change of web agency.</p><p>A URL that breaks in year six is a compliance failure discovered by whoever owns the machine, not by you.</p>');
    } else {
      parts.push('<h3>Your situation</h3><p>A hosted portal solves the requirement while you keep paying for it. The question worth asking is what happens to those URLs if you stop - the obligation runs for ' + years + ' years and does not end with your subscription.</p>');
    }

    if (monthly > 0) {
      var total = monthly * 12 * years;
      parts.push('<div class="widget-out" style="margin-top:1.2rem"><b>' + Math.round(total).toLocaleString('en-US') + ' EUR</b><span>what your current subscription costs across the ' + years + '-year obligation, at the current price</span></div>');
      parts.push('<p class="widget-note">That is the figure worth comparing against a one-off build. It also assumes the price never rises and the vendor still exists in ' + years + ' years.</p>');
    }

    parts.push('<h3>What actually has to survive ' + years + ' years</h3><ul>' +
      '<li><strong>A domain</strong> you control and keep renewing - not the agency one, not a platform one</li>' +
      '<li><strong>A stable URL per machine or per model</strong>, since it is physically marked on the product</li>' +
      '<li><strong>Files, not a running application.</strong> Anything with a database, a login or a framework needs maintaining for a decade. Plain pages and PDFs do not.</li>' +
      '<li><strong>An archive of superseded versions</strong>, because a machine sold in 2027 needs its 2027 instructions, not the current ones</li></ul>');
    parts.push('<p class="widget-note">This is an orientation tool covering the publication requirements of Article 10(7). It is not conformity assessment, and it does not cover the risk assessment, the essential health and safety requirements, or the technical file.</p>');

    document.getElementById('mdetail').innerHTML = parts.join('');
  }
  ids.forEach(function(id){
    var el = document.getElementById(id);
    el.addEventListener('input', calc); el.addEventListener('change', calc);
  });
  calc();
})();
</script>
"""

TOOLS = [
    {
        "slug": "machinery-regulation-digital-instructions",
        "title": "EU Machinery Regulation: what a 10-year instructions URL actually costs",
        "description": ("Free calculator: how many years your instructions URL must stay live "
                        "under Article 10(7), and what that costs on a subscription versus a "
                        "static page you own."),
        "intro": ("Regulation (EU) 2023/1230 lets you supply instructions for use digitally - "
                  "but only if the link keeps working for the machine's lifetime plus ten "
                  "years. Most builders discover the second part later than the first."),
        "widget": MACHINERY_WIDGET,
        "after": ("<h2>Why the ten years is the hard part</h2>"
                  "<p>Going digital is usually framed as a saving: no reprinting a manual in "
                  "four languages for every unit shipped. That saving is real. What it buys is "
                  "an obligation to keep an address alive for longer than most companies keep "
                  "the same website.</p>"
                  "<p>Article 10(7) is explicit that the instructions must be "
                  "<em>accessible online during the expected lifetime of the machinery and for "
                  "at least 10 years after the placing on the market</em>, reachable from a "
                  "marking on the machine itself, and downloadable and printable by the user.</p>"
                  "<h2>What that means technically</h2>"
                  "<p>The requirement rewards the least sophisticated architecture available. A "
                  "database, a login, a CMS or a JavaScript framework is something that must be "
                  "patched, migrated and paid for across a decade. Static files on a domain you "
                  "own are the opposite: nothing to maintain, nothing to expire, and cheap "
                  "enough that nobody ever cancels it to save money.</p>"
                  "<p>The parts that genuinely need care are version archiving - a machine sold "
                  "in 2027 must keep <em>its</em> instructions, not the current revision - and "
                  "making the marked URL stable enough that it survives every future redesign.</p>"
                  "<h2>If you want this built</h2>"
                  "<p>We build exactly this shape of thing: a static multilingual instructions "
                  "site, per-model permanent URLs with QR assets for the machine plate, "
                  "versioned archives, and a build pipeline that turns your existing source "
                  "documents into both the web pages and the downloadable PDFs. You own the "
                  "domain, the files and the pipeline - there is no subscription to cancel and "
                  "nothing of ours that has to still exist in 2040.</p>"
                  "<p>We publish documents. We do not perform conformity assessment, we are not "
                  "a notified body, and this tool is not legal advice - your risk assessment and "
                  "technical file remain yours or your consultant's.</p>"
                  "<p><a class=\"button\" href=\"../index.html#services\">Talk to us about it</a></p>"),
    },
    {
        "slug": "scope-creep-cost-calculator",
        "title": "Scope Creep Cost Calculator",
        "description": ("Work out what unbilled “quick favours” actually cost you per week, "
                        "month and year. Free, instant, nothing to install."),
        "intro": ("Scope creep never feels like money leaving the room, because it never appears "
                  "on an invoice. Put your real numbers in and it stops looking small."),
        "widget": SCOPE_CREEP_WIDGET,
        "after": ("<h2>What to do with that number</h2>"
                  "<p>If the annual figure surprised you, the fix is rarely “be tougher” - "
                  "it is having wording ready for the five or six moments where scope actually "
                  "stretches, and a log where every addition gets an estimate attached to it. "
                  "A request logged as “+4 hours” stops being a favour and becomes a "
                  "decision the client makes knowingly.</p>"
                  "<p>We packaged exactly that as the "
                  "<a href=\"../products/freelance-scope-creep-defense-kit.html\">Freelance Scope "
                  "Creep Defense Kit</a> - 7 ready-to-send scripts plus a Change Request Log "
                  "template. The first script is readable in full on that page, so you can judge "
                  "the wording before paying anything.</p>"),
    },
    {
        "slug": "freelance-rate-calculator",
        "title": "Freelance Hourly Rate Calculator",
        "description": ("Find the minimum hourly rate that actually delivers your target take-home "
                        "income, after tax, expenses and non-billable time."),
        "intro": ("Most freelancers set a rate by copying someone else's. This works backwards from "
                  "the only number that matters: what you need to take home."),
        "widget": RATE_WIDGET,
        "after": ("<h2>Why the honest number is higher than people expect</h2>"
                  "<p>Two things quietly destroy the naive calculation. First, a big share of your "
                  "week is not billable - admin, proposals, invoicing, and the client calls nobody "
                  "pays for. Second, tax and social contributions come out of gross, not net. Miss "
                  "either and you set a rate that mathematically cannot reach your target.</p>"
                  "<p>The output above is a <em>floor</em>, not a recommendation: it is the point "
                  "below which you are structurally losing money. Value, scarcity and demand all "
                  "sit above it.</p>"
                  "<p>If your rate is fine but renewals are where money leaks, the "
                  "<a href=\"../products/client-retainer-renewal-kit.html\">Client Retainer Renewal "
                  "Kit</a> covers the eight conversations where retainers quietly stay at year-one "
                  "pricing.</p>"),
    },
]


def _head_extras(title: str, description: str, path: str) -> str:
    if not SITE_BASE_URL:
        return ""
    url = f"{SITE_BASE_URL}/{path}"
    return (
        f'<link rel="canonical" href="{html.escape(url)}">\n'
        f'<meta property="og:title" content="{html.escape(title)}">\n'
        f'<meta property="og:description" content="{html.escape(description)}">\n'
        f'<meta property="og:url" content="{html.escape(url)}">\n'
        f'<meta property="og:type" content="website">\n' + OG_IMAGE_TAGS
    )


def _with_extras(page: str, extras: str) -> str:
    if not extras:
        return page
    idx = page.lower().find("</head>")
    return page[:idx] + extras + page[idx:] if idx != -1 else page


def build_tool(tool: dict) -> None:
    body = f"""{card_art(tool["slug"], tool["title"])}
<span class="eyebrow">Free tool</span>
<h1>{html.escape(tool["title"])}</h1>
<p class="subtitle">{html.escape(tool["intro"])}</p>
{tool["widget"]}
{tool["after"]}
<p class="form-note">Runs entirely in your browser. Nothing you type is sent anywhere,
stored, or logged - there is no server involved and no analytics on this tool.</p>
<p><a href="index.html">&larr; All free tools</a></p>"""
    page = page_shell(f'{tool["title"]} - Free', tool["description"], body)
    page = _with_extras(page, _head_extras(tool["title"], tool["description"],
                                           f'tools/{tool["slug"]}.html'))
    (TOOLS_DIR / f'{tool["slug"]}.html').write_text(page)


def build_index() -> None:
    cards = "\n".join(
        f'<a class="product-card" href="{t["slug"]}.html">'
        f'{card_art(t["slug"], t["title"])}'
        f'<span class="badge" style="background:#0891b2">free tool</span>'
        f'<h3>{html.escape(t["title"])}</h3>'
        f'<p>{html.escape(t["description"])}</p></a>'
        for t in TOOLS
    )
    body = f"""<div class="hero">
<span class="eyebrow">Free &middot; no signup</span>
<h1>Free tools</h1>
<p class="subtitle">Small calculators that answer one specific money question for freelancers
and consultants. They run in your browser, need no account, and nothing you type leaves
your device.</p>
</div>
<div class="product-grid">{cards}</div>"""
    title = "Free tools for freelancers - Biznis"
    desc = ("Free browser-based calculators for freelancers: scope creep cost and minimum "
            "hourly rate. No signup, nothing stored.")
    page = page_shell(title, desc, body, is_index=False)
    page = _with_extras(page, _head_extras(title, desc, "tools/index.html"))
    (TOOLS_DIR / "index.html").write_text(page)


def tool_entries() -> list[dict]:
    """For sitemap/RSS inclusion by seo_agent."""
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entries = [{"url": "tools/index.html", "title": "Free tools for freelancers",
                "meta_description": "Free browser-based calculators for freelancers.",
                "created_at": today}]
    entries += [{"url": f'tools/{t["slug"]}.html', "title": t["title"],
                 "meta_description": t["description"], "created_at": today} for t in TOOLS]
    return entries


def run() -> int:
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    for tool in TOOLS:
        build_tool(tool)
    build_index()
    print(f"[tools_agent] built {len(TOOLS)} free tools + index")
    return len(TOOLS)


if __name__ == "__main__":
    run()
