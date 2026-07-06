from __future__ import annotations

import re
from typing import Any

from ..parsers.established_year_parser import parse_established_year


class ValidationPipeline:
    def normalize_and_validate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        college_name = self._normalize_text(payload.get("name") or payload.get("college", {}).get("name"))
        courses = [
            {"name": self._normalize_text(course) if isinstance(course, str) else self._normalize_text(course.get("name"))}
            for course in payload.get("courses", [])
            if course
        ]
        fees = []
        errors: list[str] = []

        for fee in payload.get("fees", []):
            fee_text = self._normalize_text(fee)
            if not fee_text:
                continue
            amount = re.sub(r"[^0-9]", "", fee_text)
            if not amount:
                errors.append(f"Invalid fee format: {fee_text}")
                continue
            fees.append({"amount": amount, "raw": fee_text})

        phone_numbers = self._normalize_phone_numbers(payload.get("phone_numbers") or payload.get("contacts", {}).get("phone_numbers"))
        for phone in phone_numbers:
            if not re.search(r"^\+?\d[\d\s-]{7,}$", phone):
                errors.append(f"Invalid phone number: {phone}")

        emails = self._normalize_emails(payload.get("emails") or payload.get("contacts", {}).get("emails"))
        for email in emails:
            if "@" not in email:
                errors.append(f"Invalid email: {email}")

        return {
            "college": {"name": college_name, "website": self._normalize_text(payload.get("website"))},
            "courses": courses,
            "fees": fees,
            "contacts": {"phone_numbers": phone_numbers, "emails": emails},
            "validation": {"errors": errors, "is_valid": not errors},
        }

    def _normalize_text(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        return str(value)

    def _normalize_phone_numbers(self, values: list[str] | None) -> list[str]:
        if not values:
            return []
        return [value.strip() for value in values if value and isinstance(value, str)]

    def _normalize_emails(self, values: list[str] | None) -> list[str]:
        if not values:
            return []
        return [value.strip() for value in values if value and isinstance(value, str)]

    def annotate_established_year(self, text: str) -> str | None:
        return parse_established_year(text)
