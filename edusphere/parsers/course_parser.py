from __future__ import annotations

import re
from ..utils.validators import unique_matches, find_matches, split_table_lines, split_table_cells
from .regex_patterns import (
    COURSE_PATTERN,
    RANKING_PATTERN,
    RANK_KEYWORD_PATTERN,
)
from .fee_parser import (
    extract_fees,
    extract_total_fees,
    extract_registration_fees,
    extract_tuition_fees,
    extract_admission_fees,
)


def extract_courses(text: str) -> list[str]:
    """Extract courses/degrees from text."""
    if not text:
        return []
    matches = COURSE_PATTERN.findall(text)
    courses: list[str] = []

    for course in matches:
        normalized = course.strip()
        if normalized:
            courses.append(normalized)

    courses = unique_matches(courses)

    filtered: list[str] = []
    for course in sorted(courses, key=len, reverse=True):
        if any(course.lower() in longer.lower() and course.lower() != longer.lower() for longer in filtered):
            continue
        filtered.append(course)

    return filtered


def extract_rankings(text: str) -> list[str]:
    """Extract rankings from text."""
    if not text:
        return []
    rankings = [match.strip() for match in RANKING_PATTERN.findall(text)]
    rankings.extend([
        match.strip()
        for match in RANK_KEYWORD_PATTERN.findall(text)
        if not re.search(r"\b(?:cut[- ]?off|closing cutoff|opening cutoff|minimum cutoff|maximum cutoff)\b", match, re.IGNORECASE)
    ])
    return unique_matches(rankings)


def extract_cutoffs(text: str) -> list[str]:
    """Extract cutoffs from text."""
    if not text:
        return []
    cutoff_matches = [
        match.strip()
        for match in RANK_KEYWORD_PATTERN.findall(text)
        if re.search(r"\b(?:cut[- ]?off|closing cutoff|opening cutoff|minimum cutoff|maximum cutoff|cutoff rank)\b", match, re.IGNORECASE)
    ]
    return unique_matches(cutoff_matches)


def extract_course_detail_rows(text: str) -> list[str]:
    """Extract course details from tabular structures."""
    if not text:
        return []
    lines = split_table_lines(text)
    details: list[str] = []

    for line in lines:
        cells = split_table_cells(line)
        if not cells:
            continue

        course_cells = [cell for cell in cells if COURSE_PATTERN.search(cell)]
        if not course_cells:
            course_cells = extract_courses(line)

        if not course_cells:
            continue

        total_fees = extract_total_fees(line)
        registration_fees = extract_registration_fees(line)
        tuition_fees = extract_tuition_fees(line)
        admission_fees = extract_admission_fees(line)
        all_fees = extract_fees(line)
        
        rankings = extract_rankings(line)
        cutoffs = extract_cutoffs(line)

        for course in unique_matches(course_cells, limit=3):
            parts: list[str] = []
            
            if total_fees:
                parts.append("total_fees=" + " | ".join(total_fees))
            if registration_fees:
                parts.append("registration_fees=" + " | ".join(registration_fees))
            if tuition_fees:
                parts.append("tuition_fees=" + " | ".join(tuition_fees))
            if admission_fees:
                parts.append("admission_fees=" + " | ".join(admission_fees))
            if all_fees and not (total_fees or registration_fees or tuition_fees or admission_fees):
                parts.append("fees=" + " | ".join(all_fees))
                
            if rankings:
                parts.append("rankings=" + " | ".join(rankings))
            if cutoffs:
                parts.append("cutoffs=" + " | ".join(cutoffs))

            if parts:
                details.append(f"{course}: {', '.join(parts)}")

    return unique_matches(details, limit=20)


def extract_course_details(text: str) -> list[str]:
    """Extract course details using both tabular and contextual search."""
    if not text:
        return []
    details = extract_course_detail_rows(text)
    if details:
        return details

    return extract_course_details_by_context(text)


def extract_course_details_by_context(text: str) -> list[str]:
    """Extract course details by proximity context."""
    if not text:
        return []
    courses = find_matches(COURSE_PATTERN, text)
    
    total_fees = extract_total_fees(text)
    registration_fees = extract_registration_fees(text)
    tuition_fees = extract_tuition_fees(text)
    admission_fees = extract_admission_fees(text)
    all_fees = extract_fees(text)
    
    rankings = extract_rankings(text)
    cutoffs = extract_cutoffs(text)
    details: list[str] = []

    if not courses:
        return []

    for course_text, start, end in courses:
        parts: list[str] = []

        def neighbors(entities: list[str]) -> list[str]:
            nearby = []
            for entity in entities:
                entity_start = text.find(entity)
                if entity_start == -1:
                    continue
                distance = min(abs(start - entity_start), abs(end - (entity_start + len(entity))))
                if distance <= 150:
                    nearby.append(entity)
            return unique_matches(nearby, limit=5)

        nearby_total_fees = neighbors(total_fees)
        nearby_registration_fees = neighbors(registration_fees)
        nearby_tuition_fees = neighbors(tuition_fees)
        nearby_admission_fees = neighbors(admission_fees)
        nearby_all_fees = neighbors(all_fees)
        nearby_rankings = neighbors(rankings)
        nearby_cutoffs = neighbors(cutoffs)

        if nearby_total_fees:
            parts.append("total_fees=" + " | ".join(nearby_total_fees))
        if nearby_registration_fees:
            parts.append("registration_fees=" + " | ".join(nearby_registration_fees))
        if nearby_tuition_fees:
            parts.append("tuition_fees=" + " | ".join(nearby_tuition_fees))
        if nearby_admission_fees:
            parts.append("admission_fees=" + " | ".join(nearby_admission_fees))
        if nearby_all_fees and not (nearby_total_fees or nearby_registration_fees or nearby_tuition_fees or nearby_admission_fees):
            parts.append("fees=" + " | ".join(nearby_all_fees))
            
        if nearby_rankings:
            parts.append("rankings=" + " | ".join(nearby_rankings))
        if nearby_cutoffs:
            parts.append("cutoffs=" + " | ".join(nearby_cutoffs))

        if parts:
            details.append(f"{course_text}: {', '.join(parts)}")

    return unique_matches(details, limit=20)


def parse_course_detail_text(text: str) -> dict[str, str]:
    """Parse a course details line into specific fields."""
    original = text.strip()
    course = ""
    total_fees = ""
    registration_fees = ""
    tuition_fees = ""
    admission_fees = ""
    fees = ""
    rankings = ""
    cutoffs = ""
    other_details = ""

    if ":" in original:
        course_candidate, remainder = original.split(":", 1)
        course = course_candidate.strip()
        remainder = remainder.strip()
    else:
        remainder = original

    kv_pattern = re.compile(
        r"\b(total_fees|registration_fees|tuition_fees|admission_fees|fees|rankings|cutoffs)\s*=\s*",
        re.IGNORECASE
    )
    kv_data: dict[str, str] = {}
    matches = list(kv_pattern.finditer(remainder))

    for index, match in enumerate(matches):
        key = match.group(1).lower()
        value_start = match.end()
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(remainder)
        value = remainder[value_start:next_start].strip().strip(',')
        kv_data[key] = value

    if kv_data:
        total_fees = kv_data.get("total_fees", "")
        registration_fees = kv_data.get("registration_fees", "")
        tuition_fees = kv_data.get("tuition_fees", "")
        admission_fees = kv_data.get("admission_fees", "")
        fees = kv_data.get("fees", "")
        rankings = kv_data.get("rankings", "")
        cutoffs = kv_data.get("cutoffs", "")

        cleaned = remainder
        for key, value in kv_data.items():
            cleaned = re.sub(
                rf"\b{re.escape(key)}\s*=\s*{re.escape(value)}",
                "",
                cleaned,
                flags=re.IGNORECASE,
            )
        other_details = re.sub(r"[,:]+", " ", cleaned).strip()
        other_details = " ".join(other_details.split())
    else:
        if not course:
            courses = extract_courses(original)
            if courses:
                course = courses[0]

        total_fees_list = extract_total_fees(original)
        registration_fees_list = extract_registration_fees(original)
        tuition_fees_list = extract_tuition_fees(original)
        admission_fees_list = extract_admission_fees(original)
        
        total_fees = " | ".join(total_fees_list) if total_fees_list else ""
        registration_fees = " | ".join(registration_fees_list) if registration_fees_list else ""
        tuition_fees = " | ".join(tuition_fees_list) if tuition_fees_list else ""
        admission_fees = " | ".join(admission_fees_list) if admission_fees_list else ""
        
        if not any([total_fees, registration_fees, tuition_fees, admission_fees]):
            fees = " | ".join(extract_fees(original))
        
        rankings = " | ".join(extract_rankings(original))
        cutoffs = " | ".join(extract_cutoffs(original))

        cleaned = original
        if course:
            cleaned = cleaned.replace(course, "", 1)
        
        for item in [*total_fees.split(" | "), *registration_fees.split(" | "), 
                     *tuition_fees.split(" | "), *admission_fees.split(" | "),
                     *fees.split(" | "), *rankings.split(" | "), *cutoffs.split(" | ")]:
            if item:
                cleaned = cleaned.replace(item, "")
        
        other_details = re.sub(r"[:\-]+", "", cleaned).strip()
        other_details = " ".join(other_details.split())

    if not course:
        possible_courses = extract_courses(original)
        if possible_courses:
            course = possible_courses[0]

    return {
        "course": course,
        "total_fees": total_fees,
        "registration_fees": registration_fees,
        "tuition_fees": tuition_fees,
        "admission_fees": admission_fees,
        "fees": fees,
        "rankings": rankings,
        "cutoffs": cutoffs,
        "other_details": other_details,
    }


def extract_specializations(text: str) -> list[str]:
    """Extract specializations from text."""
    if not text:
        return []
    specs = [
        "Artificial Intelligence", "Data Science", "Cyber Security", "IoT",
        "Cloud Computing", "Finance", "HR", "Marketing", "Business Analytics",
        "Machine Learning", "Software Engineering", "Information Technology"
    ]
    found = []
    for spec in specs:
        if re.search(rf"\b{re.escape(spec)}\b", text, re.IGNORECASE):
            found.append(spec)
    return found
