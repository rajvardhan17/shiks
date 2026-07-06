from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert

from ..db.models import (
    Admission,
    College,
    Course,
    Cutoff,
    Fee,
    Faculty,
    Infrastructure,
    Placement,
    Recruiter,
    Scholarship,
    Specialization,
    Ranking,
    Review,
    Gallery,
    Download,
    News,
    Event,
    FAQ,
    Alumni,
    Document,
    SEOMetadata,
    RawPage,
)
from ..db.session import SessionLocal

LOGGER = logging.getLogger(__name__)


class StoragePipeline:
    def __init__(self) -> None:
        self.session_factory = SessionLocal

    def is_db_available(self) -> bool:
        session = self.session_factory()
        try:
            session.execute("SELECT 1")
            return True
        except Exception:
            return False
        finally:
            session.close()

    def upsert_college(self, record: dict[str, Any]) -> int | None:
        session = self.session_factory()
        try:
            stmt = insert(College).values(**record)
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
            return college.id if college else None
        except SQLAlchemyError as exc:
            session.rollback()
            LOGGER.error("Failed to upsert college: %s", exc)
            raise
        finally:
            session.close()

    def map_and_save(self, full_extracted: dict[str, Any]) -> None:
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
            "admission_email": contact.get("admission_email"),
            "general_email": contact.get("general_email"),
            "phone_numbers": contact.get("phone_numbers"),
            "whatsapp_number": contact.get("whatsapp_number"),
            "admission_helpline": contact.get("admission_helpline"),
            "fax": contact.get("fax"),
            "principal_director_name": contact.get("principal_director_name"),
            "social_media_links": contact.get("social_media_links"),
        }

        college_db_id = self.upsert_college(college_record)
        if not college_db_id:
            LOGGER.error("Failed to map college: upsert returned None")
            return

        session = self.session_factory()
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
                brochure_pdf=ad_info.get("brochure_pdf"),
            )
            session.add(admission_db)

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
            )
            session.add(infra_db)

            metadata = full_extracted.get("page_metadata", {})
            seo_db = SEOMetadata(
                college_id=college_db_id,
                page_title=metadata.get("page_title"),
                meta_description=metadata.get("meta_description"),
                canonical_url=metadata.get("canonical_url"),
                keywords=metadata.get("keywords"),
                schema_markup=full_extracted.get("raw_content", {}).get("schema_org_markup", {}),
            )
            session.add(seo_db)

            pl_info = full_extracted.get("placements", {})
            placement_db = Placement(
                college_id=college_db_id,
                year=pl_info.get("year"),
                average_package=pl_info.get("average_package"),
                median_package=pl_info.get("median_package"),
                highest_package=pl_info.get("highest_package"),
                placement_percentage=pl_info.get("placement_percentage"),
                companies_visited=pl_info.get("companies_visited"),
                offers_made=pl_info.get("offers_made"),
                students_placed=pl_info.get("students_placed"),
                internships=pl_info.get("internships"),
                department_wise_placement=pl_info.get("department_wise_placement"),
                year_wise_placement=pl_info.get("year_wise_placement"),
            )
            session.add(placement_db)

            for faculty_data in full_extracted.get("faculty", []):
                faculty_db = Faculty(
                    college_id=college_db_id,
                    faculty_name=faculty_data.get("faculty_name"),
                    department=faculty_data.get("department"),
                    qualification=faculty_data.get("qualification"),
                    designation=faculty_data.get("designation"),
                    experience=faculty_data.get("experience"),
                    research_papers=faculty_data.get("research_papers"),
                    google_scholar=faculty_data.get("google_scholar"),
                    email=faculty_data.get("email"),
                    photo=faculty_data.get("photo"),
                )
                session.add(faculty_db)

            for rec in full_extracted.get("recruiters", []):
                recruiter_db = Recruiter(
                    college_id=college_db_id,
                    company_name=rec.get("company_name"),
                    role=rec.get("role"),
                    package=rec.get("package"),
                    number_hired=rec.get("number_hired"),
                )
                session.add(recruiter_db)

            for hostel_data in full_extracted.get("hostel", []):
                hostel_db = Hostel(
                    college_id=college_db_id,
                    hostel_name=hostel_data.get("hostel_name"),
                    boys_girls=hostel_data.get("boys_girls"),
                    capacity=hostel_data.get("capacity"),
                    room_types=hostel_data.get("room_types"),
                    ac_non_ac=hostel_data.get("ac_non_ac"),
                    fees=hostel_data.get("fees"),
                    facilities=hostel_data.get("facilities"),
                    mess_charges=hostel_data.get("mess_charges"),
                )
                session.add(hostel_db)

            for scholarship in full_extracted.get("scholarships", []):
                scholarship_db = Scholarship(
                    college_id=college_db_id,
                    scholarship_name=scholarship.get("scholarship_name"),
                    eligibility=scholarship.get("eligibility"),
                    amount=scholarship.get("amount"),
                    government_private=scholarship.get("government_private"),
                    link=scholarship.get("link"),
                )
                session.add(scholarship_db)

            for ranking in full_extracted.get("rankings", []):
                ranking_db = Ranking(
                    college_id=college_db_id,
                    source=ranking.get("agency"),
                    rank=ranking.get("rank"),
                    year=ranking.get("year"),
                )
                session.add(ranking_db)

            for review in full_extracted.get("reviews", []):
                review_db = Review(
                    college_id=college_db_id,
                    student_name=review.get("student_name"),
                    batch=review.get("batch"),
                    course=review.get("course"),
                    rating=review.get("rating"),
                    placement_rating=review.get("placement_rating"),
                    faculty_rating=review.get("faculty_rating"),
                    infrastructure_rating=review.get("infrastructure_rating"),
                    hostel_rating=review.get("hostel_rating"),
                    campus_rating=review.get("campus_rating"),
                    review=review.get("review"),
                    pros=review.get("pros"),
                    cons=review.get("cons"),
                )
                session.add(review_db)

            for gallery_item in full_extracted.get("gallery", []):
                gallery_db = Gallery(
                    college_id=college_db_id,
                    media_type=gallery_item.get("media_type"),
                    category=gallery_item.get("category"),
                    media_url=gallery_item.get("media_url"),
                    caption=gallery_item.get("caption"),
                )
                session.add(gallery_db)

            for download in full_extracted.get("downloads", []):
                download_db = Download(
                    college_id=college_db_id,
                    title=download.get("title"),
                    url=download.get("url") or download.get("file_url"),
                    file_url=download.get("file_url"),
                )
                session.add(download_db)

            for news_item in full_extracted.get("news", []):
                news_db = News(
                    college_id=college_db_id,
                    title=news_item.get("title"),
                    url=news_item.get("url"),
                    snippet=news_item.get("snippet"),
                    published_date=news_item.get("published_date"),
                )
                session.add(news_db)

            for event in full_extracted.get("events", []):
                event_db = Event(
                    college_id=college_db_id,
                    title=event.get("title"),
                    location=event.get("location"),
                    date=event.get("date"),
                    description=event.get("description"),
                )
                session.add(event_db)

            for faq in full_extracted.get("faqs", []):
                faq_db = FAQ(
                    college_id=college_db_id,
                    question=faq.get("question"),
                    answer=faq.get("answer"),
                )
                session.add(faq_db)

            for alumni_item in full_extracted.get("alumni", []):
                alumni_db = Alumni(
                    college_id=college_db_id,
                    name=alumni_item.get("name"),
                    batch=alumni_item.get("batch"),
                    company=alumni_item.get("company"),
                    role=alumni_item.get("role"),
                )
                session.add(alumni_db)

            for document in full_extracted.get("documents", []):
                document_db = Document(
                    college_id=college_db_id,
                    title=document.get("title") or document.get("document_name"),
                    url=document.get("url") or document.get("file_url"),
                )
                session.add(document_db)

            for course_data in full_extracted.get("courses", []):
                course_db = Course(
                    college_id=college_db_id,
                    course_name=course_data.get("course_name"),
                    degree=course_data.get("degree"),
                    stream=course_data.get("stream"),
                    duration=course_data.get("duration"),
                    mode=course_data.get("mode"),
                    intake=course_data.get("intake"),
                    seats=str(course_data.get("seats")) if course_data.get("seats") is not None else None,
                    eligibility=course_data.get("eligibility"),
                    entrance_exam=course_data.get("entrance_exam"),
                    fees=course_data.get("fees"),
                    syllabus_pdf=course_data.get("syllabus_pdf"),
                    curriculum=course_data.get("curriculum"),
                    course_brochure=course_data.get("course_brochure"),
                )
                session.add(course_db)
                session.flush()

                course_fees = [fee for fee in full_extracted.get("fees", []) if fee.get("course_name") == course_data.get("course_name")]
                for fee_data in course_fees:
                    fee_db = Fee(
                        college_id=college_db_id,
                        course_id=course_db.id,
                        tuition_fee=fee_data.get("tuition_fee"),
                        hostel_fee=fee_data.get("hostel_fee"),
                        exam_fee=fee_data.get("exam_fee"),
                        library_fee=fee_data.get("library_fee"),
                        security_deposit=fee_data.get("security_deposit"),
                        transport_fee=fee_data.get("transport_fee"),
                        miscellaneous_fee=fee_data.get("miscellaneous_fee"),
                        total_annual_fee=fee_data.get("total_annual_fee"),
                        total_course_fee=fee_data.get("total_course_fee"),
                    )
                    session.add(fee_db)

                course_cutoffs = [cutoff for cutoff in full_extracted.get("cutoffs", []) if cutoff.get("course_name") == course_data.get("course_name")]
                for cutoff_data in course_cutoffs:
                    cutoff_db = Cutoff(
                        college_id=college_db_id,
                        course_id=course_db.id,
                        year=cutoff_data.get("year"),
                        category=cutoff_data.get("category"),
                        round_1=cutoff_data.get("round_1"),
                        round_2=cutoff_data.get("round_2"),
                        round_3=cutoff_data.get("round_3"),
                        last_round=cutoff_data.get("last_round"),
                    )
                    session.add(cutoff_db)

                course_specs = [spec for spec in full_extracted.get("specializations", []) if spec.get("stream") == course_data.get("stream")]
                for spec_data in course_specs:
                    spec_db = Specialization(
                        college_id=college_db_id,
                        course_id=course_db.id,
                        stream=spec_data.get("stream"),
                        specialization_name=spec_data.get("specialization_name"),
                    )
                    session.add(spec_db)

            session.commit()
            LOGGER.info("Mapped and saved college payload for ID: %s to PostgreSQL", full_extracted.get("college_id"))
        except SQLAlchemyError as exc:
            session.rollback()
            LOGGER.error("Failed to save college mappings: %s", exc)
            raise
        finally:
            session.close()
