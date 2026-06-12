from .base_scraper import ResidentAdvisorScraper, UserAgentRotator, ProxyRotator
import uuid
import time
from playwright.sync_api import sync_playwright

class ResidentAdvisorWebScraper(ResidentAdvisorScraper):
    def __init__(self):
        self.base_url = "https://ra.co"

    def search_venues(self, city):
        venues = []
        city_slug = city.lower().replace(" ", "-")
        url = f"{self.base_url}/guide/{city_slug}/venues"
        print(f"Scraping Resident Advisor venues in {city} via Playwright at {url}...")

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

                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(5000) # Wait for JS

                    if "Just a moment" in page.title():
                        print(f"  [Attempt {attempt+1}] Hit Cloudflare on RA.")
                        ProxyRotator.report_failure(proxy_url)
                        browser.close()
                        time.sleep(retry_delay * (2 ** attempt))
                        continue

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
                                        'website': self.base_url + href if href.startswith('/') else href,
                                        'google_rating': None,
                                        'tags': 'resident-advisor',
                                        'raw_about_text': f"Scraped from RA Guide: {url}. Profile link: {href}",
                                        'source': 'resident_advisor'
                                    })
                        except:
                            continue

                    browser.close()
                ProxyRotator.report_success(proxy_url)
                break # Success
            except Exception as e:
                print(f"  [Attempt {attempt+1}] RA Scraper error: {e}")
                ProxyRotator.report_failure(proxy_url)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    print(f"  RA Scraper failed after {max_retries} attempts.")

        return venues[:10]

    def enrich_venue(self, profile_url):
        """Extracts detailed info from an RA venue profile page."""
        details = {}
        print(f"Enriching RA venue from {profile_url}...")

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

                    page.goto(profile_url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(3000)

                    # Extract Website (often in an 'a' with specific icon or text)
                    # RA often uses specific labels or aria-labels
                    website_el = page.query_selector('a[aria-label="Website"], a:has-text("Website")')
                    if website_el:
                        details['website'] = website_el.get_attribute('href')

                    # Extract Description
                    desc_el = page.query_selector('span[itemprop="description"], .description, .about-text')
                    if desc_el:
                        details['description'] = desc_el.inner_text()

                    # Extract Image URL
                    img_el = page.query_selector('img[alt*="venue"], .hero img, .venue-header img')
                    if img_el:
                        details['image_url'] = img_el.get_attribute('src')

                    # Extract Socials
                    links = page.query_selector_all('a')
                    details['socials'] = []
                    for link in links:
                        href = link.get_attribute('href') or ""
                        if any(domain in href for domain in ['instagram.com', 'facebook.com', 'twitter.com']):
                            details['socials'].append(href)

                    browser.close()
                ProxyRotator.report_success(proxy_url)
                break # Success

            except Exception as e:
                print(f"  [Attempt {attempt+1}] RA Enrichment error: {e}")
                ProxyRotator.report_failure(proxy_url)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    print(f"  RA Enrichment failed after {max_retries} attempts.")

        return details
