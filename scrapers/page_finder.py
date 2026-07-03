from bs4 import BeautifulSoup
from bs4.element import Tag
from urllib.parse import urljoin, urlparse

KEYWORDS: dict[str, list[str]] = {
    "admissions": ["admission", "admissions", "apply", "application"],
    "courses": ["course", "courses", "academic", "academics", "programmes", "programs", "curriculum", "syllabus"],
    "placements": ["placement", "placements", "recruit", "recruitment", "recruiter", "recruiters", "career", "careers"],
    "fees": ["fee", "fees", "tuition", "payment", "cost"],
    "contact": ["contact", "address", "directory", "about"],
    "scholarships": ["scholarship", "scholarships", "financial", "funding", "concession"],
    "faculty": ["faculty", "staff", "teacher", "teachers", "professor", "professors", "members", "people"],
    "hostel": ["hostel", "hostels", "dorm", "dorms", "dormitory", "residential", "accommodation", "housing"],
    "infrastructure": ["infrastructure", "facility", "facilities", "campus", "library", "labs", "wifi", "gym", "canteen", "sports"],
    "rankings": ["ranking", "rankings", "rank", "nirf", "award", "awards", "achievement", "achievements", "accreditation"],
    "reviews": ["review", "reviews", "testimonial", "testimonials", "feedback", "rating", "ratings"],
    "gallery": ["gallery", "photos", "photo", "images", "videos", "media", "album", "albums"],
    "downloads": ["download", "downloads", "prospectus", "brochure", "calendar", "handbook"],
    "news": ["news", "notice", "notices", "announcement", "announcements", "press", "events", "circular", "circulars"],
    "alumni": ["alumni", "alumnus", "association", "graduate", "graduates"],
    "faqs": ["faq", "faqs", "question", "questions", "queries"]
}

CATEGORY_BOOSTS: dict[str, tuple[str, ...]] = {
    "admissions": ("admission", "admissions", "apply", "application", "prospective", "entrance"),
    "courses": ("course", "courses", "curriculum", "syllabus", "academic-program", "academic programs", "programme structure", "program structure", "departments"),
    "placements": ("placement", "placements", "career", "careers", "recruiter", "recruiters", "internship"),
    "fees": ("fee", "fees", "tuition", "payment", "scholarship", "scholarships", "financial"),
    "contact": ("contact", "contact-us", "directory", "address", "phone", "email"),
    "scholarships": ("scholarship", "scholarships", "financial aid", "concession", "stipend"),
    "faculty": ("faculty", "staff", "professors", "faculty directory", "faculty list"),
    "hostel": ("hostel", "hostels", "dorm", "dormitory", "housing", "accommodation", "residence"),
    "infrastructure": ("infrastructure", "facility", "facilities", "campus map", "library", "laboratories", "amenities"),
    "rankings": ("ranking", "rankings", "nirf", "accreditation", "awards", "recognition", "rank"),
    "reviews": ("review", "reviews", "testimonial", "testimonials", "student speak", "rating"),
    "gallery": ("gallery", "photos", "photo", "images", "videos", "media", "album"),
    "downloads": ("download", "downloads", "prospectus", "brochure", "information brochure", "handbook"),
    "news": ("news", "notice", "notices", "announcement", "announcements", "events", "press release", "circular"),
    "alumni": ("alumni", "alumnus", "association", "distinguished alumni", "network"),
    "faqs": ("faq", "faqs", "frequently asked", "questions", "queries", "help")
}

CATEGORY_PENALTIES: dict[str, tuple[str, ...]] = {
    "admissions": ("feedback", "contact", "alumni", "payment", "fee", "fees"),
    "courses": ("admission", "admissions", "apply", "application", "placement", "career"),
    "placements": ("admission", "admissions", "course", "courses", "fee", "fees"),
    "fees": ("admission", "admissions", "apply", "application", "contact", "feedback"),
    "contact": ("admission", "admissions", "course", "courses", "fee", "fees", "feedback"),
    "scholarships": ("contact", "feedback", "course", "placement"),
    "faculty": ("admission", "placement", "news", "event"),
    "hostel": ("course", "admission", "rankings", "faculty"),
    "infrastructure": ("fee", "fees", "jobs", "apply"),
    "rankings": ("form", "apply", "contact", "syllabus"),
    "reviews": ("course", "curriculum", "syllabus", "admissions"),
    "gallery": ("course", "admission", "jobs", "syllabus"),
    "downloads": ("faculty", "alumni", "jobs", "gallery"),
    "news": ("faculty", "syllabus", "apply", "course description"),
    "alumni": ("faculty", "admission", "apply", "course structure"),
    "faqs": ("news", "events", "gallery", "syllabus")
}

MIN_SCORE = 25

BAD_EXTENSIONS: tuple[str, ...] = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".zip"
)

BAD_SCHEMES: tuple[str, ...] = (
    "javascript:",
    "mailto:",
    "tel:"
)

SOCIAL_DOMAINS: tuple[str, ...] = (
    "facebook.com",
    "fb.com",
    "instagram.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "youtube.com",
    "youtu.be"
)

BLOCKED_DOMAINS: tuple[str, ...] = (
    "docs.google.com",
    "forms.gle",
)

NOISY_LINK_TERMS: tuple[str, ...] = (
    "feedback",
    "viewform",
    "google-form",
    "googleform",
    "login",
    "signin",
    "sign-in",
)


def is_valid_link(url: str) -> bool:
    """Return False for unsupported files, anchors, forms, auth, or social links."""
    lowered_url = url.lower().strip()
    parsed_url = urlparse(lowered_url)
    host = parsed_url.netloc.removeprefix("www.")
    path = parsed_url.path
    url_text = f"{host} {path} {parsed_url.query}".lower()

    if any(lowered_url.startswith(scheme) for scheme in BAD_SCHEMES):
        return False

    if parsed_url.fragment and not path.strip("/"):
        return False

    if path.endswith(BAD_EXTENSIONS):
        return False

    if any(host == domain or host.endswith(f".{domain}") for domain in SOCIAL_DOMAINS):
        return False

    if any(host == domain or host.endswith(f".{domain}") for domain in BLOCKED_DOMAINS):
        return False

    if any(term in url_text for term in NOISY_LINK_TERMS):
        return False

    return True


def score_link(link: Tag, href: str, category: str, words: list[str]) -> int:
    """Score a link for one category; higher scores are better matches."""
    label = link.get_text(" ", strip=True).lower()
    parsed_url = urlparse(href.lower())
    path = parsed_url.path.strip("/")
    url_text = f"{parsed_url.netloc} {path} {parsed_url.query}".lower()
    combined_text = f"{label} {url_text}"

    score = 0

    # Visible navigation text is usually more intentional than incidental URL text.
    for word in words:
        if word in label:
            score += 30
        if word in path:
            score += 20
        if word in combined_text:
            score += 5

    if category in path:
        score += 15

    for term in CATEGORY_BOOSTS[category]:
        if term in label:
            score += 20
        if term in path:
            score += 15

    for term in CATEGORY_PENALTIES[category]:
        if term in combined_text:
            score -= 20

    # Prefer proper pages over same-page anchors and noisy utility links.
    if parsed_url.fragment:
        score -= 10
    if any(noisy_word in combined_text for noisy_word in ["alumni", "notice", "announcement"]):
        score -= 10

    if parsed_url.path.strip("/") in {"", "home", "index.php", "index.php/en"}:
        score -= 20

    if "portal" in combined_text and category not in {"admissions", "fees"}:
        score -= 15

    return score


def find_pages(base_url: str, html: str) -> dict[str, str]:
    """Find the best matching page URL for each college information category."""
    soup = BeautifulSoup(html, "html.parser")
    best_matches: dict[str, tuple[int, str]] = {}

    for link in soup.find_all("a", href=True):
        href = urljoin(base_url, str(link["href"]).strip())

        if not is_valid_link(href):
            continue

        for category, words in KEYWORDS.items():
            score = score_link(link, href, category, words)

            if score < MIN_SCORE:
                continue

            current_score = best_matches.get(category, (0, ""))[0]

            if score > current_score:
                best_matches[category] = (score, href)

    return {
        category: best_matches.get(category, (0, ""))[1]
        for category in KEYWORDS
    }
