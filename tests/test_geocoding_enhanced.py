import os
import pytest
from unittest.mock import MagicMock, patch
from src.geocoding import GeocodingUtility
from src.db_manager import DatabaseManager
from src.dashboard.app import app

TEST_DB_PATH = "database/test_geocoding.db"

@pytest.fixture
def test_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db = DatabaseManager(db_path=TEST_DB_PATH)
    yield db
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_geocode_venue_with_address_fallback():
    geo = GeocodingUtility()

    mock_loc = MagicMock()
    mock_loc.latitude = 42.338
    mock_loc.longitude = -83.062
    mock_loc.raw = {
        "address": {
            "road": "Grand River Avenue",
            "house_number": "2548",
            "neighbourhood": "Midtown",
            "postcode": "48201"
        }
    }

    with patch.object(geo.geolocator, 'geocode', return_value=mock_loc) as mock_geocode:
        lat, lon = geo.geocode_venue("TV Lounge", "Detroit", address="2548 Grand River Ave")
        assert lat == 42.338
        assert lon == -83.062
        assert mock_geocode.called

def test_parse_and_enrich_venue_address():
    geo = GeocodingUtility()

    mock_loc = MagicMock()
    mock_loc.latitude = 42.363
    mock_loc.longitude = -83.085
    mock_loc.raw = {
        "address": {
            "road": "Holden Street",
            "house_number": "1501",
            "suburb": "New Center",
            "postcode": "48208"
        }
    }

    with patch.object(geo.geolocator, 'geocode', return_value=mock_loc):
        res = geo.parse_and_enrich_venue_address("Marble Bar", "Detroit", address="1501 Holden St")
        assert res["latitude"] == 42.363
        assert res["longitude"] == -83.085
        assert res["normalized_address"] == "1501 Holden Street"
        assert res["neighborhood"] == "New Center"
        assert res["postal_code"] == "48208"

def test_update_venue_address_details(test_db):
    venue_data = {
        "id": "geo-test-1",
        "name": "The Underground",
        "city": "Detroit",
        "address": "123 Techno Way",
        "website": "https://underground.detroit"
    }
    test_db.add_venue(venue_data)

    test_db.update_venue_address_details(
        "geo-test-1",
        lat=42.35,
        lon=-83.05,
        address="123 Techno Way NW",
        neighborhood="Downtown"
    )

    v = test_db.get_venue("geo-test-1")
    assert v["latitude"] == 42.35
    assert v["longitude"] == -83.05
    assert v["address"] == "123 Techno Way NW"
    assert v["neighborhood"] == "Downtown"

def test_dashboard_geocode_endpoint(test_db):
    app.config["TESTING"] = True
    venue_data = {
        "id": "geo-dash-1",
        "name": "City Club",
        "city": "Detroit",
        "address": "400 Bagley St",
        "website": "https://lelandcityclub.com"
    }
    test_db.add_venue(venue_data)

    with patch("src.dashboard.app.db", test_db):
        client = app.test_client()

        mock_enrichment = {
            "latitude": 42.332,
            "longitude": -83.054,
            "normalized_address": "400 Bagley Street",
            "neighborhood": "Downtown",
            "postal_code": "48226"
        }

        with patch("src.geocoding.GeocodingUtility.parse_and_enrich_venue_address", return_value=mock_enrichment):
            res = client.post("/geocode_venue/geo-dash-1")
            assert res.status_code == 200
            data = res.get_json()
            assert data["status"] == "success"
            assert data["enrichment"]["neighborhood"] == "Downtown"

            # Check database updated
            v = test_db.get_venue("geo-dash-1")
            assert v["latitude"] == 42.332
            assert v["neighborhood"] == "Downtown"
