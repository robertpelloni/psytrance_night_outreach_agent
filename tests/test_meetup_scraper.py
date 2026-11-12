import pytest
import json
from unittest.mock import MagicMock, patch
from src.scrapers.meetup import MeetupWebScraper
from main import load_scrapers

def test_meetup_jsonld_parsing():
    scraper = MeetupWebScraper()
    html_sample = """
    <html>
      <head>
        <script type="application/ld+json">
        [
          {
            "@context": "https://schema.org",
            "@type": "MusicEvent",
            "name": "Midwest Psytrance Assembly",
            "description": "Gathering of electronic music enthusiasts.",
            "location": {
              "@type": "Place",
              "name": "Tangent Gallery",
              "address": {
                "@type": "PostalAddress",
                "streetAddress": "715 E Milwaukee Ave",
                "addressLocality": "Detroit"
              }
            }
          }
        ]
        </script>
      </head>
      <body></body>
    </html>
    """
    venues = scraper._parse_search_results(html_sample, "Detroit", "psytrance")
    assert len(venues) == 1
    v = venues[0]
    assert v["name"] == "Tangent Gallery"
    assert v["city"] == "Detroit"
    assert v["address"] == "715 E Milwaukee Ave"
    assert v["source"] == "Meetup"
    assert "psytrance" in v["tags"]

def test_meetup_html_card_parsing():
    scraper = MeetupWebScraper()
    html_sample = """
    <html>
      <body>
        <div data-testid="event-card">
          <h2>Psychedelic Synth Night</h2>
          <span class="venue-name">SubMerge Detroit • 3000 E Grand Blvd</span>
        </div>
      </body>
    </html>
    """
    venues = scraper._parse_search_results(html_sample, "Detroit", "synth")
    assert len(venues) == 1
    v = venues[0]
    assert v["name"] == "SubMerge Detroit"
    assert v["address"] == "3000 E Grand Blvd"
    assert v["source"] == "Meetup"

def test_meetup_search_venues_network_handling():
    scraper = MeetupWebScraper()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "itemListElement": [
            {
              "item": {
                "name": "Underground Ambient Lounge",
                "location": {
                  "name": "Motor City Art Center",
                  "address": "100 Woodward Ave"
                }
              }
            }
          ]
        }
        </script>
      </head>
      <body></body>
    </html>
    """

    with patch("requests.get", return_value=mock_resp):
        venues = scraper.search_venues("Detroit", "ambient")
        assert len(venues) == 1
        assert venues[0]["name"] == "Motor City Art Center"

def test_meetup_dynamic_loading():
    query_scrapers, city_scrapers = load_scrapers()
    scraper_names = [s.__class__.__name__ for s in query_scrapers]
    assert "MeetupWebScraper" in scraper_names
