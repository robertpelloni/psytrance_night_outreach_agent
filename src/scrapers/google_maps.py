from .base_scraper import GoogleMapsScraper
import uuid
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
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

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

                    # For more details, we'd need to click each and wait for the side panel
                    # But for now, we'll try to get what we can from the list

                    venues.append({
                        'id': str(uuid.uuid4()),
                        'name': name,
                        'city': city,
                        'website': None, # Requires clicking
                        'google_rating': None, # Requires clicking or more complex parsing
                        'tags': query,
                        'raw_about_text': f"Scraped from Google Maps for {full_query}"
                    })
                except Exception as e:
                    print(f"Error parsing element: {e}")

            browser.close()

        return venues
