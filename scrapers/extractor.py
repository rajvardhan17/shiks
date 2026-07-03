from __future__ import annotations

import json
from urllib.parse import urljoin
from typing import Any

from bs4 import BeautifulSoup

from scrapers.page_finder import find_pages, is_valid_link
from scrapers.page_content_extractor import extract_page_content
from extractors.structured import extract_structured_facts


def _extract_meta(soup: BeautifulSoup) -> dict[str, str]:
    meta: dict[str, str] = {}

    # title / description / keywords
    if soup.title and soup.title.string:
        meta["title"] = soup.title.string.strip()

    desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    if desc and desc.get("content"):
        meta["description"] = desc["content"].strip()

    keywords = soup.find("meta", attrs={"name": "keywords"})
    if keywords and keywords.get("content"):
        meta["keywords"] = keywords["content"].strip()

    # canonical
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        meta["canonical"] = canonical["href"].strip()

    # OpenGraph / Twitter cards
    for tag in soup.find_all("meta"):
        if tag.get("property") and tag.get("content"):
            prop = tag["property"].strip()
            if prop.startswith("og:") or prop.startswith("twitter:"):
                meta[prop] = tag["content"].strip()

    return meta


def _extract_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    links: list[str] = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full = urljoin(base_url, href)
        try:
            if is_valid_link(full):
                links.append(full)
        except Exception:
            # Be permissive: include raw resolved link on unexpected errors
            links.append(full)

    # Deduplicate while preserving order
    seen = set()
    deduped: list[str] = []
    for u in links:
        if u not in seen:
            seen.add(u)
            deduped.append(u)
    return deduped


def _extract_images(soup: BeautifulSoup, base_url: str) -> list[dict[str, str]]:
    images: list[dict[str, str]] = []

    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        src = urljoin(base_url, src.strip())
        images.append({"src": src, "alt": (img.get("alt") or "").strip()})

    return images


def _extract_jsonld(soup: BeautifulSoup) -> list[Any]:
    items: list[Any] = []

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            text = script.string
            if not text:
                continue
            parsed = json.loads(text)
            items.append(parsed)
        except Exception:
            # ignore invalid JSON-LD
            continue

    return items


def extract_data(url: str, html: str) -> dict[str, Any]:
    """Return a comprehensive extraction for one page.

    Includes: page content, meta, links, images, JSON-LD, the keyword-based
    category pages and the derived structured facts used elsewhere.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Basic page-level content
    page_content = extract_page_content(html)

    # Use the page title (or page_content title) as a starting college name
    title = (soup.title.string.strip() if soup.title and soup.title.string else page_content.get("page_title", "") or "Unknown")

    # Keyword-based category page discovery (kept for backwards compatibility)
    pages = find_pages(url, html)

    # Build a page_record similar to what structured.extract_structured_facts expects
    page_record = {
        "college_name": title,
        "website": url,
        "page_url": url,
        **page_content,
        **pages,
        "status": "",
        "error": "",
    }

    structured = extract_structured_facts(page_record)

    return {
        "college_name": title,
        "website": url,
        "page_url": url,
        "page": page_content,
        "meta": _extract_meta(soup),
        "links": _extract_links(soup, url),
        "images": _extract_images(soup, url),
        "json_ld": _extract_jsonld(soup),
        "keyword_pages": pages,
        "structured_facts": structured,
        **pages,
    }
