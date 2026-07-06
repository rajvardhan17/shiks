from dataclasses import dataclass
from typing import Any


@dataclass
class AdmissionItem:
    eligibility: str | None = None
    minimum_percentage: str | None = None
    entrance_exam: str | None = None
    age_criteria: str | None = None
    reservation_rules: str | None = None
    domicile_rules: str | None = None
    admission_process: str | None = None
    documents_required: str | None = None
    counselling_process: str | None = None
    selection_process: str | None = None
    application_fee: str | None = None
    last_date: str | None = None
    application_link: str | None = None
    brochure_pdf: str | None = None
