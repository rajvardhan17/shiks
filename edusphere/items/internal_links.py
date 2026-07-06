from dataclasses import dataclass
from typing import Any


@dataclass
class InternalLinksItem:
    admissions: str | None = None
    courses: str | None = None
    placements: str | None = None
    fees: str | None = None
    contact: str | None = None
    faculty: str | None = None
    hostel: str | None = None
    departments: str | None = None
    downloads: str | None = None
