"""Render "rich" blog entries (written by the EMPID SEO studio) as HTML.

Pure functions used by build_blog.py for posts.json entries with "rich": true.
The contract is docs/seo-article-format.md in the EMPID publisher app.
The same file is copied into every site so rich pages render the same way.
"""

from __future__ import annotations

import html
import re


RICH_HEAD = '<link rel="stylesheet" href="/assets/rich.css">\n  <script src="/assets/rich.js" defer></script>'
TOKEN = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)|\*\*(.+?)\*\*")
PLAIN_LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")
PLAIN_BOLD = re.compile(r"\*\*(.+?)\*\*")
CALLOUT_LABELS = {"tip": "نصيحة", "warning": "تنبيه", "note": "ملاحظة"}
EMPID_APP = {
    "@type": "SoftwareApplication",
    "name": "EMPID",
    "applicationCategory": "BusinessApplication",
    "operatingSystem": "Web",
    "url": "https://www.empid.com/",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def safe_url(url: str) -> str:
    """Return the URL when it is a /blog/ path or an https:// address, else ""."""
    url = str(url or "").strip()
    if url.startswith("/blog/") or (url.startswith("https://") and len(url) > 8):
        if not any(ch.isspace() or ch in "<>\"'`" for ch in url):
            return url
    return ""


def image_url(url: str) -> str:
    """Images may be root-relative (/assets/...) or https://."""
    url = str(url or "").strip()
    if url.startswith("/") and not url.startswith("//"):
        return "" if any(ch.isspace() or ch in "<>\"'`" for ch in url) else url
    return safe_url(url) if url.startswith("https://") else ""


# ---------- inline markup ----------

def _inline_escaped(text: str) -> str:
    def repl(match: re.Match) -> str:
        if match.group(1) is not None:
            anchor = _inline_escaped(match.group(1))
            url = match.group(2)
            if any(bad in url for bad in ("&quot;", "&#x27;", "&lt;", "&gt;", "`")):
                return anchor
            if url.startswith("/blog/"):
                return f'<a href="{url}">{anchor}</a>'
            if url.startswith("https://") and len(url) > 8:
                return f'<a href="{url}" rel="noopener">{anchor}</a>'
            return anchor
        return f"<strong>{_inline_escaped(match.group(3))}</strong>"

    return TOKEN.sub(repl, text)


def inline(text: object) -> str:
    """Escape text, then render **bold** and [anchor](url) (only /blog/... and https:// links)."""
    return _inline_escaped(esc(text or ""))


def plain(text: object) -> str:
    """Inline markup reduced to plain text (for schema and word counts)."""
    text = PLAIN_LINK.sub(lambda m: m.group(1), str(text or ""))
    return PLAIN_BOLD.sub(lambda m: m.group(1), text)


def paragraphs(items: list | None) -> str:
    return "\n".join(f"<p>{inline(p)}</p>" for p in items or [])


def bullets(items: list | None) -> str:
    if not items:
        return ""
    return "<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>"


# ---------- figures ----------

def _number(value: object, default: float, low: float, high: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return min(high, max(low, number))


def render_figure(fig: dict, eager: bool = False, compact: bool = False) -> str:
    src = image_url(fig.get("src", ""))
    if not src:
        return ""
    width = int(_number(fig.get("width"), 1200, 1, 10000))
    height = int(_number(fig.get("height"), 675, 1, 10000))
    alt = fig.get("alt", "")
    hotspot = ""
    note = ""
    spot = fig.get("hotspot")
    if isinstance(spot, dict) and spot.get("label"):
        x = _number(spot.get("x"), 50, 0, 100)
        y = _number(spot.get("y"), 50, 0, 100)
        hotspot = f'<span class="rich-hotspot" style="left:{x:g}%;top:{y:g}%" role="img" aria-label="{esc(spot["label"])}"></span>'
        note = f'<span class="rich-hotspot-note" aria-hidden="true"><i></i>{esc(spot["label"])}</span>'
    caption = ""
    if fig.get("caption") or note:
        caption = f"<figcaption>{note}{esc(fig.get('caption', ''))}</figcaption>"
    image = (
        f'<a href="{esc(src)}" data-lightbox aria-label="تكبير الصورة: {esc(alt)}">'
        f'<img src="{esc(src)}" alt="{esc(alt)}" width="{width}" height="{height}" loading="{"eager" if eager else "lazy"}" decoding="async"></a>'
    )
    size = " rich-figure--compact" if compact else ""
    if fig.get("kind") == "screenshot":
        label = esc(fig.get("label") or "لقطة شاشة")
        return (
            f'<figure class="rich-figure rich-figure--screenshot{size}">'
            f'<div class="rich-shot-top"><span class="rich-shot-dots" aria-hidden="true"><i></i><i></i><i></i></span>{label}</div>'
            f'<div class="rich-figure-frame">{image}{hotspot}</div>{caption}</figure>'
        )
    return f'<figure class="rich-figure rich-figure--photo{size}"><div class="rich-figure-frame">{image}{hotspot}</div>{caption}</figure>'


# ---------- blocks ----------

def _title(block: dict) -> str:
    return f'<h3 class="rich-block-title">{esc(block["title"])}</h3>' if block.get("title") else ""


def render_steps(block: dict, figures_by_id: dict, first: list) -> str:
    items = []
    for number, step in enumerate(block.get("steps", []), 1):
        fig = figures_by_id.get(step.get("figure")) if step.get("figure") else None
        fig_html = _figure_once(fig, first, compact=True) if fig else ""
        title = f'<h4>{esc(step["title"])}</h4>' if step.get("title") else ""
        text = f"<p>{inline(step['text'])}</p>" if step.get("text") else ""
        items.append(f'<li class="rich-step rich-reveal"><span class="rich-step-num" aria-hidden="true">{number}</span><div class="rich-step-body">{title}{text}{fig_html}</div></li>')
    return f'<div class="rich-block rich-steps">{_title(block)}<ol class="rich-steps-list">{"".join(items)}</ol></div>'


def render_flow(block: dict) -> str:
    nodes = "".join(
        f'<li class="rich-flow-node rich-reveal"><strong>{esc(node.get("label", ""))}</strong>'
        + (f'<span>{esc(node["note"])}</span>' if node.get("note") else "")
        + "</li>"
        for node in block.get("nodes", [])
    )
    return f'<div class="rich-block rich-flow">{_title(block)}<div class="rich-flow-scroll"><ol class="rich-flow-track">{nodes}</ol></div></div>'


def render_callout(block: dict) -> str:
    tone = block.get("tone") if block.get("tone") in CALLOUT_LABELS else "note"
    title = f'<strong>{esc(block["title"])}</strong>' if block.get("title") else ""
    text = f"<p>{inline(block['text'])}</p>" if block.get("text") else ""
    return (
        f'<aside class="rich-callout rich-callout--{tone}" role="note">'
        f'<p class="rich-callout-head"><span class="rich-callout-icon" aria-hidden="true"></span><span class="rich-callout-kind">{CALLOUT_LABELS[tone]}</span>{title}</p>{text}</aside>'
    )


def render_checklist(block: dict) -> str:
    items = "".join(
        f'<li class="rich-reveal"><label><input type="checkbox" data-rich-check><span>{inline(item)}</span></label></li>'
        for item in block.get("items", [])
    )
    return f'<div class="rich-block rich-checklist">{_title(block)}<ul class="rich-checklist-list">{items}</ul></div>'


def _compare_column(side: dict, kind: str, fallback: str) -> str:
    items = "".join(f"<li>{inline(item)}</li>" for item in side.get("items", []))
    return f'<div class="rich-compare-col rich-compare-{kind}"><h4>{esc(side.get("label") or fallback)}</h4><ul>{items}</ul></div>'


def render_compare(block: dict) -> str:
    before = _compare_column(block.get("before") or {}, "before", "قبل")
    after = _compare_column(block.get("after") or {}, "after", "بعد")
    return f'<div class="rich-block rich-compare">{_title(block)}<div class="rich-compare-grid">{before}{after}</div></div>'


def render_timeline(block: dict) -> str:
    items = "".join(
        f'<li class="rich-reveal"><span class="rich-timeline-when">{esc(item.get("when", ""))}</span><p>{inline(item.get("text", ""))}</p></li>'
        for item in block.get("items", [])
    )
    return f'<div class="rich-block rich-timeline">{_title(block)}<ol class="rich-timeline-list">{items}</ol></div>'


def render_gallery(block: dict, figures_by_id: dict, first: list) -> str:
    figures = "".join(_figure_once(figures_by_id[fid], first, compact=True) for fid in block.get("figures", []) if fid in figures_by_id)
    if not figures:
        return ""
    return f'<div class="rich-block rich-gallery">{_title(block)}<div class="rich-gallery-grid">{figures}</div></div>'


def render_block(block: dict, figures_by_id: dict, first: list) -> str:
    kind = block.get("type")
    if kind == "steps":
        return render_steps(block, figures_by_id, first)
    if kind == "flow":
        return render_flow(block)
    if kind == "callout":
        return render_callout(block)
    if kind == "checklist":
        return render_checklist(block)
    if kind == "compare":
        return render_compare(block)
    if kind == "timeline":
        return render_timeline(block)
    if kind == "gallery":
        return render_gallery(block, figures_by_id, first)
    return ""


def render_table(table: dict) -> str:
    head = "".join(f'<th scope="col">{esc(h)}</th>' for h in table.get("headers", []))
    rows = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>" for row in table.get("rows", []))
    caption = f"<caption>{esc(table['caption'])}</caption>" if table.get("caption") else ""
    return f'<div class="article-table-wrap" tabindex="0" role="region" aria-label="{esc(table.get("caption") or "جدول")}"><table class="article-table">{caption}<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def _figure_once(fig: dict | None, first: list, compact: bool = False) -> str:
    """Render a figure; only the first figure of the article loads eagerly."""
    if not fig or not fig.get("src"):
        return ""
    eager = first[0]
    first[0] = False
    return render_figure(fig, eager=eager, compact=compact)


# ---------- sections ----------

def render_section(section: dict, index: int, figures_by_id: dict, first: list | None = None) -> str:
    """H2 → paragraphs → figure → bullets → subsections (H3) → blocks → table."""
    if first is None:
        first = [index == 1]
    parts = [f'<section id="section-{index}"><h2>{esc(section["heading"])}</h2>', paragraphs(section.get("paragraphs"))]
    if section.get("figure"):
        parts.append(_figure_once(figures_by_id.get(section["figure"]), first))
    parts.append(bullets(section.get("bullets")))
    for sub in section.get("subsections", []):
        parts.append(f'<div class="rich-subsection"><h3>{esc(sub.get("heading", ""))}</h3>{paragraphs(sub.get("paragraphs"))}{bullets(sub.get("bullets"))}</div>')
    parts += [render_block(block, figures_by_id, first) for block in section.get("blocks", [])]
    if section.get("table"):
        parts.append(render_table(section["table"]))
    parts.append("</section>")
    return "".join(parts)


def render_sections(post: dict) -> str:
    figures_by_id = {f["id"]: f for f in post.get("figures", []) if f.get("id")}
    first = [True]
    return "".join(render_section(section, index, figures_by_id, first) for index, section in enumerate(post.get("sections", []), 1))


# ---------- article parts ----------

def render_answer(post: dict) -> str:
    if not post.get("answer"):
        return ""
    return f'<div class="answer-box" id="short-answer"><strong>الإجابة المختصرة</strong><p>{inline(post["answer"])}</p></div>'


def render_faq(post: dict) -> str:
    if not post.get("faq"):
        return ""
    items = "".join(f'<h3>{esc(f["q"])}</h3><p>{inline(f["a"])}</p>' for f in post["faq"])
    return f'<section id="faq"><h2>أسئلة شائعة</h2><div class="faq-list">{items}</div></section>'


def render_sources(post: dict) -> str:
    if not post.get("sources"):
        return ""
    items = []
    for src in post["sources"]:
        url = safe_url(src.get("url", ""))
        if url.startswith("https://"):
            items.append(f'<li><a href="{esc(url)}" rel="noopener" target="_blank">{esc(src.get("title") or url)}</a></li>')
        else:
            items.append(f'<li>{esc(src.get("title", ""))}</li>')
    return (
        '<aside class="sources"><h2>مصادر ومراجع</h2><ul>' + "".join(items) + "</ul>"
        "<p>المعلومات في هذا المقال عامة وليست استشارة قانونية. الأنظمة تتغير، فراجع الجهة الرسمية في بلدك قبل التطبيق.</p></aside>"
    )


def render_link_out(post: dict) -> str:
    link = post.get("link_out") or {}
    url = safe_url(link.get("url", ""))
    if not url or not link.get("title"):
        return ""
    rel = ' rel="noopener"' if url.startswith("https://") else ""
    label = f"قراءة مرتبطة من {esc(link['site_name'])}" if link.get("site_name") else "قراءة مرتبطة"
    note = f"<p>{esc(link['note'])}</p>" if link.get("note") else ""
    return f'<aside class="external-reading"><span>{label}</span><a href="{esc(url)}"{rel}>{esc(link["title"])} ←</a>{note}</aside>'


def keywords_meta(post: dict) -> str:
    if not post.get("keywords"):
        return ""
    return f'<meta name="keywords" content="{esc("، ".join(post["keywords"]))}">'


def add_head(head: str, post: dict, keywords: bool = True) -> str:
    """Add rich.css, rich.js (and the keywords meta) right after the site stylesheet."""
    extra = RICH_HEAD
    if keywords and post.get("keywords"):
        extra = keywords_meta(post) + "\n  " + extra
    anchor = '<link rel="stylesheet" href="/styles.css">'
    return head.replace(anchor, anchor + "\n  " + extra, 1)


# ---------- schema ----------

def block_text(block: dict) -> list[str]:
    parts = [block.get("title", ""), block.get("text", "")]
    for step in block.get("steps", []):
        parts += [step.get("title", ""), step.get("text", "")]
    for node in block.get("nodes", []):
        parts += [node.get("label", ""), node.get("note", "")]
    for item in block.get("items", []):
        parts += [item.get("when", ""), item.get("text", "")] if isinstance(item, dict) else [item]
    for side in (block.get("before"), block.get("after")):
        if side:
            parts += [side.get("label", "")] + list(side.get("items", []))
    return parts


def word_count(post: dict) -> int:
    parts = list(post.get("intro", [])) + [post.get("answer", "")]
    for sec in post.get("sections", []):
        parts += [sec.get("heading", "")] + sec.get("paragraphs", []) + sec.get("bullets", [])
        for sub in sec.get("subsections", []):
            parts += [sub.get("heading", "")] + sub.get("paragraphs", []) + sub.get("bullets", [])
        for block in sec.get("blocks", []):
            parts += block_text(block)
        table = sec.get("table")
        if table:
            parts += list(table.get("headers", [])) + [c for row in table.get("rows", []) for c in row]
    parts += [f'{f["q"]} {f["a"]}' for f in post.get("faq", [])]
    parts += [post.get("takeaway_title", ""), post.get("takeaway", "")]
    return sum(len(plain(part).split()) for part in parts)


def article_schema(post: dict, site: str, brand: str, logo_url: str, blog_name: str) -> dict:
    path = f"/blog/{post['slug']}/"
    preview = post.get("featured")
    posting = {
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": post["summary"],
        "mainEntityOfPage": f"{site}{path}",
        "url": f"{site}{path}",
        "inLanguage": "ar",
        "author": {"@type": "Organization", "name": brand, "url": f"{site}/"},
        "publisher": {"@type": "Organization", "name": brand, "logo": {"@type": "ImageObject", "url": logo_url}},
        **({"image": f"{site}{preview['src']}" if preview["src"].startswith("/") else preview["src"]} if preview else {}),
        **({"datePublished": post["published"], "dateModified": post.get("updated") or post["published"]} if post.get("published") else {}),
        **({"keywords": post["keywords"]} if post.get("keywords") else {}),
        "wordCount": word_count(post),
        "articleSection": post["category"],
        **({"about": EMPID_APP} if post.get("about_empid") else {}),
        "isPartOf": {"@type": "Blog", "name": blog_name, "url": f"{site}/blog/"},
    }
    graph = [
        posting,
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": f"{site}/"},
                {"@type": "ListItem", "position": 2, "name": "المدونة", "item": f"{site}/blog/"},
                {"@type": "ListItem", "position": 3, "name": post["title"], "item": f"{site}{path}"},
            ],
        },
    ]
    if post.get("faq"):
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": plain(f["a"])}}
                for f in post["faq"]
            ],
        })
    return {"@context": "https://schema.org", "@graph": graph}
