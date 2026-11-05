#!/usr/bin/env python3
"""Build The Shift (https://enablement.works/shift/) as static files into static/shift/.

Run from the repo root:  python3 shift-src/build_shift.py && python3 build.py
build.py then copies static/ -> docs/. Never write into docs/ directly (it is wiped).

Inputs (all in shift-src/):
  catalog.json   the workflows (sample content until real videos replace them)
  shift.css      page styles, scoped to .shiftsite, loaded after /assets/site.css
  shift.js       progressive enhancement (scroll film, divider, board filters, copy/share)
Media (scroll film, sample clips, share cards) lives directly in static/shift/film|media|og
and is left alone by this script.
Uses build.py's page() so header, footer, fonts and the organisation graph match the site.
No cookies, analytics or trackers: the site's privacy page promises none.
"""
import html
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import build as B  # noqa: E402

OUT = ROOT / "static" / "shift"
BASE = "/shift"
URL = B.SITE["url"] + BASE
VERSION = "1"
esc = lambda s: html.escape(str(s), quote=True)  # noqa: E731

FACETS = [
    ("role", "Role", ["Sales Rep", "Frontline Manager", "Enablement", "Sales Leader"]),
    ("motion", "Motion", ["Prospecting", "Discovery", "Proposal & Close", "Forecasting", "Coaching", "Onboarding", "Competitive"]),
    ("stack", "Stack", ["Claude", "Glean", "Salesforce", "Gong", "Slack", "Higgsfield", "ElevenLabs"]),
    ("outcome", "Outcome", ["Time saved", "Win rate", "Ramp time", "Coaching coverage"]),
]
CHAPTERS = [(0, "The problem"), (1.6, "The move"), (3.4, "The result")]
ROLE_COPY = {
    "Sales Rep": "Research, follow-ups and close plans that used to eat the afternoon.",
    "Frontline Manager": "Deal reviews and coaching on every call, not the lucky three.",
    "Enablement": "Launch training, onboarding and battlecards that keep themselves current.",
    "Sales Leader": "Forecast notes and win-loss themes without the weekend spreadsheet.",
}
FAQ = [
    ("What is The Shift?", "The Shift is a library of short films that show AI workflows for B2B sales teams. Every film comes with the exact prompt, the tools it runs on, and the before and after it produced."),
    ("Who is it for?", "Sales reps who want a faster way to prepare, front-line managers who coach, enablement teams who build programmes, and sales leaders who need proof before they scale a new habit."),
    ("Can I use the prompts?", "Yes. Every video page has a Steal this prompt button. The highlighted parts are placeholders for your own account, persona or files."),
    ("Are the numbers real?", "Not yet. This is a sample library: the workflows, clips and before and after figures are illustrative until real team videos are added."),
    ("How do shared links look?", "Each video has its own share card with the before and after on it. Slack, Teams and LinkedIn show it when a link is pasted, and there is embed code for learning platforms."),
]
SAMPLE_NOTE = "Sample library. Workflows, clips and figures are illustrative until real team videos are added."


def slug(v):
    return v.lower().replace("&", "and").replace(" ", "-")


def mult(v):
    m = v["multiplier"]
    return f"{int(m) if float(m).is_integer() else m}×"


def hours(h):
    return "0" if h <= 0 else (str(round(h)) if h >= 10 else f"{h:.1f}".rstrip("0").rstrip("."))


def vurl(v):
    return f"{BASE}/v/{v['slug']}/"


def poster(v):
    return f"{BASE}/media/{v['clip']}-poster.jpg"


def clip(v):
    return f"{BASE}/media/{v['clip']}.mp4"


def head_extra(more=""):
    return (f'<link rel="stylesheet" href="{BASE}/shift.css?v={VERSION}">\n'
            f'<script src="{BASE}/shift.js?v={VERSION}" defer></script>\n'
            f'<meta name="twitter:image" content="{{img}}">\n{more}')


def impact(v):
    after = max(1 / max(v["multiplier"], 1), 0.035) if v["direction"] == "down" else 1
    before = 1 if v["direction"] == "down" else max(1 / max(v["multiplier"], 1), 0.06)
    return (f'<div class="impact" aria-label="{esc(v["beforeText"])} to {esc(v["afterText"])}">'
            f'<div class="impact__labels"><span>{esc(v["beforeLabel"])}</span><span aria-hidden="true">→</span><b>{esc(v["afterLabel"])}</b></div>'
            f'<div class="impact__track"><span class="impact__before" style="width:{before*100:.1f}%"></span>'
            f'<span class="impact__after" style="width:{after*100:.1f}%"></span></div></div>')


def chips(items):
    return '<ul class="chips">' + "".join(f"<li>{esc(s)}</li>" for s in items) + "</ul>"


def srow(v, rank):
    hay = " ".join([v["title"], v["problem"], v["value"], v["prompt"], v["motion"], v["outcome"]] + v["roles"] + v["stack"]).lower()
    tags = "".join(f'<span class="stag stag--role">{esc(r)}</span>' for r in v["roles"]) + f'<span class="stag stag--motion">{esc(v["motion"])}</span>'
    return (f'<li class="srow" data-role="{" ".join(slug(r) for r in v["roles"])}" data-motion="{slug(v["motion"])}" '
            f'data-stack="{" ".join(slug(s) for s in v["stack"])}" data-outcome="{slug(v["outcome"])}" data-hours="{v["hrsWeek"]}" '
            f'data-mult="{v["multiplier"]}" data-published="{v["published"]}" data-hay="{esc(hay)}">'
            f'<span class="srow__rank">{rank:02d}</span>'
            f'<a class="srow__thumb" href="{vurl(v)}" tabindex="-1" aria-hidden="true"><img src="{poster(v)}" alt="" loading="lazy" width="1280" height="720"></a>'
            f'<div class="srow__main"><a class="srow__title" href="{vurl(v)}">{esc(v["title"])}</a><div class="srow__tags">{tags}</div></div>'
            f'{chips(v["stack"])}{impact(v)}<span class="srow__x">{mult(v)}</span></li>')


def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": B.SITE["url"] + p} for i, (p, n) in enumerate(items)]}


def finish(doc, img):
    return doc.replace("{img}", B.SITE["url"] + img)


# ------------------------------------------------------------------ pages

def landing(vs):
    ranked = sorted(vs, key=lambda v: -v["multiplier"])
    cases = ([v for v in vs if v["featured"]] + [v for v in vs if not v["featured"]])[:4]
    total = sum(v["hrsWeek"] for v in vs)
    chapters = [
        ("Before", "From busywork to better selling.", "The Shift is a library of short films about AI workflows that sales teams can copy. Each one ships with the prompt, the stack, and the before and after.", "left",
         '<ul class="film__tags"><li>12 sample workflows</li><li>Prompts included</li></ul>'
         f'<div class="film__actions"><a class="film-cta" href="{BASE}/board/">See the biggest shifts <span aria-hidden="true">→</span></a></div>'),
        ("The wave", "Forty-seven tabs before every call.", "Research, recaps, deal prep and forecast notes eat the hours sellers should spend with buyers. That clutter is the before.", "right", ""),
        ("The move", "One prompt changes the shape of the week.", "Every film shows the exact prompt, the tools behind it and the minutes it gave back, so nobody has to guess how it was done.", "left", ""),
        ("After", "Proof you can copy.", "Watch it, steal the prompt, and send it to your team. The link unfurls with the before and after already on it.", "right",
         '<div class="film__actions"><a class="film-jump" href="#seam">Drag the seam yourself</a></div>'),
    ]
    arts = "".join(
        f'<article class="film__chapter" data-align="{al}" id="ch-{i+1}"><div class="film__copy">'
        f'{"<h1" if i == 0 else "<h2"} class="film__title">{esc(t)}{"</h1>" if i == 0 else "</h2>"}'
        f'<p class="film__body">{esc(b)}</p>{extra}</div></article>'
        for i, (lab, t, b, al, extra) in enumerate(chapters))
    cur = ' aria-current="step"'
    route = "".join(f'<button type="button"{cur if i == 0 else ""}>{esc(c[0])}</button>' for i, c in enumerate(chapters))
    film = f"""<section class="film" data-film aria-label="The Shift, a scroll film">
  <div class="film__stage">
    <picture><source media="(max-width: 860px)" srcset="{BASE}/film/film-mobile-poster.jpg"><img class="film__poster" src="{BASE}/film/film-poster.jpg" alt="" fetchpriority="high"></picture>
    <video class="film__video" muted playsinline preload="none" aria-hidden="true" data-src="{BASE}/film/film.mp4" data-src-mobile="{BASE}/film/film-mobile.mp4"></video>
    <div class="film__shade"></div>
    <div class="film__progress" aria-hidden="true"><span></span></div>
    <nav class="film__route" aria-label="Film chapters">{route}</nav>
  </div>
  <div class="film__story">{arts}</div>
</section>"""
    c0 = cases[0]
    seam_json = json.dumps([{"before": v["beforeText"], "after": v["afterText"], "href": vurl(v)} for v in cases]).replace("</", "<\\/")
    picks = "".join(f'<button type="button" aria-pressed="{"true" if i == 0 else "false"}">{esc(v["title"])}</button>' for i, v in enumerate(cases))
    seam = f"""<section class="ss ss--night" id="seam" aria-labelledby="seam-title">
  <div class="ss__head"><h2 class="ss__title" id="seam-title">Drag the seam. Watch the week change.</h2>
  <p class="ss__lede">Every workflow in the library is framed the same way: what it cost before, what it costs now. Pick one and pull the divider.</p></div>
  <div class="seamblock">
    <div class="seam" data-seam>
      <div class="seam__before">
        <div class="seam__half"><span class="seam__tag seam__tag--before">Before</span><p class="seam__metric" data-before>{esc(c0["beforeText"])}</p><p class="seam__big">From<br>busywork</p></div>
        <div class="seam__clutter" aria-hidden="true"><span class="seam__note seam__note--1">Company priorities?</span><span class="seam__note seam__note--2">Recent news?</span><span class="seam__note seam__note--3">Who signs?</span><span class="seam__note seam__note--4">Right message?</span><span class="seam__tabs">47 tabs open</span></div>
      </div>
      <div class="seam__after"><div class="seam__half seam__half--right"><span class="seam__tag seam__tag--after">After</span><p class="seam__metric" data-after>{esc(c0["afterText"])}</p><p class="seam__big">to better<br>selling.</p></div></div>
      <input class="seam__range" id="seam-range" type="range" min="0" max="100" value="50" aria-label="Move the divider between before and after">
      <div class="seam__line" aria-hidden="true"></div>
    </div>
    <div class="seamblock__foot"><div class="seamcases" role="group" aria-label="Choose a workflow">{picks}</div>
    <a class="seamwatch" href="{vurl(c0)}">Watch this shift <span aria-hidden="true">→</span></a></div>
  </div>
  <script type="application/json" id="seam-cases">{seam_json}</script>
</section>"""
    ledger = f"""<section class="ss ss--cobalt" aria-labelledby="ledger-title">
  <div class="ss__head"><h2 class="ss__title" id="ledger-title">The biggest shifts in the library</h2>
  <p class="ss__stat"><b>{hours(total)}</b> hours a week, per seller, across the time-saving workflows (sample figures)</p></div>
  <ol class="ledger">{"".join(srow(v, i + 1) for i, v in enumerate(ranked[:5]))}</ol>
  <a class="ledger-cta" href="{BASE}/board/">Open the full impact board</a>
</section>"""
    seats = "".join(
        f'<li><a class="seat" href="{BASE}/board/?role={slug(r)}"><span class="seat__count">{sum(1 for v in vs if r in v["roles"])}</span>'
        f'<span class="seat__role">{esc(r)}</span><span class="seat__copy">{esc(ROLE_COPY[r])}</span></a></li>' for r in FACETS[0][2])
    seats = f"""<section class="ss ss--white" aria-labelledby="seats-title"><div class="ss__head"><h2 class="ss__title" id="seats-title">Start from your seat</h2></div><ul class="seats">{seats}</ul></section>"""
    sample = next(v for v in vs if v["slug"] == "deal-review-prep")
    share = f"""<section class="ss ss--paper" id="share" aria-labelledby="share-title"><div class="sharesec">
  <div><h2 class="ss__title" id="share-title" style="margin-bottom:18px">Every win travels with its proof</h2>
  <p>Each video gets its own share card, built from its before and after. Paste a link in Slack or Teams and it unfurls with the card. Post it on LinkedIn and the numbers do the talking.</p>
  <ul><li><b>Slack, Teams, intranets.</b> Rich unfurl with the share card and the video.</li><li><b>LinkedIn and X.</b> Large share card, plus a downloadable clip for native posts.</li><li><b>Learning platforms.</b> Embed code and oEmbed for any page that accepts them.</li><li><b>One moment.</b> Timestamped links that open a video at the exact second.</li></ul></div>
  <figure><img src="{BASE}/og/{sample["slug"]}.png" alt="Share card: {esc(sample["title"])}, {esc(sample["beforeText"])} to {esc(sample["afterText"])}" width="1200" height="630" loading="lazy"><figcaption>The share card for “{esc(sample["title"])}”, generated from its before and after.</figcaption></figure>
</div></section>"""
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in FAQ)
    faq = f"""<section class="ss ss--white" aria-labelledby="faq-title"><div class="ss__head"><h2 class="ss__title" id="faq-title" style="font-size:clamp(30px,3.6vw,48px)">Questions sellers ask first</h2></div><div class="sfaq">{faq}</div>
  <p class="snote" style="margin-top:28px">{SAMPLE_NOTE} Want workflows like these running in your team? <a href="/#capacity-check">Book a Capacity Check</a>.</p></section>"""
    graph = [
        {"@type": "CollectionPage", "@id": URL + "/#page", "url": URL + "/", "name": "The Shift", "isPartOf": {"@id": B.WEB_ID},
         "publisher": {"@id": B.ORG_ID}, "description": "AI sales workflows on film, each with the prompt, the stack and the before and after."},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        crumbs([("/", "Home"), (BASE + "/", "The Shift")]),
    ]
    doc = B.page(BASE + "/", "The Shift: AI sales workflows on film, prompts included",
                 "Short films of AI workflows for B2B sales teams. Each comes with the prompt, the stack and the before and after, plus a filterable impact board.",
                 f'<div class="shiftsite">{film}{seam}{ledger}{seats}{share}{faq}</div>', graph,
                 og_image=BASE + "/og/home.png", tone="dark", extra_head=head_extra())
    return finish(doc, BASE + "/og/home.png")


def board_page(vs):
    ranked = sorted(vs, key=lambda v: -v["multiplier"])
    facets_json = json.dumps([{"key": k, "label": lab, "values": [[slug(x), x] for x in vals]} for k, lab, vals in FACETS]).replace("</", "<\\/")
    fs = ""
    for k, lab, vals in FACETS:
        cs = "".join(
            f'<a class="fchip" href="{BASE}/board/?{k}={slug(x)}" data-facet="{k}" data-value="{slug(x)}" aria-pressed="false">{esc(x)}'
            f'<small>{sum(1 for v in vs if x in (v["roles"] if k == "role" else v["stack"] if k == "stack" else [v[k]]))}</small></a>' for x in vals)
        fs += f'<fieldset class="facet"><legend>{lab}</legend><div class="facet__chips">{cs}</div></fieldset>'
    sorts = "".join(f'<a href="{BASE}/board/{"" if s == "shift" else "?sort=" + s}" data-sort="{s}" aria-pressed="{"true" if s == "shift" else "false"}">{lab}</a>'
                    for s, lab in [("shift", "Biggest shift"), ("hours", "Most hours back"), ("newest", "Newest")])
    total = sum(v["hrsWeek"] for v in vs)
    main = f"""<div class="shiftsite"><div class="board" data-board data-base="{BASE}/board/">
  <div class="board__head">
    <p class="board__crumb"><a href="{BASE}/">The Shift</a> / Impact board</p>
    <h1 class="board__title">Biggest <span>shifts</span>, ranked</h1>
    <form class="board__search" method="get" action="{BASE}/board/" role="search">
      <label for="board-q">Search prompts, tools and problems</label>
      <input id="board-q" name="q" type="search" placeholder="Try “forecast” or “Gong”">
      <button type="submit">Search</button>
    </form>
  </div>
  <div class="board__body">
    <div class="board__main">
      <div class="facets">{fs}</div>
      <div class="board__toolbar"><p class="board__count" role="status">{len(vs)} workflows</p><div class="sorter" role="group" aria-label="Sort by">{sorts}</div></div>
      <ol class="ledger">{"".join(srow(v, i + 1) for i, v in enumerate(ranked))}</ol>
      <div class="board__empty" hidden><h2>No workflow matches that mix yet.</h2><p>Remove a filter or try a broader word. New films are added as teams share them.</p><a href="{BASE}/board/">Clear every filter</a></div>
    </div>
    <aside class="ssum" aria-label="Summary of this view">
      <p class="ssum__label">This view</p>
      <p class="ssum__big" data-sum-hours>{hours(total)}<span> hrs / week</span></p>
      <p class="ssum__sub">back per seller across <span data-count>{len(vs)}</span> workflows</p>
      <ul class="ssum__active"></ul>
      <p class="ssum__hint">No filters yet. Every combination you pick becomes a link you can share.</p>
      <button type="button" class="ssum__copy">Copy this view</button>
      <p class="snote">{SAMPLE_NOTE}</p>
    </aside>
  </div>
  <script type="application/json" id="board-facets">{facets_json}</script>
</div></div>"""
    graph = [crumbs([("/", "Home"), (BASE + "/", "The Shift"), (BASE + "/board/", "Impact board")]),
             {"@type": "ItemList", "name": "AI sales workflows ranked by the size of the shift", "itemListElement": [
                 {"@type": "ListItem", "position": i + 1, "url": B.SITE["url"] + vurl(v), "name": v["title"]} for i, v in enumerate(ranked)]}]
    doc = B.page(BASE + "/board/", "Impact board: AI sales workflows ranked",
                 "Filter AI sales workflows by role, sales motion, stack and outcome, ranked by how much each one changes the week. Every view is a shareable link.",
                 main, graph, og_image=BASE + "/og/board.png", tone="cobalt", extra_head=head_extra())
    return finish(doc, BASE + "/og/board.png")


def prompt_html(p):
    out, i = [], 0
    while i < len(p):
        j = p.find("{", i)
        if j < 0:
            out.append(esc(p[i:])); break
        k = p.find("}", j)
        out.append(esc(p[i:j])); out.append(f"<mark>{esc(p[j:k + 1])}</mark>"); i = k + 1
    return "".join(out)


def related_of(v, vs):
    def score(o):
        return (2 if o["motion"] == v["motion"] else 0) + len(set(o["roles"]) & set(v["roles"])) + 0.5 * len(set(o["stack"]) & set(v["stack"]))
    return sorted([o for o in vs if o["slug"] != v["slug"]], key=lambda o: -score(o))[:3]


def video_page(v, vs):
    url = B.SITE["url"] + vurl(v)
    desc = f'{v["beforeText"]} became {v["afterText"]}. {v["value"]}'[:200]
    embed_src = f'{B.SITE["url"]}{BASE}/embed/{v["slug"]}/'
    embed_code = (f'<iframe src="{embed_src}" width="640" height="360" style="border:0;aspect-ratio:16/9;width:100%;height:auto" '
                  f'allow="fullscreen; picture-in-picture" title="{esc(v["title"])}"></iframe>')
    post = f'{v["beforeText"]} became {v["afterText"]}. {v["title"]}, prompt included:'
    from urllib.parse import quote
    chap = "".join(f'<li><button type="button" data-at="{at}"><i>0:0{int(at)}</i>{esc(lab)}</button></li>' for at, lab in CHAPTERS)
    rel = "".join(f'<li><a href="{vurl(o)}"><img src="{poster(o)}" alt="" loading="lazy" width="1280" height="720"><span>{esc(o["title"])}</span>{impact(o)}</a></li>' for o in related_of(v, vs))
    main = f"""<div class="shiftsite"><div class="case">
  <nav class="case__crumbs" aria-label="Breadcrumb"><a href="{BASE}/">The Shift</a><span aria-hidden="true">/</span><a href="{BASE}/board/">Impact board</a><span aria-hidden="true">/</span><a href="{BASE}/board/?motion={slug(v["motion"])}">{esc(v["motion"])}</a></nav>
  <header class="case__head">
    <div class="case__metric" aria-label="Before {esc(v["beforeText"])}, after {esc(v["afterText"])}">
      <div class="case__side-b"><span class="case__tag case__tag--b">Before</span><span class="case__num">{esc(v["beforeLabel"])}</span></div>
      <span class="case__arrow" aria-hidden="true">→</span>
      <div class="case__side-a"><span class="case__tag case__tag--a">After</span><span class="case__num case__num--a">{esc(v["afterLabel"])}</span></div>
      <span class="case__x">{mult(v)}</span>
    </div>
    <h1 class="case__title">{esc(v["title"])}</h1>
  </header>
  <div class="case__grid">
    <div class="case__media">
      <div class="player" data-player data-url="{url}">
        <video src="{clip(v)}" poster="{poster(v)}" controls playsinline preload="metadata" width="1280" height="720"></video>
        <div class="player__bar"><ol class="chapters" aria-label="Chapters">{chap}</ol><button type="button" class="moment">Share this moment at 0:00</button></div>
      </div>
      <div class="facts">
        <section><h2>The problem</h2><p>{esc(v["problem"])}</p><p class="then">{esc(v["beforeText"])}.</p></section>
        <section><h2>The value</h2><p>{esc(v["value"])}</p><p class="now">{esc(v["afterText"])}.</p></section>
      </div>
    </div>
    <div class="case__side">
      <section class="move" aria-labelledby="move-title"><h2 id="move-title">The move</h2><pre>{prompt_html(v["prompt"])}</pre>
      <p>Fill the highlighted parts with your own account, persona or files.</p><button type="button" class="steal">Steal this prompt</button></section>
      <section class="stackbox" aria-labelledby="stack-title"><h2 class="case__h" id="stack-title">The stack</h2>{chips(v["stack"])}</section>
      <dl class="specs"><div><dt>Who it is for</dt><dd>{esc(", ".join(v["roles"]))}</dd></div><div><dt>Outcome</dt><dd>{esc(v["outcome"])}</dd></div>
      <div><dt>Level</dt><dd>{esc(v["level"])}</dd></div><div><dt>Time to build</dt><dd>{esc(v["buildTime"])}</dd></div><div><dt>Shared by</dt><dd>{esc(v["team"])}</dd></div></dl>
      <p class="snote">{SAMPLE_NOTE}</p>
    </div>
  </div>
  <section class="sharebox" data-share data-url="{url}" aria-labelledby="share-title">
    <h2 id="share-title">Share this shift</h2>
    <div class="sharebox__row">
      <button type="button" class="is-primary" data-copy-link>Copy link</button>
      <a href="https://www.linkedin.com/sharing/share-offsite/?url={quote(url, safe='')}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
      <a href="https://x.com/intent/post?text={quote(post, safe='')}&amp;url={quote(url, safe='')}" target="_blank" rel="noopener noreferrer">X</a>
      <a href="mailto:?subject={quote(v["title"], safe='')}&amp;body={quote(post + chr(10) + chr(10) + url, safe='')}">Email</a>
      <button type="button" data-embed-toggle aria-expanded="false" aria-controls="embed-box">Embed</button>
      <a href="{clip(v)}" download="{v["slug"]}.mp4">Download clip</a>
    </div>
    <p class="sharebox__status" role="status"></p>
    <div class="sharebox__embed" id="embed-box" hidden><label for="embed-text">Paste into an LMS, intranet page or enablement platform</label>
    <textarea id="embed-text" readonly rows="3">{esc(embed_code)}</textarea><button type="button">Copy embed code</button></div>
    <p class="sharebox__note">Slack, Teams and most intranets unfurl this link with the share card. LinkedIn shows the share card; for a playing video in the feed, download the clip and post it natively.</p>
  </section>
  <section class="related" aria-labelledby="related-title"><h2 id="related-title">Shifts nearby</h2><ul>{rel}</ul></section>
</div></div>"""
    video_node = {"@type": "VideoObject", "@id": url + "#video", "name": v["title"], "description": f'{v["problem"]} {v["value"]}',
                  "thumbnailUrl": B.SITE["url"] + poster(v), "contentUrl": B.SITE["url"] + clip(v), "embedUrl": embed_src,
                  "uploadDate": v["published"], "duration": "PT5S", "publisher": {"@id": B.ORG_ID}}
    graph = [video_node, crumbs([("/", "Home"), (BASE + "/", "The Shift"), (BASE + "/board/", "Impact board"), (vurl(v), v["title"])])]
    extra = (f'<meta property="og:video" content="{B.SITE["url"]}{clip(v)}">\n<meta property="og:video:secure_url" content="{B.SITE["url"]}{clip(v)}">\n'
             f'<meta property="og:video:type" content="video/mp4"><meta property="og:video:width" content="1280"><meta property="og:video:height" content="720">\n'
             f'<meta property="og:image:alt" content="{esc(v["beforeText"])} to {esc(v["afterText"])}">\n'
             f'<link rel="alternate" type="application/json+oembed" href="{B.SITE["url"]}{BASE}/oembed/{v["slug"]}.json" title="{esc(v["title"])}">\n')
    doc = B.page(vurl(v), v["title"], desc, main, graph, og_image=f'{BASE}/og/{v["slug"]}.png', og_type="video.other",
                 tone="light", extra_head=head_extra(extra))
    return finish(doc, f'{BASE}/og/{v["slug"]}.png')


def embed_page(v):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(v["title"])} · The Shift</title><meta name="robots" content="noindex">
<link rel="canonical" href="{B.SITE["url"]}{vurl(v)}">
<link rel="stylesheet" href="{BASE}/shift.css?v={VERSION}"></head>
<body class="shift-embed"><h1>{esc(v["title"])}</h1>
<video src="{clip(v)}" poster="{poster(v)}" controls playsinline preload="metadata"></video>
<a href="{B.SITE["url"]}{vurl(v)}" target="_blank" rel="noopener"><b>{esc(v["beforeLabel"])} → {esc(v["afterLabel"])}</b>Prompt and stack on The Shift</a>
</body></html>
"""


def oembed(v):
    return json.dumps({"version": "1.0", "type": "video", "provider_name": "The Shift by Enablement Works", "provider_url": URL + "/",
                       "title": v["title"], "author_name": v["team"], "thumbnail_url": f'{B.SITE["url"]}{BASE}/og/{v["slug"]}.png',
                       "thumbnail_width": 1200, "thumbnail_height": 630, "width": 640, "height": 360,
                       "html": f'<iframe src="{B.SITE["url"]}{BASE}/embed/{v["slug"]}/" width="640" height="360" style="border:0" allow="fullscreen; picture-in-picture" title="{esc(v["title"])}"></iframe>'},
                      ensure_ascii=False)


def sitemap(vs):
    today = B.SITE["today"]
    urls = [f"<url><loc>{URL}/</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>",
            f"<url><loc>{URL}/board/</loc><lastmod>{today}</lastmod><priority>0.7</priority></url>"]
    for v in vs:
        urls.append(
            f'<url><loc>{B.SITE["url"]}{vurl(v)}</loc><lastmod>{v["published"]}</lastmod><priority>0.6</priority>'
            f'<video:video><video:thumbnail_loc>{B.SITE["url"]}{poster(v)}</video:thumbnail_loc><video:title>{esc(v["title"])}</video:title>'
            f'<video:description>{esc(v["problem"] + " " + v["value"])}</video:description><video:content_loc>{B.SITE["url"]}{clip(v)}</video:content_loc>'
            f'<video:player_loc>{B.SITE["url"]}{BASE}/embed/{v["slug"]}/</video:player_loc><video:duration>5</video:duration>'
            f'<video:publication_date>{v["published"]}</video:publication_date></video:video></url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">' + "".join(urls) + "</urlset>\n")


def main():
    vs = json.loads((HERE / "catalog.json").read_text())
    # footer data, exactly as build.main() fills it
    guides = B.load_docs("guides", "guide")
    pages_ = B.load_docs("pages", "page")
    by_slug = {d["slug"]: d for d in guides + pages_}
    B.FOOTER_GUIDES[:] = [(s, by_slug[s]["title"].split(":")[0]) for s in B.FEATURED if s in by_slug][:5]
    B.TICKER[:] = [(d["path"], f'{d["minutes"]} min', d["title"].split(":")[0]) for d in guides]

    # Media (film/, media/, og/) lives only in static/shift/ and is never touched here.
    # Everything else under static/shift/ is generated and rewritten on each run.
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "sitemap.xml", "shift.css", "shift.js"):
        (OUT / name).unlink(missing_ok=True)
    for sub in ("board", "v", "embed", "oembed"):
        shutil.rmtree(OUT / sub, ignore_errors=True)
    missing = [s for s in ("film", "media", "og") if not (OUT / s).is_dir()]
    if missing:
        sys.exit(f"Missing media folders in static/shift/: {', '.join(missing)}")
    shutil.copy(HERE / "shift.css", OUT / "shift.css")
    shutil.copy(HERE / "shift.js", OUT / "shift.js")

    def w(rel, text):
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    w("index.html", landing(vs))
    w("board/index.html", board_page(vs))
    for v in vs:
        w(f"v/{v['slug']}/index.html", video_page(v, vs))
        w(f"embed/{v['slug']}/index.html", embed_page(v))
        w(f"oembed/{v['slug']}.json", oembed(v))
    w("sitemap.xml", sitemap(vs))
    print(f"The Shift: {len(vs)} videos -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
