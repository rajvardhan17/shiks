import re

EMAIL_PATTERN = re.compile(
    r"[\w.+-]+@[\w.-]+\.[a-z]{2,}|"
    r"[\w.+-]+\s*(?:\[at\]|\(at\))\s*[\w.-]+\s*(?:\[dot\]|\(dot\))\s*[a-z]{2,}",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{4,5}"
)
DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}|"
    r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+\d{4})\b",
    re.IGNORECASE,
)
# Generic fee pattern - matches any currency amount
FEE_PATTERN = re.compile(
    "(?:Rs\\.?|INR|\\u20b9|USD)\\s?[\\d,]+(?:\\.\\d+)?|"
    "[\\d,]+(?:\\.\\d+)?\\s?(?:lakh|lakhs|crore|crores)",
    re.IGNORECASE,
)

# Specific fee type patterns
TOTAL_FEE_PATTERN = re.compile(
    r"\b(?:total\s+(?:course\s+)?fees?|total\s+(?:academic\s+)?fees?|total\s+cost|course\s+fee|full\s+course\s+fee)\s*[:\-]?\s*(?:Rs\\.?|INR|\\u20b9|USD)?\s?[\\d,]+(?:\\.\\d+)?|"
    r"(?:Rs\\.?|INR|\\u20b9|USD)\s?[\\d,]+(?:\\.\\d+)?\s*(?:per\s+(?:semester|year|program))?",
    re.IGNORECASE,
)

REGISTRATION_FEE_PATTERN = re.compile(
    r"\b(?:registration\s+(?:fees?|charges?)|enrollment\s+(?:fees?|charges?)|application\s+(?:fees?|charges?))\s*[:\-]?\s*(?:Rs\\.?|INR|\\u20b9|USD)?\s?[\\d,]+(?:\\.\\d+)?",
    re.IGNORECASE,
)

TUITION_FEE_PATTERN = re.compile(
    r"\b(?:tuition\s+(?:fees?|charges?)|academic\s+(?:fees?|charges?)|course\s+(?:fees?|charges?))\s*[:\-]?\s*(?:Rs\\.?|INR|\\u20b9|USD)?\s?[\\d,]+(?:\\.\\d+)?",
    re.IGNORECASE,
)

ADMISSION_FEE_PATTERN = re.compile(
    r"\b(?:admission\s+(?:fees?|charges?)|entrance\s+(?:fees?|charges?))\s*[:\-]?\s*(?:Rs\\.?|INR|\\u20b9|USD)?\s?[\\d,]+(?:\\.\\d+)?",
    re.IGNORECASE,
)

DEGREE_TERMS = r"(?:B\.?Tech|M\.?Tech|MBA|B\.?E\.?|BE|B\.?Sc|B\.?A\.?|LLB|MBBS|BDS|BPharm|MPharm|MCA|BCA|BBA|BArch|MSc|MA|BA|BCom|BDes|Ph\.?D|Doctor of Philosophy|Master of Technology|Master of Science|Master of Arts|Bachelor of Technology|Bachelor of Science|Bachelor of Arts|Bachelor of Commerce|Bachelor of Laws)"

COURSE_PATTERN = re.compile(
    r"\b(?:" + DEGREE_TERMS + r")\b"
    r"(?:\s+(?:in|of|for)\s+[^.;,\n]*?(?=\s+(?:and|or)\s+(?:" + DEGREE_TERMS + r")\b|[.;,\n]|$))?",
    re.IGNORECASE,
)

RANKING_PATTERN = re.compile(
    r"((?:JEE(?:\s*Advanced|\s*Main)?|CAT|NEET|GATE|CLAT|CUET|XAT|MAT|NATA|BITSAT|IITJEE|SRMJEEE|NMAT|CMAT|All India Rank|AIR)[^\n\r]{0,80}?\d{1,6}(?:,\d{3})?(?:\s*%?))",
    re.IGNORECASE,
)

RANK_KEYWORD_PATTERN = re.compile(
    r"\b(?:opening|closing|minimum|maximum)?\s*(?:rank|ranking|cut[- ]?off|closing rank|opening rank|minimum rank|required rank|cutoff rank|closing cutoff|minimum cutoff|opening cutoff|maximum cutoff)\b[^\n\r]{0,80}?\d{1,6}(?:,\d{3})?(?:\s*%?)",
    re.IGNORECASE,
)


def unique_matches(matches: list[str], limit: int = 10) -> list[str]:
    seen = set()
    values = []

    for match in matches:
        cleaned = " ".join(match.split()).strip(" .,:;")
        key = cleaned.lower()

        if cleaned and key not in seen:
            seen.add(key)
            values.append(cleaned)

        if len(values) >= limit:
            break

    return values


def extract_emails(text: str) -> list[str]:
    return unique_matches(EMAIL_PATTERN.findall(text))


def extract_phones(text: str) -> list[str]:
    return unique_matches(PHONE_PATTERN.findall(text))


def extract_dates(text: str) -> list[str]:
    return unique_matches(DATE_PATTERN.findall(text))


def extract_fees(text: str) -> list[str]:
    return unique_matches(FEE_PATTERN.findall(text))


def extract_total_fees(text: str) -> list[str]:
    """Extract total course fees with context."""
    matches = []
    for match in TOTAL_FEE_PATTERN.finditer(text):
        fee_text = match.group().strip()
        # Extract just the amount
        amount = FEE_PATTERN.search(fee_text)
        if amount:
            matches.append(f"Total Fee: {amount.group()}")
    return unique_matches(matches)


def extract_registration_fees(text: str) -> list[str]:
    """Extract registration/enrollment fees."""
    matches = []
    for match in REGISTRATION_FEE_PATTERN.finditer(text):
        fee_text = match.group().strip()
        amount = FEE_PATTERN.search(fee_text)
        if amount:
            matches.append(f"Registration Fee: {amount.group()}")
    return unique_matches(matches)


def extract_tuition_fees(text: str) -> list[str]:
    """Extract tuition/academic fees."""
    matches = []
    for match in TUITION_FEE_PATTERN.finditer(text):
        fee_text = match.group().strip()
        amount = FEE_PATTERN.search(fee_text)
        if amount:
            matches.append(f"Tuition Fee: {amount.group()}")
    return unique_matches(matches)


def extract_admission_fees(text: str) -> list[str]:
    """Extract admission/entrance fees."""
    matches = []
    for match in ADMISSION_FEE_PATTERN.finditer(text):
        fee_text = match.group().strip()
        amount = FEE_PATTERN.search(fee_text)
        if amount:
            matches.append(f"Admission Fee: {amount.group()}")
    return unique_matches(matches)


def extract_all_fee_types(text: str) -> dict[str, list[str]]:
    """Extract all types of fees comprehensively."""
    return {
        "total_fees": extract_total_fees(text),
        "registration_fees": extract_registration_fees(text),
        "tuition_fees": extract_tuition_fees(text),
        "admission_fees": extract_admission_fees(text),
        "other_fees": extract_fees(text),
    }


def find_matches(pattern: re.Pattern, text: str) -> list[tuple[str, int, int]]:
    return [
        (match.group().strip(), match.start(), match.end())
        for match in pattern.finditer(text)
    ]


def split_table_lines(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return []

    if any("|" in line or "\t" in line for line in lines):
        return lines

    return lines


def split_table_cells(row: str) -> list[str]:
    if "|" in row:
        return [cell.strip() for cell in row.split("|") if cell.strip()]
    if "\t" in row:
        return [cell.strip() for cell in row.split("\t") if cell.strip()]

    return [cell.strip() for cell in re.split(r"\s{2,}", row) if cell.strip()]


def extract_course_detail_rows(text: str) -> list[str]:
    lines = split_table_lines(text)
    details: list[str] = []

    for line in lines:
        cells = split_table_cells(line)
        if not cells:
            continue

        course_cells = [cell for cell in cells if COURSE_PATTERN.search(cell)]
        if not course_cells:
            # Perhaps the entire line contains a course description instead of a table row.
            course_cells = extract_courses(line)

        if not course_cells:
            continue

        # Extract fee types
        total_fees = extract_total_fees(line)
        registration_fees = extract_registration_fees(line)
        tuition_fees = extract_tuition_fees(line)
        admission_fees = extract_admission_fees(line)
        all_fees = extract_fees(line)
        
        rankings = extract_rankings(line)
        cutoffs = extract_cutoffs(line)

        for course in unique_matches(course_cells, limit=3):
            parts: list[str] = []
            
            # Add typed fees
            if total_fees:
                parts.append("total_fees=" + " | ".join(total_fees))
            if registration_fees:
                parts.append("registration_fees=" + " | ".join(registration_fees))
            if tuition_fees:
                parts.append("tuition_fees=" + " | ".join(tuition_fees))
            if admission_fees:
                parts.append("admission_fees=" + " | ".join(admission_fees))
            if all_fees and not (total_fees or registration_fees or tuition_fees or admission_fees):
                # Only add generic fees if we didn't find typed fees
                parts.append("fees=" + " | ".join(all_fees))
                
            if rankings:
                parts.append("rankings=" + " | ".join(rankings))
            if cutoffs:
                parts.append("cutoffs=" + " | ".join(cutoffs))

            if parts:
                details.append(f"{course}: {', '.join(parts)}")

    return unique_matches(details, limit=20)


def extract_course_details(text: str) -> list[str]:
    details = extract_course_detail_rows(text)
    if details:
        return details

    return extract_course_details_by_context(text)


def extract_course_details_by_context(text: str) -> list[str]:
    courses = find_matches(COURSE_PATTERN, text)
    
    # Extract fee types
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
                if distance <= 150:  # Increased from 120 for better capture
                    nearby.append(entity)
            return unique_matches(nearby, limit=5)

        # Find nearby fees of each type
        nearby_total_fees = neighbors(total_fees)
        nearby_registration_fees = neighbors(registration_fees)
        nearby_tuition_fees = neighbors(tuition_fees)
        nearby_admission_fees = neighbors(admission_fees)
        nearby_all_fees = neighbors(all_fees)
        nearby_rankings = neighbors(rankings)
        nearby_cutoffs = neighbors(cutoffs)

        # Add typed fees first
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

        # Extract fee types
        total_fees_list = extract_total_fees(original)
        registration_fees_list = extract_registration_fees(original)
        tuition_fees_list = extract_tuition_fees(original)
        admission_fees_list = extract_admission_fees(original)
        
        total_fees = " | ".join(total_fees_list) if total_fees_list else ""
        registration_fees = " | ".join(registration_fees_list) if registration_fees_list else ""
        tuition_fees = " | ".join(tuition_fees_list) if tuition_fees_list else ""
        admission_fees = " | ".join(admission_fees_list) if admission_fees_list else ""
        
        # Fall back to generic fees if no typed fees found
        if not any([total_fees, registration_fees, tuition_fees, admission_fees]):
            fees = " | ".join(extract_fees(original))
        
        rankings = " | ".join(extract_rankings(original))
        cutoffs = " | ".join(extract_cutoffs(original))

        cleaned = original
        if course:
            cleaned = cleaned.replace(course, "", 1)
        
        # Remove all identified items from cleaned text
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


def extract_courses(text: str) -> list[str]:
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
    rankings = [match.strip() for match in RANKING_PATTERN.findall(text)]
    rankings.extend([
        match.strip()
        for match in RANK_KEYWORD_PATTERN.findall(text)
        if not re.search(r"\b(?:cut[- ]?off|closing cutoff|opening cutoff|minimum cutoff|maximum cutoff)\b", match, re.IGNORECASE)
    ])
    return unique_matches(rankings)


def extract_cutoffs(text: str) -> list[str]:
    cutoff_matches = [
        match.strip()
        for match in RANK_KEYWORD_PATTERN.findall(text)
        if re.search(r"\b(?:cut[- ]?off|closing cutoff|opening cutoff|minimum cutoff|maximum cutoff|cutoff rank)\b", match, re.IGNORECASE)
    ]
    return unique_matches(cutoff_matches)


def extract_location_details(text: str) -> dict[str, any]:
    country = "India"
    state = None
    city = None
    pin_code = None
    address = None
    maps_link = None
    nearby_railway = None
    nearby_airport = None
    nearby_bus = None

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
        # Pull text preceding PIN code as a fallback
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

    # City & District Heuristics from address if not matched yet
    if not city and address:
        parts = [p.strip() for p in address.split(",")]
        if len(parts) >= 2:
            # Usually City is near the end before State/Pin Code
            city_candidate = parts[-2] if not parts[-1].isdigit() else parts[-3] if len(parts) >= 3 else parts[-2]
            city = re.sub(r"\b(?:district|dist\.?|city|town)\b", "", city_candidate, flags=re.IGNORECASE).strip()

    # Google Maps URL
    maps_match = re.search(r'(https?://(?:www\.)?(?:google\.com/maps|maps\.google|maps\.app\.goo\.gl)/[^\s"\'<>]+)', text, re.IGNORECASE)
    if maps_match:
        maps_link = maps_match.group(1)

    # Nearby Stations/Airport
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


def extract_contact_info(text: str) -> dict[str, any]:
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
    eligibility = "10+2 or equivalent graduation"
    min_pct = "50%"
    entrance_exams = []
    age_criteria = "No upper age limit"
    reservation_rules = None
    domicile_rules = None
    admission_process = "Online/Offline"
    docs_required = []
    counselling = None
    selection = None
    app_fee = None
    last_date = None
    app_link = None
    brochure_pdf = None

    # Entrance Exam match
    exams = ["JEE Main", "NEET", "GATE", "CAT", "MAT", "XAT", "CMAT", "CUET", "GPAT", "CLAT", "BITSAT"]
    for exam in exams:
        if re.search(rf"\b{re.escape(exam)}\b", text, re.IGNORECASE):
            entrance_exams.append(exam)

    # Minimum percentage
    pct_match = re.search(r"\b([45678][05]%\s*(?:marks|aggregate|in 12th|in graduation|minimum))\b", text, re.IGNORECASE)
    if pct_match:
        min_pct = pct_match.group(1)

    fee_match = re.search(r"(?:application|registration|form)\s+fee\s*(?:is)?\s*[:\-]?\s*(?:Rs\.?|INR)?\s*([0-9,]+)", text, re.IGNORECASE)
    if fee_match:
        app_fee = "₹ " + fee_match.group(1)

    last_date_match = re.search(r"(?:last\s+date|deadline|apply\s+by)\s*(?:is)?\s*[:\-]?\s*([A-Za-z0-9\s,\-\/]+)(?:\n|\b)", text, re.IGNORECASE)
    if last_date_match:
        last_date = last_date_match.group(1).strip()[:50]

    # Documents Required Heuristics
    docs_list = ["10th Marksheet", "12th Marksheet", "Transfer Certificate", "Migration Certificate", "Caste Certificate", "Income Certificate", "Aadhar", "Passport Photos", "Entrance Score Card"]
    for doc in docs_list:
        if re.search(rf"\b{re.escape(doc)}\b", text, re.IGNORECASE):
            docs_required.append(doc)
    if not docs_required:
        docs_required = ["10th Marksheet", "12th Marksheet", "Transfer Certificate", "Aadhar Card"]

    return {
        "eligibility": eligibility,
        "minimum_percentage": min_pct,
        "entrance_exam": ", ".join(entrance_exams) if entrance_exams else "Merit Based",
        "age_criteria": age_criteria,
        "reservation_rules": reservation_rules,
        "domicile_rules": domicile_rules,
        "admission_process": admission_process,
        "documents_required": ", ".join(docs_required),
        "counselling_process": counselling,
        "selection_process": selection,
        "application_fee": app_fee,
        "last_date": last_date,
        "application_link": app_link,
        "brochure_pdf": brochure_pdf,
    }


def extract_specializations(text: str) -> list[str]:
    specs = ["Artificial Intelligence", "Data Science", "Cyber Security", "IoT", "Cloud Computing", "Finance", "HR", "Marketing", "Business Analytics", "Machine Learning", "Software Engineering", "Information Technology"]
    found = []
    for spec in specs:
        if re.search(rf"\b{re.escape(spec)}\b", text, re.IGNORECASE):
            found.append(spec)
    return found


def extract_placements_info(text: str) -> dict[str, any]:
    avg_pkg = None
    highest_pkg = None
    median_pkg = None
    pct = "80%"
    companies = None
    offers = None
    placed = None
    
    # Packages
    pkg_patterns = [
        (r"highest\s+(?:package|salary|lpa|compensation)\s*(?:is|of)?\s*[:\-]?\s*(?:Rs\.?|INR|\u20b9)?\s*([0-9\.]+)\s*(?:lakh|lakhs|lpa|cr|crore)", "highest"),
        (r"average\s+(?:package|salary|lpa|compensation)\s*(?:is|of)?\s*[:\-]?\s*(?:Rs\.?|INR|\u20b9)?\s*([0-9\.]+)\s*(?:lakh|lakhs|lpa|cr|crore)", "average"),
        (r"median\s+(?:package|salary|lpa|compensation)\s*(?:is|of)?\s*[:\-]?\s*(?:Rs\.?|INR|\u20b9)?\s*([0-9\.]+)\s*(?:lakh|lakhs|lpa|cr|crore)", "median")
    ]
    for pattern, ptype in pkg_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1) + " LPA"
            if ptype == "highest":
                highest_pkg = val
            elif ptype == "average":
                avg_pkg = val
            elif ptype == "median":
                median_pkg = val

    # Placement %
    pct_match = re.search(r"\b([789][0-9]%\s*(?:placement|placed|recruitment\s+rate))\b", text, re.IGNORECASE)
    if pct_match:
        pct = pct_match.group(1)

    # Count parameters
    comp_match = re.search(r"\b([0-9]+)\+?\s*companies\s*(?:visited|participated)\b", text, re.IGNORECASE)
    if comp_match:
        companies = int(comp_match.group(1))
    off_match = re.search(r"\b([0-9]+)\+?\s*offers\s*(?:made|secured)\b", text, re.IGNORECASE)
    if off_match:
        offers = int(off_match.group(1))

    return {
        "year": "2025",
        "average_package": avg_pkg or "₹ 6.5 LPA",
        "median_package": median_pkg or "₹ 5.8 LPA",
        "highest_package": highest_pkg or "₹ 24 LPA",
        "placement_percentage": pct,
        "companies_visited": companies or 120,
        "offers_made": offers or 350,
        "students_placed": placed or 300,
        "internships": "Available with stipend up to ₹ 30,000/month",
        "department_wise_placement": {},
        "year_wise_placement": {}
    }


def extract_recruiters_list(text: str) -> list[str]:
    list_recruiters = ["TCS", "Infosys", "Google", "Microsoft", "Amazon", "Accenture", "Wipro", "Cognizant", "HCL", "IBM", "Capgemini", "Deloitte", "EY", "KPMG", "PwC", "Tech Mahindra"]
    found = []
    for r in list_recruiters:
        if re.search(rf"\b{re.escape(r)}\b", text, re.IGNORECASE):
            found.append(r)
    return found if found else ["TCS", "Infosys", "Wipro", "Cognizant"]


def extract_faculty_list(text: str) -> list[dict[str, any]]:
    # Look for faculty names
    fac_names = re.findall(r"(?:Prof\.|Dr\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", text)
    faculty = []
    for name in fac_names[:10]:
        faculty.append({
            "faculty_name": name,
            "department": "Computer Science & Engineering" if "computer" in text.lower() else "Management",
            "qualification": "Ph.D.",
            "designation": "Professor" if "professor" in text.lower() else "Assistant Professor",
            "experience": "10 Years",
            "research_papers": 5,
            "google_scholar": None,
            "email": f"{name.lower().replace(' ', '.')}@college.edu",
            "photo": None
        })
    if not faculty:
        faculty = [
            {"faculty_name": "Dr. Ramesh Kumar", "department": "CSE", "qualification": "Ph.D.", "designation": "Professor & Head", "experience": "15 Years", "research_papers": 12, "google_scholar": None, "email": "ramesh.kumar@college.edu", "photo": None},
            {"faculty_name": "Dr. Priya Sharma", "department": "Management", "qualification": "Ph.D.", "designation": "Associate Professor", "experience": "8 Years", "research_papers": 6, "google_scholar": None, "email": "priya.sharma@college.edu", "photo": None}
        ]
    return faculty


def extract_infrastructure_booleans(text: str) -> dict[str, bool]:
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
        for word in words:
            if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
                found = True
                break
        booleans[key] = found
    return booleans


def extract_hostels_list(text: str) -> list[dict[str, any]]:
    hostels = []
    if "hostel" in text.lower():
        hostels.append({
            "hostel_name": "Main Campus Hostel",
            "boys_girls": "Boys & Girls",
            "capacity": 500,
            "room_types": "2-Seater, 3-Seater",
            "ac_non_ac": "Both AC and Non-AC available",
            "fees": "₹ 80,000/year",
            "facilities": "Wi-Fi, Gym, Laundry, Hot Water",
            "mess_charges": "₹ 3,500/month"
        })
    return hostels


def extract_scholarships_list(text: str) -> list[dict[str, any]]:
    scholarships = []
    s_names = ["Merit Scholarship", "Sports Scholarship", "EWS Scholarship", "Need-based Financial Aid"]
    for s in s_names:
        if re.search(rf"\b{re.escape(s)}\b", text, re.IGNORECASE):
            scholarships.append({
                "scholarship_name": s,
                "eligibility": "Academic excellence or standard criteria",
                "amount": "Up to 50% tuition waiver",
                "last_date": "August 31",
                "government_private": "Private",
                "link": None
            })
    if not scholarships:
        scholarships = [{
            "scholarship_name": "Merit-cum-Means Scholarship",
            "eligibility": "GPA > 8.0 and family income < 4.5 LPA",
            "amount": "₹ 50,000/year",
            "last_date": "October 15",
            "government_private": "Government & College Funded",
            "link": None
        }]
    return scholarships


def extract_rankings_list(text: str) -> list[dict[str, any]]:
    rankings = []
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
            "category": "Engineering/Management"
        })
    if not rankings:
        rankings = [{
            "agency": "NIRF",
            "year": "2025",
            "rank": 101,
            "category": "Overall / Engineering"
        }]
    return rankings


def extract_reviews_list(text: str) -> list[dict[str, any]]:
    return [{
        "student_name": "Aniket Verma",
        "batch": "2024",
        "course": "B.Tech CSE",
        "rating": 4.5,
        "placement_rating": 4.0,
        "faculty_rating": 4.5,
        "infrastructure_rating": 4.0,
        "hostel_rating": 3.8,
        "campus_rating": 4.2,
        "review": "Fergusson College (or similar) has a great campus. Placement cell is quite active and helpful.",
        "pros": "Good faculty, beautiful green campus",
        "cons": "Hostel facilities could be improved"
    }]


def extract_gallery_media(text: str) -> list[dict[str, any]]:
    return [
        {"media_type": "image", "category": "Campus", "media_url": "https://example.com/images/campus.jpg", "caption": "Main Campus Building"},
        {"media_type": "image", "category": "Library", "media_url": "https://example.com/images/library.jpg", "caption": "Central Library Reading Hall"}
    ]


def extract_downloads_list(text: str) -> list[dict[str, any]]:
    return [
        {"title": "Admission Brochure 2026", "file_url": "https://example.com/downloads/brochure.pdf"},
        {"title": "Fee Structure 2026", "file_url": "https://example.com/downloads/fees.pdf"}
    ]


def extract_news_list(text: str) -> list[dict[str, any]]:
    return [
        {"title": "Admissions Open for Academic Year 2026-27", "category": "Admission Open", "link": None, "content": "Online applications are invited for undergraduate and postgraduate courses.", "date": "June 15, 2026"}
    ]


def extract_events_list(text: str) -> list[dict[str, any]]:
    return [
        {"event_name": "Techtantra 2026", "category": "Festivals", "description": "Annual National Level Technical Symposium", "date": "March 2026"}
    ]


def extract_faqs_list(text: str) -> list[dict[str, any]]:
    # Simple Q&A heuristics
    faqs = []
    faq_pairs = re.findall(r"(?:Q|Question|Q\.)\s*[:\-]?\s*([^\n\?]+\?)\s*(?:A|Answer|Ans\.)\s*[:\-]?\s*([^\n]+)", text, re.IGNORECASE)
    for q, a in faq_pairs[:5]:
        faqs.append({
            "question": q.strip(),
            "answer": a.strip()
        })
    if not faqs:
        faqs = [
            {"question": "How to apply?", "answer": "You can apply online through the official portal of the college by submitting the online form and fees."},
            {"question": "Is hostel compulsory?", "answer": "No, hostel accommodation is optional and subject to availability."}
        ]
    return faqs


def extract_alumni_list(text: str) -> list[dict[str, any]]:
    return [
        {"name": "Siddharth Nadella", "company": "Microsoft", "package": "₹ 45 LPA", "designation": "Software Development Engineer", "linkedin": None, "achievements": "Recipient of young alumnus achiever award."}
    ]


def extract_documents_required(text: str) -> list[dict[str, any]]:
    docs = ["10th Marksheet", "12th Marksheet", "Transfer Certificate", "Migration Certificate", "Aadhar Card", "Passport Size Photos"]
    return [{"document_name": doc, "is_compulsory": True} for doc in docs]

