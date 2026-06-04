import unittest
from unittest.mock import MagicMock, patch
from src.scrapers.google_maps import GoogleMapsPlaywrightScraper

class TestGoogleMapsScraper(unittest.TestCase):
    @patch('src.scrapers.google_maps.sync_playwright')
    @patch('src.scrapers.google_maps.ProxyRotator.get_playwright_proxy')
    @patch('src.scrapers.google_maps.UserAgentRotator.get_random')
    def test_search_venues_rating_extraction(self, mock_ua, mock_proxy, mock_playwright):
        # Setup mock page and browser
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        # Mock element with rating
        mock_el = MagicMock()
        mock_el.get_attribute.return_value = "Cool Club"

        mock_rating_el = MagicMock()
        mock_rating_el.get_attribute.return_value = "4.7 stars"
        mock_el.query_selector.return_value = mock_rating_el

        mock_page.query_selector_all.return_value = [mock_el]

        scraper = GoogleMapsPlaywrightScraper()
        results = scraper.search_venues("Detroit")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Cool Club")
        self.assertEqual(results[0]['google_rating'], 4.7)

if __name__ == "__main__":
    unittest.main()
