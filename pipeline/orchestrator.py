from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol
import logging

from pipeline.validators import normalize_and_validate_payload

LOGGER = logging.getLogger(__name__)


class DiscoveryService(Protocol):
    def discover(self, seed_urls: list[str]) -> list[str]:
        ...


class Crawler(Protocol):
    def crawl(self, url: str) -> str:
        ...


class Extractor(Protocol):
    def extract(self, url: str, html: str) -> dict[str, Any]:
        ...


@dataclass
class InMemoryCrawlQueue:
    urls: list[str] = field(default_factory=list)

    def enqueue(self, urls: list[str] | str) -> None:
        """Enqueue a list of URLs or a single URL string."""
        if isinstance(urls, str):
            self.urls.append(urls)
        else:
            self.urls.extend(urls)
    def dequeue(self) -> str | None:
        if not self.urls:
            return None
        item = self.urls.pop(0)
        return item


class CollegeDiscoveryPipeline:
    def __init__(
        self,
        discovery_service: DiscoveryService,
        crawler: Crawler,
        extractor: Extractor,
        queue: InMemoryCrawlQueue | None = None,
    ) -> None:
        self.discovery_service = discovery_service
        self.crawler = crawler
        self.extractor = extractor
        self.queue = queue or InMemoryCrawlQueue()

    def run(self, seed_urls: list[str]) -> list[dict[str, Any]]:
        # Seed the queue
        self.queue.enqueue(seed_urls)

        # Discover additional URLs (best-effort)
        try:
            discovered_urls = self.discovery_service.discover(seed_urls) or []
            self.queue.enqueue(discovered_urls)
        except Exception as exc:
            LOGGER.warning("Discovery service failed: %s", exc)

        results: list[dict[str, Any]] = []
        while True:
            next_url = self.queue.dequeue()
            if next_url is None:
                break

            try:
                html = self.crawler.crawl(next_url)
                if html is None:
                    LOGGER.warning("No HTML returned for %s; skipping", next_url)
                    continue

                extracted = self.extractor.extract(next_url, html)
                normalized = normalize_and_validate_payload(extracted)
                results.append(normalized)
            except Exception as exc:
                LOGGER.error("Pipeline processing failed for %s: %s", next_url, exc)
                continue

        return results
