import json
import pytest
from unittest.mock import patch, MagicMock
from src.scrapers.eventbrite import EventbriteWebScraper

MOCK_EVENTBRITE_HTML_JSON_LD = """
<!DOCTYPE html>
<html>
<head>
    <title>Psytrance Events in Detroit</title>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "item": {
                    "@type": "Event",
                    "name": "Psychedelic Solstice Detroit",
                    "description": "Full-power psytrance gathering featuring Funktion-One sound and immersive lasers.",
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
            },
            {
                "@type": "ListItem",
                "position": 2,
                "item": {
                    "@type": "Event",
                    "name": "Underground Frequencies",
                    "description": "Dark progressive and forest techno.",
                    "location": {
                        "@type": "Place",
                        "name": "Leland City Club",
                        "address": {
                            "@type": "PostalAddress",
                            "streetAddress": "400 Bagley St",
                            "addressLocality": "Detroit"
                        }
                    }
                }
            }
        ]
    }
    </script>
</head>
<body>
    <h1>Events</h1>
</body>
</html>
"""

MOCK_EVENTBRITE_HTML_CARD_FALLBACK = """
<!DOCTYPE html>
<html>
<body>
    <div data-testid="event-card">
        <h3><a class="event-card-link" href="#">Midwest Psy Gathering</a></h3>
        <p class="Typography_body-md">Marble Bar • Detroit, MI</p>
    </div>
    <div data-testid="event-card">
        <h3><a class="event-card-link" href="#">Online Stream Fest</a></h3>
        <p class="Typography_body-md">Online Event</p>
    </div>
</body>
</html>
"""

def test_eventbrite_json_ld_parsing():
    scraper = EventbriteWebScraper()
    venues = scraper._parse_search_results(MOCK_EVENTBRITE_HTML_JSON_LD, "Detroit", "psytrance")

    assert len(venues) == 2
    venue_names = [v["name"] for v in venues]
    assert "Tangent Gallery" in venue_names
    assert "Leland City Club" in venue_names

    tangent = next(v for v in venues if v["name"] == "Tangent Gallery")
    assert tangent["city"] == "Detroit"
    assert tangent["address"] == "715 E Milwaukee Ave"
    assert "Eventbrite" in tangent["source"]
    assert "psytrance" in tangent["tags"]

def test_eventbrite_html_card_parsing():
    scraper = EventbriteWebScraper()
    venues = scraper._parse_search_results(MOCK_EVENTBRITE_HTML_CARD_FALLBACK, "Detroit", "psytrance")

    assert len(venues) == 1
    marble = venues[0]
    assert marble["name"] == "Marble Bar"
    assert marble["city"] == "Detroit"
    assert "Detroit, MI" in marble["address"]
    # Ensure "Online Event" was skipped
    assert all("online" not in v["name"].lower() for v in venues)

@patch("src.scrapers.eventbrite.requests.get")
def test_eventbrite_search_venues_network_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = MOCK_EVENTBRITE_HTML_JSON_LD
    mock_get.return_value = mock_response

    scraper = EventbriteWebScraper()
    venues = scraper.search_venues("Detroit", "psytrance")

    assert len(venues) == 2
    assert venues[0]["name"] == "Tangent Gallery"
    mock_get.assert_called_once()

@patch("src.scrapers.eventbrite.requests.get")
def test_eventbrite_rate_limit_resilience(mock_get):
    mock_429 = MagicMock()
    mock_429.status_code = 429

    mock_200 = MagicMock()
    mock_200.status_code = 200
    mock_200.text = MOCK_EVENTBRITE_HTML_CARD_FALLBACK

    mock_get.side_effect = [mock_429, mock_200]

    scraper = EventbriteWebScraper()
    with patch("time.sleep", return_value=None):
        venues = scraper.search_venues("Detroit", "psytrance")

    assert len(venues) == 1
    assert venues[0]["name"] == "Marble Bar"
    assert mock_get.call_count == 2
