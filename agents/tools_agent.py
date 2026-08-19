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

from agents.common import canonical_url, card_art
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
    // Art. 10(7)(c): "during the expected lifetime ... AND for at least 10
    // years after the placing on the market". Both windows start at the
    // placing on the market, so they overlap - the obligation is whichever
    // is longer, not the sum. This read life + 10 until 2026-08-02, which
    // overstated a 15-year machine by a decade and its subscription cost
    // by 67%. Verified against the EUR-Lex primary text, not a summary.
    var years = Math.max(life, 10);
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
      '<li>keep them <strong>accessible online for the expected lifetime of the machine, and in any case for at least 10 years</strong> after it was placed on the market</li>' +
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

OPLATI_SA_WIDGET = """
<div class="widget">
  <div class="widget-row">
    <div>
      <label for="minuty">Ko\u013eko min\u00fat zaberie jeden pr\u00edpad</label>
      <input id="minuty" type="number" min="1" step="1" value="25">
    </div>
    <div>
      <label for="tyzdenne">Ko\u013ekokr\u00e1t t\u00fd\u017edenne</label>
      <input id="tyzdenne" type="number" min="1" step="1" value="12">
    </div>
  </div>
  <div class="widget-row">
    <div>
      <label for="opravy">Z ko\u013ek\u00fdch % pr\u00edpadov sa nie\u010do opravuje</label>
      <input id="opravy" type="number" min="0" max="100" step="1" value="15">
    </div>
    <div>
      <label for="sadzba">N\u00e1klad na hodinu pr\u00e1ce (\u20ac)</label>
      <input id="sadzba" type="number" min="1" step="1" value="18">
    </div>
  </div>
  <div id="vysledok" class="widget-out"></div>
</div>
<script>
(function () {
  var pole = ["minuty", "tyzdenne", "opravy", "sadzba"].map(function (i) {
    return document.getElementById(i);
  });
  var out = document.getElementById("vysledok");

  function cislo(el, min, max) {
    var v = parseFloat(el.value);
    if (isNaN(v)) return null;
    if (v < min || v > max) return null;
    return v;
  }

  function prepocitaj() {
    var m = cislo(pole[0], 1, 10000),
        t = cislo(pole[1], 1, 10000),
        o = cislo(pole[2], 0, 100),
        s = cislo(pole[3], 1, 10000);
    if (m === null || t === null || o === null || s === null) {
      out.innerHTML = "<p>Doplňte všetky štyri čísla.</p>";
      return;
    }
    var hodinRocne = (m * t * 52) / 60;
    var eurRocne = hodinRocne * s;
    var cielOprav = Math.max(1, Math.round(o / 2));
    var verdikt, preco;
    if (hodinRocne < 10) {
      verdikt = "Neoplatí sa.";
      preco = "Pod desiatimi hodinami ročne je náklad na zadanie, otestovanie a odovzdanie vyšší než úspora.";
    } else if (hodinRocne < 40) {
      verdikt = "Hraničné.";
      preco = "Oplatí sa vtedy, ak úloha zvykne padnúť alebo sa robí s chybami — teda ak je podiel opráv vysoký.";
    } else {
      verdikt = "Oplatí sa počítať vážne.";
      preco = "Pri tomto objeme sa investícia vráti aj pri skromnom zlepšení.";
    }
    out.innerHTML =
      "<p class='widget-big'>" + verdikt + "</p>" +
      "<p>" + preco + "</p>" +
      "<h3>Aritmetika, nech si ju viete skontrolovať</h3>" +
      "<ul>" +
      "<li>" + m + " min &times; " + t + " týždenne &times; 52 týždňov &divide; 60 = <strong>" +
        hodinRocne.toFixed(1) + " hodín ročne</strong></li>" +
      "<li>" + hodinRocne.toFixed(1) + " h &times; " + s + " € = <strong>" +
        Math.round(eurRocne) + " € ročne</strong> v čase, ktorý nikto nefakturuje</li>" +
      "</ul>" +
      "<h3>Toto si zapíšte PRED nasadením</h3>" +
      "<p>Bez týchto troch riadkov sa o rok nedá povedať, či to niečo prinieslo — " +
      "a hlavne sa nedá projekt ukončiť.</p>" +
      "<ol>" +
      "<li><strong>Stav teraz:</strong> " + m + " minút na prípad, " + o + " % prípadov sa opravuje. " +
        "Odmerajte päť prípadov stopkami, nehádajte.</li>" +
      "<li><strong>Termín rozhodnutia:</strong> dva mesiace od nasadenia.</li>" +
      "<li><strong>Podmienka ukončenia:</strong> „Ak sa do dvoch mesiacov podiel opráv nezníži " +
        "pod " + cielOprav + " %, vraciame sa k pôvodnému postupu.“</li>" +
      "</ol>";
  }

  pole.forEach(function (el) { el.addEventListener("input", prepocitaj); });
  prepocitaj();
})();
</script>
"""

TOOLS = [
    {
        "slug": "oplati-sa-nasadit-ai",
        "lang": "sk",
        "title": "Oplat\u00ed sa na t\u00fato \u00falohu nasadi\u0165 AI?",
        "description": ("Bezplatn\u00e1 kalkula\u010dka: ko\u013eko hod\u00edn a eur t\u00e1 \u00faloha stoj\u00ed ro\u010dne, "
                        "a ak\u00fa podmienku ukon\u010denia si m\u00e1te zap\u00edsa\u0165 e\u0161te pred nasaden\u00edm."),
        "intro": ("Ot\u00e1zka, ktor\u00e1 rozhodne o osude cel\u00e9ho projektu, znie: \u010do by sme museli "
                  "vidie\u0165, aby sme povedali, \u017ee to nefunguje? Kto na \u0148u nem\u00e1 odpove\u010f pred "
                  "za\u010diatkom, nedozvie sa ju ani potom. T\u00e1to kalkula\u010dka ju nap\u00ed\u0161e za v\u00e1s."),
        "widget": OPLATI_SA_WIDGET,
        "after": ("<h2>Pre\u010do prv\u00e9 \u010d\u00edslo rozhoduje</h2>"
                  "<p>\u00daloha na desa\u0165 min\u00fat mesa\u010dne je dve hodiny ro\u010dne. Zadanie, otestovanie "
                  "a odovzdanie stoj\u00ed viac. \u00daloha na dve hodiny t\u00fd\u017edenne je zhruba sto hod\u00edn "
                  "ro\u010dne \u2014 a to je u\u017e nieko\u013eko tis\u00edc eur v \u010dase, ktor\u00fd nikto nefakturuje. "
                  "To \u010d\u00edslo rozhodne sk\u00f4r ne\u017e ktor\u00fdko\u013evek predajca softv\u00e9ru.</p>"
                  "<h2>Pre\u010do podiel opr\u00e1v rozhoduje e\u0161te viac</h2>"
                  "<p>\u010cas sa d\u00e1 u\u0161etri\u0165 aj tak, \u017ee v\u00fdstup nikto neskontroluje. To nie je "
                  "\u00faspora, to je odlo\u017een\u00fd n\u00e1klad. Preto sa meria podiel pr\u00edpadov, ktor\u00e9 sa "
                  "musia opravova\u0165 \u2014 chyby stoja viac ne\u017e min\u00faty.</p>"
                  "<h2>\u010co t\u00e1to kalkula\u010dka NEROB\u00cd</h2>"
                  "<p>Nepovie v\u00e1m, \u017ee sa to oplat\u00ed. Povie v\u00e1m, \u010di sa to oplat\u00ed <em>po\u010d\u00edta\u0165</em>, "
                  "a d\u00e1 v\u00e1m vetu, pod\u013ea ktorej to o dva mesiace vyhodnot\u00edte. Rozdiel medzi firmou, "
                  "ktor\u00e1 o rok vie, \u010do jej AI priniesla, a firmou, ktor\u00e1 o tom vedie debatu na "
                  "porade, je pr\u00e1ve t\u00e1 veta.</p>"
                  "<p>Cel\u00fd postup aj s t\u00fdm, \u010do meran\u00edm nie je, je v \u010dl\u00e1nku "
                  "<a href=\"../sk/ako-zistite-ci-ai-nieco-priniesla.html\">Ako zist\u00edte, \u010di v\u00e1m AI "
                  "naozaj nie\u010do priniesla</a>.</p>"),
    },
    {
        "slug": "machinery-regulation-digital-instructions",
        "title": "EU Machinery Regulation: what a 10-year instructions URL actually costs",
        "description": ("Free calculator: how many years your instructions URL must stay live "
                        "under Article 10(7), and what that costs on a subscription versus a "
                        "static page you own."),
        "intro": ("Regulation (EU) 2023/1230 lets you supply instructions for use digitally - "
                  "but only if the link keeps working for the machine's whole expected "
                  "lifetime, and never less than ten years. Most builders discover the "
                  "second part later than the first."),
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
    url = canonical_url(SITE_BASE_URL, path)
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
    jazyk = tool.get("lang", "en")
    _eyebrow = "N\u00e1stroj zadarmo" if jazyk == "sk" else "Free tool"
    _poznamka = ("Be\u017e\u00ed cel\u00fd vo va\u0161om prehliada\u010di. Ni\u010d, \u010do nap\u00ed\u0161ete, "
                 "sa nikam neodosiela, neuklad\u00e1 ani nezaznamen\u00e1va \u2014 \u017eiadny server, "
                 "\u017eiadne meranie n\u00e1v\u0161tevnosti."
                 if jazyk == "sk" else
                 "Runs entirely in your browser. Nothing you type is sent anywhere, "
                 "stored, or logged - there is no server involved and no analytics on this tool.")
    body = f"""{card_art(tool["slug"], tool["title"], hero=True)}
<span class="eyebrow">{_eyebrow}</span>
<h1>{html.escape(tool["title"])}</h1>
<p class="subtitle">{html.escape(tool["intro"])}</p>
{tool["widget"]}
{tool["after"]}
<p class="form-note">{_poznamka}</p>
{_kontakt(jazyk)}
{_spat(jazyk)}"""
    # Slovensky nastroj ide do /sk/, nie do /tools/. Navigacia v page_shell(lang="sk")
    # je pisana relativne voci /sk/ — z /tools/ ukazuje na neexistujuce stranky
    # a audit to spravne zachytil. Zaroven je tam, kam slovensky navstevnik chodi,
    # a dostane sa do sitemap-sk.xml.
    kam = (TOOLS_DIR.parent / "sk") if jazyk == "sk" else TOOLS_DIR
    cesta = f'sk/{tool["slug"]}.html' if jazyk == "sk" else f'tools/{tool["slug"]}.html'
    pripona = "Zadarmo" if jazyk == "sk" else "Free"
    page = page_shell(f'{tool["title"]} - {pripona}', tool["description"], body, lang=jazyk)
    page = _with_extras(page, _head_extras(tool["title"], tool["description"], cesta))
    if jazyk != "en":
        page = page.replace('<html lang="en">', f'<html lang="{jazyk}">')
    kam.mkdir(parents=True, exist_ok=True)
    (kam / f'{tool["slug"]}.html').write_text(page)


def build_index() -> None:
    cards = "\n".join(
        f'<a class="product-card" href="{t["slug"]}.html">'
        f'{card_art(t["slug"], t["title"])}'
        f'<span class="badge" style="background:#0891b2">free tool</span>'
        f'<h3>{html.escape(t["title"])}</h3>'
        f'<p>{html.escape(t["description"])}</p></a>'
        for t in TOOLS if t.get("lang", "en") == "en"
    )
    body = f"""<div class="hero">
<span class="eyebrow">Free &middot; no signup</span>
<h1>Free tools</h1>
<p class="subtitle">Small calculators that answer one specific money question for freelancers
and consultants. They run in your browser, need no account, and nothing you type leaves
your device.</p>
</div>
<div class="product-grid">{cards}</div>
{_kontakt()}"""
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
    # Slovensky nastroj zije v /sk/, takze aj do sitemapy patri pod tou cestou.
    entries += [{"url": (f'sk/{t["slug"]}.html' if t.get("lang") == "sk"
                         else f'tools/{t["slug"]}.html'),
                 "title": t["title"],
                 "meta_description": t["description"], "created_at": today} for t in TOOLS]
    return entries



def _spat(jazyk: str) -> str:
    if jazyk == "sk":
        return '<p><a href="index.html">&larr; Sp\u00e4\u0165 na slu\u017eby</a></p>'
    return '<p><a href="index.html">&larr; All free tools</a></p>'


def _kontakt(jazyk: str = "en") -> str:
    """Formular aj na prehlade nastrojov.

    Kontrola 2026-08-17: blog index a prehlad nastrojov boli jedine stranky,
    na ktore navstevnik pristane a nema sa ako ozvat - slepa ulicka.

    Jazyk 2026-08-19: slovensky nastroj mal anglicky nadpis formulara
    ("Need something like this built?") na inak slovenskej stranke.
    """
    from agents.landing_page_agent import FORMSPREE_ENDPOINT, contact_form_html
    if not FORMSPREE_ENDPOINT:
        return ""
    if jazyk == "sk":
        return ('<h2 id="kontakt" class="section-title">Potrebujete nie\u010do tak\u00e9ho '
                'postavi\u0165?</h2>\n'
                '<p>Tieto n\u00e1stroje s\u00fa zadarmo, lebo s\u00fa mal\u00e9. Ak potrebujete '
                'nie\u010do pre va\u0161ich z\u00e1kazn\u00edkov alebo v\u00e4\u010d\u0161ie, '
                'napí\u0161te, \u010do to m\u00e1 robi\u0165.</p>\n'
                + contact_form_html("sk"))
    return ('<h2 id="kontakt" class="section-title">Need something like this built?</h2>\n'
            '<p>These are free because they are small. If you need one for your own '
            'customers, or something bigger, tell us what it has to do.</p>\n'
            + contact_form_html())

def run() -> int:
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    for tool in TOOLS:
        build_tool(tool)
    build_index()
    print(f"[tools_agent] built {len(TOOLS)} free tools + index")
    return len(TOOLS)


if __name__ == "__main__":
    run()
