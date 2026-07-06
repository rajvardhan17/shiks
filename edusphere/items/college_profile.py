from dataclasses import dataclass
from typing import Any


@dataclass
class CollegeProfile:
    college_id: str
    basic_information: dict[str, Any]
    location_details: dict[str, Any]
    contact_information: dict[str, Any]
    admission_information: dict[str, Any]
    courses: list[dict[str, Any]]
    specializations: list[dict[str, Any]]
    fees: list[dict[str, Any]]
    cutoffs: list[dict[str, Any]]
    placements: dict[str, Any]
    recruiters: list[dict[str, Any]]
    faculty: list[dict[str, Any]]
    infrastructure: dict[str, Any]
    hostel: list[dict[str, Any]]
    scholarships: list[dict[str, Any]]
    rankings: list[dict[str, Any]]
    reviews: list[dict[str, Any]]
    gallery: list[dict[str, Any]]
    downloads: list[dict[str, Any]]
    news: list[dict[str, Any]]
    events: list[dict[str, Any]]
    faqs: list[dict[str, Any]]
    alumni: list[dict[str, Any]]
    documents: list[dict[str, Any]]
    compare_parameters: dict[str, Any]
    internal_links: dict[str, str]
    page_metadata: dict[str, Any]
    raw_content: dict[str, Any]
    data_completeness: dict[str, bool]
