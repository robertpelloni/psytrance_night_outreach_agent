import requests
from bs4 import BeautifulSoup
import re

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

        try:
            response = requests.get(url, timeout=10)
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
