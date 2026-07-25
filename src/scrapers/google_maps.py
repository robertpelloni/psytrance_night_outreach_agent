from .base_scraper import GoogleMapsScraper, UserAgentRotator, ProxyRotator
import uuid
import re
from playwright.sync_api import sync_playwright
import time
import requests
import os

class GoogleMapsPlaywrightScraper(GoogleMapsScraper):
    def __init__(self):
        pass

    def search_venues(self, city, query="underground techno club"):
        venues = []
        # Refine query generation: avoid "Detroit in Detroit"
        if city.lower() in query.lower():
            full_query = query
        else:
            full_query = f"{query} in {city}"

        print(f"Scraping Google Maps for: {full_query}")

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            proxy_config = ProxyRotator.get_playwright_proxy()
            proxy_url = proxy_config['server'] if proxy_config else None

            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True, proxy=proxy_config)
                    context = browser.new_context(user_agent=UserAgentRotator.get_random())
                    page = context.new_page()

                    # Go to Google Maps
                    page.goto(f"https://www.google.com/maps/search/{full_query.replace(' ', '+')}")

                    # Wait for results to load
                    try:
                        # .m677R and .hfpxzc are common result selectors
                        page.wait_for_selector(".m677R, .hfpxzc", timeout=10000)
                    except:
                        print(f"  [Attempt {attempt+1}] Could not find results selector.")
                        if attempt < max_retries - 1:
                            ProxyRotator.report_failure(proxy_url)
                            browser.close()
                            time.sleep(retry_delay * (2 ** attempt))
                            continue
                        else:
                            print("  Max retries reached. Attempting to parse whatever is there...")

                    # Simple scrolling to load more results if needed
                    for _ in range(3):
                        page.mouse.wheel(0, 5000)
                        time.sleep(2)

                    # Extract venue elements
                    venue_elements = page.query_selector_all(".m677R") or page.query_selector_all(".hfpxzc")

                    for el in venue_elements[:15]: # Slightly higher limit
                        try:
                            name = el.get_attribute("aria-label") or "Unknown Venue"

                            # Attempt to extract rating if visible in the result item
                            # This often appears in a span with aria-label containing "stars"
                            rating = None
                            try:
                                rating_el = el.query_selector('span[aria-label*="stars"]')
                                if rating_el:
                                    rating_text = rating_el.get_attribute("aria-label")
                                    # Extract number like "4.5" from "4.5 stars"
                                    rating_match = re.search(r"(\d+\.?\d*)", rating_text)
                                    if rating_match:
                                        rating = float(rating_match.group(1))
                            except:
                                pass

                            # Extract image URL if possible
                            image_url = None
                            try:
                                img_el = el.query_selector('img')
                                if img_el:
                                    image_url = img_el.get_attribute('src')
                            except:
                                pass

                            # Attempt to extract website if visible in the card
                            website = None
                            try:
                                # Common selector for website/link in Maps results
                                web_el = el.query_selector('a[data-value="Website"]')
                                if web_el:
                                    website = web_el.get_attribute("href")
                            except:
                                pass

                            venues.append({
                                'id': str(uuid.uuid4()),
                                'name': name,
                                'city': city,
                                'website': website,
                                'google_rating': rating,
                                'tags': query,
                                'raw_about_text': f"Scraped from Google Maps for {full_query}. Rating: {rating if rating else 'N/A'}",
                                'image_url': image_url,
                                'source': 'google_maps'
                            })
                        except Exception as e:
                            print(f"Error parsing element: {e}")

                    browser.close()
                ProxyRotator.report_success(proxy_url)
                break # Success
            except Exception as e:
                print(f"  [Attempt {attempt+1}] Scraper error: {e}")
                ProxyRotator.report_failure(proxy_url)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    print(f"  Scraper failed after {max_retries} attempts.")

        if not venues:
            venues = self._fallback_api_search(city, full_query)

        return venues

    def _fallback_api_search(self, city, full_query):
        """Fallback to Google Places API if Playwright scraping fails or yields no results."""
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            print("  [Fallback] No GOOGLE_MAPS_API_KEY found in environment. Skipping API fallback.")
            return []

        print(f"  [Fallback] Attempting Google Places API search for: {full_query}")
        venues = []

        # We use Text Search (Places API)
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": full_query,
            "key": api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                for place in results:
                    rating = place.get("rating")
                    name = place.get("name", "Unknown Venue")

                    # To get a photo URL, you'd need a secondary request to the Photo API using the photo_reference
                    # For simplicity, we just leave it None unless you want to spend extra requests.
                    image_url = None
                    photos = place.get("photos", [])
                    if photos:
                        photo_ref = photos[0].get("photo_reference")
                        image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_ref}&key={api_key}"

                    venues.append({
                        'id': str(uuid.uuid4()),
                        'name': name,
                        'city': city,
                        'website': None,  # Place Search doesn't return website; Place Details does.
                        'google_rating': rating,
                        'tags': full_query,
                        'raw_about_text': f"Scraped from Google Places API for {full_query}. Rating: {rating if rating else 'N/A'}",
                        'image_url': image_url,
                        'source': 'google_maps_api'
                    })
                print(f"  [Fallback] Google Places API returned {len(venues)} venues.")
            else:
                print(f"  [Fallback] Google Places API request failed with status {response.status_code}.")
        except Exception as e:
            print(f"  [Fallback] Error calling Google Places API: {e}")

        return venues
