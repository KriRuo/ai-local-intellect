import pytest
from lmarena_scraper import parse_text_date, normalize_url, clean_thumbnail_url
from datetime import datetime

class TestParseTextDate:
    def test_english_date(self):
        assert parse_text_date("24. Feb. 2025") == datetime(2025, 2, 24)

    def test_german_date(self):
        assert parse_text_date("3. März 2025") == datetime(2025, 3, 3)

    def test_german_umlaut_variants(self):
        assert parse_text_date("3. Maerz 2025") == datetime(2025, 3, 3)
        assert parse_text_date("3. Marz 2025") == datetime(2025, 3, 3)

    def test_invalid_date(self):
        assert parse_text_date("32. Feb. 2025") is None
        assert parse_text_date("") is None
        assert parse_text_date("foo.bar.baz") is None

class TestNormalizeUrl:
    def test_basic(self):
        assert normalize_url("https://blog.lmarena.ai/post/") == "https://blog.lmarena.ai/post"

    def test_lowercase_and_trailing(self):
        assert normalize_url("HTTPS://BLOG.LMARENA.AI/POST/") == "https://blog.lmarena.ai/post"

    def test_tracking_params(self):
        url = "https://blog.lmarena.ai/post?utm_source=foo&utm_medium=bar&id=123"
        assert normalize_url(url) == "https://blog.lmarena.ai/post?id=123"

    def test_no_url(self):
        assert normalize_url("") == ""
        assert normalize_url(None) is None

class TestCleanThumbnailUrl:
    def test_absolute(self):
        url = "https://cdn.lmarena.ai/img.png"
        assert clean_thumbnail_url(url) == url

    def test_relative(self):
        url = "/img.png"
        assert clean_thumbnail_url(url) == "https://blog.lmarena.ai/img.png"

    def test_no_url(self):
        assert clean_thumbnail_url("") is None
        assert clean_thumbnail_url(None) is None

    def test_no_leading_slash(self):
        url = "img.png"
        assert clean_thumbnail_url(url) == "https://blog.lmarena.ai/img.png" 