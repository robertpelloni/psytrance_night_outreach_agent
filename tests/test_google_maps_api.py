import pytest
from unittest.mock import patch, MagicMock
from src.scrapers.google_maps import GoogleMapsPlaywrightScraper

@patch("src.scrapers.google_maps.os.getenv")
@patch("src.scrapers.google_maps.requests.get")
@patch("src.scrapers.google_maps.sync_playwright")
def test_fallback_api_trigger(mock_playwright, mock_requests_get, mock_getenv):
    # Setup mocks
    mock_getenv.return_value = "TEST_API_KEY"

    # Mock Playwright to fail to trigger fallback
    mock_playwright.side_effect = Exception("Playwright failed")

    # Mock Requests response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "name": "Test Venue API",
                "rating": 4.8,
                "photos": [{"photo_reference": "xyz"}]
            }
        ]
    }
    mock_requests_get.return_value = mock_response

    scraper = GoogleMapsPlaywrightScraper()
    venues = scraper.search_venues("Detroit", "techno club")

    assert len(venues) == 1
    assert venues[0]['name'] == "Test Venue API"
    assert venues[0]['google_rating'] == 4.8
    assert venues[0]['source'] == "google_maps_api"
    assert "photo_reference=xyz" in venues[0]['image_url']

    # Check fallback was actually called via requests
    mock_requests_get.assert_called_once()
