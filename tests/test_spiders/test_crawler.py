import requests

from edusphere.spiders.crawler import request_page


class DummyResponse:
    def __init__(self, url: str = "https://example.com") -> None:
        self.url = url
        self.status_code = 200
        self.text = "<html></html>"
        self.history = []

    def raise_for_status(self) -> None:
        return None


class FailingThenSucceedingSession:
    def __init__(self) -> None:
        self.calls: list[bool] = []

    def get(self, url: str, headers=None, timeout=None, allow_redirects=True, verify=True):
        self.calls.append(verify)
        if len(self.calls) == 1 and verify is True:
            raise requests.exceptions.SSLError("certificate verify failed")
        return DummyResponse(url)


def test_request_page_retries_without_certificate_verification() -> None:
    session = FailingThenSucceedingSession()
    response = request_page("https://example.com", session, (5, 10))
    assert response.status_code == 200
    assert session.calls == [True, False]
