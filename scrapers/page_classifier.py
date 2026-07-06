from __future__ import annotations

from typing import Tuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from scrapers.page_finder import KEYWORDS, CATEGORY_BOOSTS


def _text_score(text: str, words: list[str]) -> int:
    t = (text or "").lower()
    score = 0
    for w in words:
        if w in t:
            score += 10
    return score


def classify_page(url: str, html: str) -> Tuple[str, float]:
    """Classify the page into one of the known categories.

    Returns (best_category, confidence) where confidence is in [0,1].
    """
    soup = BeautifulSoup(html or "", "html.parser")
    title = (soup.title.string if soup.title and soup.title.string else "").strip()
    headings = " ".join([h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3"])])
    parsed = urlparse(url or "")
    path = (parsed.path or "").lower()

    best_cat = ""
    best_score = 0

    for category, words in KEYWORDS.items():
        score = 0
        # URL path signal
        for w in words:
            if w in path:
                score += 30
        # boost words
        for w in CATEGORY_BOOSTS.get(category, ()): 
            if w in path:
                score += 20
        # title and headings
        score += _text_score(title, words) * 2
        score += _text_score(headings, words) * 2

        # small penalty for empty pages
        if not title and not headings:
            score = score - 10

        if score > best_score:
            best_score = score
            best_cat = category

    # Normalize to 0..1 using a heuristic max (200)
    confidence = min(1.0, best_score / 120.0) if best_score > 0 else 0.0
    return best_cat, confidence
