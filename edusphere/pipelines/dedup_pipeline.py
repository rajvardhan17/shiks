from __future__ import annotations


class DedupPipeline:
    def remove_duplicates(self, payloads: list[dict[str, any]]) -> list[dict[str, any]]:
        seen: set[str] = set()
        unique_payloads: list[dict[str, any]] = []
        for payload in payloads:
            identifier = payload.get("college_id") or payload.get("website") or str(payload)
            if identifier in seen:
                continue
            seen.add(identifier)
            unique_payloads.append(payload)
        return unique_payloads
