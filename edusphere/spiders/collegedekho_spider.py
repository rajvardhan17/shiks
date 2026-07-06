from __future__ import annotations

from .shiksha_spider import ShikshaSpider


class CollegeDekhoSpider(ShikshaSpider):
    def parse(self, url: str, html: str) -> dict[str, any]:
        payload = super().parse(url, html)
        payload["page_metadata"]["source"] = "collegedekho"
        return payload
