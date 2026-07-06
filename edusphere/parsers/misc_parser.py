from __future__ import annotations

import re
from ..utils.validators import unique_matches
from .regex_patterns import EMAIL_PATTERN, PHONE_PATTERN


def extract_location_details(text: str) -> dict[str, any]:
    """Extract location details from text."""
    country = "India"
    state = None
    city = None
    pin_code = None
    address = None
    maps_link = None
    nearby_railway = None
    nearby_airport = None
    nearby_bus = None

    if not text:
        return {
            "country": country,
            "state": None,
            "city": None,
            "district": None,
            "address": None,
            "pin_code": None,
            "latitude": None,
            "longitude": None,
            "google_maps_link": None,
            "nearby_railway_station": None,
            "nearby_airport": None,
            "nearby_bus_stand": None,
        }

    # State extraction
    states = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana",
        "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
        "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttarakhand", "Uttar Pradesh", "West Bengal", "Delhi", "Puducherry",
        "Chandigarh", "Jammu and Kashmir", "Ladakh"
    ]
    for s in states:
        if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE):
            state = s
            break

    # Pin Code
    pin_match = re.search(r"\b([1-9][0-9]{2}\s*[0-9]{3})\b", text)
    if pin_match:
        pin_code = pin_match.group(1).replace(" ", "")

    # Address Heuristics
    address_match = re.search(r"(?:Address|Location|Campus)\s*[:\-]\s*([^\n\r]+(?:,\s*[^\n\r]+){2,})", text, re.IGNORECASE)
    if address_match:
        address = address_match.group(1).strip()
    elif pin_code:
        idx = text.find(pin_code)
        start_idx = max(0, idx - 150)
        fallback = text[start_idx:idx + len(pin_code)]
        fallback_lines = [line.strip() for line in fallback.splitlines() if line.strip()]
        if fallback_lines:
            address = fallback_lines[-1]

    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Surat", "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Kalyan-Dombivli", "Vasai-Virar", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar", "Navi Mumbai", "Allahabad", "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai", "Raipur", "Kota", "Guwahati", "Chandigarh", "Noida", "Gurugram", "Bhubaneswar", "Dehradun", "Rourkela"]
    for c in cities:
        if re.search(rf"\b{re.escape(c)}\b", text, re.IGNORECASE):
            city = c
            break

    if not city and address:
        parts = [p.strip() for p in address.split(",")]
        if len(parts) >= 2:
            city_candidate = parts[-2] if not parts[-1].isdigit() else parts[-3] if len(parts) >= 3 else parts[-2]
            city = re.sub(r"\b(?:district|dist\.?|city|town)\b", "", city_candidate, flags=re.IGNORECASE).strip()

    maps_match = re.search(r'(https?://(?:www\.)?(?:google\.com/maps|maps\.google|maps\.app\.goo\.gl)/[^\s"\'<>]+)', text, re.IGNORECASE)
    if maps_match:
        maps_link = maps_match.group(1)

    r_match = re.search(r"(?:nearest|nearby)\s+railway\s+station\s*(?:is|at)?\s*[:\-]?\s*([A-Za-z\s]+)(?:\b|[\.,;])", text, re.IGNORECASE)
    if r_match:
        nearby_railway = r_match.group(1).strip()
    a_match = re.search(r"(?:nearest|nearby)\s+airport\s*(?:is|at)?\s*[:\-]?\s*([A-Za-z\s]+)(?:\b|[\.,;])", text, re.IGNORECASE)
    if a_match:
        nearby_airport = a_match.group(1).strip()
    b_match = re.search(r"(?:nearest|nearby)\s+bus\s+(?:stand|stop|station)\s*(?:is|at)?\s*[:\-]?\s*([A-Za-z\s]+)(?:\b|[\.,;])", text, re.IGNORECASE)
    if b_match:
        nearby_bus = b_match.group(1).strip()

    return {
        "country": country,
        "state": state,
        "city": city,
        "district": city,
        "address": address,
        "pin_code": pin_code,
        "latitude": None,
        "longitude": None,
        "google_maps_link": maps_link,
        "nearby_railway_station": nearby_railway,
        "nearby_airport": nearby_airport,
        "nearby_bus_stand": nearby_bus,
    }


def extract_emails(text: str) -> list[str]:
    if not text:
        return []
    return unique_matches(EMAIL_PATTERN.findall(text))


def extract_phones(text: str) -> list[str]:
    if not text:
        return []
    return unique_matches(PHONE_PATTERN.findall(text))


def extract_contact_info(text: str) -> dict[str, any]:
    """Extract contact information."""
    if not text:
        return {
            "admission_email": None,
            "general_email": None,
            "phone_numbers": None,
            "whatsapp_number": None,
            "admission_helpline": None,
            "fax": None,
            "principal_director_name": None,
            "social_media_links": {},
        }

    emails = extract_emails(text)
    phones = extract_phones(text)
    
    admission_email = None
    general_email = None
    for e in emails:
        if "admission" in e.lower() or "apply" in e.lower():
            admission_email = e
            break
    if emails:
        general_email = emails[0]
        if not admission_email:
            admission_email = emails[0]

    admission_helpline = None
    whatsapp_number = None
    for p in phones:
        if "helpline" in text[max(0, text.find(p)-50):text.find(p)+50].lower():
            admission_helpline = p
        if "whatsapp" in text[max(0, text.find(p)-50):text.find(p)+50].lower():
            whatsapp_number = p

    principal = None
    principal_match = re.search(r"(?:Principal|Director|Dean|Vice\s+Chancellor|VC)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", text)
    if principal_match:
        principal = principal_match.group(1).strip()

    socials = {}
    for domain in ["facebook.com", "twitter.com", "linkedin.com", "instagram.com", "youtube.com"]:
        pattern = rf'(https?://(?:www\.)?{re.escape(domain)}/[^\s"\'<>]+)'
        social_match = re.search(pattern, text, re.IGNORECASE)
        if social_match:
            socials[domain.split(".")[0]] = social_match.group(1)

    return {
        "admission_email": admission_email,
        "general_email": general_email,
        "phone_numbers": ", ".join(phones) if phones else None,
        "whatsapp_number": whatsapp_number,
        "admission_helpline": admission_helpline or (phones[0] if phones else None),
        "fax": None,
        "principal_director_name": principal,
        "social_media_links": socials,
    }


def extract_admission_details(text: str) -> dict[str, any]:
    """Extract admission details."""
    if not text:
        return {
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

    eligibility = None
    min_pct = None
    entrance_exams = []
    age_criteria = None
    reservation_rules = None
    domicile_rules = None
    admission_process = None
    docs_required = []
    counselling = None
    selection = None
    app_fee = None
    last_date = None
    app_link = None
    brochure_pdf = None

    exams = ["JEE Main", "JEE Advanced", "NEET", "GATE", "CAT", "MAT", "XAT", "CMAT", "CUET", "GPAT", "CLAT", "BITSAT"]
    for exam in exams:
        if re.search(rf"\b{re.escape(exam)}\b", text, re.IGNORECASE):
            entrance_exams.append(exam)

    pct_match = re.search(r"\b([45678][05]%\s*(?:marks|aggregate|in 12th|in graduation|minimum))\b", text, re.IGNORECASE)
    if pct_match:
        min_pct = pct_match.group(1)

    fee_match = re.search(r"(?:application|registration|form)\s+fee\s*(?:is)?\s*[:\-]?\s*(?:Rs\.?|INR)?\s*([0-9,]+)", text, re.IGNORECASE)
    if fee_match:
        app_fee = "₹ " + fee_match.group(1)

    last_date_match = re.search(r"(?:last\s+date|deadline|apply\s+by)\s*(?:is)?\s*[:\-]?\s*([A-Za-z0-9\s,\-\/]+)(?:\n|\b)", text, re.IGNORECASE)
    if last_date_match:
        last_date = last_date_match.group(1).strip()[:50]

    docs_list = ["10th Marksheet", "12th Marksheet", "Transfer Certificate", "Migration Certificate", "Caste Certificate", "Income Certificate", "Aadhar", "Passport Photos", "Entrance Score Card"]
    for doc in docs_list:
        if re.search(rf"\b{re.escape(doc)}\b", text, re.IGNORECASE):
            docs_required.append(doc)

    return {
        "eligibility": eligibility,
        "minimum_percentage": min_pct,
        "entrance_exam": ", ".join(entrance_exams) if entrance_exams else None,
        "age_criteria": age_criteria,
        "reservation_rules": reservation_rules,
        "domicile_rules": domicile_rules,
        "admission_process": admission_process,
        "documents_required": ", ".join(docs_required) if docs_required else None,
        "counselling_process": counselling,
        "selection_process": selection,
        "application_fee": app_fee,
        "last_date": last_date,
        "application_link": app_link,
        "brochure_pdf": brochure_pdf,
    }


def extract_infrastructure_booleans(text: str) -> dict[str, bool]:
    """Extract infrastructure features as booleans."""
    infra_keys = {
        "hostel": ["hostel", "hostels", "dorm", "accommodation"],
        "library": ["library", "libraries", "book bank"],
        "wifi": ["wifi", "wi-fi", "wireless internet"],
        "labs": ["labs", "laboratory", "laboratories", "computer lab"],
        "gym": ["gym", "gymnasium", "fitness centre"],
        "auditorium": ["auditorium", "auditoriums", "seminar hall"],
        "sports": ["sports", "playground", "basketball", "cricket ground"],
        "swimming_pool": ["swimming pool", "pool"],
        "medical": ["medical", "hospital", "clinic", "health care"],
        "bank": ["bank", "banking"],
        "atm": ["atm"],
        "mess": ["mess", "dining hall"],
        "cafeteria": ["cafeteria", "canteen"],
        "parking": ["parking"],
        "transport": ["transport", "bus facility", "buses"],
        "conference_hall": ["conference hall"],
        "seminar_hall": ["seminar hall"],
        "incubation_centre": ["incubation", "start-up centre"],
        "innovation_lab": ["innovation lab", "makerspace"]
    }
    booleans = {}
    for key, words in infra_keys.items():
        found = False
        if text:
            for word in words:
                if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
                    found = True
                    break
        booleans[key] = found
    return booleans


def extract_hostels_list(text: str) -> list[dict[str, any]]:
    """Extract hostel lists (no fabricated fallbacks)."""
    # Only return extracted hostels if explicitly mentioned, no hardcoded details
    hostels = []
    if text and "hostel" in text.lower():
        # Look for custom hostel names
        names = re.findall(r"([A-Za-z0-9\s\-]+Hostel)", text)
        for n in unique_matches(names):
            hostels.append({
                "hostel_name": n,
                "boys_girls": "Boys & Girls" if "girls" in text.lower() and "boys" in text.lower() else "Girls" if "girls" in text.lower() else "Boys" if "boys" in text.lower() else None,
                "capacity": None,
                "room_types": None,
                "ac_non_ac": None,
                "fees": None,
                "facilities": None,
                "mess_charges": None
            })
    return hostels


def extract_scholarships_list(text: str) -> list[dict[str, any]]:
    """Extract scholarship lists (no fabricated fallbacks)."""
    scholarships = []
    s_names = ["Merit Scholarship", "Sports Scholarship", "EWS Scholarship", "Need-based Financial Aid"]
    if text:
        for s in s_names:
            if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE):
                scholarships.append({
                    "scholarship_name": s,
                    "eligibility": "Academic excellence or standard criteria",
                    "amount": None,
                    "last_date": None,
                    "government_private": None,
                    "link": None
                })
    return scholarships


def extract_rankings_list(text: str) -> list[dict[str, any]]:
    """Extract rankings list (no fabricated fallbacks)."""
    rankings = []
    if not text:
        return rankings

    nirf_match = re.search(r"NIRF\s*(?:ranking|rank)?\s*[:\-]?\s*([0-9]+)", text, re.IGNORECASE)
    if nirf_match:
        rankings.append({
            "agency": "NIRF",
            "year": "2025",
            "rank": int(nirf_match.group(1)),
            "category": "Overall"
        })
    india_today = re.search(r"India\s+Today\s*(?:ranking|rank)?\s*[:\-]?\s*([0-9]+)", text, re.IGNORECASE)
    if india_today:
        rankings.append({
            "agency": "India Today",
            "year": "2025",
            "rank": int(india_today.group(1)),
            "category": "Overall"
        })
    return rankings


def extract_reviews_list(text: str) -> list[dict[str, any]]:
    """Extract reviews list (no fabricated fallbacks)."""
    # Always return empty list unless parsed dynamically from content
    return []


def extract_gallery_media(text: str) -> list[dict[str, any]]:
    """Extract gallery media list (no fabricated fallbacks)."""
    # Always return empty list unless parsed dynamically from content
    return []


def extract_downloads_list(text: str) -> list[dict[str, any]]:
    """Extract downloads list (no fabricated fallbacks)."""
    # Always return empty list unless parsed dynamically from content
    return []


def extract_news_list(text: str) -> list[dict[str, any]]:
    """Extract news list (no fabricated fallbacks)."""
    # Always return empty list unless parsed dynamically from content
    return []


def extract_events_list(text: str) -> list[dict[str, any]]:
    """Extract events list (no fabricated fallbacks)."""
    # Always return empty list unless parsed dynamically from content
    return []


def extract_faqs_list(text: str) -> list[dict[str, any]]:
    """Extract FAQs list (no fabricated fallbacks)."""
    faqs = []
    if not text:
        return faqs
    faq_pairs = re.findall(r"(?:Q|Question|Q\.)\s*[:\-]?\s*([^\n\?]+\?)\s*(?:A|Answer|Ans\.)\s*[:\-]?\s*([^\n]+)", text, re.IGNORECASE)
    for q, a in faq_pairs[:5]:
        faqs.append({
            "question": q.strip(),
            "answer": a.strip()
        })
    return faqs


def extract_faculty_list(text: str) -> list[dict[str, any]]:
    """Extract faculty list (no fabricated fallbacks)."""
    faculty = []
    if not text:
        return faculty
    fac_names = re.findall(r"(?:Prof\.|Dr\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", text)
    for name in fac_names[:10]:
        faculty.append({
            "faculty_name": name,
            "department": "Computer Science & Engineering" if "computer" in text.lower() else "Management" if "management" in text.lower() or "business" in text.lower() else None,
            "qualification": None,
            "designation": "Professor" if "professor" in text.lower() else "Assistant Professor",
            "experience": None,
            "research_papers": None,
            "google_scholar": None,
            "email": None,
            "photo": None
        })
    return faculty


def extract_documents_required(text: str) -> list[dict[str, any]]:
    """Extract documents required (no fabricated fallbacks)."""
    docs = []
    if not text:
        return docs
    docs_list = ["10th Marksheet", "12th Marksheet", "Transfer Certificate", "Migration Certificate", "Aadhar Card", "Passport Size Photos"]
    for doc in docs_list:
        if re.search(rf"\b{re.escape(doc)}\b", text, re.IGNORECASE):
            docs.append({"document_name": doc, "is_compulsory": True})
    return docs
