def make_summary(text: str, max_chars: int = 500) -> str:
    compact_text = " ".join(text.split())

    if len(compact_text) <= max_chars:
        return compact_text

    return compact_text[:max_chars].rsplit(" ", 1)[0].strip()
