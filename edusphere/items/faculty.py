from dataclasses import dataclass
from typing import Any


@dataclass
class FacultyItem:
    faculty_name: str | None = None
    department: str | None = None
    qualification: str | None = None
    designation: str | None = None
    experience: str | None = None
    research_papers: int | None = None
    google_scholar: str | None = None
    email: str | None = None
    photo: str | None = None
    created_at: str | None = None
