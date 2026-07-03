from scrapers.aggregator import build_college_payload, extract_college_links


def test_extract_college_links_from_listing_html() -> None:
    html = """
    <html><body>
      <a href="/college/example-institute">Example Institute</a>
      <a href="https://www.shiksha.com/college/another-college">Another College</a>
      <a href="https://example.com/not-a-college">Ignore Me</a>
    </body></html>
    """

    links = extract_college_links(html, base_url="https://www.shiksha.com")

    assert links == [
        "https://www.shiksha.com/college/example-institute",
        "https://www.shiksha.com/college/another-college",
    ]


def test_build_college_payload_returns_normalized_sections() -> None:
    html = """
    <html>
      <head>
        <title>Example Institute</title>
        <meta name="description" content="A premier institute" />
      </head>
      <body>
        <h1>Example Institute</h1>
        <p>Established in 1999</p>
        <p>Address: 12, Main Road, Delhi</p>
        <p>Phone: +91-9876543210</p>
        <p>Email: admissions@example.edu</p>
        <a href="/courses">Courses</a>
        <a href="/fees">Fees</a>
      </body>
    </html>
    """

    payload = build_college_payload(
        college_url="https://example.edu",
        html=html,
        source="shiksha",
    )

    assert payload["basic_information"]["college_name"] == "Example Institute"
    assert payload["basic_information"]["established_year"] == "1999"
    assert payload["contact_information"]["city"] == "Delhi"
    assert payload["contact_information"]["phone_numbers"] == ["+91-9876543210"]
    assert payload["contact_information"]["email_addresses"] == ["admissions@example.edu"]
    assert payload["internal_links"]["courses"] == "https://example.edu/courses"
    assert payload["internal_links"]["fees"] == "https://example.edu/fees"
    assert payload["page_metadata"]["source"] == "shiksha"
