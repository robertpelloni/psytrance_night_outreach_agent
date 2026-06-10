import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from main import load_scrapers

query_scrapers, city_scrapers = load_scrapers()

print(f"Query Scrapers: {[s.__class__.__name__ for s in query_scrapers]}")
print(f"City Scrapers: {[s.__class__.__name__ for s in city_scrapers]}")

expected_query = "GoogleMapsPlaywrightScraper"
expected_city = "ResidentAdvisorWebScraper"

if expected_query in [s.__class__.__name__ for s in query_scrapers]:
    print(f"SUCCESS: {expected_query} loaded.")
else:
    print(f"FAILURE: {expected_query} NOT loaded.")

if expected_city in [s.__class__.__name__ for s in city_scrapers]:
    print(f"SUCCESS: {expected_city} loaded.")
else:
    print(f"FAILURE: {expected_city} NOT loaded.")
