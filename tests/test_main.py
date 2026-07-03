from pathlib import Path

import pytest

import main


def test_load_urls(tmp_path: Path) -> None:
    file_path = tmp_path / "urls.txt"
    file_path.write_text("https://example.edu\n\nhttps://example.edu/about\n", encoding="utf-8")

    urls = main.load_urls(str(file_path))

    assert urls == ["https://example.edu", "https://example.edu/about"]


def test_failed_record_contains_expected_fields() -> None:
    record = main.failed_record("https://example.edu", ValueError("oops"))

    assert record["college_name"] == "Unknown"
    assert record["website"] == "https://example.edu"
    assert record["status"] == "failed"
    assert "oops" in record["error"]


def test_extract_category_page_content_uses_cache_and_extractor(monkeypatch) -> None:
    record = {
        "college_name": "Example College",
        "website": "https://example.edu",
        "admissions": "https://example.edu/admissions",
    }
    page_cache: dict[str, str] = {}

    def fake_fetch_cached_page(url: str, cache: dict[str, str]) -> str:
        cache[url] = "<html></html>"
        return cache[url]

    def fake_extract_page_content(html: str) -> dict[str, str]:
        return {
            "page_title": "Admissions",
            "headings": "Admissions | Apply",
            "content": "Details about admissions.",
        }

    monkeypatch.setattr(main, "fetch_cached_page", fake_fetch_cached_page)
    monkeypatch.setattr(main, "extract_page_content", fake_extract_page_content)

    records = main.extract_category_page_content(record, page_cache)

    assert len(records) == 1
    assert records[0]["category"] == "admissions"
    assert records[0]["page_title"] == "Admissions"
    assert page_cache == {"https://example.edu/admissions": "<html></html>"}
