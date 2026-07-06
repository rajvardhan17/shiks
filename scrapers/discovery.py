from __future__ import annotations

from typing import Set, Iterable
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup

from scrapers.crawler import fetch_page
from scrapers.page_finder import is_valid_link


def _same_domain(base: str, url: str) -> bool:
    try:
        base_host = urlparse(base).netloc.removeprefix("www.")
        url_host = urlparse(url).netloc.removeprefix("www.")
        return base_host == url_host
    except Exception:
        return False


def parse_sitemap(base_url: str) -> Set[str]:
    """Attempt to fetch sitemap.xml and return listed URLs on same domain."""
    candidates = set()
    for path in ("/sitemap.xml", "/sitemap_index.xml"):
        sitemap_url = urljoin(base_url, path)
        html = fetch_page(sitemap_url)
        if not html:
            continue
        # parse <loc> tags
        soup = BeautifulSoup(html, "xml")
        for loc in soup.find_all("loc"):
            href = loc.string.strip() if loc.string else None
            if href and _same_domain(base_url, href) and is_valid_link(href):
                candidates.add(href)
    return candidates


def discover_internal_links(base_url: str, max_depth: int = 2, max_pages: int = 200) -> Set[str]:
    """BFS crawl collecting internal page URLs up to max_depth (inclusive).

    Returns a set of discovered URLs including the base_url.
    """
    discovered: Set[str] = set()
    frontier: Set[str] = {base_url}

    # seed with sitemap if available
    try:
        sitemap_urls = parse_sitemap(base_url)
        frontier.update(sitemap_urls)
    except Exception:
        pass

    for depth in range(max_depth + 1):
        if not frontier or len(discovered) >= max_pages:
            break
        next_frontier: Set[str] = set()
        for url in list(frontier):
            if url in discovered:
                continue
            if len(discovered) >= max_pages:
                break
            html = fetch_page(url)
            discovered.add(url)
            if not html:
                continue
            try:
                soup = BeautifulSoup(html, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = urljoin(url, a["href"].strip())
                    if not is_valid_link(href):
                        continue
                    if not _same_domain(base_url, href):
                        continue
                    if href not in discovered:
                        next_frontier.add(href)
            except Exception:
                continue
        frontier = next_frontier

    return discovered
