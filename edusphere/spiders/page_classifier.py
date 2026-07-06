from __future__ import annotations

from urllib.parse import urlparse

from .page_finder import KEYWORDS, CATEGORY_BOOSTS


def _text_score(text: str, words: list[str]) -> int:
    t = (text or "").lower()
    score = 0
    for w in words:
        if w in t:
            score += 10
    return score


def classify_page(url: str, html: str) -> tuple[str, float]:
    title = ""
    headings = ""
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html or "", "html.parser")
        title = (soup.title.string if soup.title and soup.title.string else "").strip()
        headings = " ".join([h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])])
    except Exception:
        pass

    parsed = urlparse(url or "")
    path = (parsed.path or "").lower()

    best_cat = ""
    best_score = 0
    for category, words in KEYWORDS.items():
        score = 0
        for w in words:
            if w in path:
                score += 30
        for w in CATEGORY_BOOSTS.get(category, ()):
            if w in path:
                score += 20
        score += _text_score(title, words) * 2
        score += _text_score(headings, words) * 2
        if not title and not headings:
            score -= 10
        if score > best_score:
            best_score = score
            best_cat = category

    confidence = min(1.0, best_score / 120.0) if best_score > 0 else 0.0
    return best_cat, confidence
