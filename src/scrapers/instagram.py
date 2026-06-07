from playwright.sync_api import sync_playwright
from .base_scraper import UserAgentRotator, ProxyRotator
import time

class InstagramScraper:
    """Scraper for public Instagram profiles to extract vibe signals."""

    def get_profile_context(self, handle):
        if not handle:
            return None

        handle = handle.strip().replace('@', '')
        url = f"https://www.instagram.com/{handle}/"
        print(f"Scraping Instagram profile: {url}")
        proxy_config = ProxyRotator.get_playwright_proxy()
        proxy_url = proxy_config['server'] if proxy_config else None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, proxy=proxy_config)
                context = browser.new_context(user_agent=UserAgentRotator.get_random())
                page = context.new_page()

                # Navigate to profile
                page.goto(url, wait_until="networkidle")

                # Attempt to extract bio and recent text
                # Note: IG is highly protected, these selectors may fail or require login
                # We prioritize the 'bio' and visible text.
                bio = ""
                try:
                    # Generic selector for bio section
                    bio_el = page.query_selector("header section")
                    if bio_el:
                        bio = bio_el.inner_text()
                except:
                    pass

                # Get visible text as a fallback/enrichment
                visible_text = page.evaluate("() => document.body.innerText")

                browser.close()

                if bio or len(visible_text) > 100:
                    ProxyRotator.report_success(proxy_url)
                    return {
                        'bio': bio,
                        'recent_activity_context': visible_text[:1000]
                    }
                ProxyRotator.report_failure(proxy_url)
                return None
        except Exception as e:
            print(f"Error scraping Instagram {handle}: {e}")
            ProxyRotator.report_failure(proxy_url)
            return None
