"""Page templates for enablement.works: home, hubs, tools, glossary, FAQ, about, privacy, 404."""
import json
import re

TRANSCRIPT = (
    "If you run sales enablement, you know this moment. The sales plan for next year lands, and it asks for more than last year: "
    "more hires, more launches, a kickoff, new talk tracks. Your team did not get bigger. So the work slips. Programs ship late. "
    "The kickoff gets no follow-up. Reps do not finish what you built. The tools you pay for sit half-used. And your CRO sees "
    "completion counts, not results. I started Enablement Works to fix the hours, not the people. We are the production and "
    "operations engine for enablement teams. You set the strategy. We do the work. We build the content, roleplays and programs "
    "your roadmap needs, in your methodology and in the tools you already own: microlearning, AI roleplays, launch kits, "
    "onboarding and certification. Your enablement lead approves every brief. A senior reviewer approves every asset before you "
    "see it. Then we run the programs. We launch with a message from your sales leader, nudge reps, send managers the list of who "
    "has not started, and escalate when completion is low. Every month your CRO gets one page: activity, practice, behavior where "
    "you record calls, and outcomes from your CRM. Your enablement lead presents it. We start with a three-week Diagnostic. It "
    "shows what your plan needs, what your team can deliver and what your tools return, and it ends with a 12-month roadmap and "
    "the first two programs. If you want to know your own numbers first, book a free 20-minute Capacity Check with your CRO and "
    "your head of enablement. You keep the results.")

MAILTO = "mailto:hello@enablement.works?subject=Capacity%20Check&body=Company%3A%20%0AQuota-carrying%20reps%3A%20%0AEnablement%20team%20size%3A%20%0APreferred%20times%3A%20"

HOME_FAQS = [
    {"q": "Are you replacing our enablement team?", "a": "No. Your enablement team sets the strategy, chooses the programs, approves every brief and presents the results to the CRO. We are the production and operations team behind them."},
    {"q": "Which tools do you work in?", "a": "Yours. We work in depth in Mindtickle, Highspot, Seismic, Gong and Second Nature, and in most LMS platforms. We do not resell licenses, and in our first year we take no referral fees from any vendor, so our advice stays neutral."},
    {"q": "Do we need to record sales calls?", "a": "No. If you record calls, we can measure behaviors on real calls. If you do not, we measure with roleplay scores, certifications, manager observations and CRM data."},
    {"q": "How do you decide how much work is included?", "a": "Your contract sets a monthly production volume from a fixed menu of assets, and a limit on how many briefs are in production at once. You see what is used and what is left at any time. Large items, such as a full onboarding program, can also be bought as a fixed-fee project."},
    {"q": "How do you keep the content right for our company?", "a": "We keep your methodology, personas, approved claims and scorecard in one client kit. Every asset is checked against it, approved by a senior reviewer, and then reviewed by your named approver in two consolidated rounds. Nothing goes live without your approval."},
    {"q": "How much of our time does it take?", "a": "In the first 30 days: about 3 to 4 hours of the CRO's time and 2 to 3 hours a week from the head of enablement. Managers and reps give 30 to 45 minutes each for interviews. After that, a 30-minute work review every one or two weeks and a 15-minute CRO report each month."},
    {"q": "How do you handle our data and AI?", "a": "We use AI models through enterprise agreements with zero data retention, and your data is never used to train a model. We sign a data protection agreement and share our sub-processor list. Sales behavior scores are for coaching only and are never used in performance reviews. You own all content and data and can export it at any time."},
    {"q": "What are the contract terms?", "a": "The Diagnostic is a fixed fee, 50% at signature. The Engine is a 12-month term billed each quarter in advance, with 90 days' notice to cancel after the first quarter. You can pause once a year for up to two months."},
]


def home_page(c):
    S, esc = c["SITE"], c["esc"]
    featured = [c["by_slug"][s] for s in c["FEATURED"] if s in c["by_slug"]]
    rest = [g for g in c["guides"] if g["slug"] not in c["FEATURED"]]
    cards = "".join(c["card"](d) for d in (featured + rest)[:9])
    faqs = "".join(f'<div class="qa"><h3>{esc(f["q"])}</h3><p>{esc(f["a"])}</p></div>' for f in HOME_FAQS)
    url = S["url"] + "/"
    service = {
        "@type": "ProfessionalService", "@id": S["url"] + "/#service", "name": "Enablement Works", "url": url,
        "description": S["description"], "email": S["email"], "areaServed": "Worldwide", "parentOrganization": {"@id": c["ORG_ID"]},
        "serviceType": ["Sales enablement services", "Outsourced sales enablement", "Sales enablement operations", "Sales training content production"],
        "audience": {"@type": "BusinessAudience", "audienceType": "B2B sales organizations with 100 to 1,000 reps"},
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Enablement Works offers", "itemListElement": [
            {"@type": "Offer", "name": "Capacity Check", "price": "0", "priceCurrency": "USD", "description": "A free 20-minute session with your CRO and head of enablement. You get a scored summary and a capacity estimate the next day."},
            {"@type": "Offer", "name": "Enablement Diagnostic", "price": "25000", "priceCurrency": "USD", "description": "Three weeks, fixed fee ($35,000 above 500 reps). Interviews, tool audit, content and behavior review, capacity model, 12-month roadmap and a readout to the CRO."},
            {"@type": "Offer", "name": "Enablement Engine: Core", "priceSpecification": {"@type": "UnitPriceSpecification", "price": "12500", "priceCurrency": "USD", "unitText": "MONTH"}, "description": "Production and program operations in two of your tools, three briefs in production at once, nudges, escalations, platform administration, quality review and a monthly CRO report."},
            {"@type": "Offer", "name": "Enablement Engine: Scale", "priceSpecification": {"@type": "UnitPriceSpecification", "price": "22000", "priceCurrency": "USD", "unitText": "MONTH"}, "description": "Everything in Core in up to four tools, six briefs at once, manager coaching packs, staggered launches, behavior measured on recorded calls and a weekly coaching card per rep."},
        ]}}
    video = {"@type": "VideoObject", "@id": S["url"] + "/#explainer", "name": "Enablement Works in two and a half minutes",
             "description": "How Enablement Works builds and runs sales enablement programs for B2B sales teams: diagnose, build, run and report.",
             "thumbnailUrl": S["url"] + "/media/enablement-works-explainer-poster.png", "uploadDate": "2026-10-06",
             "duration": "PT2M35S", "contentUrl": S["url"] + "/media/enablement-works-explainer.mp4", "transcript": TRANSCRIPT,
             "publisher": {"@id": c["ORG_ID"]}}
    graph = [service, video, c["faq_node"](HOME_FAQS, url),
             {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": "Enablement Works: your enablement strategy, built and run",
              "isPartOf": {"@id": c["WEB_ID"]}, "about": {"@id": c["ORG_ID"]}, "primaryImageOfPage": S["url"] + "/og/default.png"}]
    main = f"""<section class="hero" aria-labelledby="hero-h">
    <div class="wrap">
      <h1 id="hero-h">Your enablement strategy, built and run.</h1>
      <div>
        <p class="lede">Enablement Works is the production and operations engine for sales enablement teams. Your team sets the strategy. We build the content, roleplays and programs in your tools, run them, drive completion and report the results to your CRO every month.</p>
        <a class="btn" href="#capacity-check">Book a 20-minute Capacity Check</a>
        <p class="under">For B2B sales teams of 100 to 1,000 reps. Free. With your CRO and head of enablement together.</p>
      </div>
      <aside class="split" aria-labelledby="split-h">
        <h2 id="split-h">Who does what</h2>
        <dl>
          <div class="row"><dt>Your team</dt><dd>Sets the strategy, chooses the programs, approves every brief and presents the results to the CRO.</dd></div>
          <div class="row"><dt>Enablement Works</dt><dd>Builds the content, roleplays and programs in your tools, runs them, drives completion and reports the results every month.</dd></div>
        </dl>
      </aside>
    </div>
  </section>

  <section class="sec" aria-labelledby="problem-h">
    <div class="wrap">
      <p class="margin"><span>01</span>The problem</p>
      <div>
        <h2 id="problem-h">The sales plan grew. The enablement team did not.</h2>
        <div class="prose">
          <p>Every year the plan asks for more: onboarding for new hires, launch training, a kickoff, certifications, new talk tracks. A team of one to four people cannot build all of it and also run it. Our rule of thumb is one enablement person for every 25 to 50 quota-carrying reps. <a href="/tools/enablement-capacity-calculator/">Check your own ratio</a>.</p>
          <p>So the work slips. Programs ship late. The kickoff gets no follow-up. Reps do not finish what was built. The platforms you pay for sit half-used. And the CRO sees activity counts, not results.</p>
        </div>
        <p class="pull">The problem is not the people. It is the hours.</p>
      </div>
    </div>
  </section>

  <section class="sec" id="how" aria-labelledby="how-h">
    <div class="wrap">
      <p class="margin"><span>02</span>How it works</p>
      <div>
        <h2 id="how-h">Diagnose, build, then run and report.</h2>
        <ol class="steps">
          <li class="step"><span class="step-n" aria-hidden="true">1</span><h3>Diagnose</h3><p>In three weeks we measure what your sales plan needs from enablement, what your team can deliver, what your tools return and which sales behaviors are missing. You get a 12-month roadmap with the first two programs defined.</p></li>
          <li class="step"><span class="step-n" aria-hidden="true">2</span><h3>Build</h3><p>We produce what your roadmap needs, in your methodology and in the tools you already own: microlearning, AI roleplays, talk tracks, battlecards, launch kits, onboarding and certification programs. Your enablement lead approves every brief. A senior reviewer approves every asset before you see it.</p></li>
          <li class="step"><span class="step-n" aria-hidden="true">3</span><h3>Run and report</h3><p>We launch each program with a message from your sales leader, nudge reps in Slack or Teams, send managers the list of reps who have not started, and escalate when completion is low. Each month your CRO gets one page: <a href="/guides/sales-enablement-metrics/">activity, practice, behavior and outcomes</a>.</p></li>
        </ol>
      </div>
    </div>
  </section>

  <section class="sec" id="video" aria-labelledby="video-h">
    <div class="wrap">
      <p class="margin"><span>03</span>In two minutes</p>
      <div>
        <h2 id="video-h">What it looks like from the inside.</h2>
        <figure class="video">
          <video controls preload="none" playsinline poster="/media/enablement-works-explainer-poster.png" width="1920" height="1080">
            <source src="/media/enablement-works-explainer.mp4" type="video/mp4">
            <track kind="captions" src="/media/enablement-works-explainer.vtt" srclang="en" label="English" default>
          </video>
          <figcaption>Enablement Works explainer, 2 min 35 s, captions on. <details><summary>Read the transcript</summary><p>{esc(TRANSCRIPT)}</p></details></figcaption>
        </figure>
      </div>
    </div>
  </section>

  <section class="sec" id="offer" aria-labelledby="offer-h">
    <div class="wrap">
      <p class="margin"><span>04</span>The offer</p>
      <div>
        <h2 id="offer-h">Start with a Diagnostic. Continue with the Engine.</h2>
        <div class="offer">
          <article class="plan" aria-labelledby="diag-h">
            <div class="plan-head"><h3 id="diag-h">Enablement Diagnostic</h3></div>
            <div class="two">
              <div><p class="figure">$25,000</p><p class="figure-sub">fixed · three weeks<br><span style="color:var(--muted)">$35,000 above 500 reps</span></p></div>
              <p>Interviews, tool audit, content review, behavior review, capacity model, a 12-month roadmap and a readout to your CRO and head of enablement. The full fee is credited to the Engine if you continue within 30 days.</p>
            </div>
          </article>
          <article class="plan" aria-labelledby="eng-h">
            <div class="plan-head"><h3 id="eng-h">Enablement Engine</h3><span class="terms">12-month subscription, billed each quarter</span></div>
            <table class="tiers"><caption class="sr">Engine plans</caption><tbody>
              <tr><th scope="row"><span class="tier">Core</span></th><td class="num">$12,500<span class="per">a month</span></td><td>Production and program operations in two of your tools, three briefs in production at once, nudges and escalations, platform administration, quality review, a monthly CRO report and a quarterly AI briefing.</td></tr>
              <tr><th scope="row"><span class="tier">Scale</span></th><td class="num">$22,000<span class="per">a month</span></td><td>Everything in Core in up to four tools, six briefs in production at once, plus manager coaching packs, staggered launches across teams, a quarterly CRO review, behavior measured on recorded calls, and a weekly coaching card per rep for managers.</td></tr>
            </tbody></table>
            <p class="note">A sales kickoff in the next 90 days becomes your first program. <a href="/guides/sales-kickoff-follow-up/">What the 90 days after a kickoff need</a>.</p>
          </article>
        </div>
      </div>
    </div>
  </section>

  <section class="sec" id="guides" aria-labelledby="guides-h">
    <div class="wrap">
      <p class="margin"><span>05</span>Guides</p>
      <div>
        <h2 id="guides-h">Straight answers to the questions enablement leaders ask.</h2>
        <div class="cards">{cards}</div>
        <p style="margin-top:28px"><a class="btn btn-ghost" href="/guides/">All {len(c['guides'])} guides</a></p>
      </div>
    </div>
  </section>

  <section class="sec" id="faq" aria-labelledby="faq-h">
    <div class="wrap">
      <p class="margin"><span>06</span>Questions</p>
      <div>
        <h2 id="faq-h">Questions CROs and enablement leaders ask us</h2>
        <div class="faq">{faqs}</div>
      </div>
    </div>
  </section>

  <section class="cta" id="capacity-check" aria-labelledby="cta-h">
    <div class="wrap">
      <h2 id="cta-h">Find out how much enablement work your plan needs, and how much your team can deliver.</h2>
      <p>The Capacity Check takes 20 minutes with your CRO and head of enablement. You get a scored summary and a capacity estimate the next day. Free, and yours to keep. Email us with your rep count and a few times that suit you.</p>
      <a class="btn" href="{MAILTO}">Book a 20-minute Capacity Check</a>
      <p class="under" style="margin-top:16px">Or email <a href="mailto:{S['email']}">{S['email']}</a>. Want to run the numbers first? Try the <a href="/tools/enablement-capacity-calculator/">capacity calculator</a>.</p>
    </div>
  </section>"""
    return c["page"]("/", "Enablement Works: sales enablement, built and run", S["description"], main, graph, current="/")


def guides_hub(c):
    esc = c["esc"]
    groups = []
    for cat in c["CATEGORY_ORDER"]:
        items = [g for g in c["guides"] if g.get("category") == cat]
        if items:
            groups.append(f'<section class="sec" id="{c["CATEGORY_SLUG"][cat]}" aria-labelledby="h-{c["CATEGORY_SLUG"][cat]}"><div class="wrap"><p class="margin"><span>{len(items):02d}</span>guides</p><div><h2 id="h-{c["CATEGORY_SLUG"][cat]}">{esc(cat)}</h2><div class="cards">{"".join(c["card"](d) for d in items)}</div></div></div></section>')
    others = [g for g in c["guides"] if g.get("category") not in c["CATEGORY_ORDER"]]
    if others:
        groups.append(f'<section class="sec"><div class="wrap"><p class="margin">More</p><div><div class="cards">{"".join(c["card"](d) for d in others)}</div></div></div></section>')
    url = c["SITE"]["url"] + "/guides/"
    trail = [("/", "Home"), ("/guides/", "Guides")]
    graph = [{"@type": "CollectionPage", "@id": url, "url": url, "name": "Sales enablement guides", "isPartOf": {"@id": c["WEB_ID"]},
              "mainEntity": {"@type": "ItemList", "numberOfItems": len(c["guides"]), "itemListElement": [
                  {"@type": "ListItem", "position": i + 1, "url": c["SITE"]["url"] + g["path"], "name": g["title"]} for i, g in enumerate(c["guides"])]}},
             c["crumbs_node"](trail)]
    main = f"""<header class="page-head"><div class="wrap">{c['crumbs_html'](trail)}
<h1>Sales enablement guides</h1>
<p class="sub">Practical, sourced answers on enablement metrics, team size, ROI, onboarding, coaching, kickoffs, AI roleplay, AI agents and buying groups. Each guide opens with a short answer you can use today.</p></div></header>
{''.join(groups)}"""
    return c["page"]("/guides/", "Sales enablement guides", "Practical, sourced guides on sales enablement: metrics, team size, ROI, onboarding, coaching, kickoff follow-up, AI roleplay and AI agents.", main, graph, current="/guides/")


# ---------------------------------------------------------------- tools

CAPACITY_JS = r"""
(function(){
  const $=id=>document.getElementById(id);
  const ids=['reps','team','hires','launches','skos','coach'];
  function calc(){
    const reps=+$('reps').value||0, team=+$('team').value||0, hires=+$('hires').value||0,
          launches=+$('launches').value||0, skos=+$('skos').value||0, coach=$('coach').value;
    // Hours model (rule of thumb, see the guide): onboarding 40 h per new hire cohort-adjusted,
    // 120 h per launch, 400 h per kickoff incl. 90-day reinforcement, ongoing 18 h per rep per year,
    // coaching support 0 / 6 / 12 h per rep per year.
    const coachH={light:0,standard:6,heavy:12}[coach];
    const need = hires*14 + launches*120 + skos*400 + reps*(18+coachH);
    const fte = need/1400; // ~1,400 productive hours per enablement person per year
    const gap = fte-team;
    const lo = reps/50, hi = reps/25;
    $('need').textContent = Math.round(need).toLocaleString()+' h';
    $('fte').textContent = fte.toFixed(1);
    $('ratio').textContent = team>0 ? '1 : '+Math.round(reps/team) : 'n/a';
    $('band').textContent = lo.toFixed(1)+' to '+hi.toFixed(1);
    $('gap').textContent = (gap>0?'+':'')+gap.toFixed(1);
    const pct = fte>0 ? Math.min(100, team/fte*100) : 100;
    $('cover').style.width = pct+'%';
    $('coverlbl').textContent = Math.round(pct)+'% of the hours your plan needs';
    let v;
    if (team===0) v='Enter your current enablement headcount to see the gap.';
    else if (gap>1) v='Your plan needs about '+gap.toFixed(1)+' more enablement people than you have. That gap shows up as late programs, kickoffs with no follow-up and half-used tools.';
    else if (gap>0.25) v='You are a little short. Protect the 90 days after each launch and kickoff: that is the work that slips first.';
    else v='Your team size matches the plan on this model. Check that the hours go to programs that reach the field, not to formatting and admin.';
    $('verdict').textContent=v;
  }
  ids.forEach(i=>$(i).addEventListener('input',calc)); calc();
})();
"""

CPAU_JS = r"""
(function(){
  const $=id=>document.getElementById(id);
  const rows=[...document.querySelectorAll('[data-tool]')];
  function money(n){return '$'+Math.round(n).toLocaleString();}
  function calc(){
    let totalCost=0, out=[];
    rows.forEach(r=>{
      const cost=+r.querySelector('.cost').value||0, seats=+r.querySelector('.seats').value||0, active=+r.querySelector('.active').value||0;
      const cpau = active>0 ? cost/active : 0, cpl = seats>0 ? cost/seats : 0, use = seats>0 ? active/seats*100 : 0;
      r.querySelector('.cpau').textContent = active>0 ? money(cpau) : 'n/a';
      r.querySelector('.cpl').textContent = seats>0 ? money(cpl) : 'n/a';
      r.querySelector('.use').textContent = seats>0 ? Math.round(use)+'%' : 'n/a';
      totalCost+=cost; if(seats>0) out.push({name:r.dataset.tool, use, mult: cpl>0?cpau/cpl:0});
    });
    $('total').textContent=money(totalCost);
    const worst = out.sort((a,b)=>a.use-b.use)[0];
    $('verdict').textContent = worst ? (worst.use<50 ? 'Your '+worst.name+' is used by '+Math.round(worst.use)+'% of licensed reps, so each active user costs '+worst.mult.toFixed(1)+'x the list price per seat. Before renewal, ask what it would take to double active users, not which tool to switch to.' : 'Usage looks healthy. Keep measuring active users monthly, and check what they complete, not only that they logged in.') : '';
  }
  document.querySelectorAll('input').forEach(i=>i.addEventListener('input',calc)); calc();
})();
"""


def _tool_page(c, path, title, h1, sub, desc, body, howto, faqs, js, app_name):
    esc = c["esc"]
    url = c["SITE"]["url"] + path
    trail = [("/", "Home"), ("/tools/", "Tools"), (path, app_name)]
    graph = [{"@type": "WebApplication", "@id": url + "#app", "name": app_name, "url": url, "applicationCategory": "BusinessApplication",
              "operatingSystem": "Any (runs in the browser)", "isAccessibleForFree": True, "description": desc,
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": {"@id": c["ORG_ID"]}},
             c["crumbs_node"](trail), c["faq_node"](faqs, url)]
    main = f"""<header class="page-head"><div class="wrap">{c['crumbs_html'](trail)}<h1>{esc(h1)}</h1><p class="sub">{sub}</p></div></header>
<div class="wrap"><div class="article"><article class="article-main">
{body}
<div class="body">{howto}</div>
{c['faq_html'](faqs)}
<aside class="inline-cta"><p>Want a second opinion on your numbers? The Capacity Check takes 20 minutes with your CRO and head of enablement, and it is free.</p><a class="btn" href="/#capacity-check">Book a Capacity Check</a></aside>
</article><aside class="aside"><div class="box"><p><strong>Read next</strong></p><p><a href="/guides/sales-enablement-team-size/">How many enablement people do you need?</a></p><p><a href="/guides/cost-per-active-user/">Cost per active user</a></p><p><a href="/guides/sales-enablement-roi/">Sales enablement ROI</a></p></div></aside></div></div>
<script>{js}</script>"""
    return c["page"](path, title, desc, main, graph, current="/tools/")


def tools_pages(c):
    esc = c["esc"]
    cap_body = """<section class="tool" aria-labelledby="calc-h"><h2 id="calc-h" class="sr">Calculator</h2>
<div class="fields">
 <div class="field"><label for="reps">Quota-carrying reps</label><input id="reps" type="number" min="0" value="300" inputmode="numeric"><span class="hint">Everyone with a number, incl. SDRs</span></div>
 <div class="field"><label for="team">Enablement people today</label><input id="team" type="number" min="0" step="0.5" value="3" inputmode="decimal"><span class="hint">Full-time equivalents</span></div>
 <div class="field"><label for="hires">New reps next 12 months</label><input id="hires" type="number" min="0" value="90" inputmode="numeric"><span class="hint">Hires plus backfills</span></div>
 <div class="field"><label for="launches">Product or play launches a year</label><input id="launches" type="number" min="0" value="6" inputmode="numeric"></div>
 <div class="field"><label for="skos">Kickoffs a year</label><input id="skos" type="number" min="0" value="1" inputmode="numeric"><span class="hint">Includes 90 days of reinforcement</span></div>
 <div class="field"><label for="coach">Coaching support</label><select id="coach"><option value="light">Light: managers coach alone</option><option value="standard" selected>Standard: scorecards and packs</option><option value="heavy">Heavy: call reviews each week</option></select></div>
</div>
<div class="results" aria-live="polite">
 <div class="result"><span class="k">Enablement hours the plan needs</span><span class="v" id="need">0</span></div>
 <div class="result"><span class="k">People needed (1,400 h each)</span><span class="v" id="fte">0</span></div>
 <div class="result"><span class="k">Gap vs. your team</span><span class="v" id="gap">0</span></div>
 <div class="result"><span class="k">Your ratio today</span><span class="v" id="ratio">0</span></div>
 <div class="result"><span class="k">Rule-of-thumb range (1:25 to 1:50)</span><span class="v" id="band">0</span></div>
 <div class="result"><span class="k" id="coverlbl">Coverage</span><div class="bar"><i id="cover"></i></div></div>
</div>
<p class="verdict" id="verdict"></p></section>"""
    cap_howto = """<h2 id="how-it-works">How the calculator works</h2>
<p>The calculator adds up the enablement hours your sales plan asks for, then divides by about 1,400 productive hours per enablement person per year. It compares the result with your team and with our rule of thumb of one enablement person for every 25 to 50 quota-carrying reps.</p>
<div class="table-wrap"><table><thead><tr><th>Work in the plan</th><th>Hours assumed</th><th>Why</th></tr></thead><tbody>
<tr><td>Onboarding</td><td>14 h per new rep</td><td>Cohort onboarding shared across hires, plus certification and manager packs</td></tr>
<tr><td>Product or play launch</td><td>120 h per launch</td><td>Brief, assets, certification, roleplay, launch messages and a 30-day check</td></tr>
<tr><td>Sales kickoff</td><td>400 h per kickoff</td><td>The event content and the 90 days of reinforcement after it</td></tr>
<tr><td>Ongoing support</td><td>18 h per rep per year</td><td>Content upkeep, platform administration, completion chasing, reporting</td></tr>
<tr><td>Coaching support</td><td>0, 6 or 12 h per rep per year</td><td>Scorecards, coaching packs or weekly call reviews</td></tr>
</tbody></table></div>
<p>These are planning assumptions from our own work, not industry benchmarks. Change the inputs to match your plan. The point is to put two numbers on one page: the hours the plan needs and the hours the team has. Read the full method in <a href="/guides/sales-enablement-team-size/">How many sales enablement people do you need?</a></p>"""
    cap_faqs = [
        {"q": "What is a good sales enablement to rep ratio?", "a": "Our rule of thumb is one enablement person for every 25 to 50 quota-carrying reps. Move toward 25 when you hire many new reps, launch often or support coaching closely. Move toward 50 when the team is stable and programs are mature."},
        {"q": "How many hours does one enablement person have in a year?", "a": "About 1,400 productive hours, after meetings, admin, holidays and leave. Planning on 2,000 hours is the most common reason enablement plans overrun."},
        {"q": "What should I do if the calculator shows a gap?", "a": "Show both numbers to your CRO before the plan is final: the hours the plan needs and the hours the team has. Then either cut scope, add headcount, or move production and operations work to a partner so the team keeps the strategy."},
    ]
    cpau_rows = "".join(f"""<tr data-tool="{n}"><td>{n}</td><td><input class="cost" type="number" min="0" value="{cost}" aria-label="{n} annual cost"></td><td><input class="seats" type="number" min="0" value="{seats}" aria-label="{n} licensed seats"></td><td><input class="active" type="number" min="0" value="{act}" aria-label="{n} reps active in last 30 days"></td><td class="use">0</td><td class="cpl">0</td><td class="cpau">0</td></tr>""" for n, cost, seats, act in [("LMS", 60000, 300, 210), ("Content platform", 90000, 300, 120), ("Roleplay tool", 45000, 150, 40)])
    cpau_body = f"""<section class="tool" aria-labelledby="calc-h"><h2 id="calc-h" class="sr">Calculator</h2>
<div class="body"><div class="table-wrap"><table class="cpau-table"><thead><tr><th>Tool</th><th>Annual cost ($)</th><th>Licensed seats</th><th>Active in last 30 days</th><th>Usage</th><th>Cost per seat</th><th>Cost per active user</th></tr></thead><tbody>{cpau_rows}</tbody></table></div></div>
<div class="results" aria-live="polite"><div class="result"><span class="k">Total annual spend</span><span class="v" id="total">0</span></div></div>
<p class="verdict" id="verdict"></p></section>
<style>.cpau-table input{{width:7.5em;font:500 15px var(--f-data);padding:6px 8px;border:1px solid var(--line);background:var(--bg);color:var(--ink)}}</style>"""
    cpau_howto = """<h2 id="formula">The formula</h2>
<p><strong>Cost per active user = annual licence cost ÷ number of reps who used the tool and completed something in the last 30 days.</strong></p>
<p>Compare it with cost per seat (annual cost ÷ licensed seats). When usage is 40%, each active user costs 2.5 times the seat price. Count a rep as active only if they completed something: a module, a roleplay, a certification or a shared asset. Logins alone flatter the number.</p>
<h2 id="what-it-tells-you">What the number tells you</h2>
<p>Low usage rarely means a bad tool. It usually means nobody had the hours to fill the tool with current content, build programs in it, launch them properly and chase completion. The tool was bought; the operations were not. Before your next renewal, ask what it would take to double active users, not which tool to switch to. Read more in <a href="/guides/cost-per-active-user/">Cost per active user: the enablement tool metric to check before renewal</a>.</p>"""
    cpau_faqs = [
        {"q": "What is cost per active user for an enablement tool?", "a": "It is the annual licence cost divided by the number of reps who used the tool and completed something in the last 30 days. It shows what you really pay for each rep the tool reaches."},
        {"q": "What counts as an active user?", "a": "A rep who completed something in the last 30 days: a module, a roleplay, a certification or an asset shared with a buyer. A login alone does not count."},
        {"q": "What usage rate should an enablement tool reach?", "a": "As our rule of thumb, aim for at least 60% of licensed reps active each month for a core tool such as an LMS or content platform. Below 40%, fix the operations before you renew or switch."},
    ]
    tools = [
        ("/tools/enablement-capacity-calculator/", "Sales enablement capacity calculator: how many enablement people do you need?",
         "Enablement capacity calculator", "Enter your reps, hires, launches and kickoffs. See the enablement hours your sales plan needs, the people that takes, and the gap against your team today.",
         "Free calculator: enter reps, hires, launches and kickoffs to see the enablement hours your sales plan needs and how many enablement people that takes.",
         cap_body, cap_howto, cap_faqs, CAPACITY_JS, "Enablement capacity calculator"),
        ("/tools/cost-per-active-user-calculator/", "Cost per active user calculator for sales enablement tools",
         "Cost per active user calculator", "Enter the annual cost, licensed seats and active reps for each enablement tool. See what each active user really costs before your next renewal.",
         "Free calculator: find the cost per active user of your LMS, content platform and roleplay tool before renewal. Formula, thresholds and what to do next.",
         cpau_body, cpau_howto, cpau_faqs, CPAU_JS, "Cost per active user calculator"),
    ]
    out = []
    for path, title, h1, sub, desc, body, howto, faqs, js, name in tools:
        out.append((path, _tool_page(c, path, title, h1, sub, desc, body, howto, faqs, js, name)))
    trail = [("/", "Home"), ("/tools/", "Tools")]
    hub_main = f"""<header class="page-head"><div class="wrap">{c['crumbs_html'](trail)}<h1>Free sales enablement tools</h1><p class="sub">Two calculators that put enablement in numbers a CRO reads. No sign-up. Nothing you type leaves your browser.</p></div></header>
<section class="sec"><div class="wrap"><p class="margin"><span>02</span>tools</p><div class="cards">
<article class="card"><span class="cat">Capacity</span><h3><a href="/tools/enablement-capacity-calculator/">Enablement capacity calculator</a></h3><p>How many enablement people your sales plan needs, and the gap against your team today.</p></article>
<article class="card"><span class="cat">Tools and ROI</span><h3><a href="/tools/cost-per-active-user-calculator/">Cost per active user calculator</a></h3><p>What your LMS, content platform and roleplay tool cost per rep who actually uses them.</p></article>
</div></div></section>"""
    out.append(("/tools/", c["page"]("/tools/", "Free sales enablement calculators", "Free sales enablement calculators: enablement team capacity and cost per active user for enablement tools. No sign-up.", hub_main, [c["crumbs_node"](trail)], current="/tools/")))
    return out


# ---------------------------------------------------------------- glossary, FAQ

def glossary_page(c):
    esc, S = c["esc"], c["SITE"]
    terms = sorted(c["glossary"], key=lambda g: g["term"].lower())
    index = "".join(f'<a href="#{esc(g["id"])}">{esc(g["term"])}</a>' for g in terms)
    items = []
    for g in terms:
        rel = "".join(f' <a href="/guides/{s}/">{esc(c["by_slug"][s]["title"].split(":")[0])}</a>' for s in (g.get("related_guides") or []) if s in c["by_slug"])
        items.append(f'<section class="gl" id="{esc(g["id"])}"><h2>{esc(g["term"])}</h2><p class="short">{c["inline_md"](g.get("short", ""))}</p><p>{c["inline_md"](g.get("long", ""))}</p>{f"<p class=more>Read:{rel}</p>" if rel else ""}</section>')
    url = S["url"] + "/glossary/"
    trail = [("/", "Home"), ("/glossary/", "Glossary")]
    graph = [{"@type": "DefinedTermSet", "@id": url, "url": url, "name": "Sales enablement glossary", "publisher": {"@id": c["ORG_ID"]},
              "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": url + "#" + g["id"], "name": g["term"], "description": g.get("short", ""),
                                  "url": url + "#" + g["id"], "inDefinedTermSet": url} for g in terms]}, c["crumbs_node"](trail)]
    main = f"""<header class="page-head"><div class="wrap">{c['crumbs_html'](trail)}<h1>Sales enablement glossary</h1><p class="sub">{len(terms)} terms enablement leaders, sales managers and RevOps use, defined in one sentence each, with the formula where there is one.</p></div></header>
<div class="wrap"><div class="article"><article class="article-main"><nav class="terms-index" aria-label="Terms">{index}</nav>{''.join(items)}</article><aside class="aside"><div class="box"><p><strong>Start here</strong></p><p><a href="/guides/what-is-sales-enablement/">What is sales enablement?</a></p><p><a href="/guides/sales-enablement-metrics/">Sales enablement metrics</a></p></div></aside></div></div>"""
    return c["page"]("/glossary/", "Sales enablement glossary: key terms defined", f"Sales enablement glossary: {len(terms)} terms defined in plain English, from coaching coverage and cost per active user to ramp time, MCP and skill sprints.", main, graph, current="/glossary/")


def faq_page(c):
    esc, S = c["esc"], c["SITE"]
    groups = {}
    for f in c["faqs"]:
        groups.setdefault(f.get("group", "Basics"), []).append(f)
    order = ["Basics", "Team and budget", "Measurement", "Programs and coaching", "AI", "Working with a partner"]
    secs = []
    for gname in order + [g for g in groups if g not in order]:
        if gname not in groups:
            continue
        qs = "".join('<div class="qa"><h3>' + esc(f["q"]) + '</h3><p>' + c["inline_md"](f["a"]) + ((' <a href="' + esc(f["link"]) + '">Read more</a>') if f.get("link") else "") + '</p></div>' for f in groups[gname])
        secs.append(f'<section class="faqs"><h2>{esc(gname)}</h2>{qs}</section>')
    url = S["url"] + "/faq/"
    trail = [("/", "Home"), ("/faq/", "FAQ")]
    main = f"""<header class="page-head"><div class="wrap">{c['crumbs_html'](trail)}<h1>Sales enablement FAQ</h1><p class="sub">Direct answers to the questions people ask most about sales enablement: what it is, how big the team should be, how to measure it, and where AI fits.</p></div></header>
<div class="wrap"><div class="article"><article class="article-main">{''.join(secs)}</article><aside class="aside"><div class="box"><p><strong>Tools</strong></p><p><a href="/tools/enablement-capacity-calculator/">Capacity calculator</a></p><p><a href="/tools/cost-per-active-user-calculator/">Cost per active user</a></p></div></aside></div></div>"""
    return c["page"]("/faq/", "Sales enablement FAQ: direct answers", f"Sales enablement FAQ: {len(c['faqs'])} direct answers on definitions, team size, budgets, metrics, coaching, onboarding and AI.", main, [c["faq_node"](c["faqs"], url), c["crumbs_node"](trail)], current="/faq/")


# ---------------------------------------------------------------- about, privacy, 404

def about_page(c):
    S = c["SITE"]
    trail = [("/", "Home"), ("/about/", "About")]
    url = S["url"] + "/about/"
    main = f"""<header class="page-head"><div class="wrap">{c['crumbs_html'](trail)}<h1>About Enablement Works</h1><p class="sub">Enablement Works is the production and operations engine for B2B sales enablement teams. Your team sets the strategy. We build the content, roleplays and programs in your tools, run them, drive completion and report results to your CRO every month.</p></div></header>
<div class="wrap"><div class="article"><article class="article-main"><div class="body">
<h2 id="what-we-do">What we do</h2>
<p>We work with B2B sales organizations of 100 to 1,000 reps whose enablement team is too small for the plan. We start with a three-week Enablement Diagnostic and continue with the Enablement Engine, a 12-month subscription for production and program operations. We work in the tools you already own and in your methodology. We do not resell licences.</p>
<h2 id="what-we-believe">What we believe</h2>
<ul>
<li><strong>Strategy is the scarce part.</strong> Enablement leaders should spend their hours on judgment: which behaviors matter, which programs come first. Production and operations can be done by others, to their standard.</li>
<li><strong>The asset is the cheap part.</strong> AI made content cheap. Launching it, driving completion, getting managers to reinforce it and showing the CRO what changed are the expensive parts.</li>
<li><strong>Report evidence, not activity.</strong> Activity, practice, behavior and outcomes, on one page, every month.</li>
</ul>
<h2 id="editorial-standards">Editorial standards for our guides</h2>
<ul>
<li>Every guide opens with a short, direct answer, then shows the method, a worked example and the limits.</li>
<li>Every external statistic links to its public source. Numbers we could not verify are left out. Our own rules of thumb are labelled as ours.</li>
<li>Worked examples use made-up, round numbers and say so. We never publish client names, client results or testimonials without written permission.</li>
<li>Guides show the date they were last updated. We review them at least every quarter.</li>
<li>Spotted an error? Email <a href="mailto:{S['email']}?subject=Correction">{S['email']}</a> and we will correct it and note the change.</li>
</ul>
<h2 id="contact">Contact</h2>
<p>Email <a href="mailto:{S['email']}">{S['email']}</a>, or <a href="/#capacity-check">book a free 20-minute Capacity Check</a>.</p>
</div></article><aside class="aside"><div class="box"><p><strong>Popular guides</strong></p><p><a href="/guides/what-is-sales-enablement/">What is sales enablement?</a></p><p><a href="/guides/outsourced-sales-enablement/">Outsourced sales enablement</a></p></div></aside></div></div>"""
    graph = [{"@type": "AboutPage", "@id": url, "url": url, "name": "About Enablement Works", "about": {"@id": c["ORG_ID"]}, "isPartOf": {"@id": c["WEB_ID"]}}, c["crumbs_node"](trail)]
    return c["page"]("/about/", "About Enablement Works", "About Enablement Works, the production and operations engine for B2B sales enablement teams, and the editorial standards behind our guides.", main, graph, current="/about/")


def privacy_page(c):
    S = c["SITE"]
    trail = [("/", "Home"), ("/privacy/", "Privacy")]
    main = f"""<header class="page-head"><div class="wrap">{c['crumbs_html'](trail)}<h1>Privacy</h1><p class="sub">Last updated 6 November 2026.</p></div></header>
<div class="wrap"><div class="article"><article class="article-main"><div class="body">
<p>This website does not use cookies, analytics, advertising trackers or forms. The calculators run in your browser; nothing you type is sent to us.</p>
<p>The site is hosted on GitHub Pages, which may log visitor IP addresses for security. Fonts load from Google Fonts, which may receive your IP address. See the privacy policies of GitHub and Google for details.</p>
<p>If you email us, we use your message only to reply and to provide the service you ask about. We do not sell or share it. To ask what we hold about you, or to have it deleted, email <a href="mailto:{S['email']}">{S['email']}</a>.</p>
</div></article></div></div>"""
    return c["page"]("/privacy/", "Privacy", "Enablement Works privacy notice: no cookies, no analytics, no trackers.", main, [c["crumbs_node"](trail)])


def not_found_page(c):
    main = """<header class="page-head"><div class="wrap"><h1>Page not found</h1><p class="sub">The page you asked for is not here. Try the <a href="/guides/">guides</a>, the <a href="/glossary/">glossary</a> or the <a href="/">home page</a>.</p></div></header>"""
    return c["page"]("/404.html", "Page not found", "Page not found.", main, [])
