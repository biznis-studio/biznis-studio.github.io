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

TOOLS = [
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
