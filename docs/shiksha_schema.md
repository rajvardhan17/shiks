# Shiksha-like Target Data Schema

This document defines the target schema (logical) for college/course data and maps fields to the project's existing SQLAlchemy models in `db/models.py`.

## Top-level objects

- college: core college metadata
- courses: list of courses offered
- specializations: course specializations (optional tie to course)
- fees: per-course or general fees
- admissions: admission details
- placements: placement stats
- contacts: phone, email, website, social
- seo: SEO metadata and schema markup
- raw_page: raw scraped page info (keeps provenance)

---

## `college` (maps to `College` model)
- `college_id` (string) : unique id / source id
- `name` (string) : college name
- `short_name` (string)
- `type` (string) : Government / Private / Deemed / Autonomous
- `university_affiliation` (string)
- `ownership` (string)
- `year_established` (string)
- `accreditation` (string)
- `approval` (string)
- `campus_size` (string)
- `website` (string)
- `logo`, `cover_image` (string)
- `description`, `highlights` (string/text)
- `location` (object): `country`, `state`, `city`, `district`, `address`, `pin_code`, `latitude`, `longitude`, `google_maps_link`
- `contact` (object): `admission_email`, `general_email`, `phone_numbers` (list), `whatsapp_number`, `admission_helpline`, `fax`, `social_media_links` (object/dict)

## `courses` (maps to `Course` model)
Each entry:
- `name` (string)
- `degree` (string) e.g. `B.Tech`, `MBA`
- `stream` (string) e.g. `Engineering`, `Management`
- `duration`, `mode`, `intake`, `seats`
- `eligibility` (text)
- `entrance_exam` (string)
- `fees` (string or object)
- `syllabus_pdf`, `curriculum`, `course_brochure`

## `specializations` (maps to `Specialization`)
- `specialization_name` (string)
- `stream` (string)
- optional link: `course_name` or `course_id`

## `fees` (maps to `Fee`)
Fees can be per-course or general; each entry:
- `course_name` (optional)
- `tuition_fee`, `hostel_fee`, `exam_fee`, `library_fee`, `transport_fee`, `miscellaneous_fee`, `total_annual_fee`, `total_course_fee`
- `raw` (string) - original scraped text
- `amount` (string / digits-only) - normalized numeric value

## `admissions` (maps to `Admission`)
- `eligibility`, `minimum_percentage`, `entrance_exam`, `age_criteria`, `reservation_rules`, `domicile_rules`, `admission_process`, `documents_required`, `counselling_process`, `selection_process`, `application_fee`, `last_date`, `application_link`, `brochure_pdf`

## `placements` (maps to `Placement`)
- `year`, `average_package`, `median_package`, `highest_package`, `placement_percentage`, `companies_visited`, `offers_made`, `students_placed`, `internships`, `department_wise_placement` (JSON), `year_wise_placement` (JSON)

## `seo` (maps to `SEOMetadata`)
- `meta_title`, `meta_description`, `slug`, `canonical_url`, `keywords`, `schema_markup` (JSON-LD)

## `raw_page` (maps to `RawPage`)
- `page_url`, `content`, `table_content`, `page_title`, `headings`, `meta` (JSON), `links` (JSON), `images` (JSON), `json_ld` (JSON), `structured_facts` (JSON), `checksum`, `status`, `error`, `fetched_at`

---

## Sample normalized payload (JSON)

{
  "college": {
    "college_id": "mamc_001",
    "name": "Maharaja Agrasen Medical College",
    "website": "https://www.mamc.ac.in",
    "state": "Haryana",
    "city": "[City]",
    "description": "Short description...",
    "contact": {
      "phone_numbers": ["+91 12345 67890"],
      "emails": ["admissions@mamc.ac.in"],
      "social_media_links": {"facebook": "..."}
    }
  },
  "courses": [
    {"name": "MBBS", "degree": "MBBS", "duration": "5.5 Years", "entrance_exam": "NEET"},
    {"name": "MD - General Medicine", "degree": "MD", "duration": "3 Years"}
  ],
  "specializations": [
    {"specialization_name": "Cardiology", "stream": "Medical", "course_name": "MD - General Medicine"}
  ],
  "fees": [
    {"course_name": "MBBS", "amount": "1500000", "raw": "Rs. 15,00,000 (total course fee)"}
  ],
  "admissions": {"eligibility": "NEET qualified", "application_link": "https://..."},
  "placements": [],
  "seo": {"meta_title": "MAMC - Admissions 2026", "schema_markup": {}},
  "raw_page": {"page_url": "https://www.mamc.ac.in/admissions", "status": "new"}
}

---

## Notes & next steps
- The existing `normalize_and_validate_payload` in `pipeline/validators.py` already outputs a minimal normalized payload compatible with `db.models` for `college`, `courses`, `fees`, and `contacts`.
- Next: pick source sites and a minimal field subset to implement extractor updates (e.g., `name`, `website`, `courses[].name`, `fees`, `contacts`).

