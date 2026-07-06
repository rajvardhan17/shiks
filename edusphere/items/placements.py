from dataclasses import dataclass
from typing import Any


@dataclass
class PlacementItem:
    year: str | None = None
    average_package: str | None = None
    median_package: str | None = None
    highest_package: str | None = None
    placement_percentage: str | None = None
    companies_visited: int | None = None
    offers_made: int | None = None
    students_placed: int | None = None
    internships: str | None = None
    department_wise_placement: dict[str, Any] = None
    year_wise_placement: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.department_wise_placement is None:
            self.department_wise_placement = {}
        if self.year_wise_placement is None:
            self.year_wise_placement = {}
