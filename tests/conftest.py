"""Pytest configuration: skip Selenium/Chrome tests in CI (Chrome 138+ unavailable)."""
import pytest

SELENIUM_KEYWORDS = [
    "scraper",
    "scroll",
    "login",
    "undetected",
    "selenium",
]


def pytest_collection_modifyitems(config, items):
    skip_marker = pytest.mark.skip(reason="Selenium/Chrome not available in CI")
    for item in items:
        nodeid = item.nodeid.lower()
        if any(key in nodeid for key in SELENIUM_KEYWORDS):
            item.add_marker(skip_marker) 