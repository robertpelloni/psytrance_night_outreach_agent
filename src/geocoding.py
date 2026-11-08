import os
import requests
import json
from src.ai_engine import AIEngine
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class GeocodingUtility:
    def __init__(self, api_key=None):
        self.ai = AIEngine(api_key=api_key)
        self.geolocator = Nominatim(user_agent="psytrance_outreach_agent")

    def geocode_venue(self, venue_name, city, address=None):
        """
        Attempts coordinate lookup with progressive specificity:
        1. Venue Name + Full Address + City
        2. Full Address + City
        3. Venue Name + City
        Falls back to AI estimation if geocoding returns empty.
        """
        queries = []
        if address and address.strip():
            clean_addr = address.strip()
            # If address already has city or name, avoid redundant concatenation
            if venue_name and venue_name.lower() not in clean_addr.lower():
                queries.append(f"{venue_name}, {clean_addr}, {city}")
            queries.append(f"{clean_addr}, {city}")

        queries.append(f"{venue_name}, {city}")

        for query in queries:
            try:
                location = self.geolocator.geocode(query, addressdetails=True, timeout=10)
                if location:
                    print(f"Geocoding: Found '{query}' via Nominatim: ({location.latitude}, {location.longitude})")
                    return location.latitude, location.longitude
            except (GeocoderTimedOut, Exception) as e:
                print(f"Nominatim Geocoding Error for '{query}': {e}")

        # Fallback to AI estimation
        prompt = f"""
        Find the approximate latitude and longitude for the music venue:
        Venue: {venue_name}
        Address: {address or 'N/A'}
        City: {city}

        Return ONLY a JSON object with:
        {{
            "latitude": float,
            "longitude": float
        }}
        """
        try:
            if not self.ai.client:
                return None, None

            response = self.ai.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return data.get("latitude"), data.get("longitude")
        except Exception as e:
            print(f"Geocoding Error for {venue_name}: {e}")
            return None, None

    def parse_and_enrich_venue_address(self, venue_name, city, address=None):
        """
        Performs high-precision geocoding and reverse parsing to extract:
        - latitude, longitude
        - normalized_address
        - neighborhood
        - postal_code
        """
        # First delegate to geocode_venue to preserve existing mocks and fallback hierarchy
        lat, lon = self.geocode_venue(venue_name, city, address=address)
        result = {
            "latitude": lat,
            "longitude": lon,
            "normalized_address": address,
            "neighborhood": None,
            "postal_code": None
        }

        queries = []
        if address and address.strip():
            clean_addr = address.strip()
            if venue_name and venue_name.lower() not in clean_addr.lower():
                queries.append(f"{venue_name}, {clean_addr}, {city}")
            queries.append(f"{clean_addr}, {city}")
        queries.append(f"{venue_name}, {city}")

        for query in queries:
            try:
                location = self.geolocator.geocode(query, addressdetails=True, timeout=10)
                if location:
                    if result["latitude"] is None or result["longitude"] is None:
                        result["latitude"] = location.latitude
                        result["longitude"] = location.longitude

                    raw = getattr(location, "raw", {})
                    addr_details = raw.get("address", {})
                    if addr_details:
                        # Extract neighborhood or suburb or quarter
                        neighborhood = (
                            addr_details.get("neighbourhood")
                            or addr_details.get("suburb")
                            or addr_details.get("quarter")
                            or addr_details.get("district")
                        )
                        result["neighborhood"] = neighborhood
                        result["postal_code"] = addr_details.get("postcode")

                        # Build formatted street address if present
                        road = addr_details.get("road")
                        house_number = addr_details.get("house_number")
                        if road:
                            result["normalized_address"] = f"{house_number} {road}".strip() if house_number else road
                        elif "display_name" in raw:
                            result["normalized_address"] = raw["display_name"].split(",")[0].strip()

                    return result
            except (GeocoderTimedOut, Exception) as e:
                print(f"Nominatim parsing error for '{query}': {e}")

        return result

if __name__ == "__main__":
    geo = GeocodingUtility()
    lat, lon = geo.geocode_venue("Berghain", "Berlin")
    print(f"Berghain: {lat}, {lon}")
