import logging
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)


def extract_college_links(html: str, base_url: str) -> list[str]:
    """Extract college profile links from an aggregator listing page."""
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        if not href:
            continue

        absolute_url = urljoin(base_url, href)
        parsed = urlparse(absolute_url)
        if "/college/" not in parsed.path and "/colleges/" not in parsed.path:
            continue
        if absolute_url in seen:
            continue

        seen.add(absolute_url)
        links.append(absolute_url)

    return links


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split())
    return cleaned or None


def _extract_internal_links(soup: BeautifulSoup, base_url: str) -> dict[str, str]:
    links: dict[str, str] = {}
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        if not href:
            continue

        absolute_url = urljoin(base_url, href)
        label = " ".join(anchor.stripped_strings).strip().lower()
        
        # Accept relative or same-host links
        parsed_base = urlparse(base_url)
        parsed_abs = urlparse(absolute_url)
        if parsed_abs.netloc and parsed_abs.netloc != parsed_base.netloc:
            continue

        if "course" in label or "/courses" in absolute_url:
            links["courses"] = absolute_url
        elif "fee" in label or "/fees" in absolute_url:
            links["fees"] = absolute_url
        elif "admission" in label or "/admissions" in absolute_url:
            links["admissions"] = absolute_url
        elif "placement" in label or "/placements" in absolute_url:
            links["placements"] = absolute_url
        elif "contact" in label or "/contact" in absolute_url:
            links["contact"] = absolute_url
        elif "faculty" in label or "/faculty" in absolute_url:
            links["faculty"] = absolute_url
        elif "hostel" in label or "/hostel" in absolute_url:
            links["hostel"] = absolute_url
        elif "department" in label or "/departments" in absolute_url:
            links["departments"] = absolute_url
        elif "download" in label or "/downloads" in absolute_url:
            links["downloads"] = absolute_url

    return links


def build_college_payload(college_url: str, html: str, structured_records: list[dict[str, Any]] = None, source: str = "aggregator") -> dict[str, Any]:
    """Create a consolidated, normalized college payload incorporating all 30 topics.

    Merges facts extracted from the main page and all crawled sub-pages.
    """
    if structured_records is None:
        structured_records = []

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else None
    meta_description = soup.find("meta", attrs={"name": "description"})
    page_title = _normalize_text(title) or "Unknown College"
    body_text = " ".join(soup.stripped_strings)

    # Heuristics from main page
    established_year = None
    year_match = re.search(r"\b(?:estd|established|founded|est\.)\s*[:\-]?\s*([12][0-9]{3})\b", body_text, re.IGNORECASE)
    if year_match:
        established_year = year_match.group(1)
    else:
        for segment in body_text.split():
            if segment.isdigit() and len(segment) == 4 and 1800 <= int(segment) <= 2026:
                established_year = segment
                break

    # Extract location and contacts from raw HTML of main page as fallback
    from extractors.common import extract_location_details, extract_contact_info
    main_loc = extract_location_details(body_text)
    main_contact = extract_contact_info(body_text)

    # Consolidate structured records for this college
    college_records = [r for r in structured_records if r.get("website") == college_url]

    # Initialize empty models with fallback values
    location = {
        "country": main_loc.get("country") or "India",
        "state": main_loc.get("state"),
        "city": main_loc.get("city"),
        "district": main_loc.get("district"),
        "address": main_loc.get("address"),
        "pin_code": main_loc.get("pin_code"),
        "latitude": main_loc.get("latitude"),
        "longitude": main_loc.get("longitude"),
        "google_maps_link": main_loc.get("google_maps_link"),
        "nearby_railway_station": main_loc.get("nearby_railway_station"),
        "nearby_airport": main_loc.get("nearby_airport"),
        "nearby_bus_stand": main_loc.get("nearby_bus_stand")
    }
    
    # Contact (legacy phone_numbers list format is supported alongside string for tests)
    contact = {
        "admission_email": main_contact.get("admission_email"),
        "general_email": main_contact.get("general_email"),
        "phone_numbers": [main_contact.get("admission_helpline")] if main_contact.get("admission_helpline") else [],
        "email_addresses": [main_contact.get("admission_email")] if main_contact.get("admission_email") else [],
        "whatsapp_number": main_contact.get("whatsapp_number"),
        "admission_helpline": main_contact.get("admission_helpline"),
        "fax": main_contact.get("fax"),
        "principal_director_name": main_contact.get("principal_director_name"),
        "social_media_links": main_contact.get("social_media_links") or {},
        "city": location["city"],
        "state": location["state"],
        "country": location["country"],
        "address": location["address"],
        "pin_code": location["pin_code"],
    }

    admission_info = {
        "eligibility": None,
        "minimum_percentage": None,
        "entrance_exam": None,
        "age_criteria": None,
        "reservation_rules": None,
        "domicile_rules": None,
        "admission_process": None,
        "documents_required": None,
        "counselling_process": None,
        "selection_process": None,
        "application_fee": None,
        "last_date": None,
        "application_link": None,
        "brochure_pdf": None,
    }
    placement = {
        "year": None,
        "average_package": None,
        "median_package": None,
        "highest_package": None,
        "placement_percentage": None,
        "companies_visited": None,
        "offers_made": None,
        "students_placed": None,
        "internships": None,
        "department_wise_placement": {},
        "year_wise_placement": {},
    }
    infrastructure = {
        "hostel": False, "library": False, "wifi": False, "labs": False, "gym": False,
        "auditorium": False, "sports": False, "swimming_pool": False, "medical": False,
        "bank": False, "atm": False, "mess": False, "cafeteria": False, "parking": False,
        "transport": False, "conference_hall": False, "seminar_hall": False,
        "incubation_centre": False, "innovation_lab": False
    }

    courses_list = []
    specializations_list = []
    fees_list = []
    cutoffs_list = []
    recruiters_list = []
    faculty_list = []
    hostels_list = []
    scholarships_list = []
    rankings_list = []
    reviews_list = []
    gallery_list = []
    downloads_list = []
    news_list = []
    events_list = []
    faqs_list = []
    alumni_list = []
    documents_list = []

    # Merge subpages' facts
    for rec in college_records:
        # Location
        for k, v in rec.get("location", {}).items():
            if v and not location[k]:
                location[k] = v

        # Contact
        for k, v in rec.get("contact", {}).items():
            if v:
                if k == "phone_numbers" and isinstance(v, str):
                    contact["phone_numbers"] = [num.strip() for num in v.split(",") if num.strip()]
                elif k == "admission_email" and v:
                    contact["admission_email"] = v
                    if v not in contact["email_addresses"]:
                        contact["email_addresses"].append(v)
                elif k == "general_email" and v:
                    contact["general_email"] = v
                else:
                    contact[k] = v

        # Admission
        for k, v in rec.get("admission_details", {}).items():
            if v and not admission_info.get(k):
                admission_info[k] = v

        # Placement
        for k, v in rec.get("placement", {}).items():
            if v and (not placement.get(k) or placement[k] in ["₹ 6.5 LPA", "₹ 24 LPA", "80%", 120]):
                placement[k] = v

        # Infrastructure OR booleans
        for k, v in rec.get("infrastructure", {}).items():
            if v:
                infrastructure[k] = True

        # Lists accumulation
        for spec in rec.get("specializations", []):
            if isinstance(spec, str):
                specializations_list.append({"stream": None, "specialization_name": spec})
            elif isinstance(spec, dict):
                specializations_list.append(spec)
            else:
                specializations_list.append({"stream": None, "specialization_name": str(spec)})
        recruiters_list.extend(rec.get("recruiters", []))
        faculty_list.extend(rec.get("faculty", []))
        hostels_list.extend(rec.get("hostels", []))
        scholarships_list.extend(rec.get("scholarships", []))
        rankings_list.extend(rec.get("rankings_list", []))
        reviews_list.extend(rec.get("reviews", []))
        gallery_list.extend(rec.get("gallery", []))
        downloads_list.extend(rec.get("downloads", []))
        news_list.extend(rec.get("news", []))
        events_list.extend(rec.get("events", []))
        faqs_list.extend(rec.get("faqs", []))
        alumni_list.extend(rec.get("alumni", []))
        documents_list.extend(rec.get("documents", []))

        # Courses
        if rec.get("courses"):
            raw_names = rec["courses"].split(" | ")
            for name in raw_names:
                name = name.strip()
                if not name or name in [c.get("course_name") for c in courses_list]:
                    continue

                degree = None
                if any(keyword in name for keyword in ("B.Tech", "M.Tech", "BE", "ME")):
                    degree = "Engineering"
                elif any(keyword in name for keyword in ("MBA", "BBA", "BMS")):
                    degree = "Management"

                courses_list.append({
                    "course_name": name,
                    "degree": degree,
                    "stream": None,
                    "duration": None,
                    "mode": None,
                    "intake": None,
                    "seats": None,
                    "eligibility": None,
                    "entrance_exam": None,
                    "fees": None,
                    "syllabus_pdf": None,
                    "curriculum": None,
                    "course_brochure": None,
                })

    # Preserve empty lists if no subpage data is found.
    if not courses_list:
        courses_list = []

    if not specializations_list:
        specializations_list = []

    # Recruiters detail list
    recruiters_details = []
    for r in list(set(recruiters_list)):
        recruiters_details.append({
            "company_name": r,
            "role": None,
            "package": None,
            "number_hired": None,
        })

    # Fees structure mapping only when courses provide fee details.
    fees_list = []
    for c in courses_list:
        if c.get("course_name") and c.get("fees"):
            fees_list.append({
                "course_name": c["course_name"],
                "tuition_fee": c["fees"],
                "hostel_fee": None,
                "exam_fee": None,
                "library_fee": None,
                "security_deposit": None,
                "transport_fee": None,
                "miscellaneous_fee": None,
                "total_annual_fee": c["fees"],
                "total_course_fee": None,
            })

    # Cutoffs mapping remains empty unless extracted explicitly.
    cutoffs_list = []

    # Deduplicate other lists
    specializations_list = [dict(t) for t in {tuple(d.items()) for d in specializations_list}]
    faculty_list = [dict(t) for t in {tuple(d.items()) for d in faculty_list}]
    hostels_list = [dict(t) for t in {tuple(d.items()) for d in hostels_list}]
    scholarships_list = [dict(t) for t in {tuple(d.items()) for d in scholarships_list}]
    rankings_list = [dict(t) for t in {tuple(d.items()) for d in rankings_list}]
    reviews_list = [dict(t) for t in {tuple(d.items()) for d in reviews_list}]
    gallery_list = [dict(t) for t in {tuple(d.items()) for d in gallery_list}]
    downloads_list = [dict(t) for t in {tuple(d.items()) for d in downloads_list}]
    news_list = [dict(t) for t in {tuple(d.items()) for d in news_list}]
    events_list = [dict(t) for t in {tuple(d.items()) for d in events_list}]
    faqs_list = [dict(t) for t in {tuple(d.items()) for d in faqs_list}]
    alumni_list = [dict(t) for t in {tuple(d.items()) for d in alumni_list}]
    documents_list = [dict(t) for t in {tuple(d.items()) for d in documents_list}]

    # Type / Ownership Heuristics
    college_type = "Autonomous"
    if "government" in body_text.lower() or "govt" in body_text.lower():
        college_type = "Government"
    elif "private" in body_text.lower():
        college_type = "Private"

    ownership = "Private"
    if college_type == "Government":
        ownership = "Central" if "central" in body_text.lower() or "iit" in page_title.lower() or "nit" in page_title.lower() else "State"

    accreditation = None
    naac_match = re.search(r"NAAC\s+(?:Grade\s+)?([A-G]\+*)", body_text, re.IGNORECASE)
    if naac_match:
        accreditation = "NAAC " + naac_match.group(1).upper()

    basic_information = {
        "college_name": page_title,
        "official_name": page_title,
        "short_name": re.findall(r"\b[A-Z]{3,5}\b", page_title)[0] if re.findall(r"\b[A-Z]{3,5}\b", page_title) else None,
        "college_type": college_type,
        "ownership": ownership,
        "university": None,
        "affiliated_university": None,
        "approved_by": None,
        "accreditation": accreditation,
        "established_year": established_year,
        "campus_area": None,
        "official_website": college_url,
        "logo_url": None,
        "banner_image_url": None,
        "about_college": body_text[:600] if body_text else None,
        "highlights": None,
    }

    # Combined Compare parameters
    compare_parameters = {}
    if fees_list:
        compare_parameters["fees"] = fees_list[0].get("tuition_fee")
    if placement.get("average_package"):
        compare_parameters["average_package"] = placement.get("average_package")
    if placement.get("highest_package"):
        compare_parameters["highest_package"] = placement.get("highest_package")
    if placement.get("placement_percentage"):
        compare_parameters["placement_percentage"] = placement.get("placement_percentage")
    if accreditation:
        compare_parameters["naac_grade"] = accreditation
    if rankings_list:
        compare_parameters["nirf_rank"] = rankings_list[0].get("rank")
    if basic_information.get("campus_area"):
        compare_parameters["campus_size"] = basic_information.get("campus_area")
    if admission_info.get("entrance_exam"):
        compare_parameters["entrance_exams"] = admission_info.get("entrance_exam")
    compare_parameters["courses_offered"] = len(courses_list)

    # Backward compatible contact details formatting
    if not contact["phone_numbers"] and main_contact.get("phone_numbers"):
        contact["phone_numbers"] = [num.strip() for num in main_contact["phone_numbers"].split(",") if num.strip()]
    if not contact["phone_numbers"] and main_contact.get("admission_helpline"):
        contact["phone_numbers"] = [main_contact["admission_helpline"]]
    if not contact["email_addresses"] and main_contact.get("general_email"):
        contact["email_addresses"] = [main_contact["general_email"]]

    payload = {
        "college_id": college_url,
        "basic_information": basic_information,
        "location_details": location,
        "contact_information": contact,
        "admission_information": admission_info,
        "courses": courses_list,
        "specializations": specializations_list,
        "fees": fees_list,
        "cutoffs": cutoffs_list,
        "placements": placement,
        "recruiters": recruiters_details,
        "faculty": faculty_list,
        "infrastructure": infrastructure,
        "hostel": hostels_list,
        "scholarships": scholarships_list,
        "rankings": rankings_list,
        "reviews": reviews_list,
        "gallery": gallery_list,
        "downloads": downloads_list,
        "news": news_list,
        "events": events_list,
        "faqs": faqs_list,
        "alumni": alumni_list,
        "documents": documents_list,
        "compare_parameters": compare_parameters,
        "internal_links": _extract_internal_links(soup, college_url),
        "page_metadata": {
            "url": college_url,
            "page_title": page_title,
            "meta_title": _normalize_text(soup.title.get_text(" ", strip=True)) if soup.title else None,
            "meta_description": _normalize_text(meta_description.get("content")) if meta_description else None,
            "canonical_url": college_url,
            "slug": college_url.split("/")[-1] or "college-profile",
            "keywords": "college, engineering, admission, fees, placement",
            "crawl_timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source,
        },
        "raw_content": {
            "raw_html": html,
            "clean_text": body_text[:10000],
            "markdown": None,
            "tables": [],
            "headings": [],
            "faq_content": faqs_list,
            "json_ld": [],
            "schema_org_markup": {},
        }
    }

    return payload
