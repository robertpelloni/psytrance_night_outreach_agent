import os
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

class ScraperGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_scraper(self, url, source_name):
        if not self.client:
            print("AI not configured for scraper generation.")
            return None

        # 1. Fetch page content for context
        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            # Get a snippet of the page to help the AI understand the structure
            page_snippet = soup.get_text()[:3000]
        except Exception as e:
            print(f"Error fetching {url} for generation: {e}")
            page_snippet = "Could not fetch page content."

        prompt = f"""
        Generate a Python Playwright-based scraper class for the website: {url}
        The name of the source is: {source_name}

        The class must:
        1. Inherit from a base class (assume `BaseScraper` from `.base_scraper` is available).
        2. Implement a `search_venues(self, city)` method.
        3. Use Playwright (`sync_playwright`) to extract venue names, websites (if any), and a short description.
        4. Return a list of dictionaries with keys: 'id' (uuid string), 'name', 'city', 'website', 'google_rating', 'tags', 'raw_about_text'.
        5. Use `UserAgentRotator.get_random()` for the browser context.

        Website context (text snippet):
        {page_snippet}

        Output ONLY the raw Python code for the file `src/scrapers/{source_name.lower().replace(' ', '_')}.py`.
        Do not include markdown markers like ```python.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a senior software engineer specialized in web scraping."},
                          {"role": "user", "content": prompt}]
            )
            code = response.choices[0].message.content.strip()

            # Save the generated scraper
            filename = f"src/scrapers/{source_name.lower().replace(' ', '_')}.py"
            with open(filename, "w") as f:
                f.write(code)

            print(f"Generated and saved scraper: {filename}")
            return filename
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return None
