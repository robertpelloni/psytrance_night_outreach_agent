import requests
from bs4 import BeautifulSoup
import re
import uuid
import time
import json
from .base_scraper import BaseScraper, UserAgentRotator, ProxyRotator

class FacebookEventsWebScraper(BaseScraper):
    """
    Scraper for discovering underground music spaces and nightlife venues from public Facebook Events.
    Extracts venue names, addresses, event descriptions, and music genre tags.
    """

    def __init__(self):
        self.base_url = "https://www.facebook.com"

    def search_venues(self, city: str, query: str = "psytrance"):
        """
        Searches public event listings for a city and genre.
        Returns a list of venue dictionaries formatted for the discovery pipeline.
        """
        venues = []
        city_slug = city.lower().replace(" ", "")
        formatted_query = query.lower().replace(" ", "+")
        # Public search URL structure for Facebook event search
        url = f"{self.base_url}/events/search/?q={formatted_query}+{city_slug}"
        print(f"Scraping Facebook Events for '{query}' in {city} at {url}...")

        headers = {
            "User-Agent": UserAgentRotator.get_random(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        proxies = ProxyRotator.get_proxy_config()
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
                if response.status_code == 200:
                    if proxies:
                        ProxyRotator.report_success(proxies.get("http"))
                    venues = self._parse_search_results(response.text, city, query)
                    break
                elif response.status_code in [403, 429]:
                    print(f"  [Attempt {attempt+1}] Facebook rate limit or challenge ({response.status_code}).")
                    if proxies:
                        ProxyRotator.report_failure(proxies.get("http"))
                    proxies = ProxyRotator.get_proxy_config()
                    headers["User-Agent"] = UserAgentRotator.get_random()
                    time.sleep(2 * (attempt + 1))
                else:
                    print(f"  [Attempt {attempt+1}] Unexpected status code {response.status_code} from Facebook.")
                    break
            except Exception as e:
                print(f"  [Attempt {attempt+1}] Facebook Events request error: {e}")
                if proxies:
                    ProxyRotator.report_failure(proxies.get("http"))
                proxies = ProxyRotator.get_proxy_config()
                time.sleep(2 * (attempt + 1))

        return venues

    def _parse_search_results(self, html: str, city: str, query: str):
        """Parses HTML or embedded JSON/schema from Facebook event search results."""
        venues = []
        soup = BeautifulSoup(html, "html.parser")
        seen_names = set()

        # 1. Look for schema.org JSON-LD event metadata
        scripts = soup.find_all("script", type="application/ld+json")
        for s in scripts:
            try:
                data = json.loads(s.string or "{}")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    event_type = item.get("@type", "")
                    if "Event" in event_type or item.get("location"):
                        location = item.get("location", {})
                        if isinstance(location, dict):
                            venue_name = location.get("name")
                            address_info = location.get("address", {})
                            address_str = ""
                            if isinstance(address_info, dict):
                                address_str = address_info.get("streetAddress", "") or address_info.get("addressLocality", "")
                            elif isinstance(address_info, str):
                                address_str = address_info

                            if venue_name and venue_name.strip() and venue_name.strip().lower() not in seen_names:
                                clean_name = venue_name.strip()
                                seen_names.add(clean_name.lower())
                                venues.append({
                                    "id": str(uuid.uuid4()),
                                    "name": clean_name,
                                    "city": city,
                                    "address": address_str,
                                    "venue_type": "Event Space / Music Venue",
                                    "raw_about_text": f"Discovered via Facebook Event '{item.get('name', query)}'. {item.get('description', '')}"[:1000],
                                    "tags": f"facebook-events, nightlife, {query}",
                                    "extracted_traits": json.dumps(["facebook event", "underground gathering", query]),
                                    "source": "Facebook Events"
                                })
            except Exception:
                continue

        # 2. Fallback: Parse event cards and anchor links
        cards = soup.select("div[role='article'], div[data-testid='event_card'], a[href*='/events/']")
        for card in cards:
            try:
                text_content = card.get_text(separator=" ", strip=True)
                # Check for location patterns or text indicators
                # Typical pattern: "Event Title · Venue Name · City"
                if "·" in text_content:
                    parts = [p.strip() for p in text_content.split("·")]
                    if len(parts) >= 2:
                        candidate_venue = parts[1]
                        if (
                            candidate_venue
                            and len(candidate_venue) > 2
                            and len(candidate_venue) < 80
                            and "online" not in candidate_venue.lower()
                            and candidate_venue.lower() not in seen_names
                        ):
                            seen_names.add(candidate_venue.lower())
                            venues.append({
                                "id": str(uuid.uuid4()),
                                "name": candidate_venue,
                                "city": city,
                                "address": parts[2] if len(parts) > 2 else "",
                                "venue_type": "Nightlife / Club",
                                "raw_about_text": f"Discovered via Facebook Event listing. Details: {text_content[:300]}",
                                "tags": f"facebook-events, nightlife, {query}",
                                "extracted_traits": json.dumps(["facebook event", "live music", query]),
                                "source": "Facebook Events"
                            })
            except Exception:
                continue

        return venues
