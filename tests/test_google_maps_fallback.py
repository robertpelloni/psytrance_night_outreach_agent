import pytest
from unittest.mock import patch, MagicMock
from src.scrapers.google_maps import GoogleMapsPlaywrightScraper

@patch('src.scrapers.google_maps.sync_playwright')
@patch('requests.get')
@patch('os.getenv')
def test_google_maps_fallback(mock_getenv, mock_requests_get, mock_playwright):
    # Setup env
    mock_getenv.return_value = 'FAKE_API_KEY'

    # Setup Playwright to fail
    mock_playwright.side_effect = Exception("Playwright failed")

    # Setup requests mock to return valid API data
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'status': 'OK',
        'results': [
            {'name': 'API Venue 1', 'rating': 4.5},
            {'name': 'API Venue 2', 'rating': 4.0}
        ]
    }
    mock_requests_get.return_value = mock_response

    scraper = GoogleMapsPlaywrightScraper()

    # Execute
    # We patch time.sleep to avoid waiting 3 retries in the test
    with patch('time.sleep', return_value=None):
        venues = scraper.search_venues('Detroit', 'techno club')

    # Verify fallback executed and returned API results
    assert len(venues) == 2
    assert venues[0]['name'] == 'API Venue 1'
    assert venues[0]['source'] == 'google_maps_api'

    # Verify it tried requests.get
    assert mock_requests_get.called
    args, kwargs = mock_requests_get.call_args
    assert 'FAKE_API_KEY' in args[0]
