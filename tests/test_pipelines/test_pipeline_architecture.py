from edusphere.pipelines.validation_pipeline import ValidationPipeline
from edusphere.pipelines.dedup_pipeline import DedupPipeline


class StubDiscoveryService:
    def discover(self, seed_urls):
        return [f"{seed_url}/admissions" for seed_url in seed_urls]


class StubCrawler:
    def crawl(self, url):
        return f"<html><body>{url}</body></html>"


class StubExtractor:
    def extract(self, url, html):
        return {
            "name": "Demo College",
            "website": url,
            "courses": ["B.Tech"],
            "fees": ["₹1,20,000"],
            "phone_numbers": ["+91 9876543210"],
            "emails": ["admissions@example.com"],
        }


def test_validation_pipeline_normalizes_payload() -> None:
    pipeline = ValidationPipeline()
    normalized = pipeline.normalize_and_validate_payload({
        "name": "Demo College",
        "website": "https://demo.edu",
        "courses": ["B.Tech"],
        "fees": ["₹1,20,000"],
        "phone_numbers": ["+91 9876543210"],
        "emails": ["admissions@example.com"],
    })

    assert normalized["college"]["name"] == "Demo College"
    assert normalized["courses"][0]["name"] == "B.Tech"
    assert normalized["fees"][0]["amount"] == "120000"
    assert normalized["contacts"]["phone_numbers"] == ["+91 9876543210"]
    assert normalized["validation"]["errors"] == []


def test_dedup_pipeline_removes_duplicate_payloads() -> None:
    payloads = [
        {"college_id": "https://demo.edu"},
        {"college_id": "https://demo.edu"},
        {"college_id": "https://example.edu"},
    ]
    dedup = DedupPipeline()
    unique = dedup.remove_duplicates(payloads)
    assert len(unique) == 2
