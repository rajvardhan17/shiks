from __future__ import annotations

import re


def unique_matches(matches: list[str], limit: int = 10) -> list[str]:
    seen = set()
    values = []

    for match in matches:
        cleaned = " ".join(match.split()).strip(" .,:;")
        if not cleaned:
            continue
        if cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            values.append(cleaned)
            if len(values) >= limit:
                break
    return values


def find_matches(pattern: re.Pattern, text: str) -> list[tuple[str, int, int]]:
    return [
        (match.group().strip(), match.start(), match.end())
        for match in pattern.finditer(text)
    ]


def split_table_lines(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines


def split_table_cells(row: str) -> list[str]:
    if "|" in row:
        return [cell.strip() for cell in row.split("|") if cell.strip()]
    if "\t" in row:
        return [cell.strip() for cell in row.split("\t") if cell.strip()]

    return [cell.strip() for cell in re.split(r"\s{2,}", row) if cell.strip()]


def make_summary(text: str, max_chars: int = 500) -> str:
    compact_text = " ".join(text.split())

    if len(compact_text) <= max_chars:
        return compact_text

    # Safely split at the last space within limit
    truncated = compact_text[:max_chars]
    if " " in truncated:
        return truncated.rsplit(" ", 1)[0].strip()
    return truncated.strip()
