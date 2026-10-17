"""Verify generated pages, links, metadata, and editorial separation."""

import json
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

SITES = {
    "alretaj.com": Path("D:/alretaj"),
    "bsmah.com": Path("D:/bsmah"),
    "orkeed.com": Path(__file__).resolve().parents[1],
}


def pages_for(root: Path) -> list[Path]:
    return [root / "index.html", *sorted((root / "blog").rglob("index.html"))]


def audit_site(domain: str, root: Path) -> tuple[int, dict[str, int]]:
    problems: list[str] = []
    outbound = {other: 0 for other in SITES if other != domain}
    pages = pages_for(root)
    titles: set[str] = set()
    for page in pages:
        relative = page.relative_to(root)
        route = "/" if relative == Path("index.html") else "/" + str(relative.parent).replace("\\", "/") + "/"
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        title = soup.title.get_text(strip=True) if soup.title else ""
        if not title or title in titles:
            problems.append(f"{relative}: missing or duplicate title")
        titles.add(title)
        if len(soup.find_all("h1")) != 1:
            problems.append(f"{relative}: expected one h1")
        if soup.html.get("lang") != "ar" or soup.html.get("dir") != "rtl":
            problems.append(f"{relative}: missing Arabic/RTL markers")
        canonical = soup.find("link", rel="canonical")
        if canonical is None or canonical.get("href") != f"https://{domain}{route}":
            problems.append(f"{relative}: wrong canonical")
        if not soup.find("meta", attrs={"name": "description"}):
            problems.append(f"{relative}: missing description")
        for block in soup.find_all("script", type="application/ld+json"):
            try:
                json.loads(block.string or "")
            except json.JSONDecodeError:
                problems.append(f"{relative}: invalid JSON-LD")
        for tag in soup.find_all(["a", "img", "script", "link"]):
            attr = "href" if tag.name in {"a", "link"} else "src"
            url = tag.get(attr, "")
            for other in outbound:
                if tag.name == "a" and url.startswith(f"https://{other}/"):
                    outbound[other] += 1
            if not url.startswith("/") or url.startswith("//"):
                continue
            target = root / unquote(urlparse(url).path).lstrip("/")
            if target.is_dir():
                target /= "index.html"
            if not target.is_file():
                problems.append(f"{relative}: missing local target {url}")
        for img in soup.find_all("img", srcset=True):
            for candidate in img["srcset"].split(","):
                url = candidate.strip().split(" ")[0]
                if url.startswith("/") and not (root / url.lstrip("/")).is_file():
                    problems.append(f"{relative}: missing srcset image {url}")
    if problems:
        raise AssertionError("\n".join(problems))
    return len(pages), outbound


def compare_posts() -> tuple[int, float]:
    collections = {
        domain: {post["slug"]: post for post in json.loads((root / "content/posts.json").read_text(encoding="utf-8"))}
        for domain, root in SITES.items()
    }
    slugs = set(next(iter(collections.values())))
    assert len(slugs) == 16 and all(set(posts) == slugs for posts in collections.values())
    max_ratio = 0.0
    for slug in slugs:
        titles = [posts[slug]["title"] for posts in collections.values()]
        assert len(set(titles)) == len(titles), f"duplicate article title: {slug}"
        bodies = [" ".join(p["intro"] + [text for s in p["sections"] for text in s["paragraphs"]] + [p["takeaway"]]) for posts in collections.values() for p in [posts[slug]]]
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                max_ratio = max(max_ratio, SequenceMatcher(None, bodies[i], bodies[j]).ratio())
    return len(slugs), max_ratio


if __name__ == "__main__":
    counts = {domain: audit_site(domain, root) for domain, root in SITES.items()}
    articles, max_similarity = compare_posts()
    assert counts["orkeed.com"][1] == {"alretaj.com": 1, "bsmah.com": 2}
    assert counts["alretaj.com"][1]["orkeed.com"] == 1
    assert counts["bsmah.com"][1]["orkeed.com"] == 1
    for domain, (page_count, links) in counts.items():
        print(f"{domain}: {page_count} pages, editorial links {links}")
    print(f"Shared article subjects: {articles}; highest pairwise body similarity: {max_similarity:.2%}")
