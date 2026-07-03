from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from pipeline.validators import normalize_and_validate_payload


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

    def enqueue(self, urls: list[str]) -> None:
        self.urls.extend(urls)

    def dequeue(self) -> list[str] | None:
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
        self.queue.enqueue(seed_urls)
        discovered_urls = self.discovery_service.discover(seed_urls)
        self.queue.enqueue(discovered_urls)

        results: list[dict[str, Any]] = []
        while True:
            next_url = self.queue.dequeue()
            if next_url is None:
                break
            html = self.crawler.crawl(next_url)
            extracted = self.extractor.extract(next_url, html)
            normalized = normalize_and_validate_payload(extracted)
            results.append(normalized)

        return results
