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

NAV = [("/guides/", "Guides"), ("/tools/", "Tools"), ("/sales-enablement-statistics/", "Statistics"), ("/glossary/", "Glossary")]


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
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{items}</ol></nav>'


def page(path, title, description, main, graph, og_image="/og/default.png", og_type="website", current="", extra_head=""):
    url = SITE["url"] + path
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{u}"{cur if current == u else ""}>{n}</a>' for u, n in NAV)
    ld = json.dumps({"@context": "https://schema.org", "@graph": [org_node(), website_node()] + graph}, ensure_ascii=False, separators=(",", ":"))
    full_title = title if title.endswith(SITE["name"]) else f"{title} · {SITE['name']}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
<meta name="theme-color" content="#14453D">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/logo-180.png">
<link rel="alternate" type="application/atom+xml" title="Enablement Works guides" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Public+Sans:wght@400;500;600;700&family=Red+Hat+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v=3">
{extra_head}<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
  <div class="wrap">
    <a class="word" href="/" aria-label="Enablement Works, home">Enablement Works</a>
    <nav aria-label="Main">{nav}<a class="btn btn-sm" href="/#capacity-check">Capacity Check</a></nav>
  </div>
</header>
<main id="main">
{main}
</main>
{footer()}
</body>
</html>
"""


def footer():
    g = "".join(f'<li><a href="/guides/{s}/">{esc(t)}</a></li>' for s, t in FOOTER_GUIDES)
    return f"""<footer class="site">
  <div class="wrap">
    <div class="cols">
      <div><h2>Enablement Works</h2><p>{esc(SITE['tagline'])}. Your team sets the strategy. We build, run and report.</p><p><a href="mailto:{SITE['email']}">{SITE['email']}</a></p></div>
      <div><h2>Guides</h2><ul>{g}<li><a href="/guides/">All guides</a></li></ul></div>
      <div><h2>Resources</h2><ul><li><a href="/tools/enablement-capacity-calculator/">Capacity calculator</a></li><li><a href="/tools/cost-per-active-user-calculator/">Cost per active user</a></li><li><a href="/sales-enablement-statistics/">Statistics</a></li><li><a href="/glossary/">Glossary</a></li><li><a href="/faq/">FAQ</a></li></ul></div>
      <div><h2>Company</h2><ul><li><a href="/about/">About</a></li><li><a href="/#offer">The offer</a></li><li><a href="/#capacity-check">Capacity Check</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="/feed.xml">RSS</a></li><li><a href="/llms.txt">llms.txt</a></li></ul></div>
    </div>
    <p class="legal">© 2026 Enablement Works. Guides may be quoted with a link to the source page.</p>
  </div>
</footer>"""


FOOTER_GUIDES = []

# ---------------------------------------------------------------- page types

def card(d):
    return (f'<article class="card"><span class="cat">{esc(d.get("category", ""))}</span>'
            f'<h3><a href="{d["path"]}">{esc(d["title"])}</a></h3><p>{esc(d.get("description", ""))}</p></article>')


def faq_html(faqs, heading="Frequently asked questions"):
    if not faqs:
        return ""
    qs = "".join(f'<div class="qa"><h3>{esc(f["q"])}</h3><p>{inline_md(f["a"])}</p></div>' for f in faqs)
    return f'<section class="faqs" aria-labelledby="faq-h"><h2 id="faq-h">{heading}</h2>{qs}</section>'


def inline_md(s):
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\((/[^)\s]*|https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def faq_node(faqs, url):
    return {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", f["a"])}} for f in faqs]}


def render_doc(d, by_slug, crumbs):
    url = SITE["url"] + d["path"]
    toc = "".join(f'<li><a href="#{i}">{esc(n)}</a></li>' for i, n in d["toc"])
    takeaways = "".join(f"<li>{inline_md(t)}</li>" for t in d.get("key_takeaways") or [])
    sources = "".join(f'<li><a href="{esc(s.get("url"))}" rel="noopener">{esc(s.get("title"))}</a></li>' for s in d.get("sources") or [] if s.get("url"))
    related = [by_slug[s] for s in d.get("related") or [] if s in by_slug][:4]
    related_html = (f'<section class="related"><div class="wrap"><h2>Related guides</h2><div class="cards">{"".join(card(r) for r in related)}</div></div></section>') if related else ""
    answer = d.get("answer", "")
    main = f"""<header class="page-head"><div class="wrap">
  {crumbs_html(crumbs)}
  <h1>{esc(d['title'])}</h1>
  <p class="byline"><span>{esc(d.get('category', 'Guide'))}</span><span>Updated <time datetime="{d['updated']}">{fmt_date(d['updated'])}</time></span><span>{d['minutes']} min read</span><span>By the Enablement Works editorial team</span></p>
</div></header>
<div class="wrap"><div class="article">
  <article class="article-main">
    {f'<section class="answer" aria-labelledby="answer-h"><h2 id="answer-h">Short answer</h2><p>{inline_md(answer)}</p></section>' if answer else ''}
    {f'<section class="takeaways"><h2>Key takeaways</h2><ul>{takeaways}</ul></section>' if takeaways else ''}
    <div class="body">{d['body_html']}</div>
    {faq_html(d.get('faqs'))}
    {f'<section class="sources"><h2>Sources</h2><ol>{sources}</ol></section>' if sources else ''}
    <aside class="inline-cta"><p>Want to know how much enablement work your plan needs, and how much your team can deliver? The Capacity Check takes 20 minutes and is free.</p><a class="btn" href="/#capacity-check">Book a Capacity Check</a></aside>
  </article>
  <aside class="aside">
    {f'<nav class="toc" aria-label="On this page"><h2>On this page</h2><ol>{toc}</ol></nav>' if toc else ''}
    <div class="box"><p><strong>Free tools</strong></p><p><a href="/tools/enablement-capacity-calculator/">Enablement capacity calculator</a></p><p><a href="/tools/cost-per-active-user-calculator/">Cost per active user calculator</a></p></div>
  </aside>
</div></div>
{related_html}"""
    graph = [{
        "@type": "Article", "@id": url + "#article", "headline": d["title"][:110], "description": d.get("description", ""),
        "abstract": answer, "url": url, "mainEntityOfPage": url, "datePublished": d["published"], "dateModified": d["updated"],
        "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}, "isPartOf": {"@id": WEB_ID}, "inLanguage": "en-US",
        "image": f"{SITE['url']}/og/{d['slug']}.png", "articleSection": d.get("category", ""), "wordCount": d["words"],
        "keywords": ", ".join([d.get("primary_query", "")] + (d.get("related_queries") or [])),
        "about": {"@type": "Thing", "name": d.get("primary_query", d["title"])},
        "citation": [s.get("url") for s in d.get("sources") or [] if s.get("url")],
    }, crumbs_node(crumbs)]
    if d.get("faqs"):
        graph.append(faq_node(d["faqs"], url))
    extra = f'<link rel="alternate" type="text/markdown" href="{d["path"].rstrip("/")}.md">\n'
    extra += f'<meta property="article:published_time" content="{d["published"]}"><meta property="article:modified_time" content="{d["updated"]}">\n'
    return page(d["path"], d["title"], d.get("description", ""), main, graph, og_image=f"/og/{d['slug']}.png", og_type="article",
                current="/guides/" if d["kind"] == "guide" else d["path"], extra_head=extra)


def fmt_date(s):
    try:
        return dt.datetime.strptime(s, "%Y-%m-%d").strftime("%-d %B %Y")
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


from pages import home_page, tools_pages, about_page, privacy_page, not_found_page, glossary_page, faq_page, guides_hub  # noqa: E402
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

    ctx = dict(SITE=SITE, page=page, card=card, esc=esc, crumbs_html=crumbs_html, crumbs_node=crumbs_node, faq_html=faq_html,
               faq_node=faq_node, inline_md=inline_md, ORG_ID=ORG_ID, WEB_ID=WEB_ID, by_slug=by_slug, guides=guides,
               FEATURED=FEATURED, CATEGORY_ORDER=CATEGORY_ORDER, CATEGORY_SLUG=CATEGORY_SLUG, glossary=glossary, faqs=faqs)

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
    write("/about/", about_page(ctx), priority=0.6)
    write("/privacy/", privacy_page(ctx), priority=0.2)
    write("/404.html", not_found_page(ctx), sitemap=False)

    site_files(guides, pages_, glossary, faqs)
    og.build_all(OUT, SITE, guides + pages_)
    print(f"Built {len(WRITTEN)} pages: {len(guides)} guides, {len(pages_)} pages, {len(glossary)} terms, {len(faqs)} FAQs")


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
    robots += "User-agent: *\nAllow: /\n\nSitemap: " + SITE["url"] + "/sitemap.xml\n"
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
