from __future__ import annotations

import pandas as pd
from pathlib import Path


def flatten_payload(payload: dict[str, any]) -> dict[str, any]:
    flattened: dict[str, any] = {}
    for key, value in payload.items():
        if key == "internal_links" and isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flattened[f"internal_link_{sub_key}"] = sub_value
        elif isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flattened[f"{key}_{sub_key}"] = sub_value
        else:
            flattened[key] = value
    return flattened


def export_payloads_to_xlsx(payloads: list[dict[str, any]], output_file: str) -> None:
    rows = [flatten_payload(payload) for payload in payloads]
    df = pd.DataFrame(rows)
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_file, index=False)
