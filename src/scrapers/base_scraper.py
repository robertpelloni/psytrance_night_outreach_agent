import requests
from bs4 import BeautifulSoup
import re
import random

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
    def scrape_website(url):
        if not url:
            return {}

        headers = {'User-Agent': UserAgentRotator.get_random()}
        try:
            response = requests.get(url, headers=headers, timeout=10)
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
