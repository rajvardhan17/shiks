from __future__ import annotations

import re
from typing import Any


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value)


def _normalize_phone_numbers(values: list[str] | None) -> list[str]:
    if not values:
        return []
    return [value.strip() for value in values if value and isinstance(value, str)]


def _normalize_emails(values: list[str] | None) -> list[str]:
    if not values:
        return []
    return [value.strip() for value in values if value and isinstance(value, str)]


def normalize_and_validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    college_name = _normalize_text(payload.get("name") or payload.get("college", {}).get("name"))
    courses = [
        {"name": _normalize_text(course) if isinstance(course, str) else _normalize_text(course.get("name"))}
        for course in payload.get("courses", [])
        if course
    ]
    fees = []
    errors: list[str] = []

    for fee in payload.get("fees", []):
        fee_text = _normalize_text(fee)
        if not fee_text:
            continue
        amount = re.sub(r"[^0-9]", "", fee_text)
        if not amount:
            errors.append(f"Invalid fee format: {fee_text}")
            continue
        fees.append({"amount": amount, "raw": fee_text})

    phone_numbers = _normalize_phone_numbers(payload.get("phone_numbers") or payload.get("contacts", {}).get("phone_numbers"))
    for phone in phone_numbers:
        if not re.search(r"^\+?\d[\d\s-]{7,}$", phone):
            errors.append(f"Invalid phone number: {phone}")

    emails = _normalize_emails(payload.get("emails") or payload.get("contacts", {}).get("emails"))
    for email in emails:
        if "@" not in email:
            errors.append(f"Invalid email: {email}")

    contacts: dict[str, Any] = {
        "phone_numbers": phone_numbers,
        "emails": emails,
    }

    return {
        "college": {"name": college_name, "website": _normalize_text(payload.get("website"))},
        "courses": courses,
        "fees": fees,
        "contacts": contacts,
        "validation": {"errors": errors, "is_valid": not errors},
    }
