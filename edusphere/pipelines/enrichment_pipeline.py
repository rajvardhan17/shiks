from __future__ import annotations

from typing import Any


class EnrichmentPipeline:
    def enrich_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload["data_completeness"] = {
            "has_real_courses": bool(payload.get("courses")),
            "has_real_placement": bool(payload.get("placements") and any(payload.get("placements", {}).values())),
            "has_real_admission_info": bool(payload.get("admission_information") and any(payload.get("admission_information", {}).values())),
            "has_real_contact_info": bool(payload.get("contact_information") and any(payload.get("contact_information", {}).values())),
            "has_real_location_info": bool(payload.get("location_details") and any(payload.get("location_details", {}).values())),
        }
        return payload
