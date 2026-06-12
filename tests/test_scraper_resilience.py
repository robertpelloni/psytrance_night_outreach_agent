import unittest
from unittest.mock import MagicMock, patch
from src.scrapers.google_maps import GoogleMapsPlaywrightScraper

class TestScraperResilience(unittest.TestCase):
    @patch('src.scrapers.google_maps.sync_playwright')
    @patch('src.scrapers.google_maps.ProxyRotator')
    def test_scraper_retries_on_failure(self, mock_proxy_rotator, mock_playwright):
        # Setup: first 2 attempts fail, 3rd succeeds
        mock_browser = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

        # We need to make page.goto or similar fail
        mock_page = MagicMock()
        mock_browser.new_context.return_value.new_page.return_value = mock_page

        # Side effect to fail then succeed
        mock_page.goto.side_effect = [Exception("Fail 1"), Exception("Fail 2"), None]
        mock_page.query_selector_all.return_value = [] # Empty results but success

        # Mock ProxyRotator methods
        mock_proxy_rotator.get_playwright_proxy.return_value = {'server': 'http://proxy.test'}

        scraper = GoogleMapsPlaywrightScraper()
        with patch('time.sleep'): # Skip actual sleeping
            scraper.search_venues("Detroit")

        # Verify 3 attempts were made
        self.assertEqual(mock_page.goto.call_count, 3)

        # Verify failures and success were reported
        self.assertEqual(mock_proxy_rotator.report_failure.call_count, 2)
        mock_proxy_rotator.report_success.assert_called_once()

if __name__ == "__main__":
    unittest.main()
