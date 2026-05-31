import unittest
from unittest.mock import patch, MagicMock
from src.scrapers.resident_advisor import ResidentAdvisorWebScraper

class TestRAEnrichment(unittest.TestCase):
    @patch('src.scrapers.resident_advisor.sync_playwright')
    @patch('src.scrapers.resident_advisor.ProxyRotator.get_playwright_proxy')
    @patch('src.scrapers.resident_advisor.UserAgentRotator.get_random')
    def test_enrich_venue_mock(self, mock_ua, mock_proxy, mock_playwright):
        # Setup mock page and browser
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        # Mock element queries
        mock_website = MagicMock()
        mock_website.get_attribute.return_value = "http://venue-site.com"

        mock_desc = MagicMock()
        mock_desc.inner_text.return_value = "A dark underground techno bunker."

        mock_ig = MagicMock()
        mock_ig.get_attribute.return_value = "https://instagram.com/venue_ig"

        # Configure page.query_selector behavior
        def side_effect(selector, **kwargs):
            if 'aria-label="Website"' in selector: return mock_website
            if 'itemprop="description"' in selector: return mock_desc
            return None

        mock_page.query_selector.side_effect = side_effect
        mock_page.query_selector_all.return_value = [mock_ig]

        scraper = ResidentAdvisorWebScraper()
        details = scraper.enrich_venue("https://ra.co/venues/test")

        self.assertEqual(details['website'], "http://venue-site.com")
        self.assertEqual(details['description'], "A dark underground techno bunker.")
        self.assertIn("https://instagram.com/venue_ig", details['socials'])

if __name__ == "__main__":
    unittest.main()
