import pytest
from unittest.mock import MagicMock, patch
from src.scrapers.resident_advisor import ResidentAdvisorWebScraper

@patch('src.scrapers.resident_advisor.sync_playwright')
def test_ra_scraper_discovery(mock_playwright):
    # Mock Playwright objects
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    # Mock elements
    mock_link = MagicMock()
    mock_link.get_attribute.return_value = "/venues/berlin-club"
    mock_link.inner_text.return_value = "Berlin Club"

    mock_page.query_selector_all.return_value = [mock_link]
    mock_page.title.return_value = "RA Guide"

    scraper = ResidentAdvisorWebScraper()
    venues = scraper.search_venues("Berlin")

    assert len(venues) == 1
    assert venues[0]['name'] == "Berlin Club"
    assert "ra.co/venues/berlin-club" in venues[0]['website']
