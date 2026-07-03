from extractors.common import (
    extract_course_details,
    extract_courses,
    extract_cutoffs,
    extract_dates,
    extract_emails,
    extract_fees,
    extract_phones,
    extract_rankings,
    extract_total_fees,
    extract_registration_fees,
    extract_tuition_fees,
    extract_admission_fees,
    extract_all_fee_types,
    extract_location_details,
    extract_contact_info,
    extract_admission_details,
    extract_specializations,
    extract_placements_info,
    extract_recruiters_list,
    extract_faculty_list,
    extract_infrastructure_booleans,
    extract_hostels_list,
    extract_scholarships_list,
    extract_rankings_list,
    extract_reviews_list,
    extract_gallery_media,
    extract_downloads_list,
    extract_news_list,
    extract_events_list,
    extract_faqs_list,
    extract_alumni_list,
    extract_documents_required,
)
from extractors.summary import make_summary


def extract_structured_facts(page_record: dict[str, str]) -> dict[str, any]:
    """Extract comprehensive searchable facts from one page content record."""
    content = page_record.get("content", "")
    table_content = page_record.get("table_content", "")
    searchable_text = " ".join([
        page_record.get("page_title", ""),
        page_record.get("headings", ""),
        content,
        table_content,
    ])

    # Extract standard fee types dictionary
    fee_types = extract_all_fee_types(searchable_text)

    return {
        "college_name": page_record.get("college_name", ""),
        "website": page_record.get("website", ""),
        "category": page_record.get("category", ""),
        "page_url": page_record.get("page_url", ""),
        "summary": make_summary(content),
        "emails": " | ".join(extract_emails(searchable_text)),
        "phones": " | ".join(extract_phones(searchable_text)),
        "dates": " | ".join(extract_dates(searchable_text)),
        "total_fees": " | ".join(fee_types.get("total_fees", [])),
        "registration_fees": " | ".join(fee_types.get("registration_fees", [])),
        "tuition_fees": " | ".join(fee_types.get("tuition_fees", [])),
        "admission_fees": " | ".join(fee_types.get("admission_fees", [])),
        "fees": " | ".join(extract_fees(searchable_text)),
        "courses": " | ".join(extract_courses(searchable_text)),
        "rankings": " | ".join(extract_rankings(searchable_text)),
        "cutoffs": " | ".join(extract_cutoffs(searchable_text)),
        "course_details": "\n".join(extract_course_details(searchable_text)),
        
        # New Structured Fields
        "location": extract_location_details(searchable_text),
        "contact": extract_contact_info(searchable_text),
        "admission_details": extract_admission_details(searchable_text),
        "specializations": extract_specializations(searchable_text),
        "placement": extract_placements_info(searchable_text),
        "recruiters": extract_recruiters_list(searchable_text),
        "faculty": extract_faculty_list(searchable_text),
        "infrastructure": extract_infrastructure_booleans(searchable_text),
        "hostels": extract_hostels_list(searchable_text),
        "scholarships": extract_scholarships_list(searchable_text),
        "rankings_list": extract_rankings_list(searchable_text),
        "reviews": extract_reviews_list(searchable_text),
        "gallery": extract_gallery_media(searchable_text),
        "downloads": extract_downloads_list(searchable_text),
        "news": extract_news_list(searchable_text),
        "events": extract_events_list(searchable_text),
        "faqs": extract_faqs_list(searchable_text),
        "alumni": extract_alumni_list(searchable_text),
        "documents": extract_documents_required(searchable_text),
        
        "status": page_record.get("status", ""),
        "error": page_record.get("error", ""),
    }
