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

                            venues.append({
                                'id': str(uuid.uuid4()),
                                'name': name,
                                'city': city,
                                'website': None,
                                'google_rating': rating,
                                'tags': query,
                                'raw_about_text': f"Scraped from Google Maps for {full_query}. Rating: {rating if rating else 'N/A'}",
                                'image_url': image_url
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

        return venues
