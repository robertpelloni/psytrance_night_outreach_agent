import requests
from bs4 import BeautifulSoup
import re
import uuid
import time
import json
import urllib.parse
from .base_scraper import UserAgentRotator, ProxyRotator

class MeetupWebScraper:
    """
    Scraper for discovering underground music communities, recurring events,
    and venues from Meetup public listings.
    Extracts venue names, addresses, event summaries, and community tags.
    """

    def __init__(self):
        self.base_url = "https://www.meetup.com"

    def search_venues(self, city: str, query: str = "psytrance"):
        """
        Searches Meetup events for the given city and music genre/keyword query.
        Returns a list of venue dictionaries.
        """
        venues = []
        encoded_query = urllib.parse.quote_plus(query)
        encoded_city = urllib.parse.quote_plus(city)
        url = f"{self.base_url}/find/?keywords={encoded_query}&location={encoded_city}&source=EVENTS"
        print(f"Scraping Meetup for '{query}' in {city} at {url}...")

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
                    print(f"  [Attempt {attempt+1}] Meetup rate limit / security challenge ({response.status_code}).")
                    if proxies:
                        ProxyRotator.report_failure(proxies.get("http"))
                    proxies = ProxyRotator.get_proxy_config()
                    headers["User-Agent"] = UserAgentRotator.get_random()
                    time.sleep(2 * (attempt + 1))
                else:
                    print(f"  [Attempt {attempt+1}] Unexpected status code {response.status_code} from Meetup.")
                    break
            except Exception as e:
                print(f"  [Attempt {attempt+1}] Meetup request error: {e}")
                if proxies:
                    ProxyRotator.report_failure(proxies.get("http"))
                proxies = ProxyRotator.get_proxy_config()
                time.sleep(2 * (attempt + 1))

        return venues

    def _parse_search_results(self, html: str, city: str, query: str):
        """Parses HTML or embedded JSON-LD schema from Meetup search results."""
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

                        if (venue_name
                            and venue_name.strip()
                            and "online" not in venue_name.lower()
                            and venue_name.strip().lower() not in seen_names):
                            clean_name = venue_name.strip()
                            seen_names.add(clean_name.lower())
                            venues.append({
                                "id": str(uuid.uuid4()),
                                "name": clean_name,
                                "city": city,
                                "address": address_str,
                                "venue_type": "Community Space / Event Venue",
                                "raw_about_text": f"Discovered via Meetup event '{event.get('name', query)}'. {event.get('description', '')}"[:1000],
                                "tags": f"meetup, electronic community, {query}",
                                "extracted_traits": json.dumps(["community events", "meetup listing", query]),
                                "source": "Meetup"
                            })
            except Exception:
                continue

        # 2. Fallback: Parse card elements in HTML
        cards = soup.select("div[data-testid='event-card'], div.eventCard, div[data-event-label]")
        for card in cards:
            try:
                venue_el = card.select_one("span.venue-name, p[data-testid='venue-name'], span.text-gray6")
                name_el = card.select_one("h2, h3, a[id*='event-card-link']")
                event_title = name_el.get_text().strip() if name_el else ""

                if venue_el:
                    v_text = venue_el.get_text().strip()
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
                            "venue_type": "Community / Gathering Space",
                            "raw_about_text": f"Discovered via Meetup listing '{event_title}'. Location: {v_text}",
                            "tags": f"meetup, electronic community, {query}",
                            "extracted_traits": json.dumps(["community gathering", "meetup listing", query]),
                            "source": "Meetup"
                        })
            except Exception:
                continue

        return venues
