from __future__ import annotations

from typing import Any

from .crawler import fetch_page
from .page_content_extractor import extract_page_content
from .page_finder import find_pages, is_valid_link
from .page_classifier import classify_page
from .discovery import discover_internal_links
from ..pipelines.enrichment_pipeline import EnrichmentPipeline
from ..pipelines.validation_pipeline import ValidationPipeline


class BaseSpider:
    def __init__(self) -> None:
        self.enricher = EnrichmentPipeline()
        self.validator = ValidationPipeline()

    def crawl(self, url: str) -> dict[str, Any] | None:
        html = fetch_page(url)
        if html is None:
            return None
        return self.parse(url, html)

    def parse(self, url: str, html: str) -> dict[str, Any]:
        raise NotImplementedError("Subclasses must implement parse")

    def discover_additional_pages(self, url: str, html: str, missing: list[str]) -> dict[str, str]:
        section_pages = find_pages(url, html)
        for cat, page_url in section_pages.items():
            if not page_url or cat not in missing:
                continue
            if not is_valid_link(page_url):
                continue
            page_html = fetch_page(page_url)
            if not page_html:
                continue
            best_cat, conf = classify_page(page_url, page_html)
            if best_cat == cat and conf >= 0.35:
                section_pages[cat] = page_url
        if missing:
            discovered = discover_internal_links(url, max_depth=2, max_pages=200)
            for page_url in discovered:
                if not missing:
                    break
                page_html = fetch_page(page_url)
                if not page_html:
                    continue
                best_cat, conf = classify_page(page_url, page_html)
                if best_cat in missing and conf >= 0.45:
                    section_pages[best_cat] = page_url
                    missing.remove(best_cat)
        return section_pages
