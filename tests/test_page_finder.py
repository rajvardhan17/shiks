from scrapers.page_finder import find_pages, is_valid_link


def test_rejects_noisy_urls() -> None:
    assert not is_valid_link("https://example.edu/#collapse4")
    assert not is_valid_link("https://docs.google.com/forms/d/e/example/viewform")
    assert not is_valid_link("https://example.edu/feedback.aspx")
    assert is_valid_link("https://example.edu/contact-us")


def test_finds_category_specific_pages() -> None:
    html = """
        <a href="/pg-admissions">PG Admissions</a>
        <a href="/admissions/apply">Apply now</a>
        <a href="/academics/courses">Courses and curriculum</a>
        <a href="/career/placements">Career placements</a>
        <a href="/fees">Fee structure</a>
        <a href="/contact-us">Contact us</a>
        <a href="https://docs.google.com/forms/d/e/example/viewform">Fee form</a>
        <a href="/#collapse4">Fees</a>
    """

    pages = find_pages("https://example.edu", html)

    assert pages["admissions"] == "https://example.edu/pg-admissions"
    assert pages["courses"] == "https://example.edu/academics/courses"
    assert pages["placements"] == "https://example.edu/career/placements"
    assert pages["fees"] == "https://example.edu/fees"
    assert pages["contact"] == "https://example.edu/contact-us"
