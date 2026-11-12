import requests
from bs4 import BeautifulSoup
import re
import uuid
import time
import json
from .base_scraper import UserAgentRotator, ProxyRotator

class EventbriteWebScraper:
    """
    Scraper for discovering nightlife and music venues from Eventbrite public listings.
    Extracts venue names, addresses, event descriptions, and tags.
    """

    def __init__(self):
        self.base_url = "https://www.eventbrite.com"

    def search_venues(self, city: str, query: str = "psytrance"):
        """
        Searches Eventbrite event listings for the given city and music genre/query.
        Returns a list of venue dictionaries.
        """
        venues = []
        city_slug = city.lower().replace(" ", "-")
        formatted_query = query.lower().replace(" ", "-")
        url = f"{self.base_url}/d/{city_slug}/{formatted_query}/"
        print(f"Scraping Eventbrite for '{query}' in {city} at {url}...")

        headers = {
            "User-Agent": UserAgentRotator.get_random(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        # Check proxy config
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
                    print(f"  [Attempt {attempt+1}] Eventbrite rate limit or bot challenge ({response.status_code}).")
                    if proxies:
                        ProxyRotator.report_failure(proxies.get("http"))
                    proxies = ProxyRotator.get_proxy_config()
                    headers["User-Agent"] = UserAgentRotator.get_random()
                    time.sleep(2 * (attempt + 1))
                else:
                    print(f"  [Attempt {attempt+1}] Unexpected status code {response.status_code} from Eventbrite.")
                    break
            except Exception as e:
                print(f"  [Attempt {attempt+1}] Request error: {e}")
                if proxies:
                    ProxyRotator.report_failure(proxies.get("http"))
                proxies = ProxyRotator.get_proxy_config()
                time.sleep(2 * (attempt + 1))

        return venues

    def _parse_search_results(self, html: str, city: str, query: str):
        """Parses HTML or embedded JSON-LD schema from Eventbrite search page."""
        venues = []
        soup = BeautifulSoup(html, "html.parser")
        seen_names = set()

        # 1. Attempt parsing schema.org JSON-LD scripts
        scripts = soup.find_all("script", type="application/ld+json")
        for s in scripts:
            try:
                data = json.loads(s.string or "{}")
                items = data.get("itemListElement", []) if isinstance(data, dict) else []
                if isinstance(data, list):
                    items = data
                for item in items:
                    event = item.get("item", item) if isinstance(item, dict) else {}
                    location = event.get("location", {})
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
                                "raw_about_text": f"Discovered via Eventbrite event '{event.get('name', query)}'. {event.get('description', '')}"[:1000],
                                "tags": f"eventbrite, nightlife, {query}",
                                "extracted_traits": json.dumps(["electronic events", "eventbrite listing", query]),
                                "source": "Eventbrite"
                            })
            except Exception:
                continue

        # 2. Fallback: Parse card elements in HTML
        cards = soup.select("section.event-card-details, div[data-testid='event-card'], .discover-search-desktop-card")
        for card in cards:
            try:
                # Look for venue location text
                venue_el = card.select_one("p[class*='location'], span[class*='location'], p.Typography_body-md")
                name_el = card.select_one("h2, h3, a[class*='event-card-link']")
                event_title = name_el.get_text().strip() if name_el else ""

                if venue_el:
                    v_text = venue_el.get_text().strip()
                    # Eventbrite often shows "Venue Name • City, State"
                    parts = [p.strip() for p in v_text.split("•")]
                    candidate_venue = parts[0] if parts else v_text

                    if (candidate_venue
                        and len(candidate_venue) > 2
                        and "online" not in candidate_venue.lower()
                        and candidate_venue.lower() not in seen_names):
                        seen_names.add(candidate_venue.lower())
                        venues.append({
                            "id": str(uuid.uuid4()),
                            "name": candidate_venue,
                            "city": city,
                            "address": parts[1] if len(parts) > 1 else "",
                            "venue_type": "Nightlife / Music Venue",
                            "raw_about_text": f"Discovered via Eventbrite listing '{event_title}'. Location: {v_text}",
                            "tags": f"eventbrite, nightlife, {query}",
                            "extracted_traits": json.dumps(["nightlife", "eventbrite listing", query]),
                            "source": "Eventbrite"
                        })
            except Exception:
                continue

        return venues
