from dataclasses import dataclass
from typing import Any


@dataclass
class CourseItem:
    course_name: str | None = None
    degree: str | None = None
    stream: str | None = None
    duration: str | None = None
    mode: str | None = None
    intake: str | None = None
    seats: str | None = None
    eligibility: str | None = None
    entrance_exam: str | None = None
    fees: str | None = None
    syllabus_pdf: str | None = None
    curriculum: str | None = None
    course_brochure: str | None = None


