from extractors.common import (
    extract_courses,
    extract_cutoffs,
    extract_course_details,
    extract_rankings,
    parse_course_detail_text,
)
from extractors.structured import extract_structured_facts


def test_extract_courses_matches_common_program_names() -> None:
    text = (
        "The institute offers B.Tech in Computer Science, M.Tech in Electrical Engineering, "
        "MBA, and Bachelor of Arts programs."
    )

    courses = extract_courses(text)

    assert "B.Tech in Computer Science" in courses
    assert "M.Tech in Electrical Engineering" in courses
    assert "MBA" in courses
    assert "Bachelor of Arts" in courses


def test_extract_rankings_matches_exam_and_rank_phrases() -> None:
    text = (
        "Last year the expected JEE Advanced closing rank was 18000, "
        "CAT score cutoff is 99 percentile, and the All India Rank was 256."
    )

    rankings = extract_rankings(text)

    assert any("JEE Advanced" in item for item in rankings)
    assert any("CAT" in item for item in rankings)
    assert any("All India Rank" in item for item in rankings)


def test_extract_cutoffs_matches_cutoff_terms() -> None:
    text = (
        "The closing cutoff for Computer Science was 2500 and the opening cutoff "
        "for Mechanical Engineering was 5000."
    )

    cutoffs = extract_cutoffs(text)

    assert any("closing cutoff" in item.lower() for item in cutoffs)
    assert any("opening cutoff" in item.lower() for item in cutoffs)


def test_extract_structured_facts_includes_new_fields() -> None:
    page_record = {
        "college_name": "Example Institute",
        "website": "https://example.edu",
        "category": "courses",
        "page_url": "https://example.edu/courses",
        "page_title": "Courses",
        "headings": "B.Tech | MBA",
        "content": "Our fees are INR 2,00,000 per year. We accept JEE Advanced rank 1500 and CAT 98 percentile. Closing cutoff is 5000.",
        "table_content": "Program | Fee \n B.Tech in Computer Science | INR 2,50,000",
        "status": "success",
        "error": "",
    }

    structured = extract_structured_facts(page_record)

    assert structured["courses"]
    assert structured["fees"]
    assert structured["rankings"]
    assert structured["cutoffs"] or "closing cutoff" in structured["rankings"]
    assert "INR 2,50,000" in structured["fees"]
    assert "B.Tech in Computer Science" in structured["courses"]
    assert "JEE Advanced" in structured["rankings"] or "CAT" in structured["rankings"]
    assert "B.Tech in Computer Science:" in structured["course_details"]


def test_parse_course_detail_text_extracts_fields() -> None:
    detail = "MCA: fees=INR 1,20,000, rankings=CAT 98 percentile, cutoffs=closing cutoff 2500"
    parsed = parse_course_detail_text(detail)

    assert parsed["course"] == "MCA"
    assert "INR 1,20,000" in parsed["fees"]
    assert "CAT 98 percentile" in parsed["rankings"]
    assert "closing cutoff 2500" in parsed["cutoffs"]
