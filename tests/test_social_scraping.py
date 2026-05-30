import pytest
from unittest.mock import MagicMock, patch
from src.scrapers.instagram import InstagramScraper
from src.scrapers.base_scraper import ContactExtractor

def test_instagram_scraper_none_handle():
    scraper = InstagramScraper()
    assert scraper.get_profile_context(None) is None

@patch('src.scrapers.instagram.sync_playwright')
def test_instagram_scraper_success(mock_playwright):
    # Mock Playwright objects
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_page.query_selector.return_value.inner_text.return_value = "Underground Forest Psytrance Venue"
    mock_page.evaluate.return_value = "Check out our upcoming dark psy event this Friday!"

    scraper = InstagramScraper()
    result = scraper.get_profile_context("psy_forest_club")

    assert result is not None
    assert "Forest Psytrance" in result['bio']
    assert "dark psy event" in result['recent_activity_context']

@patch('src.scrapers.instagram.InstagramScraper.get_profile_context')
def test_contact_extractor_social_integration(mock_get_context):
    mock_get_context.return_value = {
        'bio': 'Techno & Psytrance Sanctuary',
        'recent_activity_context': 'Lasers and Funktion-One sound tonight!'
    }

    context = ContactExtractor.get_social_context("@techno_sanctuary")
    assert "Techno & Psytrance Sanctuary" in context
    assert "Lasers and Funktion-One" in context

def test_contact_extractor_social_none():
    assert ContactExtractor.get_social_context(None) is None
