import pytest
from unittest.mock import patch, MagicMock
import json
from src.scrapers.facebook_events import FacebookEventsWebScraper

def test_facebook_scraper_json_ld_parsing():
    scraper = FacebookEventsWebScraper()

    html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@type": "MusicEvent",
          "name": "Midwest Psytrance Ritual",
          "description": "Deep psychedelic trance warehouse gathering in Detroit.",
          "location": {
            "@type": "Place",
            "name": "Russell Industrial Center",
            "address": {
              "@type": "PostalAddress",
              "streetAddress": "1600 Clay St",
              "addressLocality": "Detroit"
            }
          }
        }
        </script>
      </head>
      <body></body>
    </html>
    """

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_get.return_value = mock_response

        venues = scraper.search_venues("Detroit", query="psytrance")
        assert len(venues) == 1
        v = venues[0]
        assert v["name"] == "Russell Industrial Center"
        assert v["city"] == "Detroit"
        assert "1600 Clay St" in v["address"]
        assert "Facebook Events" in v["source"]
        assert "psytrance" in v["tags"]

def test_facebook_scraper_html_card_parsing():
    scraper = FacebookEventsWebScraper()

    html = """
    <html>
      <body>
        <div role="article">
          <h2>Psychedelic Gathering · Tangent Gallery · Detroit, MI</h2>
        </div>
        <div role="article">
          <h2>Dark Prog Showcase · City Club · Detroit</h2>
        </div>
      </body>
    </html>
    """

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_get.return_value = mock_response

        venues = scraper.search_venues("Detroit", query="dark prog")
        assert len(venues) == 2
        names = [v["name"] for v in venues]
        assert "Tangent Gallery" in names
        assert "City Club" in names

def test_facebook_scraper_rate_limit_retry():
    scraper = FacebookEventsWebScraper()

    with patch("requests.get") as mock_get:
        # First attempt rate limit (429), second succeeds
        res_429 = MagicMock()
        res_429.status_code = 429

        res_200 = MagicMock()
        res_200.status_code = 200
        res_200.text = "<html><body></body></html>"

        mock_get.side_effect = [res_429, res_200]

        with patch("time.sleep", return_value=None):
            venues = scraper.search_venues("Detroit", query="psytrance")
            assert mock_get.call_count == 2
            assert venues == []

def test_facebook_scraper_dynamic_discovery():
    from main import load_scrapers
    query_scrapers, city_scrapers = load_scrapers()
    scraper_names = [s.__class__.__name__ for s in query_scrapers]
    assert "FacebookEventsWebScraper" in scraper_names
