from __future__ import annotations

import re
from ..utils.validators import unique_matches
from .regex_patterns import (
    FEE_PATTERN,
    TOTAL_FEE_PATTERN,
    REGISTRATION_FEE_PATTERN,
    TUITION_FEE_PATTERN,
    ADMISSION_FEE_PATTERN,
)


def extract_fees(text: str) -> list[str]:
    """Extract general fees from text."""
    if not text:
        return []
    matches = []
    for match in FEE_PATTERN.finditer(text):
        matches.append(match.group().strip())
    return unique_matches(matches)


def extract_total_fees(text: str) -> list[str]:
    """Extract total course fees."""
    if not text:
        return []
    matches = []
    for match in TOTAL_FEE_PATTERN.finditer(text):
        fee_text = match.group().strip()
        amount = FEE_PATTERN.search(fee_text)
        if amount:
            matches.append(f"Total Fees: {amount.group()}")
    return unique_matches(matches)


def extract_registration_fees(text: str) -> list[str]:
    """Extract registration fees."""
    if not text:
        return []
    matches = []
    for match in REGISTRATION_FEE_PATTERN.finditer(text):
        fee_text = match.group().strip()
        amount = FEE_PATTERN.search(fee_text)
        if amount:
            matches.append(f"Registration Fee: {amount.group()}")
    return unique_matches(matches)


def extract_tuition_fees(text: str) -> list[str]:
    """Extract tuition/academic fees."""
    if not text:
        return []
    matches = []
    for match in TUITION_FEE_PATTERN.finditer(text):
        fee_text = match.group().strip()
        amount = FEE_PATTERN.search(fee_text)
        if amount:
            matches.append(f"Tuition Fee: {amount.group()}")
    return unique_matches(matches)


def extract_admission_fees(text: str) -> list[str]:
    """Extract admission/entrance fees."""
    if not text:
        return []
    matches = []
    for match in ADMISSION_FEE_PATTERN.finditer(text):
        fee_text = match.group().strip()
        amount = FEE_PATTERN.search(fee_text)
        if amount:
            matches.append(f"Admission Fee: {amount.group()}")
    return unique_matches(matches)


def extract_all_fee_types(text: str) -> dict[str, list[str]]:
    """Extract all types of fees comprehensively."""
    return {
        "total_fees": extract_total_fees(text),
        "registration_fees": extract_registration_fees(text),
        "tuition_fees": extract_tuition_fees(text),
        "admission_fees": extract_admission_fees(text),
        "other_fees": extract_fees(text),
    }
