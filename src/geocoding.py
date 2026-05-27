import os
import requests
import json
from src.ai_engine import AIEngine

class GeocodingUtility:
    def __init__(self, api_key=None):
        self.ai = AIEngine(api_key=api_key)

    def geocode_venue(self, venue_name, city):
        """
        Uses AI to estimate coordinates if no API is available,
        or a search utility if configured.
        """
        # For this autonomous agent, we use GPT-4o to 'hallucinate' or
        # recall coordinates for established venues, or use city centroids.
        prompt = f"""
        Find the approximate latitude and longitude for the music venue:
        Venue: {venue_name}
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

if __name__ == "__main__":
    geo = GeocodingUtility()
    lat, lon = geo.geocode_venue("Berghain", "Berlin")
    print(f"Berghain: {lat}, {lon}")
