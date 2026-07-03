"""Scraper to collect college URLs from shiksha.com directory."""
import logging
import re

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)

# Shiksha.com college listing pages by category
SHIKSHA_LISTING_URLS = [
    "https://www.shiksha.com/colleges/list-of-engineering-colleges",
    "https://www.shiksha.com/colleges/list-of-management-colleges",
    "https://www.shiksha.com/colleges/list-of-medical-colleges",
    "https://www.shiksha.com/colleges/list-of-law-colleges",
    "https://www.shiksha.com/colleges/list-of-arts-colleges",
    "https://www.shiksha.com/colleges/list-of-science-colleges",
]

SHIKSHA_BASE = "https://www.shiksha.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_page(url: str, timeout: int = 10) -> str:
    """Fetch page content with retry logic."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as error:
        LOGGER.error("Error fetching %s: %s", url, error)
        return ""


def extract_college_urls_from_listing(html: str) -> set[str]:
    """Extract college profile URLs from listing page."""
    urls: set[str] = set()
    
    try:
        soup = BeautifulSoup(html, "html.parser")
        
        # Look for college links in various formats
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            
            # Match shiksha.com college profile URLs
            if "/college/" in href and "shiksha.com" in href:
                # Make URL absolute
                if href.startswith("/"):
                    href = SHIKSHA_BASE + href
                if href.startswith("http"):
                    urls.add(href)
            elif "/college/" in href and not href.startswith("http"):
                # Relative URL
                full_url = SHIKSHA_BASE + href
                urls.add(full_url)
    
    except Exception as error:
        LOGGER.error("Error parsing listing page: %s", error)
    
    return urls


def collect_shiksha_college_urls(max_urls: int = 100) -> list[str]:
    """Collect college URLs from shiksha.com directories."""
    all_urls: set[str] = set()
    
    for listing_url in SHIKSHA_LISTING_URLS:
        if len(all_urls) >= max_urls:
            break
        
        LOGGER.info("Fetching listing: %s", listing_url)
        html = fetch_page(listing_url)
        
        if html:
            urls = extract_college_urls_from_listing(html)
            all_urls.update(urls)
            LOGGER.info("Found %d college URLs from %s", len(urls), listing_url)
    
    # Remove duplicates and limit
    unique_urls = list(all_urls)[:max_urls]
    LOGGER.info("Total unique college URLs collected: %d", len(unique_urls))
    
    return sorted(unique_urls)


def append_to_urls_file(urls: list[str], output_file: str) -> None:
    """Append URLs to existing URL file."""
    if not urls:
        LOGGER.warning("No URLs to append")
        return
    
    try:
        # Read existing URLs
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing = set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            existing = set()
        
        # Add new URLs
        existing.update(urls)
        
        # Write back
        with open(output_file, "w", encoding="utf-8") as f:
            for url in sorted(existing):
                f.write(url + "\n")
        
        LOGGER.info("Appended %d unique URLs to %s", len(urls), output_file)
    
    except Exception as error:
        LOGGER.error("Error writing to %s: %s", output_file, error)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    
    print("Collecting shiksha.com college URLs...")
    college_urls = collect_shiksha_college_urls(max_urls=50)
    
    if college_urls:
        print(f"Found {len(college_urls)} colleges:")
        for url in college_urls[:10]:
            print(f"  {url}")
        if len(college_urls) > 10:
            print(f"  ... and {len(college_urls) - 10} more")
        
        # Append to URL list
        append_to_urls_file(college_urls, "urls/colleges.txt")
        print(f"Appended to urls/colleges.txt")
    else:
        print("No URLs collected")
