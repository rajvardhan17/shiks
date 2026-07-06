import json
import logging
import os
import re
from pathlib import Path

from scrapers.aggregator import build_college_payload
from scrapers.crawler import fetch_page
from scrapers.extractor import extract_data
from scrapers.page_content_extractor import extract_page_content
from scrapers.page_finder import is_valid_link, find_pages
from scrapers.discovery import discover_internal_links
from scrapers.page_classifier import classify_page
from scrapers.saver import save_to_csv
from extractors import extract_structured_facts
from extractors.common import parse_course_detail_text

LOGGER = logging.getLogger(__name__)
CONTENT_CATEGORIES = (
    "admissions",
    "courses",
    "placements",
    "fees",
    "contact",
    "scholarships",
    "faculty",
    "hostel",
    "infrastructure",
    "rankings",
    "reviews",
    "gallery",
    "downloads",
    "news",
    "alumni",
)


def load_urls(urls_file: str) -> list[str]:
    if not os.path.exists(urls_file):
        return []
    lines = Path(urls_file).read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip()]


def failed_record(url: str, error: Exception) -> dict[str, str]:
    return {
        "college_name": "Unknown",
        "website": url,
        "status": "failed",
        "error": str(error),
    }


def failed_page_content_record(college_name: str, website: str, category: str, page_url: str, error: Exception) -> dict[str, str]:
    return {
        "college_name": college_name,
        "website": website,
        "category": category,
        "page_url": page_url,
        "page_title": "",
        "headings": "",
        "content": "",
        "table_content": "",
        "status": "failed",
        "error": str(error),
    }


def fetch_cached_page(url: str, cache: dict[str, str]) -> str:
    if url in cache:
        return cache[url]
    html = fetch_page(url)
    if html is None:
        raise RuntimeError(f"Failed to fetch page: {url}")
    cache[url] = html
    return html


def extract_category_page_content(record: dict[str, str], page_cache: dict[str, str]) -> list[dict[str, str]]:
    content_records: list[dict[str, str]] = []
    for category in CONTENT_CATEGORIES:
        page_url = record.get(category, "")

        if not page_url:
            continue

        if not is_valid_link(page_url):
            content_records.append(
                failed_page_content_record(
                    record.get("college_name", "Unknown"),
                    record.get("website", ""),
                    category,
                    page_url,
                    ValueError("Skipped invalid content URL"),
                )
            )
            continue

        try:
            html = fetch_cached_page(page_url, page_cache)
            content = extract_page_content(html)
            content_records.append(
                {
                    "college_name": record.get("college_name", ""),
                    "website": record.get("website", ""),
                    "category": category,
                    "page_url": page_url,
                    **content,
                    "status": "success",
                    "error": "",
                }
            )
        except Exception as error:
            content_records.append(
                failed_page_content_record(
                    record.get("college_name", "Unknown"),
                    record.get("website", ""),
                    category,
                    page_url,
                    error,
                )
            )

    return content_records


def aggregate_college_facts(
    college_records: list[dict[str, str]],
    structured_records: list[dict[str, str]],
) -> None:
    aggregated: dict[str, dict[str, set[str]]] = {}

    for record in structured_records:
        website = record.get("website", "")
        if not website:
            continue

        bucket = aggregated.setdefault(
            website,
            {
                "courses": set(),
                "fees": set(),
                "rankings": set(),
                "cutoffs": set(),
                "course_details": set(),
            },
        )

        for field in ("courses", "fees", "rankings", "cutoffs"):
            bucket[field].update(
                value.strip()
                for value in record.get(field, "").split(" | ")
                if value.strip()
            )

        for detail in record.get("course_details", "").splitlines():
            if detail.strip():
                bucket["course_details"].add(detail.strip())

    for record in college_records:
        bucket = aggregated.get(record.get("website", ""), {})
        record["courses_list"] = " | ".join(sorted(bucket.get("courses", set())))
        record["fees_list"] = " | ".join(sorted(bucket.get("fees", set())))
        record["rankings"] = " | ".join(sorted(bucket.get("rankings", set())))
        record["cutoffs"] = " | ".join(sorted(bucket.get("cutoffs", set())))
        record["course_details"] = "\n".join(sorted(bucket.get("course_details", set())))


def build_combined_records(
    college_records: list[dict[str, str]],
    page_content_records: list[dict[str, str]],
    structured_records: list[dict[str, str]],
) -> list[dict[str, str]]:
    college_lookup = {record.get("website", ""): record for record in college_records}
    structured_lookup = {record.get("page_url", ""): record for record in structured_records}
    combined: list[dict[str, str]] = []

    for page in page_content_records:
        college = college_lookup.get(page.get("website", ""), {})
        structured = structured_lookup.get(page.get("page_url", ""), {})

        combined.append(
            {
                "college_name": college.get("college_name", ""),
                "website": page.get("website", ""),
                "admissions": college.get("admissions", ""),
                "courses": college.get("courses", ""),
                "placements": college.get("placements", ""),
                "fees": college.get("fees", ""),
                "contact": college.get("contact", ""),
                "courses_list": college.get("courses_list", ""),
                "fees_list": college.get("fees_list", ""),
                "rankings": college.get("rankings", ""),
                "cutoffs": college.get("cutoffs", ""),
                "course_details": college.get("course_details", ""),
                "page_category": page.get("category", ""),
                "page_url": page.get("page_url", ""),
                "page_title": page.get("page_title", ""),
                "headings": page.get("headings", ""),
                "content": page.get("content", ""),
                "table_content": page.get("table_content", ""),
                "page_status": page.get("status", ""),
                "page_error": page.get("error", ""),
                "structured_summary": structured.get("summary", ""),
                "structured_emails": structured.get("emails", ""),
                "structured_phones": structured.get("phones", ""),
                "structured_dates": structured.get("dates", ""),
                "structured_fees": structured.get("fees", ""),
                "structured_courses": structured.get("courses", ""),
                "structured_rankings": structured.get("rankings", ""),
                "structured_cutoffs": structured.get("cutoffs", ""),
                "structured_course_details": structured.get("course_details", ""),
                "structured_status": structured.get("status", ""),
                "structured_error": structured.get("error", ""),
            }
        )

    return combined


def build_course_detail_records(
    college_records: list[dict[str, str]],
    structured_records: list[dict[str, str]],
) -> list[dict[str, str]]:
    college_lookup = {record.get("website", ""): record for record in college_records}
    rows: list[dict[str, str]] = []

    for structured in structured_records:
        website = structured.get("website", "")
        if not website:
            continue

        college = college_lookup.get(website, {})
        for detail_line in structured.get("course_details", "").splitlines():
            detail_line = detail_line.strip()
            if not detail_line:
                continue

            parsed = parse_course_detail_text(detail_line)
            rows.append(
                {
                    "college_name": college.get("college_name", ""),
                    "website": website,
                    "page_category": structured.get("category", ""),
                    "page_url": structured.get("page_url", ""),
                    "page_title": structured.get("summary", ""),
                    "course": parsed.get("course", ""),
                    "fees": parsed.get("fees", ""),
                    "rankings": parsed.get("rankings", ""),
                    "cutoffs": parsed.get("cutoffs", ""),
                    "other_details": parsed.get("other_details", ""),
                    "raw_detail": detail_line,
                    "structured_summary": structured.get("summary", ""),
                    "structured_status": structured.get("status", ""),
                    "structured_error": structured.get("error", ""),
                }
            )

    return rows


def scrape_colleges(
    urls_file: str = "urls/colleges.txt",
    colleges_file: str = "data/colleges.csv",
    page_contents_file: str = "data/page_contents.csv",
    structured_file: str = "data/structured_facts.csv",
    all_file: str = "data/all_data.csv",
    course_details_file: str = "data/course_details.csv",
    payloads_file: str = "data/college_payloads.json",
) -> None:
    urls = load_urls(urls_file)
    records: list[dict[str, str]] = []
    page_content_records: list[dict[str, str]] = []
    page_cache: dict[str, str] = {}
    payloads: list[dict[str, object]] = []

    Path(colleges_file).parent.mkdir(parents=True, exist_ok=True)
    Path(page_contents_file).parent.mkdir(parents=True, exist_ok=True)
    Path(structured_file).parent.mkdir(parents=True, exist_ok=True)
    Path(course_details_file).parent.mkdir(parents=True, exist_ok=True)
    Path(payloads_file).parent.mkdir(parents=True, exist_ok=True)

    for url in urls:
        try:
            html = fetch_page(url)
            if html is None:
                raise RuntimeError("Page unreachable or network error")
            data = extract_data(url, html)

            # Discover section pages (admissions, courses, fees, placements, etc.)
            try:
                section_pages = find_pages(url, html)
                # Validate candidates via light-weight classification
                for cat, page_url in section_pages.items():
                    if not page_url:
                        continue
                    # If extractor already found a page, prefer it
                    if data.get(cat):
                        continue
                    try:
                        page_html = fetch_page(page_url)
                        if not page_html:
                            continue
                        best_cat, conf = classify_page(page_url, page_html)
                        # require reasonable confidence to accept the page
                        if best_cat == cat and conf >= 0.35:
                            data.setdefault(cat, page_url)
                    except Exception:
                        # Ignore classification failures and keep going
                        continue

                # If some categories are still missing, crawl internal links up to depth=2
                missing = [c for c in section_pages.keys() if not data.get(c)]
                if missing:
                    discovered = discover_internal_links(url, max_depth=2, max_pages=200)
                    # iterate discovered pages and classify
                    for page_url in discovered:
                        if any(data.get(c) for c in missing):
                            # refresh missing list
                            missing = [c for c in section_pages.keys() if not data.get(c)]
                        if not missing:
                            break
                        try:
                            page_html = fetch_page(page_url)
                            if not page_html:
                                continue
                            best_cat, conf = classify_page(page_url, page_html)
                            if best_cat in missing and conf >= 0.45:
                                data.setdefault(best_cat, page_url)
                        except Exception:
                            continue
            except Exception as fe:
                LOGGER.debug("find_pages/discovery failed for %s: %s", url, fe)
            data["status"] = "success"
            data["error"] = ""
            records.append(data)
            page_cache[url] = html
            page_content_records.extend(extract_category_page_content(data, page_cache))
            LOGGER.info("Processed: %s", url)
        except Exception as error:
            records.append(failed_record(url, error))
            LOGGER.error("Error processing %s: %s", url, error)

    structured_records = [extract_structured_facts(record) for record in page_content_records]

    # Build consolidated payloads with all category facts!
    for url in urls:
        html = page_cache.get(url) or fetch_page(url)
        if html is None:
            LOGGER.warning("Skipping payload build for %s: page unreachable", url)
            continue
        payloads.append(build_college_payload(url, html, structured_records, source="aggregator"))

    aggregate_college_facts(records, structured_records)
    combined_records = build_combined_records(records, page_content_records, structured_records)
    course_detail_records = build_course_detail_records(records, structured_records)

    save_to_csv(records, colleges_file)
    save_to_csv(page_content_records, page_contents_file)
    save_to_csv(structured_records, structured_file)
    save_to_csv(combined_records, all_file)
    save_to_csv(course_detail_records, course_details_file)
    save_payloads(payloads, payloads_file)

    # Persist to PostgreSQL (skipped gracefully when DB is unavailable)
    try:
        from edusphere.pipelines.storage_pipeline import StoragePipeline

        storage_pipeline = StoragePipeline()
        if not storage_pipeline.is_db_available():
            LOGGER.warning(
                "PostgreSQL is not reachable — skipping database persistence. "
                "Start PostgreSQL and re-run to save data to the database."
            )
        else:
            saved = 0
            for payload in payloads:
                try:
                    storage_pipeline.map_and_save(payload)
                    saved += 1
                except Exception as payload_err:
                    LOGGER.error("Failed to persist payload for %s: %s", payload.get("college_id"), payload_err)
            LOGGER.info("Persisted %d/%d college payloads to PostgreSQL.", saved, len(payloads))
    except Exception as db_err:
        LOGGER.error("PostgreSQL persistence setup error: %s", db_err)
    LOGGER.info(
        "Scraping complete. Saved %d college records, %d page content records, %d combined records, and %d normalized payloads.",
        len(records),
        len(page_content_records),
        len(combined_records),
        len(payloads),
    )


def save_payloads(payloads: list[dict[str, object]], payloads_file: str) -> None:
    """Persist normalized payloads to JSON and, when configured, to MongoDB."""
    Path(payloads_file).parent.mkdir(parents=True, exist_ok=True)
    Path(payloads_file).write_text(json.dumps(payloads, indent=2, ensure_ascii=False), encoding="utf-8")

    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        return

    try:
        from pymongo import MongoClient
    except ImportError:
        LOGGER.warning("pymongo is not installed; skipping MongoDB persistence")
        return

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db_name = os.getenv("MONGODB_DB", "college_scraper")
        collection_name = os.getenv("MONGODB_COLLECTION", "college_payloads")
        db = client[db_name]
        collection = db[collection_name]
        collection.delete_many({})
        if payloads:
            collection.insert_many(payloads)
        LOGGER.info("Saved %d payloads to MongoDB collection %s.%s", len(payloads), db_name, collection_name)
    except Exception as error:
        LOGGER.warning("MongoDB persistence failed; fallback JSON file was written: %s", error)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


def main() -> None:
    configure_logging()
    scrape_colleges()


if __name__ == "__main__":
    main()
