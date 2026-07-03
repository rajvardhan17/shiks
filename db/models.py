from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class College(Base):
    __tablename__ = "colleges"
    id = Column(Integer, primary_key=True)
    college_id = Column(String(128), unique=True, index=True)
    name = Column(String(512), nullable=False, index=True)
    short_name = Column(String(128))
    type = Column(String(128))  # Government / Private / Deemed / Autonomous
    university_affiliation = Column(String(256))
    ownership = Column(String(128))  # Central / State / Private
    year_established = Column(String(32))
    accreditation = Column(String(128))  # NAAC Grade
    approval = Column(String(256))  # AICTE, UGC, PCI, NMC, BCI etc.
    campus_size = Column(String(128))  # Acres
    website = Column(String(1024))
    logo = Column(String(1024))
    cover_image = Column(String(1024))
    description = Column(Text)
    highlights = Column(Text)

    # Location Details
    country = Column(String(128))
    state = Column(String(128), index=True)
    city = Column(String(128), index=True)
    district = Column(String(128))
    address = Column(Text)
    pin_code = Column(String(32))
    latitude = Column(Float)
    longitude = Column(Float)
    google_maps_link = Column(String(1024))
    nearby_railway_station = Column(String(256))
    nearby_airport = Column(String(256))
    nearby_bus_stand = Column(String(256))

    # Contact Information
    admission_email = Column(String(256))
    general_email = Column(String(256))
    phone_numbers = Column(String(512))
    whatsapp_number = Column(String(128))
    admission_helpline = Column(String(128))
    fax = Column(String(128))
    principal_director_name = Column(String(256))
    social_media_links = Column(JSONB)  # Facebook, Twitter, LinkedIn, etc.

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    courses = relationship("Course", back_populates="college", cascade="all, delete-orphan")
    specializations = relationship("Specialization", back_populates="college", cascade="all, delete-orphan")
    admissions = relationship("Admission", back_populates="college", cascade="all, delete-orphan")
    fees = relationship("Fee", back_populates="college", cascade="all, delete-orphan")
    cutoffs = relationship("Cutoff", back_populates="college", cascade="all, delete-orphan")
    placements = relationship("Placement", back_populates="college", cascade="all, delete-orphan")
    recruiters = relationship("Recruiter", back_populates="college", cascade="all, delete-orphan")
    faculty = relationship("Faculty", back_populates="college", cascade="all, delete-orphan")
    infrastructure = relationship("Infrastructure", uselist=False, back_populates="college", cascade="all, delete-orphan")
    hostels = relationship("Hostel", back_populates="college", cascade="all, delete-orphan")
    scholarships = relationship("Scholarship", back_populates="college", cascade="all, delete-orphan")
    rankings = relationship("Ranking", back_populates="college", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="college", cascade="all, delete-orphan")
    gallery = relationship("Gallery", back_populates="college", cascade="all, delete-orphan")
    downloads = relationship("Download", back_populates="college", cascade="all, delete-orphan")
    news = relationship("News", back_populates="college", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="college", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="college", cascade="all, delete-orphan")
    alumni = relationship("Alumni", back_populates="college", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="college", cascade="all, delete-orphan")
    seo_metadata = relationship("SEOMetadata", uselist=False, back_populates="college", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    course_name = Column(String(512), index=True)
    degree = Column(String(128), index=True)  # B.Tech, MBA, etc.
    stream = Column(String(128), index=True)  # Engineering, Management, etc.
    duration = Column(String(64))  # e.g., 4 Years
    mode = Column(String(64))  # Full-time, Part-time, etc.
    intake = Column(String(64))
    seats = Column(String(64))
    eligibility = Column(Text)
    entrance_exam = Column(String(256))
    fees = Column(String(128))
    syllabus_pdf = Column(String(1024))
    curriculum = Column(Text)
    course_brochure = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="courses")
    specializations = relationship("Specialization", back_populates="course", cascade="all, delete-orphan")
    fees_relation = relationship("Fee", back_populates="course", cascade="all, delete-orphan")
    cutoffs = relationship("Cutoff", back_populates="course", cascade="all, delete-orphan")


class Specialization(Base):
    __tablename__ = "specializations"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=True)
    stream = Column(String(128))
    specialization_name = Column(String(256), index=True)  # AI, Data Science, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="specializations")
    course = relationship("Course", back_populates="specializations")


class Admission(Base):
    __tablename__ = "admissions"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    eligibility = Column(Text)
    minimum_percentage = Column(String(128))
    entrance_exam = Column(String(256))
    age_criteria = Column(String(256))
    reservation_rules = Column(Text)
    domicile_rules = Column(Text)
    admission_process = Column(String(64))  # Online/Offline
    documents_required = Column(Text)
    counselling_process = Column(Text)
    selection_process = Column(Text)
    application_fee = Column(String(128))
    last_date = Column(String(128))
    application_link = Column(String(1024))
    brochure_pdf = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="admissions")


class Fee(Base):
    __tablename__ = "fees"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=True)
    tuition_fee = Column(String(128))
    hostel_fee = Column(String(128))
    exam_fee = Column(String(128))
    library_fee = Column(String(128))
    security_deposit = Column(String(128))
    transport_fee = Column(String(128))
    miscellaneous_fee = Column(String(128))
    total_annual_fee = Column(String(128))
    total_course_fee = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="fees")
    course = relationship("Course", back_populates="fees_relation")


class Cutoff(Base):
    __tablename__ = "cutoffs"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=True)
    year = Column(String(32))
    category = Column(String(64))  # General, OBC, SC, ST, EWS, PwD
    round_1 = Column(String(64))
    round_2 = Column(String(64))
    round_3 = Column(String(64))
    last_round = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="cutoffs")
    course = relationship("Course", back_populates="cutoffs")


class Placement(Base):
    __tablename__ = "placements"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    year = Column(String(32))
    average_package = Column(String(128))
    median_package = Column(String(128))
    highest_package = Column(String(128))
    placement_percentage = Column(String(64))
    companies_visited = Column(Integer)
    offers_made = Column(Integer)
    students_placed = Column(Integer)
    internships = Column(Text)
    department_wise_placement = Column(JSONB)
    year_wise_placement = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="placements")


class Recruiter(Base):
    __tablename__ = "recruiters"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    company_name = Column(String(256), index=True)
    role = Column(String(256))
    package = Column(String(128))
    number_hired = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="recruiters")


class Faculty(Base):
    __tablename__ = "faculty"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    faculty_name = Column(String(256), index=True)
    department = Column(String(256))
    qualification = Column(String(256))
    designation = Column(String(256))
    experience = Column(String(128))
    research_papers = Column(Integer)
    google_scholar = Column(String(1024))
    email = Column(String(256))
    photo = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="faculty")


class Infrastructure(Base):
    __tablename__ = "infrastructure"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True, unique=True)
    hostel = Column(Boolean, default=False)
    library = Column(Boolean, default=False)
    wifi = Column(Boolean, default=False)
    labs = Column(Boolean, default=False)
    gym = Column(Boolean, default=False)
    auditorium = Column(Boolean, default=False)
    sports = Column(Boolean, default=False)
    swimming_pool = Column(Boolean, default=False)
    medical = Column(Boolean, default=False)
    bank = Column(Boolean, default=False)
    atm = Column(Boolean, default=False)
    mess = Column(Boolean, default=False)
    cafeteria = Column(Boolean, default=False)
    parking = Column(Boolean, default=False)
    transport = Column(Boolean, default=False)
    conference_hall = Column(Boolean, default=False)
    seminar_hall = Column(Boolean, default=False)
    incubation_centre = Column(Boolean, default=False)
    innovation_lab = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="infrastructure")


class Hostel(Base):
    __tablename__ = "hostels"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    hostel_name = Column(String(256))
    boys_girls = Column(String(32))  # Boys / Girls
    capacity = Column(Integer)
    room_types = Column(String(256))
    ac_non_ac = Column(String(32))
    fees = Column(String(128))
    facilities = Column(Text)
    mess_charges = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="hostels")


class Scholarship(Base):
    __tablename__ = "scholarships"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    scholarship_name = Column(String(256), index=True)
    eligibility = Column(Text)
    amount = Column(String(128))
    last_date = Column(String(128))
    government_private = Column(String(64))  # Government / Private
    link = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="scholarships")


class Ranking(Base):
    __tablename__ = "rankings"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    agency = Column(String(128))  # NIRF, India Today, Outlook, The Week, IIRF, Times Ranking
    year = Column(String(32))
    rank = Column(Integer)
    category = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="rankings")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    student_name = Column(String(256))
    batch = Column(String(128))
    course = Column(String(256))
    rating = Column(Float)
    placement_rating = Column(Float)
    faculty_rating = Column(Float)
    infrastructure_rating = Column(Float)
    hostel_rating = Column(Float)
    campus_rating = Column(Float)
    review = Column(Text)
    pros = Column(Text)
    cons = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="reviews")


class Gallery(Base):
    __tablename__ = "gallery"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    media_type = Column(String(32))  # image / video
    category = Column(String(64))  # Campus, Hostel, Library, Classrooms, Labs, Sports, Auditorium, Events, Convocation, Campus Tour, Student Life, Virtual Tour
    media_url = Column(String(1024))
    caption = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="gallery")


class Download(Base):
    __tablename__ = "downloads"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    title = Column(String(256))  # Prospectus, Admission Brochure, etc.
    file_url = Column(String(1024))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="downloads")


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    title = Column(String(512), index=True)
    category = Column(String(128))  # Admission Open, Results, etc.
    link = Column(String(1024))
    content = Column(Text)
    date = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="news")


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    event_name = Column(String(512))
    category = Column(String(128))  # Student Clubs, Festivals, Hackathons, etc.
    description = Column(Text)
    date = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="events")


class FAQ(Base):
    __tablename__ = "faqs"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    question = Column(Text)
    answer = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="faqs")


class Alumni(Base):
    __tablename__ = "alumni"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    name = Column(String(256), index=True)
    company = Column(String(256))
    package = Column(String(128))
    designation = Column(String(256))
    linkedin = Column(String(1024))
    achievements = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="alumni")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True)
    document_name = Column(String(256))
    is_compulsory = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="documents")


class SEOMetadata(Base):
    __tablename__ = "seo_metadata"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), index=True, unique=True)
    meta_title = Column(String(512))
    meta_description = Column(Text)
    slug = Column(String(256), index=True)
    canonical_url = Column(String(1024))
    keywords = Column(Text)
    schema_markup = Column(JSONB)  # College, Course, FAQ
    created_at = Column(DateTime, default=datetime.utcnow)

    college = relationship("College", back_populates="seo_metadata")


class RawPage(Base):
    __tablename__ = "raw_pages"
    id = Column(Integer, primary_key=True)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="SET NULL"), index=True, nullable=True)
    page_url = Column(String(2048), nullable=False, index=True)
    content = Column(Text)
    table_content = Column(Text)
    page_title = Column(String(1024))
    headings = Column(Text)
    meta = Column(JSONB)
    links = Column(JSONB)
    images = Column(JSONB)
    json_ld = Column(JSONB)
    structured_facts = Column(JSONB)
    checksum = Column(String(128), index=True)
    status = Column(String(64), default="new")
    error = Column(Text)
    fetched_at = Column(DateTime)

    __table_args__ = (UniqueConstraint("page_url", name="uix_page_url"),)
