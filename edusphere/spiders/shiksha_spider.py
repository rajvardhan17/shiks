from __future__ import annotations

from typing import Any
from bs4 import BeautifulSoup

from .base_spider import BaseSpider
from .page_content_extractor import extract_page_content
from .page_finder import find_pages
from .page_classifier import classify_page
from .discovery import discover_internal_links
from ..parsers.established_year_parser import parse_established_year
from ..items.internal_links import InternalLinksItem


class ShikshaSpider(BaseSpider):
    def parse(self, url: str, html: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")
        page_title = soup.title.get_text(" ", strip=True) if soup.title else None
        body_text = " ".join(soup.stripped_strings)

        established_year = parse_established_year(body_text)

        internal_links = self._extract_internal_links(soup, url)

        payload = {
            "college_id": url,
            "basic_information": {
                "college_name": page_title,
                "official_name": page_title,
                "short_name": None,
                "college_type": None,
                "ownership": None,
                "university": None,
                "affiliated_university": None,
                "approved_by": None,
                "accreditation": None,
                "established_year": established_year,
                "campus_area": None,
                "official_website": url,
                "logo_url": None,
                "banner_image_url": None,
                "about_college": None,
                "highlights": None,
            },
            "location_details": {},
            "contact_information": {
                "admission_email": None,
                "general_email": None,
                "phone_numbers": [],
                "email_addresses": [],
                "whatsapp_number": None,
                "admission_helpline": None,
                "fax": None,
                "principal_director_name": None,
                "social_media_links": {},
                "city": None,
                "state": None,
                "country": None,
                "address": None,
                "pin_code": None,
            },
            "admission_information": {},
            "courses": [],
            "specializations": [],
            "fees": [],
            "cutoffs": [],
            "placements": {},
            "recruiters": [],
            "faculty": [],
            "infrastructure": {},
            "hostel": [],
            "scholarships": [],
            "rankings": [],
            "reviews": [],
            "gallery": [],
            "downloads": [],
            "news": [],
            "events": [],
            "faqs": [],
            "alumni": [],
            "documents": [],
            "compare_parameters": {},
            "internal_links": internal_links,
            "page_metadata": {
                "url": url,
                "page_title": page_title,
                "source": "shiksha",
            },
            "raw_content": {
                "raw_html": html,
                "clean_text": body_text[:10000],
                "markdown": None,
                "tables": [],
                "headings": [],
                "faq_content": [],
                "json_ld": [],
                "schema_org_markup": {},
            },
        }

        return self.enricher.enrich_payload(payload)

    def _extract_internal_links(self, soup, base_url: str) -> dict[str, str]:
        links: dict[str, str] = {}
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            if not href:
                continue
            absolute_url = href if href.startswith("http") else base_url.rstrip("/") + "/" + href.lstrip("/")
            label = " ".join(anchor.stripped_strings).lower()
            if "course" in label or "/courses" in absolute_url:
                links["courses"] = absolute_url
            elif "fee" in label or "/fees" in absolute_url:
                links["fees"] = absolute_url
            elif "admission" in label or "/admissions" in absolute_url:
                links["admissions"] = absolute_url
            elif "placement" in label or "/placements" in absolute_url:
                links["placements"] = absolute_url
            elif "contact" in label or "/contact" in absolute_url:
                links["contact"] = absolute_url
            elif "faculty" in label or "/faculty" in absolute_url:
                links["faculty"] = absolute_url
            elif "hostel" in label or "/hostel" in absolute_url:
                links["hostel"] = absolute_url
            elif "department" in label or "/departments" in absolute_url:
                links["departments"] = absolute_url
            elif "download" in label or "/downloads" in absolute_url:
                links["downloads"] = absolute_url
        return links
