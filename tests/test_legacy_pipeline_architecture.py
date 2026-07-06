from pipeline.orchestrator import CollegeDiscoveryPipeline, InMemoryCrawlQueue
from pipeline.validators import normalize_and_validate_payload


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


def test_pipeline_runs_discovery_crawl_and_normalization() -> None:
    queue = InMemoryCrawlQueue()
    pipeline = CollegeDiscoveryPipeline(
        discovery_service=StubDiscoveryService(),
        crawler=StubCrawler(),
        extractor=StubExtractor(),
        queue=queue,
    )

    results = pipeline.run(["https://demo.edu"])

    assert len(results) == 2
    assert results[0]["college"]["name"] == "Demo College"
    assert results[0]["courses"][0]["name"] == "B.Tech"
    assert results[0]["fees"][0]["amount"] == "120000"
    assert results[0]["contacts"]["phone_numbers"] == ["+91 9876543210"]
    assert results[0]["validation"]["errors"] == []


def test_normalization_detects_invalid_fee_and_phone() -> None:
    payload = {
        "name": "Demo College",
        "website": "https://demo.edu",
        "courses": ["B.Tech"],
        "fees": ["invalid-fee"],
        "phone_numbers": ["not-a-phone"],
        "emails": ["bad-email"],
    }

    normalized = normalize_and_validate_payload(payload)

    assert normalized["college"]["name"] == "Demo College"
    assert normalized["validation"]["errors"]
    assert any("fee" in error.lower() for error in normalized["validation"]["errors"])
    assert any("phone" in error.lower() for error in normalized["validation"]["errors"])
