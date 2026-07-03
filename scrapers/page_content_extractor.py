from bs4 import BeautifulSoup

MAX_CONTENT_CHARS = 5000


def extract_page_text(html: str) -> str:
    """Extract readable text from cleaned HTML."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(" ", strip=True)


def normalize_text(text: str) -> str:
    """Collapse repeated whitespace so extracted text is CSV-friendly."""
    return " ".join(text.split())


def extract_title(soup: BeautifulSoup) -> str:
    """Extract a useful page title when one is available."""
    if soup.title and soup.title.text:
        return normalize_text(soup.title.text)

    heading = soup.find(["h1", "h2"])
    return normalize_text(heading.get_text(" ", strip=True)) if heading else ""


def extract_headings(soup: BeautifulSoup) -> str:
    """Return top-level headings as a compact pipe-separated summary."""
    headings = [
        normalize_text(heading.get_text(" ", strip=True))
        for heading in soup.find_all(["h1", "h2", "h3"])
    ]
    return " | ".join(heading for heading in headings if heading)


def remove_layout_noise(soup: BeautifulSoup) -> None:
    """Drop repeated layout sections before extracting page-specific content."""
    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()


def extract_table_text(soup: BeautifulSoup) -> str:
    """Extract readable text from HTML tables while preserving row structure."""
    rows: list[str] = []

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = [
                normalize_text(cell.get_text(" ", strip=True))
                for cell in row.find_all(["th", "td"])
                if normalize_text(cell.get_text(" ", strip=True))
            ]
            if cells:
                rows.append(" ; ".join(cells))

    return " | ".join(rows)


def extract_page_content(
    html: str,
    max_chars: int = MAX_CONTENT_CHARS,
) -> dict[str, str]:
    """Extract title, headings, readable body text, and table content from a detail page."""
    soup = BeautifulSoup(html, "html.parser")
    remove_layout_noise(soup)

    content_source = soup.body if soup.body else soup
    content = normalize_text(content_source.get_text(" ", strip=True))
    table_content = normalize_text(extract_table_text(soup))

    return {
        "page_title": extract_title(soup),
        "headings": extract_headings(soup),
        "content": content[:max_chars],
        "table_content": table_content,
    }
