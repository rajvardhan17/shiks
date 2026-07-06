import logging
from itertools import cycle
from urllib.parse import urlparse, urlunparse

import requests
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT: tuple[int, int] = (5, 30)
MAX_REDIRECTS = 5

USER_AGENTS: tuple[str, ...] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36",
)

_user_agents = cycle(USER_AGENTS)


def create_session() -> requests.Session:
    """Create a configured HTTP session with retry support."""
    session = requests.Session()
    session.max_redirects = MAX_REDIRECTS

    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "HEAD"),
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


SESSION = create_session()


def get_url_candidates(url: str) -> list[str]:
    """Return fallback URL variants for transient DNS or host alias failures."""
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    candidates = [url]

    if host.startswith("www."):
        fallback_host = host.removeprefix("www.")
        candidates.append(urlunparse(parsed_url._replace(netloc=fallback_host)))
    elif host and len(host.split(".")) <= 3:
        candidates.append(urlunparse(parsed_url._replace(netloc=f"www.{host}")))

    return candidates


def get_headers() -> dict[str, str]:
    """Return headers for the next request, rotating the User-Agent."""
    return {
        "User-Agent": next(_user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }


def clean_html(html: str) -> str:
    """Remove noisy tags and return normalized HTML for downstream parsing."""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    return str(soup)


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception_type((RuntimeError, requests.exceptions.RequestException)),
)
def request_page(
    url: str,
    session: requests.Session,
    timeout: tuple[int, int],
) -> requests.Response:
    """Request one URL and convert requests errors into clear runtime errors.

    Retries are handled by tenacity with exponential backoff for RuntimeError
    produced by transient network or HTTP issues.
    """
    try:
        response = session.get(
            url,
            headers=get_headers(),
            timeout=timeout,
            allow_redirects=True,
            verify=True,
        )
    except requests.exceptions.SSLError as exc:
        logger.warning(
            "SSL verification failed for %s; retrying without certificate verification",
            url,
        )
        try:
            response = session.get(
                url,
                headers=get_headers(),
                timeout=timeout,
                allow_redirects=True,
                verify=False,
            )
        except requests.exceptions.RequestException as exc2:
            logger.error("Request failed for %s: %s", url, exc2)
            raise RuntimeError(f"Request failed for {url}: {exc2}") from exc2
        except Exception as exc2:
            logger.error("Unexpected error for %s: %s", url, exc2)
            raise RuntimeError(f"Request failed for {url}: {exc2}") from exc2
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as exc:
        logger.error("Request failed for %s: %s", url, exc)
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc
    except Exception as exc:
        logger.error("Unexpected error for %s: %s", url, exc)
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc

    try:
        # Treat 429/5xx as transient
        if response.status_code >= 500 or response.status_code == 429:
            logger.warning("Transient HTTP %s for %s", response.status_code, url)
            raise RuntimeError(f"Transient HTTP {response.status_code} for {url}")

        response.raise_for_status()
        return response
    except requests.exceptions.Timeout as exc:
        logger.error("Request timed out for %s", url)
        raise RuntimeError(f"Request timed out for {url}") from exc
    except requests.exceptions.TooManyRedirects as exc:
        logger.error("Too many redirects for %s", url)
        raise RuntimeError(f"Too many redirects for {url}") from exc
    except requests.exceptions.RequestException as exc:
        logger.error("Request failed for %s: %s", url, exc)
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc


def fetch_page(
    url: str,
    session: requests.Session = SESSION,
    timeout: tuple[int, int] = DEFAULT_TIMEOUT,
) -> str:
    """Fetch a page with retries, redirects, timeout handling, and clean HTML output."""
    last_error: RuntimeError | None = None

    for candidate_url in get_url_candidates(url):
        logger.info("Fetching page: %s", candidate_url)

        try:
            response = request_page(candidate_url, session, timeout)
            break
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Trying next URL candidate after failure: %s (%s)",
                candidate_url,
                type(exc).__name__,
            )
    else:
        logger.error("All URL candidates failed for %s: %s", url, last_error)
        return None

    if response is None:
        logger.error("No response returned for %s", url)
        return None

    if response.history:
        redirect_chain = " -> ".join(
            [redirect.url for redirect in response.history] + [response.url]
        )
        logger.info("Redirect chain for %s: %s", url, redirect_chain)

    logger.info("Fetched %s with status %s", response.url, response.status_code)
    return clean_html(response.text)
