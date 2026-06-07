import requests
from bs4 import BeautifulSoup
import re
import random
import os

import time

class ProxyRotator:
    """Manages a pool of proxies with health tracking and dynamic rotation."""
    _proxies = {} # url -> {'fails': 0, 'success': 0, 'blacklist_until': 0}
    _initialized = False

    @classmethod
    def _initialize(cls):
        if cls._initialized:
            return
        proxy_list = os.getenv("PROXY_LIST")
        if proxy_list:
            urls = [p.strip() for p in proxy_list.split(",") if p.strip()]
            for url in urls:
                if url not in cls._proxies:
                    cls._proxies[url] = {'fails': 0, 'success': 0, 'blacklist_until': 0}
        cls._initialized = True

    @classmethod
    def get_proxy_url(cls):
        """Selects the best available proxy based on health."""
        cls._initialize()
        if not cls._proxies:
            return None

        now = time.time()
        # Filter out currently blacklisted proxies
        available = [url for url, stats in cls._proxies.items() if stats['blacklist_until'] < now]

        if not available:
            # If all are blacklisted, pick the one that expires soonest
            print("  [ProxyRotator] All proxies blacklisted. Picking least-bad option.")
            available = sorted(cls._proxies.keys(), key=lambda x: cls._proxies[x]['blacklist_until'])[:1]

        # Weight selection by success/fail ratio (simple epsilon-greedy or weighted choice)
        # For now, just random choice from available to keep it simple but effective
        return random.choice(available)

    @classmethod
    def get_proxy_config(cls):
        proxy = cls.get_proxy_url()
        if not proxy:
            return None
        return {
            "http": proxy,
            "https": proxy
        }

    @classmethod
    def get_playwright_proxy(cls):
        """Returns proxy config in the format expected by Playwright."""
        proxy = cls.get_proxy_url()
        if not proxy:
            return None
        return {"server": proxy}

    @classmethod
    def report_success(cls, proxy_url):
        if not proxy_url: return
        cls._initialize()
        if proxy_url in cls._proxies:
            cls._proxies[proxy_url]['success'] += 1
            cls._proxies[proxy_url]['fails'] = 0 # Reset fails on success
            cls._proxies[proxy_url]['blacklist_until'] = 0

    @classmethod
    def report_failure(cls, proxy_url):
        if not proxy_url: return
        cls._initialize()
        if proxy_url in cls._proxies:
            cls._proxies[proxy_url]['fails'] += 1
            # Exponential backoff for blacklist: 10s, 40s, 90s, 160s... (fails^2 * 10)
            wait_time = (cls._proxies[proxy_url]['fails'] ** 2) * 10
            cls._proxies[proxy_url]['blacklist_until'] = time.time() + wait_time
            print(f"  [ProxyRotator] Proxy {proxy_url} failed {cls._proxies[proxy_url]['fails']} times. Blacklisted for {wait_time}s.")

class UserAgentRotator:
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
    ]

    @classmethod
    def get_random(cls):
        return random.choice(cls.USER_AGENTS)

class ContactExtractor:
    @staticmethod
    def extract_emails(text):
        return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

    @staticmethod
    def extract_instagram(text):
        # Basic instagram handle regex
        return re.findall(r'(?:@|(?:www\.)?instagram\.com/)([a-zA-Z0-9_.]+)', text)

    @staticmethod
    def get_social_context(instagram_handle):
        """
        Extracts recent vibe/context from Instagram using real-time scraping.
        """
        if not instagram_handle: return None

        # Avoid circular import
        from .instagram import InstagramScraper

        scraper = InstagramScraper()
        context = scraper.get_profile_context(instagram_handle)

        if context:
            summary = f"Bio: {context.get('bio', 'N/A')}\n"
            summary += f"Recent Activity Snippet: {context.get('recent_activity_context', 'N/A')}"
            return summary

        return "social media activity suggests a standard high-energy club atmosphere."

    @staticmethod
    def scrape_website(url):
        if not url:
            return {}

        headers = {'User-Agent': UserAgentRotator.get_random()}

        # Bypass proxy for localhost to support component tests
        is_localhost = "localhost" in url or "127.0.0.1" in url
        proxies = ProxyRotator.get_proxy_config() if not is_localhost else None

        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            emails = ContactExtractor.extract_emails(response.text)
            instagrams = ContactExtractor.extract_instagram(response.text)

            return {
                'emails': list(set(emails)),
                'instagrams': list(set(instagrams)),
                'about_text': soup.get_text()[:2000] # Cap text for LLM
            }
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {}

class ResidentAdvisorScraper:
    # Placeholder for RA scraping logic
    def search_venues(self, city):
        print(f"Searching RA venues in {city}...")
        return []

class GoogleMapsScraper:
    # Placeholder for Google Maps scraping logic (e.g. via Playwright or API)
    def search_venues(self, city, query="underground techno club"):
        print(f"Searching Google Maps for {query} in {city}...")
        return []

class BaseScraper:
    """Base class for all scrapers."""
    def search_venues(self, city, query=None):
        raise NotImplementedError("Scrapers must implement search_venues")
