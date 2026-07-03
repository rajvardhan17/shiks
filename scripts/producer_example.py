from __future__ import annotations

import hashlib
import os
import sys
from datetime import datetime
from time import sleep

from scrapers import crawler, extractor
from scrapers.saver_postgres import map_and_save


URL_FILE = os.path.join(os.path.dirname(__file__), "..", "temp_urls.txt")


def checksum_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def process_url(url: str) -> None:
    try:
        html = crawler.fetch_page(url)
    except Exception as exc:
        print(f"Failed to fetch {url}: {exc}")
        return

    extracted = extractor.extract_data(url, html)
    extracted["checksum"] = checksum_text(html)
    extracted["fetched_at"] = datetime.utcnow().isoformat()
    extracted["status"] = "fetched"

    try:
        map_and_save(extracted)
        print(f"Saved: {url}")
    except Exception as exc:
        print(f"Failed to save {url}: {exc}")


def main():
    if not os.path.exists(URL_FILE):
        print(f"URL file not found: {URL_FILE}")
        sys.exit(1)

    with open(URL_FILE, "r", encoding="utf-8") as fh:
        urls = [line.strip() for line in fh if line.strip()]

    for url in urls:
        process_url(url)
        # be polite between requests; in production replace with rate limiter
        sleep(1)


if __name__ == "__main__":
    main()
