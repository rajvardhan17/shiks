from dataclasses import dataclass
from typing import Any


@dataclass
class FeeItem:
    course_name: str | None = None
    tuition_fee: str | None = None
    hostel_fee: str | None = None
    exam_fee: str | None = None
    library_fee: str | None = None
    security_deposit: str | None = None
    transport_fee: str | None = None
    miscellaneous_fee: str | None = None
    total_annual_fee: str | None = None
    total_course_fee: str | None = None
