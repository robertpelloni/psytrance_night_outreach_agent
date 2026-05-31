from .base_scraper import GoogleMapsScraper, UserAgentRotator, ProxyRotator
import uuid
import re
from playwright.sync_api import sync_playwright
import time

class GoogleMapsPlaywrightScraper(GoogleMapsScraper):
    def __init__(self):
        pass

    def search_venues(self, city, query="underground techno club"):
        venues = []
        full_query = f"{query} in {city}"
        print(f"Scraping Google Maps for: {full_query}")

        with sync_playwright() as p:
            proxy = ProxyRotator.get_playwright_proxy()
            browser = p.chromium.launch(headless=True, proxy=proxy)
            context = browser.new_context(user_agent=UserAgentRotator.get_random())
            page = context.new_page()

            # Go to Google Maps
            page.goto(f"https://www.google.com/maps/search/{full_query.replace(' ', '+')}")

            # Wait for results to load
            try:
                page.wait_for_selector(".m677R", timeout=10000)
            except:
                print("Could not find results selector, attempting to continue...")

            # Simple scrolling to load more results if needed
            for _ in range(3):
                page.mouse.wheel(0, 5000)
                time.sleep(2)

            # Extract venue elements
            # Note: Google Maps selectors change frequently.
            # These are common ones but might need updates.
            venue_elements = page.query_selector_all(".m677R") or page.query_selector_all(".hfpxzc")

            for el in venue_elements[:10]: # Limit to 10 for now
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

                    venues.append({
                        'id': str(uuid.uuid4()),
                        'name': name,
                        'city': city,
                        'website': None,
                        'google_rating': rating,
                        'tags': query,
                        'raw_about_text': f"Scraped from Google Maps for {full_query}. Rating: {rating if rating else 'N/A'}"
                    })
                except Exception as e:
                    print(f"Error parsing element: {e}")

            browser.close()

        return venues
