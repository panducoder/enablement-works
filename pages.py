"""Page templates for enablement.works in The Shift design language: home, guide board, tools, glossary, FAQ, about, privacy, 404."""
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



TOOL_DOCS = [
    {"slug": "enablement-capacity-calculator", "kind": "tool", "path": "/tools/enablement-capacity-calculator/",
     "title": "Enablement capacity calculator: how many enablement people your plan needs", "category": "Capacity and ROI",
     "description": "Enter reps, hires, launches and kickoffs. See the enablement hours your plan needs and the gap against your team.",
     "primary_query": "sales enablement team size calculator", "related_queries": ["enablement to rep ratio"], "minutes": 3, "updated": "2026-11-06"},
    {"slug": "cost-per-active-user-calculator", "kind": "tool", "path": "/tools/cost-per-active-user-calculator/",
     "title": "Cost per active user calculator for enablement tools", "category": "Capacity and ROI",
     "description": "What your LMS, content platform and roleplay tool cost per rep who actually uses them, before renewal.",
     "primary_query": "cost per active user", "related_queries": ["enablement tool usage"], "minutes": 2, "updated": "2026-11-06"},
]

SEAM_CASES = [
    {"id": "kickoff", "label": "Sales kickoff", "before_big": "Day 1.", "before": "A big event. Then nothing for 90 days.",
     "after_big": "Day 90.", "after": "Certified in two weeks. A roleplay per play. A CRO report at day 30, 60 and 90.",
     "notes": ["SKO deck v9 FINAL (2)", "who owns follow-up??", "certification… later"], "tabs": "47 tabs open", "link": "/guides/sales-kickoff-follow-up/"},
    {"id": "onboarding", "label": "Onboarding", "before_big": "Shadow.", "before": "New reps ramp by shadowing whoever has time.",
     "after_big": "Ready.", "after": "Tools, plan and first calls set up before day one. Time to first deal tracked.",
     "notes": ["laptop arrives day 3", "ask Priya, she knows", "quota from week 1?"], "tabs": "12 onboarding docs", "link": "/guides/sales-onboarding-program/"},
    {"id": "renewal", "label": "Tool renewal", "before_big": "Half-used.", "before": "Licences paid for every rep. Used by a few.",
     "after_big": "Used.", "after": "Cost per active user known. Usage doubled before anyone talks about switching tools.",
     "notes": ["300 seats, 120 active", "renewal in 30 days", "nobody filled the LMS"], "tabs": "3 platforms, 0 owners", "link": "/guides/cost-per-active-user/"},
    {"id": "report", "label": "CRO report", "before_big": "94%?", "before": "Completion is up. The CRO asks what changed.",
     "after_big": "4 levels.", "after": "Activity, practice, behavior and outcome, on one page, every month.",
     "notes": ["completion 94%!!", "logins up 12%", "is anyone selling differently?"], "tabs": "dashboard_final.xlsx", "link": "/guides/sales-enablement-metrics/"},
]

METRICS = [
    ("Enablement-to-rep ratio", "Is the team sized for the plan?", "quota-carrying reps ÷ enablement FTEs", "1 : 25–50", "/guides/sales-enablement-team-size/"),
    ("Cost per active user", "What each tool really costs.", "annual licence ÷ reps active in last 30 days", "≥ 70% active", "/guides/cost-per-active-user/"),
    ("Coaching coverage", "Do managers make it stick?", "reps coached on a real call or roleplay in 30 days ÷ active reps", "70–85%", "/guides/sales-coaching-coverage/"),
    ("Enablement output per dollar", "Does spend reach the field?", "programs completed, practiced and used ÷ total enablement spend", "per quarter", "/guides/sales-enablement-roi/"),
    ("Four levels of evidence", "What a CRO can fund.", "activity → practice → behavior → outcome, baseline first", "1 page / month", "/guides/sales-enablement-metrics/"),
]

SEAM_JS = r"""
(function(){
  const cases = __CASES__;
  const seam = document.querySelector('.seam'); if(!seam) return;
  const range = seam.querySelector('.seam__range');
  range.addEventListener('input', ()=> seam.style.setProperty('--seam', range.value + '%'));
  const set = id => {
    const c = cases.find(x=>x.id===id); if(!c) return;
    seam.querySelector('[data-k=before_big]').textContent = c.before_big;
    seam.querySelector('[data-k=before]').textContent = c.before;
    seam.querySelector('[data-k=after_big]').textContent = c.after_big;
    seam.querySelector('[data-k=after]').textContent = c.after;
    seam.querySelectorAll('.seam__note').forEach((n,i)=> n.textContent = c.notes[i]||'');
    seam.querySelector('.seam__tabs').textContent = c.tabs;
    const w = document.querySelector('.seam-watch'); if (w) w.href = c.link;
    document.querySelectorAll('.seamcases__pick').forEach(b=> b.setAttribute('aria-pressed', b.dataset.case===id ? 'true':'false'));
  };
  document.querySelectorAll('.seamcases__pick').forEach(b=> b.addEventListener('click', ()=> set(b.dataset.case)));
})();
"""


def home_page(c):
    S, esc = c["SITE"], c["esc"]
    k = SEAM_CASES[0]
    picks = "".join(f'<button type="button" class="seamcases__pick" data-case="{x["id"]}" aria-pressed="{"true" if i == 0 else "false"}">{esc(x["label"])}</button>' for i, x in enumerate(SEAM_CASES))
    notes = "".join(f'<span class="seam__note seam__note--{i + 1}">{esc(n)}</span>' for i, n in enumerate(k["notes"]))
    metrics = "".join(f'<li class="metricrow"><span class="shiftrow__rank">{i + 1:02d}</span><div><a class="metricrow__name" href="{u}">{esc(n)}</a><span class="metricrow__why">{esc(w)}</span></div><code class="metricrow__formula">{esc(f)}</code><span class="metricrow__target">{esc(t)}</span></li>'
                      for i, (n, w, f, t, u) in enumerate(METRICS))
    counts = {r: sum(1 for g in c["guides"] if r in c["roles_of"](g)) for r in c["ROLE_NAMES"]}
    role_copy = {"cro": "Fund the plan, read one page a month, and know what changed on calls.",
                 "enablement": "Size the team, pick the programs, prove the impact and protect your hours for strategy.",
                 "manager": "Coach on real calls, reinforce one skill at a time, and keep new reps ramping.",
                 "revops": "Join the LMS to call data and the CRM, and measure tools by active use."}
    seats = "".join(f'<li class="seat"><a class="seat__link" href="/guides/?role={r}"><span class="seat__count">{counts[r]:02d}</span><span class="seat__role">{esc(c["ROLE_NAMES"][r])}</span><span class="seat__copy">{esc(role_copy[r])}</span></a></li>' for r in c["ROLE_NAMES"])
    steps = [("01", "Diagnose", "Three weeks. What your plan needs, what your team can deliver, what your tools return. A 12-month roadmap."),
             ("02", "Build", "Microlearning, AI roleplays, talk tracks, launch kits, onboarding and certification, in your tools and methodology."),
             ("03", "Run", "Launch with your sales leader, nudge reps in Slack or Teams, send managers who has not started, escalate."),
             ("04", "Report", "One page to your CRO each month: activity, practice, behavior and outcomes.")]
    step_tiles = "".join(f'<li class="seat"><div class="seat__link"><span class="seat__count">{n}</span><span class="seat__role">{t}</span><span class="seat__copy">{esc(x)}</span></div></li>' for n, t, x in steps)
    featured = [c["by_slug"][s] for s in c["FEATURED"] if s in c["by_slug"]]
    faqs = "".join(f'<details class="faq__item"{" open" if i == 0 else ""}><summary>{esc(f["q"])}</summary><p class="faq__a">{esc(f["a"])}</p></details>' for i, f in enumerate(HOME_FAQS))
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
    <div class="hero__grid">
      <h1 class="hero__title" id="hero-h">Your enablement strategy, <span class="after">built and run.</span></h1>
      <div>
        <p class="hero__lede">Enablement Works is the production and operations engine for sales enablement teams. Your team sets the strategy. We build the content, roleplays and programs in your tools, run them, drive completion and report the results to your CRO every month.</p>
        <div class="hero__ctas"><a class="cta-enter" href="#capacity-check">Book a 20-minute Capacity Check <span class="cta-enter__arrow" aria-hidden="true">→</span></a><a class="cta-scroll" href="#seam">Drag the seam yourself</a></div>
        <ul class="tags"><li>B2B teams, 100–1,000 reps</li><li>{len(c['guides'])} free guides</li><li>Free Capacity Check</li></ul>
      </div>
    </div>
    <div class="seamblock" id="seam">
      <div class="seam">
        <div class="seam__before">
          <div class="seam__half"><span class="seam__tag seam__tag--before">Before</span><div><p class="seam__big" data-k="before_big">{esc(k['before_big'])}</p><p class="seam__metric" data-k="before">{esc(k['before'])}</p></div></div>
          <div class="seam__clutter">{notes}<span class="seam__tabs">{esc(k['tabs'])}</span></div>
        </div>
        <div class="seam__after">
          <div class="seam__half seam__half--right"><span class="seam__tag seam__tag--after">After</span><div><p class="seam__big" data-k="after_big">{esc(k['after_big'])}</p><p class="seam__metric" data-k="after">{esc(k['after'])}</p></div></div>
        </div>
        <input class="seam__range" type="range" min="4" max="96" value="50" aria-label="Move the line between before and after">
        <span class="seam__line" aria-hidden="true"></span>
      </div>
      <div class="seamblock__foot"><div class="seamcases" role="group" aria-label="Pick a moment">{picks}</div><a class="btn-block seam-watch" href="{k['link']}">Read how it works</a></div>
    </div>
  </div>
</section>

<section class="sec sec--cobalt" aria-labelledby="metrics-h">
  <div class="wrap">
    <div class="sec__head"><h2 class="sec__title" id="metrics-h">Five numbers to put in front of your CRO.</h2><p class="sec__lede">Each has a formula, a target and a guide that shows how to measure it. The targets are our rules of thumb, and we say so wherever they appear.</p></div>
    <ol class="ledger">{metrics}</ol>
    <a class="cta-banner" href="/tools/enablement-capacity-calculator/">Run your own numbers in the capacity calculator</a>
  </div>
</section>

<section class="sec" id="how" aria-labelledby="how-h">
  <div class="wrap">
    <div class="sec__head"><h2 class="sec__title" id="how-h">The plan grew. The team did not.</h2><div class="sec__lede"><p>Every year the plan asks for more: onboarding, launches, a kickoff, certifications, new talk tracks. A team of one to four people cannot build all of it and also run it. So programs ship late, the kickoff gets no follow-up and the tools sit half-used.</p><p><strong>The problem is not the people. It is the hours.</strong> So we take the hours.</p></div></div>
    <ol class="seats">{step_tiles}</ol>
  </div>
</section>

<section class="sec sec--paper" id="video" aria-labelledby="video-h">
  <div class="wrap share-grid">
    <div>
      <span class="eyebrow">2 min 35 s · captions on</span>
      <h2 class="sec__title" id="video-h">What it looks like from the inside.</h2>
      <ul class="ticklist"><li>Your enablement lead approves every brief.</li><li>A senior reviewer approves every asset before you see it.</li><li>Every month, one page to the CRO.</li></ul>
      <details class="transcript"><summary>Read the transcript</summary><p>{esc(TRANSCRIPT)}</p></details>
    </div>
    <figure class="player" style="margin:0">
      <video controls preload="none" playsinline poster="/media/enablement-works-explainer-poster.png" width="1920" height="1080">
        <source src="/media/enablement-works-explainer.mp4" type="video/mp4">
        <track kind="captions" src="/media/enablement-works-explainer.vtt" srclang="en" label="English" default>
      </video>
      <figcaption class="player__bar"><span>Enablement Works explainer</span><b>02:35</b></figcaption>
    </figure>
  </div>
</section>

<section class="sec" id="offer" aria-labelledby="offer-h">
  <div class="wrap">
    <div class="sec__head"><h2 class="sec__title" id="offer-h">Start with a Diagnostic. Continue with the Engine.</h2><p class="sec__lede">Fixed fees, published prices. A sales kickoff in the next 90 days becomes your first program.</p></div>
    <div class="offer">
      <article class="offer__card"><h3 class="offer__name">Enablement Diagnostic</h3><p class="offer__terms">fixed · three weeks · $35,000 above 500 reps</p><p class="offer__num">$25,000</p><p>Interviews, tool audit, content review, behavior review, capacity model, a 12-month roadmap and a readout to your CRO and head of enablement. The full fee is credited to the Engine if you continue within 30 days.</p></article>
      <article class="offer__card offer__card--cobalt"><h3 class="offer__name">Enablement Engine</h3><p class="offer__terms">12-month subscription · billed each quarter</p>
        <div class="tiers">
          <div><p class="offer__num">$12.5k<small>/ month</small></p><h4>Core</h4><p>Production and program operations in two of your tools, three briefs in production at once, nudges and escalations, platform administration, quality review, a monthly CRO report and a quarterly AI briefing.</p></div>
          <div><p class="offer__num">$22k<small>/ month</small></p><h4>Scale</h4><p>Everything in Core in up to four tools, six briefs at once, manager coaching packs, staggered launches, a quarterly CRO review, behavior measured on recorded calls and a weekly coaching card per rep.</p></div>
        </div>
      </article>
    </div>
    <p class="offer__note">Not sure yet? <a href="/guides/outsourced-sales-enablement/">What to keep in-house and what to hand off</a>.</p>
  </div>
</section>

<section class="sec sec--mist" id="guides" aria-labelledby="seats-h">
  <div class="wrap">
    <div class="sec__head"><h2 class="sec__title" id="seats-h">Start where you sit.</h2><p class="sec__lede">{len(c['guides'])} guides, each with a short answer up top, a worked example and its sources. Filter them by role, topic or format.</p></div>
    <ol class="seats">{seats}</ol>
  </div>
</section>

<section class="sec sec--cobalt" aria-labelledby="popular-h">
  <div class="wrap">
    <div class="sec__head"><h2 class="sec__title" id="popular-h">The questions we get asked most.</h2><p class="sec__lede">Straight answers, with the formula, the threshold and the limits.</p></div>
    <ol class="ledger">{"".join(c["row"](d, i + 1) for i, d in enumerate(featured))}</ol>
    <a class="cta-banner" href="/guides/">Open the full guide board</a>
  </div>
</section>

<section class="sec" id="faq" aria-labelledby="faq-h">
  <div class="wrap" style="max-width:980px">
    <h2 class="sec__title" id="faq-h" style="margin-bottom:28px">Questions CROs and enablement leaders ask us.</h2>
    <div class="faq">{faqs}</div>
  </div>
</section>

<section class="sec sec--cobalt" id="capacity-check" aria-labelledby="cta-h">
  <div class="wrap">
    <div class="sec__head"><h2 class="sec__title" id="cta-h">How much enablement work does your plan need?</h2>
    <div><p class="sec__lede" style="margin-bottom:24px">The Capacity Check takes 20 minutes with your CRO and head of enablement. You get a scored summary and a capacity estimate the next day. Free, and yours to keep. Email us your rep count and a few times that suit you.</p>
    <a class="btn-block" href="{MAILTO}">Book a 20-minute Capacity Check</a>
    <p class="sec__lede" style="margin-top:22px;font-size:15px">Or write to <a href="mailto:{S['email']}">{S['email']}</a>. Want the numbers first? Try the <a href="/tools/enablement-capacity-calculator/">capacity calculator</a>.</p></div></div>
  </div>
</section>
<script>{SEAM_JS.replace('__CASES__', json.dumps(SEAM_CASES))}</script>"""
    return c["page"]("/", "Enablement Works: sales enablement, built and run", "The production and operations engine for B2B sales enablement teams. You set the strategy; we build, run and report to your CRO. Free guides and calculators.", main, graph, current="/", tone="dark")


# ---------------------------------------------------------------- the board (guides hub)

BOARD_JS = r"""
(function(){
  const rows=[...document.querySelectorAll('.board .shiftrow')], list=document.querySelector('.board .ledger');
  const q=document.getElementById('board-q'), state={topic:'',role:'',format:'',q:'',sort:'rank'};
  const p=new URLSearchParams(location.search); for (const k in state) if (p.get(k)) state[k]=p.get(k); q.value=state.q;
  const match=(r,s)=> (!s.topic||r.dataset.topic===s.topic)&&(!s.role||r.dataset.roles.split(' ').includes(s.role))&&(!s.format||r.dataset.format===s.format)&&(!s.q||r.dataset.hay.includes(s.q.toLowerCase()));
  function render(){
    let shown=rows.filter(r=>match(r,state));
    rows.forEach(r=>r.hidden=!shown.includes(r));
    const key={rank:r=>+r.dataset.rank,newest:r=>-Date.parse(r.dataset.updated)-(+r.dataset.rank)/1000,shortest:r=>+r.dataset.minutes*100+(+r.dataset.rank)}[state.sort];
    rows.slice().sort((a,b)=>key(a)-key(b)).forEach(r=>list.appendChild(r));
    document.querySelectorAll('.chip').forEach(ch=>{
      const f=ch.dataset.facet,v=ch.dataset.value, on=state[f]===v; ch.setAttribute('aria-pressed',on);
      const n=rows.filter(r=>match(r,{...state,[f]:v})).length; ch.querySelector('.chip__n').textContent=n; ch.dataset.empty=n===0;
    });
    document.querySelectorAll('.sorter__opt').forEach(o=>o.setAttribute('aria-pressed',o.dataset.sort===state.sort));
    const mins=shown.reduce((a,r)=>a+(+r.dataset.minutes),0);
    document.getElementById('sum-n').firstChild.textContent=shown.length;
    document.getElementById('sum-min').textContent=mins+' min of reading';
    document.getElementById('board-count').textContent=shown.length+' of '+rows.length+' shown';
    document.getElementById('board-empty').hidden=shown.length>0;
    const act=document.getElementById('sum-active'); act.innerHTML='';
    ['topic','role','format','q'].forEach(f=>{ if(state[f]){ const b=document.createElement('button'); b.className='summary__token'; b.type='button';
      const chip=document.querySelector('.chip[data-facet="'+f+'"][data-value="'+state[f]+'"]'); b.textContent=(chip?chip.dataset.label:'“'+state[f]+'”')+' ×';
      b.onclick=()=>{state[f]=''; if(f==='q') q.value=''; render();}; const li=document.createElement('li'); li.appendChild(b); act.appendChild(li);} });
    const u=new URLSearchParams(); for (const k in state) if(state[k]&&!(k==='sort'&&state[k]==='rank')) u.set(k,state[k]);
    history.replaceState(null,'',location.pathname+(u.toString()?'?'+u:'')+location.hash);
  }
  document.querySelectorAll('.chip').forEach(ch=>ch.addEventListener('click',()=>{const f=ch.dataset.facet; state[f]=state[f]===ch.dataset.value?'':ch.dataset.value; render();}));
  document.querySelectorAll('.sorter__opt').forEach(o=>o.addEventListener('click',()=>{state.sort=o.dataset.sort; render();}));
  q.addEventListener('input',()=>{state.q=q.value.trim(); render();});
  document.getElementById('board-form').addEventListener('submit',e=>{e.preventDefault(); state.q=q.value.trim(); render();});
  document.getElementById('board-reset').addEventListener('click',e=>{e.preventDefault(); state.topic=state.role=state.format=state.q=''; q.value=''; render();});
  document.getElementById('sum-copy').addEventListener('click',e=>{navigator.clipboard&&navigator.clipboard.writeText(location.href).then(()=>{e.target.textContent='Link copied'; setTimeout(()=>e.target.textContent='Copy this view',1600);});});
  render();
})();
"""


def guides_hub(c):
    esc = c["esc"]
    docs = list(c["guides"]) + [d for d in c["by_slug"].values() if d["kind"] == "page"] + TOOL_DOCS
    order = {s: i for i, s in enumerate(c["FEATURED"])}
    cat_i = {k: i for i, k in enumerate(c["CATEGORY_ORDER"])}
    docs.sort(key=lambda d: (order.get(d["slug"], 99), cat_i.get(d.get("category"), 99), d["title"]))
    rows = "".join(c["row"](d, i + 1) for i, d in enumerate(docs))
    topics = [(c["CATEGORY_SLUG"][k], k) for k in c["CATEGORY_ORDER"] if any(d.get("category") == k for d in docs)]
    chip = lambda f, v, label: f'<button type="button" class="chip" data-facet="{f}" data-value="{v}" data-label="{esc(label)}" aria-pressed="false">{esc(label)} <span class="chip__n"></span></button>'
    facets = (f'<fieldset class="facet"><legend class="facet__label">Role</legend><div class="facet__chips">{"".join(chip("role", r, n) for r, n in c["ROLE_NAMES"].items())}</div></fieldset>'
              f'<fieldset class="facet"><legend class="facet__label">Topic</legend><div class="facet__chips">{"".join(chip("topic", v, n) for v, n in topics)}</div></fieldset>'
              f'<fieldset class="facet"><legend class="facet__label">Format</legend><div class="facet__chips">{chip("format", "guide", "Guides")}{chip("format", "reference", "Reference")}{chip("format", "tool", "Calculators")}</div></fieldset>')
    url = c["SITE"]["url"] + "/guides/"
    trail = [("/", "Home"), ("/guides/", "Guides")]
    graph = [{"@type": "CollectionPage", "@id": url, "url": url, "name": "Sales enablement guides", "isPartOf": {"@id": c["WEB_ID"]},
              "mainEntity": {"@type": "ItemList", "numberOfItems": len(docs), "itemListElement": [
                  {"@type": "ListItem", "position": i + 1, "url": c["SITE"]["url"] + d["path"], "name": d["title"]} for i, d in enumerate(docs)]}},
             c["crumbs_node"](trail)]
    total = sum(d["minutes"] for d in docs)
    main = f"""<section class="board" aria-labelledby="board-h">
  <div class="wrap">
    <div class="board__head">
      <div><h1 class="board__title" id="board-h">Every enablement question, <span class="under-coral">answered.</span></h1>
      <p class="board__sub">{len(c['guides'])} guides, a statistics library and two calculators. Each guide opens with a short answer, then the formula, a worked example and its sources. Filter by who you are and what you need.</p></div>
      <form class="board__search" id="board-form" role="search"><label class="board__searchlabel" for="board-q">Search the board</label><input id="board-q" type="search" placeholder="e.g. ramp time, coaching, ROI" autocomplete="off"><button class="board__go" type="submit">Find</button></form>
    </div>
    <div class="board__body">
      <div class="board__main">
        <div class="facets">{facets}</div>
        <div class="board__toolbar"><p class="board__count" id="board-count">{len(docs)} of {len(docs)} shown</p>
          <div class="sorter" role="group" aria-label="Sort"><button type="button" class="sorter__opt" data-sort="rank" aria-pressed="true">Most asked</button><button type="button" class="sorter__opt" data-sort="newest" aria-pressed="false">Newest</button><button type="button" class="sorter__opt" data-sort="shortest" aria-pressed="false">Quickest</button></div></div>
        <ol class="ledger">{rows}</ol>
        <div class="board__empty" id="board-empty" hidden><h2>Nothing matches that mix.</h2><p>Drop a filter, or ask us directly: hello@enablement.works.</p><a href="#" id="board-reset" style="color:#fff;font-weight:800">Reset the board</a></div>
      </div>
      <aside class="summary" aria-live="polite">
        <p class="summary__label">This view</p>
        <p class="summary__big" id="sum-n">{len(docs)}<span id="sum-min">{total} min of reading</span></p>
        <p class="summary__sub">Free. No sign-up. Quote anything with a link.</p>
        <ul class="summary__active" id="sum-active"></ul>
        <p class="summary__hint">Share a filtered view with your team.</p>
        <button type="button" class="ticket" id="sum-copy">Copy this view</button>
      </aside>
    </div>
  </div>
</section>
<script>{BOARD_JS}</script>"""
    return c["page"]("/guides/", "Sales enablement guides by role and topic",
                     "Free sales enablement guides, filterable by role and topic: metrics, team size, ROI, onboarding, coaching, kickoff follow-up, AI roleplay and AI agents.",
                     main, graph, current="/guides/", tone="cobalt")


# ---------------------------------------------------------------- tools

CAPACITY_JS = r"""
(function(){
  const $=id=>document.getElementById(id);
  function calc(){
    const reps=+$('reps').value||0, team=+$('team').value||0, hires=+$('hires').value||0, launches=+$('launches').value||0, skos=+$('skos').value||0;
    const coachH={light:0,standard:6,heavy:12}[$('coach').value];
    const need = hires*14 + launches*120 + skos*400 + reps*(18+coachH);
    const fte = need/1400, gap = fte-team, lo = reps/50, hi = reps/25;
    $('need').textContent = Math.round(need).toLocaleString()+' h';
    $('fte').textContent = fte.toFixed(1);
    $('ratio').textContent = team>0 ? '1:'+Math.round(reps/team) : 'n/a';
    $('band').textContent = lo.toFixed(1)+'–'+hi.toFixed(1);
    $('gap').textContent = (gap>0?'+':'')+gap.toFixed(1);
    const pct = fte>0 ? Math.min(100, team/fte*100) : 100;
    $('cover').style.width = pct+'%'; $('coverlbl').textContent = Math.round(pct)+'% of the hours your plan needs';
    $('verdict').textContent = team===0 ? 'Enter your current enablement headcount to see the gap.'
      : gap>1 ? 'Your plan needs about '+gap.toFixed(1)+' more enablement people than you have. That gap shows up as late programs, kickoffs with no follow-up and half-used tools.'
      : gap>0.25 ? 'You are a little short. Protect the 90 days after each launch and kickoff: that is the work that slips first.'
      : 'Your team size matches the plan on this model. Check that the hours go to programs that reach the field, not to formatting and admin.';
  }
  ['reps','team','hires','launches','skos','coach'].forEach(i=>$(i).addEventListener('input',calc)); calc();
})();
"""

CPAU_JS = r"""
(function(){
  const $=id=>document.getElementById(id), rows=[...document.querySelectorAll('[data-tool]')];
  const money=n=>'$'+Math.round(n).toLocaleString();
  function calc(){
    let total=0, out=[];
    rows.forEach(r=>{
      const cost=+r.querySelector('.cost').value||0, seats=+r.querySelector('.seats').value||0, active=+r.querySelector('.active').value||0;
      const cpau=active>0?cost/active:0, cpl=seats>0?cost/seats:0, use=seats>0?active/seats*100:0;
      r.querySelector('.cpau').textContent=active>0?money(cpau):'n/a'; r.querySelector('.cpl').textContent=seats>0?money(cpl):'n/a';
      r.querySelector('.use').textContent=seats>0?Math.round(use)+'%':'n/a';
      total+=cost; if(seats>0) out.push({name:r.dataset.tool,use,mult:cpl>0?cpau/cpl:0,idle:seats>0?cost*(1-Math.min(1,active/seats)):0});
    });
    $('total').textContent=money(total);
    $('idle').textContent=money(out.reduce((a,o)=>a+o.idle,0));
    const w=out.sort((a,b)=>a.use-b.use)[0];
    $('verdict').textContent = !w ? '' : w.use<40 ? 'Act: your '+w.name+' is used by '+Math.round(w.use)+'% of licensed reps, so each active user costs '+w.mult.toFixed(1)+'x the seat price. Run a 90-day operations plan before renewal: ask what it would take to double active users, not which tool to switch to.'
      : w.use<70 ? 'Watch: your '+w.name+' is at '+Math.round(w.use)+'% active use. Find which teams are inactive and why before the next renewal.'
      : 'Healthy: every tool is above 70% active use. Keep measuring monthly, and count completions, not logins.';
  }
  document.querySelectorAll('.tool input').forEach(i=>i.addEventListener('input',calc)); calc();
})();
"""


def _tool_page(c, path, title, h1, sub, desc, body, howto, faqs, js, app_name):
    url = c["SITE"]["url"] + path
    trail = [("/", "Home"), ("/tools/", "Tools"), (path, app_name)]
    graph = [{"@type": "WebApplication", "@id": url + "#app", "name": app_name, "url": url, "applicationCategory": "BusinessApplication",
              "operatingSystem": "Any (runs in the browser)", "isAccessibleForFree": True, "description": desc,
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": {"@id": c["ORG_ID"]}},
             c["crumbs_node"](trail), c["faq_node"](faqs, url)]
    main = f"""<section class="board" aria-labelledby="tool-h">
  <div class="wrap">
    <div class="board__head"><div><h1 class="board__title" id="tool-h">{h1}</h1><p class="board__sub">{sub}</p></div>
    <p class="board__sub" style="font-family:var(--f-mono);font-size:13px">Runs in your browser. Nothing you type leaves this page.</p></div>
    {body}
    <div class="paper-panel"><div class="body">{howto}</div>{c['faq_html'](faqs, open_first=True)}</div>
    <a class="cta-banner" href="/#capacity-check">Want a second opinion on your numbers? Book a free Capacity Check</a>
  </div>
</section>
<script>{js}</script>"""
    return c["page"](path, title, desc, main, graph, current="/tools/", tone="cobalt", og_image=f"/og/{path.strip('/').split('/')[-1]}.png")


def tools_pages(c):
    cap_body = """<section class="tool" aria-labelledby="calc-h"><h2 id="calc-h" class="sr">Calculator</h2>
<div class="fields">
 <div class="field"><label for="reps">Quota-carrying reps</label><input id="reps" type="number" min="0" value="300" inputmode="numeric"><span class="hint">Everyone with a number, incl. SDRs</span></div>
 <div class="field"><label for="team">Enablement people today</label><input id="team" type="number" min="0" step="0.5" value="3" inputmode="decimal"><span class="hint">Full-time equivalents</span></div>
 <div class="field"><label for="hires">New reps, next 12 months</label><input id="hires" type="number" min="0" value="90" inputmode="numeric"><span class="hint">Hires plus backfills</span></div>
 <div class="field"><label for="launches">Launches a year</label><input id="launches" type="number" min="0" value="6" inputmode="numeric"><span class="hint">Products or new plays</span></div>
 <div class="field"><label for="skos">Kickoffs a year</label><input id="skos" type="number" min="0" value="1" inputmode="numeric"><span class="hint">Includes 90 days of reinforcement</span></div>
 <div class="field"><label for="coach">Coaching support</label><select id="coach"><option value="light">Light: managers coach alone</option><option value="standard" selected>Standard: scorecards and packs</option><option value="heavy">Heavy: weekly call reviews</option></select></div>
</div>
<div class="results" aria-live="polite">
 <div class="result"><span class="k">Hours the plan needs</span><span class="v" id="need">0</span></div>
 <div class="result"><span class="k">People needed</span><span class="v" id="fte">0</span></div>
 <div class="result"><span class="k">Gap vs. your team</span><span class="v coral" id="gap">0</span></div>
 <div class="result"><span class="k">Your ratio today</span><span class="v" id="ratio">0</span></div>
 <div class="result"><span class="k">Rule of thumb (1:25–1:50)</span><span class="v" id="band">0</span></div>
 <div class="result"><span class="k" id="coverlbl">Coverage</span><div class="bar"><i id="cover"></i></div></div>
</div>
<p class="verdict" id="verdict"></p></section>"""
    cap_howto = """<h2 id="how-it-works">How the calculator works</h2>
<p>The calculator adds up the enablement hours your sales plan asks for, then divides by about 1,400 productive hours per enablement person per year. It compares the result with your team and with our rule of thumb of one enablement person for every 25 to 50 quota-carrying reps.</p>
<div class="table-wrap"><table><thead><tr><th>Work in the plan</th><th>Hours assumed</th><th>Why</th></tr></thead><tbody>
<tr><td>Onboarding</td><td>14 h per new rep</td><td>Cohort onboarding shared across hires, plus certification and manager packs</td></tr>
<tr><td>Launch</td><td>120 h per launch</td><td>Brief, assets, certification, roleplay, launch messages and a 30-day check</td></tr>
<tr><td>Sales kickoff</td><td>400 h per kickoff</td><td>The event content and the 90 days of reinforcement after it</td></tr>
<tr><td>Ongoing support</td><td>18 h per rep per year</td><td>Content upkeep, platform administration, completion chasing, reporting</td></tr>
<tr><td>Coaching support</td><td>0, 6 or 12 h per rep per year</td><td>Scorecards, coaching packs or weekly call reviews</td></tr>
</tbody></table></div>
<p>These are planning assumptions from our own work, not industry benchmarks. Change the inputs to match your plan. The point is to put two numbers on one page: the hours the plan needs and the hours the team has. Read the full method in <a href="/guides/sales-enablement-team-size/">How many sales enablement people do you need?</a></p>"""
    cap_faqs = [
        {"q": "What is a good sales enablement to rep ratio?", "a": "Our rule of thumb is one enablement person for every 25 to 50 quota-carrying reps. Move toward 25 when you hire many new reps, launch often or support coaching closely. Move toward 50 when the team is stable and programs are mature."},
        {"q": "How many hours does one enablement person have in a year?", "a": "About 1,400 productive hours, after meetings, admin, holidays and leave. Planning on 2,000 hours is a common reason enablement plans overrun."},
        {"q": "What should I do if the calculator shows a gap?", "a": "Show both numbers to your CRO before the plan is final: the hours the plan needs and the hours the team has. Then cut scope, add headcount, or move production and operations work to a partner so the team keeps the strategy."},
    ]
    rows = "".join(f"""<tr data-tool="{n}"><td data-k="Tool">{n}</td><td data-k="Annual cost $"><input class="cost" type="number" min="0" value="{cost}" aria-label="{n} annual cost"></td><td data-k="Seats"><input class="seats" type="number" min="0" value="{seats}" aria-label="{n} licensed seats"></td><td data-k="Active 30 days"><input class="active" type="number" min="0" value="{act}" aria-label="{n} reps active in last 30 days"></td><td class="out use" data-k="Usage"></td><td class="out cpl" data-k="Per seat"></td><td class="out cpau" data-k="Per active user"></td></tr>"""
                   for n, cost, seats, act in [("LMS", 60000, 300, 210), ("Content platform", 90000, 300, 120), ("Roleplay tool", 45000, 150, 40)])
    cpau_body = f"""<section class="tool" aria-labelledby="calc-h"><h2 id="calc-h" class="sr">Calculator</h2>
<div style="overflow-x:auto"><table class="cpau-table"><thead><tr><th>Tool</th><th>Annual cost ($)</th><th>Licensed seats</th><th>Active, last 30 days</th><th>Usage</th><th>Per seat</th><th>Per active user</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="results" aria-live="polite" style="margin-top:18px"><div class="result"><span class="k">Total annual spend</span><span class="v" id="total">0</span></div><div class="result"><span class="k">Spent on idle seats</span><span class="v coral" id="idle">0</span></div></div>
<p class="verdict" id="verdict"></p></section>"""
    cpau_howto = """<h2 id="formula">The formula</h2>
<p><strong>Cost per active user = annual licence cost ÷ reps who used the tool and completed something in the last 30 days.</strong></p>
<p>Compare it with cost per seat (annual cost ÷ licensed seats). At 40% usage, each active user costs 2.5 times the seat price. Count a rep as active only if they completed something: a module, a roleplay, a certification or a shared asset. Logins alone flatter the number.</p>
<div class="table-wrap"><table><thead><tr><th>Active use</th><th>Cost per active user vs. seat</th><th>Status</th><th>What to do</th></tr></thead><tbody>
<tr><td>70% or more</td><td>Under 1.4x</td><td>Healthy</td><td>Keep measuring monthly</td></tr>
<tr><td>40% to 70%</td><td>1.4x to 2.5x</td><td>Watch</td><td>Find which teams are inactive and why</td></tr>
<tr><td>Under 40%</td><td>Above 2.5x</td><td>Act</td><td>Run a 90-day operations plan before renewal</td></tr>
</tbody></table></div>
<p>Low usage rarely means a bad tool. It usually means nobody had the hours to fill it with current content, launch programs in it and chase completion. The tool was bought; the operations were not. Read more in <a href="/guides/cost-per-active-user/">Cost per active user: the enablement tool metric to check before renewal</a>.</p>"""
    cpau_faqs = [
        {"q": "What is cost per active user for an enablement tool?", "a": "It is the annual licence cost divided by the number of reps who used the tool and completed something in the last 30 days. It shows what you really pay for each rep the tool reaches."},
        {"q": "What counts as an active user?", "a": "A rep who completed something in the last 30 days: a module, a roleplay, a certification or an asset shared with a buyer. A login alone does not count."},
        {"q": "What usage rate should an enablement tool reach?", "a": "As our rule of thumb, 70% or more of licensed reps active each month is healthy for a core tool. Between 40% and 70%, find out which teams are inactive. Below 40%, fix the operations before you renew or switch."},
    ]
    tools = [
        ("/tools/enablement-capacity-calculator/", "Sales enablement team size calculator",
         'How many enablement people does your plan <span class="under-coral">need?</span>', "Enter your reps, hires, launches and kickoffs. See the hours your sales plan needs, the people that takes, and the gap against your team today.",
         "Free calculator: enter reps, hires, launches and kickoffs to see the enablement hours your sales plan needs and how many enablement people that takes.",
         cap_body, cap_howto, cap_faqs, CAPACITY_JS, "Enablement capacity calculator"),
        ("/tools/cost-per-active-user-calculator/", "Cost per active user calculator for enablement tools",
         'What does each active user <span class="under-coral">really</span> cost?', "Enter the annual cost, licensed seats and active reps for each enablement tool. See the real price per rep who uses it, and what idle seats cost you.",
         "Free calculator: find the cost per active user of your LMS, content platform and roleplay tool before renewal. Formula, thresholds and what to do next.",
         cpau_body, cpau_howto, cpau_faqs, CPAU_JS, "Cost per active user calculator"),
    ]
    out = [(path, _tool_page(c, path, title, h1, sub, desc, body, howto, faqs, js, name)) for path, title, h1, sub, desc, body, howto, faqs, js, name in tools]
    trail = [("/", "Home"), ("/tools/", "Tools")]
    hub_main = f"""<section class="board" aria-labelledby="tools-h"><div class="wrap">
<div class="board__head"><div><h1 class="board__title" id="tools-h">Put enablement in <span class="under-coral">numbers.</span></h1><p class="board__sub">Two free calculators that turn enablement into numbers a CRO reads. No sign-up. Nothing you type leaves your browser.</p></div></div>
<ol class="ledger">{"".join(c["row"](d, i + 1) for i, d in enumerate(TOOL_DOCS))}</ol>
<a class="cta-banner" href="/guides/">Read the guides behind the numbers</a></div></section>"""
    out.append(("/tools/", c["page"]("/tools/", "Free sales enablement calculators", "Free sales enablement calculators: enablement team capacity and cost per active user for enablement tools. No sign-up.", hub_main, [c["crumbs_node"](trail)], current="/tools/", tone="cobalt")))
    return out


# ---------------------------------------------------------------- glossary, FAQ

def glossary_page(c):
    esc, S = c["esc"], c["SITE"]
    terms = sorted(c["glossary"], key=lambda g: g["term"].lower())
    index = "".join(f'<a class="tag tag--ink" href="#{esc(g["id"])}">{esc(g["term"])}</a>' for g in terms)
    items = []
    for g in terms:
        rel = "".join(f'<a href="/guides/{s}/">{esc(c["by_slug"][s]["title"].split(":")[0])}</a>' for s in (g.get("related_guides") or []) if s in c["by_slug"])
        more = f'<p class="more">Read: {rel}</p>' if rel else ""
        items.append(f'<section class="gl" id="{esc(g["id"])}"><h2>{esc(g["term"])}</h2><div><p class="short">{c["inline_md"](g.get("short", ""))}</p><p>{c["inline_md"](g.get("long", ""))}</p>{more}</div></section>')
    url = S["url"] + "/glossary/"
    trail = [("/", "Home"), ("/glossary/", "Glossary")]
    graph = [{"@type": "DefinedTermSet", "@id": url, "url": url, "name": "Sales enablement glossary", "publisher": {"@id": c["ORG_ID"]},
              "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": url + "#" + g["id"], "name": g["term"], "description": g.get("short", ""),
                                  "url": url + "#" + g["id"], "inDefinedTermSet": url} for g in terms]}, c["crumbs_node"](trail)]
    main = f"""<article class="case wrap">{c['crumbs_html'](trail)}
<header class="case__head"><h1 class="case__title">Sales enablement glossary.</h1><p class="case__byline"><span>{len(terms)} terms</span><span>one sentence each</span><span>formulas where there is one</span></p></header>
<nav class="gl-index" aria-label="Terms">{index}</nav>{''.join(items)}</article>"""
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
        qs = "".join('<details class="faq__item"><summary>' + esc(f["q"]) + '</summary><p class="faq__a">' + c["inline_md"](f["a"]) + ((' <a href="' + esc(f["link"]) + '">Read the guide →</a>') if f.get("link") else "") + '</p></details>' for f in groups[gname])
        secs.append(f'<h2 class="faq__group">{esc(gname)}</h2><div class="faq">{qs}</div>')
    url = S["url"] + "/faq/"
    trail = [("/", "Home"), ("/faq/", "FAQ")]
    main = f"""<article class="case wrap" style="max-width:1040px">{c['crumbs_html'](trail)}
<header class="case__head"><h1 class="case__title">Sales enablement, answered.</h1><p class="case__byline"><span>{len(c['faqs'])} questions</span><span>direct answers first</span><span>links to the full guide</span></p></header>
{''.join(secs)}</article>"""
    return c["page"]("/faq/", "Sales enablement FAQ: direct answers", f"Sales enablement FAQ: {len(c['faqs'])} direct answers on definitions, team size, budgets, metrics, coaching, onboarding and AI.", main, [c["faq_node"](c["faqs"], url), c["crumbs_node"](trail)], current="/faq/")


# ---------------------------------------------------------------- about, privacy, 404

def about_page(c):
    S = c["SITE"]
    trail = [("/", "Home"), ("/about/", "About")]
    url = S["url"] + "/about/"
    main = f"""<article class="case wrap">{c['crumbs_html'](trail)}
<header class="case__head"><h1 class="case__title">The production and operations engine for enablement.</h1></header>
<div class="case__grid"><div class="case__main"><div class="body">
<p>Enablement Works is the production and operations engine for B2B sales enablement teams. Your team sets the strategy. We build the content, roleplays and programs in your tools, run them, drive completion and report results to your CRO every month.</p>
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
<li>Every outside statistic links to its public source. Numbers we could not verify are left out. Our own rules of thumb are labelled as ours.</li>
<li>Worked examples use made-up, round numbers and say so. We never publish client names, client results or testimonials without written permission.</li>
<li>Guides show the date they were last updated. We review them at least every quarter.</li>
<li>Spotted an error? Email <a href="mailto:{S['email']}?subject=Correction">{S['email']}</a> and we will correct it and note the change.</li>
</ul>
<h2 id="contact">Contact</h2>
<p>Email <a href="mailto:{S['email']}">{S['email']}</a>, or <a href="/#capacity-check">book a free 20-minute Capacity Check</a>.</p>
</div></div>
<aside class="case__side"><section class="move"><h2 class="move__title">In one line</h2><p class="move__text" id="short-answer">Enablement Works builds, runs and reports on sales enablement programs for B2B teams of 100 to 1,000 reps, so the enablement team can spend its hours on strategy.</p><a class="slab" href="/#capacity-check">Book a Capacity Check</a></section></aside></div></article>"""
    graph = [{"@type": "AboutPage", "@id": url, "url": url, "name": "About Enablement Works", "about": {"@id": c["ORG_ID"]}, "isPartOf": {"@id": c["WEB_ID"]}}, c["crumbs_node"](trail)]
    return c["page"]("/about/", "About Enablement Works", "About Enablement Works, the production and operations engine for B2B sales enablement teams, and the editorial standards behind our guides.", main, graph, current="/about/")


def privacy_page(c):
    S = c["SITE"]
    trail = [("/", "Home"), ("/privacy/", "Privacy")]
    main = f"""<article class="case wrap" style="max-width:900px">{c['crumbs_html'](trail)}
<header class="case__head"><h1 class="case__title">Privacy.</h1><p class="case__byline"><span>Last updated 6 Nov 2026</span></p></header>
<div class="body">
<p>This website does not use cookies, analytics, advertising trackers or forms. The calculators run in your browser; nothing you type is sent to us.</p>
<p>The site is hosted on GitHub Pages, which may log visitor IP addresses for security. Fonts load from Google Fonts, which may receive your IP address. See the privacy policies of GitHub and Google for details.</p>
<p>If you email us, we use your message only to reply and to provide the service you ask about. We do not sell or share it. To ask what we hold about you, or to have it deleted, email <a href="mailto:{S['email']}">{S['email']}</a>.</p>
</div></article>"""
    return c["page"]("/privacy/", "Privacy", "Enablement Works privacy notice: no cookies, no analytics, no trackers.", main, [c["crumbs_node"](trail)])


def not_found_page(c):
    main = """<section class="board"><div class="wrap"><h1 class="board__title">Not <span class="under-coral">here.</span></h1><p class="board__sub">The page you asked for has moved or never existed. Try the <a href="/guides/" style="color:#fff">guide board</a>, the <a href="/glossary/" style="color:#fff">glossary</a> or the <a href="/" style="color:#fff">home page</a>.</p></div></section>"""
    return c["page"]("/404.html", "Page not found", "Page not found.", main, [], tone="cobalt")
