#!/usr/bin/env python3
"""Build enablement.works into docs/ (served by GitHub Pages).

Stdlib plus `markdown` and `yaml`. Run: python3 build.py
Content lives in content/ (guides/*.md, pages/*.md, glossary.yaml, faq.yaml).
Every page gets: canonical URL, Open Graph image, JSON-LD (@graph), breadcrumbs.
Site-wide files: sitemap.xml, robots.txt, feed.xml, llms.txt, llms-full.txt, IndexNow key, 404.
"""
import datetime as dt
import html
import json
import os
import re
import shutil
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
CONTENT = ROOT / "content"
STATIC = ROOT / "static"

SITE = {
    "url": "https://enablement.works",
    "name": "Enablement Works",
    "tagline": "The production and operations engine for sales enablement",
    "email": "hello@enablement.works",
    "description": "Enablement Works is the production and operations engine for B2B sales enablement teams. Your team sets the strategy. We build the content, roleplays and programs in your tools, run them, drive completion and report results to your CRO every month.",
    "indexnow_key": "8f3c1e7a52b94d06a1e2c9f4b7d05e63",
    "today": "2026-11-06",
}
CATEGORY_ORDER = ["Fundamentals", "Measurement", "Capacity and ROI", "Programs", "Coaching", "AI and agents", "Buyer-first selling"]
CATEGORY_SLUG = {c: re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-") for c in CATEGORY_ORDER}
FEATURED = ["what-is-sales-enablement", "sales-enablement-metrics", "sales-enablement-team-size", "sales-kickoff-follow-up", "ai-roleplay-sales-training", "outsourced-sales-enablement"]

esc = lambda s: html.escape(str(s or ""), quote=True)
ORG_ID = SITE["url"] + "/#org"
WEB_ID = SITE["url"] + "/#website"

# ---------------------------------------------------------------- content loading

def split_front(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def md_to_html(body):
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists", "attr_list", "fenced_code"],
                           extension_configs={"toc": {"permalink": False, "toc_depth": "2-3"}})
    out = md.convert(body)
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    out = re.sub(r'<a href="(https?://(?!enablement\.works)[^"]+)"', r'<a href="\1" rel="noopener">', out)
    toc = [(t["id"], t["name"]) for t in md.toc_tokens]
    return out, toc


def to_date(v):
    if isinstance(v, (dt.date, dt.datetime)):
        return v.strftime("%Y-%m-%d")
    return str(v or SITE["today"])


def load_docs(folder, kind):
    docs = []
    for p in sorted((CONTENT / folder).glob("*.md")) if (CONTENT / folder).exists() else []:
        fm, body = split_front(p.read_text(encoding="utf-8"))
        if not fm.get("title"):
            continue
        slug = fm.get("slug") or p.stem
        body_html, toc = md_to_html(body)
        words = len(re.findall(r"\w+", body))
        docs.append({**fm, "slug": slug, "kind": kind, "body_md": body.strip(), "body_html": body_html, "toc": toc,
                     "words": words, "minutes": max(3, round(words / 230)),
                     "published": to_date(fm.get("published")), "updated": to_date(fm.get("updated")),
                     "path": f"/guides/{slug}/" if kind == "guide" else f"/{slug}/"})
    return docs


def load_yaml(name):
    p = CONTENT / name
    if not p.exists():
        return []
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or []
    except yaml.YAMLError as e:
        print("YAML error in", name, e)
        return []

# ---------------------------------------------------------------- layout

NAV = [("/guides/", "Guides"), ("/tools/", "Tools"), ("/videos/", "Videos"), ("/sales-enablement-statistics/", "Statistics"), ("/glossary/", "Glossary")]


def org_node():
    return {"@type": "Organization", "@id": ORG_ID, "name": SITE["name"], "url": SITE["url"] + "/",
            "logo": {"@type": "ImageObject", "url": SITE["url"] + "/assets/logo-512.png", "width": 512, "height": 512},
            "email": SITE["email"], "description": SITE["description"], "slogan": SITE["tagline"],
            "knowsAbout": ["Sales enablement", "Sales training", "Sales onboarding", "Sales coaching", "Sales kickoff reinforcement",
                           "Enablement metrics", "AI roleplay", "Sales enablement operations", "Revenue enablement"],
            "areaServed": "Worldwide"}


def website_node():
    return {"@type": "WebSite", "@id": WEB_ID, "url": SITE["url"] + "/", "name": SITE["name"],
            "description": SITE["description"], "publisher": {"@id": ORG_ID}, "inLanguage": "en-US"}


def crumbs_node(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE["url"] + u} for i, (u, n) in enumerate(trail)]}


def crumbs_html(trail):
    items = "".join(f'<li><a href="{u}">{esc(n)}</a></li>' if i < len(trail) - 1 else f'<li aria-current="page">{esc(n)}</li>'
                    for i, (u, n) in enumerate(trail))
    return f'<nav class="case__crumbs" aria-label="Breadcrumb"><ol>{items}</ol></nav>'


ROLE_NAMES = {"cro": "CROs", "enablement": "Enablement leaders", "manager": "Sales managers", "revops": "RevOps"}
ROLE_TAG = {"cro": "CRO", "enablement": "Enablement", "manager": "Managers", "revops": "RevOps"}
ROLES = {
    "what-is-sales-enablement": ["cro", "enablement", "manager", "revops"],
    "sales-enablement-vs-sales-training": ["enablement", "cro"],
    "sales-enablement-roadmap": ["enablement", "cro"],
    "sales-enablement-metrics": ["cro", "enablement", "revops"],
    "measuring-sales-training-effectiveness": ["enablement", "revops"],
    "sales-skills-scorecard": ["enablement", "manager"],
    "enablement-report-for-cro": ["cro", "enablement"],
    "enablement-pilot-design": ["enablement", "revops"],
    "sales-enablement-team-size": ["cro", "enablement"],
    "sales-enablement-roi": ["cro", "enablement", "revops"],
    "cost-per-active-user": ["revops", "enablement", "cro"],
    "outsourced-sales-enablement": ["cro", "enablement"],
    "sales-kickoff-follow-up": ["enablement", "manager", "cro"],
    "sales-coaching-coverage": ["manager", "cro", "enablement"],
    "sales-manager-reinforcement": ["manager", "enablement"],
    "continuous-sales-training": ["enablement", "manager"],
    "sales-onboarding-program": ["enablement", "manager"],
    "ai-in-sales-enablement": ["enablement", "cro", "revops"],
    "ai-roleplay-sales-training": ["enablement", "manager"],
    "ai-agents-sales-enablement": ["revops", "enablement"],
    "buying-group-consensus": ["manager", "cro"],
    "problem-first-selling": ["manager", "enablement"],
    "sales-enablement-statistics": ["cro", "enablement", "revops", "manager"],
}

VIDEO_META = json.loads((ROOT / "video" / "video-meta.json").read_text()) if (ROOT / "video" / "video-meta.json").exists() else {}
VIDEOS = {  # guide slug -> video
    "sales-enablement-team-size": {"name": "team-size", "title": "How many enablement people does your plan need?", "desc": "The 1:25 to 50 rule of thumb for sizing a sales enablement team, and what the gap looks like when the plan outgrows the team."},
    "sales-enablement-metrics": {"name": "four-levels", "title": "The four levels of evidence a CRO will fund", "desc": "Activity, practice, behavior and outcome: the four levels of sales enablement evidence, and how to set a baseline."},
    "sales-kickoff-follow-up": {"name": "kickoff-90-days", "title": "What the 90 days after a sales kickoff need", "desc": "Certification, roleplays, nudges and a day 30/60/90 report: the plan for the 90 days after a sales kickoff."},
}


def iso_dur(sec):
    sec = int(round(sec))
    return f"PT{sec // 60}M{sec % 60}S"


def video_node(slug, page_url):
    v = VIDEOS[slug]
    m = VIDEO_META.get(v["name"], {})
    return {"@type": "VideoObject", "@id": page_url + "#video", "name": v["title"], "description": v["desc"],
            "thumbnailUrl": f"{SITE['url']}/media/{v['name']}-poster.jpg", "uploadDate": "2026-11-06",
            "duration": iso_dur(m.get("duration", 50)), "contentUrl": f"{SITE['url']}/media/{v['name']}.mp4",
            "embedUrl": page_url, "transcript": m.get("transcript", ""), "inLanguage": "en", "publisher": {"@id": ORG_ID}}


def video_html(slug):
    v = VIDEOS[slug]
    m = VIDEO_META.get(v["name"], {})
    return (f'<figure class="player" style="transform:none;margin:0 0 36px"><video controls preload="none" playsinline poster="/media/{v["name"]}-poster.jpg" width="1920" height="1080">'
            f'<source src="/media/{v["name"]}.mp4" type="video/mp4"><track kind="captions" src="/media/{v["name"]}.vtt" srclang="en" label="English"></video>'
            f'<figcaption class="player__bar"><span>Watch: {esc(v["title"])}</span><b>{int(m.get("duration", 50))} s</b></figcaption></figure>'
            f'<details class="transcript" style="margin:-20px 0 36px"><summary>Video transcript</summary><p>{esc(m.get("transcript", ""))}</p></details>')


WORDMARK = ('<span class="wordmark">Enablement<svg class="wordmark__slash" viewBox="0 0 12 20" aria-hidden="true">'
            '<path d="M10 2 L2 18"/></svg>Works</span>')


def page(path, title, description, main, graph, og_image="/og/default.png", og_type="website", current="", extra_head="", tone="light"):
    url = SITE["url"] + path
    cur = ' aria-current="page"'
    nav = "".join(f'<a class="sitenav__link{" keep" if u == "/guides/" else ""}" href="{u}"{cur if current == u else ""}>{n}</a>' for u, n in NAV)
    ld = json.dumps({"@context": "https://schema.org", "@graph": [org_node(), website_node()] + graph}, ensure_ascii=False, separators=(",", ":"))
    full_title = title if (SITE["name"] in title or len(title) > 52) else f"{title} · {SITE['name']}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE['url']}{og_image}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1530FF">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/logo-180.png">
<link rel="alternate" type="application/atom+xml" title="Enablement Works guides" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,500;0,600;0,700;0,800;0,900;1,800;1,900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v=5">
{extra_head}<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skiplink" href="#main">Skip to content</a>
<header class="sitenav" data-tone="{tone}">
  <a class="sitenav__home" href="/" aria-label="Enablement Works, home">{WORDMARK}</a>
  <nav class="sitenav__links" aria-label="Main">{nav}<a class="sitenav__cta" href="/#capacity-check"><span class="long">Capacity Check</span><span class="short">Book a call</span></a></nav>
</header>
<main id="main">
{main}
</main>
{footer()}
</body>
</html>
"""


TICKER = []


def footer():
    g = "".join(f'<li><a href="/guides/{s}/">{esc(t)}</a></li>' for s, t in FOOTER_GUIDES)
    run = "".join(f'<a class="ticker__item" href="{u}"><b>{esc(k)}</b>{esc(t)}</a>' for u, k, t in TICKER)
    ticker = f'<div class="ticker" aria-hidden="true"><div class="ticker__run">{run}{run}</div></div>' if run else ""
    return f"""<footer class="sitefooter">
  {ticker}
  <div class="sitefooter__inner">
    <div>{WORDMARK.replace('class="wordmark"', 'class="wordmark" style="font-size:26px"')}<p class="sitefooter__line">{esc(SITE['tagline'])}. Your team sets the strategy. We build, run and report.</p><p class="sitefooter__line"><a href="mailto:{SITE['email']}">{SITE['email']}</a></p></div>
    <div><h2>Guides</h2><ul class="sitefooter__nav">{g}<li><a href="/guides/">All guides →</a></li></ul></div>
    <div><h2>Resources</h2><ul class="sitefooter__nav"><li><a href="/tools/enablement-capacity-calculator/">Capacity calculator</a></li><li><a href="/tools/cost-per-active-user-calculator/">Cost per active user</a></li><li><a href="/sales-enablement-statistics/">Statistics</a></li><li><a href="/glossary/">Glossary</a></li><li><a href="/faq/">FAQ</a></li></ul></div>
    <div><h2>Company</h2><ul class="sitefooter__nav"><li><a href="/about/">About</a></li><li><a href="/#offer">The offer</a></li><li><a href="/#capacity-check">Capacity Check</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/feed.xml">RSS</a> · <a href="/llms.txt">llms.txt</a></li></ul></div>
  </div>
  <div class="wrap"><p class="samplenote" style="padding-bottom:28px">© 2026 Enablement Works. Guides may be quoted with a link to the source page. Rules of thumb are ours; every outside number links to its source.</p></div>
</footer>"""


FOOTER_GUIDES = []

# ---------------------------------------------------------------- page types

def roles_of(d):
    return ROLES.get(d["slug"], ["enablement"])


def row(d, rank, by_rank=True):
    """A ledger row (The Shift's .shiftrow) for a guide or page."""
    roles = roles_of(d)
    tags = "".join(f'<span class="tag tag--role">{ROLE_TAG[r]}</span>' for r in roles[:2])
    tags += f'<span class="tag tag--topic">{esc(d.get("category", "Guide"))}</span>'
    chips = "".join(f"<li>{esc(q)}</li>" for q in ([d.get("primary_query")] + (d.get("related_queries") or [])[:1]) if q)
    cat = CATEGORY_SLUG.get(d.get("category", ""), "other")
    hay = " ".join([d["title"], d.get("description", ""), d.get("primary_query", "")] + (d.get("related_queries") or [])).lower()
    return (f'<li class="shiftrow" data-topic="{cat}" data-roles="{" ".join(roles)}" data-format="{ {"page": "reference", "tool": "tool"}.get(d["kind"], "guide") }" '
            f'data-minutes="{d["minutes"]}" data-updated="{d["updated"]}" data-rank="{rank}" data-hay="{esc(hay)}">'
            f'<span class="shiftrow__rank">{rank:02d}</span>'
            f'<a class="shiftrow__thumb" href="{d["path"]}" tabindex="-1" aria-hidden="true"><img src="/og/{d["slug"]}.png" alt="" loading="lazy" width="1200" height="630"></a>'
            f'<div class="shiftrow__main"><a class="shiftrow__title" href="{d["path"]}">{esc(d["title"])}</a>'
            f'<p class="shiftrow__desc">{esc(d.get("description", ""))}</p><div class="shiftrow__tags">{tags}</div></div>'
            f'<ul class="stackchips">{chips}</ul><span class="shiftrow__x">{d["minutes"]} min</span></li>')


def card(d):
    return row(d, 1)


def faq_html(faqs, heading="Frequently asked questions", open_first=False):
    if not faqs:
        return ""
    qs = "".join(f'<details class="faq__item"{" open" if (open_first and i == 0) else ""}><summary>{esc(f["q"])}</summary><p class="faq__a">{inline_md(f["a"])}</p></details>'
                 for i, f in enumerate(faqs))
    return f'<section class="faqs" aria-labelledby="faq-h"><h2 id="faq-h">{heading}</h2><div class="faq">{qs}</div></section>'


def inline_md(s):
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\((/[^)\s]*|https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def faq_node(faqs, url):
    return {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", f["a"])}} for f in faqs]}


SHARE_JS = """<script>
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',()=>{const t=b.getAttribute('data-copy')==='url'?location.href:document.getElementById(b.getAttribute('data-copy')).innerText;navigator.clipboard&&navigator.clipboard.writeText(t).then(()=>{const o=b.textContent;b.textContent='Copied';setTimeout(()=>b.textContent=o,1600)})}));
</script>"""


def render_doc(d, by_slug, crumbs):
    from urllib.parse import quote
    url = SITE["url"] + d["path"]
    toc = "".join(f'<li><a href="#{i}">{esc(n)}</a></li>' for i, n in d["toc"])
    takeaways = "".join(f"<li>{inline_md(t)}</li>" for t in d.get("key_takeaways") or [])
    srcs = [s for s in d.get("sources") or [] if s.get("url")]
    sources = "".join(f'<li><a href="{esc(s.get("url"))}" rel="noopener">{esc(s.get("title"))}</a></li>' for s in srcs)
    related = [by_slug[s] for s in d.get("related") or [] if s in by_slug][:4]
    related_html = (f'<section class="sec sec--cobalt"><div class="wrap"><div class="sec__head"><h2 class="sec__title">Read next.</h2>'
                    f'<p class="sec__lede">Guides that answer the next question people ask after this one.</p></div>'
                    f'<ol class="ledger">{"".join(row(r, i + 1) for i, r in enumerate(related))}</ol>'
                    f'<a class="cta-banner" href="/guides/">Open every guide, filtered by role and topic</a></div></section>') if related else ""
    answer = d.get("answer", "")
    roles = "".join(f'<a class="tag tag--role" href="/guides/?role={r}">{ROLE_TAG[r]}</a>' for r in roles_of(d))
    q = quote(url, safe="")
    t = quote(d["title"], safe="")
    main = f"""<article class="case wrap">
  {crumbs_html(crumbs)}
  <header class="case__head">
    <div class="case__tags"><a class="tag tag--ink" href="/guides/?topic={CATEGORY_SLUG.get(d.get('category', ''), '')}">{esc(d.get('category', 'Guide'))}</a>{roles}</div>
    <h1 class="case__title">{esc(d['title'])}</h1>
    <p class="case__byline"><span>Updated <time datetime="{d['updated']}">{fmt_date(d['updated'])}</time></span><span>{d['minutes']} min read</span><span>{len(srcs)} sources</span><span>Enablement Works editorial team</span></p>
  </header>
  <div class="case__grid">
    <div class="case__main">
      {f'<section class="takeaways"><h2>Key takeaways</h2><ul class="ticklist">{takeaways}</ul></section>' if takeaways else ''}
      {video_html(d['slug']) if d['slug'] in VIDEOS else ''}
      <div class="body">{d['body_html']}</div>
      {faq_html(d.get('faqs'), open_first=True)}
      {f'<section class="sources"><h2>Sources</h2><ol>{sources}</ol></section>' if sources else ''}
      <section class="share" aria-labelledby="share-h"><h2 class="share__title" id="share-h">Share this guide</h2>
        <div class="share__row"><button type="button" data-copy="url">Copy link</button><a href="https://www.linkedin.com/sharing/share-offsite/?url={q}" rel="noopener" target="_blank">LinkedIn</a><a href="https://x.com/intent/post?url={q}&amp;text={t}" rel="noopener" target="_blank">X</a><a href="mailto:?subject={t}&amp;body={q}">Email</a><a href="{d['path'].rstrip('/')}.md">Markdown</a></div></section>
      <aside class="cta-cobalt"><h2>How much enablement work does your plan need?</h2><p>The Capacity Check takes 20 minutes with your CRO and head of enablement. You get a scored summary and a capacity estimate the next day. Free.</p><a class="btn-block" href="/#capacity-check">Book a Capacity Check</a></aside>
    </div>
    <aside class="case__side">
      {f'<section class="move" aria-labelledby="answer-h"><h2 class="move__title" id="answer-h">The short answer</h2><p class="move__text" id="short-answer">{inline_md(answer)}</p><button type="button" class="slab" data-copy="short-answer">Copy the answer</button><p class="move__hint">Quote it with a link to this page.</p></section>' if answer else ''}
      <dl class="specs"><div><dt>Updated</dt><dd>{fmt_date(d['updated'])}</dd></div><div><dt>Read</dt><dd>{d['minutes']} min</dd></div><div><dt>Topic</dt><dd>{esc(d.get('category', 'Guide'))}</dd></div><div><dt>Sources</dt><dd>{len(srcs)} linked</dd></div></dl>
      {f'<nav class="toc" aria-label="On this page"><h2>On this page</h2><ol>{toc}</ol></nav>' if toc else ''}
    </aside>
  </div>
</article>
{related_html}
{SHARE_JS}"""
    graph = [{
        "@type": "Article", "@id": url + "#article", "headline": d["title"][:110], "description": d.get("description", ""),
        "abstract": answer, "url": url, "mainEntityOfPage": url, "datePublished": d["published"], "dateModified": d["updated"],
        "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}, "isPartOf": {"@id": WEB_ID}, "inLanguage": "en-US",
        "image": f"{SITE['url']}/og/{d['slug']}.png", "articleSection": d.get("category", ""), "wordCount": d["words"],
        "keywords": ", ".join([d.get("primary_query", "")] + (d.get("related_queries") or [])),
        "about": {"@type": "Thing", "name": d.get("primary_query", d["title"])},
        "audience": [{"@type": "Audience", "audienceType": ROLE_NAMES[r]} for r in roles_of(d)],
        "citation": [s.get("url") for s in srcs],
        "speakable": {"@type": "SpeakableSpecification", "cssSelector": ["#short-answer"]},
    }, crumbs_node(crumbs)]
    if d.get("faqs"):
        graph.append(faq_node(d["faqs"], url))
    if d["slug"] in VIDEOS:
        graph.append(video_node(d["slug"], url))
    extra = f'<link rel="alternate" type="text/markdown" href="{d["path"].rstrip("/")}.md">\n'
    extra += f'<meta property="article:published_time" content="{d["published"]}"><meta property="article:modified_time" content="{d["updated"]}">\n'
    return page(d["path"], seo_title(d["title"]), d.get("description", ""), main, graph, og_image=f"/og/{d['slug']}.png", og_type="article",
                current="/guides/" if d["kind"] == "guide" else d["path"], extra_head=extra, tone="light")


def seo_title(title):
    """Short <title> for search results: keep the question or the part before the colon when the full title is long."""
    if len(title) <= 60:
        return title
    m = re.match(r"^(.{20,70}?[?:])\s", title)
    if m:
        t = m.group(1).rstrip(":")
        return t
    return title


def fmt_date(s):
    try:
        return dt.datetime.strptime(s, "%Y-%m-%d").strftime("%-d %b %Y")
    except ValueError:
        return s


# ---------------------------------------------------------------- output helpers

WRITTEN = []  # (path, lastmod, priority)


def write(path, content, lastmod=None, priority=0.6, sitemap=True):
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    if sitemap and (path.endswith("/") or path.endswith(".html")):
        WRITTEN.append((path, lastmod or SITE["today"], priority))


from pages import TOOL_DOCS, home_page, tools_pages, about_page, privacy_page, not_found_page, glossary_page, faq_page, guides_hub  # noqa: E402
import og  # noqa: E402


def main():
    if OUT.exists():
        for child in OUT.iterdir():
            if child.name in ("media",):  # large media kept between builds
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    OUT.mkdir(exist_ok=True)
    shutil.copytree(STATIC, OUT, dirs_exist_ok=True)

    guides = load_docs("guides", "guide")
    pages_ = load_docs("pages", "page")
    by_slug = {d["slug"]: d for d in guides + pages_}
    glossary = load_yaml("glossary.yaml")
    faqs = load_yaml("faq.yaml")
    FOOTER_GUIDES[:] = [(s, by_slug[s]["title"].split(":")[0]) for s in FEATURED if s in by_slug][:5]
    TICKER[:] = [(d["path"], f'{d["minutes"]} min', d["title"].split(":")[0]) for d in guides]

    ctx = dict(SITE=SITE, page=page, card=card, esc=esc, crumbs_html=crumbs_html, crumbs_node=crumbs_node, faq_html=faq_html,
               faq_node=faq_node, inline_md=inline_md, ORG_ID=ORG_ID, WEB_ID=WEB_ID, by_slug=by_slug, guides=guides,
               FEATURED=FEATURED, CATEGORY_ORDER=CATEGORY_ORDER, row=row, roles_of=roles_of, ROLE_NAMES=ROLE_NAMES, ROLE_TAG=ROLE_TAG, WORDMARK=WORDMARK, SHARE_JS=SHARE_JS, CATEGORY_SLUG=CATEGORY_SLUG, glossary=glossary, faqs=faqs)

    write("/", home_page(ctx), priority=1.0)
    write("/guides/", guides_hub(ctx), priority=0.9)
    for d in guides:
        write(d["path"], render_doc(d, by_slug, [("/", "Home"), ("/guides/", "Guides"), (d["path"], d["title"].split(":")[0])]), d["updated"], 0.8)
        write(d["path"].rstrip("/") + ".md", doc_markdown(d), sitemap=False)
    for d in pages_:
        write(d["path"], render_doc(d, by_slug, [("/", "Home"), (d["path"], d["title"].split(":")[0])]), d["updated"], 0.9)
        write(d["path"].rstrip("/") + ".md", doc_markdown(d), sitemap=False)
    for path, html_ in tools_pages(ctx):
        write(path, html_, priority=0.8)
    if glossary:
        write("/glossary/", glossary_page(ctx), priority=0.8)
    if faqs:
        write("/faq/", faq_page(ctx), priority=0.7)
    write("/videos/", videos_page(by_slug), priority=0.7)
    write("/about/", about_page(ctx), priority=0.6)
    write("/privacy/", privacy_page(ctx), priority=0.2)
    write("/404.html", not_found_page(ctx), sitemap=False)

    site_files(guides, pages_, glossary, faqs)
    video_sitemap(by_slug)
    og.build_all(OUT, SITE, guides + pages_ + TOOL_DOCS)
    print(f"Built {len(WRITTEN)} pages: {len(guides)} guides, {len(pages_)} pages, {len(glossary)} terms, {len(faqs)} FAQs")


def videos_page(by_slug):
    items = []
    for slug, v in VIDEOS.items():
        d = by_slug.get(slug)
        if not d:
            continue
        m = VIDEO_META.get(v["name"], {})
        items.append(f'''<li class="seat" style="margin-top:0"><div class="seat__link" style="background:var(--cobalt-deep);color:#fff">
<figure class="player" style="transform:none;margin:0"><video controls preload="none" playsinline poster="/media/{v["name"]}-poster.jpg" width="1920" height="1080"><source src="/media/{v["name"]}.mp4" type="video/mp4"><track kind="captions" src="/media/{v["name"]}.vtt" srclang="en" label="English"></video></figure>
<span class="seat__role">{esc(v["title"])}</span><span class="seat__copy">{esc(v["desc"])}</span><a class="cta-enter" href="{d["path"]}">Read the guide <span class="cta-enter__arrow">→</span></a></div></li>''')
    url = SITE["url"] + "/videos/"
    trail = [("/", "Home"), ("/videos/", "Videos")]
    graph = [crumbs_node(trail), {"@type": "CollectionPage", "@id": url, "url": url, "name": "Sales enablement videos", "isPartOf": {"@id": WEB_ID}}]
    graph += [video_node(slug, SITE["url"] + by_slug[slug]["path"]) for slug in VIDEOS if slug in by_slug]
    main = f'''<section class="board" aria-labelledby="v-h"><div class="wrap">
<div class="board__head"><div><h1 class="board__title" id="v-h">Enablement in <span class="under-coral">under a minute.</span></h1><p class="board__sub">Short, captioned explainers. Each one goes with a full guide that has the formula, a worked example and its sources.</p></div></div>
<ol class="seats" style="grid-template-columns:repeat(auto-fill,minmax(min(100%,360px),1fr))">{"".join(items)}</ol>
<a class="cta-banner" href="/#video">Watch the 2-minute Enablement Works explainer</a></div></section>'''
    return page("/videos/", "Sales enablement videos: short explainers", "Short, captioned sales enablement explainers: team size, the four levels of evidence and the 90 days after a sales kickoff.", main, graph, current="/videos/", tone="cobalt")


def video_sitemap(by_slug):
    entries = []
    for slug, v in VIDEOS.items():
        d = by_slug.get(slug)
        if not d:
            continue
        m = VIDEO_META.get(v["name"], {})
        entries.append(f"""<url><loc>{SITE['url']}{d['path']}</loc><video:video><video:thumbnail_loc>{SITE['url']}/media/{v['name']}-poster.jpg</video:thumbnail_loc><video:title>{esc(v['title'])}</video:title><video:description>{esc(v['desc'])}</video:description><video:content_loc>{SITE['url']}/media/{v['name']}.mp4</video:content_loc><video:duration>{int(m.get('duration', 50))}</video:duration><video:publication_date>2026-11-06T09:00:00+00:00</video:publication_date><video:family_friendly>yes</video:family_friendly></video:video></url>""")
    entries.append(f"""<url><loc>{SITE['url']}/</loc><video:video><video:thumbnail_loc>{SITE['url']}/media/enablement-works-explainer-poster.png</video:thumbnail_loc><video:title>Enablement Works in two and a half minutes</video:title><video:description>How Enablement Works builds and runs sales enablement programs for B2B sales teams.</video:description><video:content_loc>{SITE['url']}/media/enablement-works-explainer.mp4</video:content_loc><video:duration>155</video:duration><video:publication_date>2026-10-06T09:00:00+00:00</video:publication_date></video:video></url>""")
    (OUT / "sitemap-video.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">' + "".join(entries) + "</urlset>\n")


def doc_markdown(d):
    lines = [f"# {d['title']}", "", f"> {d.get('answer', '')}", "", f"Source: {SITE['url']}{d['path']} · Updated {d['updated']} · Enablement Works", ""]
    if d.get("key_takeaways"):
        lines += ["## Key takeaways", ""] + [f"- {t}" for t in d["key_takeaways"]] + [""]
    lines += [d["body_md"], ""]
    if d.get("faqs"):
        lines += ["## FAQ", ""]
        for f in d["faqs"]:
            lines += [f"### {f['q']}", "", f["a"], ""]
    if d.get("sources"):
        lines += ["## Sources", ""] + [f"- [{s.get('title')}]({s.get('url')})" for s in d["sources"]]
    return "\n".join(lines) + "\n"


def site_files(guides, pages_, glossary, faqs):
    # sitemap
    urls = "".join(f"<url><loc>{SITE['url']}{p}</loc><lastmod>{m}</lastmod><priority>{pr:.1f}</priority></url>" for p, m, pr in WRITTEN if p != "/404.html")
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    # robots: welcome search and answer-engine crawlers explicitly
    bots = ["Googlebot", "Bingbot", "OAI-SearchBot", "ChatGPT-User", "GPTBot", "PerplexityBot", "Perplexity-User", "Claude-SearchBot",
            "Claude-User", "ClaudeBot", "Google-Extended", "Applebot", "Applebot-Extended", "DuckDuckBot", "CCBot", "Amazonbot", "meta-externalagent"]
    robots = "# Enablement Works welcomes search engines and AI answer engines.\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
    robots += "User-agent: *\nAllow: /\n\nSitemap: " + SITE["url"] + "/sitemap.xml\nSitemap: " + SITE["url"] + "/sitemap-video.xml\n"
    for extra in sorted(STATIC.glob("*/**/sitemap*.xml")):  # sub-sites copied from static/, e.g. static/shift/sitemap.xml
        robots += "Sitemap: " + SITE["url"] + "/" + extra.relative_to(STATIC).as_posix() + "\n"
    (OUT / "robots.txt").write_text(robots)
    # IndexNow key
    (OUT / f"{SITE['indexnow_key']}.txt").write_text(SITE["indexnow_key"])
    # Atom feed
    items = sorted(guides + pages_, key=lambda d: d["updated"], reverse=True)
    entries = "".join(f"""<entry><title>{esc(d['title'])}</title><link href="{SITE['url']}{d['path']}"/><id>{SITE['url']}{d['path']}</id><updated>{d['updated']}T09:00:00Z</updated><published>{d['published']}T09:00:00Z</published><summary>{esc(d.get('answer') or d.get('description'))}</summary><category term="{esc(d.get('category', ''))}"/></entry>""" for d in items)
    (OUT / "feed.xml").write_text(f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>Enablement Works guides</title><subtitle>{esc(SITE['tagline'])}</subtitle><link href="{SITE['url']}/feed.xml" rel="self"/><link href="{SITE['url']}/"/><id>{SITE['url']}/</id><updated>{SITE['today']}T09:00:00Z</updated><author><name>Enablement Works</name><email>{SITE['email']}</email></author>{entries}</feed>
""")
    # llms.txt (summary index) and llms-full.txt (all guide text)
    by_cat = {}
    for d in guides:
        by_cat.setdefault(d.get("category", "Guides"), []).append(d)
    L = [f"# {SITE['name']}", "", f"> {SITE['description']}", "",
         "Enablement Works publishes practical, sourced guides on sales enablement: metrics, team sizing, ROI, onboarding, coaching, kickoff reinforcement, AI roleplay, AI agents and buying groups. Every guide opens with a direct answer. Quote freely with a link to the source page.", "",
         "## Company", "", f"- [What we do]({SITE['url']}/): production and operations for sales enablement teams of B2B companies with 100 to 1,000 reps. Offers: a three-week Enablement Diagnostic and the Enablement Engine subscription. Free 20-minute Capacity Check.",
         f"- [About and editorial standards]({SITE['url']}/about/)", f"- Contact: {SITE['email']}", ""]
    for c in CATEGORY_ORDER:
        if c in by_cat:
            L += [f"## {c}", ""] + [f"- [{d['title']}]({SITE['url']}{d['path']}): {d.get('answer', '')}" for d in by_cat[c]] + [""]
    L += ["## Reference", "", f"- [Sales enablement statistics]({SITE['url']}/sales-enablement-statistics/): sourced numbers for 2026",
          f"- [Sales enablement glossary]({SITE['url']}/glossary/): {len(glossary)} terms with definitions",
          f"- [Sales enablement FAQ]({SITE['url']}/faq/): {len(faqs)} direct answers",
          f"- [Enablement capacity calculator]({SITE['url']}/tools/enablement-capacity-calculator/): how many enablement people a sales plan needs",
          f"- [Cost per active user calculator]({SITE['url']}/tools/cost-per-active-user-calculator/): what each enablement tool costs per rep who uses it",
          "", "## Optional", "", f"- [Full text of every guide]({SITE['url']}/llms-full.txt)", ""]
    (OUT / "llms.txt").write_text("\n".join(L))
    full = [f"# {SITE['name']}: full guide text", "", f"> {SITE['description']}", ""]
    for d in pages_ + guides:
        full += ["---", "", doc_markdown(d)]
    if glossary:
        full += ["---", "", "# Sales enablement glossary", ""] + [f"**{g['term']}**: {g.get('short', '')} {g.get('long', '')}\n" for g in glossary]
    (OUT / "llms-full.txt").write_text("\n".join(full))
    (OUT / "CNAME").write_text("enablement.works\n")
    (OUT / ".nojekyll").write_text("")


if __name__ == "__main__":
    main()
