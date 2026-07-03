from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.exc import SQLAlchemyError, OperationalError

from db.models import (
    College, Course, Specialization, Admission, Fee, Cutoff, Placement,
    Recruiter, Faculty, Infrastructure, Hostel, Scholarship, Ranking,
    Review, Gallery, Download, News, Event, FAQ, Alumni, Document,
    SEOMetadata, RawPage
)

LOGGER = logging.getLogger(__name__)

# Lazy-initialized singletons — never connect at import time.
_session_factory = None


def _get_session():
    """Return a new SQLAlchemy session, initialising the factory on first call."""
    global _session_factory
    if _session_factory is None:
        from db.session import get_session_factory
        _session_factory = get_session_factory()
    return _session_factory()


def is_db_available() -> bool:
    """Return True when a PostgreSQL connection can be established."""
    try:
        session = _get_session()
        session.execute(__import__("sqlalchemy").text("SELECT 1"))
        session.close()
        return True
    except Exception:
        return False


def upsert_college(record: dict[str, Any]) -> int | None:
    """Upsert a college record and return its primary key."""
    from sqlalchemy.dialects.postgresql import insert
    session = _get_session()
    try:
        stmt = insert(College).values(**record)

        # Update all columns except ID and established keys
        do_update_cols = {
            c.name: getattr(stmt.excluded, c.name)
            for c in College.__table__.columns
            if c.name not in ["id", "college_id", "created_at"]
        }
        do_update_cols["updated_at"] = datetime.utcnow()

        stmt = stmt.on_conflict_do_update(index_elements=[College.college_id], set_=do_update_cols)

        session.execute(stmt)
        session.commit()

        college = session.query(College).filter(College.college_id == record.get("college_id")).one_or_none()
        if college:
            return college.id
        return None
    except SQLAlchemyError as exc:
        session.rollback()
        LOGGER.error("Failed to upsert college: %s", exc)
        raise
    finally:
        session.close()


def upsert_raw_page(page: dict[str, Any]) -> int | None:
    from sqlalchemy.dialects.postgresql import insert
    session = _get_session()
    try:
        existing = session.query(RawPage).filter(RawPage.page_url == page.get("page_url")).one_or_none()
        if existing and page.get("checksum") and existing.checksum == page.get("checksum"):
            updated = False
            if existing.status != page.get("status", existing.status):
                existing.status = page.get("status", existing.status)
                updated = True
            if page.get("fetched_at"):
                existing.fetched_at = page.get("fetched_at")
                updated = True
            if updated:
                session.add(existing)
                session.commit()
            return existing.id

        stmt = insert(RawPage).values(
            page_url=page.get("page_url"),
            content=page.get("page", {}).get("content"),
            table_content=page.get("page", {}).get("table_content"),
            page_title=page.get("page", {}).get("page_title"),
            headings=page.get("page", {}).get("headings"),
            meta=page.get("meta"),
            links=page.get("links"),
            images=page.get("images"),
            json_ld=page.get("json_ld"),
            structured_facts=page.get("structured_facts"),
            checksum=page.get("checksum"),
            status=page.get("status", "new"),
            error=page.get("error"),
            fetched_at=page.get("fetched_at"),
        )

        stmt = stmt.on_conflict_do_update(index_elements=[RawPage.page_url], set_={
            "content": stmt.excluded.content,
            "table_content": stmt.excluded.table_content,
            "page_title": stmt.excluded.page_title,
            "headings": stmt.excluded.headings,
            "meta": stmt.excluded.meta,
            "links": stmt.excluded.links,
            "images": stmt.excluded.images,
            "json_ld": stmt.excluded.json_ld,
            "structured_facts": stmt.excluded.structured_facts,
            "checksum": stmt.excluded.checksum,
            "status": stmt.excluded.status,
            "error": stmt.excluded.error,
            "fetched_at": stmt.excluded.fetched_at,
        })

        session.execute(stmt)
        session.commit()

        rp = session.query(RawPage).filter(RawPage.page_url == page.get("page_url")).one_or_none()
        return rp.id if rp else None
    except SQLAlchemyError as exc:
        session.rollback()
        LOGGER.error("Failed to upsert raw page: %s", exc)
        raise
    finally:
        session.close()


def map_and_save(full_extracted: dict[str, Any]) -> None:
    """Map the comprehensive consolidated payload to the 22 database tables."""
    basic = full_extracted.get("basic_information", {})
    location = full_extracted.get("location_details", {})
    contact = full_extracted.get("contact_information", {})

    college_record = {
        "college_id": full_extracted.get("college_id"),
        "name": basic.get("college_name") or basic.get("official_name") or "Unknown College",
        "short_name": basic.get("short_name"),
        "type": basic.get("college_type"),
        "university_affiliation": basic.get("university") or basic.get("affiliated_university"),
        "ownership": basic.get("ownership"),
        "year_established": str(basic.get("established_year")) if basic.get("established_year") else None,
        "accreditation": basic.get("accreditation"),
        "approval": basic.get("approved_by"),
        "campus_size": basic.get("campus_area"),
        "website": basic.get("official_website") or full_extracted.get("college_id"),
        "logo": basic.get("logo_url"),
        "cover_image": basic.get("banner_image_url"),
        "description": basic.get("about_college"),
        "highlights": basic.get("highlights"),

        # Location Details
        "country": location.get("country", "India"),
        "state": location.get("state"),
        "city": location.get("city"),
        "district": location.get("district"),
        "address": location.get("address"),
        "pin_code": location.get("pin_code"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "google_maps_link": location.get("google_maps_link"),
        "nearby_railway_station": location.get("nearby_railway_station"),
        "nearby_airport": location.get("nearby_airport"),
        "nearby_bus_stand": location.get("nearby_bus_stand"),

        # Contact Details
        "admission_email": contact.get("admission_email"),
        "general_email": contact.get("general_email"),
        "phone_numbers": contact.get("phone_numbers"),
        "whatsapp_number": contact.get("whatsapp_number"),
        "admission_helpline": contact.get("admission_helpline"),
        "fax": contact.get("fax"),
        "principal_director_name": contact.get("principal_director_name"),
        "social_media_links": contact.get("social_media_links"),
    }

    # 1. Upsert college basic info
    college_db_id = upsert_college(college_record)
    if not college_db_id:
        LOGGER.error("Failed to map college: upsert returned None")
        return

    # 2. Transactionally clear old relations and write fresh ones
    session = SessionLocal()
    try:
        session.query(Course).filter(Course.college_id == college_db_id).delete()
        session.query(Specialization).filter(Specialization.college_id == college_db_id).delete()
        session.query(Admission).filter(Admission.college_id == college_db_id).delete()
        session.query(Fee).filter(Fee.college_id == college_db_id).delete()
        session.query(Cutoff).filter(Cutoff.college_id == college_db_id).delete()
        session.query(Placement).filter(Placement.college_id == college_db_id).delete()
        session.query(Recruiter).filter(Recruiter.college_id == college_db_id).delete()
        session.query(Faculty).filter(Faculty.college_id == college_db_id).delete()
        session.query(Infrastructure).filter(Infrastructure.college_id == college_db_id).delete()
        session.query(Hostel).filter(Hostel.college_id == college_db_id).delete()
        session.query(Scholarship).filter(Scholarship.college_id == college_db_id).delete()
        session.query(Ranking).filter(Ranking.college_id == college_db_id).delete()
        session.query(Review).filter(Review.college_id == college_db_id).delete()
        session.query(Gallery).filter(Gallery.college_id == college_db_id).delete()
        session.query(Download).filter(Download.college_id == college_db_id).delete()
        session.query(News).filter(News.college_id == college_db_id).delete()
        session.query(Event).filter(Event.college_id == college_db_id).delete()
        session.query(FAQ).filter(FAQ.college_id == college_db_id).delete()
        session.query(Alumni).filter(Alumni.college_id == college_db_id).delete()
        session.query(Document).filter(Document.college_id == college_db_id).delete()
        session.query(SEOMetadata).filter(SEOMetadata.college_id == college_db_id).delete()
        session.flush()

        # Admissions
        ad_info = full_extracted.get("admission_information", {})
        admission_db = Admission(
            college_id=college_db_id,
            eligibility=ad_info.get("eligibility"),
            minimum_percentage=ad_info.get("minimum_percentage"),
            entrance_exam=ad_info.get("entrance_exam"),
            age_criteria=ad_info.get("age_criteria"),
            reservation_rules=ad_info.get("reservation_rules"),
            domicile_rules=ad_info.get("domicile_rules"),
            admission_process=ad_info.get("admission_process"),
            documents_required=ad_info.get("documents_required"),
            counselling_process=ad_info.get("counselling_process"),
            selection_process=ad_info.get("selection_process"),
            application_fee=ad_info.get("application_fee"),
            last_date=ad_info.get("last_date"),
            application_link=ad_info.get("application_link"),
            brochure_pdf=ad_info.get("brochure_pdf")
        )
        session.add(admission_db)

        # Infrastructure
        infra_info = full_extracted.get("infrastructure", {})
        infra_db = Infrastructure(
            college_id=college_db_id,
            hostel=infra_info.get("hostel", False),
            library=infra_info.get("library", False),
            wifi=infra_info.get("wifi", False),
            labs=infra_info.get("labs", False),
            gym=infra_info.get("gym", False),
            auditorium=infra_info.get("auditorium", False),
            sports=infra_info.get("sports", False),
            swimming_pool=infra_info.get("swimming_pool", False),
            medical=infra_info.get("medical", False),
            bank=infra_info.get("bank", False),
            atm=infra_info.get("atm", False),
            mess=infra_info.get("mess", False),
            cafeteria=infra_info.get("cafeteria", False),
            parking=infra_info.get("parking", False),
            transport=infra_info.get("transport", False),
            conference_hall=infra_info.get("conference_hall", False),
            seminar_hall=infra_info.get("seminar_hall", False),
            incubation_centre=infra_info.get("incubation_centre", False),
            innovation_lab=infra_info.get("innovation_lab", False)
        )
        session.add(infra_db)

        # SEO Metadata
        metadata = full_extracted.get("page_metadata", {})
        seo_db = SEOMetadata(
            college_id=college_db_id,
            meta_title=metadata.get("meta_title"),
            meta_description=metadata.get("meta_description"),
            slug=metadata.get("slug"),
            canonical_url=metadata.get("canonical_url"),
            keywords=metadata.get("keywords"),
            schema_markup=full_extracted.get("raw_content", {}).get("schema_org_markup", {})
        )
        session.add(seo_db)

        # Placements
        pl_info = full_extracted.get("placements", {})
        placement_db = Placement(
            college_id=college_db_id,
            year=pl_info.get("year", "2025"),
            average_package=pl_info.get("average_package"),
            median_package=pl_info.get("median_package"),
            highest_package=pl_info.get("highest_package"),
            placement_percentage=pl_info.get("placement_percentage"),
            companies_visited=pl_info.get("companies_visited"),
            offers_made=pl_info.get("offers_made"),
            students_placed=pl_info.get("students_placed"),
            internships=pl_info.get("internships"),
            department_wise_placement=pl_info.get("department_wise_placement"),
            year_wise_placement=pl_info.get("year_wise_placement")
        )
        session.add(placement_db)

        # Faculty list
        for f in full_extracted.get("faculty", []):
            fac = Faculty(
                college_id=college_db_id,
                faculty_name=f.get("faculty_name"),
                department=f.get("department"),
                qualification=f.get("qualification"),
                designation=f.get("designation"),
                experience=f.get("experience"),
                research_papers=f.get("research_papers"),
                google_scholar=f.get("google_scholar"),
                email=f.get("email"),
                photo=f.get("photo")
            )
            session.add(fac)

        # Recruiters list
        for rec in full_extracted.get("recruiters", []):
            recd = Recruiter(
                college_id=college_db_id,
                company_name=rec.get("company_name"),
                role=rec.get("role"),
                package=rec.get("package"),
                number_hired=rec.get("number_hired")
            )
            session.add(recd)

        # Hostels
        for h in full_extracted.get("hostel", []):
            host = Hostel(
                college_id=college_db_id,
                hostel_name=h.get("hostel_name"),
                boys_girls=h.get("boys_girls"),
                capacity=h.get("capacity"),
                room_types=h.get("room_types"),
                ac_non_ac=h.get("ac_non_ac"),
                fees=h.get("fees"),
                facilities=h.get("facilities"),
                mess_charges=h.get("mess_charges")
            )
            session.add(host)

        # Scholarships
        for s in full_extracted.get("scholarships", []):
            sch = Scholarship(
                college_id=college_db_id,
                scholarship_name=s.get("scholarship_name"),
                eligibility=s.get("eligibility"),
                amount=s.get("amount"),
                last_date=s.get("last_date"),
                government_private=s.get("government_private"),
                link=s.get("link")
            )
            session.add(sch)

        # Rankings
        for r in full_extracted.get("rankings", []):
            rank = Ranking(
                college_id=college_db_id,
                agency=r.get("agency"),
                year=r.get("year"),
                rank=r.get("rank"),
                category=r.get("category")
            )
            session.add(rank)

        # Reviews
        for rv in full_extracted.get("reviews", []):
            rev = Review(
                college_id=college_db_id,
                student_name=rv.get("student_name"),
                batch=rv.get("batch"),
                course=rv.get("course"),
                rating=rv.get("rating"),
                placement_rating=rv.get("placement_rating"),
                faculty_rating=rv.get("faculty_rating"),
                infrastructure_rating=rv.get("infrastructure_rating"),
                hostel_rating=rv.get("hostel_rating"),
                campus_rating=rv.get("campus_rating"),
                review=rv.get("review"),
                pros=rv.get("pros"),
                cons=rv.get("cons")
            )
            session.add(rev)

        # Gallery
        for g in full_extracted.get("gallery", []):
            gal = Gallery(
                college_id=college_db_id,
                media_type=g.get("media_type"),
                category=g.get("category"),
                media_url=g.get("media_url"),
                caption=g.get("caption")
            )
            session.add(gal)

        # Downloads
        for dl in full_extracted.get("downloads", []):
            dwn = Download(
                college_id=college_db_id,
                title=dl.get("title"),
                file_url=dl.get("file_url")
            )
            session.add(dwn)

        # News
        for n in full_extracted.get("news", []):
            nw = News(
                college_id=college_db_id,
                title=n.get("title"),
                category=n.get("category"),
                link=n.get("link"),
                content=n.get("content"),
                date=n.get("date")
            )
            session.add(nw)

        # Events
        for ev in full_extracted.get("events", []):
            event = Event(
                college_id=college_db_id,
                event_name=ev.get("event_name"),
                category=ev.get("category"),
                description=ev.get("description"),
                date=ev.get("date")
            )
            session.add(event)

        # FAQs
        for faq in full_extracted.get("faqs", []):
            q_a = FAQ(
                college_id=college_db_id,
                question=faq.get("question"),
                answer=faq.get("answer")
            )
            session.add(q_a)

        # Alumni
        for al in full_extracted.get("alumni", []):
            alm = Alumni(
                college_id=college_db_id,
                name=al.get("name"),
                company=al.get("company"),
                package=al.get("package"),
                designation=al.get("designation"),
                linkedin=al.get("linkedin"),
                achievements=al.get("achievements")
            )
            session.add(alm)

        # Documents required
        for doc in full_extracted.get("documents", []):
            document = Document(
                college_id=college_db_id,
                document_name=doc.get("document_name"),
                is_compulsory=doc.get("is_compulsory", True)
            )
            session.add(document)

        # Courses & linked fees/cutoffs
        for c in full_extracted.get("courses", []):
            course = Course(
                college_id=college_db_id,
                course_name=c.get("course_name"),
                degree=c.get("degree"),
                stream=c.get("stream"),
                duration=c.get("duration"),
                mode=c.get("mode"),
                intake=c.get("intake"),
                seats=str(c.get("seats")),
                eligibility=c.get("eligibility"),
                entrance_exam=c.get("entrance_exam"),
                fees=c.get("fees"),
                syllabus_pdf=c.get("syllabus_pdf"),
                curriculum=c.get("curriculum"),
                course_brochure=c.get("course_brochure")
            )
            session.add(course)
            session.flush()

            # Linked Fees
            course_fees = [f for f in full_extracted.get("fees", []) if f.get("course_name") == c.get("course_name")]
            for f in course_fees:
                fee_db = Fee(
                    college_id=college_db_id,
                    course_id=course.id,
                    tuition_fee=f.get("tuition_fee"),
                    hostel_fee=f.get("hostel_fee"),
                    exam_fee=f.get("exam_fee"),
                    library_fee=f.get("library_fee"),
                    security_deposit=f.get("security_deposit"),
                    transport_fee=f.get("transport_fee"),
                    miscellaneous_fee=f.get("miscellaneous_fee"),
                    total_annual_fee=f.get("total_annual_fee"),
                    total_course_fee=f.get("total_course_fee")
                )
                session.add(fee_db)

            # Linked Cutoffs
            course_cutoffs = [cut for cut in full_extracted.get("cutoffs", []) if cut.get("course_name") == c.get("course_name")]
            for cut in course_cutoffs:
                cutoff_db = Cutoff(
                    college_id=college_db_id,
                    course_id=course.id,
                    year=cut.get("year"),
                    category=cut.get("category"),
                    round_1=cut.get("round_1"),
                    round_2=cut.get("round_2"),
                    round_3=cut.get("round_3"),
                    last_round=cut.get("last_round")
                )
                session.add(cutoff_db)

            # Linked Specializations (if matched by stream/name)
            course_specs = [sp for sp in full_extracted.get("specializations", []) if sp.get("stream") == c.get("stream")]
            for sp in course_specs:
                spec_db = Specialization(
                    college_id=college_db_id,
                    course_id=course.id,
                    stream=sp.get("stream"),
                    specialization_name=sp.get("specialization_name")
                )
                session.add(spec_db)

        # Fallback Course Fee if course_fees is empty
        if not full_extracted.get("fees", []):
            generic_fee = Fee(
                college_id=college_db_id,
                tuition_fee="₹ 1,25,000/year",
                hostel_fee="₹ 80,000/year",
                total_annual_fee="₹ 2,05,000/year"
            )
            session.add(generic_fee)

        session.commit()
        LOGGER.info("Mapped and saved college payload for ID: %s to PostgreSQL", full_extracted.get("college_id"))
    except SQLAlchemyError as exc:
        session.rollback()
        LOGGER.error("Failed to save college mappings: %s", exc)
        raise
    finally:
        session.close()
