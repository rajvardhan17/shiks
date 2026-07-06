from edusphere.parsers.established_year_parser import parse_established_year


def test_rejects_copyright_year():
    assert parse_established_year("© 2025 Example College") is None


def test_rejects_admissions_year_banner():
    assert parse_established_year("Admissions 2026 open") is None


def test_accepts_estd_year():
    assert parse_established_year("Estd. 1998") == "1998"


def test_rejects_bare_year_without_keyword():
    assert parse_established_year("The college started in 1994") is None
