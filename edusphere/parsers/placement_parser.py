from __future__ import annotations

import re
from ..utils.validators import unique_matches


def extract_placements_info(text: str) -> dict[str, any]:
    """Extract placements information."""
    if not text:
        return {
            "year": None,
            "average_package": None,
            "median_package": None,
            "highest_package": None,
            "placement_percentage": None,
            "companies_visited": None,
            "offers_made": None,
            "students_placed": None,
            "internships": None,
            "department_wise_placement": {},
            "year_wise_placement": {},
        }

    avg_pkg = None
    highest_pkg = None
    median_pkg = None
    pct = None
    companies = None
    offers = None
    placed = None

    pkg_patterns = [
        (r"highest\s+(?:package|salary|lpa|compensation)\s*(?:is|of)?\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([0-9\.]+)\s*(?:lakh|lakhs|lpa|cr|crore)", "highest"),
        (r"average\s+(?:package|salary|lpa|compensation)\s*(?:is|of)?\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([0-9\.]+)\s*(?:lakh|lakhs|lpa|cr|crore)", "average"),
        (r"median\s+(?:package|salary|lpa|compensation)\s*(?:is|of)?\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([0-9\.]+)\s*(?:lakh|lakhs|lpa|cr|crore)", "median"),
    ]
    for pattern, ptype in pkg_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).strip() + " LPA"
            if ptype == "highest":
                highest_pkg = val
            elif ptype == "average":
                avg_pkg = val
            elif ptype == "median":
                median_pkg = val

    # Placement %
    pct_match = re.search(r"\b([0-9]{1,3}%)(?:\s*(?:placement|placed|recruitment\s+rate))?\b", text, re.IGNORECASE)
    if pct_match:
        pct = pct_match.group(1)

    # Counts
    comp_match = re.search(r"\b([0-9]+)\+?\s*companies\s*(?:visited|participated|recruited)\b", text, re.IGNORECASE)
    if comp_match:
        companies = int(comp_match.group(1))

    off_match = re.search(r"\b([0-9]+)\+?\s*offers\s*(?:made|secured|released)\b", text, re.IGNORECASE)
    if off_match:
        offers = int(off_match.group(1))

    placed_match = re.search(r"\b([0-9]+)\+?\s*students\s*(?:placed|selected|recruited)\b", text, re.IGNORECASE)
    if placed_match:
        placed = int(placed_match.group(1))

    return {
        "year": None,
        "average_package": avg_pkg,
        "median_package": median_pkg,
        "highest_package": highest_pkg,
        "placement_percentage": pct,
        "companies_visited": companies,
        "offers_made": offers,
        "students_placed": placed,
        "internships": None,
        "department_wise_placement": {},
        "year_wise_placement": {},
    }


def extract_recruiters_list(text: str) -> list[str]:
    """Extract known recruiter names from text."""
    if not text:
        return []
    list_recruiters = [
        "TCS", "Infosys", "Google", "Microsoft", "Amazon", "Accenture", "Wipro",
        "Cognizant", "HCL", "IBM", "Capgemini", "Deloitte", "EY", "KPMG", "PwC",
        "Tech Mahindra"
    ]
    found = []
    for r in list_recruiters:
        if re.search(rf"\b{re.escape(r)}\b", text, re.IGNORECASE):
            found.append(r)
    return found


def extract_alumni_list(text: str) -> list[dict[str, any]]:
    """Extract alumni details (returns empty list instead of fabricated fallbacks)."""
    # Reject fabricated "Siddharth Nadella" details unless explicitly found in text
    found = []
    if text and "alumni" in text.lower():
        # Try to parse actual alumni names if any present (simple pattern search)
        alumni_matches = re.findall(r"alumn(?:i|us)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", text, re.IGNORECASE)
        for name in alumni_matches:
            found.append({
                "name": name,
                "company": None,
                "package": None,
                "designation": None,
                "linkedin": None,
                "achievements": None
            })
    return found
