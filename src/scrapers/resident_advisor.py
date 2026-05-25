from .base_scraper import ResidentAdvisorScraper, UserAgentRotator, ProxyRotator
import uuid
from playwright.sync_api import sync_playwright

class ResidentAdvisorWebScraper(ResidentAdvisorScraper):
    def __init__(self):
        self.base_url = "https://ra.co"

    def search_venues(self, city):
        venues = []
        city_slug = city.lower().replace(" ", "-")
        # Try a different URL pattern if the guide one fails or is empty
        # Sometimes RA uses /directory/venues/[city]
        url = f"{self.base_url}/guide/{city_slug}/venues"

        print(f"Scraping Resident Advisor venues in {city} via Playwright at {url}...")

        with sync_playwright() as p:
            proxy = ProxyRotator.get_playwright_proxy()
            browser = p.chromium.launch(headless=True, proxy=proxy)
            context = browser.new_context(
                user_agent=UserAgentRotator.get_random()
            )
            page = context.new_page()

            try:
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(5000) # Wait for JS to render

                # Check for "Just a moment" (Cloudflare)
                if "Just a moment" in page.title():
                    print("Hit Cloudflare on RA. Attempting to wait...")
                    page.wait_for_timeout(10000)

                # Search for any links that look like venues
                links = page.query_selector_all('a')
                for link in links:
                    try:
                        href = link.get_attribute("href") or ""
                        name = link.inner_text()
                        if "/venues/" in href and name and len(name.strip()) > 1:
                            # Avoid duplicates and common UI strings
                            if name.strip() not in [v['name'] for v in venues] and len(name.strip()) < 50:
                                venues.append({
                                    'id': str(uuid.uuid4()),
                                    'name': name.strip(),
                                    'city': city,
                                    'website': None,
                                    'google_rating': None,
                                    'tags': 'resident-advisor',
                                    'raw_about_text': f"Scraped from RA Guide: {url}"
                                })
                    except:
                        continue

            except Exception as e:
                print(f"Error scraping RA: {e}")
            finally:
                browser.close()

        return venues[:10]
