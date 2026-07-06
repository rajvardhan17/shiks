from __future__ import annotations

import re
from datetime import datetime

ESTABLISHED_PATTERNS = [
    r"\b(?:estd|established|founded|est\.|since)\s*[:\-]?\s*([12][0-9]{3})\b",
    r"\b([12][0-9]{3})\s*(?:estd|established|founded|since)\b",
]

CURRENT_YEAR = datetime.now().year


def parse_established_year(text: str) -> str | None:
    if not text:
        return None

    normalized = " ".join(text.split())
    for pattern in ESTABLISHED_PATTERNS:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            year_text = match.group(1)
            try:
                year = int(year_text)
            except ValueError:
                continue
            if year >= CURRENT_YEAR - 2:
                return None
            if 1800 <= year <= CURRENT_YEAR:
                return str(year)
    return None
